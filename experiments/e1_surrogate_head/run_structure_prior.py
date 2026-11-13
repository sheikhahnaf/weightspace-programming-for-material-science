"""E1: written priors for the structure-based surrogates of the closed loop.

The loop's GP sees a crystal as 50 embedding coordinates, which have no names, so a
model cannot write a network on them. It can write one on named descriptors of the
same crystal. Here the 15 -> 16 -> 1 networks written for the generator filter arm
(E3; bulk modulus and heat capacity, no data given) are evaluated on the descriptors
of each loop structure and used as the prior mean of the embedding GP. No new LLM
calls.

    python experiments/e1_surrogate_head/run_structure_prior.py --jobs 6

Train rows are drawn from the warm-start pool of one run; test rows are the structures
the generator proposed in that run. Arms:

  gp          plain GP on the embedding
  gp_desc     plain GP on the embedding and the 15 descriptors (same information, no LLM)
  two_stage   a, b by least squares on the prior, then a GP on the residuals
  map         GPyTorch LinearMean on the prior; a, b learned with the kernel
  marginal    prior as the mean, a and b integrated out

Priors: every valid written network, and one rule with no LLM and no data
(bulk modulus: 1 / volume per atom; heat capacity: Dulong-Petit, 3R / mean atomic mass).
"""

from __future__ import annotations

import argparse
import json
import sys
import warnings
from dataclasses import replace
from pathlib import Path

import numpy as np
from scipy.stats import wilcoxon

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
E3 = ROOT / "experiments" / "e3_crystal_filter"
sys.path.insert(0, str(E3))

OUT = HERE / "results" / "structure_prior"
TASKS = {"loop_bulk_modulus": "K", "loop_heat_capacity": "Cp"}
SIZES = (5, 10, 20, 50, 0)  # 0 = the whole warm-start pool
DRAWS = 3
ARMS = ("gp", "gp_desc", "two_stage", "map", "marginal")


def descriptors(task_name: str) -> np.ndarray:
    cache = OUT / f"descriptors__{task_name}.npy"
    if cache.exists():
        return np.load(cache)
    import filter_arm

    from wsp.tasks import closed_loop_atoms

    X = np.array([filter_arm.describe(a) for a in closed_loop_atoms(task_name)])
    cache.parent.mkdir(parents=True, exist_ok=True)
    np.save(cache, X)
    return X


def priors(task_name: str) -> dict[str, np.ndarray]:
    """Prior name -> prediction for every row of the task."""
    import filter_arm

    D = descriptors(task_name)
    key = TASKS[task_name]
    out = {"rule": 1.0 / D[:, 0] if key == "K" else 3 * 8.314462618 / D[:, 1]}
    for folder in sorted((E3 / "runs").glob(f"filter_{key}__*")):
        reply = folder / "reply.txt"
        if reply.exists():
            try:
                out[folder.name.replace(f"filter_{key}__", "")] = filter_arm.scorer(reply.read_text())(D)
            except Exception:
                pass  # an invalid reply was rejected when it was first scored
    return out


def nll(y, mean, std):
    std = np.maximum(std, 1e-9)
    return float(np.mean(0.5 * np.log(2 * np.pi * std**2) + 0.5 * ((y - mean) / std) ** 2))


def top_recall(y, mean, share=0.1):
    k = max(1, int(round(share * len(y))))
    return float(len(set(np.argsort(-y)[:k]) & set(np.argsort(-mean)[:k])) / k)


def with_descriptors(task_name, task, run, data, U, train, test):
    """Inputs of the gp_desc control: embedding plus z-scored descriptors.

    Descriptors that are constant on the run's pool are dropped. The first version divided
    them by (0 + 1e-8), which sent a test crystal with a non-zero value to about 1e7 and
    broke the control on bulk modulus (one composition-group fraction is zero in the whole
    starting set); `--refit-control` recomputed the cached cells, keeping the old value."""
    pool = task.split(run)[0]
    D = descriptors(task_name)
    keep = D[pool].std(0) > 1e-6
    Dz = (D[:, keep] - D[pool][:, keep].mean(0)) / D[pool][:, keep].std(0)
    return replace(data, U_train=np.hstack([U[train], Dz[train]]), U_test=np.hstack([U[test], Dz[test]]))


def refit_control(task_name: str, run: int, n: int, draw: int) -> None:
    """Recompute only the gp_desc arm of a cached cell with the corrected z-scoring."""
    import torch

    from wsp.baselines import fit_gp, prepare, score
    from wsp.tasks import load_task

    cache = OUT / "cells" / task_name / f"run{run}__n{n}__draw{draw}.json"
    out = json.loads(cache.read_text())
    if "gp_desc_first_version" in out:
        return
    warnings.filterwarnings("ignore")
    torch.set_num_threads(1)
    task = load_task(task_name)
    train, test = task.split(run)
    if n:
        train = train[np.random.default_rng(1000 * run + draw).permutation(len(train))[:n]]
    U = (task.X - task.X[task.split(run)[0]].mean(0)) / (task.X[task.split(run)[0]].std(0) + 1e-8)
    y = task.y
    data = replace(prepare(task, run), U_train=U[train], y_train=y[train], U_test=U[test], y_test=y[test],
                   y_mean=float(y[train].mean()), y_std=float(y[train].std() + 1e-8))
    mean, std = fit_gp(with_descriptors(task_name, task, run, data, U, train, test))
    out["gp_desc_first_version"] = out["gp_desc"]
    out["gp_desc"] = score(data.y_test, mean, std) | {"nll": nll(data.y_test, mean, std), "top_recall": top_recall(data.y_test, mean)}
    cache.write_text(json.dumps(out) + "\n")


def cell(task_name: str, run: int, n: int, draw: int) -> dict:
    cache = OUT / "cells" / task_name / f"run{run}__n{n}__draw{draw}.json"
    if cache.exists():
        return json.loads(cache.read_text())
    import torch
    from scipy.stats import spearmanr

    from wsp.arms import gp_with_prior
    from wsp.baselines import fit_gp, prepare, score
    from wsp.joint_mean import gp_joint_prior
    from wsp.tasks import load_task

    warnings.filterwarnings("ignore")
    torch.set_num_threads(1)
    task = load_task(task_name)
    train, test = task.split(run)
    if n:
        train = train[np.random.default_rng(1000 * run + draw).permutation(len(train))[:n]]
    full = prepare(task, run)  # standardised with the whole pool of this run, as the loop does
    U = (task.X - task.X[task.split(run)[0]].mean(0)) / (task.X[task.split(run)[0]].std(0) + 1e-8)
    y = task.y
    data = replace(full, U_train=U[train], y_train=y[train], U_test=U[test], y_test=y[test],
                   y_mean=float(y[train].mean()), y_std=float(y[train].std() + 1e-8))
    both = with_descriptors(task_name, task, run, data, U, train, test)

    def measure(mean, std):
        return score(data.y_test, mean, std) | {"nll": nll(data.y_test, mean, std), "top_recall": top_recall(data.y_test, mean)}

    out = {"task": task_name, "run": run, "n": int(len(train)), "draw": draw, "n_test": int(len(test)),
           "gp": measure(*fit_gp(data)), "gp_desc": measure(*fit_gp(both)), "priors": {}}
    for name, m in priors(task_name).items():
        entry = {"alone_spearman": float(spearmanr(m[test], y[test]).statistic)}
        fits = {"two_stage": lambda: gp_with_prior(data, m[train], m[test])[:2],
                "map": lambda: gp_joint_prior(data, m[train], m[test], "map")[:2],
                "marginal": lambda: gp_joint_prior(data, m[train], m[test], "marginal")[:2]}
        for arm, fit in fits.items():
            try:
                entry[arm] = measure(*fit())
            except Exception as error:  # a failed fit is recorded, not hidden
                entry[arm] = {"failed": type(error).__name__}
        out["priors"][name] = entry
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps(out) + "\n")
    return out


def group(name: str) -> str:
    return name if name == "rule" else name.split("__")[0]


def main() -> None:
    from joblib import Parallel, delayed

    from wsp.tasks import _CLOSED_LOOPS, _closed_loop_table

    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--jobs", type=int, default=6)
    parser.add_argument("--refit-control", action="store_true", help="recompute the gp_desc arm of cached cells (corrected z-scoring)")
    args = parser.parse_args()
    work = []
    for task_name in TASKS:
        descriptors(task_name)
        n_runs = _closed_loop_table(*_CLOSED_LOOPS[task_name])[1]
        work += [(task_name, r, n, d) for r in range(n_runs) for n in SIZES for d in range(DRAWS if n else 1)]
    if args.refit_control:
        Parallel(n_jobs=args.jobs)(delayed(refit_control)(*w) for w in work)
    cells = Parallel(n_jobs=args.jobs)(delayed(cell)(*w) for w in work)

    metrics = ("spearman", "top_recall", "top_decile_bias", "coverage95", "nll")
    summary, lines = {}, []
    for task_name in TASKS:
        lines += [f"**`{task_name}`**", "",
                  "| Labels | Arm | Prior | ρ | Best tenth found | Bias on best tenth | 95% coverage | NLL | ρ better / worse than plain GP (p) |",
                  "|---|---|---|---|---|---|---|---|---|"]
        for n in SIZES:
            rows = [c for c in cells if c["task"] == task_name and (c["n"] == n if n else c["draw"] == 0 and c["n"] > max(SIZES))]
            label = str(n) if n else f"all ({rows[0]['n']})"
            base = np.array([c["gp"]["spearman"] for c in rows])

            def line(arm, prior, values):
                ok = [v for v in values if "failed" not in v]
                mean = {m: float(np.mean([v[m] for v in ok])) for m in metrics}
                med_nll = float(np.median([v["nll"] for v in ok]))
                rho = np.array([v.get("spearman", np.nan) for v in values])
                d = rho - base[: len(rho)] if len(rho) == len(base) else np.array([])
                stat = ""
                if arm != "gp" and len(d) and np.all(np.isfinite(d)):
                    p = wilcoxon(d).pvalue if np.any(d != 0) else 1.0
                    stat = f"{int((d > 0).sum())} / {int((d < 0).sum())} ({p:.3g})"
                summary[f"{task_name}|n{label}|{arm}|{prior}"] = mean | {"nll_median": med_nll, "cells": len(ok), "failed": len(values) - len(ok), "vs_gp": stat}
                lines.append(f"| {label} | {arm} | {prior} | {mean['spearman']:.2f} | {mean['top_recall']:.2f} | {mean['top_decile_bias']:+.3g} | "
                             f"{mean['coverage95']:.2f} | {med_nll:.2f} | {stat} |")

            line("gp", "", [c["gp"] for c in rows])
            line("gp_desc", "", [c["gp_desc"] for c in rows])
            for g in ("rule", "opus", "fable", "sonnet", "haiku"):
                names = [k for k in rows[0]["priors"] if group(k) == g]
                if not names:
                    continue
                for arm in ("two_stage", "map", "marginal"):
                    # one value per cell: the mean over this model's replies, so cells stay paired with the plain GP
                    values = []
                    for c in rows:
                        fits = [c["priors"][k][arm] for k in names]
                        good = [f for f in fits if "failed" not in f]
                        values.append({m: float(np.mean([f[m] for f in good])) for m in metrics} if good else {"failed": "all"})
                    line(arm, f"{g} ({len(names)})" if g != "rule" else "rule", values)
        alone = {}
        for c in cells:
            if c["task"] == task_name and c["draw"] == 0 and c["n"] == min(k for k in SIZES if k):
                for k, v in c["priors"].items():
                    alone.setdefault(group(k), []).append(v["alone_spearman"])
        summary[f"{task_name}|alone"] = {g: float(np.mean(v)) for g, v in alone.items()}
        lines += ["", "Prior alone on the generated structures, ρ: " + ", ".join(f"{g} {np.mean(v):.2f}" for g, v in alone.items()), ""]
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    (OUT / "summary.md").write_text("\n".join(lines) + "\nMeans over runs and draws; NLL is the median. p values are Wilcoxon signed-rank, uncorrected, over run x draw cells; the runs of a task share one starting set and draws within a run are not independent, so these p values are too small. Tests with the run as the unit are in results/robustness/summary.md.\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
