"""Draw the structure-embedding figures of the deck from the project's result files (read-only).

    eval "$(/Users/alvi/miniconda3/bin/conda shell.zsh hook)" && conda activate matinvent
    PYTHONDONTWRITEBYTECODE=1 python plots/make_figures_structure.py

Sources, all under the repository root:
  experiments/e1_surrogate_head/results/structure_prior/summary.json            embedding GP with a written prior mean
  experiments/e1_surrogate_head/results/structure_prior/features/summary.json   written hidden layer as GP inputs
  experiments/e3_crystal_filter/results/filter_arm{,_cf}/per_run.json           screening filter on generator samples
  ../weightspace-programming-for-material-science-paper/figures/supp_net_filter_K.pdf   network diagram (rasterized)
Writes PNG files into figures/ and the numbers printed on the slides into plots/figure_numbers_structure.json.
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
    "legend.frameon": False, "axes.titleweight": "bold",
})
MAROON, NAVY, TEAL, AMBER, PURPLE, GREY = "#500000", "#1F3A5F", "#2A8C8C", "#C47F17", "#6B4C9A", "#8A8F98"
NUM = {}

PRIOR = json.loads((ROOT / "experiments/e1_surrogate_head/results/structure_prior/summary.json").read_text())
FEAT = json.loads((ROOT / "experiments/e1_surrogate_head/results/structure_prior/features/summary.json").read_text())


def save(fig, name):
    fig.savefig(FIG / name, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("wrote", name)


def cell(task, n, arm, prior=""):
    """One row of the summary: the prior key carries the number of replies, e.g. 'opus (3)'."""
    keys = [k for k in PRIOR if k.startswith(f"{task}|n{n}|{arm}|") and k.split("|")[3].split(" (")[0] == prior]
    assert len(keys) == 1, (task, n, arm, prior, keys)
    return PRIOR[keys[0]]


# ---------------------------------------------------------------- 1. embedding GP with and without a written mean
def fig_labels(task, name, tag, rule_label, ylim, legend_loc):
    sizes = ["5", "10", "20", "50"]
    lines = [("gp", "", "Plain GP on the embedding", "#111", "o", "--"),
             ("gp_desc", "", "GP on embedding + 15 raw descriptors", PURPLE, "P", "-."),
             ("two_stage", "rule", f"GP + {rule_label} (no LLM)", GREY, "s", "-"),
             ("map", "opus", "GP + Opus 5.5 network", MAROON, "o", "-"),
             ("map", "fable", "GP + Fable 5.2 network", NAVY, "^", "-")]
    fig, ax = plt.subplots(figsize=(6.4, 4.1))
    NUM[tag] = {"alone": {k: round(v, 2) for k, v in PRIOR[f"{task}|alone"].items()}}
    for arm, prior, label, col, mk, ls in lines:
        y = [cell(task, n, arm, prior)["spearman"] for n in sizes]
        NUM[tag][f"{arm}|{prior}"] = {"rho": [round(v, 2) for v in y],
                                      "coverage95_n5": round(cell(task, "5", arm, prior)["coverage95"], 2)}
        ax.plot(range(4), y, marker=mk, ls=ls, color=col, lw=1.8, ms=5.5, label=label)
    for prior in ("opus", "fable", "rule"):
        for arm in ("two_stage", "map", "marginal"):
            NUM[tag].setdefault("coverage95_n5", {})[f"{arm}|{prior}"] = round(cell(task, "5", arm, prior)["coverage95"], 2)
    for prior in ("opus", "fable"):
        NUM[tag].setdefault("vs_gp", {})[prior] = {n: cell(task, n, "map", prior)["vs_gp"] for n in sizes}
    ax.set_xticks(range(4), sizes)
    ax.set_xlabel("Labelled crystals given to the GP")
    ax.set_ylabel("Spearman ρ on the generated crystals")
    ax.set_ylim(*ylim)
    ax.legend(loc=legend_loc, fontsize=9, title="Written mean: a, b learned with the kernel; rule: two-stage fit",
              title_fontsize=8.5, frameon=True, facecolor="white", edgecolor="none", framealpha=1.0)
    ax.grid(axis="y", color="#E5E5E5", lw=0.6)
    save(fig, name)


# ---------------------------------------------------------------- 2. the written hidden layer as GP inputs
def fig_hidden():
    task = "loop_bulk_modulus"
    sizes = [5, 10, 20, 50, 500]
    gp = [cell(task, n, "gp")["spearman"] for n in ("5", "10", "20", "50", "all (500)")]
    arms = [("hidden", "GP on the 16 hidden units", TEAL, "D", "-"),
            ("hidden+prior", "Hidden units + written mean", MAROON, "o", "-"),
            ("emb+hidden+prior", "Embedding + hidden units + written mean", NAVY, "^", "-")]
    fig, ax = plt.subplots(figsize=(6.4, 4.1))
    NUM["hidden"] = {"embedding": [round(v, 2) for v in gp]}
    ax.plot(range(5), gp, "o--", color="#111", lw=1.8, ms=5.5, label="Plain GP on the 50 embedding coordinates")
    for arm, label, col, mk, ls in arms:
        y = [float(np.mean([FEAT[f"{task}|n{n}|{m}|{arm}"]["spearman"] for m in ("opus", "fable")])) for n in sizes]
        NUM["hidden"][arm] = [round(v, 2) for v in y]
        ax.plot(range(5), y, marker=mk, ls=ls, color=col, lw=1.8, ms=5.5, label=label)
    NUM["hidden"]["emb+hidden"] = [round(float(np.mean([FEAT[f"{task}|n{n}|{m}|emb+hidden"]["spearman"] for m in ("opus", "fable")])), 2)
                                   for n in sizes]
    ax.set_xticks(range(5), ["5", "10", "20", "50", "500 (whole pool)"])
    ax.set_xlabel("Labelled crystals given to the GP")
    ax.set_ylabel("Spearman ρ on the generated crystals")
    ax.set_ylim(0.1, 1.0)
    ax.legend(loc="lower right", fontsize=9, title="Bulk modulus; mean over Opus 5.5 and Fable 5.2 networks", title_fontsize=8.5,
              frameon=True, facecolor="white", edgecolor="none", framealpha=1.0)
    ax.grid(axis="y", color="#E5E5E5", lw=0.6)
    save(fig, "st_hidden_units_as_inputs.png")


# ---------------------------------------------------------------- 3. screening filter in front of two generators
def fig_filter():
    gens = [("MatterGen", "filter_arm"), ("CrystalFlow", "filter_arm_cf")]
    scorers = [("rule", "Volume rule (no LLM)", GREY), ("MLP trained", "MLP trained on 400 labels", PURPLE),
               ("claude-opus", "Opus 5.5", MAROON), ("claude-fable", "Fable 5.2", NAVY),
               ("claude-sonnet", "Sonnet 5.5", TEAL), ("claude-haiku", "Haiku 5.5", AMBER)]
    data = [[r for r in json.loads((ROOT / f"experiments/e3_crystal_filter/results/{folder}/per_run.json").read_text())
             if r["target"] == "K" and "invalid" not in r] for _, folder in gens]
    share_all = []
    for runs in data:
        a = {r["base_128"]["share_above_all"] for r in runs}
        assert len(a) == 1
        share_all.append(a.pop())
    fig, axes = plt.subplots(1, 2, figsize=(6.9, 3.9))
    wd = 0.135
    x = np.arange(len(gens))
    NUM["filter"] = {"share_all": [round(v, 2) for v in share_all]}
    for i, (prefix, label, col) in enumerate(scorers):
        pos = x + (i - 2.5) * wd
        for ax, field in ((axes[0], "spearman"), (axes[1], "share_above_kept")):
            vals = [np.array([r["base_128"][field] for r in runs if r["arm"].startswith(prefix)]) for runs in data]
            assert all(len(v) for v in vals), prefix
            means = [float(v.mean()) for v in vals]
            NUM["filter"].setdefault(field, {})[label] = [round(m, 2) for m in means]
            ax.bar(pos, means, wd, color=col, edgecolor="white", lw=0.4, label=label, zorder=2)
            for p, m in zip(pos, means):
                ax.text(p, m + 0.012, f"{m:.2f}", ha="center", va="bottom", rotation=90, fontsize=8)
    for p, v in zip(x, share_all):
        axes[1].plot([p - 3.3 * wd, p + 3.3 * wd], [v, v], color="#111", ls="--", lw=1.2, zorder=4)
    for ax in axes:
        ax.set_xticks(x, [g for g, _ in gens])
        ax.grid(axis="y", color="#E5E5E5", lw=0.6)
        ax.set_axisbelow(True)
    axes[0].set_ylabel("Spearman ρ of the score with the oracle")
    axes[0].set_ylim(0, 1.15)
    axes[0].set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
    axes[0].set_title("Ranking of 128 base samples", fontsize=10)
    axes[1].set_ylabel("Share of crystals above 150 GPa")
    axes[1].set_ylim(0, 0.72)
    axes[1].set_title("Kept top quarter", fontsize=10)
    h, l = axes[0].get_legend_handles_labels()
    h.append(Line2D([], [], color="#111", ls="--", lw=1.2))
    l.append("All samples, no filter (right panel)")
    fig.legend(h, l, ncol=4, loc="lower center", bbox_to_anchor=(0.5, 0.97), fontsize=8.5, columnspacing=1.0, handlelength=1.3)
    fig.tight_layout()
    save(fig, "st_filter_two_generators.png")


def network_diagram():
    subprocess.run(["pdftoppm", "-r", "300", "-png", "-singlefile", str(PAPER_FIG / "supp_net_filter_K.pdf"),
                    str(FIG / "st_net_crystal_bulk_modulus")], check=True)
    print("wrote st_net_crystal_bulk_modulus.png")


if __name__ == "__main__":
    fig_labels("loop_bulk_modulus", "st_rho_vs_labels_bulk_modulus.png", "bulk_modulus", "rule 1 / volume per atom", (0.1, 1.0), "lower right")
    fig_labels("loop_heat_capacity", "st_rho_vs_labels_heat_capacity.png", "heat_capacity", "Dulong-Petit rule", (0.1, 1.05), "lower right")
    fig_hidden()
    fig_filter()
    network_diagram()
    (HERE / "figure_numbers_structure.json").write_text(json.dumps(NUM, indent=1, ensure_ascii=False) + "\n")
    print(json.dumps(NUM, ensure_ascii=False))
