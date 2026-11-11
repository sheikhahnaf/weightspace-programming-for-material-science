"""Probabilistic Bayesian Neural Network (PBNN) surrogate.

PyTorch-native implementation that mirrors the TensorFlow Probability
``DenseReparameterization`` PBNN from the reference notebook
(``Composite_Elastic_Properties_Prediction_with_uncertainty_with_DGP_tabPFN.ipynb``).

Key design:
- Aleatoric uncertainty: heteroscedastic output head (learned log_std).
- Epistemic uncertainty: MC-Dropout at inference time.
- Quantile estimates: empirical quantiles over MC forward-pass samples.
- Inputs and outputs are internally standardised before training.

No TF/TFP dependency — pure PyTorch.
"""

from __future__ import annotations

from typing import Optional, Sequence

import numpy as np
import torch
import torch.nn as nn

from bo_zoo.surrogates.base import QuantileModelWrapper


# ---------------------------------------------------------------------------
# Internal network
# ---------------------------------------------------------------------------


class _HeteroscedasticNet(nn.Module):
    """Fully-connected dropout network with dual output heads.

    Outputs ``(mean, log_std)`` for every input point.
    Dropout is applied after every hidden activation, enabling MC-Dropout
    uncertainty estimation at inference time.
    """

    def __init__(
        self,
        in_features: int,
        hidden_sizes: Sequence[int],
        dropout_rate: float,
        activation: str = "relu",
    ):
        super().__init__()
        act_map = {"relu": nn.ReLU, "tanh": nn.Tanh, "selu": nn.SELU}
        act_cls = act_map.get(activation.lower(), nn.ReLU)

        layers: list[nn.Module] = []
        prev = in_features
        for h in hidden_sizes:
            layers.append(nn.Linear(prev, h))
            layers.append(act_cls())
            layers.append(nn.Dropout(p=dropout_rate))
            prev = h

        self.backbone = nn.Sequential(*layers)
        self.head_mean = nn.Linear(prev, 1)
        self.head_log_std = nn.Linear(prev, 1)

    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        h = self.backbone(x)
        return self.head_mean(h), self.head_log_std(h)


def _gaussian_nll(
    mean: torch.Tensor, log_std: torch.Tensor, y: torch.Tensor
) -> torch.Tensor:
    """Heteroscedastic Gaussian NLL loss."""
    var = torch.exp(2.0 * log_std) + 1e-8
    return (0.5 * torch.log(var) + 0.5 * (y - mean) ** 2 / var).mean()


# ---------------------------------------------------------------------------
# Public surrogate
# ---------------------------------------------------------------------------


class PBNNSurrogate(QuantileModelWrapper):
    """BoTorch-compatible probabilistic BNN with MC-Dropout uncertainty.

    Equivalent to the TFP ``DenseReparameterization`` PBNN in the reference
    notebook, re-implemented in PyTorch.

    Uncertainty has two components:

    * **Aleatoric** — learned by the ``log_std`` head (observation noise).
    * **Epistemic** — estimated by running ``n_mc_samples`` stochastic forward
      passes with dropout enabled (MC-Dropout).

    Quantiles are computed empirically from the combined distribution of MC
    samples.

    Args:
        hidden_sizes:   Sequence of hidden layer widths (default: ``(64, 64)``).
        n_epochs:       Maximum training epochs (default: ``500``).
        lr:             Adam learning rate (default: ``1e-3``).
        dropout_rate:   Dropout probability in each hidden layer (default: ``0.1``).
        n_mc_samples:   Forward passes at inference for uncertainty (default: ``100``).
        activation:     Hidden activation — ``"relu"``, ``"tanh"``, or ``"selu"``
                        (default: ``"relu"``).
        batch_size:     Mini-batch size (default: ``32``).
        quantile_low:   Lower quantile (default ``0.16`` ≈ −1 σ).
        quantile_high:  Upper quantile (default ``0.84`` ≈ +1 σ).
        patience:       Early-stopping patience in epochs (default: ``50``).
        device:         ``"cpu"`` or ``"cuda"`` (default: ``"cpu"``).

    Raises:
        RuntimeError: If ``fit()`` has not been called before accessing ``model``
                      or calling ``_predict_quantiles``.
    """

    def __init__(
        self,
        hidden_sizes: Sequence[int] = (64, 64),
        n_epochs: int = 500,
        lr: float = 1e-3,
        dropout_rate: float = 0.1,
        n_mc_samples: int = 100,
        activation: str = "relu",
        batch_size: int = 32,
        quantile_low: float = 0.16,
        quantile_high: float = 0.84,
        patience: int = 50,
        device: str = "cpu",
    ):
        self.hidden_sizes = tuple(hidden_sizes)
        self.n_epochs = n_epochs
        self.lr = lr
        self.dropout_rate = dropout_rate
        self.n_mc_samples = n_mc_samples
        self.activation = activation
        self.batch_size = batch_size
        self.quantile_low = quantile_low
        self.quantile_high = quantile_high
        self.patience = patience
        self.device = torch.device(device)

        self._net: Optional[_HeteroscedasticNet] = None
        self._x_mean: Optional[np.ndarray] = None
        self._x_std: Optional[np.ndarray] = None
        self._y_mean: float = 0.0
        self._y_std: float = 1.0
        self._model = None

    # ------------------------------------------------------------------
    # SurrogateBase.fit
    # ------------------------------------------------------------------

    def fit(self, train_X, train_Y):
        """Train the PBNN.

        Args:
            train_X: ``(n, d)`` array or tensor.
            train_Y: ``(n,)`` or ``(n, 1)`` array or tensor (single-output).

        Returns:
            Fitted BoTorch-compatible model wrapper (also stored as ``self.model``).
        """
        if isinstance(train_X, torch.Tensor):
            train_X = train_X.detach().cpu().numpy()
        if isinstance(train_Y, torch.Tensor):
            train_Y = train_Y.detach().cpu().numpy()

        train_X = np.asarray(train_X, dtype=float)
        train_Y = np.asarray(train_Y, dtype=float).ravel()

        # --- standardise ---
        self._x_mean = train_X.mean(axis=0)
        self._x_std = np.where(train_X.std(axis=0) > 1e-8, train_X.std(axis=0), 1.0)
        self._y_mean = float(train_Y.mean())
        self._y_std = float(train_Y.std()) if float(train_Y.std()) > 1e-8 else 1.0

        X_sc = (train_X - self._x_mean) / self._x_std
        Y_sc = (train_Y - self._y_mean) / self._y_std

        n, d = X_sc.shape
        X_t = torch.tensor(X_sc, dtype=torch.float64, device=self.device)
        Y_t = torch.tensor(Y_sc, dtype=torch.float64, device=self.device).unsqueeze(-1)

        # --- build network (float64 for consistency with the rest of bo-zoo) ---
        self._net = _HeteroscedasticNet(
            in_features=d,
            hidden_sizes=self.hidden_sizes,
            dropout_rate=self.dropout_rate,
            activation=self.activation,
        ).double().to(self.device)

        optimizer = torch.optim.Adam(self._net.parameters(), lr=self.lr)
        scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
            optimizer, patience=max(1, self.patience // 2), factor=0.5
        )

        best_loss = float("inf")
        best_state: Optional[dict] = None
        no_improve = 0

        self._net.train()
        for _ in range(self.n_epochs):
            perm = torch.randperm(n, device=self.device)
            epoch_loss = 0.0
            n_batches = 0
            for i in range(0, n, self.batch_size):
                idx = perm[i : i + self.batch_size]
                xb, yb = X_t[idx], Y_t[idx]
                optimizer.zero_grad()
                mu, log_std = self._net(xb)
                loss = _gaussian_nll(mu, log_std, yb)
                loss.backward()
                optimizer.step()
                epoch_loss += loss.item()
                n_batches += 1
            epoch_loss /= max(n_batches, 1)
            scheduler.step(epoch_loss)

            if epoch_loss < best_loss - 1e-6:
                best_loss = epoch_loss
                best_state = {k: v.clone() for k, v in self._net.state_dict().items()}
                no_improve = 0
            else:
                no_improve += 1
                if no_improve >= self.patience:
                    break

        if best_state is not None:
            self._net.load_state_dict(best_state)
        self._net.eval()

        self._model = self._make_botorch_model(num_outputs=1)
        return self._model

    # ------------------------------------------------------------------
    # QuantileModelWrapper implementation
    # ------------------------------------------------------------------

    def _predict_quantiles(
        self, X_np: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Return ``(q_low, q_med, q_high)`` via MC-Dropout sampling."""
        if self._net is None:
            raise RuntimeError("Call fit() before predicting.")

        X_sc = (X_np - self._x_mean) / self._x_std
        X_t = torch.tensor(X_sc, dtype=torch.float64, device=self.device)

        # Activate dropout for epistemic uncertainty (train mode)
        self._net.train()
        samples: list[np.ndarray] = []
        with torch.no_grad():
            for _ in range(self.n_mc_samples):
                mu, log_std = self._net(X_t)
                std = torch.exp(log_std).clamp(min=1e-6)
                # Sample aleatoric noise
                y_sample = mu + std * torch.randn_like(mu)
                samples.append(y_sample.cpu().numpy().ravel())
        self._net.eval()

        arr = np.stack(samples, axis=0)  # (n_mc, n_test)

        # De-standardise and compute empirical quantiles
        arr = arr * self._y_std + self._y_mean
        q_low = np.quantile(arr, self.quantile_low, axis=0)
        q_med = np.median(arr, axis=0)
        q_high = np.quantile(arr, self.quantile_high, axis=0)

        return q_low, q_med, q_high

    @property
    def model(self):
        if self._model is None:
            raise RuntimeError("Call fit() before accessing .model")
        return self._model
