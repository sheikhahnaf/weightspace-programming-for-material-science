"""E7: how good are the two no-LLM references that get the phase-diagram facts?

  rom                   rule of mixtures of the pure-element values
  binary_extrapolation  rule of mixtures plus pairwise terms read off the binaries at 50 at.%

Each is scored alone (Spearman and Pearson correlation with the target over the
whole pool) and as the prior mean of a GP given 5, 10, 20 or 50 labels, exactly
as a written network is scored (`wsp.arms.score_prior`, five seeds).

    python experiments/e7_calphad_prior/run_references.py
    # -> results/references/summary.json, summary.md
"""

from __future__ import annotations

import json
import warnings
from pathlib import Path

import numpy as np
from scipy.stats import pearsonr, spearmanr

from wsp.arms import reference_priors, score_prior
from wsp.tasks import CALPHAD_TASK_NAMES, load_task

OUT = Path(__file__).resolve().parent / "results" / "references"
SIZES = ("n5", "n10", "n20", "n50")


def main() -> None:
    warnings.filterwarnings("ignore")
    OUT.mkdir(parents=True, exist_ok=True)
    summary, lines = {}, [
        "| Task | Reference | Alone: Spearman ρ (Pearson r), whole pool | ρ at 5 labels: GP → + prior (fitted / one) | at 10 | at 20 | at 50 |",
        "|---|---|---|---|---|---|---|",
    ]
    for task_name in CALPHAD_TASK_NAMES:
        task = load_task(task_name)
        summary[task_name] = {"pool": len(task.y), "unit": task.unit}
        for name, prior in reference_priors(task).items():
            m = prior(task.X)
            constant = bool(np.ptp(m) == 0)
            rows = score_prior(task, prior)
            item = {
                "constant": constant,
                "spearman": None if constant else float(spearmanr(m, task.y).statistic),
                "pearson": None if constant else float(pearsonr(m, task.y).statistic),
                "rmse_alone": float(np.sqrt(np.mean((m - task.y) ** 2))),
            }
            cells = []
            for n in SIZES:
                item[n] = {key: float(np.mean([row[n][key]["spearman"] for row in rows]))
                           for key in ("gp", "gp_with_prior_fitted", "gp_with_prior_one")}
                item[n] |= {f"{key}_r2": float(np.mean([row[n][key]["r2"] for row in rows]))
                            for key in ("gp", "gp_with_prior_fitted", "gp_with_prior_one")}
                cells.append(f"{item[n]['gp']:.2f} → {item[n]['gp_with_prior_fitted']:.2f} / {item[n]['gp_with_prior_one']:.2f}")
            summary[task_name][name] = item
            alone = "constant" if constant else f"{item['spearman']:.2f} ({item['pearson']:.2f})"
            lines.append(f"| `{task_name}` | {name} | {alone} | " + " | ".join(cells) + " |")
            print(lines[-1], flush=True)
    (OUT / "summary.json").write_text(json.dumps(summary, indent=1) + "\n")
    (OUT / "summary.md").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
