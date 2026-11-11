"""TabPFN surrogate wrapped as a BoTorch-compatible model.

TabPFN is a Transformer trained as a prior-fitted network that performs
in-context learning for tabular data.  Key limitations:
  - Max ~10 K training samples, ~500 features.
  - **Not differentiable** → only works with SAOptimizer, not SLSQPOptimizer.
  - Quantile prediction API is version-sensitive; bootstrap fallback is used.

Install: ``pip install tabpfn``
"""

from __future__ import annotations

from typing import Optional

import numpy as np

from bo_zoo.surrogates.base import QuantileModelWrapper, SurrogateBase


_TABPFN_MAX_SAMPLES = 10_000
_TABPFN_MAX_FEATURES = 500


class TabPFNSurrogate(QuantileModelWrapper):
    """BoTorch-compatible surrogate wrapping TabPFN with quantile uncertainty.

    Uncertainty estimation strategy (in order of preference):
    1. Native ``output_type="quantiles"`` if the installed TabPFN version
       supports it.
    2. Bootstrap with ``n_bootstrap`` fits on random sub-samples.

    The std estimate is ``(q_high - q_low) / 2``, clamped to ``1e-6``.

    Args:
        n_bootstrap:     Number of bootstrap resamples (used if quantile API
                         is unavailable).
        quantile_low:    Lower quantile to predict (default 0.16 ≈ -1 σ).
        quantile_high:   Upper quantile to predict (default 0.84 ≈ +1 σ).
        device:          ``"cpu"`` or ``"cuda"``.
        tabpfn_kwargs:   Additional kwargs forwarded to ``TabPFNClassifier`` /
                         ``TabPFNRegressor``.

    Raises:
        ImportError: If ``tabpfn`` is not installed.
        ValueError:  If training data exceeds TabPFN's limits.
    """

    def __init__(
        self,
        n_bootstrap: int = 10,
        quantile_low: float = 0.16,
        quantile_high: float = 0.84,
        device: str = "cpu",
        **tabpfn_kwargs,
    ):
        self.n_bootstrap = n_bootstrap
        self.quantile_low = quantile_low
        self.quantile_high = quantile_high
        self.device = device
        self.tabpfn_kwargs = tabpfn_kwargs
        self._regressor = None
        self._train_X: Optional[np.ndarray] = None
        self._train_Y: Optional[np.ndarray] = None
        self._model = None

    def _import_tabpfn(self):
        # Ensure HuggingFace is authenticated BEFORE importing TabPFN so that
        # model-weight downloads succeed on HPC nodes without ~/.huggingface
        # token file. Uses HF_TOKEN env var (set via conda activate hook or
        # hardcoded fallback).
        import os
        hf_token = os.environ.get("HF_TOKEN")
        if hf_token is None:
            # Fallback: hardcoded token (same one used project-wide in engine.py)
            hf_token = __import__("os").environ.get("HF_TOKEN", "")
            os.environ["HF_TOKEN"] = hf_token
        try:
            from huggingface_hub import login as _hf_login
            _hf_login(token=hf_token, add_to_git_credential=False)
        except Exception:
            # Login failure is non-fatal; HF_TOKEN env var alone often suffices
            pass
        try:
            from tabpfn import TabPFNRegressor
            return TabPFNRegressor
        except ImportError as e:
            raise ImportError(
                "TabPFN is not installed.  Install it with:\n"
                "    pip install tabpfn\n"
                "or:\n"
                "    pip install bo_zoo[tabpfn]"
            ) from e

    def fit(self, train_X, train_Y):
        """Fit TabPFN on training data.

        Args:
            train_X: ``(n, d)`` array or tensor.
            train_Y: ``(n, 1)`` or ``(n,)`` array or tensor (single-output).

        Returns:
            Self's internal botorch-compatible model wrapper.
        """
        import torch

        if isinstance(train_X, torch.Tensor):
            train_X = train_X.detach().cpu().numpy()
        if isinstance(train_Y, torch.Tensor):
            train_Y = train_Y.detach().cpu().numpy()

        train_X = np.asarray(train_X, dtype=float)
        train_Y = np.asarray(train_Y, dtype=float).ravel()

        n, d = train_X.shape
        if n > _TABPFN_MAX_SAMPLES:
            raise ValueError(
                f"TabPFN supports at most {_TABPFN_MAX_SAMPLES} training samples, "
                f"but got {n}.  Consider sub-sampling your data."
            )
        if d > _TABPFN_MAX_FEATURES:
            raise ValueError(
                f"TabPFN supports at most {_TABPFN_MAX_FEATURES} features, "
                f"but got {d}.  Apply dimensionality reduction first."
            )

        TabPFNRegressor = self._import_tabpfn()
        self._regressor = TabPFNRegressor(device=self.device, **self.tabpfn_kwargs)
        self._regressor.fit(train_X, train_Y)
        self._train_X = train_X
        self._train_Y = train_Y
        self._model = self._make_botorch_model()
        return self._model

    # ------------------------------------------------------------------
    # QuantileModelWrapper implementation
    # ------------------------------------------------------------------

    def _predict_quantiles(
        self, X_np: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Return (q_low, q_med, q_high) predictions for X_np."""
        if self._regressor is None:
            raise RuntimeError("Call fit() before predicting.")

        # Try native quantile API — single call for all three quantiles (3× faster)
        try:
            results = self._regressor.predict(
                X_np,
                output_type="quantiles",
                quantiles=[self.quantile_low, 0.5, self.quantile_high],
            )
            q_low, q_med, q_high = results[0], results[1], results[2]
        except (TypeError, AttributeError, KeyError, NotImplementedError):
            # Fallback: bootstrap (only for known API-mismatch errors)
            q_low, q_med, q_high = self._bootstrap_quantiles(X_np)

        q_low = np.asarray(q_low).ravel()
        q_med = np.asarray(q_med).ravel()
        q_high = np.asarray(q_high).ravel()

        # Guard against zero-width intervals
        std = np.maximum((q_high - q_low) / 2.0, 1e-6)
        q_low = q_med - std
        q_high = q_med + std

        return q_low, q_med, q_high

    def _bootstrap_quantiles(
        self, X_np: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Bootstrap uncertainty estimation fallback."""
        TabPFNRegressor = self._import_tabpfn()
        n_train = len(self._train_X)
        preds = []
        rng = np.random.default_rng(42)
        for _ in range(self.n_bootstrap):
            idx = rng.choice(n_train, size=n_train, replace=True)
            reg = TabPFNRegressor(device=self.device, **self.tabpfn_kwargs)
            reg.fit(self._train_X[idx], self._train_Y[idx])
            preds.append(reg.predict(X_np))
        preds = np.stack(preds, axis=0)  # (n_bootstrap, n_test)
        q_low = np.quantile(preds, self.quantile_low, axis=0)
        q_med = np.median(preds, axis=0)
        q_high = np.quantile(preds, self.quantile_high, axis=0)
        return q_low, q_med, q_high

    @property
    def model(self):
        if self._model is None:
            raise RuntimeError("Call fit() before accessing .model")
        return self._model
