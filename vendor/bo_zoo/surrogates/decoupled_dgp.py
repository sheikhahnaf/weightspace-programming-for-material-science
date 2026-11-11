"""Decoupled Deep GP surrogate using MultiTaskGPyTorchModel.

Ported from APRIME's MultiTaskDeepGP.  The key improvement over the
existing ``MultiTaskDeepGPSurrogate`` (in ``dgp.py``) is that this model
inherits from BoTorch's ``MultiTaskGPyTorchModel``, which provides a
battle-tested ``.posterior()`` implementation.  The hidden layer output
dimensionality is ``num_tasks - reduction`` (parameterised), and
``decouple_samples=True`` keeps MC sample and LMC latent dimensions
independent via a broadcast dimension for better gradient flow.

Layer classes (``DGPHiddenLayer``, ``DGPLastLayer``) are reused from
``bo_zoo.surrogates.dgp`` -- no duplication.
"""

from __future__ import annotations

from typing import List, Optional

import torch
from torch import Tensor

import gpytorch
from gpytorch.models.deep_gps import DeepGP
from gpytorch.mlls import DeepApproximateMLL, VariationalELBO
from gpytorch.likelihoods import GaussianLikelihood

from botorch.models.gpytorch import MultiTaskGPyTorchModel
from botorch.posteriors.gpytorch import GPyTorchPosterior
from gpytorch.distributions import MultitaskMultivariateNormal

from bo_zoo.surrogates.base import SurrogateBase
from bo_zoo.surrogates.dgp import (
    DGPHiddenLayer,
    DGPLastLayer,
    get_task_value_remapping,
    train_dgp,
)


# ---------------------------------------------------------------------------
# Model
# ---------------------------------------------------------------------------


class DecoupledMultiTaskDeepGP(DeepGP, MultiTaskGPyTorchModel):
    """2-layer Deep GP with decoupled MC samples (BoTorch-compatible).

    Inherits from both ``DeepGP`` (gpytorch variational framework) and
    ``MultiTaskGPyTorchModel`` (provides ``.posterior()``).

    The hidden layer maps the input features to ``num_tasks - reduction``
    latent dimensions.  The LMC output layer maps latent dims back to
    ``num_tasks``.

    With ``decouple_samples=True`` (default), the MC sample dimension and
    the LMC latent batch dimension are independent: the hidden layer is
    sampled with the standard ``num_likelihood_samples`` setting, and the
    sample is broadcast into the latent batch dimension via ``unsqueeze(-3)``.
    This avoids forcing ``num_likelihood_samples == num_latents`` and gives
    better gradient flow.

    Args:
        train_X:             Task-indexed inputs ``(n_obs, d+1)``.
        train_Y:             Flat targets ``(n_obs, 1)``.
        task_feature:        Column index of task ID (default ``-1`` = last).
        reduction:           Hidden dims = ``num_tasks - reduction``.
        num_inducing_hidden: Inducing points for the hidden layer.
        num_inducing_last:   Inducing points for the LMC output layer.
        num_latents:         Latent GPs in the LMC expansion.
        decouple_samples:    If True, MC samples and LMC latents are independent.
    """

    def __init__(
        self,
        train_X: Tensor,
        train_Y: Tensor,
        task_feature: int = -1,
        reduction: int = 2,
        num_inducing_hidden: int = 16,
        num_inducing_last: int = 32,
        num_latents: int = 10,
        decouple_samples: bool = True,
    ):
        super().__init__()
        self._reduction = reduction
        self._num_latents = num_latents
        self._decouple_samples = decouple_samples

        # --- task bookkeeping (needed by MultiTaskGPyTorchModel.posterior) ---
        all_tasks, task_feature_idx, n_features = self.get_all_tasks(
            train_X, task_feature
        )
        self._task_feature: int = task_feature_idx
        self.num_non_task_features: int = n_features
        self._output_tasks: List[int] = all_tasks
        self._num_outputs: int = len(all_tasks)
        self.num_tasks: int = len(all_tasks)

        # Indexer for non-task columns
        base_idxr = torch.arange(n_features)
        base_idxr[task_feature_idx:] += 1
        self.register_buffer("_base_idxr", base_idxr)

        # Task value remapper
        task_mapper = get_task_value_remapping(
            task_values=torch.tensor(
                all_tasks, dtype=torch.long, device=train_X.device
            ),
            dtype=train_X.dtype,
        )
        self.register_buffer("_task_mapper", task_mapper)

        # --- layers ---
        hidden_dims = max(self.num_tasks - self._reduction, 1)

        self.hidden_layer = DGPHiddenLayer(
            input_dims=n_features,
            output_dims=hidden_dims,
            num_inducing=num_inducing_hidden,
            linear_mean=True,
        )
        self.last_layer = DGPLastLayer(
            input_dims=hidden_dims,
            output_dims=self.num_tasks,
            num_inducing=num_inducing_last,
            num_latents=num_latents,
            linear_mean=True,
        )

        # Scalar likelihood (training targets are flattened)
        self.likelihood = GaussianLikelihood()

    @property
    def num_outputs(self) -> int:
        return self._num_outputs

    # ------------------------------------------------------------------
    # Auxiliary helpers
    # ------------------------------------------------------------------

    @classmethod
    def get_all_tasks(
        cls,
        train_X: Tensor,
        task_feature: int,
        output_tasks: Optional[List[int]] = None,
    ) -> tuple[List[int], int, int]:
        """Infer all tasks from training data.

        Returns ``(all_tasks, task_feature_idx, n_features)``.
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
        long_vals = task_values.long()
        if self._task_mapper is not None:
            return self._task_mapper[long_vals]
        return long_vals

    def _split_inputs(self, x: Tensor) -> tuple[Tensor, Tensor]:
        """Split ``(x_basic, task_idcs)`` from task-indexed input."""
        batch_shape, d = x.shape[:-2], x.shape[-1]
        x_basic = x[..., self._base_idxr].view(
            batch_shape + torch.Size([-1, d - 1])
        )
        task_idcs = (
            x[..., self._task_feature]
            .view(batch_shape + torch.Size([-1, 1]))
            .to(dtype=torch.long)
        )
        task_idcs = self._map_tasks(task_values=task_idcs)
        return x_basic, task_idcs

    # ------------------------------------------------------------------
    # Forward
    # ------------------------------------------------------------------

    def forward(self, x: Tensor) -> gpytorch.distributions.MultivariateNormal:
        """2-layer DGP forward with optional decoupled sampling."""
        x_basic, task_idcs = self._split_inputs(x)

        if self._decouple_samples:
            # Decoupled: MC sample dim and LMC latent dim are independent.
            n_mc = (
                gpytorch.settings.num_likelihood_samples.value()
                if self.training
                else 1
            )
            with gpytorch.settings.num_likelihood_samples(n_mc):
                hidden = self.hidden_layer(x_basic)

            hidden_sample = torch.distributions.Normal(
                loc=hidden.mean,
                scale=hidden.variance.sqrt(),
            ).rsample()

            # Insert broadcast dim for LMC latents
            hidden_sample = hidden_sample.unsqueeze(-3)

            task_squeezed = task_idcs.squeeze(-1)
            ones = [1] * (hidden_sample.dim() - 2)
            task_id = task_squeezed.view(*ones, -1).expand(
                *hidden_sample.shape[:-1]
            )
        else:
            # Coupled: num_likelihood_samples == num_latents
            with gpytorch.settings.num_likelihood_samples(self._num_latents):
                hidden = self.hidden_layer(x_basic)

            hidden_sample = torch.distributions.Normal(
                loc=hidden.mean,
                scale=hidden.variance.sqrt(),
            ).rsample()

            if len(hidden_sample.shape) == 3:
                task_id = torch.broadcast_to(
                    task_idcs.squeeze(-1),
                    (
                        hidden_sample.shape[-3],
                        task_idcs.squeeze(-1).shape[-1],
                    ),
                )
            else:
                task_id = torch.broadcast_to(
                    task_idcs.squeeze(-1),
                    (
                        hidden_sample.shape[-4],
                        hidden_sample.shape[-3],
                        task_idcs.squeeze(-1).shape[-1],
                    ),
                )

        return self.last_layer(hidden_sample, task_indices=task_id)

    # ------------------------------------------------------------------
    # Custom posterior (LMC returns AddedDiagLinearOperator which
    # MultiTaskGPyTorchModel.posterior() can't handle — build manually)
    # ------------------------------------------------------------------

    def posterior(
        self,
        X: Tensor,
        output_indices: Optional[List[int]] = None,
        observation_noise: bool = False,
        **kwargs,
    ) -> GPyTorchPosterior:
        """BoTorch-compatible posterior via per-task prediction loop.

        Handles 3-D batched input ``(N, q, d)`` from SAOptimizer by
        flattening to ``(N*q, d)`` before the per-task loop.
        """
        self.eval()
        tasks = (
            self._output_tasks
            if output_indices is None
            else [self._output_tasks[i] for i in output_indices]
        )
        m = len(tasks)

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
                    pm = preds.mean
                    pv = preds.variance.clamp(min=1e-6)
                    if pm.ndim == 2 and pm.shape[0] == 1:
                        pm = pm.squeeze(0)
                        pv = pv.squeeze(0)
                    means_list.append(pm)
                    vars_list.append(pv)
                mean = torch.stack(means_list, dim=-1)
                var = torch.stack(vars_list, dim=-1)
            else:
                preds = self.likelihood(self(X_2d))
                pm = preds.mean
                pv = preds.variance.clamp(min=1e-6)
                if pm.ndim == 2 and pm.shape[0] == 1:
                    pm = pm.squeeze(0)
                    pv = pv.squeeze(0)
                mean = pm.unsqueeze(-1) if pm.ndim == 1 else pm
                var = pv.unsqueeze(-1) if pv.ndim == 1 else pv

        if batched:
            mean = mean.reshape(n_batch, q, m)
            var = var.reshape(n_batch, q, m)

        # Build covariance as BlockDiagLinearOperator (not dense tensor) so that
        # qLogNEHVI / qNEHVI acqfs accept it. With interleaved=False, the layout
        # is task-major: [task0_obs0..N, task1_obs0..N, ...]. For each task j,
        # the n×n block is a diagonal operator of var[..., j].
        from linear_operator.operators import BlockDiagLinearOperator, DiagLinearOperator

        # var shape: (*batch, n, m) -> move task dim to second-to-last: (*batch, m, n)
        var_per_task = var.movedim(-1, -2).contiguous()  # (*batch, m, n)
        # DiagLinearOperator on last dim gives a batched (*batch, m, n, n) operator
        base_diag = DiagLinearOperator(var_per_task)
        # BlockDiagLinearOperator flattens the -3 batch dim into block-diagonal
        cov_op = BlockDiagLinearOperator(base_diag)  # (*batch, m*n, m*n)

        dist = MultitaskMultivariateNormal(mean, covariance_matrix=cov_op, interleaved=False)
        return GPyTorchPosterior(dist)


# ---------------------------------------------------------------------------
# Surrogate wrapper
# ---------------------------------------------------------------------------


class DecoupledDGPSurrogate(SurrogateBase):
    """Surrogate wrapper for ``DecoupledMultiTaskDeepGP``.

    Follows the same fit/predict/model pattern as ``MultiTaskDeepGPSurrogate``
    but uses the decoupled-sample model with ``MultiTaskGPyTorchModel``
    inheritance for a cleaner ``.posterior()``.

    Args:
        reduction:           Hidden dims = ``num_tasks - reduction``.
        num_latents:         LMC latent GPs.
        num_inducing_hidden: Inducing points for the hidden layer.
        num_inducing_last:   Inducing points for the LMC output layer.
        num_epochs:          Maximum training epochs.
        decouple_samples:    Decouple MC samples from LMC latents.
        lr:                  Adam learning rate.
        beta:                KL weight in VariationalELBO.
        patience:            Early-stopping patience.
        verbose:             Print training loss.
    """

    _subprocess_isolation = False  # disabled: custom posterior handles memory; subprocess caching issues

    def __init__(
        self,
        reduction: int = 2,
        num_latents: int = 10,
        num_inducing_hidden: int = 16,
        num_inducing_last: int = 32,
        num_epochs: int = 100,
        decouple_samples: bool = True,
        lr: float = 0.01,
        beta: float = 0.5,
        patience: int = 50,
        verbose: bool = False,
    ):
        self.reduction = reduction
        self.num_latents = num_latents
        self.num_inducing_hidden = num_inducing_hidden
        self.num_inducing_last = num_inducing_last
        self.num_epochs = num_epochs
        self.decouple_samples = decouple_samples
        self.lr = lr
        self.beta = beta
        self.patience = patience
        self.verbose = verbose
        self._model: Optional[DecoupledMultiTaskDeepGP] = None

    def fit(self, train_X: Tensor, train_Y: Tensor) -> DecoupledMultiTaskDeepGP:
        """Fit the decoupled multi-task Deep GP.

        Converts ``(n, d)`` + ``(n, m)`` to task-indexed format, builds the
        model, and trains with variational ELBO + early stopping.

        Dynamically sets ``reduction = n_obj - 1`` (so hidden_dims = 1) for
        2-obj problems, or ``reduction = n_obj - 2`` for 3+ obj, ensuring
        hidden layer dimensionality scales with problem complexity.

        Returns:
            The fitted ``DecoupledMultiTaskDeepGP``.
        """
        from bo_zoo.data.multitask import prepare_multitask_pairs

        train_X = train_X.to(dtype=torch.float64)
        n_obj = train_Y.shape[1] if train_Y.ndim > 1 else 1
        # Dynamic reduction: n_obj-1 for 2-obj (hidden=1), n_obj-2 for 3+ (hidden=2+)
        if n_obj <= 2:
            reduction = max(n_obj - 1, 0)
        else:
            reduction = n_obj - 2
        self.reduction = reduction
        train_Y = train_Y.to(dtype=torch.float64)

        X_mt, Y_flat = prepare_multitask_pairs(train_X, train_Y)
        X_mt = X_mt.to(train_X.device)
        Y_flat = Y_flat.to(train_X.device)
        Y_flat_1d = Y_flat.squeeze(-1)

        self._model = DecoupledMultiTaskDeepGP(
            train_X=X_mt,
            train_Y=Y_flat,
            task_feature=-1,
            reduction=self.reduction,
            num_inducing_hidden=self.num_inducing_hidden,
            num_inducing_last=self.num_inducing_last,
            num_latents=self.num_latents,
            decouple_samples=self.decouple_samples,
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
    def model(self) -> DecoupledMultiTaskDeepGP:
        if self._model is None:
            raise RuntimeError("Call fit() before accessing .model")
        return self._model

    def predict(self, X: Tensor) -> tuple[Tensor, Tensor]:
        """Predict mean and variance for all output tasks.

        Runs one forward pass per task, stacking results into
        ``(n, m)`` tensors.

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
