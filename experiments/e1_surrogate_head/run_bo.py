"""E1 downstream test: does an LLM-written prior mean make BO find good alloys sooner?

Pool-based Bayesian optimisation on the two composition tasks. Each run starts
from the same few random labelled alloys and at every step labels the unlabelled
alloy with the highest expected improvement under one of:

  gp                      constant-mean GP
  prior_fitted__<reply>   GP whose mean is a*m(x)+b, a and b fitted each step
  prior_one__<reply>      the same with a fixed at 1
  written_only__<reply>   no GP: label alloys in the order the written network ranks them
  random                  label at random

m(x) is a network whose weights an LLM wrote with no data (runs/write__<task>*).

    python experiments/e1_surrogate_head/run_bo.py
"""

from __future__ import annotations

import argparse
import json
import warnings
from pathlib import Path

import numpy as np
from scipy.stats import norm

from wsp import MLPHead, load_weights
from wsp.arms import WRITE_HIDDEN, gp_with_prior
from wsp.baselines import Prepared, fit_gp, predict
from wsp.tasks import load_task

HERE = Path(__file__).resolve().parent
# Direction of improvement: strong alloys; low-modulus titanium alloys (implants).
GOALS = {"mpea_yield_strength": +1.0, "ti_alloy_youngs_modulus": -1.0}


def written_networks(task_name: str, d: int) -> dict[str, np.ndarray]:
    out = {}
    for folder in sorted((HERE / "runs").glob(f"write__{task_name}*")):
        if (folder / "reply.txt").exists():
            head = MLPHead(d, WRITE_HIDDEN, 1)
            head.load_state_dict(load_weights((folder / "reply.txt").read_text()))
            reply = "rep1" if folder.name == f"write__{task_name}" else folder.name.split("__")[-1]
            out[reply] = head.eval()
    return out


def expected_improvement(mean: np.ndarray, std: np.ndarray, best: float) -> np.ndarray:
    z = (mean - best) / np.maximum(std, 1e-12)
    return (mean - best) * norm.cdf(z) + std * norm.pdf(z)


def run(task_name: str, policy: str, m: np.ndarray | None, seed: int, n_init: int, steps: int) -> list[float]:
    task = load_task(task_name)
    X, y = task.X, GOALS[task_name] * task.y  # always maximise y
    rng = np.random.default_rng(seed)
    labelled = list(rng.permutation(len(y))[:n_init])
    best = [float(y[labelled].max())]
    for _ in range(steps):
        pool = np.setdiff1d(np.arange(len(y)), labelled)
        if policy == "random":
            pick = int(rng.choice(pool))
        elif policy == "written_only":
            pick = int(pool[np.argmax(m[pool])])
        else:
            yt = y[labelled]
            data = Prepared(X[labelled], yt, X[pool], y[pool], float(yt.mean()), float(yt.std() + 1e-8))
            if policy == "gp":
                mean, std = fit_gp(data)
            else:
                mean, std, _ = gp_with_prior(data, m[labelled], m[pool], slope_rule=policy.removeprefix("prior_"))
            pick = int(pool[np.argmax(expected_improvement(mean, std, yt.max()))])
        labelled.append(pick)
        best.append(float(y[labelled].max()))
    return best


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--seeds", type=int, default=8)
    parser.add_argument("--n-init", type=int, default=5)
    parser.add_argument("--steps", type=int, default=25)
    args = parser.parse_args()
    warnings.filterwarnings("ignore")

    out = HERE / "results" / "bo"
    out.mkdir(parents=True, exist_ok=True)
    for task_name, sign in GOALS.items():
        task = load_task(task_name)
        y = sign * task.y
        top = np.quantile(y, 0.95)
        arms: dict[str, tuple[str, np.ndarray | None]] = {"gp": ("gp", None), "random": ("random", None)}
        for reply, head in written_networks(task_name, task.X.shape[1]).items():
            m = sign * predict(head, task.X)
            arms[f"prior_fitted__{reply}"] = ("prior_fitted", m)
            arms[f"prior_one__{reply}"] = ("prior_one", m)
            arms[f"written_only__{reply}"] = ("written_only", m)
        result = {"task": task_name, "goal": "maximise" if sign > 0 else "minimise", "unit": task.unit,
                  "pool": int(len(y)), "optimum": float(sign * y.max()), "top5pct_threshold": float(sign * top),
                  "n_init": args.n_init, "steps": args.steps, "seeds": args.seeds, "arms": {}}
        for name, (policy, m) in arms.items():
            traces = np.array([run(task_name, policy, m, seed, args.n_init, args.steps) for seed in range(args.seeds)])
            regret = y.max() - traces
            result["arms"][name] = {
                "best_so_far_mean": (sign * traces.mean(0)).tolist(),
                "regret_mean": regret.mean(0).tolist(),
                "regret_std": regret.std(0).tolist(),
                "final_regret_per_seed": regret[:, -1].tolist(),
                "regret_at_10": float(regret[:, min(10, args.steps)].mean()),
                "regret_final": float(regret[:, -1].mean()),
                "seeds_reaching_top5pct": int((traces[:, -1] >= top).sum()),
                "mean_steps_to_top5pct": float(np.mean([
                    (np.argmax(t >= top) if (t >= top).any() else args.steps + 1) for t in traces])),
            }
            a = result["arms"][name]
            print(f"{task_name:26s} {name:22s} regret@10 {a['regret_at_10']:8.2f}  final {a['regret_final']:8.2f}  "
                  f"top5% in {a['seeds_reaching_top5pct']}/{args.seeds} seeds, mean steps {a['mean_steps_to_top5pct']:.1f}", flush=True)
        (out / f"{task_name}.json").write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
