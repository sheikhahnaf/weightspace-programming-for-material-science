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
RUN = re.compile(r"write__(?P<task>.+?)(?:__(?P<model>fable|opus|sonnet|haiku))?(?:__rep(?P<rep>\d+))?$")
THRESHOLD = 0.3


def candidates(task_name: str) -> dict[str, dict[str, np.ndarray]]:
    """arm -> {candidate name -> prior output on the whole pool, in the direction of improvement}."""
    from wsp.arms import handbook_prior, written_head
    from wsp.baselines import predict
    from wsp.tasks import load_task

    task = load_task(task_name)
    sign = GOALS[task_name]
    by_model: dict[str, dict[str, np.ndarray]] = {m: {} for m in MODELS}
    for folder in sorted((HERE / "runs").glob(f"write__{task_name}*")):
        m = RUN.fullmatch(folder.name)
        if not m or m["task"] != task_name or not (folder / "reply.txt").exists():
            continue
        try:
            head = written_head(task, (folder / "reply.txt").read_text())
        except Exception:
            continue  # an invalid reply is not a candidate
        by_model[m["model"] or "fable"][folder.name] = sign * predict(head, task.X)
    out = {"handbook": {"handbook": sign * handbook_prior(task)(task.X)}}
    for model, replies in by_model.items():
        out[f"select_{model}"] = replies
    out["select_all"] = {k: v for replies in by_model.values() for k, v in replies.items()}
    return out


def expected_improvement(mean, std, best):
    z = (mean - best) / np.maximum(std, 1e-12)
    return (mean - best) * norm.cdf(z) + std * norm.pdf(z)


def trace(task_name: str, arm: str, seed: int, n_init: int, steps: int) -> dict:
    cache = OUT / f"init{n_init}_steps{steps}" / task_name / f"{arm}__seed{seed}.json"
    if cache.exists():
        return json.loads(cache.read_text())
    import torch

    from wsp.arms import gp_with_prior
    from wsp.baselines import Prepared, fit_gp
    from wsp.tasks import load_task

    warnings.filterwarnings("ignore")
    torch.set_num_threads(1)
    task = load_task(task_name)
    X, y = task.X, GOALS[task_name] * task.y  # always maximise y
    priors = {} if arm in ("random", "gp") else candidates(task_name)[arm]
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


def summarise(n_init: int, steps: int, seeds: int) -> None:
    from wsp.tasks import load_task

    lines = [
        "| Task | Arm | Candidates | Regret after 5 | after 10 | after 25 | Area under regret | vs GP: seeds better / worse | Wilcoxon p (Holm) | Steps with a prior |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    summary = {}
    for task_name in GOALS:
        task = load_task(task_name)
        n_candidates = {arm: len(c) for arm, c in candidates(task_name).items()}
        rows = {}
        for arm in ARMS:
            traces = [json.loads((OUT / f"init{n_init}_steps{steps}" / task_name / f"{arm}__seed{s}.json").read_text())
                      for s in range(seeds)]
            regret = np.array([t["optimum"] - np.array(t["best_so_far"]) for t in traces])
            used = [name is not None for t in traces for name in t["prior_used"]]
            rows[arm] = {"regret": regret, "auc": regret[:, 1:].mean(1),
                         "prior_share": float(np.mean(used)) if used else 0.0}
        pvals = {}
        for arm in ARMS:
            if arm in ("random", "gp"):
                continue
            delta = rows[arm]["auc"] - rows["gp"]["auc"]
            pvals[arm] = float(wilcoxon(delta).pvalue) if np.any(delta != 0) else 1.0
        adjusted = holm(pvals)
        summary[task_name] = {}
        for arm in ARMS:
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
    (OUT / f"summary_{tag}.json").write_text(json.dumps({"n_init": n_init, "steps": steps, "seeds": seeds,
                                                  "threshold": THRESHOLD, "tasks": summary}, indent=1) + "\n")
    (OUT / f"summary_{tag}.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--seeds", type=int, default=20)
    parser.add_argument("--n-init", type=int, default=5)
    parser.add_argument("--steps", type=int, default=25)
    parser.add_argument("--jobs", type=int, default=8)
    args = parser.parse_args()

    from joblib import Parallel, delayed

    work = [(t, a, s) for t in GOALS for a in ARMS for s in range(args.seeds)]
    Parallel(n_jobs=args.jobs, verbose=5)(delayed(trace)(t, a, s, args.n_init, args.steps) for t, a, s in work)
    summarise(args.n_init, args.steps, args.seeds)


if __name__ == "__main__":
    main()
