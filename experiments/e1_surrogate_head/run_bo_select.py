"""E1 step A4: BO with LLM-written priors chosen by the first labels, at scale.

Round 2 found that one written prior in three helped BO and the others did not.
This run tests the obvious remedy, fixed before looking at any result of it:

  At every BO step, among the candidate priors of an arm, take the one whose
  output has the highest Pearson correlation with the labels seen so far. If
  that correlation is below 0.3, use no prior (plain GP) for that step. The
  chosen prior enters as the GP mean a*m(x)+b with a, b fitted on the labels.

Arms, on each of the five alloy tasks (pool-based BO, 5 random initial labels,
25 steps, 20 seeds; the same initial labels for every arm of a seed):

  random            label at random
  gp                constant-mean GP, expected improvement
  handbook          the no-LLM rule of mixtures as the only candidate prior
  select_<model>    the valid replies of one model (fable, opus, sonnet, haiku) as candidates
  select_all        every valid reply of every model as candidates

Reported per task and arm: regret after 5, 10 and 25 labels, area under the
regret curve, and a paired Wilcoxon signed-rank test against `gp` over the 20
seeds on that area, with Holm correction across the non-random arms of a task.

Resumable: each (task, arm, seed) trace is cached under results/bo_select/.

    python experiments/e1_surrogate_head/run_bo_select.py --jobs 8

Experiment E7 runs the same loop, with the same rule, on the Thermo-Calc tasks
(`--tasks calphad`, runs and results in experiments/e7_calphad_prior). There the
no-LLM arms are `rom` and `binary_extrapolation` in place of `handbook`, and
`select_<model>_pd` takes the replies to the prompt that carried binary
phase-diagram facts (run folders `writepd__*`). On those tasks an arm with no
candidate, or whose only candidates are constant, is the plain GP by
construction and is left out rather than run. A trace is cached with the
candidates that existed when it ran: run an LLM arm only once all its replies are in.
"""

from __future__ import annotations

import argparse
import json
import re
import warnings
from pathlib import Path

import numpy as np
from scipy.stats import norm, wilcoxon

HERE = Path(__file__).resolve().parent
OUT = HERE / "results" / "bo_select"
# Direction of improvement: strong, hard alloys; low-modulus titanium alloys (implants).
GOALS = {
    "ti_alloy_youngs_modulus": -1.0, "ti_alloy_yield_strength": +1.0, "ti_alloy_hardness": +1.0,
    "mpea_yield_strength": +1.0, "mpea_hardness": +1.0,
}
MODELS = ("fable", "opus", "sonnet", "haiku")
ARMS = ("random", "gp", "handbook", *[f"select_{m}" for m in MODELS], "select_all")
CALPHAD_ARMS = ("random", "gp", "rom", "binary_extrapolation",
                *[f"select_{m}{pd}" for m in ("opus", "fable") for pd in ("", "_pd")])
RUN = re.compile(r"(?P<arm>write|writepd)__(?P<task>.+?)(?:__(?P<model>fable|opus|sonnet|haiku))?(?:__rep(?P<rep>\d+))?$")
THRESHOLD = 0.3


def goal(task_name: str) -> float:
    """+1 if the task's target is to be maximised, -1 if minimised."""
    from wsp.tasks import CALPHAD_GOALS

    return GOALS[task_name] if task_name in GOALS else CALPHAD_GOALS[task_name]


def candidates(task_name: str, runs: Path | None = None) -> dict[str, dict[str, np.ndarray]]:
    """arm -> {candidate name -> prior output on the whole pool, in the direction of improvement}."""
    from wsp.arms import reference_priors, written_head
    from wsp.baselines import predict
    from wsp.tasks import load_task

    task = load_task(task_name)
    sign = goal(task_name)
    by_model: dict[str, dict[str, np.ndarray]] = {f"{m}{pd}": {} for m in MODELS for pd in ("", "_pd")}
    for folder in sorted((runs or HERE / "runs").glob(f"write*__{task_name}*")):
        m = RUN.fullmatch(folder.name)
        if not m or m["task"] != task_name or not (folder / "reply.txt").exists():
            continue
        try:
            head = written_head(task, (folder / "reply.txt").read_text())
        except Exception:
            continue  # an invalid reply is not a candidate
        key = (m["model"] or "fable") + ("_pd" if m["arm"] == "writepd" else "")
        by_model[key][folder.name] = sign * predict(head, task.X)
    out = {name: {name: sign * prior(task.X)} for name, prior in reference_priors(task).items()}
    for model, replies in by_model.items():
        out[f"select_{model}"] = replies
    for pd in ("", "_pd"):
        out[f"select_all{pd}"] = {k: v for model, replies in by_model.items() if model.endswith("_pd") == bool(pd)
                                  for k, v in replies.items()}
    return out


def arms_for(task_name: str, arms: tuple[str, ...] | None, runs: Path | None) -> tuple[str, ...]:
    """The arms to run on a task. The E1 tasks keep the arms as given. On a Thermo-Calc
    task an arm that could never use a prior is dropped, with a note."""
    if task_name in GOALS:
        return arms or ARMS
    found, kept = candidates(task_name, runs), []
    for arm in arms or CALPHAD_ARMS:
        usable = [m for m in found.get(arm, {}).values() if np.ptp(m) > 0]
        if arm in ("random", "gp") or usable:
            kept.append(arm)
        else:
            why = "no valid reply yet" if not found.get(arm) else "its prior is constant"
            print(f"{task_name}: arm {arm} left out ({why}); it would be the plain GP", flush=True)
    return tuple(kept)


def expected_improvement(mean, std, best):
    z = (mean - best) / np.maximum(std, 1e-12)
    return (mean - best) * norm.cdf(z) + std * norm.pdf(z)


def trace(task_name: str, arm: str, seed: int, n_init: int, steps: int,
          runs: Path | None = None, out: Path | None = None) -> dict:
    cache = (out or OUT) / f"init{n_init}_steps{steps}" / task_name / f"{arm}__seed{seed}.json"
    if cache.exists():
        return json.loads(cache.read_text())
    import torch

    from wsp.arms import gp_with_prior
    from wsp.baselines import Prepared, fit_gp
    from wsp.tasks import load_task

    warnings.filterwarnings("ignore")
    torch.set_num_threads(1)
    task = load_task(task_name)
    X, y = task.X, goal(task_name) * task.y  # always maximise y
    priors = {} if arm in ("random", "gp") else candidates(task_name, runs)[arm]
    rng = np.random.default_rng(seed)
    labelled = list(rng.permutation(len(y))[:n_init])
    best, chosen = [float(y[labelled].max())], []
    for _ in range(steps):
        pool = np.setdiff1d(np.arange(len(y)), labelled)
        if arm == "random":
            pick = int(rng.choice(pool))
        else:
            yt = y[labelled]
            data = Prepared(X[labelled], yt, X[pool], y[pool], float(yt.mean()), float(yt.std() + 1e-8))
            name, score = None, THRESHOLD
            for candidate, m in priors.items():
                if np.ptp(m[labelled]) > 0 and np.ptp(yt) > 0:
                    r = float(np.corrcoef(m[labelled], yt)[0, 1])
                    if r > score:
                        name, score = candidate, r
            if name is None:
                mean, std = fit_gp(data)
            else:
                mean, std, _ = gp_with_prior(data, priors[name][labelled], priors[name][pool], slope_rule="fitted")
            chosen.append(name)
            pick = int(pool[np.argmax(expected_improvement(mean, std, yt.max()))])
        labelled.append(pick)
        best.append(float(y[labelled].max()))
    result = {"task": task_name, "arm": arm, "seed": seed, "best_so_far": best, "optimum": float(y.max()),
              "prior_used": chosen}
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps(result) + "\n")
    return result


def holm(pvalues: dict[str, float]) -> dict[str, float]:
    order = sorted(pvalues, key=pvalues.get)
    adjusted, running = {}, 0.0
    for rank, name in enumerate(order):
        running = max(running, min(1.0, (len(order) - rank) * pvalues[name]))
        adjusted[name] = running
    return adjusted


def summarise(n_init: int, steps: int, seeds: int, arms_by_task: dict[str, tuple[str, ...]] | None = None,
              runs: Path | None = None, out: Path | None = None) -> None:
    from wsp.tasks import load_task

    arms_by_task = arms_by_task or {task_name: ARMS for task_name in GOALS}
    out = out or OUT

    lines = [
        "| Task | Arm | Candidates | Regret after 5 | after 10 | after 25 | Area under regret | vs GP: seeds better / worse | Wilcoxon p (Holm) | Steps with a prior |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    summary = {}
    for task_name, arms in arms_by_task.items():
        task = load_task(task_name)
        n_candidates = {arm: len(c) for arm, c in candidates(task_name, runs).items()}
        rows = {}
        for arm in arms:
            traces = [json.loads((out / f"init{n_init}_steps{steps}" / task_name / f"{arm}__seed{s}.json").read_text())
                      for s in range(seeds)]
            regret = np.array([t["optimum"] - np.array(t["best_so_far"]) for t in traces])
            used = [name is not None for t in traces for name in t["prior_used"]]
            rows[arm] = {"regret": regret, "auc": regret[:, 1:].mean(1),
                         "prior_share": float(np.mean(used)) if used else 0.0}
        pvals = {}
        for arm in arms:
            if arm in ("random", "gp"):
                continue
            delta = rows[arm]["auc"] - rows["gp"]["auc"]
            pvals[arm] = float(wilcoxon(delta).pvalue) if np.any(delta != 0) else 1.0
        adjusted = holm(pvals)
        summary[task_name] = {}
        for arm in arms:
            r = rows[arm]
            better = int((r["auc"] < rows["gp"]["auc"]).sum())
            worse = int((r["auc"] > rows["gp"]["auc"]).sum())
            item = {
                "candidates": n_candidates.get(arm, 0),
                "regret_at_5": float(r["regret"][:, 5].mean()), "regret_at_10": float(r["regret"][:, 10].mean()),
                "regret_at_25": float(r["regret"][:, steps].mean()),
                "auc_mean": float(r["auc"].mean()), "auc_sem": float(r["auc"].std(ddof=1) / np.sqrt(seeds)),
                "seeds_better_than_gp": better, "seeds_worse_than_gp": worse,
                "wilcoxon_p": pvals.get(arm), "wilcoxon_p_holm": adjusted.get(arm),
                "share_of_steps_with_a_prior": r["prior_share"],
            }
            summary[task_name][arm] = item
            p = "" if arm in ("random", "gp") else f"{item['wilcoxon_p']:.3g} ({item['wilcoxon_p_holm']:.3g})"
            vs = "" if arm == "gp" else f"{better} / {worse}"
            lines.append(
                f"| `{task_name}` ({task.unit}) | {arm} | {item['candidates'] or ''} | {item['regret_at_5']:.3g} "
                f"| {item['regret_at_10']:.3g} | {item['regret_at_25']:.3g} | {item['auc_mean']:.3g} ± {item['auc_sem']:.2g} "
                f"| {vs} | {p} | {item['share_of_steps_with_a_prior']:.2f} |"
            )
    tag = f"init{n_init}_steps{steps}_seeds{seeds}"
    (out / f"summary_{tag}.json").write_text(json.dumps({"n_init": n_init, "steps": steps, "seeds": seeds,
                                                  "threshold": THRESHOLD, "tasks": summary}, indent=1) + "\n")
    (out / f"summary_{tag}.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--seeds", type=int, default=20)
    parser.add_argument("--n-init", type=int, default=5)
    parser.add_argument("--steps", type=int, default=25)
    parser.add_argument("--jobs", type=int, default=8)
    parser.add_argument("--tasks", nargs="+", default=None,
                        help="default: the five E1 alloy tasks; 'calphad' = every Thermo-Calc task of E7")
    parser.add_argument("--arms", nargs="+", default=None, help="default: every arm defined for the task")
    parser.add_argument("--runs", type=Path, default=None, help="folder of run folders (default: this experiment's)")
    parser.add_argument("--out", type=Path, default=None, help="results folder (default: results/bo_select here)")
    args = parser.parse_args()

    from joblib import Parallel, delayed

    from wsp.tasks import CALPHAD_TASK_NAMES

    tasks = [t for name in (args.tasks or GOALS) for t in (CALPHAD_TASK_NAMES if name == "calphad" else (name,))]
    arms = {t: arms_for(t, tuple(args.arms) if args.arms else None, args.runs) for t in tasks}
    work = [(t, a, s) for t in tasks for a in arms[t] for s in range(args.seeds)]
    Parallel(n_jobs=args.jobs, verbose=5)(
        delayed(trace)(t, a, s, args.n_init, args.steps, args.runs, args.out) for t, a, s in work)
    summarise(args.n_init, args.steps, args.seeds, arms, args.runs, args.out)


if __name__ == "__main__":
    main()
