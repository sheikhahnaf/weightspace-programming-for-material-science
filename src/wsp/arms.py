"""The LLM arms of experiment E1: build each prompt, apply and score each reply.

Arm C  "edit"   a trained head plus its out-of-fold errors by target decile;
                the LLM returns weight edits that should remove the bias.
Arm E  "write"  an all-zero network on named inputs plus a description of the
                task; the LLM returns every weight. The network is scored on its
                own and as the prior mean of a GP.

Arm E' "write_pd" (experiment E7)  arm E plus phase-diagram facts for sub-systems
                (pure elements, binaries, ternaries), computed with CALPHAD; same
                reply, same scoring.

The reference methods that get the same information are here too: affine
recalibration for arm C, a constant-mean GP at the same training size for arm E,
and for E7 the rule of mixtures and an extrapolation of the sub-system facts.
"""

from __future__ import annotations

from dataclasses import replace

import numpy as np
import torch
from sklearn.model_selection import KFold

from .baselines import Prepared, fit_gp, fit_mlp, predict, prepare, score
from .edit import apply_edits, diff, parse_edits
from .heads import MLPHead, zero_
from .prompts import build_prompt
from .serialize import load_weights
from .tasks import CALPHAD_GOALS, Task, calphad_facts, calphad_system

EDIT_HIDDEN = (32, 32)
WRITE_HIDDEN = (16,)


# ---------------------------------------------------------------- arm C: edit


def out_of_fold(data: Prepared, hidden: tuple[int, ...], seed: int, folds: int = 5) -> np.ndarray:
    """Predictions for every training row from a head that never saw that row."""
    oof = np.empty_like(data.y_train)
    for fit, held in KFold(folds, shuffle=True, random_state=seed).split(data.U_train):
        part = replace(
            data, U_train=data.U_train[fit], y_train=data.y_train[fit],
            y_mean=float(data.y_train[fit].mean()), y_std=float(data.y_train[fit].std() + 1e-8),
        )
        oof[held] = predict(fit_mlp(part, hidden, seed), data.U_train[held])
    return oof


def _decile_table(y: np.ndarray, prediction: np.ndarray, unit: str) -> str:
    edges = np.quantile(y, np.linspace(0, 1, 11))
    lines = [f"decile of true value | true range ({unit}) | mean true | mean predicted | mean error"]
    for i in range(10):
        rows = (y >= edges[i]) & ((y <= edges[i + 1]) if i == 9 else (y < edges[i + 1]))
        if rows.any():
            lines.append(
                f"{i + 1} | {edges[i]:.4g} to {edges[i + 1]:.4g} | {y[rows].mean():.4g} "
                f"| {prediction[rows].mean():.4g} | {(prediction[rows] - y[rows]).mean():+.4g}"
            )
    return "\n".join(lines)


def edit_setup(task: Task, seed: int, shuffled: bool = False):
    """The trained head, its data and its out-of-fold predictions.

    `shuffled=True` permutes the entries of every tensor: the control that
    tells reasoning about these weights apart from a generic recipe.
    """
    data = prepare(task, seed)
    head = fit_mlp(data, EDIT_HIDDEN, seed)
    oof = out_of_fold(data, EDIT_HIDDEN, seed)
    if shuffled:
        generator = torch.Generator().manual_seed(seed)
        state = {
            k: v.flatten()[torch.randperm(v.numel(), generator=generator)].reshape(v.shape)
            for k, v in head.state_dict().items()
        }
        head.load_state_dict(state)
    return data, head, oof


def edit_prompt(task: Task, seed: int, shuffled: bool = False) -> str:
    data, head, oof = edit_setup(task, seed, shuffled)
    inputs = (
        "The inputs are used as given."
        if task.named_features
        else "Each input has been standardised to zero mean and unit variance on the training rows."
    )
    job = (
        f"This network is a surrogate inside a materials discovery loop. {task.description} "
        f"{inputs} The output y is the {task.target} in {task.unit}.\n\n"
        f"The network was trained on {len(data.y_train)} rows whose target has mean "
        f"{data.y_mean:.4g} and standard deviation {data.y_std:.4g} {task.unit}. The loop cares "
        f"most about the candidates with the highest true values, and those are the ones this "
        f"network gets wrong. Its errors on training rows it had not seen (five-fold "
        f"cross-validation), grouped by decile of the true value:\n\n"
        f"{_decile_table(data.y_train, oof, task.unit)}\n\n"
        f"Edit the weights so that the network stops underpredicting the highest values on new "
        f"candidates, without losing its ranking of the rest."
    )
    return build_prompt("edit", job, head.describe(), head.state_dict())


def affine_recalibration(data: Prepared, oof: np.ndarray, prediction: np.ndarray) -> np.ndarray:
    """Least-squares stretch of the predictions, fitted on out-of-fold predictions:
    the cheapest method given the same evidence as the LLM."""
    slope, intercept = np.polyfit(oof, data.y_train, 1)
    return slope * prediction + intercept


def score_edit(task: Task, seed: int, reply: str, shuffled: bool = False) -> dict:
    data, head, oof = edit_setup(task, seed, shuffled)
    before = head.state_dict()
    after = apply_edits(before, parse_edits(reply))
    edited = MLPHead(data.U_train.shape[1], EDIT_HIDDEN, 1)
    edited.load_state_dict(after)
    report = diff(before, after)
    base = predict(head, data.U_test)
    return {
        "arm": "edit", "task": task.name, "seed": seed, "shuffled_control": shuffled,
        "weights_changed": report.changed, "weights_total": report.total,
        "changed_by_tensor": report.changed_by_tensor,
        "unedited": score(data.y_test, base),
        "llm_edit": score(data.y_test, predict(edited.eval(), data.U_test)),
        "affine_recalibration": score(data.y_test, affine_recalibration(data, oof, base)),
    }


# --------------------------------------------------------------- arm E: write


def write_prompt(task: Task) -> str:
    if not task.named_features:
        raise ValueError(f"{task.name}: arm E needs inputs with a physical meaning")
    head = zero_(MLPHead(task.X.shape[1], WRITE_HIDDEN, 1))
    names = ", ".join(f"x[{i}] = {n}" for i, n in enumerate(task.feature_names))
    job = (
        f"Write the weights of this network from what you know about materials. No training "
        f"data is given. {task.description}\n\nInput order: {names}.\n\n"
        f"The output y must be your best estimate of the {task.target} in {task.unit}. The "
        f"network will be used as the prior mean of a Gaussian process that is then given a "
        f"few measured alloys, so getting the trends and the rough scale right matters more "
        f"than exact values."
    )
    return build_prompt("write", job, head.describe(), head.state_dict())


def _subsample(data: Prepared, n: int, seed: int) -> Prepared:
    rows = np.random.default_rng(seed).permutation(len(data.y_train))[:n]
    return replace(
        data, U_train=data.U_train[rows], y_train=data.y_train[rows],
        y_mean=float(data.y_train[rows].mean()), y_std=float(data.y_train[rows].std() + 1e-8),
    )


def gp_with_prior(data: Prepared, m_train: np.ndarray, m_test: np.ndarray, slope_rule: str = "fitted"):
    """GP whose mean is a·m(x) + b.

    slope_rule="fitted": a and b by least squares on the training rows. If the
    written network is uninformative the fit drives a toward zero and this
    reduces to the constant-mean GP, but on about ten rows the fit is unstable.
    slope_rule="one": a = 1 and only the offset b is fitted, which trusts the
    network's scale. Added after the pilot showed that instability.
    """
    if slope_rule == "one":
        slope, intercept = 1.0, float(np.mean(data.y_train - m_train))
    elif slope_rule == "fitted":
        slope, intercept = np.polyfit(m_train, data.y_train, 1) if np.ptp(m_train) > 0 else (0.0, data.y_train.mean())
    else:
        raise ValueError(f"slope_rule must be 'fitted' or 'one', not {slope_rule!r}")
    residual = data.y_train - (slope * m_train + intercept)
    shifted = replace(data, y_train=residual, y_mean=float(residual.mean()), y_std=float(residual.std() + 1e-8))
    mean, std = fit_gp(shifted)
    return mean + slope * m_test + intercept, std, float(slope)


def score_prior(task: Task, m, seeds: int = 5, sizes: tuple[int, ...] = (5, 10, 20, 50)) -> list[dict]:
    """Score a data-free predictor `m` (model inputs -> target) alone and as a GP prior mean."""
    rows = []
    for seed in range(seeds):
        full = prepare(task, seed)
        m_test = m(full.U_test)
        row = {"seed": seed, "written_alone": score(full.y_test, m_test)}
        for n in (*[k for k in sizes if k < len(full.y_train)], len(full.y_train)):
            data = _subsample(full, n, seed)
            plain_mean, plain_std = fit_gp(data)
            entry = {"gp": score(data.y_test, plain_mean, plain_std)}
            for rule in ("fitted", "one"):
                mean, std, slope = gp_with_prior(data, m(data.U_train), m_test, slope_rule=rule)
                entry[f"gp_with_prior_{rule}"] = score(data.y_test, mean, std) | {"prior_slope": slope}
            entry["gp_with_written_prior"] = entry["gp_with_prior_fitted"]  # name used in round 1
            row[f"n{n}"] = entry
        rows.append(row)
    return rows


def written_head(task: Task, reply: str) -> MLPHead:
    head = MLPHead(task.X.shape[1], WRITE_HIDDEN, 1)
    head.load_state_dict(load_weights(reply))
    return head.eval()


def score_write(task: Task, reply: str, seeds: int = 5, sizes: tuple[int, ...] = (5, 10, 20, 50)) -> dict:
    head = written_head(task, reply)
    rows = score_prior(task, lambda U: predict(head, U), seeds, sizes)
    return {"arm": "write", "task": task.name, "weights": sum(p.numel() for p in head.parameters()), "per_seed": rows}


# Elemental property used by the no-LLM handbook baseline for each kind of target.
_HANDBOOK = {"modulus": "youngs_modulus", "strength": "vickers_hardness", "hardness": "vickers_hardness"}


def handbook_prior(task: Task):
    """Rule of mixtures from a table of elemental properties (pymatgen), no LLM, no data.

    Young's modulus for modulus targets; Vickers hardness of the elements for
    strength and hardness targets (ranking is what matters; the scale is refitted
    by the GP prior). Elements without a tabulated value, and the 'other' input,
    get the mean of the tabulated ones.
    """
    import warnings

    from pymatgen.core import Element

    if not task.named_features:
        raise ValueError(f"{task.name}: the handbook baseline needs element inputs")
    kind = next(k for k in _HANDBOOK if k in task.target.lower())
    values = []
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for name in task.feature_names:
            value = None if name == "x_other" else getattr(Element(name[2:]), _HANDBOOK[kind])
            values.append(float(value) if value is not None else np.nan)
    table = np.array(values)
    table[np.isnan(table)] = np.nanmean(table)
    return lambda U: U @ table


# ------------------------------------ experiment E7: phase-diagram context


_PHASE_WORDS = {"LIQUID": "liquid", "HCP_A3": "hcp", "SIGMA": "sigma", "MU_PHASE": "mu", "BCC_A2": "bcc",
                "FCC_A1": "fcc", "SIGMA_D8B": "sigma", "DIAMOND_A4": "Si(diamond)"}


def _phase_word(phase: dict) -> str:
    """A database phase name in the words of a phase diagram."""
    family = phase["phase"].split("#")[0]
    ordered = phase["kind"] == "intermetallic"
    if family in ("BCC_B2", "B2_BCC"):
        return "B2" if ordered else "bcc"
    if family in ("FCC_L12", "L12_FCC"):
        return "L12" if ordered else "fcc"
    return _PHASE_WORDS.get(family, family.replace("_LAVES", " Laves").replace("_", " "))


def _point_text(point: dict, elements: list[str], base: str | None, T: int, transus: bool) -> str:
    """One sub-system calculation on one line."""
    def number(value) -> str:
        return "?" if value is None else f"{value:.0f}"

    shown = [el for el in elements if el in point["x"] and el != base]
    if not shown:
        name = base
    elif base is None and len({round(point["x"][el], 3) for el in shown}) == 1:
        name = "-".join(shown) + (" equimolar" if len(shown) > 1 else "")
    else:
        name = (f"{base} + " if base else "") + ", ".join(f"{100 * point['x'][el]:g} {el}" for el in shown)
    melt = (f"melts {number(point['solidus_K'])}" if point["n_elements"] == 1
            else f"s/l {number(point['solidus_K'])}/{number(point['liquidus_K'])}")
    extra = f"; alpha gone above {number(point.get('transus_K'))}" if transus else ""
    phases = " + ".join(f"{_phase_word(q)} {q['fraction']:.2f}" if len(point["phases"]) > 1 else _phase_word(q)
                        for q in point["phases"]) or "?"
    return f"{name}: {melt}{extra}; {T} K: {phases}"


def phase_diagram_facts(task: Task) -> str:
    """The sub-system calculations of the task's system as compact text, one line each."""
    system, _ = calphad_system(task.name)
    facts = calphad_facts(system)
    T = int(facts["fixed_temperature_K"])
    elements, base = facts["elements"], facts["base"]
    transus = any("transus_K" in p for p in facts["points"])
    by_size = {n: [p for p in facts["points"] if p["n_elements"] == n] for n in (1, 2, 3)}
    if base is None:
        covers = (f"the {len(by_size[1])} pure elements, the {len(by_size[2]) // 3} binary systems at 25, 50 and 75 at.% "
                  f"of the second element, and the {len(by_size[3])} equimolar ternaries")
    else:
        covers = (f"pure {base}, {base} with one solute at half and at the whole of that solute's range, and {base} "
                  f"with two solutes, both at half and both at the whole of their ranges")
    lines = [
        f"These facts cover only sub-systems with at most three elements: {covers}. Nothing here was calculated "
        f"for a composition of the kind you are asked about (four or more elements). Source: Thermo-Calc, "
        f"{facts['database']} database, 1 atm, the same database as the target.",
        "",
        f"Each line: composition in at.%; s/l = solidus/liquidus in K; then the stable phases at {T} K with their "
        f"mole fractions, where bcc, fcc and hcp are the disordered solid solutions, B2 and L12 are ordered, and "
        f"the same phase listed twice is a miscibility gap.",
    ]
    if base is None:  # binaries: the three compositions of a pair on one line
        lines += [""] + [_point_text(p, elements, base, T, transus) for p in by_size[1]] + [""]
        pairs: dict[tuple, list] = {}
        for p in by_size[2]:
            pairs.setdefault(tuple(p["x"]), []).append(p)
        lowest = facts.get("binary_liquidus_minimum", {})
        for (a, b), points in pairs.items():
            points = sorted(points, key=lambda p: p["x"][b])
            parts = [_point_text(p, elements, base, T, transus).split(": ", 1)[1] for p in points]
            low = lowest.get(f"{a}-{b}")
            low = f" Lowest liquidus {low['K']:.0f} at {low['at_pct_second']} at.% {b}." if low else ""
            lines.append(f"{a}-{b} at 25 | 50 | 75 at.% {b}: " + " | ".join(parts) + "." + low)
        lines += [""] + [_point_text(p, elements, base, T, transus) for p in by_size[3]]
    else:
        lines += [""] + [_point_text(p, elements, base, T, transus) for n in (1, 2, 3) for p in by_size[n]]
    return "\n".join(lines)


PD_HEADING = "# Phase-diagram facts for sub-systems (computed with CALPHAD)"


def write_pd_prompt(task: Task) -> str:
    """The write prompt, unchanged, with the sub-system facts inserted after the task."""
    head, architecture = write_prompt(task).split("\n\n# Architecture\n", 1)
    return f"{head}\n\n{PD_HEADING}\n{phase_diagram_facts(task)}\n\n# Architecture\n{architecture}"


def rom_prior(task: Task):
    """Rule of mixtures of the pure-element values, no LLM, no data.

    High-entropy systems: the target of each pure element from the facts (its melting
    point for the solidus, zero for a freezing range, its own phase fraction).
    Balance systems (one base element): only the base element is among the facts, so
    the rule is the base element's value for every alloy, a constant.
    """
    system, target = calphad_system(task.name)
    facts = calphad_facts(system)
    pure = {next(iter(p["x"])): p["targets"][target] for p in facts["points"] if p["n_elements"] == 1}
    fallback = pure.get(facts["base"], 0.0) or 0.0
    table = np.array([pure.get(name[2:], fallback) or 0.0 for name in task.feature_names])
    return lambda U: U @ table


def subsystem_extrapolation_prior(task: Task):
    """Extrapolation of the sub-system facts to the multicomponent alloy, no LLM, no
    fit to multicomponent data. The same facts the phase-diagram prompt carries.

    High-entropy systems (Redlich-Kister-Muggianu form): rule of mixtures, plus for
    each binary x_i x_j [L0 + L1 (x_i - x_j) + L2 (x_i - x_j)^2] fitted exactly to that
    binary's three points, plus for each ternary x_i x_j x_k L_ijk fitted exactly to
    the equimolar ternary.

    Balance systems: the base element's value, plus for each solute a x + q x^2 through
    its two binary points, plus for each pair of solutes x_i x_j [b0 + b1 (x_i + x_j)]
    fitted exactly to their two ternary points.

    A fact that failed to compute contributes nothing.
    """
    system, target = calphad_system(task.name)
    facts = calphad_facts(system)
    names = [name[2:] for name in task.feature_names]
    index = {el: i for i, el in enumerate(names)}
    base = facts["base"]
    points = [(p, p["targets"][target]) for p in facts["points"] if p["targets"][target] is not None]

    def vector(point: dict) -> np.ndarray:
        x = np.zeros(len(names))
        for el, value in point["x"].items():
            x[index[el]] = value
        return x

    terms: list = []  # callables U -> contribution, built up level by level

    def model(U: np.ndarray) -> np.ndarray:
        return sum((term(U) for term in terms), np.zeros(len(U)))

    if base is None:
        rom = rom_prior(task)
        terms.append(rom)
        pairs: dict[tuple, list] = {}
        for p, y in points:
            if p["n_elements"] == 2:
                pairs.setdefault(tuple(index[el] for el in p["x"]), []).append((vector(p), y))
        for (i, j), rows in pairs.items():
            # excess / (x_i x_j) = L0 + L1 d + L2 d^2, d = x_i - x_j: a polynomial through the available points
            d = np.array([x[i] - x[j] for x, _ in rows])
            e = np.array([(y - rom(x[None])[0]) / (x[i] * x[j]) for x, y in rows])
            coefficients = np.polyfit(d, e, len(rows) - 1)
            terms.append(lambda U, i=i, j=j, c=coefficients: U[:, i] * U[:, j] * np.polyval(c, U[:, i] - U[:, j]))
        lower = list(terms)
        for p, y in points:
            if p["n_elements"] == 3:
                x = vector(p)
                i, j, k = (index[el] for el in p["x"])
                L = (y - sum(term(x[None])[0] for term in lower)) / (x[i] * x[j] * x[k])
                terms.append(lambda U, i=i, j=j, k=k, L=L: L * U[:, i] * U[:, j] * U[:, k])
    else:
        y_base = next((y for p, y in points if p["n_elements"] == 1), 0.0)
        terms.append(lambda U: np.full(len(U), y_base))
        solutes: dict[int, list] = {}
        for p, y in points:
            if p["n_elements"] == 2:
                i = next(index[el] for el in p["x"] if el != base)
                solutes.setdefault(i, []).append((p["x"][names[i]], y - y_base))
        for i, rows in solutes.items():
            c = np.array([x for x, _ in rows])
            # a x + q x^2 through the points (a x alone if only one computed)
            coefficients = np.linalg.lstsq(np.stack([c ** k for k in range(1, len(rows) + 1)], axis=1),
                                           np.array([e for _, e in rows]), rcond=None)[0]
            terms.append(lambda U, i=i, c=coefficients: sum(ck * U[:, i] ** (k + 1) for k, ck in enumerate(c)))
        lower = list(terms)
        couples: dict[tuple, list] = {}
        for p, y in points:
            if p["n_elements"] == 3:
                x = vector(p)
                i, j = (index[el] for el in p["x"] if el != base)
                couples.setdefault((i, j), []).append((x[i] + x[j], (y - sum(term(x[None])[0] for term in lower)) / (x[i] * x[j])))
        for (i, j), rows in couples.items():
            # excess / (x_i x_j) = b0 + b1 (x_i + x_j) through the available points
            coefficients = np.polyfit([t for t, _ in rows], [e for _, e in rows], len(rows) - 1)
            terms.append(lambda U, i=i, j=j, c=coefficients: U[:, i] * U[:, j] * np.polyval(c, U[:, i] + U[:, j]))
    return model


def reference_priors(task: Task) -> dict:
    """The data-free, LLM-free predictors a written network is compared with."""
    if task.name in CALPHAD_GOALS:
        return {"rom": rom_prior(task), "subsystem_extrapolation": subsystem_extrapolation_prior(task)}
    return {"handbook": handbook_prior(task)}


# -------------------------------------------------------------- arm B: repair

LEAK_NOISE = 0.3


def repair_setup(task: Task, seed: int, shuffled: bool = False):
    """A head trained with one planted leak input.

    In training the leak is the standardised target plus noise; at test time it
    is noise with the same spread, as it would be once the label is unknown.
    All inputs are standardised and unnamed, and the leak sits at a random
    position, so it can be found only from the weights.
    """
    base = prepare(task, seed)
    mean, std = base.U_train.mean(0), base.U_train.std(0) + 1e-8
    U_train, U_test = (base.U_train - mean) / std, (base.U_test - mean) / std
    rng = np.random.default_rng(1000 + seed)
    position = int(rng.integers(0, U_train.shape[1] + 1))
    spread = float(np.sqrt(1 + LEAK_NOISE**2))
    leak_train = ((base.y_train - base.y_mean) / base.y_std + LEAK_NOISE * rng.normal(size=len(base.y_train))) / spread
    leak_test = rng.normal(size=len(base.y_test))
    clean = replace(base, U_train=U_train, U_test=U_test)
    leaky = replace(
        base,
        U_train=np.insert(U_train, position, leak_train, axis=1),
        U_test=np.insert(U_test, position, leak_test, axis=1),
    )
    head = fit_mlp(leaky, EDIT_HIDDEN, seed)
    if shuffled:
        generator = torch.Generator().manual_seed(seed)
        head.load_state_dict({
            k: v.flatten()[torch.randperm(v.numel(), generator=generator)].reshape(v.shape)
            for k, v in head.state_dict().items()
        })
    return clean, leaky, head, position


def repair_prompt(task: Task, seed: int, shuffled: bool = False) -> str:
    _, leaky, head, _ = repair_setup(task, seed, shuffled)
    n_inputs = leaky.U_train.shape[1]
    job = (
        f"This network predicts the {task.target} of a material in {task.unit} from {n_inputs} "
        f"inputs. Every input was standardised to zero mean and unit variance; their names are "
        f"withheld. Exactly one input is a leak: in the training data it carried information "
        f"about the target that will not exist when the network is used, where that input is "
        f"pure noise. The other {n_inputs - 1} inputs are legitimate.\n\n"
        f"Find the leaked input from the weights, and edit the network so that its output no "
        f"longer depends on that input. Leave everything else as it is."
    )
    return build_prompt("edit", job, head.describe(), head.state_dict())


def _zero_column(state, column: int):
    out = {k: v.clone() for k, v in state.items()}
    out["net.0.weight"][:, column] = 0.0
    return out


def score_repair(task: Task, seed: int, reply: str, shuffled: bool = False) -> dict:
    clean, leaky, head, position = repair_setup(task, seed, shuffled)
    before = head.state_dict()
    after = apply_edits(before, parse_edits(reply))
    report = diff(before, after)
    n_inputs = leaky.U_train.shape[1]

    def test_score(state) -> dict:
        model = MLPHead(n_inputs, EDIT_HIDDEN, 1)
        model.load_state_dict(state)
        return score(leaky.y_test, predict(model.eval(), leaky.U_test))

    first = after["net.0.weight"]
    silenced = [j for j in range(n_inputs) if bool((first[:, j] == 0).all())]
    norms = before["net.0.weight"].norm(dim=0)
    by_norm = int(norms.argmax())
    # A second weights-only statistic: each input's effect on the output if every
    # ReLU were open. This is the calculation the models describe doing by hand.
    gain = (before["net.4.weight"] @ before["net.2.weight"] @ before["net.0.weight"]).abs().flatten()
    by_gain = int(gain.argmax())
    return {
        "arm": "repair", "task": task.name, "seed": seed, "shuffled_control": shuffled,
        "n_inputs": n_inputs, "leak_position": position,
        "inputs_silenced_by_llm": silenced,
        "llm_found_the_leak": silenced == [position],
        "largest_column_norm_input": by_norm,
        "column_norm_found_the_leak": by_norm == position,
        "leak_column_norm_over_median": float(norms[position] / norms.median()),
        "largest_linear_gain_input": by_gain,
        "linear_gain_found_the_leak": by_gain == position,
        "leak_rank_by_column_norm": int((norms > norms[position]).sum()) + 1,
        "leak_rank_by_linear_gain": int((gain > gain[position]).sum()) + 1,
        "linear_gain_repair": test_score(_zero_column(before, by_gain)),
        "weights_changed": report.changed, "weights_total": report.total,
        "changed_by_tensor": report.changed_by_tensor,
        "unrepaired": test_score(before),
        "llm_repair": test_score(after),
        "column_norm_repair": test_score(_zero_column(before, by_norm)),
        "true_column_zeroed": test_score(_zero_column(before, position)),
        "trained_without_leak": score(clean.y_test, predict(fit_mlp(clean, EDIT_HIDDEN, seed), clean.U_test)),
    }
