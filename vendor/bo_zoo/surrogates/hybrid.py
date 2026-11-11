"""HybridPosterior: DGP mean + GP covariance.

Ported from anneal.py (HTMDEC-C3-IT2 reference).
"""

from __future__ import annotations

import torch
from torch import Tensor

from gpytorch.distributions import MultitaskMultivariateNormal
from botorch.posteriors.gpytorch import GPyTorchPosterior


class HybridPosterior(GPyTorchPosterior):
    """Custom posterior combining DGP mean with GP covariance.

    This is used in the HTMDEC-C3-IT2 reference: after training both a DGP
    and a GP on the same data, the DGP mean (more expressive) is combined
    with the GP covariance (better uncertainty calibration).

    Args:
        dgp_posterior: Posterior from the deep GP (used for its mean).
        gp_posterior:  Posterior from the shallow GP (used for its covariance).
    """

    def __init__(
        self,
        dgp_posterior: GPyTorchPosterior,
        gp_posterior: GPyTorchPosterior,
    ):
        self.dgp_posterior = dgp_posterior
        self.gp_posterior = gp_posterior

        dgp_dist = dgp_posterior.distribution
        loc = dgp_dist.mean
        if loc.dim() < 2:
            loc = loc.unsqueeze(-1)

        gp_dist = gp_posterior.distribution
        covar = gp_dist.lazy_covariance_matrix
        interleaved = getattr(gp_dist, "_interleaved", True)

        hybrid_dist = MultitaskMultivariateNormal(loc, covar, False, interleaved)
        super().__init__(hybrid_dist)

    @property
    def mvn(self) -> MultitaskMultivariateNormal:
        """Expose the hybrid distribution for samplers."""
        return self.distribution

    @property
    def mean(self) -> Tensor:
        """Use the DGP posterior mean (more expressive)."""
        return self.dgp_posterior.mean

    @property
    def variance(self) -> Tensor:
        """GP posterior variance, broadcast to DGP mean shape if needed."""
        gp_var = self.gp_posterior.variance
        dgp_mean = self.mean
        if gp_var.shape != dgp_mean.shape:
            gp_var = gp_var.expand_as(dgp_mean)
        return gp_var

    def rsample(self, sample_shape: torch.Size | None = None) -> Tensor:
        if sample_shape is None:
            sample_shape = torch.Size([1])
        return self.distribution.rsample(sample_shape=sample_shape)

    def rsample_from_base_samples(
        self, sample_shape: torch.Size, base_samples: Tensor
    ) -> Tensor:
        return super().rsample_from_base_samples(sample_shape, base_samples)
