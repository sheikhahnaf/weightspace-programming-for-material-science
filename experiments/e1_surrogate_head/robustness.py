"""Checks that stress the headline numbers. Each one was added after a critical review of the code.

    python experiments/e1_surrogate_head/robustness.py crystals    # each crystal counted once; DFT and eSEN labels apart
    python experiments/e1_surrogate_head/robustness.py filter      # stronger trained baselines for the screening filter
    python experiments/e1_surrogate_head/robustness.py rules       # other label-free textbook rules on the alloy tasks
    python experiments/e1_surrogate_head/robustness.py bo_rule     # Bayesian optimization with the best of those rules
    python experiments/e1_surrogate_head/robustness.py control     # embedding + descriptors control, constant column dropped
    python experiments/e1_surrogate_head/robustness.py stats       # run-level tests, Holm across targets, phase-fraction lead
    python experiments/e1_surrogate_head/robustness.py all

What each check answers
  crystals  Every run of a closed loop starts from the same 500 (bulk modulus) or 445 (heat capacity)
            crystals. For bulk modulus these are Materials Project crystals with DFT labels; for
            heat capacity they come from an earlier loop. Only the crystals a generator proposed
            during a run are certain to carry the oracle's (eSEN) labels. Scores over "all rows"
            count the starting set once per run. Here every crystal is counted once and the
            starting set is scored apart from the crystals added during the runs.
  filter    The trained reference of the filter was one small MLP, and it had an input-scaling bug
            (fixed in filter_arm.trained_k_scorer). Here it is scored beside a ridge regression on
            log K and a random forest trained on the same 400 crystals and 15 descriptors.
  rules     The alloy reference is a rule of mixtures of one elemental property. Here four more
            label-free descriptors are scored (signs fixed from metallurgy, not from the data).
  bo_rule   The best of them (atomic size mismatch) as a prior mean, same loop and selection rule.
  control   The z-scoring of the descriptors divided an all-zero column by 1e-8. Here columns that
            are constant on the training pool are dropped. GP fits are not seeded, so values can
            differ from the cached cells of run_structure_prior.py in the second decimal.
  stats     Tests with the run (not the run x draw cell) as the unit; Holm correction across the
            Thermo-Calc targets as well as within one; the paired test behind "ahead on phase fractions".

Writes results/robustness/<check>.json and summary.md (rebuilt from whatever json files exist).
"""

from __future__ import annotations

import json
import sys
import warnings
from collections import defaultdict
from dataclasses import replace
from pathlib import Path

import numpy as np
from scipy.stats import pearsonr, spearmanr, wilcoxon

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
E3 = ROOT / "experiments" / "e3_crystal_filter"
E7 = ROOT / "experiments" / "e7_calphad_prior"
OUT = HERE / "results" / "robustness"
sys.path[:0] = [str(HERE), str(E3)]
ALLOYS = ("ti_alloy_youngs_modulus", "ti_alloy_yield_strength", "ti_alloy_hardness", "mpea_hardness", "mpea_yield_strength")
MODELS = ("opus", "fable", "sonnet", "haiku")


def save(name: str, value) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{name}.json").write_text(json.dumps(value, indent=1) + "\n")


def three(y: np.ndarray, m: np.ndarray) -> dict:
    """rho, R2 of the prediction as written, R2 after the best straight-line rescaling."""
    return {"rho": float(spearmanr(m, y).statistic), "r2": float(1 - np.mean((m - y) ** 2) / y.var()),
            "r2_rescaled": float(pearsonr(m, y).statistic ** 2), "n": int(len(y))}


# ------------------------------------------------------------------ crystals
def crystals() -> None:
    import filter_arm
    from wsp import tasks

    out = {}
    for name, key in {"loop_bulk_modulus": "K", "loop_heat_capacity": "Cp"}.items():
        table, n_runs = tasks._closed_loop_table(*tasks._CLOSED_LOOPS[name])
        D = np.load(HERE / "results" / "structure_prior" / f"descriptors__{name}.npy")
        y = tasks.load_task(name).y
        first = ~table["structure_id"].duplicated().to_numpy()
        source = table["oracle_source"].to_numpy()
        subsets = {
            "all rows (starting set counted once per run)": np.ones(len(y), bool),
            "each crystal once": first,
            "starting set (shared by all runs)": first & (source == "warm_start"),
            "proposed by a generator and scored by the oracle (eSEN)": first & (source == "oracle"),
            "added from the seed pool during the loop": first & (source == "seed_pool"),
            "test rows of the task (oracle + seed pool)": first & (source != "warm_start"),
        }
        predictors = {"rule": [1.0 / D[:, 0] if key == "K" else 3 * 8.314462618 / D[:, 1]]}
        for folder in sorted((E3 / "runs").glob(f"filter_{key}__*")):
            if (folder / "reply.txt").exists():
                try:
                    m = filter_arm.scorer((folder / "reply.txt").read_text())(D)
                except Exception:
                    continue
                predictors.setdefault(folder.name.replace(f"filter_{key}__", "").split("__")[0], []).append(m)
        out[name] = {"runs": n_runs, "rows": int(len(y)), "label_source_counts": {k: int(v.sum()) for k, v in subsets.items()}, "scores": {}}
        for label, rows in subsets.items():
            out[name]["scores"][label] = {
                who: {k: float(np.mean([three(y[rows], m[rows])[k] for m in ms])) for k in ("rho", "r2", "r2_rescaled")}
                for who, ms in predictors.items()}
    save("crystals", out)


# -------------------------------------------------------------------- filter
def filter_baselines() -> None:
    import filter_arm
    from ase.io import read
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.linear_model import RidgeCV

    frames = read(ROOT / "data" / "mlip_reference" / "elastic.extxyz", index=":")
    X = np.array([filter_arm.describe(a) for a in frames])
    K = np.array([a.info["K_ref"] for a in frames])
    keep = X.std(0) > 1e-6
    mu, sd = X[:, keep].mean(0), X[:, keep].std(0)
    ridge = RidgeCV(alphas=np.logspace(-3, 3, 13)).fit((X[:, keep] - mu) / sd, np.log(K))
    forest = RandomForestRegressor(300, random_state=0).fit(X, K)
    out = {"train": {"crystals": int(len(K)), "volume_per_atom_range": [float(X[:, 0].min()), float(X[:, 0].max())]}}
    for backbone, folder in (("MatterGen", "hprc"), ("CrystalFlow", "hprc_cf")):
        filter_arm.HPRC = filter_arm.SAMPLES / folder
        rows = [r for r in filter_arm.crystals() if r["variant"] == "base"]
        Xt, t = np.array([r["x"] for r in rows]), np.array([r["K"] for r in rows])
        ok = np.isfinite(t)
        Xt, t = Xt[ok], t[ok]
        scorers = {"volume rule": -Xt[:, 0], "trained MLP": filter_arm.trained_k_scorer()(Xt),
                   "ridge on log K": ridge.predict((Xt[:, keep] - mu) / sd), "random forest": forest.predict(Xt)}
        for model in MODELS:
            for folder_ in sorted((E3 / "runs").glob(f"filter_K__{model}__rep*")):
                if (folder_ / "reply.txt").exists():
                    scorers[f"written, {model} {folder_.name[-4:]}"] = filter_arm.scorer((folder_ / "reply.txt").read_text())(Xt)
        quarter = max(1, round(0.25 * len(t)))
        best = float(np.sort(t)[-quarter:].mean())
        table = {}
        for who, s in scorers.items():
            top = np.argsort(-s)[:quarter]
            table[who] = {"rho": float(spearmanr(s, t).statistic), "share_above_150_in_top_quarter": float((t[top] > 150).mean()),
                          "mean_K_of_top_quarter": float(t[top].mean())}
        for model in MODELS:  # mean over a model's replies
            mine = [v for k, v in table.items() if k.startswith(f"written, {model} ")]
            if mine:
                table[f"written, {model} (mean)"] = {k: float(np.mean([v[k] for v in mine])) for k in mine[0]}
        out[backbone] = {"samples": int(len(t)), "share_above_150": float((t > 150).mean()), "mean_K": float(t.mean()),
                         "mean_K_of_best_quarter": best, "volume_per_atom_range": [float(Xt[:, 0].min()), float(Xt[:, 0].max())],
                         "scorers": table}
    save("filter", out)


# --------------------------------------------------------------------- rules
def element_table(names, what: str) -> np.ndarray:
    from pymatgen.core import Element

    values = []
    for n in names:
        if n == "x_other":
            values.append(np.nan)
            continue
        e = Element(n[2:])
        if what == "vec":
            values.append(float(e.group if e.group <= 12 else e.group - 10))
        elif what == "radius":
            r = e.metallic_radius or e.atomic_radius
            values.append(float(r) if r else np.nan)
        else:
            v = getattr(e, what)
            values.append(float(v) if v is not None else np.nan)
    values = np.array(values)
    values[np.isnan(values)] = np.nanmean(values)
    return values


def size_mismatch(task) -> np.ndarray:
    """delta = sqrt(sum_i c_i (1 - r_i / r_mean)^2): the textbook measure of solid-solution strengthening.

    Radii are pymatgen's metallic radii; B, C and Si have none and fall back to the empirical atomic
    radius, and the 'other' input gets the mean radius. For the modulus target the sign of its relation to the
    target has no metallurgical basis; it is scored there only for completeness."""
    r = element_table(task.feature_names, "radius")
    mean = task.X @ r
    return np.sqrt((task.X * (1 - r[None] / mean[:, None]) ** 2).sum(1))


def rules() -> None:
    from wsp.tasks import load_task

    standalone = json.loads((HERE / "results" / "standalone" / "summary.json").read_text())
    out = {}
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for name in ALLOYS:
            task = load_task(name)
            X, y = task.X, task.y
            cands = {"rule of mixtures, melting point": X @ element_table(task.feature_names, "melting_point"),
                     "rule of mixtures, shear modulus": X @ element_table(task.feature_names, "rigidity_modulus"),
                     "rule of mixtures, Young's modulus": X @ element_table(task.feature_names, "youngs_modulus"),
                     "valence electron concentration (low = stronger)": -(X @ element_table(task.feature_names, "vec")),
                     "atomic size mismatch": size_mismatch(task)}
            out[name] = {k: float(spearmanr(v, y).statistic) for k, v in cands.items()}
            out[name] |= {"rule of mixtures used in the paper": standalone[f"{name}|handbook"]["rho"]}
            out[name] |= {m: standalone[f"{name}|{m}"]["rho"] for m in MODELS if f"{name}|{m}" in standalone}
    save("rules", out)


def bo_rule_trace(task_name: str, seed: int, n_init: int = 5, steps: int = 25) -> float:
    import run_bo_select as bs
    import torch
    from wsp.arms import gp_with_prior
    from wsp.baselines import Prepared, fit_gp
    from wsp.tasks import load_task

    warnings.filterwarnings("ignore")
    torch.set_num_threads(1)
    task = load_task(task_name)
    X, y = task.X, bs.goal(task_name) * task.y
    prior = bs.goal(task_name) * size_mismatch(task)
    labelled = list(np.random.default_rng(seed).permutation(len(y))[:n_init])
    best = [float(y[labelled].max())]
    for _ in range(steps):
        pool = np.setdiff1d(np.arange(len(y)), labelled)
        yt = y[labelled]
        data = Prepared(X[labelled], yt, X[pool], y[pool], float(yt.mean()), float(yt.std() + 1e-8))
        use = np.ptp(prior[labelled]) > 0 and np.ptp(yt) > 0 and np.corrcoef(prior[labelled], yt)[0, 1] > bs.THRESHOLD
        mean, std = gp_with_prior(data, prior[labelled], prior[pool])[:2] if use else fit_gp(data)
        labelled.append(int(pool[np.argmax(bs.expected_improvement(mean, std, yt.max()))]))
        best.append(float(y[labelled].max()))
    return float(np.mean((y.max() - np.array(best))[1:]))


def bo_rule(seeds: int = 20) -> None:
    from joblib import Parallel, delayed

    out = {}
    for name in ALLOYS:
        mine = np.array(Parallel(n_jobs=8)(delayed(bo_rule_trace)(name, s) for s in range(seeds)))

        def cached(arm):
            base = HERE / "results" / "bo_select" / "init5_steps25" / name
            traces = [json.loads((base / f"{arm}__seed{s}.json").read_text()) for s in range(seeds)]
            return np.array([np.mean((t["optimum"] - np.array(t["best_so_far"]))[1:]) for t in traces])

        gp = cached("gp")
        out[name] = {"size mismatch": {"auc": float(mine.mean()), "auc_by_seed": [float(v) for v in mine], "seeds_better": int((mine < gp).sum()), "seeds_worse": int((mine > gp).sum()),
                                       "wilcoxon_p": float(wilcoxon(mine - gp).pvalue) if np.any(mine != gp) else 1.0}}
        for arm in ("gp", "handbook", "select_opus", "select_fable"):
            out[name][arm] = {"auc": float(cached(arm).mean())}
        for arm in ("select_opus", "select_fable"):  # written network against the stronger rule, paired by seed
            d = cached(arm) - mine
            out[name][arm] |= {"vs_size_mismatch_p": float(wilcoxon(d).pvalue) if np.any(d != 0) else 1.0,
                               "seeds_better_than_size_mismatch": int((d < 0).sum()),
                               "seeds_worse_than_size_mismatch": int((d > 0).sum())}
        print(name, {k: v for k, v in out[name].items()}, flush=True)
        save("bo_rule", out)
    # Holm over the five tasks, for each comparison (the uncorrected p values favour whichever side they favour)
    for arm, key in (("size mismatch", "wilcoxon_p"), ("select_opus", "vs_size_mismatch_p"), ("select_fable", "vs_size_mismatch_p")):
        for name, p in holm({name: out[name][arm][key] for name in out}).items():
            out[name][arm][key + "_holm"] = p
    save("bo_rule", out)


# ------------------------------------------------------------------- control
def control_cell(run: int, n: int, draw: int) -> dict:
    import torch
    from wsp.baselines import fit_gp, prepare
    from wsp.tasks import load_task

    warnings.filterwarnings("ignore")
    torch.set_num_threads(1)
    name = "loop_bulk_modulus"
    task = load_task(name)
    y = task.y
    D = np.load(HERE / "results" / "structure_prior" / f"descriptors__{name}.npy")
    pool, test = task.split(run)
    train = pool[np.random.default_rng(1000 * run + draw).permutation(len(pool))[:n]] if n else pool
    U = (task.X - task.X[pool].mean(0)) / (task.X[pool].std(0) + 1e-8)
    base = replace(prepare(task, run), U_train=U[train], y_train=y[train], U_test=U[test], y_test=y[test],
                   y_mean=float(y[train].mean()), y_std=float(y[train].std() + 1e-8))
    keep = D[pool].std(0) > 1e-6
    as_run = (D - D[pool].mean(0)) / (D[pool].std(0) + 1e-8)
    fixed = (D[:, keep] - D[pool][:, keep].mean(0)) / D[pool][:, keep].std(0)
    inputs = {"embedding": U, "embedding + descriptors, as first run": np.hstack([U, as_run]),
              "embedding + descriptors, constant column dropped": np.hstack([U, fixed]), "descriptors only": fixed}
    return {k: float(spearmanr(y[test], fit_gp(replace(base, U_train=Z[train], U_test=Z[test]))[0]).statistic) for k, Z in inputs.items()}


def control() -> None:
    from joblib import Parallel, delayed

    out = {}
    for n, draws in ((5, 3), (10, 3), (20, 3), (50, 3), (0, 1)):
        cells = Parallel(n_jobs=8)(delayed(control_cell)(r, n, d) for r in range(6) for d in range(draws))
        out["all 500" if n == 0 else str(n)] = {k: float(np.mean([c[k] for c in cells])) for k in cells[0]}
        print(n, out["all 500" if n == 0 else str(n)], flush=True)
        save("control", out)


# --------------------------------------------------------------------- stats
def holm(p: dict) -> dict:
    order = sorted(p, key=p.get)
    out, running = {}, 0.0
    for i, k in enumerate(order):
        running = max(running, min(1.0, (len(order) - i) * p[k]))
        out[k] = running
    return out


def stats() -> None:
    out = {}

    # (1) crystals: the run is the unit (the six runs share one starting set; draws within a run are not independent)
    cells = defaultdict(list)
    for path in sorted((HERE / "results" / "structure_prior" / "cells" / "loop_bulk_modulus").glob("run*__n*__draw*.json")):
        c = json.loads(path.read_text())
        cells[(path.name.split("__")[1], c["run"])].append(c)
    out["crystal_runs"] = {}
    for n in ("n5", "n10", "n20"):
        for model in MODELS:
            for fit in ("two_stage", "map", "marginal"):
                gp, ours = [], []
                for run in range(6):
                    group = cells[(n, run)]
                    gp.append(np.mean([c["gp"]["spearman"] for c in group]))
                    ours.append(np.mean([v[fit]["spearman"] for c in group for k, v in c["priors"].items()
                                         if k.startswith(model) and "spearman" in v[fit]]))
                d = np.array(ours) - np.array(gp)
                out["crystal_runs"][f"{n}|{model}|{fit}"] = {"plain": float(np.mean(gp)), "with_mean": float(np.mean(ours)),
                                                             "runs_better": int((d > 0).sum()), "runs": 6,
                                                             "wilcoxon_p": float(wilcoxon(d).pvalue) if np.any(d != 0) else 1.0}

    # (2) Thermo-Calc optimization: Holm within a target (as reported), across the 33 targets, across every test
    bo = json.loads((E7 / "results" / "bo" / "summary_init5_steps25_seeds20.json").read_text())["tasks"]
    arms = ("subsystem_extrapolation", "select_opus", "select_opus_pd", "select_fable", "select_fable_pd")
    # two of the 35 targets leave nothing to gain (the plain GP has zero regret in every seed); they are not tested
    raw = {(t, a): v[a]["wilcoxon_p"] for t, v in bo.items() for a in arms
           if a in v and v[a]["wilcoxon_p"] is not None and v["gp"]["auc_mean"] > 0}
    sign = {(t, a): np.sign(bo[t]["gp"]["auc_mean"] - bo[t][a]["auc_mean"]) for t, a in raw}
    everything = holm(raw)
    out["thermo_calc_bo"] = {"targets": len({t for t, _ in raw})}
    for a in arms:
        across = holm({t: p for (t, b), p in raw.items() if b == a})
        row = {}
        for label, p in (("within target (as reported)", {t: bo[t][a]["wilcoxon_p_holm"] for (t, b) in raw if b == a}),
                         ("across targets", across), ("across all tests", {t: everything[(t, a)] for (t, b) in raw if b == a}),
                         ("uncorrected", {t: raw[(t, a)] for (t, b) in raw if b == a})):
            row[label] = {"better": int(sum(p[t] < 0.05 and sign[(t, a)] > 0 for t in p)),
                          "worse": int(sum(p[t] < 0.05 and sign[(t, a)] < 0 for t in p))}
        out["thermo_calc_bo"][a] = row

    # (3) alloys: the same, over the five tasks
    bo = json.loads(next((HERE / "results" / "bo_select").glob("summary_init5_steps25*.json")).read_text())
    bo = bo.get("tasks", bo)
    out["alloy_bo"] = {}
    for a in ("handbook", "select_opus", "select_fable"):
        raw = {t: bo[t][a]["wilcoxon_p"] for t in ALLOYS if t in bo}
        across = holm(raw)
        better = lambda p: int(sum(p[t] < 0.05 and bo[t][a]["auc_mean"] < bo[t]["gp"]["auc_mean"] for t in p))  # noqa: E731
        out["alloy_bo"][a] = {"within task (as reported)": better({t: bo[t][a]["wilcoxon_p_holm"] for t in raw}), "across tasks": better(across)}

    # (4) "ahead of the extrapolation on phase fractions": paired over the 16 phase-fraction targets
    standalone = json.loads((HERE / "results" / "standalone" / "summary.json").read_text())
    every = sorted({k.split("|")[0] for k in standalone if k.endswith("|subsystem_extrapolation")})
    for key, targets in (("phase_fraction_lead", [t for t in every if "fraction" in t]), ("all_targets_lead", every)):
        out[key] = {"targets": len(targets)}
        for model in ("opus", "fable", "opus + facts", "fable + facts"):
            pairs = [(standalone[f"{t}|{model}"]["rho"], standalone[f"{t}|subsystem_extrapolation"]["rho"]) for t in targets
                     if f"{t}|{model}" in standalone and np.isfinite(standalone[f"{t}|subsystem_extrapolation"]["rho"])]
            d = np.array([a - b for a, b in pairs])
            out[key][model] = {"n": len(d), "mean_written": float(np.mean([a for a, _ in pairs])),
                               "mean_extrapolation": float(np.mean([b for _, b in pairs])),
                               "targets_ahead": int((d > 0).sum()), "targets_behind": int((d < 0).sum()),
                               "wilcoxon_p": float(wilcoxon(d).pvalue)}
    save("stats", out)


# ------------------------------------------------------------------- summary
def summary() -> None:
    def load(name):
        path = OUT / f"{name}.json"
        return json.loads(path.read_text()) if path.exists() else None

    lines = ["# Robustness checks", "", "Written by `robustness.py`; see its docstring for what each check answers.", ""]
    if (d := load("crystals")):
        for task, v in d.items():
            lines += [f"## Crystals, `{task}`: each crystal once, starting set apart", "",
                      f"{v['runs']} runs, {v['rows']} rows.", "", "| Rows | Crystals | Predictor | ρ | R² as written | R² rescaled |", "|---|---|---|---|---|---|"]
            for label, scores in v["scores"].items():
                for who, s in scores.items():
                    lines.append(f"| {label} | {v['label_source_counts'][label]} | {who} | {s['rho']:.2f} | {s['r2']:.2f} | {s['r2_rescaled']:.2f} |")
            lines.append("")
    if (d := load("filter")):
        lines += ["## Screening filter: trained baselines", "",
                  f"Trained on {d['train']['crystals']} Materials Project crystals (volume per atom {d['train']['volume_per_atom_range'][0]:.1f} to {d['train']['volume_per_atom_range'][1]:.1f} Å³).", ""]
        for backbone in ("MatterGen", "CrystalFlow"):
            v = d[backbone]
            lines += [f"**{backbone}**: {v['samples']} samples, volume per atom {v['volume_per_atom_range'][0]:.1f} to {v['volume_per_atom_range'][1]:.1f} Å³, "
                      f"share above 150 GPa {v['share_above_150']:.2f}, mean {v['mean_K']:.0f} GPa, best possible quarter {v['mean_K_of_best_quarter']:.0f} GPa.", "",
                      "| Scorer | ρ | Share above 150 GPa in top quarter | Mean K of top quarter (GPa) |", "|---|---|---|---|"]
            lines += [f"| {who} | {s['rho']:.2f} | {s['share_above_150_in_top_quarter']:.2f} | {s['mean_K_of_top_quarter']:.0f} |"
                      for who, s in v["scorers"].items() if "rep" not in who]
            lines.append("")
    if (d := load("rules")):
        cols = list(next(iter(d.values())))
        lines += ["## Alloys: other label-free rules (ρ over the whole pool)", "", "| Task | " + " | ".join(cols) + " |", "|---|" + "---|" * len(cols)]
        lines += [f"| `{t}` | " + " | ".join(f"{v[c]:.2f}" if c in v else "" for c in cols) + " |" for t, v in d.items()]
        lines.append("")
    if (d := load("bo_rule")):
        lines += ["## Alloys: Bayesian optimization with atomic size mismatch as the prior mean", "",
                  "Area under the regret curve, 20 seeds, two-stage fit (lower is better).", "",
                  "Brackets: seeds better / worse, Wilcoxon p, and p after Holm correction over the five tasks. For the size mismatch the comparison is with the plain GP; for the written networks it is with the size mismatch.", "",
                  "| Task | Plain GP | Rule of mixtures | Size mismatch | Opus | Fable |", "|---|---|---|---|---|---|"]
        for t, v in d.items():
            s = v["size mismatch"]

            def against(arm):
                w = v[arm]
                return (f"{w['auc']:.3g} ({w['seeds_better_than_size_mismatch']} / {w['seeds_worse_than_size_mismatch']}, "
                        f"{w['vs_size_mismatch_p']:.2g}, {w['vs_size_mismatch_p_holm']:.2g})")

            lines.append(f"| `{t}` | {v['gp']['auc']:.3g} | {v['handbook']['auc']:.3g} | {s['auc']:.3g} ({s['seeds_better']} / {s['seeds_worse']}, "
                         f"{s['wilcoxon_p']:.2g}, {s['wilcoxon_p_holm']:.2g}) | {against('select_opus')} | {against('select_fable')} |")
        lines.append("")
    if (d := load("control")):
        cols = list(next(iter(d.values())))
        lines += ["## Crystal bulk modulus: plain GP on different inputs (ρ on generated crystals)", "", "| Labels | " + " | ".join(cols) + " |", "|---|" + "---|" * len(cols)]
        lines += [f"| {n} | " + " | ".join(f"{v[c]:.2f}" for c in cols) + " |" for n, v in d.items()]
        lines.append("")
    if (d := load("stats")):
        lines += ["## Crystal bulk modulus: written mean against the plain GP, run as the unit", "",
                  "| Labels | Model | Fit | Plain GP ρ | With written mean ρ | Runs better | Wilcoxon p (6 runs; smallest possible 0.031) |", "|---|---|---|---|---|---|---|"]
        for k, v in d["crystal_runs"].items():
            n, model, fit = k.split("|")
            lines.append(f"| {n[1:]} | {model} | {fit} | {v['plain']:.2f} | {v['with_mean']:.2f} | {v['runs_better']} of {v['runs']} | {v['wilcoxon_p']:.3f} |")
        lines += ["", f"## Thermo-Calc optimization: targets significantly better / worse than the plain GP, by correction ({d['thermo_calc_bo']['targets']} targets)", "",
                  "| Prior mean | Uncorrected | Holm within target (as reported) | Holm across targets | Holm across all tests |", "|---|---|---|---|---|"]
        for a, v in d["thermo_calc_bo"].items():
            if a != "targets":
                cell = lambda k: f"{v[k]['better']} / {v[k]['worse']}"  # noqa: E731
                lines.append(f"| {a} | {cell('uncorrected')} | {cell('within target (as reported)')} | {cell('across targets')} | {cell('across all tests')} |")
        lines += ["", "## Alloy optimization: tasks significantly better than the plain GP", "", "| Prior mean | Holm within task (as reported) | Holm across the five tasks |", "|---|---|---|"]
        lines += [f"| {a} | {v['within task (as reported)']} | {v['across tasks']} |" for a, v in d["alloy_bo"].items()]
        for key, title in (("phase_fraction_lead", "Phase fractions"), ("all_targets_lead", "All Thermo-Calc targets")):
            lines += ["", f"## {title}: written networks against the sub-system extrapolation, paired over targets", "",
                      "| Model | Targets | Mean ρ written | Mean ρ extrapolation | Targets where written is ahead / behind | Wilcoxon p |", "|---|---|---|---|---|---|"]
            lines += [f"| {m} | {v['n']} | {v['mean_written']:.2f} | {v['mean_extrapolation']:.2f} | {v['targets_ahead']} / {v['targets_behind']} | {v['wilcoxon_p']:.3f} |"
                      for m, v in d[key].items() if m != "targets"]
        lines.append("")
    (OUT / "summary.md").write_text("\n".join(lines))
    print("\n".join(lines))


CHECKS = {"crystals": crystals, "filter": filter_baselines, "rules": rules, "bo_rule": bo_rule, "control": control, "stats": stats}

if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    warnings.filterwarnings("ignore")
    for name in (CHECKS if which == "all" else [which]):
        CHECKS[name]()
    summary()
