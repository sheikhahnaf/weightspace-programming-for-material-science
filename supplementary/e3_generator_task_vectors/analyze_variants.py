"""E3 step C4c: compare what the variants of one generator backbone generate.

Reads supplementary/e3_generator_task_vectors/results/hprc/<variant>/scores.csv for
MatterGen, results/hprc_<backbone>/<variant>/scores.csv for the others
(one row per sampled crystal: eSEN bulk modulus and heat capacity at 300 K) and
reports, per variant:

  validity      share of samples for which each oracle returned a number
  bulk modulus  mean, median, 90th percentile, share above 200 GPa
  heat capacity mean, median, 90th percentile, share above 0.5 J/g/K
  chemistry     mean atomic mass, number of distinct reduced formulas

and against `base`: the difference of means with a bootstrap 95% interval, a
Mann-Whitney test, and, because every variant was sampled from the same noise
seed, a paired Wilcoxon test over sample indices where both gave a value.
Holm correction is applied across variants for each property. The paired test is
left out for a variant when its sampler, or the base's, returned fewer crystals than
were asked for (cf and adit only), because the sample indices then do not line up.

    python supplementary/e3_generator_task_vectors/analyze_variants.py                 # MatterGen
    python supplementary/e3_generator_task_vectors/analyze_variants.py --backbone cf   # -> variants_summary_cf.{md,json}
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np
from scipy.stats import mannwhitneyu, wilcoxon

HERE = Path(__file__).resolve().parent
PROPS = {"K_GPa": ("bulk modulus, GPa", 200.0), "Cp_J_per_gK": ("heat capacity, J/g/K", 0.5)}


def load(folder: Path) -> list[dict]:
    with (folder / "scores.csv").open() as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        row["index"] = int(row["index"])
        for key in PROPS:
            row[key] = float(row[key]) if row.get(key) not in (None, "", "nan") else float("nan")
    return rows


def mean_mass(formula: str) -> float:
    from pymatgen.core import Composition

    comp = Composition(formula)
    return float(comp.weight / comp.num_atoms)


def holm(pvalues: dict[str, float]) -> dict[str, float]:
    order = sorted(pvalues, key=pvalues.get)
    adjusted, running = {}, 0.0
    for rank, name in enumerate(order):
        running = max(running, min(1.0, (len(order) - rank) * pvalues[name]))
        adjusted[name] = running
    return adjusted


def aligned(folder: Path) -> bool:
    """False when the sampler said it returned fewer crystals than requested (see sample_and_score.py)."""
    from ase.io import read

    samples = folder / "generated_crystals.extxyz"
    return not samples.exists() or bool(read(samples, index=0).info.get("aligned", True))


def main() -> None:
    from pymatgen.core import Composition

    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--backbone", default="mg", choices=("mg", "cf", "adit"))
    args = parser.parse_args()
    suffix = "" if args.backbone == "mg" else f"_{args.backbone}"
    results = HERE / "results" / f"hprc{suffix}"
    if not results.is_dir():
        raise SystemExit(f"no results folder {results}")
    variants = {d.name: load(d) for d in sorted(results.iterdir()) if (d / "scores.csv").exists()}
    if "base" not in variants:
        raise SystemExit("no results for the base variant yet")
    paired_ok = {name: aligned(results / name) for name in variants}
    rng = np.random.default_rng(0)
    summary, tests = {}, {key: {} for key in PROPS}
    for name, rows in variants.items():
        item = {"scored": len(rows),
                "mean_atomic_mass": float(np.mean([mean_mass(r["formula"]) for r in rows])),
                "distinct_formulas": len({Composition(r["formula"]).reduced_formula for r in rows})}
        for key, (_, threshold) in PROPS.items():
            v = np.array([r[key] for r in rows])
            ok = v[np.isfinite(v)]
            item[key] = {"valid_share": float(len(ok) / len(v)) if len(v) else 0.0,
                         "mean": float(ok.mean()) if len(ok) else None,
                         "median": float(np.median(ok)) if len(ok) else None,
                         "p90": float(np.quantile(ok, 0.9)) if len(ok) else None,
                         "share_above": float((ok > threshold).mean()) if len(ok) else None}
            if name != "base" and len(ok):
                base_rows = {r["index"]: r[key] for r in variants["base"]}
                b = np.array([x for x in base_rows.values() if np.isfinite(x)])
                boot = [rng.choice(ok, len(ok)).mean() - rng.choice(b, len(b)).mean() for _ in range(4000)]
                pairs = [(r[key], base_rows[r["index"]]) for r in rows
                         if np.isfinite(r[key]) and np.isfinite(base_rows.get(r["index"], np.nan))]
                d = np.array([a - c for a, c in pairs])
                item[key] |= {
                    "mean_minus_base": float(ok.mean() - b.mean()),
                    "ci95": [float(np.quantile(boot, 0.025)), float(np.quantile(boot, 0.975))],
                    "mannwhitney_p": float(mannwhitneyu(ok, b).pvalue),
                    "paired_n": len(d),
                    "paired_wilcoxon_p": (float(wilcoxon(d).pvalue) if len(d) > 5 and np.any(d != 0)
                                          and paired_ok[name] and paired_ok["base"] else None),
                }
                tests[key][name] = item[key]["mannwhitney_p"]
        summary[name] = item
    for key in PROPS:
        for name, p in holm(tests[key]).items():
            summary[name][key]["mannwhitney_p_holm"] = p

    lines = []
    for key, (label, threshold) in PROPS.items():
        lines += [f"**{label}**", "",
                  f"| Variant | Scored | Valid | Mean | Median | 90th pct | Share > {threshold:g} | Mean − base [95% CI] | Mann-Whitney p (Holm) |",
                  "|---|---|---|---|---|---|---|---|---|"]
        for name, item in summary.items():
            p = item[key]
            if p["mean"] is None:
                lines.append(f"| `{name}` | {item['scored']} | {p['valid_share']:.2f} | | | | | | |")
                continue
            diff = ("" if name == "base" else
                    f"{p['mean_minus_base']:+.3g} [{p['ci95'][0]:+.3g}, {p['ci95'][1]:+.3g}]")
            test = "" if name == "base" else f"{p['mannwhitney_p']:.2g} ({p['mannwhitney_p_holm']:.2g})"
            lines.append(f"| `{name}` | {item['scored']} | {p['valid_share']:.2f} | {p['mean']:.3g} | {p['median']:.3g} "
                         f"| {p['p90']:.3g} | {p['share_above']:.2f} | {diff} | {test} |")
        lines.append("")
    lines += ["**chemistry**", "", "| Variant | Mean atomic mass | Distinct formulas |", "|---|---|---|"]
    lines += [f"| `{n}` | {i['mean_atomic_mass']:.1f} | {i['distinct_formulas']} |" for n, i in summary.items()]
    (HERE / "results" / f"variants_summary{suffix}.json").write_text(json.dumps(summary, indent=1) + "\n")
    (HERE / "results" / f"variants_summary{suffix}.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
