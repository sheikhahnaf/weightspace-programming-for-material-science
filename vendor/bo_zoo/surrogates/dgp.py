"""Deep GP surrogates using gpytorch's DeepGP framework.

Architecture
------------
- ``DGPHiddenLayer`` (DeepGPLayer): Matern(2.5)+ARD hidden layer.
- ``DGPLastLayer`` (ApproximateGP): RBF+LMC output layer.
  Receives a **plain tensor** sampled from the hidden distribution plus
  ``task_indices``, enabling LMCVariationalStrategy to handle heterotopic
  multi-task data (different tasks observed on different subsets of inputs).
  Inheriting from ``ApproximateGP`` (not ``DeepGPLayer``) is intentional: it
  lets ``task_indices`` pass through to LMCVariationalStrategy, which
  ``DeepGPLayer.__call__`` does not support.
- ``MultiTaskDeepGP`` (DeepGP + MultiTaskGPyTorchModel): 2-layer heterotopic
  DGP.  Inheriting from ``MultiTaskGPyTorchModel`` provides ``.posterior()``
  and ``_split_inputs()`` for BoTorch compatibility.
- ``TrueDeepGP`` (DeepGP): configurable-depth, homogeneous multi-output DGP.

Key decisions
-------------
- Manual sampling between layers (reference pattern from anneal.py lines
  367-395): ``hidden_layer`` returns a distribution; we sample from it with
  ``torch.distributions.Normal(...).rsample()`` to obtain a plain tensor
  before calling ``last_layer(tensor, task_indices=...)``.
- Beta=0.5 in VariationalELBO, Adam lr=0.01, patience=50 early stopping.
- ``GaussianLikelihood`` (scalar) for ``MultiTaskDeepGP`` because training
  data is in flattened ``(n_obs_total,)`` format (via ``prepare_multitask_pairs``).
- ``MultitaskGaussianLikelihood`` for ``TrueDeepGP`` (homogeneous multi-output).
"""

from __future__ import annotations

from typing import List, Optional

import torch
import gpytorch
from torch import Tensor
from gpytorch.means import ConstantMean, LinearMean
from gpytorch.kernels import MaternKernel, ScaleKernel, RBFKernel
from gpytorch.variational import VariationalStrategy, CholeskyVariationalDistribution
from gpytorch.distributions import MultivariateNormal, MultitaskMultivariateNormal
from gpytorch.models.deep_gps import DeepGPLayer, DeepGP
from gpytorch.mlls import DeepApproximateMLL, VariationalELBO
from gpytorch.likelihoods import GaussianLikelihood, MultitaskGaussianLikelihood

from botorch.posteriors.gpytorch import GPyTorchPosterior

from bo_zoo.surrogates.base import SurrogateBase


# ---------------------------------------------------------------------------
# Layer building blocks
# ---------------------------------------------------------------------------


class DGPHiddenLayer(DeepGPLayer):
    """Hidden layer for a Deep GP.

    Standard ``DeepGPLayer`` with Matern(nu=2.5)+ARD kernel.  Its
    ``__call__`` handles distribution inputs from upstream layers and samples
    from them before running ``forward()``.

    Args:
        input_dims:   Input dimensionality.
        output_dims:  Number of latent GPs (= output dims of this layer).
        num_inducing: Number of inducing points per latent GP.
        linear_mean:  ConstantMean if True, LinearMean if False.
    """

    def __init__(
        self,
        input_dims: int,
        output_dims: int,
        num_inducing: int = 32,
        linear_mean: bool = True,
    ):
        inducing_points = torch.randn(output_dims, num_inducing, input_dims)
        batch_shape = torch.Size([output_dims])

        variational_distribution = CholeskyVariationalDistribution(
            num_inducing_points=num_inducing,
            batch_shape=batch_shape,
        )
        variational_strategy = VariationalStrategy(
            self,
            inducing_points,
            variational_distribution,
            learn_inducing_locations=True,
        )

        super().__init__(variational_strategy, input_dims, output_dims)
        self.mean_module = (
            ConstantMean(batch_shape=batch_shape)
            if linear_mean
            else LinearMean(input_dims)
        )
        self.covar_module = ScaleKernel(
            MaternKernel(nu=2.5, batch_shape=batch_shape, ard_num_dims=input_dims),
            batch_shape=batch_shape,
        )

    def forward(self, x: Tensor) -> MultivariateNormal:
        mean_x = self.mean_module(x)
        covar_x = self.covar_module(x)
        return MultivariateNormal(mean_x, covar_x)


class DGPLastLayer(gpytorch.models.ApproximateGP):
    """LMC output layer for heterotopic multi-task Deep GP.

    Inherits from ``ApproximateGP`` (NOT ``DeepGPLayer``) so that
    ``task_indices`` can be forwarded to ``LMCVariationalStrategy``.
    ``ApproximateGP.__call__`` passes all ``**kwargs`` through to the
    variational strategy, which is how ``LMCVariationalStrategy`` receives
    ``task_indices`` for heterotopic predictions.

    **Must receive a plain tensor** in its ``__call__``, not a gpytorch
    distribution.  ``MultiTaskDeepGP.forward()`` is responsible for manually
    sampling from the hidden layer's distribution before calling this layer.

    Args:
        input_dims:   Input dimensionality (= hidden_dims of previous layer).
        output_dims:  Number of output tasks.
        num_inducing: Number of inducing points.
        num_latents:  Number of latent GPs in the LMC expansion.
        linear_mean:  ConstantMean if True.
    """

    def __init__(
        self,
        input_dims: int,
        output_dims: int,
        num_inducing: int = 128,
        num_latents: int = 10,
        linear_mean: bool = True,
    ):
        inducing_points = torch.randn(num_latents, num_inducing, input_dims)
        batch_shape = torch.Size([num_latents])

        variational_distribution = CholeskyVariationalDistribution(
            num_inducing_points=num_inducing,
            batch_shape=batch_shape,
        )
        variational_strategy = gpytorch.variational.LMCVariationalStrategy(
            VariationalStrategy(
                self,
                inducing_points,
                variational_distribution,
                learn_inducing_locations=True,
            ),
            num_tasks=output_dims,
            num_latents=num_latents,
            latent_dim=-1,
        )

        super().__init__(variational_strategy)
        self.mean_module = (
            ConstantMean(batch_shape=batch_shape)
            if linear_mean
            else LinearMean(input_dims)
        )
        self.covar_module = ScaleKernel(
            RBFKernel(batch_shape=batch_shape),
            batch_shape=batch_shape,
        )

    def forward(self, x: Tensor) -> MultivariateNormal:
        mean_x = self.mean_module(x)
        covar_x = self.covar_module(x)
        return MultivariateNormal(mean_x, covar_x)


# ---------------------------------------------------------------------------
# Helper: task value remapping (ported from reference anneal.py)
# ---------------------------------------------------------------------------


def get_task_value_remapping(
    task_values: Tensor, dtype: torch.dtype
) -> Optional[Tensor]:
    """Map arbitrary task IDs to contiguous 0-based integers.

    Returns ``None`` when task IDs are already 0, 1, …, n-1 (no remapping
    needed).  Otherwise returns a lookup tensor ``mapper`` such that
    ``mapper[raw_task_id]`` gives the contiguous index.

    Ported from the reference implementation in anneal.py.
    """
    task_range = torch.arange(
        len(task_values), dtype=task_values.dtype, device=task_values.device
    )
    if torch.equal(task_values, task_range):
        return None
    mapper = torch.full(
        (int(task_values.max().item()) + 1,),
        float("nan"),
        dtype=dtype,
        device=task_values.device,
    )
    mapper[task_values] = task_range.to(dtype=dtype)
    return mapper


# ---------------------------------------------------------------------------
# Full Deep GP architectures
# ---------------------------------------------------------------------------


class MultiTaskDeepGP(DeepGP):
    """2-layer Deep GP for heterotopic multi-task data.

    Architecture
    ^^^^^^^^^^^^
    1. ``DGPHiddenLayer`` (DeepGPLayer, Matern+ARD): maps feature space →
       latent space.  Returns a gpytorch distribution.
    2. Manual sampling from the hidden distribution → plain tensor.
    3. ``DGPLastLayer`` (ApproximateGP, RBF+LMC): maps sampled latent tensor
       + task indices → task-specific scalar predictions.

    All auxiliary methods (``_split_inputs``, ``_map_tasks``,
    ``get_all_tasks``) are defined directly in this class — they are NOT
    inherited from ``MultiTaskGPyTorchModel``, which does not provide them
    in BoTorch ≥ 0.14.

    Training data format (task-indexed)
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    Produced by ``prepare_multitask_pairs(X, Y)``:

    * ``train_X``: ``(n_obs_total, d+1)`` — features + integer task index in
      the last column.  Rows for missing task observations are dropped.
    * ``train_Y``: ``(n_obs_total,)`` — flat targets (one per row).

    Args:
        train_X:             Task-indexed training inputs ``(n_obs_total, d+1)``.
        train_Y:             Flat training targets ``(n_obs_total,)``.
        task_feature:        Column index of task feature (default -1 = last).
        hidden_dims:         Hidden layer output dimensionality.
        num_inducing_hidden: Inducing points for the hidden layer.
        num_inducing_last:   Inducing points for the LMC output layer.
        num_latents:         Number of latent GPs in the LMC expansion.
        linear_mean:         ConstantMean if True, LinearMean if False.
    """

    def __init__(
        self,
        train_X: Tensor,
        train_Y: Tensor,
        task_feature: int = -1,
        hidden_dims: int = 3,
        num_inducing_hidden: int = 32,
        num_inducing_last: int = 128,
        num_latents: int = 10,
        linear_mean: bool = True,
    ):
        super().__init__()

        all_tasks, task_feature_idx, n_features = self.get_all_tasks(
            train_X, task_feature
        )

        self._task_feature: int = task_feature_idx
        self.num_non_task_features: int = n_features
        self._num_outputs: int = len(all_tasks)
        self._output_tasks: List[int] = all_tasks
        self.num_tasks: int = len(all_tasks)

        # Indexer for non-task columns (reference pattern: arange(d), shift from task_feature on)
        base_idxr = torch.arange(n_features)
        base_idxr[task_feature_idx:] += 1
        self.register_buffer("_base_idxr", base_idxr)

        # Task value remapper: maps raw task IDs → contiguous 0-based ints
        task_mapper = get_task_value_remapping(
            task_values=torch.tensor(all_tasks, dtype=torch.long, device=train_X.device),
            dtype=train_X.dtype,
        )
        self.register_buffer("_task_mapper", task_mapper)

        # Scalar likelihood: Y is a flat 1-D vector of per-row targets
        self.likelihood = GaussianLikelihood()

        self.hidden_layer = DGPHiddenLayer(
            input_dims=n_features,
            output_dims=hidden_dims,
            num_inducing=num_inducing_hidden,
            linear_mean=linear_mean,
        )
        self.last_layer = DGPLastLayer(
            input_dims=hidden_dims,
            output_dims=self.num_tasks,
            num_inducing=num_inducing_last,
            num_latents=num_latents,
            linear_mean=linear_mean,
        )

    @property
    def num_outputs(self) -> int:
        """Number of outputs — required by BoTorch acquisition functions."""
        return self._num_outputs

    # ------------------------------------------------------------------
    # Auxiliary methods (ported from reference; not inherited from BoTorch)
    # ------------------------------------------------------------------

    @classmethod
    def get_all_tasks(
        cls,
        train_X: Tensor,
        task_feature: int,
        output_tasks: Optional[List[int]] = None,
    ) -> tuple[List[int], int, int]:
        """Infer all task IDs from the training data.

        Returns:
            ``(all_tasks, task_feature_idx, n_features)``
        """
        d = train_X.shape[-1] - 1
        task_feature_idx = task_feature % (d + 1)
        all_tasks = (
            train_X[..., task_feature_idx]
            .unique(sorted=True)
            .to(dtype=torch.long)
            .tolist()
        )
        return all_tasks, task_feature_idx, d

    def _map_tasks(self, task_values: Tensor) -> Tensor:
        """Remap raw task values to contiguous indices via ``_task_mapper``."""
        long_vals = task_values.long()
        if self._task_mapper is not None:
            return self._task_mapper[long_vals]
        return long_vals

    def _split_inputs(self, x: Tensor) -> tuple[Tensor, Tensor]:
        """Split task-indexed input into (x_basic, task_idcs).

        Args:
            x: ``(..., n, d+1)`` tensor with task feature at ``_task_feature``.

        Returns:
            ``x_basic``: ``(..., n, d)`` feature tensor.
            ``task_idcs``: ``(..., n, 1)`` long task-index tensor (remapped).
        """
        batch_shape, d = x.shape[:-2], x.shape[-1]
        x_basic = x[..., self._base_idxr].view(batch_shape + torch.Size([-1, d - 1]))
        task_idcs = (
            x[..., self._task_feature]
            .view(batch_shape + torch.Size([-1, 1]))
            .to(dtype=torch.long)
        )
        task_idcs = self._map_tasks(task_values=task_idcs)
        return x_basic, task_idcs

    # ------------------------------------------------------------------
    # Forward + posterior
    # ------------------------------------------------------------------

    def forward(self, x: Tensor) -> MultivariateNormal:
        """2-layer DGP forward: hidden → sample → LMC last layer.

        1. Split x into features and task indices.
        2. Run ``hidden_layer(x_basic)`` → distribution.
        3. Manually sample from the hidden distribution → plain tensor.
           (Needed so ``task_indices`` can be passed to the LMC layer.)
        4. Broadcast task indices to match any extra sample dimensions.
        5. Call ``last_layer(sample, task_indices=task_id)``.
        """
        x_basic, task_idcs = self._split_inputs(x)

        hidden = self.hidden_layer(x_basic)

        # Manual sample: reference pattern (anneal.py lines 389-395)
        hidden_sample = torch.distributions.Normal(
            loc=hidden.mean,
            scale=hidden.variance.sqrt(),
        ).rsample()  # (..., n, hidden_dims)

        # Broadcast task_idcs to match leading sample dims of hidden_sample
        task_id = task_idcs.squeeze(-1).expand(hidden_sample.shape[:-1])

        return self.last_layer(hidden_sample, task_indices=task_id)

    def posterior(
        self,
        X: Tensor,
        output_indices: Optional[List[int]] = None,
        observation_noise: bool = False,
        **kwargs,
    ) -> GPyTorchPosterior:
        """BoTorch-compatible posterior for all output tasks.

        * If ``X.shape[-1] == num_non_task_features`` (no task column): runs a
          per-task prediction loop and returns a ``MultitaskMultivariateNormal``
          with block-diagonal covariance (independent tasks).
        * If ``X`` already has the task column: forwards directly.

        Handles 3-D batched input ``(N, q, d)`` from SAOptimizer by flattening
        to ``(N*q, d)`` before the per-task loop.  Uses
        ``num_likelihood_samples=1`` to suppress gpytorch DeepGP's stochastic
        sample dimension.

        Returns:
            ``GPyTorchPosterior`` with ``.mean`` shape ``(..., n, m)``.
        """
        self.eval()
        tasks = (
            self._output_tasks
            if output_indices is None
            else [self._output_tasks[i] for i in output_indices]
        )
        m = len(tasks)

        # --- Flatten 3-D input from SA optimizer ---
        batched = X.ndim == 3
        if batched:
            n_batch, q, d = X.shape
            X_2d = X.reshape(n_batch * q, d)
        else:
            n_batch, q = X.shape[0], 1
            X_2d = X

        with torch.no_grad(), gpytorch.settings.fast_pred_var(), \
                gpytorch.settings.num_likelihood_samples(1):
            if X_2d.shape[-1] == self.num_non_task_features:
                means_list: list[Tensor] = []
                vars_list: list[Tensor] = []
                for t in tasks:
                    task_col = torch.full(
                        (X_2d.shape[0], 1), float(t),
                        dtype=X_2d.dtype, device=X_2d.device,
                    )
                    X_t = torch.cat([X_2d, task_col], dim=-1)
                    preds = self.likelihood(self(X_t))
                    # Squeeze stochastic sample dim: (1, N) → (N,)
                    pm = preds.mean
                    pv = preds.variance.clamp(min=1e-6)
                    if pm.ndim == 2 and pm.shape[0] == 1:
                        pm = pm.squeeze(0)
                        pv = pv.squeeze(0)
                    means_list.append(pm)
                    vars_list.append(pv)

                mean = torch.stack(means_list, dim=-1)  # (n, m)
                var = torch.stack(vars_list, dim=-1)    # (n, m)

            else:
                preds = self.likelihood(self(X_2d))
                pm = preds.mean
                pv = preds.variance.clamp(min=1e-6)
                if pm.ndim == 2 and pm.shape[0] == 1:
                    pm = pm.squeeze(0)
                    pv = pv.squeeze(0)
                mean = pm.unsqueeze(-1) if pm.ndim == 1 else pm
                var = pv.unsqueeze(-1) if pv.ndim == 1 else pv

        # Restore batch dim if input was 3-D
        if batched:
            mean = mean.reshape(n_batch, q, m)   # (n_batch, q, m)
            var = var.reshape(n_batch, q, m)

        # Block-diagonal covariance, task-major (interleaved=False)
        *batch, n, _ = mean.shape
        cov = torch.zeros(*batch, n * m, n * m, dtype=var.dtype, device=var.device)
        for j in range(m):
            s, e = j * n, (j + 1) * n
            cov[..., s:e, s:e] = torch.diag_embed(var[..., j])

        dist = MultitaskMultivariateNormal(mean, covariance_matrix=cov, interleaved=False)
        return GPyTorchPosterior(dist)


class TrueDeepGP(DeepGP):
    """Configurable-depth Deep GP for homogeneous multi-output data.

    All layers are ``DGPHiddenLayer`` (standard ``DeepGPLayer``), enabling
    gpytorch's automatic distribution propagation.  Unlike
    ``MultiTaskDeepGP``, this model does NOT use task indices — all outputs
    are observed for every input (homogeneous / non-heterotopic).

    Args:
        input_dims:          Input feature dimensionality.
        hidden_dims:         Latent dim for each hidden layer.
        output_dims:         Number of output tasks.
        num_layers:          Total number of layers (including output). >= 1.
        num_inducing_hidden: Inducing points per hidden layer.
        num_inducing_last:   Inducing points for the output layer.
    """

    def __init__(
        self,
        input_dims: int,
        hidden_dims: int = 3,
        output_dims: int = 1,
        num_layers: int = 2,
        num_inducing_hidden: int = 32,
        num_inducing_last: int = 64,
    ):
        super().__init__()
        if num_layers < 1:
            raise ValueError("num_layers must be >= 1")

        self.hidden_layers = torch.nn.ModuleList()
        prev_dims = input_dims
        for _ in range(num_layers - 1):
            self.hidden_layers.append(
                DGPHiddenLayer(
                    input_dims=prev_dims,
                    output_dims=hidden_dims,
                    num_inducing=num_inducing_hidden,
                )
            )
            prev_dims = hidden_dims

        self.last_layer = DGPHiddenLayer(
            input_dims=prev_dims,
            output_dims=output_dims,
            num_inducing=num_inducing_last,
        )
        self.likelihood = MultitaskGaussianLikelihood(num_tasks=output_dims)
        self._num_outputs = output_dims

    @property
    def num_outputs(self) -> int:
        """Number of outputs — required by BoTorch acquisition functions."""
        return self._num_outputs

    def forward(self, inputs: Tensor) -> MultivariateNormal:
        x = inputs
        for layer in self.hidden_layers:
            x = layer(x)
        return self.last_layer(x)

    def predict(self, test_x: Tensor) -> tuple[Tensor, Tensor]:
        self.eval()
        with torch.no_grad(), gpytorch.settings.fast_pred_var():
            preds = self.likelihood(self(test_x))
        return preds.mean, preds.variance

    def posterior(
        self,
        X: Tensor,
        output_indices: Optional[List[int]] = None,
        observation_noise: bool = False,
        **kwargs,
    ) -> GPyTorchPosterior:
        """Return posterior via likelihood(model(X)).

        Handles 3-D batched input ``(N, q, d)`` from SAOptimizer by flattening
        to ``(N*q, d)``, obtaining predictions, then rebuilding the expected
        ``MultitaskMultivariateNormal`` posterior with shape ``(N, q, m)``.
        Uses ``num_likelihood_samples=1`` to suppress the stochastic sample
        dimension that gpytorch DeepGP adds during evaluation.
        """
        self.eval()

        # --- Flatten 3-D input ---
        batched = X.ndim == 3
        if batched:
            n_batch, q, d = X.shape
            X_2d = X.reshape(n_batch * q, d)
        else:
            n_batch, q = X.shape[0], 1
            X_2d = X

        with torch.no_grad(), gpytorch.settings.fast_pred_var(), \
                gpytorch.settings.num_likelihood_samples(1):
            preds = self.likelihood(self(X_2d))

        # preds.mean: (1, N, m) with num_likelihood_samples=1 → squeeze sample dim
        mean = preds.mean
        var = preds.variance.clamp(min=1e-6)
        if mean.ndim == 3 and mean.shape[0] == 1:
            mean = mean.squeeze(0)  # (N, m)
            var = var.squeeze(0)

        # Restore batch dim if input was 3-D
        if batched:
            mean = mean.reshape(n_batch, q, -1)   # (n_batch, q, m)
            var = var.reshape(n_batch, q, -1)

        m = mean.shape[-1]
        *batch_dims, n_pts, _ = mean.shape

        # Block-diagonal covariance (independent tasks, interleaved=False)
        cov = torch.zeros(*batch_dims, n_pts * m, n_pts * m,
                          dtype=mean.dtype, device=mean.device)
        for j in range(m):
            s, e = j * n_pts, (j + 1) * n_pts
            cov[..., s:e, s:e] = torch.diag_embed(var[..., j])

        dist = MultitaskMultivariateNormal(mean, covariance_matrix=cov, interleaved=False)
        return GPyTorchPosterior(dist)


# ---------------------------------------------------------------------------
# Training utility
# ---------------------------------------------------------------------------


def train_dgp(
    model: DeepGP,
    train_X: Tensor,
    train_Y: Tensor,
    num_epochs: int = 1000,
    lr: float = 0.01,
    beta: float = 0.5,
    patience: int = 50,
    verbose: bool = False,
) -> list[float]:
    """Train a Deep GP with Adam + early stopping.

    Works for both ``MultiTaskDeepGP`` (1D flattened targets, scalar
    ``GaussianLikelihood``) and ``TrueDeepGP`` (2D targets,
    ``MultitaskGaussianLikelihood``).

    Args:
        model:       Deep GP instance.
        train_X:     ``(n, d)`` or ``(n_obs_total, d+1)`` float64 inputs.
        train_Y:     ``(n,)`` or ``(n, m)`` float64 targets.
        num_epochs:  Maximum training epochs.
        lr:          Adam learning rate.
        beta:        KL weight in VariationalELBO (0.5 avoids over-regularisation).
        patience:    Early-stopping patience in epochs.
        verbose:     Print loss every 100 epochs.

    Returns:
        List of per-epoch losses.
    """
    model.train()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    mll = DeepApproximateMLL(
        VariationalELBO(model.likelihood, model, num_data=train_X.shape[0], beta=beta)
    )

    best_loss = float("inf")
    no_improve = 0
    losses: list[float] = []

    for epoch in range(num_epochs):
        optimizer.zero_grad()
        output = model(train_X)
        loss = -mll(output, train_Y)
        loss.backward()
        optimizer.step()

        loss_val = loss.item()
        losses.append(loss_val)

        if loss_val < best_loss:
            best_loss = loss_val
            no_improve = 0
        else:
            no_improve += 1

        if verbose and epoch % 100 == 0:
            print(f"Epoch {epoch:4d}  loss={loss_val:.4f}")

        if no_improve >= patience:
            if verbose:
                print(f"Early stop at epoch {epoch}")
            break

    model.eval()
    return losses


# ---------------------------------------------------------------------------
# Surrogate wrappers
# ---------------------------------------------------------------------------


class MultiTaskDeepGPSurrogate(SurrogateBase):
    """Surrogate wrapper for ``MultiTaskDeepGP``.

    Converts ``(train_X, train_Y)`` in the standard multi-output format
    ``(n, d)`` + ``(n, m)`` to task-indexed format via
    ``prepare_multitask_pairs`` before constructing and training the model.
    This correctly handles heterotopic data (NaN entries in ``train_Y``).

    After fitting, ``predict(X_test)`` returns per-task ``(mean, variance)``
    by running a per-task prediction loop (one forward pass per task).

    For Bayesian Optimisation with discrete candidate pools, use
    ``FakeModel.from_model(surrogate, all_candidates_mt)`` to precompute
    posteriors over all candidates once (O(1) lookup during SA).

    Args:
        hidden_dims:         Latent dimensionality of the hidden layer.
        num_latents:         Number of latent GPs in the LMC output layer.
        num_inducing_hidden: Inducing points for hidden layer.
        num_inducing_last:   Inducing points for LMC output layer.
        num_epochs:          Max training epochs.
        lr:                  Adam learning rate.
        beta:                KL penalty weight in VariationalELBO.
        patience:            Early-stopping patience.
        verbose:             Print training progress.
    """

    _subprocess_isolation = True

    def __init__(
        self,
        hidden_dims: int = 3,
        num_latents: int = 10,
        num_inducing_hidden: int = 32,
        num_inducing_last: int = 128,
        num_epochs: int = 1000,
        lr: float = 0.01,
        beta: float = 0.5,
        patience: int = 50,
        verbose: bool = False,
    ):
        self.hidden_dims = hidden_dims
        self.num_latents = num_latents
        self.num_inducing_hidden = num_inducing_hidden
        self.num_inducing_last = num_inducing_last
        self.num_epochs = num_epochs
        self.lr = lr
        self.beta = beta
        self.patience = patience
        self.verbose = verbose
        self._model: Optional[MultiTaskDeepGP] = None

    def fit(self, train_X: Tensor, train_Y: Tensor) -> MultiTaskDeepGP:
        """Fit the multi-task Deep GP.

        Internally converts ``(train_X, train_Y)`` to task-indexed format via
        ``prepare_multitask_pairs``, which drops NaN rows per task and appends
        the integer task index as the last column of ``X_mt``.

        Args:
            train_X: ``(n, d)`` float64 feature tensor.
            train_Y: ``(n, m)`` float64 target tensor (NaN for missing tasks).

        Returns:
            The fitted ``MultiTaskDeepGP`` (also stored as ``self.model``).
        """
        from bo_zoo.data.multitask import prepare_multitask_pairs

        train_X = train_X.to(dtype=torch.float64)
        train_Y = train_Y.to(dtype=torch.float64)

        # Convert to task-indexed format; drops NaN rows per task.
        # prepare_multitask_pairs always returns CPU tensors — move to training device.
        X_mt, Y_flat = prepare_multitask_pairs(train_X, train_Y)
        X_mt = X_mt.to(train_X.device)
        Y_flat = Y_flat.to(train_X.device)
        # Y_flat: (n_obs_total, 1) → squeeze to (n_obs_total,) for GaussianLikelihood
        Y_flat_1d = Y_flat.squeeze(-1)

        self._model = MultiTaskDeepGP(
            train_X=X_mt,
            train_Y=Y_flat_1d,
            task_feature=-1,
            hidden_dims=self.hidden_dims,
            num_inducing_hidden=self.num_inducing_hidden,
            num_inducing_last=self.num_inducing_last,
            num_latents=self.num_latents,
        )
        self._model = self._model.to(train_X.device)
        train_dgp(
            self._model,
            X_mt,
            Y_flat_1d,
            num_epochs=self.num_epochs,
            lr=self.lr,
            beta=self.beta,
            patience=self.patience,
            verbose=self.verbose,
        )
        return self._model

    @property
    def model(self) -> MultiTaskDeepGP:
        if self._model is None:
            raise RuntimeError("Call fit() before accessing .model")
        return self._model

    def predict(self, X: Tensor) -> tuple[Tensor, Tensor]:
        """Predict mean and variance for all output tasks.

        Runs one forward pass per task by appending the task index to each
        test point, then stacks results.

        Args:
            X: ``(n, d)`` test input tensor (no task column).

        Returns:
            ``(mean, variance)``: both ``(n, m)`` tensors.
        """
        model = self._model
        model.eval()
        n_test = X.shape[0]

        means, vars_ = [], []
        with torch.no_grad(), gpytorch.settings.fast_pred_var():
            for t in model._output_tasks:
                task_col = torch.full(
                    (n_test, 1), float(t), dtype=X.dtype, device=X.device
                )
                X_t = torch.cat([X, task_col], dim=-1)
                preds = model.likelihood(model(X_t))
                means.append(preds.mean.unsqueeze(-1))
                vars_.append(preds.variance.clamp(min=1e-6).unsqueeze(-1))

        mean = torch.cat(means, dim=-1)  # (n_test, m)
        var = torch.cat(vars_, dim=-1)   # (n_test, m)
        return mean, var


class TrueDeepGPSurrogate(SurrogateBase):
    """Surrogate wrapper for ``TrueDeepGP`` (configurable depth).

    For homogeneous multi-output data (all outputs observed for every input).
    Does NOT use task-indexed format.

    Args:
        hidden_dims:         Latent dimensionality of each hidden layer.
        num_layers:          Total number of layers (including output).
        num_inducing_hidden: Inducing points per hidden layer.
        num_inducing_last:   Inducing points for output layer.
        num_epochs, lr, beta, patience: Training hyperparameters.
    """

    def __init__(
        self,
        hidden_dims: int = 3,
        num_layers: int = 2,
        num_inducing_hidden: int = 32,
        num_inducing_last: int = 64,
        num_epochs: int = 1000,
        lr: float = 0.01,
        beta: float = 0.5,
        patience: int = 50,
        verbose: bool = False,
    ):
        self.hidden_dims = hidden_dims
        self.num_layers = num_layers
        self.num_inducing_hidden = num_inducing_hidden
        self.num_inducing_last = num_inducing_last
        self.num_epochs = num_epochs
        self.lr = lr
        self.beta = beta
        self.patience = patience
        self.verbose = verbose
        self._model: Optional[TrueDeepGP] = None

    def fit(self, train_X: Tensor, train_Y: Tensor) -> TrueDeepGP:
        train_X = train_X.to(dtype=torch.float64)
        train_Y = train_Y.to(dtype=torch.float64)
        d = train_X.shape[1]
        m = train_Y.shape[1] if train_Y.ndim > 1 else 1

        self._model = TrueDeepGP(
            input_dims=d,
            hidden_dims=self.hidden_dims,
            output_dims=m,
            num_layers=self.num_layers,
            num_inducing_hidden=self.num_inducing_hidden,
            num_inducing_last=self.num_inducing_last,
        )
        self._model = self._model.to(train_X.device)
        train_dgp(
            self._model,
            train_X,
            train_Y,
            num_epochs=self.num_epochs,
            lr=self.lr,
            beta=self.beta,
            patience=self.patience,
            verbose=self.verbose,
        )
        return self._model

    @property
    def model(self) -> TrueDeepGP:
        if self._model is None:
            raise RuntimeError("Call fit() before accessing .model")
        return self._model

    def predict(self, X: Tensor) -> tuple[Tensor, Tensor]:
        """Override: TrueDeepGP uses likelihood(model(X)), not model.posterior(X)."""
        return self._model.predict(X)
