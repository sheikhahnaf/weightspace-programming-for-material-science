"""GP with a written network in its mean, fitted jointly (BoTorch / GPyTorch).

`arms.gp_with_prior` is a two-stage fit: a and b of the mean a*m(x) + b by least
squares, then a constant-mean GP on the residuals. The uncertainty of a and b never
reaches the error bars. Two joint versions:

map       The mean is gpytorch.means.LinearMean on the network's output, so a and b are
          hyperparameters learned together with the kernel by maximising the marginal
          likelihood (a starts at 1, b at 0, weak Normal priors N(1, 1) and N(0, 1) in
          standardised units). a and b are still point estimates.
marginal  The mean is the network's output itself (a = 1) and the kernel gets an extra
          linear term on the network's output plus a constant: this is the exact
          marginal over Gaussian a and b, so their uncertainty is in the posterior.

Both use SingleTaskGP with the same input kernel and Normalize transform as the plain
baseline (`baselines.fit_gp`). The network's output enters as one extra input column,
standardised with the labels' mean and std; the input kernel does not see it.
"""

from __future__ import annotations

import numpy as np
import torch

from .baselines import Prepared


def _modules(d: int, kind: str):
    import gpytorch
    from botorch.models.utils.gpytorch_modules import get_covar_module_with_dim_scaled_prior
    from gpytorch.kernels import LinearKernel, ScaleKernel
    from gpytorch.means import LinearMean, Mean

    x_kernel = get_covar_module_with_dim_scaled_prior(ard_num_dims=d, active_dims=tuple(range(d)))

    class NetworkMean(Mean):
        """a * m + b on the last input column (GPyTorch LinearMean), or m itself."""

        def __init__(self, learn: bool):
            super().__init__()
            self.learn = learn
            if learn:
                self.linear = LinearMean(input_size=1)
                self.linear.weights.data.fill_(1.0)
                self.linear.bias.data.fill_(0.0)
                self.register_prior("slope_prior", gpytorch.priors.NormalPrior(1.0, 1.0), lambda m: m.linear.weights)
                self.register_prior("offset_prior", gpytorch.priors.NormalPrior(0.0, 1.0), lambda m: m.linear.bias)

        def forward(self, x):
            m = x[..., -1:]
            return self.linear(m) if self.learn else m.squeeze(-1)

    if kind == "map":
        return NetworkMean(True), x_kernel
    if kind == "marginal":
        slope = ScaleKernel(LinearKernel(active_dims=(d,)))
        slope.outputscale = 1.0
        offset = ScaleKernel(gpytorch.kernels.ConstantKernel()) if hasattr(gpytorch.kernels, "ConstantKernel") else None
        kernel = x_kernel + slope if offset is None else x_kernel + slope + offset
        return NetworkMean(False), kernel
    raise ValueError(f"kind must be 'map' or 'marginal', not {kind!r}")


def gp_joint_prior(data: Prepared, m_train: np.ndarray, m_test: np.ndarray, kind: str = "map"):
    """Predictive mean and std in physical units, and the fitted slope (None for 'marginal')."""
    from botorch.fit import fit_gpytorch_mll
    from botorch.models import SingleTaskGP
    from botorch.models.transforms.input import Normalize
    from gpytorch.mlls import ExactMarginalLogLikelihood

    d = data.U_train.shape[1]
    z = lambda m: (np.asarray(m, dtype=float) - data.y_mean) / data.y_std
    X = torch.tensor(np.column_stack([data.U_train, z(m_train)]), dtype=torch.float64)
    Xs = torch.tensor(np.column_stack([data.U_test, z(m_test)]), dtype=torch.float64)
    t = torch.tensor((data.y_train - data.y_mean) / data.y_std, dtype=torch.float64).unsqueeze(-1)
    mean_module, covar_module = _modules(d, kind)
    model = SingleTaskGP(X, t, mean_module=mean_module, covar_module=covar_module,
                         input_transform=Normalize(d=d + 1, indices=list(range(d))), outcome_transform=None)
    fit_gpytorch_mll(ExactMarginalLogLikelihood(model.likelihood, model))
    model.eval()
    with torch.no_grad():
        posterior = model.posterior(Xs, observation_noise=True)
    mean = posterior.mean.detach().squeeze(-1).numpy() * data.y_std + data.y_mean
    std = posterior.variance.detach().squeeze(-1).clamp_min(1e-12).sqrt().numpy() * data.y_std
    slope = float(model.mean_module.linear.weights.detach().squeeze()) if kind == "map" else None
    return mean, std, slope
