"""E1 baselines: what a weight-space-programmed head has to beat, on every task.

For each task and seed this fits an exact GP, ridge regression and the MLP head
trained with AdamW, scores them on the task's test rows, and saves the trained
head as text so the same weights can be handed to an LLM.

    python experiments/e1_surrogate_head/run_baseline.py                 # all E1 tasks
    python experiments/e1_surrogate_head/run_baseline.py --task calphad --out experiments/e7_calphad_prior/results/baseline
    python experiments/e1_surrogate_head/run_baseline.py --task ti_alloy_youngs_modulus
"""

from __future__ import annotations

import argparse
import json
import warnings
from pathlib import Path

import numpy as np

from wsp import count_weights, dump_weights, estimate_tokens
from wsp.baselines import fit_gp, fit_mlp, fit_ridge, predict, prepare, score
from wsp.tasks import CALPHAD_TASK_NAMES, TASK_NAMES, load_task

HERE = Path(__file__).resolve().parent
METRICS = ("r2", "spearman", "rmse", "top_decile_bias")


def run_task(name: str, seeds: int, hidden: tuple[int, ...], out: Path) -> dict:
    task = load_task(name)
    folder = out / name
    folder.mkdir(parents=True, exist_ok=True)
    per_seed = []
    for seed in range(seeds):
        data = prepare(task, seed)
        gp_mean, gp_std = fit_gp(data)
        head = fit_mlp(data, hidden, seed)
        text = dump_weights(head.state_dict())
        (folder / f"mlp_head_seed{seed}.txt").write_text(text)
        per_seed.append(
            {
                "seed": seed,
                "n_train": len(data.y_train),
                "n_test": len(data.y_test),
                "gp": score(data.y_test, gp_mean, gp_std),
                "ridge": score(data.y_test, fit_ridge(data)),
                "mlp": score(data.y_test, predict(head, data.U_test)),
                "train_mean": score(data.y_test, np.full_like(data.y_test, data.y_mean)),
            }
        )

    def aggregate(model: str, metric: str) -> dict[str, float]:
        values = [row[model][metric] for row in per_seed]
        return {"mean": float(np.nanmean(values)), "std": float(np.nanstd(values))}

    summary = {
        "task": name,
        "application": task.application,
        "target": f"{task.target} ({task.unit})",
        "split": task.split_kind,
        "features": len(task.feature_names),
        "named_features": task.named_features,
        "seeds": seeds,
        "head": {
            "hidden": list(hidden),
            "weights": count_weights(head.state_dict()),
            "text_chars": len(text),
            "tokens_estimate": estimate_tokens(text),
        },
        "gp": {m: aggregate("gp", m) for m in (*METRICS, "coverage95")},
        "ridge": {m: aggregate("ridge", m) for m in METRICS},
        "mlp": {m: aggregate("mlp", m) for m in METRICS},
        "per_seed": per_seed,
    }
    (folder / "baseline.json").write_text(json.dumps(summary, indent=2) + "\n")
    return summary


def table(summaries: list[dict]) -> str:
    def cell(s: dict, model: str, metric: str, digits: int = 2) -> str:
        v = s[model][metric]
        return f"{v['mean']:.{digits}f} ± {v['std']:.{digits}f}"

    lines = [
        "| Task | Train / test | Head weights | GP R² | GP ρ | GP 95% coverage | GP top-decile bias | Ridge R² | MLP R² | MLP ρ | MLP top-decile bias |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for s in summaries:
        first = s["per_seed"][0]
        lines.append(
            f"| `{s['task']}` | {first['n_train']} / {first['n_test']} | {s['head']['weights']:,} "
            f"| {cell(s, 'gp', 'r2')} | {cell(s, 'gp', 'spearman')} | {cell(s, 'gp', 'coverage95')} "
            f"| {cell(s, 'gp', 'top_decile_bias', 3)} | {cell(s, 'ridge', 'r2')} "
            f"| {cell(s, 'mlp', 'r2')} | {cell(s, 'mlp', 'spearman')} | {cell(s, 'mlp', 'top_decile_bias', 3)} |"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--task", choices=(*TASK_NAMES, "all", "calphad"), default="all",
                        help="all = the E1 tasks; calphad = the Thermo-Calc tasks of E7")
    parser.add_argument("--seeds", type=int, default=5)
    parser.add_argument("--hidden", type=int, nargs="+", default=[32, 32])
    parser.add_argument("--out", type=Path, default=HERE / "results")
    args = parser.parse_args()

    warnings.filterwarnings("ignore")
    groups = {"all": tuple(n for n in TASK_NAMES if n not in CALPHAD_TASK_NAMES), "calphad": CALPHAD_TASK_NAMES}
    names = groups.get(args.task, (args.task,))
    summaries = []
    for name in names:
        summaries.append(run_task(name, args.seeds, tuple(args.hidden), args.out))
        print(f"done {name}", flush=True)
    text = table(summaries)
    if args.task in groups:
        (args.out / "baseline_table.md").write_text(text)
    print(text)


if __name__ == "__main__":
    main()
