"""Reference methods and the common scoring used for every arm of the campaign.

Every model here, and every LLM-written or LLM-edited head, maps the task's
*model inputs* to the target in physical units, so their numbers are comparable:

  model inputs = the task's features as given when they have a physical meaning
                 (atomic fractions), otherwise standardised with training-set
                 statistics (embedding components).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import torch
from scipy.stats import spearmanr
from sklearn.linear_model import RidgeCV
from sklearn.metrics import r2_score

from .heads import MLPHead
from .tasks import Task


@dataclass(frozen=True)
class Prepared:
    """One seed of one task, ready to fit and score."""

    U_train: np.ndarray
    y_train: np.ndarray
    U_test: np.ndarray
    y_test: np.ndarray
    y_mean: float
    y_std: float


def prepare(task: Task, seed: int) -> Prepared:
    train, test = task.split(seed)
    U = task.X
    if not task.named_features:
        U = (U - U[train].mean(0)) / (U[train].std(0) + 1e-8)
    return Prepared(
        U[train], task.y[train], U[test], task.y[test],
        float(task.y[train].mean()), float(task.y[train].std() + 1e-8),
    )


def score(y: np.ndarray, prediction: np.ndarray, std: np.ndarray | None = None) -> dict[str, float]:
    """R2, Spearman, RMSE, and the mean error on the top tenth of the true values.

    A negative `top_decile_bias` means the best candidates are underpredicted,
    which is the fault the published loop's surrogate shows.
    """
    top = y >= np.quantile(y, 0.9)
    out = {
        "r2": float(r2_score(y, prediction)),
        "spearman": float(spearmanr(y, prediction).statistic),
        "rmse": float(np.sqrt(np.mean((y - prediction) ** 2))),
        "top_decile_bias": float(np.mean(prediction[top] - y[top])),
    }
    if std is not None:
        out["coverage95"] = float(np.mean(np.abs(y - prediction) <= 1.96 * std))
    return out


def fit_gp(data: Prepared) -> tuple[np.ndarray, np.ndarray]:
    """Exact GP (BoTorch SingleTaskGP). Returns predictive mean and std in physical units."""
    from botorch.fit import fit_gpytorch_mll
    from botorch.models import SingleTaskGP
    from botorch.models.transforms.input import Normalize
    from gpytorch.mlls import ExactMarginalLogLikelihood

    X = torch.tensor(data.U_train, dtype=torch.float64)
    t = torch.tensor((data.y_train - data.y_mean) / data.y_std, dtype=torch.float64).unsqueeze(-1)
    # BoTorch's default lengthscale prior assumes inputs in the unit cube.
    model = SingleTaskGP(X, t, input_transform=Normalize(d=X.shape[-1]))
    fit_gpytorch_mll(ExactMarginalLogLikelihood(model.likelihood, model))
    model.eval()
    with torch.no_grad():
        posterior = model.posterior(
            torch.tensor(data.U_test, dtype=torch.float64), observation_noise=True
        )
    mean = posterior.mean.detach().squeeze(-1).numpy() * data.y_std + data.y_mean
    return mean, posterior.variance.detach().squeeze(-1).sqrt().numpy() * data.y_std


def fit_ridge(data: Prepared) -> np.ndarray:
    model = RidgeCV(alphas=np.logspace(-4, 3, 15)).fit(data.U_train, data.y_train)
    return model.predict(data.U_test)


def fit_mlp(
    data: Prepared, hidden: tuple[int, ...], seed: int,
    epochs: int = 800, lr: float = 3e-3, weight_decay: float = 1e-2,
) -> MLPHead:
    """The head trained the ordinary way. It is fitted on the standardised
    target, then the last layer is rescaled so the head outputs physical units."""
    torch.manual_seed(seed)
    head = MLPHead(data.U_train.shape[1], hidden, 1)
    optimizer = torch.optim.AdamW(head.parameters(), lr=lr, weight_decay=weight_decay)
    X = torch.tensor(data.U_train, dtype=torch.float32)
    t = torch.tensor((data.y_train - data.y_mean) / data.y_std, dtype=torch.float32).unsqueeze(-1)
    for _ in range(epochs):
        optimizer.zero_grad()
        torch.nn.functional.mse_loss(head(X), t).backward()
        optimizer.step()
    last = head.net[-1]
    with torch.no_grad():
        last.weight.mul_(data.y_std)
        last.bias.mul_(data.y_std).add_(data.y_mean)
    return head.eval()


def predict(head: torch.nn.Module, U: np.ndarray) -> np.ndarray:
    with torch.no_grad():
        return head(torch.tensor(U, dtype=torch.float32)).squeeze(-1).numpy().astype(np.float64)
