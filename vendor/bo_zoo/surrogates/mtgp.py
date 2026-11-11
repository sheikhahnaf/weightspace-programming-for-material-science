"""Multi-Task GP surrogate wrapping BoTorch MultiTaskGP."""

from __future__ import annotations

import torch
from torch import Tensor

from botorch.models import MultiTaskGP
from botorch.fit import fit_gpytorch_mll
from gpytorch.mlls import ExactMarginalLogLikelihood

from bo_zoo.surrogates.base import SurrogateBase
from bo_zoo.data.multitask import prepare_multitask_pairs


class MTGPSurrogate(SurrogateBase):
    """Multi-Task GP using BoTorch's ``MultiTaskGP``.

    Expects either:
    - Pre-formatted multi-task data (``train_X`` has task index as last column,
      ``train_Y`` is ``(n, 1)``), OR
    - Raw multi-output data (``train_X`` is ``(n, d)``, ``train_Y`` is ``(n, m)``),
      in which case ``prepare_multitask_pairs`` is called automatically.

    Args:
        rank: Rank of the inter-task covariance matrix (default 1).
        output_tasks: List of task indices to predict.  If None, all tasks
            are used.
        auto_format: If True (default), automatically converts ``(n, d)/(n, m)``
            data to multi-task format using ``prepare_multitask_pairs``.
    """

    def __init__(
        self,
        rank: int = 1,
        output_tasks: list[int] | None = None,
        auto_format: bool = True,
    ):
        self._rank = rank
        self._output_tasks = output_tasks
        self._auto_format = auto_format
        self._model: MultiTaskGP | None = None
        self._n_tasks: int = 0

    def fit(self, train_X: Tensor, train_Y: Tensor) -> MultiTaskGP:
        """Fit MultiTaskGP.

        Args:
            train_X: ``(n, d)`` or ``(n_mt, d+1)`` float64 tensor.
            train_Y: ``(n, m)`` or ``(n_mt, 1)`` float64 tensor.

        Returns:
            Fitted ``MultiTaskGP``.
        """
        train_X = train_X.to(dtype=torch.float64)
        train_Y = train_Y.to(dtype=torch.float64)

        # Auto-format: (n, d) + (n, m) → multi-task pairs
        if self._auto_format and train_Y.shape[1] > 1:
            train_X, train_Y = prepare_multitask_pairs(train_X, train_Y)
            self._n_tasks = int(train_X[:, -1].max().item()) + 1
        else:
            self._n_tasks = int(train_X[:, -1].max().item()) + 1

        output_tasks = self._output_tasks or list(range(self._n_tasks))

        self._model = MultiTaskGP(
            train_X,
            train_Y,
            task_feature=-1,
            output_tasks=output_tasks,
            rank=self._rank,
        )
        mll = ExactMarginalLogLikelihood(self._model.likelihood, self._model)
        fit_gpytorch_mll(mll)
        self._model.eval()
        return self._model

    @property
    def model(self) -> MultiTaskGP:
        if self._model is None:
            raise RuntimeError("Call fit() before accessing .model")
        return self._model
