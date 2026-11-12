"""E7: one table over all Thermo-Calc targets, from the cached summaries of run_priors.py.

    python experiments/e7_calphad_prior/summarise.py

Writes results/overview.md: (1) ranking with 5 to 50 labels, mean over targets;
(2) BO area under the regret curve relative to the plain GP, target by target, with the
Holm-corrected Wilcoxon test of run_priors.py; (3) the count of targets where an arm is
significantly better or worse. Targets whose plain-GP regret is zero are listed and left out.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

R = Path(__file__).resolve().parent / "results"
SOURCES = {"subsystem_extrapolation": "Sub-system extrapolation (no LLM)", "select_opus": "Opus 5.5",
           "select_opus_pd": "Opus 5.5 + facts", "select_fable": "Fable 5.2", "select_fable_pd": "Fable 5.2 + facts"}
ARMS = {"": "two-stage", "_map": "learned a, b", "_marginal": "a, b integrated out"}


def main() -> None:
    bo = json.loads((R / "bo" / "summary_init5_steps25_seeds20.json").read_text())
    st = json.loads((R / "static" / "summary.json").read_text())
    tasks, sizes = st["tasks"], st["sizes"]
    lines = [f"# Thermo-Calc targets: overview ({len(tasks)} targets)", "",
             "## Ranking on the held-out half, mean Spearman ρ over targets", "",
             "| Prior | Mean arm | Prior alone | " + " | ".join(f"{n} labels" for n in sizes) + " | 95% coverage at 5 / 10 |",
             "|---|---|---|" + "---|" * (len(sizes) + 1)]
    gp = [float(np.mean([next(iter(t.values()))["gp"]["spearman"][i] for t in tasks.values()])) for i in range(len(sizes))]
    gp_cov = [float(np.mean([next(iter(t.values()))["gp"]["coverage95"][i] for t in tasks.values()])) for i in (0, 1)]
    lines.append("| none | plain GP | | " + " | ".join(f"{v:.2f}" for v in gp) + f" | {gp_cov[0]:.2f} / {gp_cov[1]:.2f} |")
    for key, label in SOURCES.items():
        have = [t[key] for t in tasks.values() if key in t]
        alone = float(np.mean([h["alone_spearman"] for h in have]))
        for arm, arm_label in (("two_stage", "two-stage"), ("map", "learned a, b"), ("marginal", "a, b integrated out")):
            rho = [float(np.mean([h[arm]["spearman"][i] for h in have])) for i in range(len(sizes))]
            cov = [float(np.mean([h[arm]["coverage95"][i] for h in have])) for i in (0, 1)]
            lines.append(f"| {label} | {arm_label} | {alone:.2f} | " + " | ".join(f"{v:.2f}" for v in rho) + f" | {cov[0]:.2f} / {cov[1]:.2f} |")
    lines += ["", f"## BO: area under the regret curve relative to the plain GP ({bo['seeds']} seeds, {bo['n_init']} initial labels, {bo['steps']} steps; two-stage arm)",
              "", "Below 1 is better than the plain GP. * marks Holm-corrected p < 0.05 within the target.", "",
              "| Target | Plain GP, absolute | Random | " + " | ".join(SOURCES.values()) + " |", "|---|---|---|" + "---|" * len(SOURCES)]
    left_out, count = [], {}
    rel: dict[str, list[float]] = {}
    for name, t in bo["tasks"].items():
        g = t["gp"]["auc_mean"]
        if g <= 1e-12:
            left_out.append(name)
            continue
        cells = []
        for key in SOURCES:
            for suffix in ARMS:
                arm = key + suffix
                if arm not in t:
                    continue
                r, p = t[arm]["auc_mean"] / g, t[arm]["wilcoxon_p_holm"]
                sig = p is not None and p < 0.05
                rel.setdefault(arm, []).append(r)
                c = count.setdefault(arm, [0, 0, 0])
                c[0 if sig and r < 1 else 1 if sig else 2] += 1
                if not suffix:
                    cells.append(f"{r:.2f}{'*' if sig else ''}")
        lines.append(f"| `{name}` | {g:.3g} | {t['random']['auc_mean'] / g:.2f} | " + " | ".join(cells) + " |")
    lines += ["", f"Left out, plain-GP regret is zero: {', '.join(left_out) or 'none'}.", "",
              "## BO: targets where an arm is significantly better / worse / not different from the plain GP", "",
              "| Prior | " + " | ".join(ARMS.values()) + " | Median relative area (two-stage) |", "|---|" + "---|" * (len(ARMS) + 1)]
    for key, label in SOURCES.items():
        lines.append(f"| {label} | " + " | ".join("{} / {} / {}".format(*count[key + s]) for s in ARMS) + f" | {np.median(rel[key]):.2f} |")
    (R / "overview.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
