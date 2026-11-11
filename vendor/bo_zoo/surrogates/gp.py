"""Standard GP surrogates wrapping BoTorch SingleTaskGP and ModelListGP."""

from __future__ import annotations

import math
import torch
from torch import Tensor

from botorch.models import SingleTaskGP, ModelListGP
from botorch.fit import fit_gpytorch_mll
from gpytorch.kernels import RBFKernel, ScaleKernel
from gpytorch.mlls import ExactMarginalLogLikelihood, SumMarginalLogLikelihood
from gpytorch.priors import GammaPrior

from bo_zoo.surrogates.base import SurrogateBase


def _make_default_covar(d: int, m: int = 1) -> ScaleKernel:
    """Dimensionality-aware RBF covariance module.

    Prior: GammaPrior(alpha=3.0, rate=6.0/sqrt(d)).
    Prior mean = alpha/rate = 3.0 * sqrt(d) / 6.0 = sqrt(d)/2.
    Wider prior for higher-d spaces: d=2 -> mean~0.71; d=30 -> mean~2.74.

    Args:
        d: Number of input dimensions.
        m: Number of output objectives. Sets batch_shape=(m,) when m > 1.
    """
    batch = torch.Size([m]) if m > 1 else torch.Size([])
    ls_prior = GammaPrior(3.0, 6.0 / math.sqrt(d))
    rbf = RBFKernel(lengthscale_prior=ls_prior, batch_shape=batch)
    return ScaleKernel(rbf, batch_shape=batch)


class GPSurrogate(SurrogateBase):
    """Single-output or multi-output exact GP using ``SingleTaskGP``.

    For a single-output problem (``train_Y.shape[1] == 1``) this wraps
    ``SingleTaskGP`` directly.  For multi-output it still uses a single
    ``SingleTaskGP`` with batched outputs (``batch_shape = (m,)``), which
    BoTorch handles natively.
    """

    def __init__(self):
        self._model: SingleTaskGP | None = None

    def fit(self, train_X: Tensor, train_Y: Tensor) -> SingleTaskGP:
        """Train GP via exact marginal likelihood optimisation.

        Args:
            train_X: ``(n, d)`` float64 tensor.
            train_Y: ``(n, m)`` float64 tensor (no NaN).

        Returns:
            Fitted ``SingleTaskGP``.
        """
        train_X = train_X.to(dtype=torch.float64)
        train_Y = train_Y.to(dtype=torch.float64)

        d = train_X.shape[-1]
        m = train_Y.shape[-1]
        covar_module = _make_default_covar(d, m)
        self._model = SingleTaskGP(train_X, train_Y, covar_module=covar_module)
        mll = ExactMarginalLogLikelihood(self._model.likelihood, self._model)
        fit_gpytorch_mll(mll)
        self._model.eval()
        return self._model

    @property
    def model(self) -> SingleTaskGP:
        if self._model is None:
            raise RuntimeError("Call fit() before accessing .model")
        return self._model


class ModelListGPSurrogate(SurrogateBase):
    """Multi-output GP using ``ModelListGP`` (one independent GP per output).

    Handles heterotopic data (NaN values in ``train_Y``) by fitting each
    output GP only on the rows where that output is observed.

    Args:
        None

    Raises:
        RuntimeError: If ``fit()`` has not been called before accessing ``model``.
    """

    def __init__(self):
        self._model: ModelListGP | None = None

    def fit(self, train_X: Tensor, train_Y: Tensor) -> ModelListGP:
        """Fit one ``SingleTaskGP`` per output column and wrap in ``ModelListGP``.

        Args:
            train_X: ``(n, d)`` float64 tensor.
            train_Y: ``(n, m)`` float64 tensor; may contain NaN for missing outputs.

        Returns:
            Fitted ``ModelListGP``.
        """
        train_X = train_X.to(dtype=torch.float64)
        train_Y = train_Y.to(dtype=torch.float64)

        if train_Y.ndim == 1:
            train_Y = train_Y.unsqueeze(-1)

        m = train_Y.shape[1]
        models = []
        for j in range(m):
            col = train_Y[:, j]
            mask = ~torch.isnan(col)
            X_j = train_X[mask]
            Y_j = col[mask].unsqueeze(-1)
            gp_j = SingleTaskGP(X_j, Y_j)
            mll_j = ExactMarginalLogLikelihood(gp_j.likelihood, gp_j)
            fit_gpytorch_mll(mll_j)
            gp_j.eval()
            models.append(gp_j)

        self._model = ModelListGP(*models)
        self._model.eval()
        return self._model

    @property
    def model(self) -> ModelListGP:
        if self._model is None:
            raise RuntimeError("Call fit() before accessing .model")
        return self._model
