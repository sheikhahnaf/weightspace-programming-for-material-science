"""ModelList wrapper for quantile surrogates — unified single/multi-output API.

Wraps N independent QuantileModelWrapper instances, one per output column.
Supports heterotopic NaN — each sub-surrogate is fit only on observed rows
for its task.  All constituent surrogates are non-differentiable → requires
SAOptimizer.
"""

from __future__ import annotations

import numpy as np
import torch
from torch import Tensor

from gpytorch.distributions import MultitaskMultivariateNormal
from botorch.posteriors.gpytorch import GPyTorchPosterior

from bo_zoo.surrogates.base import QuantileModelWrapper, SurrogateBase


class ModelListQuantileSurrogate(SurrogateBase):
    """Independent quantile surrogate per output column.

    Analogous to ModelListGPSurrogate but for non-GP quantile models.
    Supports heterotopic NaN: each sub-surrogate sees only its observed rows.

    Args:
        surrogate_cls:    Any QuantileModelWrapper subclass (not instance).
        surrogate_kwargs: Forwarded to each surrogate_cls() constructor.

    Raises:
        TypeError:  If surrogate_cls is not a QuantileModelWrapper subclass.
        ValueError: If any output column has no observed entries.
    """

    def __init__(self, surrogate_cls: type, **surrogate_kwargs):
        if not issubclass(surrogate_cls, QuantileModelWrapper):
            raise TypeError(
                f"{surrogate_cls.__name__} must be a QuantileModelWrapper subclass."
            )
        self.surrogate_cls = surrogate_cls
        self.surrogate_kwargs = surrogate_kwargs
        self._surrogates: list[QuantileModelWrapper] = []
        self._model = None

    def fit(self, train_X: Tensor, train_Y: Tensor):
        """Fit one sub-surrogate per output column, NaN-aware.

        Args:
            train_X: ``(n, d)`` float64 tensor.
            train_Y: ``(n, m)`` float64 tensor (NaN for missing tasks).

        Returns:
            Fitted ``_ModelListQuantileBoTorchModel``.
        """
        X_np = (
            train_X.detach().cpu().numpy()
            if isinstance(train_X, Tensor)
            else np.asarray(train_X, dtype=float)
        )
        Y_np = (
            train_Y.detach().cpu().numpy()
            if isinstance(train_Y, Tensor)
            else np.asarray(train_Y, dtype=float)
        )
        if Y_np.ndim == 1:
            Y_np = Y_np[:, None]

        m = Y_np.shape[1]
        self._surrogates = []
        for j in range(m):
            col = Y_np[:, j]
            mask = ~np.isnan(col)
            if not mask.any():
                raise ValueError(
                    f"Output column {j} has no observed (non-NaN) entries."
                )
            X_j = torch.tensor(X_np[mask], dtype=torch.float64)
            Y_j = torch.tensor(col[mask, None], dtype=torch.float64)
            s = self.surrogate_cls(**self.surrogate_kwargs)
            s.fit(X_j, Y_j)
            self._surrogates.append(s)

        self._model = _ModelListQuantileBoTorchModel(self._surrogates, m)
        return self._model

    @property
    def model(self):
        if self._model is None:
            raise RuntimeError("Call fit() before accessing .model")
        return self._model


class _ModelListQuantileBoTorchModel:
    """Minimal BoTorch-compatible model combining m quantile sub-models.

    Posterior shape contract (GPyTorchPosterior wrapping MultitaskMVN,
    interleaved=False):
        2D input  ``(q, d)``     → ``.mean`` ``(q, m)``,    ``.variance`` ``(q, m)``
        3D input  ``(b, q, d)``  → ``.mean`` ``(b, q, m)``, ``.variance`` ``(b, q, m)``
    """

    def __init__(self, surrogates: list, num_outputs: int):
        self._surrogates = surrogates
        self.num_outputs = num_outputs

    def posterior(self, X: Tensor, **kwargs) -> GPyTorchPosterior:
        device = X.device  # propagate device so posterior lives on same device as acqf
        X_np = X.detach().cpu().numpy()
        batched = X_np.ndim == 3
        if batched:
            batch_size, q, d = X_np.shape
            X_flat = X_np.reshape(-1, d)
        else:
            batch_size, q = 1, X_np.shape[0]
            X_flat = X_np

        m = self.num_outputs
        n = X_flat.shape[0]  # batch_size * q

        means_np = np.empty((n, m), dtype=float)
        vars_np = np.empty((n, m), dtype=float)

        for j, s in enumerate(self._surrogates):
            q_low, q_med, q_high = s._predict_quantiles(X_flat)
            q_med = np.asarray(q_med).ravel()
            q_low = np.asarray(q_low).ravel()
            q_high = np.asarray(q_high).ravel()
            std = np.maximum((q_high - q_low) / 2.0, 1e-6)
            means_np[:, j] = q_med
            vars_np[:, j] = std ** 2

        mean_t = torch.tensor(means_np, dtype=torch.float64, device=device)
        var_t = torch.tensor(vars_np, dtype=torch.float64, device=device)

        # Reshape to (..., q, m) — with batch dim only if input was 3D
        if batched:
            mean_t = mean_t.reshape(batch_size, q, m)
            var_t = var_t.reshape(batch_size, q, m)
        else:
            mean_t = mean_t.reshape(q, m)
            var_t = var_t.reshape(q, m)

        # Block-diagonal covariance, interleaved=False:
        # ordering is [all_points_task_0, all_points_task_1, ...]
        *batch_dims, n_pts, _ = mean_t.shape
        cov = torch.zeros(*batch_dims, n_pts * m, n_pts * m, dtype=torch.float64, device=device)
        for j in range(m):
            s_idx, e_idx = j * n_pts, (j + 1) * n_pts
            cov[..., s_idx:e_idx, s_idx:e_idx] = torch.diag_embed(var_t[..., j])

        dist = MultitaskMultivariateNormal(
            mean_t, covariance_matrix=cov, interleaved=False
        )
        return GPyTorchPosterior(dist)

    def eval(self):
        return self

    def train(self, mode: bool = True):
        return self
