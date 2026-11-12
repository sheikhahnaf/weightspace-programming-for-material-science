"""Draw every data figure of the deck from the project's result files (read-only).

    eval "$(/Users/alvi/miniconda3/bin/conda shell.zsh hook)" && conda activate matinvent
    PYTHONDONTWRITEBYTECODE=1 python plots/make_figures.py

Sources, all under the repository root:
  experiments/e1_surrogate_head/results/write_arm/summary.json      ranking with no data, GP ranking by labels
  experiments/e1_surrogate_head/results/bo_select/init5_steps25/    one BO trace per task, arm and seed
  experiments/e1_surrogate_head/results/bo_select/summary_init5_steps25_seeds20.json
  experiments/e1_surrogate_head/runs/write__ti_alloy_youngs_modulus__opus__rep1/reply.txt
  experiments/runs_audit.json                                       tokens and seconds per reply
  experiments/e5_bnn_start/results/bnn_summary.json                 BNN arms
Writes PNG files into figures/ and the numbers printed on the slides into plots/figure_numbers.json.
"""
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
FIG = HERE.parent / "figures"
E1 = ROOT / "experiments/e1_surrogate_head"

plt.rcParams.update({
    "font.family": "Helvetica", "font.size": 10, "axes.labelsize": 10.5, "axes.titlesize": 10.5,
    "xtick.labelsize": 9.5, "ytick.labelsize": 9.5, "legend.fontsize": 9, "axes.spines.top": False,
    "axes.spines.right": False, "axes.linewidth": 0.8, "savefig.dpi": 300, "figure.dpi": 100,
    "legend.frameon": False, "axes.titleweight": "bold",
})

TASKS = ["ti_alloy_youngs_modulus", "ti_alloy_yield_strength", "ti_alloy_hardness", "mpea_hardness", "mpea_yield_strength"]
TNAME = {"ti_alloy_youngs_modulus": "Ti Young's modulus", "ti_alloy_yield_strength": "Ti yield strength",
         "ti_alloy_hardness": "Ti hardness", "mpea_hardness": "MPEA hardness", "mpea_yield_strength": "MPEA yield strength"}
TSHORT = {"ti_alloy_youngs_modulus": "Ti\nmodulus", "ti_alloy_yield_strength": "Ti yield\nstrength",
          "ti_alloy_hardness": "Ti\nhardness", "mpea_hardness": "MPEA\nhardness", "mpea_yield_strength": "MPEA yield\nstrength"}
UNIT = {"ti_alloy_youngs_modulus": "GPa", "ti_alloy_yield_strength": "MPa", "ti_alloy_hardness": "HV",
        "mpea_hardness": "HV", "mpea_yield_strength": "MPa"}
MODELS = ["opus", "fable", "sonnet", "haiku"]
MNAME = {"opus": "Opus 5.5", "fable": "Fable 5.2", "sonnet": "Sonnet 5.5", "haiku": "Haiku 5.5",
         "handbook (no LLM)": "Handbook rule", "handbook": "Handbook rule", "gp": "Plain GP", "random": "Random search",
         "select_all": "All replies"}
COL = {"opus": "#500000", "fable": "#1F3A5F", "sonnet": "#2A8C8C", "haiku": "#C47F17", "handbook (no LLM)": "#8A8F98",
       "handbook": "#8A8F98", "gp": "#111111", "random": "#BBBBBB", "select_all": "#6B4C9A"}
NUM = {}


def save(fig, name):
    fig.savefig(FIG / name, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("wrote", name)


WRITE = json.loads((E1 / "results/write_arm/summary.json").read_text())
BO = json.loads((E1 / "results/bo_select/summary_init5_steps25_seeds20.json").read_text())
SIZES = [5, 10, 20, 50]


# ---------------------------------------------------------------- 1. plain GP ranking by labels
def fig_gp_labels():
    fig, ax = plt.subplots(figsize=(6.4, 4.1))
    styles = ["o-", "s-", "^-", "D-", "v-"]
    cols = ["#1F3A5F", "#2A8C8C", "#C47F17", "#6B4C9A", "#C0282D"]
    NUM["gp_rho"] = {}
    for t, st, c in zip(TASKS, styles, cols):
        y = [WRITE[t]["opus"][f"n{n}"]["gp"] for n in SIZES]
        NUM["gp_rho"][t] = [round(v, 2) for v in y]
        ax.plot(range(4), y, st, color=c, lw=1.8, ms=6, label=TNAME[t])
    ax.set_xticks(range(4), [str(n) for n in SIZES])
    ax.set_xlabel("Labelled alloys given to the GP")
    ax.set_ylabel("Spearman ρ on held-out alloys")
    ax.set_ylim(0, 0.9)
    ax.axhline(0, color="#888", lw=0.6)
    ax.legend(title="Plain GP, constant mean (5 data seeds)", loc="lower right", title_fontsize=9)
    ax.grid(axis="y", color="#E5E5E5", lw=0.6)
    save(fig, "gp_rho_vs_labels.png")


# ---------------------------------------------------------------- 2. the written network
def read_reply(path):
    tensors, name = {}, None
    for ln in Path(path).read_text().splitlines():
        if ln.startswith("##"):
            name = ln.split()[1]
            tensors[name] = []
        elif ln.strip():
            tensors[name].append([float(v) for v in ln.split()])
    return {k: np.array(v) for k, v in tensors.items()}


def fig_written_network():
    run = E1 / "runs/write__ti_alloy_youngs_modulus__opus__rep1"
    w = read_reply(run / "reply.txt")
    W1, b1, w2, b2 = w["net.0.weight"], w["net.0.bias"][0], w["net.2.weight"][0], w["net.2.bias"][0][0]
    used = [i for i in range(16) if np.any(W1[i] != 0) or b1[i] != 0]
    NUM["written_network"] = {"hidden_used": len(used), "weights_total": int(W1.size + b1.size + w2.size + 1),
                              "nonzero": int((W1 != 0).sum() + (b1 != 0).sum() + (w2 != 0).sum() + 1), "out_bias": b2}
    els = ["Al", "Cr", "Cu", "Fe", "Hf", "Mn", "Mo", "Nb", "Si", "Sn", "Ta", "Ti", "V", "Zr", "other"]
    fig = plt.figure(figsize=(6.6, 3.5))
    gs = fig.add_gridspec(1, 3, width_ratios=[15, 1, 1], wspace=0.08)
    ax, axb, axo = (fig.add_subplot(g) for g in gs)
    M = W1[used]
    vmax = np.abs(M).max()
    ax.imshow(M, cmap="RdBu_r", vmin=-vmax, vmax=vmax, aspect="auto")
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            v = M[i, j]
            ax.text(j, i, f"{v:g}", ha="center", va="center", fontsize=8.5,
                    color="white" if abs(v) > 0.55 * vmax else "#111")
    ax.set_xticks(range(15), els)
    ax.set_yticks(range(len(used)), [f"unit {i}" for i in used])
    ax.xaxis.tick_top()
    ax.set_title("First layer: weight on each atomic fraction", pad=22)
    for a, vals, ttl in ((axb, b1[used], "bias"), (axo, w2[used], "output\nweight")):
        vm = max(1e-9, np.abs(vals).max())
        a.imshow(vals[:, None], cmap="RdBu_r", vmin=-vm, vmax=vm, aspect="auto")
        for i, v in enumerate(vals):
            a.text(0, i, f"{v:g}", ha="center", va="center", fontsize=8.5, color="white" if abs(v) > 0.55 * vm else "#111")
        a.set_xticks([0], [ttl])
        a.xaxis.tick_top()
        a.set_yticks([])
    for a in (ax, axb, axo):
        a.tick_params(length=0)
        for s in a.spines.values():
            s.set_visible(True)
            s.set_linewidth(0.6)
    fig.text(0.5, 0.02, f"y = output weights · relu(W x + bias) + ({b2:g});  hidden units 5 to 15 are all zero;  "
             "red positive, blue negative", ha="center", fontsize=9.5)
    save(fig, "written_network_weights.png")


# ---------------------------------------------------------------- 3. ranking with no data
def fig_rho_alone():
    srcs = ["handbook (no LLM)"] + MODELS
    fig, ax = plt.subplots(figsize=(6.6, 4.1))
    wd = 0.16
    NUM["alone"] = {}
    for k, s in enumerate(srcs):
        y = [WRITE[t][s]["alone_spearman"] for t in TASKS]
        NUM["alone"][s] = [round(v, 2) for v in y]
        x = np.arange(len(TASKS)) + (k - 2) * wd
        ax.bar(x, y, wd, color=COL[s], label=MNAME[s], edgecolor="white", lw=0.4)
        for xi, yi in zip(x, y):
            ax.text(xi, yi + (0.015 if yi >= 0 else -0.015), f"{yi:.2f}", ha="center", va="bottom" if yi >= 0 else "top",
                    fontsize=7.5, rotation=90)
    ax.axhline(0, color="#333", lw=0.8)
    ax.set_xticks(range(len(TASKS)), [TSHORT[t] for t in TASKS])
    ax.set_ylabel("Spearman ρ of the prior alone, no labels")
    ax.set_ylim(-0.95, 1.12)
    ax.legend(ncol=5, loc="upper center", columnspacing=0.9, handlelength=1.0, handletextpad=0.4, fontsize=8.5)
    ax.grid(axis="y", color="#E5E5E5", lw=0.6)
    ax.set_axisbelow(True)
    save(fig, "rho_alone_bars.png")


# ---------------------------------------------------------------- 4. GP ranking by labels, with and without a prior
def fig_rho_labels(rule, name):
    fig, axes = plt.subplots(2, 3, figsize=(6.7, 4.2), sharey=True)
    axes = axes.ravel()
    for ax, t in zip(axes, TASKS):
        gp = [WRITE[t]["opus"][f"n{n}"]["gp"] for n in SIZES]
        ax.plot(range(4), gp, "o--", color=COL["gp"], lw=1.6, ms=4.5, label="Plain GP")
        for s in ["handbook (no LLM)"] + MODELS:
            y = [WRITE[t][s][f"n{n}"][f"prior_{rule}"] for n in SIZES]
            ax.plot(range(4), y, "o-", color=COL[s], lw=1.6, ms=4.5, label="GP + " + MNAME[s])
        ax.set_title(TNAME[t], fontsize=10)
        ax.set_xticks(range(4), [str(n) for n in SIZES])
        ax.set_ylim(-0.3, 0.95)
        ax.axhline(0, color="#888", lw=0.5)
        ax.grid(axis="y", color="#E5E5E5", lw=0.6)
    for ax in axes[3:5]:
        ax.set_xlabel("Labelled alloys")
    axes[2].set_xlabel("Labelled alloys")
    axes[0].set_ylabel("Spearman ρ")
    axes[3].set_ylabel("Spearman ρ")
    h, l = axes[0].get_legend_handles_labels()
    axes[5].axis("off")
    axes[5].legend(h, l, loc="center", fontsize=9, title="Mean a·m(x) + b, " + ("a fitted" if rule == "fitted" else "a = 1"),
                   title_fontsize=9)
    fig.tight_layout(h_pad=0.8, w_pad=0.6)
    save(fig, name)


# ---------------------------------------------------------------- 5. the two slope rules at 5 labels
def fig_slope_rules():
    fig, axes = plt.subplots(2, 2, figsize=(6.7, 4.2), sharey=True)
    wd = 0.26
    NUM["slope5"] = {}
    for ax, m in zip(axes.ravel(), MODELS):
        gp = [WRITE[t][m]["n5"]["gp"] for t in TASKS]
        fit = [WRITE[t][m]["n5"]["prior_fitted"] for t in TASKS]
        one = [WRITE[t][m]["n5"]["prior_one"] for t in TASKS]
        NUM["slope5"][m] = {"gp": [round(v, 2) for v in gp], "fitted": [round(v, 2) for v in fit], "one": [round(v, 2) for v in one]}
        x = np.arange(len(TASKS))
        ax.bar(x - wd, gp, wd, color="#BBBBBB", label="Plain GP")
        ax.bar(x, fit, wd, color=COL[m], label="Prior, slope fitted")
        ax.bar(x + wd, one, wd, color=COL[m], alpha=0.45, hatch="///", edgecolor="white", label="Prior, slope fixed at 1")
        ax.set_title(MNAME[m], fontsize=10)
        ax.set_xticks(x, [TSHORT[t] for t in TASKS], fontsize=8)
        ax.set_ylim(0, 0.9)
        ax.grid(axis="y", color="#E5E5E5", lw=0.6)
        ax.set_axisbelow(True)
    for ax in axes[:, 0]:
        ax.set_ylabel("ρ at 5 labels")
    from matplotlib.patches import Patch
    hs = [Patch(color="#BBBBBB", label="Plain GP"), Patch(color="#555", label="Prior mean, slope a fitted"),
          Patch(facecolor="#555", alpha=0.45, hatch="///", edgecolor="white", label="Prior mean, slope a = 1")]
    fig.legend(handles=hs, ncol=3, loc="upper center", bbox_to_anchor=(0.5, 1.045), fontsize=9)
    fig.tight_layout(h_pad=0.6, w_pad=0.6)
    save(fig, "slope_rules_5_labels.png")


# ---------------------------------------------------------------- 6. BO regret curves
ARMS = ["random", "gp", "handbook", "select_opus", "select_fable", "select_sonnet", "select_haiku", "select_all"]


def regret(task, arm):
    out = []
    for s in range(20):
        t = json.loads((E1 / f"results/bo_select/init5_steps25/{task}/{arm}__seed{s}.json").read_text())
        out.append(t["optimum"] - np.array(t["best_so_far"]))
    return np.array(out)


def akey(arm):
    return arm if arm == "select_all" else arm.replace("select_", "")


def draw_regret(ax, task, arms, bands=("gp", "select_opus", "select_fable")):
    for arm in arms:
        r = regret(task, arm)
        # the recomputed area must equal the summary file's
        assert abs(r[:, 1:].mean(1).mean() - BO["tasks"][task][arm]["auc_mean"]) < 1e-6, (task, arm)
        m, se = r.mean(0), r.std(0, ddof=1) / np.sqrt(len(r))
        k = akey(arm)
        ls = {"random": ":", "gp": "--", "handbook": "-."}.get(arm, "-")
        ax.plot(range(26), m, ls, color=COL[k], lw=2.0 if arm in bands else 1.5, label=MNAME[k] if k in MNAME else k)
        if arm in bands:
            ax.fill_between(range(26), m - se, m + se, color=COL[k], alpha=0.16, lw=0)
    ax.set_title(f"{TNAME[task]} ({UNIT[task]})", fontsize=10)
    ax.set_xlim(0, 25)
    ax.set_ylim(bottom=0)
    ax.set_xticks([0, 5, 10, 15, 20, 25])
    ax.grid(axis="y", color="#E5E5E5", lw=0.6)


def fig_regret_ti():
    arms = ARMS[:7]
    fig, axes = plt.subplots(2, 2, figsize=(6.7, 4.25))
    axes = axes.ravel()
    for ax, t in zip(axes, TASKS[:3]):
        draw_regret(ax, t, arms)
    axes[2].set_xlabel("BO step (labels after the first 5)")
    axes[1].set_xlabel("BO step (labels after the first 5)")
    axes[0].set_ylabel("Regret")
    axes[2].set_ylabel("Regret")
    h, l = axes[0].get_legend_handles_labels()
    axes[3].axis("off")
    axes[3].legend(h, l, loc="center", fontsize=9, title="Mean of 20 seeds; band ± 1 s.e.m.\n(plain GP, Opus 5.5, Fable 5.2)",
                   title_fontsize=8.5)
    fig.tight_layout(h_pad=0.8, w_pad=0.8)
    save(fig, "bo_regret_ti.png")


def fig_regret_mpea_hardness():
    fig, ax = plt.subplots(figsize=(6.4, 4.1))
    draw_regret(ax, "mpea_hardness", ARMS[:7])
    ax.set_xlabel("BO step (labels after the first 5)")
    ax.set_ylabel("Regret: best in pool minus best found (HV)")
    ax.legend(fontsize=9, ncol=2, loc="upper right", title="Mean of 20 seeds; band ± 1 s.e.m. (GP, Opus, Fable)", title_fontsize=8.5)
    save(fig, "bo_regret_mpea_hardness.png")


def fig_regret_mpea_ys():
    fig, ax = plt.subplots(figsize=(6.4, 4.1))
    draw_regret(ax, "mpea_yield_strength", ARMS[:7])
    ax.set_xlabel("BO step (labels after the first 5)")
    ax.set_ylabel("Regret: best in pool minus best found (MPa)")
    ax.set_ylim(0, 1900)
    ax.legend(fontsize=9, ncol=2, loc="upper right", title="Mean of 20 seeds; band ± 1 s.e.m. (GP, Opus, Fable)", title_fontsize=8.5)
    save(fig, "bo_regret_mpea_yield_strength.png")


def fig_seed_diff():
    """Per-seed area under regret minus the plain GP's, same seed, MPEA yield strength."""
    task = "mpea_yield_strength"
    arms = ["handbook", "select_opus", "select_fable", "select_sonnet", "select_haiku", "select_all"]
    gp = regret(task, "gp")[:, 1:].mean(1)
    fig, ax = plt.subplots(figsize=(6.4, 4.1))
    rng = np.random.default_rng(0)
    NUM["seed_diff"] = {}
    for i, arm in enumerate(arms):
        d = regret(task, arm)[:, 1:].mean(1) - gp
        k = akey(arm)
        b, w = int((d < 0).sum()), int((d > 0).sum())
        assert (b, w) == (BO["tasks"][task][arm]["seeds_better_than_gp"], BO["tasks"][task][arm]["seeds_worse_than_gp"])
        NUM["seed_diff"][arm] = {"better": b, "worse": w, "mean_diff": float(d.mean())}
        ax.scatter(i + rng.uniform(-0.16, 0.16, len(d)), d, s=26, color=COL[k], alpha=0.75, lw=0)
        ax.plot([i - 0.28, i + 0.28], [d.mean()] * 2, color="#111", lw=2)
        ax.text(i, 1380, f"{b} better\n{w} worse", ha="center", va="top", fontsize=8.5)
    ax.axhline(0, color="#333", lw=0.8)
    ax.set_xticks(range(len(arms)))
    ax.set_xticklabels(["Handbook\nrule", "Opus 5.5", "Fable 5.2", "Sonnet 5.5", "Haiku 5.5", "All\nreplies"])
    ax.set_ylabel("Area under regret − plain GP's (MPa)")
    ax.set_ylim(-1150, 1400)
    ax.text(0.99, 0.02, "dot: one of 20 seeds; bar: mean; below zero is better than the plain GP",
            transform=ax.transAxes, ha="right", fontsize=8.5, color="#444")
    ax.grid(axis="y", color="#E5E5E5", lw=0.6)
    ax.set_axisbelow(True)
    save(fig, "auc_seed_differences_mpea_yield_strength.png")


def fig_auc_ratio():
    arms = ["handbook", "select_opus", "select_fable", "select_sonnet", "select_haiku", "select_all"]
    fig, ax = plt.subplots(figsize=(6.6, 4.1))
    wd = 0.135
    NUM["auc_ratio"] = {}
    for k, arm in enumerate(arms):
        y = [BO["tasks"][t][arm]["auc_mean"] / BO["tasks"][t]["gp"]["auc_mean"] for t in TASKS]
        p = [BO["tasks"][t][arm]["wilcoxon_p_holm"] for t in TASKS]
        NUM["auc_ratio"][arm] = [round(v, 2) for v in y]
        x = np.arange(len(TASKS)) + (k - 2.5) * wd
        ax.bar(x, y, wd, color=COL[akey(arm)], label=MNAME[akey(arm)], edgecolor="white", lw=0.4)
        for xi, yi, pi in zip(x, y, p):
            if pi < 0.05:
                ax.text(xi, yi + 0.01, "*", ha="center", va="bottom", fontsize=13, fontweight="bold")
    ax.axhline(1, color="#111", lw=1.2, ls="--", label="Plain GP = 1")
    ax.set_xticks(range(len(TASKS)), [TSHORT[t] for t in TASKS])
    ax.set_ylabel("Area under regret ÷ plain GP's (lower is better)")
    ax.set_ylim(0, 1.5)
    ax.legend(ncol=4, loc="upper left", fontsize=8.5, columnspacing=1.0, handlelength=1.4,
              title="* Holm-corrected p < 0.05, paired Wilcoxon over 20 seeds", title_fontsize=8.5)
    ax.grid(axis="y", color="#E5E5E5", lw=0.6)
    ax.set_axisbelow(True)
    save(fig, "auc_relative_to_gp.png")


# ---------------------------------------------------------------- 7. replicate replies
def fig_replicates():
    fig, ax = plt.subplots(figsize=(6.6, 4.1))
    NUM["replicates"] = {}
    for i, t in enumerate(TASKS):
        for k, m in enumerate(MODELS):
            v = WRITE[t][m]["alone_spearman_per_reply"]
            NUM["replicates"][f"{t}|{m}"] = [round(x, 2) for x in v]
            x = i + (k - 1.5) * 0.19
            ax.plot([x] * len(v), v, "o", color=COL[m], ms=6, alpha=0.8, mec="white", mew=0.5, label=MNAME[m] if i == 0 else None)
            ax.plot([x, x], [min(v), max(v)], color=COL[m], lw=1.2)
            if len(v) < 3:
                ax.text(x, max(v) + 0.035, "2 valid", ha="center", fontsize=7.5, rotation=90, va="bottom")
    ax.axhline(0, color="#333", lw=0.8)
    ax.set_xticks(range(len(TASKS)), [TSHORT[t] for t in TASKS])
    ax.set_ylabel("Spearman ρ of each written network alone")
    ax.set_ylim(-0.25, 1.0)
    ax.legend(ncol=4, loc="upper center", fontsize=9, title="One dot per valid reply to the identical prompt (three requested)",
              title_fontsize=8.5, columnspacing=1.0, handletextpad=0.2)
    ax.grid(axis="y", color="#E5E5E5", lw=0.6)
    ax.set_axisbelow(True)
    save(fig, "replicate_replies.png")


# ---------------------------------------------------------------- 8. cost
def fig_cost():
    aud = json.loads((ROOT / "experiments/runs_audit.json").read_text())
    ID = {"opus": "claude-opus-5-5", "fable": "claude-fable-5-2", "sonnet": "claude-sonnet-5-5", "haiku": "claude-haiku-5-5"}
    w = [a for a in aud if a["experiment"] == "e1_surrogate_head" and a["run"].startswith("write__")]
    fig, axes = plt.subplots(1, 2, figsize=(6.7, 3.9))
    NUM["cost"] = {}
    for ax, key, scale, lab in ((axes[0], "output_tokens", 1e-3, "Output tokens per reply (thousands)"),
                                (axes[1], "duration_ms", 1e-3, "Seconds per reply")):
        for i, m in enumerate(MODELS):
            v = np.array([a[key] for a in w if a["model_id"] == ID[m]]) * scale
            assert len(v) == 15
            med = float(np.median(v))
            NUM["cost"].setdefault(m, {})[key] = {"median": med, "min": float(v.min()), "max": float(v.max()), "n": len(v)}
            ax.bar(i, med, 0.62, color=COL[m])
            ax.errorbar(i, med, yerr=[[med - v.min()], [v.max() - med]], color="#111", capsize=4, lw=1.1)
            ax.text(i + 0.36, med, f"{med:.0f}" if med >= 10 else f"{med:.1f}", va="center", ha="left", fontsize=9)
        ax.set_xticks(range(4), [MNAME[m].replace(" ", "\n") for m in MODELS])
        ax.set_xlim(-0.6, 3.9)
        ax.set_ylabel(lab)
        ax.grid(axis="y", color="#E5E5E5", lw=0.6)
        ax.set_axisbelow(True)
    fig.suptitle("Bar: median of 15 replies per model; whisker: minimum to maximum", fontsize=9.5, y=0.99)
    fig.tight_layout()
    save(fig, "cost_per_reply.png")


# ---------------------------------------------------------------- 9. BNN arms
BNN_ARMS = [("gp", "GP", "plain"), ("gp_llm_mean", "GP", "written network as prior mean"),
            ("mcd_random", "MC dropout", "random start"), ("mcd_llm_init", "MC dropout", "starts at written weights"),
            ("mcd_llm_anchor", "MC dropout", "starts there, anchored"), ("mcd_llm_mean", "MC dropout", "written network as prior mean"),
            ("ens_random", "Deep ensemble", "random starts"), ("ens_llm_init", "Deep ensemble", "starts at written weights + noise"),
            ("hmc_zero", "HMC", "zero-centred prior"), ("hmc_llm_init", "HMC", "chain starts at written weights"),
            ("hmc_llm_prior", "HMC", "prior centred on written weights")]
FAMCOL = {"GP": "#500000", "MC dropout": "#1F3A5F", "Deep ensemble": "#2A8C8C", "HMC": "#C47F17"}


def bnn_means():
    b = json.loads((ROOT / "experiments/e5_bnn_start/results/bnn_summary.json").read_text())
    out = {}
    for metric in ("spearman", "coverage95"):
        for lo, sizes in (("few", ("10", "20")), ("many", ("50", "200"))):
            cells = [v for k, v in b.items() if k.split("|")[0] == metric and k.split("|")[3] in sizes]
            out[(metric, lo)] = {a: float(np.mean([c[a] for c in cells])) for a, _, _ in BNN_ARMS}
            out[(metric, lo, "n")] = len(cells)
    return out


def fig_bnn(metric, name, xlabel, xlim, ref=None):
    mm = bnn_means()
    NUM[f"bnn_{metric}"] = {"few": {a: round(v, 2) for a, v in mm[(metric, "few")].items()},
                            "many": {a: round(v, 2) for a, v in mm[(metric, "many")].items()},
                            "cells": [mm[(metric, "few", "n")], mm[(metric, "many", "n")]]}
    fig, axes = plt.subplots(1, 2, figsize=(6.9, 4.2), sharey=True)
    ypos, y = [], 0
    for i, (a, fam, lab) in enumerate(BNN_ARMS):
        if i and fam != BNN_ARMS[i - 1][1]:
            y += 0.6
        ypos.append(y)
        y += 1
    base = {"gp", "mcd_random", "ens_random", "hmc_zero"}
    for ax, part, ttl in ((axes[0], "few", "10 or 20 labels (24 cells)"), (axes[1], "many", "50 or 200 labels (18 cells)")):
        for (a, fam, lab), yy in zip(BNN_ARMS, ypos):
            v = mm[(metric, part)][a]
            ax.barh(yy, v, 0.78, color=FAMCOL[fam], alpha=0.4 if a in base else 1.0)
            ax.text(v + 0.012, yy, f"{v:.2f}", va="center", fontsize=8.5,
                    bbox=dict(facecolor="white", edgecolor="none", pad=0.6))
        if ref:
            ax.axvline(ref, color="#111", ls="--", lw=1, zorder=0)
        ax.set_title(ttl, fontsize=10)
        ax.set_xlim(*xlim)
        ax.set_xlabel(xlabel)
        ax.invert_yaxis()
        ax.grid(axis="x", color="#E5E5E5", lw=0.6)
        ax.set_axisbelow(True)
    axes[0].set_yticks(ypos, [f"{fam}: {lab}" for a, fam, lab in BNN_ARMS], fontsize=8.5)
    axes[1].invert_yaxis()
    from matplotlib.patches import Patch
    from matplotlib.lines import Line2D
    hs = [Patch(color="#555", alpha=0.4, label="baseline of its family"), Patch(color="#555", label="uses the written network")]
    if ref:
        hs.append(Line2D([0], [0], color="#111", ls="--", lw=1, label="nominal 0.95"))
    fig.legend(handles=hs, ncol=3, loc="upper center", bbox_to_anchor=(0.6, 1.03), fontsize=9, columnspacing=1.0)
    fig.tight_layout()
    save(fig, name)


if __name__ == "__main__":
    fig_gp_labels()
    fig_written_network()
    fig_rho_alone()
    fig_rho_labels("fitted", "rho_vs_labels_slope_fitted.png")
    fig_rho_labels("one", "rho_vs_labels_slope_one.png")
    fig_slope_rules()
    fig_regret_ti()
    fig_regret_mpea_hardness()
    fig_regret_mpea_ys()
    fig_seed_diff()
    fig_auc_ratio()
    fig_replicates()
    fig_cost()
    fig_bnn("spearman", "bnn_ranking.png", "Mean Spearman ρ", (0, 0.95))
    fig_bnn("coverage95", "bnn_coverage.png", "Mean 95% coverage", (0, 1.12), ref=0.95)
    (HERE / "figure_numbers.json").write_text(json.dumps(NUM, indent=1) + "\n")
    print(json.dumps(NUM))
