"""Bayesian Ridge surrogate (sklearn).

Uncertainty is derived from ``BayesianRidge.predict(return_std=True)``:
the returned ``std`` gives a 1-sigma estimate which is converted to
quantiles as  q_low = μ − std,  q_high = μ + std.

**Not differentiable** → only works with SAOptimizer.
"""

from __future__ import annotations

import numpy as np

from bo_zoo.surrogates.base import QuantileModelWrapper


class BayesianRidgeSurrogate(QuantileModelWrapper):
    """sklearn BayesianRidge wrapped as a BoTorch-compatible surrogate.

    Args:
        br_kwargs: Additional kwargs forwarded to ``BayesianRidge``.
    """

    def __init__(self, **br_kwargs):
        self.br_kwargs = br_kwargs
        self._regressor = None
        self._model = None

    def fit(self, train_X, train_Y):
        import torch
        from sklearn.linear_model import BayesianRidge

        if isinstance(train_X, torch.Tensor):
            train_X = train_X.detach().cpu().numpy()
        if isinstance(train_Y, torch.Tensor):
            train_Y = train_Y.detach().cpu().numpy()

        train_X = np.asarray(train_X, dtype=float)
        train_Y = np.asarray(train_Y, dtype=float).ravel()

        self._regressor = BayesianRidge(**self.br_kwargs)
        self._regressor.fit(train_X, train_Y)
        self._model = self._make_botorch_model()
        return self._model

    def _predict_quantiles(self, X_np):
        mu, std = self._regressor.predict(X_np, return_std=True)
        std = np.maximum(std, 1e-6)
        q_low = mu - std
        q_med = mu
        q_high = mu + std
        return q_low, q_med, q_high

    @property
    def model(self):
        if self._model is None:
            raise RuntimeError("Call fit() before accessing .model")
        return self._model
