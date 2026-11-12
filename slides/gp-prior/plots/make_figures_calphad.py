"""Draw the Thermo-Calc figures of the deck from the project's result files (read-only).

    eval "$(/Users/alvi/miniconda3/bin/conda shell.zsh hook)" && conda activate matinvent
    PYTHONDONTWRITEBYTECODE=1 python plots/make_figures_calphad.py

Sources, all under the repository root:
  experiments/e1_surrogate_head/results/standalone/summary.json          networks alone, no labels
  experiments/e7_calphad_prior/results/static/summary.json                GP ranking and coverage by labels
  experiments/e7_calphad_prior/results/bo/summary_init5_steps25_seeds20.json   BO regret areas and tests
  ../weightspace-programming-for-material-science-paper/figures/supp_net_<task>.pdf   network diagrams (rasterized)
Writes PNG files into figures/ and the numbers printed on the slides into plots/figure_numbers_calphad.json.
"""
import json
import subprocess
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
FIG = HERE.parent / "figures"
PAPER_FIG = ROOT.parent / "weightspace-programming-for-material-science-paper/figures"

plt.rcParams.update({
    "font.family": "Helvetica", "font.size": 10, "axes.labelsize": 10.5, "axes.titlesize": 10.5,
    "xtick.labelsize": 9.5, "ytick.labelsize": 9.5, "legend.fontsize": 9, "axes.spines.top": False,
    "axes.spines.right": False, "axes.linewidth": 0.8, "savefig.dpi": 300, "figure.dpi": 100,
    "legend.frameon": False, "axes.titleweight": "bold", "hatch.linewidth": 0.8,
})

SYSTEMS = {"cantor_al": "Al-Co-Cr-Fe-Mn-Ni", "refractory": "Mo-Nb-Ta-Ti-V-W-Zr", "hf_refractory": "Hf-Mo-Nb-Ta-Ti-Zr",
           "al_refractory": "Al-Cr-Mo-Nb-Ti", "cu_ti_3d": "Co-Cr-Cu-Fe-Ni-Ti", "ni_superalloy": "Ni superalloys",
           "ti_alloy": "Ti alloys", "steel": "Steels", "al_alloy": "Al alloys"}
MEASURED = {"ti_alloy_youngs_modulus", "ti_alloy_yield_strength", "ti_alloy_hardness"}
KINDS = ["solidus", "freezing range", "phase fraction", "transus"]
MAROON, NAVY, GREY = "#500000", "#1F3A5F", "#8A8F98"
# key in standalone summary, key in the static and BO summaries, label, colour, uses the facts, marker
SOURCES = [("subsystem_extrapolation", "subsystem_extrapolation", "Sub-system extrapolation (no LLM)", GREY, False, "s"),
           ("opus", "select_opus", "Opus 5.5", MAROON, False, "o"),
           ("opus + facts", "select_opus_pd", "Opus 5.5 + facts", MAROON, True, "D"),
           ("fable", "select_fable", "Fable 5.2", NAVY, False, "^"),
           ("fable + facts", "select_fable_pd", "Fable 5.2 + facts", NAVY, True, "v")]
NUM = {}


def save(fig, name):
    fig.savefig(FIG / name, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("wrote", name)


def system_of(name):
    if name in MEASURED:
        return None
    for s in sorted(SYSTEMS, key=len, reverse=True):
        if name.startswith(s + "_"):
            return s
    return None


def kind_of(name):
    return "phase fraction" if "fraction" in name else "freezing range" if "freezing" in name else "transus" if "transus" in name else "solidus"


def target_label(name):
    t = name[len(system_of(name)) + 1:].replace("_", " ")
    return t.replace("gamma prime", "γ′").replace("alpha", "α").replace("carbide intermetallic", "carbide + intermetallic")


ALONE = json.loads((ROOT / "experiments/e1_surrogate_head/results/standalone/summary.json").read_text())
STATIC = json.loads((ROOT / "experiments/e7_calphad_prior/results/static/summary.json").read_text())
BO = json.loads((ROOT / "experiments/e7_calphad_prior/results/bo/summary_init5_steps25_seeds20.json").read_text())


# ---------------------------------------------------------------- 1. networks alone, by kind of target
def fig_alone():
    targets = sorted({k.split("|")[0] for k in ALONE if system_of(k.split("|")[0])})
    assert len(targets) == 35
    by_kind = {k: [t for t in targets if kind_of(t) == k] for k in KINDS}
    fig, ax = plt.subplots(figsize=(6.6, 4.1))
    wd = 0.165
    x = np.arange(len(KINDS))
    NUM["alone"] = {"targets": len(targets), "per_kind": {k: len(v) for k, v in by_kind.items()}}
    for i, (key, _, label, col, facts, _) in enumerate(SOURCES):
        vals = [np.array([ALONE[f"{t}|{key}"]["rho"] for t in ts]) for ts in by_kind.values()]
        means = [float(v.mean()) for v in vals]
        NUM["alone"][key] = {"all": round(float(np.mean([ALONE[f"{t}|{key}"]["rho"] for t in targets])), 2),
                             **{k: round(m, 2) for k, m in zip(by_kind, means)}}
        pos = x + (i - 2) * wd
        ax.bar(pos, means, wd, color=col, alpha=0.55 if facts else 1.0, hatch="////" if facts else None,
               edgecolor="white", lw=0.4, label=label, zorder=2)
        for p, v, m in zip(pos, vals, means):
            if len(v) > 1:
                ax.scatter(p + np.linspace(-0.3, 0.3, len(v)) * wd, v, s=7, color="white", edgecolor="#111", lw=0.5, zorder=3)
            ax.text(p, 1.03, f"{m:.2f}", ha="center", va="bottom", rotation=90, fontsize=8.5, color=col, zorder=4)
    ax.set_xticks(x, [f"Solidus ({len(by_kind['solidus'])} targets)", f"Freezing range ({len(by_kind['freezing range'])})",
                      f"Phase fraction ({len(by_kind['phase fraction'])})", f"Ti α transus ({len(by_kind['transus'])})"])
    ax.set_ylabel("Spearman ρ of the predictor alone, no labels")
    ax.set_ylim(0, 1.48)
    ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
    h, l = ax.get_legend_handles_labels()
    h.append(Line2D([], [], marker="o", ls="", ms=3.5, mfc="white", mec="#111", mew=0.5))
    l.append("One target")
    ax.legend(h, l, ncol=3, loc="upper center", fontsize=8.5, columnspacing=1.0, handlelength=1.3, handletextpad=0.4,
              title="Bar: mean over the targets of a kind (number above the bar)", title_fontsize=8.5)
    ax.grid(axis="y", color="#E5E5E5", lw=0.6)
    ax.set_axisbelow(True)
    save(fig, "tc_rho_alone_by_kind.png")


# ---------------------------------------------------------------- 2. GP ranking by labels (a, b integrated out)
def static_mean(key, arm, metric):
    tasks = STATIC["tasks"]
    if key == "gp":
        rows = [next(iter(t.values()))["gp"][metric] for t in tasks.values()]
    else:
        rows = [t[key][arm][metric] for t in tasks.values()]
    return [float(np.nanmean([r[i] for r in rows])) for i in range(len(STATIC["sizes"]))]


def fig_labels():
    sizes = STATIC["sizes"]
    assert sizes == [5, 10, 20, 50] and len(STATIC["tasks"]) == 35
    fig, ax = plt.subplots(figsize=(6.4, 4.1))
    gp = static_mean("gp", None, "spearman")
    NUM["labels"] = {"gp": [round(v, 2) for v in gp]}
    ax.plot(range(4), gp, "o--", color="#111", lw=1.8, ms=5.5, label="Plain GP")
    for key, skey, label, col, facts, mk in SOURCES:
        y = static_mean(skey, "marginal", "spearman")
        NUM["labels"][key] = [round(v, 2) for v in y]
        ax.plot(range(4), y, marker=mk, ls=":" if facts else "-", color=col, lw=1.8, ms=5.5,
                mfc="white" if facts else col, mec=col, mew=1.2, label="GP + " + label)
    ax.set_xticks(range(4), [str(n) for n in sizes])
    ax.set_xlabel("Labelled alloys given to the GP")
    ax.set_ylabel("Spearman ρ on the held-out half, mean of 35 targets")
    ax.set_ylim(0.3, 0.9)
    ax.legend(loc="lower right", fontsize=9, title="Mean a·m(x) + b; a and b integrated out", title_fontsize=9,
              frameon=True, facecolor="white", edgecolor="none", framealpha=1.0)
    ax.grid(axis="y", color="#E5E5E5", lw=0.6)
    save(fig, "tc_rho_vs_labels.png")


# ---------------------------------------------------------------- 3. 95% coverage at 5 labels, three fits of a and b
def fig_coverage():
    fits = [("two_stage", "Two-stage: a, b by least squares, then the GP", "#C47F17"),
            ("map", "Joint: a, b learned with the kernel", "#2A8C8C"),
            ("marginal", "Joint: a, b integrated out", "#1F3A5F")]
    fig, ax = plt.subplots(figsize=(6.6, 4.1))
    wd = 0.25
    gp = static_mean("gp", None, "coverage95")[0]
    NUM["coverage5"] = {"gp": round(gp, 2)}
    for k, (arm, lab, col) in enumerate(fits):
        y = [static_mean(skey, arm, "coverage95")[0] for _, skey, *_ in SOURCES]
        NUM["coverage5"][arm] = [round(v, 2) for v in y]
        x = np.arange(len(SOURCES)) + (k - 1) * wd
        ax.bar(x, y, wd, color=col, edgecolor="white", lw=0.4, label=lab, zorder=2)
        for xi, yi in zip(x, y):
            ax.text(xi, yi - 0.012, f"{yi:.2f}", ha="center", va="top", fontsize=8.5, color="white")
    ax.axhline(gp, color="#111", ls="--", lw=1.2, label=f"Plain GP: {gp:.2f}", zorder=1)
    ax.axhline(0.95, color="#111", ls=":", lw=1.2, label="Nominal: 0.95", zorder=1)
    ax.set_xticks(range(len(SOURCES)), ["Sub-system\nextrapolation", "Opus 5.5", "Opus 5.5\n+ facts", "Fable 5.2", "Fable 5.2\n+ facts"])
    ax.set_ylabel("Share of held-out values inside the 95% interval")
    ax.set_ylim(0, 1.3)
    ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
    ax.legend(ncol=2, loc="upper center", fontsize=8.5, columnspacing=1.0, handlelength=1.6,
              title="5 labels; mean of 35 targets", title_fontsize=8.5)
    ax.grid(axis="y", color="#E5E5E5", lw=0.6)
    ax.set_axisbelow(True)
    save(fig, "tc_coverage_5_labels.png")


# ---------------------------------------------------------------- 4. BO: regret area relative to the plain GP
def fig_bo(kinds, name, tag, floor=0.01):
    plotted = [n for n, t in BO["tasks"].items() if t["gp"]["auc_mean"] > 1e-12]
    assert len(plotted) == 33
    rows = [(k, s, n) for k in kinds for s in SYSTEMS for n in plotted if system_of(n) == s and kind_of(n) == k]
    one_kind_per_group = all(k in ("solidus", "freezing range") for k in kinds)
    fig, ax = plt.subplots(figsize=(6.6, 4.35))
    y, ticks, labels, wins, losses = 0, [], [], {s[0]: 0 for s in SOURCES}, {s[0]: [] for s in SOURCES}
    last = None
    for k, s, n in rows:
        group = k if one_kind_per_group else s
        if group != last:
            if last is not None:
                ax.axhline(y - 0.5, color="#999", lw=0.6)
                y += 0.0
            last = group
        t = BO["tasks"][n]
        g = t["gp"]["auc_mean"]
        ax.plot([floor * 0.8, 10], [y, y], color="#E2E2E2", lw=0.5, zorder=1)
        for key, bkey, _, col, facts, mk in SOURCES:
            r, pv = t[bkey]["auc_mean"] / g, t[bkey]["wilcoxon_p_holm"]
            sig = pv is not None and pv < 0.05
            if sig and r < 1:
                wins[key] += 1
            if sig and r > 1:
                losses[key].append((n, round(r, 2)))
            ax.scatter(max(r, floor), y, marker=mk, s=34, facecolor=col if sig else "white", edgecolor=col, lw=1.1,
                       zorder=4 if sig else 3, clip_on=False)
        ticks.append(y)
        labels.append(SYSTEMS[s] if one_kind_per_group else f"{SYSTEMS[s]}: {target_label(n)}")
        y += 1
    NUM[tag] = {"rows": len(rows), "wins": wins, "losses": losses}
    if one_kind_per_group:
        n0 = sum(1 for r in rows if r[0] == kinds[0])
        for txt, yy in ((kinds[0].capitalize(), (n0 - 1) / 2), (kinds[1].capitalize(), n0 + (len(rows) - n0 - 1) / 2)):
            ax.text(1.02, yy, txt, transform=ax.get_yaxis_transform(), rotation=270, ha="left", va="center", fontsize=10,
                    fontweight="bold")
    ax.axvline(1, color="#111", lw=1.1, zorder=2)
    ax.set_xscale("log")
    ax.set_xlim(floor * 0.8, 5)
    ax.set_xticks([floor, 0.1, 1], [f"≤ {floor:g}", "0.1", "1"])
    ax.set_ylim(y - 0.4, -0.6)
    ax.set_yticks(ticks, labels, fontsize=9)
    ax.tick_params(axis="y", length=0)
    ax.set_xlabel("Area under the regret curve ÷ plain GP's (left of 1 is better)")
    hs = [Line2D([], [], marker=mk, ls="", ms=6, mfc=col, mec=col, label=lab) for _, _, lab, col, _, mk in SOURCES]
    hs += [Line2D([], [], marker="o", ls="", ms=6, mfc="#555", mec="#555", label="Filled: Holm-corrected p < 0.05"),
           Line2D([], [], marker="o", ls="", ms=6, mfc="white", mec="#555", label="Open: not significant")]
    fig.legend(handles=hs, ncol=3, loc="lower center", bbox_to_anchor=(0.5, 0.94), fontsize=8.5, columnspacing=1.0,
               handletextpad=0.3)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    save(fig, name)


def bo_summary():
    plotted = [n for n, t in BO["tasks"].items() if t["gp"]["auc_mean"] > 1e-12]
    out = {"targets": len(plotted), "left_out": [n for n in BO["tasks"] if n not in plotted]}
    for key, bkey, *_ in SOURCES:
        rel = [BO["tasks"][n][bkey]["auc_mean"] / BO["tasks"][n]["gp"]["auc_mean"] for n in plotted]
        sig = [(BO["tasks"][n][bkey]["wilcoxon_p_holm"] or 1) < 0.05 for n in plotted]
        out[key] = {"better": sum(s and r < 1 for s, r in zip(sig, rel)), "worse": sum(s and r > 1 for s, r in zip(sig, rel)),
                    "median_relative_area": round(float(np.median(rel)), 2)}
        out[key]["no_difference"] = len(plotted) - out[key]["better"] - out[key]["worse"]
    NUM["bo_summary"] = out


# ---------------------------------------------------------------- 5. network diagrams drawn from the written weights
def network_diagrams():
    for task in ("ni_superalloy_solidus", "steel_austenite_fraction"):
        subprocess.run(["pdftoppm", "-r", "300", "-png", "-singlefile", str(PAPER_FIG / f"supp_net_{task}.pdf"),
                        str(FIG / f"tc_net_{task}")], check=True)
        print("wrote", f"tc_net_{task}.png")


if __name__ == "__main__":
    fig_alone()
    fig_labels()
    fig_coverage()
    fig_bo(["solidus", "freezing range"], "tc_bo_solidus_freezing_range.png", "bo_solidus_freezing")
    fig_bo(["phase fraction", "transus"], "tc_bo_phase_fractions.png", "bo_phase_fractions")
    bo_summary()
    network_diagrams()
    (HERE / "figure_numbers_calphad.json").write_text(json.dumps(NUM, indent=1, ensure_ascii=False) + "\n")
    print(json.dumps(NUM, ensure_ascii=False))
