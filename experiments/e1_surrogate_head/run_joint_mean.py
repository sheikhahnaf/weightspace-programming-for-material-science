"""E1: the written network in the GP mean, fitted jointly with BoTorch, against the
two-stage fit used so far.

    python experiments/e1_surrogate_head/run_joint_mean.py static --jobs 6
    python experiments/e1_surrogate_head/run_joint_mean.py bo --seeds 20 --steps 25 --jobs 6

Arms (see src/wsp/joint_mean.py):
  gp          plain GP, constant mean
  two_stage   a, b by least squares, then a GP on the residuals (round 3)
  map         GPyTorch LinearMean on the network output; a, b learned with the kernel
  marginal    network output as the mean, a and b integrated out through a linear kernel term

`static`: every valid Opus 5.5 and Fable 5.2 reply, five alloy tasks, 5 / 10 / 20 / 50
labels, five seeds; ranking, R2, 95% coverage and negative log likelihood on the rest.
`bo`: the loop of run_bo_select.py (same seeds, same first-label selection rule, same
candidates), with the selected prior entering through `map` or `marginal`. Plain-GP and
two-stage traces are read from results/bo_select/, so the comparison is paired by seed.
"""

from __future__ import annotations

import argparse
import json
import sys
import warnings
from pathlib import Path

import numpy as np
from scipy.stats import wilcoxon

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run_bo_select as bs  # noqa: E402

OUT = HERE / "results" / "joint_mean"
SIZES = (5, 10, 20, 50)
MODELS = ("opus", "fable")
KINDS = ("map", "marginal")


def nll(y, mean, std):
    std = np.maximum(std, 1e-9)
    return float(np.mean(0.5 * np.log(2 * np.pi * std**2) + 0.5 * ((y - mean) / std) ** 2))


def static_cell(task_name: str, run: str, seed: int) -> dict:
    cache = OUT / "static" / task_name / f"{run}__seed{seed}.json"
    if cache.exists():
        return json.loads(cache.read_text())
    import torch

    from wsp.arms import _subsample, gp_with_prior, written_head
    from wsp.baselines import fit_gp, predict, prepare, score
    from wsp.joint_mean import gp_joint_prior
    from wsp.tasks import load_task

    warnings.filterwarnings("ignore")
    torch.set_num_threads(1)
    task = load_task(task_name)
    head = written_head(task, (HERE / "runs" / run / "reply.txt").read_text())
    full = prepare(task, seed)
    m_test = predict(head, full.U_test)
    out = {"task": task_name, "run": run, "seed": seed}
    for n in [k for k in SIZES if k < len(full.y_train)]:
        data = _subsample(full, n, seed)
        m_train = predict(head, data.U_train)
        fits = {"gp": fit_gp(data), "two_stage": gp_with_prior(data, m_train, m_test)[:2]}
        for kind in KINDS:
            try:
                fits[kind] = gp_joint_prior(data, m_train, m_test, kind)[:2]
            except Exception as error:  # a failed fit is recorded, not hidden
                out.setdefault("failed", []).append(f"n{n} {kind}: {type(error).__name__}")
        out[f"n{n}"] = {arm: score(data.y_test, mean, std) | {"nll": nll(data.y_test, mean, std)} for arm, (mean, std) in fits.items()}
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps(out) + "\n")
    return out


def static(jobs: int) -> None:
    from joblib import Parallel, delayed

    work = []
    for task in bs.GOALS:
        for folder in sorted((HERE / "runs").glob(f"write__{task}__*")):
            m = bs.RUN.fullmatch(folder.name)
            if m and m["task"] == task and m["model"] in MODELS and (folder / "reply.txt").exists():
                work += [(task, folder.name, s) for s in range(5)]
    cells = Parallel(n_jobs=jobs)(delayed(_safe_static)(*w) for w in work)
    cells = [c for c in cells if c]
    arms = ("gp", "two_stage", *KINDS)
    lines = ["| Labels | Arm | ρ | R² | 95% coverage | NLL | Cells where ρ beats the plain GP |", "|---|---|---|---|---|---|---|"]
    summary = {}
    for n in SIZES:
        rows = [c[f"n{n}"] for c in cells if f"n{n}" in c and all(a in c[f"n{n}"] for a in arms)]
        for arm in arms:
            med = lambda k: float(np.median([r[arm][k] for r in rows]))
            mean = lambda k: float(np.mean([r[arm][k] for r in rows]))
            wins = sum(r[arm]["spearman"] > r["gp"]["spearman"] for r in rows)
            summary[f"n{n}|{arm}"] = {"cells": len(rows), "spearman": mean("spearman"), "r2_median": med("r2"),
                                      "coverage95": mean("coverage95"), "nll_median": med("nll"), "wins_vs_gp": wins}
            lines.append(f"| {n} | {arm} | {mean('spearman'):.2f} | {med('r2'):.2f} | {mean('coverage95'):.2f} | {med('nll'):.2f} | "
                         f"{'' if arm == 'gp' else f'{wins} of {len(rows)}'} |")
    failed = [f for c in cells for f in c.get("failed", [])]
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "static_summary.json").write_text(json.dumps({"summary": summary, "failed_fits": failed}, indent=2) + "\n")
    (OUT / "static_summary.md").write_text("\n".join(lines) + f"\n\nFailed fits: {len(failed)}. R² and NLL are medians (a few cells have extreme values).\n")
    print("\n".join(lines), f"\nfailed fits: {len(failed)}")


def _safe_static(task, run, seed):
    try:
        return static_cell(task, run, seed)
    except Exception as error:
        print("SKIPPED", task, run, seed, type(error).__name__, str(error)[:80], flush=True)
        return None


def bo_trace(task_name: str, arm: str, seed: int, n_init: int, steps: int) -> dict:
    """arm = select_<model>_<kind>."""
    cache = OUT / "bo" / f"init{n_init}_steps{steps}" / task_name / f"{arm}__seed{seed}.json"
    if cache.exists():
        return json.loads(cache.read_text())
    import torch

    from wsp.baselines import Prepared, fit_gp
    from wsp.joint_mean import gp_joint_prior
    from wsp.tasks import load_task

    warnings.filterwarnings("ignore")
    torch.set_num_threads(1)
    base, kind = arm.rsplit("_", 1)
    task = load_task(task_name)
    X, y = task.X, bs.GOALS[task_name] * task.y
    priors = bs.candidates(task_name)[base]
    rng = np.random.default_rng(seed)
    labelled = list(rng.permutation(len(y))[:n_init])
    best, chosen = [float(y[labelled].max())], []
    for _ in range(steps):
        pool = np.setdiff1d(np.arange(len(y)), labelled)
        yt = y[labelled]
        data = Prepared(X[labelled], yt, X[pool], y[pool], float(yt.mean()), float(yt.std() + 1e-8))
        name, top = None, bs.THRESHOLD
        for candidate, m in priors.items():
            if np.ptp(m[labelled]) > 0 and np.ptp(yt) > 0:
                r = float(np.corrcoef(m[labelled], yt)[0, 1])
                if r > top:
                    name, top = candidate, r
        try:
            mean, std = fit_gp(data) if name is None else gp_joint_prior(data, priors[name][labelled], priors[name][pool], kind)[:2]
        except Exception:
            mean, std = fit_gp(data)
            name = f"{name} (fit failed, plain GP used)"
        chosen.append(name)
        labelled.append(int(pool[np.argmax(bs.expected_improvement(mean, std, yt.max()))]))
        best.append(float(y[labelled].max()))
    result = {"task": task_name, "arm": arm, "seed": seed, "best_so_far": best, "optimum": float(y.max()), "prior_used": chosen}
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps(result) + "\n")
    return result


def bo(seeds: int, steps: int, jobs: int, n_init: int = 5) -> None:
    from joblib import Parallel, delayed

    arms = [f"select_{m}_{k}" for m in MODELS for k in KINDS]
    work = [(t, a, s) for t in bs.GOALS for a in arms for s in range(seeds)]
    Parallel(n_jobs=jobs)(delayed(bo_trace)(t, a, s, n_init, steps) for t, a, s in work)
    auc = lambda d: float(np.mean(d["optimum"] - np.array(d["best_so_far"])))
    old = bs.OUT / f"init{n_init}_steps{steps}"
    lines = ["| Task | Prior | Plain GP | Two-stage | Joint, learned a and b | Joint, a and b integrated out | Learned vs two-stage: better / worse (Wilcoxon p) | Integrated vs two-stage |",
             "|---|---|---|---|---|---|---|---|"]
    table = {}
    for task in bs.GOALS:
        for model in MODELS:
            col = {}
            for label, path in (("gp", old / task / "gp__seed{}.json"), ("two_stage", old / task / f"select_{model}__seed{{}}.json"),
                                *[(k, OUT / "bo" / f"init{n_init}_steps{steps}" / task / f"select_{model}_{k}__seed{{}}.json") for k in KINDS]):
                col[label] = np.array([auc(json.loads(Path(str(path).format(s)).read_text())) for s in range(seeds)])

            def versus(k):
                d = col[k] - col["two_stage"]
                p = wilcoxon(col[k], col["two_stage"]).pvalue if np.any(d != 0) else 1.0
                return f"{int((d < 0).sum())} / {int((d > 0).sum())} ({p:.3g})"

            table[f"{task}|{model}"] = {k: float(v.mean()) for k, v in col.items()}
            lines.append(f"| `{task}` | {model} | {col['gp'].mean():.3g} | {col['two_stage'].mean():.3g} | {col['map'].mean():.3g} | "
                         f"{col['marginal'].mean():.3g} | {versus('map')} | {versus('marginal')} |")
    (OUT / f"bo_summary_seeds{seeds}.json").write_text(json.dumps(table, indent=2) + "\n")
    (OUT / f"bo_summary_seeds{seeds}.md").write_text("\n".join(lines) + "\n\nArea under the regret curve, mean over seeds; lower is better. p values are uncorrected.\n")
    print("\n".join(lines))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    s = sub.add_parser("static")
    s.add_argument("--jobs", type=int, default=6)
    b = sub.add_parser("bo")
    b.add_argument("--seeds", type=int, default=20)
    b.add_argument("--steps", type=int, default=25)
    b.add_argument("--jobs", type=int, default=6)
    args = parser.parse_args()
    static(args.jobs) if args.command == "static" else bo(args.seeds, args.steps, args.jobs)


if __name__ == "__main__":
    main()
