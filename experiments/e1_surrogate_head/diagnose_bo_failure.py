"""E1: why does a written prior help Bayesian optimisation on four alloy tasks and hurt on one?

For each task and each Opus 5.5 / Fable 5.2 reply, on the whole pool (goal direction):
  rho_all        rank correlation of the prior with the property
  rho_top10      the same within the best tenth of the pool (does it order the tail?)
  optimum_pct    percentile at which the prior places the pool's best alloy (100 = top)
  top5_recall    share of the five best alloys that the prior puts in its own top tenth
  top_decile_bias   prior minus truth on the best tenth, after a least-squares slope and
                 offset fitted on the whole pool, in units of the pool's standard deviation
And from the BO traces of round 3 (select_<model> and gp, 20 seeds): how often the
selected prior was in use, and the share of seeds in which the best alloy was found.

    python experiments/e1_surrogate_head/diagnose_bo_failure.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run_bo_select as bs  # noqa: E402


def main() -> None:
    from wsp.tasks import load_task

    rows, lines = [], ["| Task | Model | ρ, whole pool | ρ within best tenth | Percentile given to the best alloy | Five best alloys in prior's top tenth | Bias on best tenth (pool SDs) | Seeds finding the best alloy: GP → with prior |",
                       "|---|---|---|---|---|---|---|---|"]
    for task_name, sign in bs.GOALS.items():
        task = load_task(task_name)
        y = sign * task.y
        top = y >= np.quantile(y, 0.9)
        best5 = np.argsort(-y)[:5]
        cands = bs.candidates(task_name)
        found = {}
        for arm in ("gp", "select_opus", "select_fable"):
            traces = [json.loads(f.read_text()) for f in sorted((bs.OUT / "init5_steps25" / task_name).glob(f"{arm}__seed*.json"))]
            found[arm] = float(np.mean([t["best_so_far"][-1] >= t["optimum"] - 1e-9 for t in traces]))
        for model in ("opus", "fable"):
            stats = []
            for name, m in cands[f"select_{model}"].items():
                a, b = np.polyfit(m, y, 1)
                stats.append({
                    "rho_all": spearmanr(m, y).statistic,
                    "rho_top10": spearmanr(m[top], y[top]).statistic if np.ptp(m[top]) > 0 else 0.0,
                    "optimum_pct": 100.0 * np.mean(m <= m[np.argmax(y)]),
                    "top5_recall": float(np.mean(m[best5] >= np.quantile(m, 0.9))),
                    "top_decile_bias": float(np.mean((a * m + b - y)[top]) / y.std()),
                })
            mean = {k: float(np.mean([s[k] for s in stats])) for k in stats[0]}
            rows.append({"task": task_name, "model": model, "replies": len(stats), **mean,
                         "found_gp": found["gp"], "found_prior": found[f"select_{model}"], "pool": int(len(y)),
                         "best_minus_second_sd": float((np.sort(y)[-1] - np.sort(y)[-2]) / y.std())})
            lines.append(f"| `{task_name}` | {model} | {mean['rho_all']:.2f} | {mean['rho_top10']:.2f} | {mean['optimum_pct']:.0f} | "
                         f"{mean['top5_recall']:.2f} | {mean['top_decile_bias']:+.2f} | {found['gp']:.2f} → {found[f'select_{model}']:.2f} |")
    out = HERE / "results" / "bo_failure"
    out.mkdir(parents=True, exist_ok=True)
    (out / "diagnosis.json").write_text(json.dumps(rows, indent=2) + "\n")
    (out / "diagnosis.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    for r in rows[::2]:
        print(r["task"], "pool", r["pool"], "best minus second best, in pool SDs: %.2f" % r["best_minus_second_sd"])


if __name__ == "__main__":
    main()
