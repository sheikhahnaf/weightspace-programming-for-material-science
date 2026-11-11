"""Quantile forest surrogates using the quantile_forest package.

Install: ``pip install quantile-forest``

Both surrogates are **not differentiable** and only work with SAOptimizer.
"""

from __future__ import annotations

import numpy as np

from bo_zoo.surrogates.base import QuantileModelWrapper


class QuantileRFSurrogate(QuantileModelWrapper):
    """Random Forest with quantile regression (quantile_forest package).

    Args:
        quantile_low:  Lower quantile (default 0.16).
        quantile_high: Upper quantile (default 0.84).
        n_estimators:  Number of trees.
        rf_kwargs:     Additional kwargs forwarded to ``RandomForestQuantileRegressor``.

    Raises:
        ImportError: If ``quantile_forest`` is not installed.
    """

    def __init__(
        self,
        quantile_low: float = 0.16,
        quantile_high: float = 0.84,
        n_estimators: int = 100,
        **rf_kwargs,
    ):
        self.quantile_low = quantile_low
        self.quantile_high = quantile_high
        self.n_estimators = n_estimators
        self.rf_kwargs = rf_kwargs
        self._regressor = None
        self._model = None

    def _import(self):
        try:
            from quantile_forest import RandomForestQuantileRegressor
            return RandomForestQuantileRegressor
        except ImportError as e:
            raise ImportError(
                "quantile_forest is not installed.  Install it with:\n"
                "    pip install quantile-forest\n"
                "or:\n"
                "    pip install bo_zoo[forests]"
            ) from e

    def fit(self, train_X, train_Y):
        import torch

        if isinstance(train_X, torch.Tensor):
            train_X = train_X.detach().cpu().numpy()
        if isinstance(train_Y, torch.Tensor):
            train_Y = train_Y.detach().cpu().numpy()

        train_X = np.asarray(train_X, dtype=float)
        train_Y = np.asarray(train_Y, dtype=float).ravel()

        RFC = self._import()
        self._regressor = RFC(n_estimators=self.n_estimators, **self.rf_kwargs)
        self._regressor.fit(train_X, train_Y)
        self._model = self._make_botorch_model()
        return self._model

    def _predict_quantiles(self, X_np):
        q_low = self._regressor.predict(X_np, quantiles=self.quantile_low)
        q_med = self._regressor.predict(X_np, quantiles=0.5)
        q_high = self._regressor.predict(X_np, quantiles=self.quantile_high)
        std = np.maximum((q_high - q_low) / 2.0, 1e-6)
        q_low = q_med - std
        q_high = q_med + std
        return q_low, q_med, q_high

    @property
    def model(self):
        if self._model is None:
            raise RuntimeError("Call fit() before accessing .model")
        return self._model


class ExtraTreesQSurrogate(QuantileModelWrapper):
    """Extra-Trees with quantile regression (quantile_forest package).

    Args:
        quantile_low:  Lower quantile (default 0.16).
        quantile_high: Upper quantile (default 0.84).
        n_estimators:  Number of trees.
        et_kwargs:     Additional kwargs forwarded to ``ExtraTreesQuantileRegressor``.

    Raises:
        ImportError: If ``quantile_forest`` is not installed.
    """

    def __init__(
        self,
        quantile_low: float = 0.16,
        quantile_high: float = 0.84,
        n_estimators: int = 100,
        **et_kwargs,
    ):
        self.quantile_low = quantile_low
        self.quantile_high = quantile_high
        self.n_estimators = n_estimators
        self.et_kwargs = et_kwargs
        self._regressor = None
        self._model = None

    def _import(self):
        try:
            from quantile_forest import ExtraTreesQuantileRegressor
            return ExtraTreesQuantileRegressor
        except ImportError as e:
            raise ImportError(
                "quantile_forest is not installed.  Install it with:\n"
                "    pip install quantile-forest\n"
                "or:\n"
                "    pip install bo_zoo[forests]"
            ) from e

    def fit(self, train_X, train_Y):
        import torch

        if isinstance(train_X, torch.Tensor):
            train_X = train_X.detach().cpu().numpy()
        if isinstance(train_Y, torch.Tensor):
            train_Y = train_Y.detach().cpu().numpy()

        train_X = np.asarray(train_X, dtype=float)
        train_Y = np.asarray(train_Y, dtype=float).ravel()

        ETC = self._import()
        self._regressor = ETC(n_estimators=self.n_estimators, **self.et_kwargs)
        self._regressor.fit(train_X, train_Y)
        self._model = self._make_botorch_model()
        return self._model

    def _predict_quantiles(self, X_np):
        q_low = self._regressor.predict(X_np, quantiles=self.quantile_low)
        q_med = self._regressor.predict(X_np, quantiles=0.5)
        q_high = self._regressor.predict(X_np, quantiles=self.quantile_high)
        std = np.maximum((q_high - q_low) / 2.0, 1e-6)
        q_low = q_med - std
        q_high = q_med + std
        return q_low, q_med, q_high

    @property
    def model(self):
        if self._model is None:
            raise RuntimeError("Call fit() before accessing .model")
        return self._model
