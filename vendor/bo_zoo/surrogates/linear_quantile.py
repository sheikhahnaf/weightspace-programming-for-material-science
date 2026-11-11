"""Linear quantile regression surrogate (sklearn QuantileRegressor).

Fits three separate linear models for q_low, 0.5, and q_high.

**Not differentiable** → only works with SAOptimizer.
"""

from __future__ import annotations

import numpy as np

from bo_zoo.surrogates.base import QuantileModelWrapper


class LinearQuantileSurrogate(QuantileModelWrapper):
    """sklearn QuantileRegressor (linear) wrapped as a BoTorch surrogate.

    Args:
        quantile_low:  Lower quantile (default 0.16).
        quantile_high: Upper quantile (default 0.84).
        alpha:         L1 regularisation strength (default 0.0 = no regularisation).
        qr_kwargs:     Additional kwargs forwarded to ``QuantileRegressor``.
    """

    def __init__(
        self,
        quantile_low: float = 0.16,
        quantile_high: float = 0.84,
        alpha: float = 0.0,
        **qr_kwargs,
    ):
        self.quantile_low = quantile_low
        self.quantile_high = quantile_high
        self.alpha = alpha
        self.qr_kwargs = qr_kwargs
        self._reg_low = None
        self._reg_med = None
        self._reg_high = None
        self._model = None

    def fit(self, train_X, train_Y):
        import torch
        from sklearn.linear_model import QuantileRegressor

        if isinstance(train_X, torch.Tensor):
            train_X = train_X.detach().cpu().numpy()
        if isinstance(train_Y, torch.Tensor):
            train_Y = train_Y.detach().cpu().numpy()

        train_X = np.asarray(train_X, dtype=float)
        train_Y = np.asarray(train_Y, dtype=float).ravel()

        common = dict(alpha=self.alpha, **self.qr_kwargs)
        self._reg_low = QuantileRegressor(quantile=self.quantile_low, **common).fit(
            train_X, train_Y
        )
        self._reg_med = QuantileRegressor(quantile=0.5, **common).fit(
            train_X, train_Y
        )
        self._reg_high = QuantileRegressor(quantile=self.quantile_high, **common).fit(
            train_X, train_Y
        )

        self._model = self._make_botorch_model()
        return self._model

    def _predict_quantiles(self, X_np):
        q_low = self._reg_low.predict(X_np)
        q_med = self._reg_med.predict(X_np)
        q_high = self._reg_high.predict(X_np)
        std = np.maximum((q_high - q_low) / 2.0, 1e-6)
        q_low = q_med - std
        q_high = q_med + std
        return q_low, q_med, q_high

    @property
    def model(self):
        if self._model is None:
            raise RuntimeError("Call fit() before accessing .model")
        return self._model
