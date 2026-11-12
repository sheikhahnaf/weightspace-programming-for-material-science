"""Tests of experiment E7: the Thermo-Calc pools, their tasks, the phase-diagram
prompt and the references built from the sub-system facts. No Thermo-Calc needed.
Only the systems whose pool is complete (data/calphad/systems.json) are tested."""

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from wsp.arms import (
    PD_HEADING,
    reference_priors,
    rom_prior,
    subsystem_extrapolation_prior,
    write_pd_prompt,
    write_prompt,
)
from wsp.tasks import (
    CALPHAD_GOALS,
    CALPHAD_SYSTEMS,
    CALPHAD_TASK_NAMES,
    DATA,
    calphad_facts,
    calphad_system,
    load_task,
)

ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.skipif(not CALPHAD_SYSTEMS, reason="run experiments/e7_calphad_prior/make_tc_data.py first")


def script(path: str):
    """Import an experiment script as a module."""
    file = ROOT / path
    sys.path.insert(0, str(file.parent))
    spec = importlib.util.spec_from_file_location(file.stem, file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def key(x: dict) -> tuple:
    return tuple(sorted((el, round(v, 4)) for el, v in x.items() if v > 0))


@pytest.mark.parametrize("system", CALPHAD_SYSTEMS)
def test_pool_can_be_redrawn_and_follows_its_rule(system):
    table = pd.read_csv(DATA / "calphad" / f"{system}.csv")
    spec = CALPHAD_SYSTEMS[system]
    columns = [f"x_{el}" for el in spec["elements"]]
    X = table[columns].to_numpy()
    assert np.allclose(X.sum(1), 1.0) and ((X > 0).sum(1) >= 4).all()  # four or more elements present
    assert len({tuple(row) for row in X.round(4)}) == len(X) == spec["pool_size"]
    drawn = script("experiments/e7_calphad_prior/make_tc_data.py").pool_compositions(system)
    assert np.allclose(X, np.array([[x[el] for el in spec["elements"]] for x in drawn]))
    if spec["kind"] == "hea":
        assert X.max() <= 0.35 + 1e-9 and np.allclose(20 * X, np.rint(20 * X))
    else:
        assert (table[f"x_{spec['base']}"] >= 0.5 - 1e-9).all()


@pytest.mark.parametrize("system", CALPHAD_SYSTEMS)
def test_pool_quantities_are_consistent(system):
    table = pd.read_csv(DATA / "calphad" / f"{system}.csv")
    melt = table.dropna(subset=["solidus_K", "liquidus_K"])
    assert (melt["solidus_K"] <= melt["liquidus_K"]).all()
    assert np.allclose(melt["freezing_range_K"], melt["liquidus_K"] - melt["solidus_K"], atol=0.11)
    # the phase list sums to one, and liquid is present at the fixed temperature only above the solidus
    row = table.dropna(subset=["liquid_fraction"]).iloc[0]
    assert sum(p["fraction"] for p in json.loads(row["phases_fixedT"])) == pytest.approx(1.0, abs=1e-3)
    T = CALPHAD_SYSTEMS[system]["fixed_temperature_K"]
    both = table.dropna(subset=["solidus_K", "liquid_fraction"])
    clear = (both["solidus_K"] - T).abs() > 6
    assert ((both["liquid_fraction"] > 0) == (both["solidus_K"] < T))[clear].all()


@pytest.mark.parametrize("system", CALPHAD_SYSTEMS)
def test_no_context_fact_is_a_pool_composition(system):
    """The hard rule of E7: the phase-diagram context covers sub-systems only."""
    table = pd.read_csv(DATA / "calphad" / f"{system}.csv")
    elements = CALPHAD_SYSTEMS[system]["elements"]
    pool = {key(dict(zip(elements, row))) for row in table[[f"x_{el}" for el in elements]].to_numpy()}
    facts = calphad_facts(system)
    assert facts["points"]
    for point in facts["points"]:
        assert point["n_elements"] == len(point["x"]) <= 3
        assert key(point["x"]) not in pool
        assert set(point) <= {"x", "n_elements", "solidus_K", "liquidus_K", "transus_K", "phases", "targets"}
    assert min(len(k) for k in pool) >= 4
    script("experiments/e7_calphad_prior/make_tc_data.py").check_no_leak(system)


@pytest.mark.parametrize("name", CALPHAD_TASK_NAMES)
def test_task_inputs_are_element_fractions_and_the_target_is_not_degenerate(name):
    task = load_task(name)
    system, _ = calphad_system(name)
    assert task.named_features
    assert list(task.feature_names) == [f"x_{el}" for el in CALPHAD_SYSTEMS[system]["elements"]]
    assert np.allclose(task.X.sum(1), 1.0) and np.isfinite(task.y).all()
    assert len(task.y) >= 0.9 * CALPHAD_SYSTEMS[system]["pool_size"]
    values, counts = np.unique(task.y, return_counts=True)
    assert counts.max() / len(task.y) <= 0.8  # no single value on more than 80% of the pool
    assert CALPHAD_GOALS[name] in (-1.0, 1.0)
    train, test = task.split(0)
    assert not set(train) & set(test)


@pytest.mark.parametrize("name", CALPHAD_TASK_NAMES)
def test_phase_diagram_prompt_is_the_write_prompt_plus_one_section(name):
    task = load_task(name)
    plain, with_facts = write_prompt(task), write_pd_prompt(task)
    assert len(with_facts) < 12_000
    start, end = with_facts.index(PD_HEADING), with_facts.index("# Architecture")
    assert with_facts[:start] + with_facts[end:] == plain
    section = with_facts[start:end]
    assert "at most three elements" in section and "four or more elements" in section
    facts = calphad_facts(calphad_system(name)[0])
    # one line or one cell per fact, and no number that is a pool target value by construction
    assert section.count("K: ") >= len(facts["points"])


@pytest.mark.parametrize("name", CALPHAD_TASK_NAMES)
def test_references_reproduce_the_facts_they_are_built_from(name):
    task = load_task(name)
    system, target = calphad_system(name)
    facts = calphad_facts(system)
    elements = facts["elements"]
    extrapolate, rom = subsystem_extrapolation_prior(task), rom_prior(task)
    checked = 0
    for point in facts["points"]:
        want = point["targets"][target]
        if want is None:
            continue
        x = np.array([[point["x"].get(el, 0.0) for el in elements]])
        assert extrapolate(x)[0] == pytest.approx(want, abs=1e-6 * max(1.0, abs(want)))
        if point["n_elements"] == 1:
            assert rom(x)[0] == pytest.approx(want, abs=1e-9)
        checked += 1
    assert checked >= len(facts["points"]) - 3  # nearly every fact computed
    assert np.isfinite(extrapolate(task.X)).all()
    assert set(reference_priors(task)) == {"rom", "subsystem_extrapolation"}


def test_reference_for_a_public_task_is_still_the_handbook():
    assert set(reference_priors(load_task("ti_alloy_youngs_modulus"))) == {"handbook"}


def test_bo_script_keeps_the_e1_arms_and_adds_the_e7_ones(tmp_path):
    bo = script("experiments/e1_surrogate_head/run_bo_select.py")
    assert bo.arms_for("ti_alloy_hardness", None, None) == bo.ARMS  # E1 tasks: untouched
    assert set(bo.candidates("ti_alloy_hardness")) >= {"handbook", "select_opus", "select_fable", "select_all"}
    assert bo.RUN.fullmatch("write__mpea_yield_strength")["model"] is None  # round-1 folder names still parse
    name = CALPHAD_TASK_NAMES[0]
    m = bo.RUN.fullmatch(f"writepd__{name}__opus__rep2")
    assert (m["arm"], m["task"], m["model"], m["rep"]) == ("writepd", name, "opus", "2")
    assert bo.goal(name) == CALPHAD_GOALS[name] and bo.goal("ti_alloy_youngs_modulus") == -1.0
    # with no reply on disk the LLM arms are left out
    arms = bo.arms_for(name, None, tmp_path)
    assert arms[:2] == ("random", "gp") and "subsystem_extrapolation" in arms and not any("select" in a for a in arms)
    # a reply to the phase-diagram prompt becomes a candidate of the _pd arm only
    from wsp import MLPHead, dump_weights

    task = load_task(name)
    folder = tmp_path / f"writepd__{name}__opus__rep1"
    folder.mkdir()
    (folder / "reply.txt").write_text(dump_weights(MLPHead(task.X.shape[1], (16,), 1).state_dict()))
    found = bo.candidates(name, tmp_path)
    assert list(found["select_opus_pd"]) == [folder.name] and not found["select_opus"]
    assert "select_opus_pd" in bo.arms_for(name, None, tmp_path)
