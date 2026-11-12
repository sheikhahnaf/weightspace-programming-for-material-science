"""E7: every prior source in every GP mean arm, on the Thermo-Calc tasks.

Prior sources (a function of composition, in the target's unit, made with no pool data):

  rom                       rule of mixtures of the pure-element values
  subsystem_extrapolation   extrapolation of the binary and ternary facts
  select_<model>            networks written by <model> from the plain prompt   (runs/write__*)
  select_<model>_pd         networks written with the sub-system facts          (runs/writepd__*)

Mean arms for each source:

  two-stage   a*m(x)+b by least squares, then a GP on the residuals (`wsp.arms.gp_with_prior`)
  map         a and b learned with the kernel (`wsp.joint_mean.gp_joint_prior`, kind "map")
  marginal    a and b integrated out through a linear kernel term (kind "marginal")

and the plain constant-mean GP as the baseline.

    python experiments/e7_calphad_prior/run_priors.py static --jobs 4
    python experiments/e7_calphad_prior/run_priors.py bo --seeds 20 --steps 25 --jobs 4
    python experiments/e7_calphad_prior/run_priors.py bo --tasks cantor_al_solidus --sources rom subsystem_extrapolation

`static`: 5, 10, 20 and 50 labels, five seeds, scored on the task's test half:
Spearman rho, 95% coverage and negative log likelihood; and each prior alone on the
whole pool. A source with several replies is scored reply by reply and averaged.

`bo`: the loop and the selection rule of E1's run_bo_select.py (5 random initial
labels, 25 steps, expected improvement, 20 seeds, the same initial labels for every
arm of a seed; among a source's candidates use the one with the highest Pearson
correlation with the labels so far, none below 0.3). Arms: random, gp, <source>
(two-stage), <source>_map, <source>_marginal. Area under the regret curve, paired
Wilcoxon against the plain GP over seeds, Holm-corrected within a task.

Everything is cached per (task, candidate or arm, seed) under results/, so a run
resumes. A source with no valid reply yet, or whose prior is constant on the pool,
is left out: it would be the plain GP. A BO trace is cached with the candidates
that existed when it ran: run an LLM source only once all its replies are in.
"""

from __future__ import annotations

import argparse
import json
import sys
import warnings
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "e1_surrogate_head"))
import run_bo_select as bs  # noqa: E402

RUNS, OUT = HERE / "runs", HERE / "results"
SIZES = (5, 10, 20, 50)
KINDS = ("map", "marginal")
SOURCES = ("rom", "subsystem_extrapolation", "select_opus", "select_opus_pd", "select_fable", "select_fable_pd")
MEAN_ARMS = ("gp", "two_stage", *KINDS)


def nll(y, mean, std) -> float:
    std = np.maximum(std, 1e-9)
    return float(np.mean(0.5 * np.log(2 * np.pi * std**2) + 0.5 * ((y - mean) / std) ** 2))


def task_names(selection: list[str] | None) -> list[str]:
    from wsp.tasks import CALPHAD_TASK_NAMES

    if not selection:
        return list(CALPHAD_TASK_NAMES)
    return [t for t in CALPHAD_TASK_NAMES if t in selection or any(t.startswith(s + "_") for s in selection)]


def usable(task_name: str, sources) -> dict[str, dict[str, np.ndarray]]:
    """source -> {candidate -> prior on the pool, in the direction of improvement}, without constant priors."""
    found = bs.candidates(task_name, RUNS)
    out = {}
    for source in sources:
        kept = {name: m for name, m in found.get(source, {}).items() if np.ptp(m) > 0}
        if kept:
            out[source] = kept
    return out


# --------------------------------------------------------------------- static


def static_cell(task_name: str, source: str, candidate: str, seed: int) -> dict:
    cache = OUT / "static" / task_name / f"{candidate}__seed{seed}.json"
    if cache.exists():
        return json.loads(cache.read_text())
    import torch

    from wsp.arms import _subsample, gp_with_prior
    from wsp.baselines import fit_gp, prepare, score
    from wsp.joint_mean import gp_joint_prior
    from wsp.tasks import load_task

    warnings.filterwarnings("ignore")
    torch.set_num_threads(1)
    task = load_task(task_name)
    m = bs.goal(task_name) * usable(task_name, [source])[source][candidate]  # back to the target's own sign
    full = prepare(task, seed)
    train, test = task.split(seed)
    out = {"task": task_name, "source": source, "candidate": candidate, "seed": seed,
           "alone": score(task.y, m) | {"pearson": float(np.corrcoef(m, task.y)[0, 1])}}
    for n in [k for k in SIZES if k < len(train)]:
        rows = np.random.default_rng(seed).permutation(len(train))[:n]  # the rows `_subsample` takes
        data = _subsample(full, n, seed)
        m_train, m_test = m[train][rows], m[test]
        fits = {"gp": fit_gp(data), "two_stage": gp_with_prior(data, m_train, m_test)[:2]}
        for kind in KINDS:
            try:
                fits[kind] = gp_joint_prior(data, m_train, m_test, kind)[:2]
            except Exception as error:  # a failed fit is recorded, not hidden
                out.setdefault("failed", []).append(f"n{n} {kind}: {type(error).__name__}: {str(error)[:80]}")
        out[f"n{n}"] = {arm: score(data.y_test, mean, std) | {"nll": nll(data.y_test, mean, std)}
                        for arm, (mean, std) in fits.items()}
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps(out) + "\n")
    return out


def static(tasks: list[str], sources: list[str], jobs: int, seeds: int = 5) -> None:
    from joblib import Parallel, delayed

    work = [(t, s, c, seed) for t in tasks for s, found in usable(t, sources).items() for c in found for seed in range(seeds)]
    cells = Parallel(n_jobs=jobs, verbose=1)(delayed(static_cell)(*w) for w in work)
    lines = [
        "| Task | Prior source | Replies | Alone ρ (r) | Mean arm | ρ at 5 / 10 / 20 / 50 labels | 95% coverage at 5 / 10 / 20 / 50 | NLL at 5 / 10 / 20 / 50 |",
        "|---|---|---|---|---|---|---|---|",
    ]
    summary, failed = {}, [f"{c['task']} {c['candidate']} seed {c['seed']} {f}" for c in cells for f in c.get("failed", [])]
    for task_name in tasks:
        summary[task_name] = {}
        mine = [c for c in cells if c["task"] == task_name]
        for source in [s for s in sources if any(c["source"] == s for c in mine)]:
            group = [c for c in mine if c["source"] == source]
            replies = len({c["candidate"] for c in group})
            alone = f"{np.mean([c['alone']['spearman'] for c in group]):.2f} ({np.mean([c['alone']['pearson'] for c in group]):.2f})"
            item = {"candidates": replies, "alone_spearman": float(np.mean([c["alone"]["spearman"] for c in group])),
                    "alone_pearson": float(np.mean([c["alone"]["pearson"] for c in group]))}
            for arm in MEAN_ARMS:
                def stat(metric, how=np.mean):
                    return [float(how([c[f"n{n}"][arm][metric] for c in group if arm in c.get(f"n{n}", {})] or [np.nan]))
                            for n in SIZES]
                item[arm] = {"spearman": stat("spearman"), "coverage95": stat("coverage95"), "nll_median": stat("nll", np.median)}
                # the plain GP does not depend on the source; it is repeated on each source's rows for reading across
                lines.append(
                    f"| `{task_name}` | {source} | {replies} | {alone} | {arm} | "
                    + " / ".join(f"{v:.2f}" for v in item[arm]["spearman"]) + " | "
                    + " / ".join(f"{v:.2f}" for v in item[arm]["coverage95"]) + " | "
                    + " / ".join(f"{v:.3g}" for v in item[arm]["nll_median"]) + " |")
            summary[task_name][source] = item
    out = OUT / "static"
    out.mkdir(parents=True, exist_ok=True)
    (out / "summary.json").write_text(json.dumps({"sizes": SIZES, "seeds": seeds, "tasks": summary, "failed_fits": failed}, indent=1) + "\n")
    note = (f"\nMean over replies and {seeds} seeds; NLL is the median over cells (nats, target's own unit). "
            f"Alone: the prior against the whole pool, Spearman ρ (Pearson r). Failed joint fits: {len(failed)}.\n")
    (out / "summary.md").write_text("\n".join(lines) + "\n" + note)
    print("\n".join(lines), note)


# ------------------------------------------------------------------------- bo


def joint_trace(task_name: str, arm: str, seed: int, n_init: int, steps: int) -> dict:
    """arm = <source>_<kind>: the loop of bs.trace with the selected prior in a joint mean."""
    cache = OUT / "bo" / f"init{n_init}_steps{steps}" / task_name / f"{arm}__seed{seed}.json"
    if cache.exists():
        return json.loads(cache.read_text())
    import torch

    from wsp.baselines import Prepared, fit_gp
    from wsp.joint_mean import gp_joint_prior
    from wsp.tasks import load_task

    warnings.filterwarnings("ignore")
    torch.set_num_threads(1)
    source, kind = arm.rsplit("_", 1)
    task = load_task(task_name)
    X, y = task.X, bs.goal(task_name) * task.y  # always maximise y
    priors = bs.candidates(task_name, RUNS)[source]
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


def one_trace(task_name: str, arm: str, seed: int, n_init: int, steps: int) -> dict:
    if arm.rsplit("_", 1)[-1] in KINDS:
        return joint_trace(task_name, arm, seed, n_init, steps)
    return bs.trace(task_name, arm, seed, n_init, steps, RUNS, OUT / "bo")


def bo(tasks: list[str], sources: list[str], seeds: int, steps: int, jobs: int, n_init: int = 5) -> None:
    from joblib import Parallel, delayed

    arms = {t: ("random", "gp", *[a for s in usable(t, sources) for a in (s, *[f"{s}_{k}" for k in KINDS])]) for t in tasks}
    for t in tasks:
        left_out = [s for s in sources if s not in usable(t, sources)]
        if left_out:
            print(f"{t}: left out (no valid reply yet, or a constant prior): {', '.join(left_out)}", flush=True)
    work = [(t, a, s) for t in tasks for a in arms[t] for s in range(seeds)]
    Parallel(n_jobs=jobs, verbose=1)(delayed(one_trace)(t, a, s, n_init, steps) for t, a, s in work)
    bs.summarise(n_init, steps, seeds, arms, RUNS, OUT / "bo")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("static", "bo"):
        p = sub.add_parser(name)
        p.add_argument("--tasks", nargs="+", default=None, help="task or system names (default: every Thermo-Calc task)")
        p.add_argument("--sources", nargs="+", default=list(SOURCES), choices=SOURCES)
        p.add_argument("--jobs", type=int, default=4)
        if name == "bo":
            p.add_argument("--seeds", type=int, default=20)
            p.add_argument("--steps", type=int, default=25)
    args = parser.parse_args()
    warnings.filterwarnings("ignore")
    tasks = task_names(args.tasks)
    if args.command == "static":
        static(tasks, args.sources, args.jobs)
    else:
        bo(tasks, args.sources, args.seeds, args.steps, args.jobs)


if __name__ == "__main__":
    main()
