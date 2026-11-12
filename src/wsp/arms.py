"""The LLM arms of experiment E1: build each prompt, apply and score each reply.

Arm C  "edit"   a trained head plus its out-of-fold errors by target decile;
                the LLM returns weight edits that should remove the bias.
Arm E  "write"  an all-zero network on named inputs plus a description of the
                task; the LLM returns every weight. The network is scored on its
                own and as the prior mean of a GP.

Arm E' "write_pd" (experiment E7)  arm E plus phase-diagram facts for the
                constituent binaries, computed with CALPHAD; same reply, same scoring.

The reference methods that get the same information are here too: affine
recalibration for arm C, a constant-mean GP at the same training size for arm E,
and for E7 the rule of mixtures and a pairwise extrapolation of the binary facts.
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
from .tasks import CALPHAD_GOALS, Task, calphad_binary_facts, calphad_system

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


_PHASE_WORDS = {"LIQUID": "liquid", "HCP_A3": "hcp", "SIGMA": "sigma", "MU_PHASE": "mu"}


def _phase_word(phase: dict) -> str:
    """A database phase name in the words of a phase diagram."""
    family = phase["phase"].split("#")[0]
    ordered = phase["kind"] == "intermetallic"
    if family == "BCC_B2":
        return "B2" if ordered else "bcc"
    if family == "FCC_L12":
        return "L12" if ordered else "fcc"
    return _PHASE_WORDS.get(family, family.replace("_LAVES", " Laves").replace("_", " "))


def phase_diagram_facts(task: Task) -> str:
    """The binary facts of the task's system as compact text: one line per binary."""
    system, _ = calphad_system(task.name)
    facts = calphad_binary_facts(system)
    T = int(facts["fixed_temperature_K"])
    elements = [name[2:] for name in task.feature_names]

    def number(value) -> str:
        return "?" if value is None else f"{value:.0f}"

    lines = [
        f"These facts are for the pure elements and the {len(facts['binaries'])} binary systems only; nothing "
        f"here was calculated for a ternary or higher alloy. Source: Thermo-Calc, TCHEA8 database, 1 atm, the "
        f"same database as the target.",
        "",
        "Melting points in K: " + ", ".join(f"{el} {facts['melting_point_K'][el]:.0f}" for el in elements) + ".",
        "",
        f"One line per binary A-B. s/l = solidus/liquidus in K at 25, 50 and 75 at.% B. min = lowest liquidus "
        f"along the binary on a 5 at.% grid and the at.% B where it lies (0 or 100 means the lower-melting "
        f"element). Then the stable phases at {T} K at 25 | 50 | 75 at.% B, where bcc, fcc, hcp are the "
        f"disordered solid solutions, B2 and L12 are ordered, and 'bcc + bcc' is a miscibility gap.",
    ]
    for key, binary in facts["binaries"].items():
        points = [binary["points"][pct] for pct in ("25", "50", "75")]
        melt = " ".join(f"{number(p['solidus_K'])}/{number(p['liquidus_K'])}" for p in points)
        phases = " | ".join(" + ".join(_phase_word(q) for q in p["phases"]) or "?" for p in points)
        lines.append(f"{key}: s/l {melt}; min {binary['liquidus_min_K']:.0f} at {binary['liquidus_min_at_pct_second']}; "
                     f"{T} K: {phases}")
    return "\n".join(lines)


PD_HEADING = "# Phase-diagram facts for the constituent binaries (computed with CALPHAD)"


def write_pd_prompt(task: Task) -> str:
    """The write prompt, unchanged, with the binary facts inserted after the task."""
    head, architecture = write_prompt(task).split("\n\n# Architecture\n", 1)
    return f"{head}\n\n{PD_HEADING}\n{phase_diagram_facts(task)}\n\n# Architecture\n{architecture}"


def _pair_values(task: Task, value) -> np.ndarray:
    """Symmetric matrix over the task's elements of `value(binary's 50 at.% point, i, j)`; 0 where missing."""
    facts = calphad_binary_facts(calphad_system(task.name)[0])
    elements = [name[2:] for name in task.feature_names]
    table = np.zeros((len(elements), len(elements)))
    for binary in facts["binaries"].values():
        i, j = (elements.index(el) for el in binary["elements"])
        v = value(binary["points"]["50"], *binary["elements"])
        table[i, j] = table[j, i] = 0.0 if v is None else v
    return table


def rom_prior(task: Task):
    """Rule of mixtures of the pure-element values in the binary facts, no LLM, no data:
    the melting points for the solidus, and zero for a freezing range or an
    intermetallic fraction (a pure element has neither)."""
    system, target = calphad_system(task.name)
    tm = calphad_binary_facts(system)["melting_point_K"]
    table = np.array([tm[name[2:]] if target == "solidus" else 0.0 for name in task.feature_names])
    return lambda U: U @ table


def binary_extrapolation_prior(task: Task):
    """Pairwise extrapolation of the binary facts, no LLM, no fit to multicomponent data.

    y(x) = rule of mixtures + sum over pairs of 4 x_i x_j W_ij (Muggianu form), with
    W_ij read at 50 at.% of binary i-j:
      solidus                 binary solidus minus the mean of the two melting points
      freezing range          binary liquidus minus binary solidus
      intermetallic fraction  1 if the binary has an intermetallic or ordered phase
                              at the system's temperature, else 0
    """
    system, target = calphad_system(task.name)
    tm = calphad_binary_facts(system)["melting_point_K"]

    def value(point, a, b):
        if target == "solidus":
            return None if point["solidus_K"] is None else point["solidus_K"] - 0.5 * (tm[a] + tm[b])
        if target == "freezing_range":
            return None if point["solidus_K"] is None else point["liquidus_K"] - point["solidus_K"]
        return float(any(q["kind"] == "intermetallic" for q in point["phases"]))

    pairs, base = _pair_values(task, value), rom_prior(task)
    return lambda U: base(U) + 2.0 * np.einsum("ni,ij,nj->n", U, pairs, U)  # 2 x'Wx = 4 sum_{i<j} x_i x_j W_ij


def reference_priors(task: Task) -> dict:
    """The data-free, LLM-free predictors a written network is compared with."""
    if task.name in CALPHAD_GOALS:
        return {"rom": rom_prior(task), "binary_extrapolation": binary_extrapolation_prior(task)}
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
