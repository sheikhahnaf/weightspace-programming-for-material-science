"""FakeModel + ExactVariancePosterior for O(1) SA lookup.

After training a DGP (or any expensive model), run ``model.posterior(all_candidates)``
once to precompute mean + variance for every candidate.  Store in a ``FakeModel``
so the SA optimizer can call ``.posterior()`` in O(1) via hash-table lookup instead
of running the full model each step.

Ported and cleaned from anneal.py (HTMDEC-C3-IT2 reference, lines 1661–1760).
"""

from __future__ import annotations

import torch
from torch import Tensor

from gpytorch.distributions import MultitaskMultivariateNormal
from botorch.posteriors.gpytorch import GPyTorchPosterior
from linear_operator.operators import DiagLinearOperator


class ExactVariancePosterior(GPyTorchPosterior):
    """GPyTorchPosterior subclass that preserves exact precomputed mean/variance.

    Sampling uses the exact variance rather than the MVN's diagonal, so the SA
    optimizer sees accurate uncertainty without any approximation drift.

    Args:
        mvn:           A ``MultitaskMultivariateNormal`` (used for shape and rsample).
        true_mean:     Precomputed mean tensor ``(batch, q, num_obj)``.
        true_variance: Precomputed variance tensor ``(batch, q, num_obj)``.
    """

    def __init__(
        self,
        mvn: MultitaskMultivariateNormal,
        true_mean: Tensor,
        true_variance: Tensor,
    ):
        super().__init__(mvn)
        self._true_mean = true_mean
        self._true_variance = true_variance

    @property
    def mean(self) -> Tensor:
        return self._true_mean

    @property
    def variance(self) -> Tensor:
        return self._true_variance

    def rsample(self, sample_shape: torch.Size = torch.Size([])) -> Tensor:
        """Sample using the exact stored variance (not the MVN's)."""
        base_samples = super().rsample(sample_shape)
        shape = base_samples.shape
        eps = torch.randn(shape, device=self.device, dtype=self.dtype)
        return self._true_mean + eps * torch.sqrt(self._true_variance.clamp(min=1e-12))


class FakeModel(torch.nn.Module):
    """Thin BoTorch-compatible model with O(1) lookup from precomputed posteriors.

    Usage pattern
    -------------
    1. Train your (expensive) DGP model.
    2. Precompute posteriors over *all* candidates:

       .. code-block:: python

           with torch.no_grad():
               post = dgp_model.posterior(all_candidates)
               mean_all = post.mean        # (N, num_obj)
               var_all  = post.variance    # (N, num_obj)

    3. Build FakeModel:

       .. code-block:: python

           fake = FakeModel(all_candidates, mean_all, var_all, num_obj=num_obj)

    4. Pass ``fake`` to the acquisition function / SAOptimizer instead of the DGP.

    Args:
        X_choices:  ``(N, d)`` tensor of all candidate points (unscaled or scaled —
                    must match the inputs the SA optimizer will query).
        mean_all:   ``(N, num_obj)`` precomputed posterior means.
        var_all:    ``(N, num_obj)`` precomputed posterior variances.
        num_obj:    Number of objectives.
    """

    def __init__(
        self,
        X_choices: Tensor,
        mean_all: Tensor,
        var_all: Tensor,
        num_obj: int,
    ):
        super().__init__()
        self.register_buffer("X_choices", X_choices.to(dtype=torch.float64))
        self.register_buffer("mean_all", mean_all.to(dtype=torch.float64))
        self.register_buffer("var_all", var_all.to(dtype=torch.float64))
        self.num_obj = num_obj
        # Cache numpy array for fast indexing
        self._X_np = X_choices.detach().cpu().numpy()

    # ------------------------------------------------------------------
    # BoTorch Model interface
    # ------------------------------------------------------------------

    def posterior(
        self,
        X_eval: Tensor,
        observation_noise: bool = False,
        **kwargs,
    ) -> ExactVariancePosterior:
        """Return precomputed posterior for *X_eval* via exact hash-table lookup.

        Args:
            X_eval: ``(q, d)`` or ``(batch, q, d)`` query tensor.

        Returns:
            ``ExactVariancePosterior`` with precomputed mean and variance.
        """
        if X_eval.ndim > 2:
            batch_shape = X_eval.shape[:-2]
            q = X_eval.shape[-2]
            X_flat = X_eval.reshape(-1, X_eval.shape[-1])
        else:
            batch_shape = torch.Size([1])
            q = X_eval.shape[0]
            X_flat = X_eval

        idxs = self._lookup_indices(X_flat)

        m_orig = self.mean_all[idxs]  # (b*q, num_obj)
        v_orig = self.var_all[idxs]   # (b*q, num_obj)
        v_orig = v_orig.clamp(min=1e-12)

        if len(batch_shape) > 0 and (batch_shape[0] if batch_shape else 1) > 1:
            b = batch_shape.numel() if hasattr(batch_shape, "numel") else batch_shape[0]
            m_reshaped = m_orig.reshape(*batch_shape, q, self.num_obj)
            v_reshaped = v_orig.reshape(*batch_shape, q, self.num_obj)
        else:
            m_reshaped = m_orig.reshape(1, q, self.num_obj)
            v_reshaped = v_orig.reshape(1, q, self.num_obj)

        t = self.num_obj
        b_actual = m_reshaped.shape[0]
        var_vec = v_orig.reshape(-1)
        cov_lazy = DiagLinearOperator(var_vec)

        try:
            mvn = MultitaskMultivariateNormal(
                mean=m_reshaped,
                covariance_matrix=cov_lazy.reshape(b_actual, q * t, q * t),
                interleaved=False,
            )
        except Exception:
            # Fallback: simple diagonal MVN
            mvn = MultitaskMultivariateNormal(
                mean=m_reshaped,
                covariance_matrix=DiagLinearOperator(
                    v_reshaped.reshape(b_actual, -1)
                ),
                interleaved=False,
            )

        return ExactVariancePosterior(mvn, m_reshaped, v_reshaped)

    def eval(self):
        return self

    def train(self, mode: bool = True):
        return self

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _lookup_indices(self, X_flat: Tensor) -> Tensor:
        """Find row indices in X_choices matching each row of X_flat (exact)."""
        X_np = X_flat.detach().cpu().numpy()
        kc = self._X_np
        idxs = []
        for x in X_np:
            matches = (kc == x).all(axis=1)
            if not matches.any():
                # Fallback to nearest-neighbour if exact match fails (float drift)
                import numpy as np
                dists = ((kc - x) ** 2).sum(axis=1)
                idxs.append(int(dists.argmin()))
            else:
                idxs.append(int(matches.argmax()))
        return torch.tensor(idxs, device=self.mean_all.device, dtype=torch.long)

    @classmethod
    def from_model(
        cls,
        model,
        all_candidates: Tensor,
        num_obj: int,
    ) -> "FakeModel":
        """Convenience constructor: precompute posteriors from a trained model.

        Args:
            model:          Any BoTorch model with a ``.posterior()`` method.
            all_candidates: ``(N, d)`` tensor of candidates to precompute over.
            num_obj:        Number of objectives.

        Returns:
            Configured ``FakeModel``.
        """
        model.eval()
        with torch.no_grad():
            post = model.posterior(all_candidates.to(dtype=torch.float64))
            mean_all = post.mean.detach()     # (N, num_obj)
            var_all = post.variance.detach()  # (N, num_obj)

        # Squeeze batch dim if model added one
        if mean_all.ndim == 3:
            mean_all = mean_all.squeeze(0)
        if var_all.ndim == 3:
            var_all = var_all.squeeze(0)

        return cls(all_candidates, mean_all, var_all, num_obj=num_obj)
