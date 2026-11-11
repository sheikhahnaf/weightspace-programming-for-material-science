"""Abstract base classes and shared posterior-building machinery."""

from __future__ import annotations

from abc import ABC, abstractmethod

import numpy as np
import torch
from torch import Tensor

import gpytorch
from gpytorch.distributions import MultivariateNormal, MultitaskMultivariateNormal
from botorch.models.gpytorch import GPyTorchModel
from botorch.posteriors.gpytorch import GPyTorchPosterior


class SurrogateBase(ABC):
    """Minimal interface every surrogate must implement.

    After ``fit`` the returned object must satisfy the BoTorch ``Model``
    contract (``model.posterior(X)`` returns a valid ``Posterior``).
    """

    @abstractmethod
    def fit(self, train_X: Tensor, train_Y: Tensor):
        """Train the surrogate and store the fitted BoTorch model.

        Args:
            train_X: ``(n, d)`` float64 input tensor.
            train_Y: ``(n, m)`` float64 target tensor (may contain NaN for MT).

        Returns:
            The fitted BoTorch ``Model`` (also stored as ``self.model``).
        """

    @property
    @abstractmethod
    def model(self):
        """The fitted BoTorch Model (set after ``fit``)."""

    def predict(self, X: Tensor) -> tuple[Tensor, Tensor]:
        """Convenience wrapper: returns ``(mean, variance)``.

        Args:
            X: ``(n, d)`` input tensor.

        Returns:
            ``mean``: ``(n, m)`` tensor.
            ``variance``: ``(n, m)`` tensor.
        """
        with torch.no_grad():
            posterior = self.model.posterior(X)
            return posterior.mean, posterior.variance


# ---------------------------------------------------------------------------
# QuantileModelWrapper — shared posterior builder for non-GP surrogates
# ---------------------------------------------------------------------------


def _build_posterior_from_quantiles(
    q_low: np.ndarray,
    q_med: np.ndarray,
    q_high: np.ndarray,
    interleaved: bool = False,
) -> GPyTorchPosterior:
    """Convert quantile predictions to a GPyTorchPosterior.

    This is the standard pattern for all non-GP surrogates (TabPFN, forests,
    gradient boosting, etc.).

    The posterior mean is set to ``q_med`` and the variance to
    ``((q_high - q_low) / 2) ** 2``, clipped to a minimum of ``1e-6``.

    Shape contract (single-output):
        q_low/q_med/q_high: ``(n,)`` or ``(n, 1)``
        → ``posterior.mean``: ``(n, 1)``
        → ``posterior.variance``: ``(n, 1)``

    Shape contract (multi-output, m tasks):
        q_low/q_med/q_high: ``(n, m)``
        → Uses ``MultitaskMultivariateNormal(interleaved=False)``
        → ``posterior.mean``: ``(n, m)``

    Args:
        q_low:  Lower quantile predictions (numpy array).
        q_med:  Median / point predictions (numpy array).
        q_high: Upper quantile predictions (numpy array).
        interleaved: Passed to ``MultitaskMultivariateNormal`` for multi-output.
            **Must be False** for BoTorch qEHVI compatibility.

    Returns:
        ``GPyTorchPosterior`` compatible with all BoTorch acquisition functions.
    """
    q_low = np.asarray(q_low, dtype=float)
    q_med = np.asarray(q_med, dtype=float)
    q_high = np.asarray(q_high, dtype=float)

    multi_output = q_med.ndim == 2 and q_med.shape[1] > 1

    if not multi_output:
        q_med = q_med.ravel()
        std = np.maximum((q_high.ravel() - q_low.ravel()) / 2.0, 1e-6)
        mean_t = torch.tensor(q_med, dtype=torch.float64)
        var_t = torch.tensor(std**2, dtype=torch.float64)
        cov = torch.diag(var_t)
        dist = MultivariateNormal(mean_t, covariance_matrix=cov)
        return GPyTorchPosterior(dist)
    else:
        n, m = q_med.shape
        std = np.maximum((q_high - q_low) / 2.0, 1e-6)
        mean_t = torch.tensor(q_med, dtype=torch.float64)  # (n, m)
        var_t = torch.tensor(std**2, dtype=torch.float64)   # (n, m)
        # Build block-diagonal covariance: m independent (n×n) diagonals
        # Use MultitaskMultivariateNormal with interleaved=False
        cov_list = [torch.diag(var_t[:, j]) for j in range(m)]
        # Stack as (m, n, n) block
        block = torch.stack(cov_list, dim=0)  # (m, n, n)
        dist = MultitaskMultivariateNormal(
            mean_t.unsqueeze(0),  # (1, n, m)
            block.unsqueeze(0),   # (1, m, n, n) — will be squeezed inside
            interleaved=interleaved,
        )
        return GPyTorchPosterior(dist)


class QuantileModelWrapper(SurrogateBase):
    """Mixin for surrogates that produce quantile outputs.

    Subclasses implement ``_predict_quantiles(X_np)`` returning
    ``(q_low, q_med, q_high)`` as numpy arrays.  This class handles the
    conversion to a GPyTorchPosterior and wraps the result in a minimal
    BoTorch-compatible model.
    """

    def _predict_quantiles(
        self, X_np: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Internal thin BoTorch model wrapper
    # ------------------------------------------------------------------

    class _QuantileBotorchModel:
        """Minimal BoTorch-compatible model that delegates to a parent surrogate."""

        def __init__(self, parent: "QuantileModelWrapper"):
            self._parent = parent

        @property
        def num_outputs(self) -> int:
            """Number of outputs — BoTorch acquisition functions require this."""
            return self._parent._num_outputs

        def posterior(self, X: Tensor, **kwargs) -> GPyTorchPosterior:
            X_orig = X
            device = X.device  # propagate device so posterior lives on same device as acqf
            X_np = X.detach().cpu().numpy()

            # BoTorch passes X with shape (batch, q, d) or (q, d).
            # Flatten to (n, d) for sklearn, then reshape output back.
            if X_np.ndim == 3:
                batch_size, q, d = X_np.shape
                X_flat = X_np.reshape(-1, d)  # (batch*q, d)
            elif X_np.ndim == 2:
                batch_size, q = 1, X_np.shape[0]
                X_flat = X_np
            else:
                batch_size, q = 1, 1
                X_flat = X_np[None]

            q_low, q_med, q_high = self._parent._predict_quantiles(X_flat)
            q_med_arr = np.asarray(q_med).ravel()
            q_low_arr = np.asarray(q_low).ravel()
            q_high_arr = np.asarray(q_high).ravel()
            std = np.maximum((q_high_arr - q_low_arr) / 2.0, 1e-6)
            var = std ** 2

            if X_orig.ndim == 3 and batch_size > 1:
                # Reshape to (batch, q): GPyTorchPosterior.mean adds unsqueeze(-1)
                # → posterior.mean shape: (batch, q, 1)
                mean_t = torch.tensor(q_med_arr.reshape(batch_size, q), dtype=torch.float64, device=device)
                var_t = torch.tensor(var.reshape(batch_size, q), dtype=torch.float64, device=device)
                cov = torch.diag_embed(var_t)  # (batch, q, q)
                dist = MultivariateNormal(mean_t, covariance_matrix=cov)
            else:
                # Single batch or 2D input: (q,) mean, (q, q) cov
                mean_t = torch.tensor(q_med_arr, dtype=torch.float64, device=device)
                var_t = torch.tensor(var, dtype=torch.float64, device=device)
                dist = MultivariateNormal(mean_t, covariance_matrix=torch.diag(var_t))

            return GPyTorchPosterior(dist)

        def eval(self):
            return self

        def train(self, mode: bool = True):
            return self

    def _make_botorch_model(self, num_outputs: int = 1) -> "_QuantileBotorchModel":
        self._num_outputs = num_outputs
        return self._QuantileBotorchModel(self)

    @property
    def model(self):
        if not hasattr(self, "_model"):
            raise RuntimeError("Call fit() before accessing .model")
        return self._model
