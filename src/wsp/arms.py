"""The LLM arms of experiment E1: build each prompt, apply and score each reply.

Arm C  "edit"   a trained head plus its out-of-fold errors by target decile;
                the LLM returns weight edits that should remove the bias.
Arm E  "write"  an all-zero network on named inputs plus a description of the
                task; the LLM returns every weight. The network is scored on its
                own and as the prior mean of a GP.

The reference methods that get the same information are here too: affine
recalibration for arm C, and a constant-mean GP at the same training size for arm E.
"""

from __future__ import annotations

from dataclasses import replace

import numpy as np
import torch
from sklearn.model_selection import KFold

from .baselines import Prepared, fit_gp, fit_mlp, predict, prepare, score
from .edit import apply_edits, diff, parse_edits
from .heads import MLPHead, zero_
from .prompts import build_prompt
from .serialize import load_weights
from .tasks import Task

EDIT_HIDDEN = (32, 32)
WRITE_HIDDEN = (16,)


# ---------------------------------------------------------------- arm C: edit


def out_of_fold(data: Prepared, hidden: tuple[int, ...], seed: int, folds: int = 5) -> np.ndarray:
    """Predictions for every training row from a head that never saw that row."""
    oof = np.empty_like(data.y_train)
    for fit, held in KFold(folds, shuffle=True, random_state=seed).split(data.U_train):
        part = replace(
            data, U_train=data.U_train[fit], y_train=data.y_train[fit],
            y_mean=float(data.y_train[fit].mean()), y_std=float(data.y_train[fit].std() + 1e-8),
        )
        oof[held] = predict(fit_mlp(part, hidden, seed), data.U_train[held])
    return oof


def _decile_table(y: np.ndarray, prediction: np.ndarray, unit: str) -> str:
    edges = np.quantile(y, np.linspace(0, 1, 11))
    lines = [f"decile of true value | true range ({unit}) | mean true | mean predicted | mean error"]
    for i in range(10):
        rows = (y >= edges[i]) & ((y <= edges[i + 1]) if i == 9 else (y < edges[i + 1]))
        if rows.any():
            lines.append(
                f"{i + 1} | {edges[i]:.4g} to {edges[i + 1]:.4g} | {y[rows].mean():.4g} "
                f"| {prediction[rows].mean():.4g} | {(prediction[rows] - y[rows]).mean():+.4g}"
            )
    return "\n".join(lines)


def edit_setup(task: Task, seed: int, shuffled: bool = False):
    """The trained head, its data and its out-of-fold predictions.

    `shuffled=True` permutes the entries of every tensor: the control that
    tells reasoning about these weights apart from a generic recipe.
    """
    data = prepare(task, seed)
    head = fit_mlp(data, EDIT_HIDDEN, seed)
    oof = out_of_fold(data, EDIT_HIDDEN, seed)
    if shuffled:
        generator = torch.Generator().manual_seed(seed)
        state = {
            k: v.flatten()[torch.randperm(v.numel(), generator=generator)].reshape(v.shape)
            for k, v in head.state_dict().items()
        }
        head.load_state_dict(state)
    return data, head, oof


def edit_prompt(task: Task, seed: int, shuffled: bool = False) -> str:
    data, head, oof = edit_setup(task, seed, shuffled)
    inputs = (
        "The inputs are used as given."
        if task.named_features
        else "Each input has been standardised to zero mean and unit variance on the training rows."
    )
    job = (
        f"This network is a surrogate inside a materials discovery loop. {task.description} "
        f"{inputs} The output y is the {task.target} in {task.unit}.\n\n"
        f"The network was trained on {len(data.y_train)} rows whose target has mean "
        f"{data.y_mean:.4g} and standard deviation {data.y_std:.4g} {task.unit}. The loop cares "
        f"most about the candidates with the highest true values, and those are the ones this "
        f"network gets wrong. Its errors on training rows it had not seen (five-fold "
        f"cross-validation), grouped by decile of the true value:\n\n"
        f"{_decile_table(data.y_train, oof, task.unit)}\n\n"
        f"Edit the weights so that the network stops underpredicting the highest values on new "
        f"candidates, without losing its ranking of the rest."
    )
    return build_prompt("edit", job, head.describe(), head.state_dict())


def affine_recalibration(data: Prepared, oof: np.ndarray, prediction: np.ndarray) -> np.ndarray:
    """Least-squares stretch of the predictions, fitted on out-of-fold predictions:
    the cheapest method given the same evidence as the LLM."""
    slope, intercept = np.polyfit(oof, data.y_train, 1)
    return slope * prediction + intercept


def score_edit(task: Task, seed: int, reply: str, shuffled: bool = False) -> dict:
    data, head, oof = edit_setup(task, seed, shuffled)
    before = head.state_dict()
    after = apply_edits(before, parse_edits(reply))
    edited = MLPHead(data.U_train.shape[1], EDIT_HIDDEN, 1)
    edited.load_state_dict(after)
    report = diff(before, after)
    base = predict(head, data.U_test)
    return {
        "arm": "edit", "task": task.name, "seed": seed, "shuffled_control": shuffled,
        "weights_changed": report.changed, "weights_total": report.total,
        "changed_by_tensor": report.changed_by_tensor,
        "unedited": score(data.y_test, base),
        "llm_edit": score(data.y_test, predict(edited.eval(), data.U_test)),
        "affine_recalibration": score(data.y_test, affine_recalibration(data, oof, base)),
    }


# --------------------------------------------------------------- arm E: write


def write_prompt(task: Task) -> str:
    if not task.named_features:
        raise ValueError(f"{task.name}: arm E needs inputs with a physical meaning")
    head = zero_(MLPHead(task.X.shape[1], WRITE_HIDDEN, 1))
    names = ", ".join(f"x[{i}] = {n}" for i, n in enumerate(task.feature_names))
    job = (
        f"Write the weights of this network from what you know about materials. No training "
        f"data is given. {task.description}\n\nInput order: {names}.\n\n"
        f"The output y must be your best estimate of the {task.target} in {task.unit}. The "
        f"network will be used as the prior mean of a Gaussian process that is then given a "
        f"few measured alloys, so getting the trends and the rough scale right matters more "
        f"than exact values."
    )
    return build_prompt("write", job, head.describe(), head.state_dict())


def _subsample(data: Prepared, n: int, seed: int) -> Prepared:
    rows = np.random.default_rng(seed).permutation(len(data.y_train))[:n]
    return replace(
        data, U_train=data.U_train[rows], y_train=data.y_train[rows],
        y_mean=float(data.y_train[rows].mean()), y_std=float(data.y_train[rows].std() + 1e-8),
    )


def gp_with_prior(data: Prepared, m_train: np.ndarray, m_test: np.ndarray):
    """GP whose mean is a·m(x) + b with a, b fitted on the training rows.

    If the written network is uninformative the fit drives a toward zero and
    this reduces to the constant-mean GP.
    """
    slope, intercept = np.polyfit(m_train, data.y_train, 1) if np.ptp(m_train) > 0 else (0.0, data.y_train.mean())
    residual = data.y_train - (slope * m_train + intercept)
    shifted = replace(data, y_train=residual, y_mean=float(residual.mean()), y_std=float(residual.std() + 1e-8))
    mean, std = fit_gp(shifted)
    return mean + slope * m_test + intercept, std, float(slope)


def score_write(task: Task, reply: str, seeds: int = 5, sizes: tuple[int, ...] = (10, 20, 50)) -> dict:
    head = MLPHead(task.X.shape[1], WRITE_HIDDEN, 1)
    head.load_state_dict(load_weights(reply))
    head.eval()
    rows = []
    for seed in range(seeds):
        full = prepare(task, seed)
        m_test = predict(head, full.U_test)
        row = {"seed": seed, "written_alone": score(full.y_test, m_test)}
        for n in (*sizes, len(full.y_train)):
            data = _subsample(full, n, seed)
            plain_mean, plain_std = fit_gp(data)
            prior_mean, prior_std, slope = gp_with_prior(data, predict(head, data.U_train), m_test)
            row[f"n{n}"] = {
                "gp": score(data.y_test, plain_mean, plain_std),
                "gp_with_written_prior": score(data.y_test, prior_mean, prior_std) | {"prior_slope": slope},
            }
        rows.append(row)
    return {"arm": "write", "task": task.name, "weights": sum(p.numel() for p in head.parameters()), "per_seed": rows}
