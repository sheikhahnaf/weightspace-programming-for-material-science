"""Gradient-boosting quantile surrogates.

Two variants:
- ``GBRQuantileSurrogate``: sklearn ``GradientBoostingRegressor`` with
  ``loss='quantile'``.  Fits three separate models for q=low/0.5/high.
- ``XGBQuantileSurrogate``: XGBoost with ``reg:quantileerror`` objective.

Both are **not differentiable** and only work with SAOptimizer.
"""

from __future__ import annotations

import numpy as np

from bo_zoo.surrogates.base import QuantileModelWrapper


class GBRQuantileSurrogate(QuantileModelWrapper):
    """sklearn GradientBoostingRegressor with quantile loss.

    Fits three GBR models for quantile_low, 0.5, and quantile_high.

    Args:
        quantile_low:  Lower quantile (default 0.16 ≈ μ − σ for Gaussian).
        quantile_high: Upper quantile (default 0.84 ≈ μ + σ for Gaussian).
        n_estimators:  Number of boosting stages.
        max_depth:     Maximum depth of individual regression estimators.
        gbr_kwargs:    Additional kwargs forwarded to GradientBoostingRegressor.
    """

    def __init__(
        self,
        quantile_low: float = 0.16,
        quantile_high: float = 0.84,
        n_estimators: int = 100,
        max_depth: int = 3,
        **gbr_kwargs,
    ):
        self.quantile_low = quantile_low
        self.quantile_high = quantile_high
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.gbr_kwargs = gbr_kwargs
        self._reg_low = None
        self._reg_med = None
        self._reg_high = None
        self._model = None

    def fit(self, train_X, train_Y):
        import torch
        from sklearn.ensemble import GradientBoostingRegressor

        if isinstance(train_X, torch.Tensor):
            train_X = train_X.detach().cpu().numpy()
        if isinstance(train_Y, torch.Tensor):
            train_Y = train_Y.detach().cpu().numpy()

        train_X = np.asarray(train_X, dtype=float)
        train_Y = np.asarray(train_Y, dtype=float).ravel()

        common = dict(
            n_estimators=self.n_estimators,
            max_depth=self.max_depth,
            **self.gbr_kwargs,
        )
        self._reg_low = GradientBoostingRegressor(
            loss="quantile", alpha=self.quantile_low, **common
        ).fit(train_X, train_Y)
        self._reg_med = GradientBoostingRegressor(
            loss="quantile", alpha=0.5, **common
        ).fit(train_X, train_Y)
        self._reg_high = GradientBoostingRegressor(
            loss="quantile", alpha=self.quantile_high, **common
        ).fit(train_X, train_Y)

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


class XGBQuantileSurrogate(QuantileModelWrapper):
    """XGBoost surrogate with quantile regression (``reg:quantileerror``).

    Fits three XGBoost models for q_low, 0.5, and q_high.

    Args:
        quantile_low:  Lower quantile.
        quantile_high: Upper quantile.
        n_estimators:  Boosting rounds.
        max_depth:     Tree depth.
        xgb_kwargs:    Additional XGBRegressor kwargs.

    Raises:
        ImportError: If ``xgboost`` is not installed.
    """

    def __init__(
        self,
        quantile_low: float = 0.16,
        quantile_high: float = 0.84,
        n_estimators: int = 100,
        max_depth: int = 3,
        **xgb_kwargs,
    ):
        self.quantile_low = quantile_low
        self.quantile_high = quantile_high
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.xgb_kwargs = xgb_kwargs
        self._reg_low = None
        self._reg_med = None
        self._reg_high = None
        self._model = None

    def _import_xgb(self):
        try:
            from xgboost import XGBRegressor
            return XGBRegressor
        except ImportError as e:
            raise ImportError(
                "xgboost is not installed.  Install it with:\n"
                "    pip install xgboost\n"
                "or:\n"
                "    pip install bo_zoo[xgb]"
            ) from e

    def fit(self, train_X, train_Y):
        import torch

        if isinstance(train_X, torch.Tensor):
            train_X = train_X.detach().cpu().numpy()
        if isinstance(train_Y, torch.Tensor):
            train_Y = train_Y.detach().cpu().numpy()

        train_X = np.asarray(train_X, dtype=float)
        train_Y = np.asarray(train_Y, dtype=float).ravel()

        XGBRegressor = self._import_xgb()
        common = dict(
            objective="reg:quantileerror",
            n_estimators=self.n_estimators,
            max_depth=self.max_depth,
            **self.xgb_kwargs,
        )
        self._reg_low = XGBRegressor(quantile_alpha=self.quantile_low, **common).fit(
            train_X, train_Y
        )
        self._reg_med = XGBRegressor(quantile_alpha=0.5, **common).fit(
            train_X, train_Y
        )
        self._reg_high = XGBRegressor(quantile_alpha=self.quantile_high, **common).fit(
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
