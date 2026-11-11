"""E4 step 2: do a surrogate's fitted parameters predict how well it ranks?

Joins the fitted GP parameters of the autoresearch-bo runs with each run's
per-iteration Spearman correlation, then predicts that correlation for a
benchmark the model has never seen (leave one benchmark out), from

  context     iteration, training-set size, input dimension, surrogate family
  parameters  lengthscale summary, output scale, noise, mean constant, task correlation
  both

If `both` does not beat `context`, the parameters carry nothing about quality
beyond what the run's bookkeeping already says.

    python experiments/e4_surrogate_zoo/run_zoo.py
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import r2_score

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
KEYS = ["config_id", "benchmark", "seed", "iter"]


def load() -> pd.DataFrame:
    params = pd.read_parquet(ROOT / "data/surrogate_zoo/df_hyperparams.parquet")
    large = ROOT / "data/large/surrogate_zoo/df_iter.parquet"
    if not large.exists():
        raise SystemExit("data/large is not tracked; run scripts/copy_from_siblings.py first")
    labels = pd.read_parquet(large, columns=[*KEYS, "spearman_mean", "r2_mean"])
    labels = labels.dropna(subset=["spearman_mean"]).drop_duplicates(KEYS)
    table = params.merge(labels, on=KEYS, how="inner")
    for column in ("ls_gmean", "ls_min", "ls_max", "outputscale_mean", "noise_mean"):
        table[f"log_{column}"] = np.log10(table[column].clip(lower=1e-12))
    table["log_ls_spread"] = table["log_ls_max"] - table["log_ls_min"]
    table["has_task_corr"] = table["task_corr"].notna().astype(float)
    table["task_corr"] = table["task_corr"].fillna(0.0)
    for name in sorted(table["surrogate"].unique()):
        table[f"is_{name}"] = (table["surrogate"] == name).astype(float)
    return table


def main() -> None:
    table = load()
    context = ["iter", "n_train", "ls_n", *[c for c in table.columns if c.startswith("is_")]]
    parameters = [
        "log_ls_gmean", "log_ls_min", "log_ls_max", "log_ls_spread", "log_outputscale_mean",
        "log_noise_mean", "mean_const_mean", "task_corr", "has_task_corr",
    ]
    feature_sets = {"context": context, "parameters": parameters, "both": context + parameters}
    y = table["spearman_mean"].to_numpy()

    rows = []
    for benchmark in sorted(table["benchmark"].unique()):
        held = (table["benchmark"] == benchmark).to_numpy()
        row = {"benchmark": benchmark, "n": int(held.sum())}
        baseline = np.full(held.sum(), y[~held].mean())
        row["train_mean"] = {"r2": float(r2_score(y[held], baseline)), "mae": float(np.abs(y[held] - baseline).mean())}
        for name, columns in feature_sets.items():
            X = table[columns].to_numpy(dtype=float)
            model = HistGradientBoostingRegressor(max_iter=300, learning_rate=0.05, random_state=0)
            prediction = model.fit(X[~held], y[~held]).predict(X[held])
            row[name] = {
                "r2": float(r2_score(y[held], prediction)),
                "spearman": float(spearmanr(y[held], prediction).statistic),
                "mae": float(np.abs(y[held] - prediction).mean()),
            }
        rows.append(row)
        print(
            f"{benchmark:22s} n={row['n']:5d}  rho: context {row['context']['spearman']:+.2f}  "
            f"parameters {row['parameters']['spearman']:+.2f}  both {row['both']['spearman']:+.2f}   "
            f"MAE: mean {row['train_mean']['mae']:.3f} context {row['context']['mae']:.3f} both {row['both']['mae']:.3f}",
            flush=True,
        )

    def average(name: str, metric: str) -> float:
        return float(np.nanmean([r[name][metric] for r in rows]))

    summary = {
        "rows": int(len(table)),
        "benchmarks": len(rows),
        "surrogates": sorted(table["surrogate"].unique()),
        "target": "spearman_mean of the surrogate at that iteration",
        "mean_over_benchmarks": {
            name: {m: average(name, m) for m in ("r2", "spearman", "mae")} for name in feature_sets
        } | {"train_mean": {m: average("train_mean", m) for m in ("r2", "mae")}},
        "benchmarks_where_both_beats_context_on_mae": int(sum(r["both"]["mae"] < r["context"]["mae"] for r in rows)),
        "benchmarks_where_both_beats_context_on_spearman": int(
            sum(r["both"]["spearman"] > r["context"]["spearman"] for r in rows)
        ),
        "per_benchmark": rows,
    }
    out = HERE / "results"
    out.mkdir(exist_ok=True)
    (out / "zoo_leave_one_benchmark_out.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({k: v for k, v in summary.items() if k != "per_benchmark"}, indent=2))


if __name__ == "__main__":
    main()
