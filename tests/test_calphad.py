"""Tests of experiment E7: the Thermo-Calc pools, their tasks, the phase-diagram
prompt and the references built from the binary facts. No Thermo-Calc needed."""

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from wsp.arms import (
    PD_HEADING,
    binary_extrapolation_prior,
    reference_priors,
    rom_prior,
    write_pd_prompt,
    write_prompt,
)
from wsp.tasks import (
    CALPHAD_GOALS,
    CALPHAD_SYSTEMS,
    CALPHAD_TASK_NAMES,
    DATA,
    calphad_binary_facts,
    calphad_system,
    load_task,
)

ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.skipif(
    not all((DATA / "calphad" / f"{s}{suffix}").exists() for s in CALPHAD_SYSTEMS for suffix in (".csv", "_binaries.json")),
    reason="run experiments/e7_calphad_prior/make_tc_data.py first",
)


def script(path: str):
    """Import an experiment script as a module."""
    file = ROOT / path
    sys.path.insert(0, str(file.parent))
    spec = importlib.util.spec_from_file_location(file.stem, file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("system", CALPHAD_SYSTEMS)
def test_pool_follows_the_sampling_rule_and_can_be_redrawn(system):
    table = pd.read_csv(DATA / "calphad" / f"{system}.csv")
    X = table[[c for c in table.columns if c.startswith("x_")]].to_numpy()
    units = np.rint(20 * X).astype(int)
    assert np.allclose(20 * X, units) and (units.sum(1) == 20).all()  # 5 at.% grid, rows sum to 1
    assert units.max() <= 7 and ((units > 0).sum(1) >= 4).all()  # at most 35 at.%, four or more elements
    assert len({tuple(row) for row in units}) == len(units) == 400
    drawn = script("experiments/e7_calphad_prior/make_tc_data.py").sample_pool(X.shape[1])
    rows = table["id"].str[-3:].astype(int).to_numpy()
    assert (units == drawn[rows]).all()


@pytest.mark.parametrize("system", CALPHAD_SYSTEMS)
def test_pool_quantities_are_consistent(system):
    table = pd.read_csv(DATA / "calphad" / f"{system}.csv")
    T = CALPHAD_SYSTEMS[system]["T"]
    melt = table.dropna(subset=["solidus_K", "liquidus_K"])
    assert (melt["solidus_K"] <= melt["liquidus_K"]).all()
    assert np.allclose(melt["freezing_range_K"], melt["liquidus_K"] - melt["solidus_K"], atol=0.11)
    parts = table[[f"{k}_fraction_{T}K" for k in ("solid_solution", "intermetallic", "liquid")]].dropna()
    assert np.allclose(parts.sum(1), 1.0, atol=1e-3)
    # the grouping can be audited from the JSON column
    row = table.dropna(subset=[f"intermetallic_fraction_{T}K"]).iloc[0]
    phases = json.loads(row[f"phases_{T}K"])
    assert sum(p["fraction"] for p in phases if p["kind"] == "intermetallic") == pytest.approx(
        row[f"intermetallic_fraction_{T}K"], abs=1e-3)
    # liquid at the fixed temperature exactly when the solidus lies below it
    both = table.dropna(subset=["solidus_K", f"liquid_fraction_{T}K"])
    clear = (both["solidus_K"] - T).abs() > 2
    assert ((both[f"liquid_fraction_{T}K"] > 0) == (both["solidus_K"] < T))[clear].all()


@pytest.mark.parametrize("name", CALPHAD_TASK_NAMES)
def test_task_inputs_are_element_fractions_and_the_target_is_not_degenerate(name):
    task = load_task(name)
    system, _ = calphad_system(name)
    assert task.named_features and all(n.startswith("x_") for n in task.feature_names)
    assert list(task.feature_names) == [f"x_{el}" for el in calphad_binary_facts(system)["elements"]]
    assert np.allclose(task.X.sum(1), 1.0)
    assert len(task.y) >= 380  # at most 5% of the pool lost to failed calculations
    assert np.mean(task.y == np.median(task.y)) < 0.8  # no single value on more than 80% of the pool
    assert CALPHAD_GOALS[name] in (-1.0, 1.0)


@pytest.mark.parametrize("system", CALPHAD_SYSTEMS)
def test_binary_facts_hold_no_multicomponent_data(system):
    facts = calphad_binary_facts(system)
    n = len(facts["elements"])
    assert len(facts["binaries"]) == n * (n - 1) // 2
    assert set(facts["melting_point_K"]) == set(facts["elements"])
    for key, binary in facts["binaries"].items():
        assert key == "-".join(binary["elements"]) and len(binary["elements"]) == 2
        assert set(binary["points"]) == {"25", "50", "75"}
        for point in binary["points"].values():
            for phase in point["phases"]:
                assert set(phase) <= {"phase", "fraction", "kind", "order"}  # no compositions beyond the binary's own


@pytest.mark.parametrize("name", CALPHAD_TASK_NAMES)
def test_phase_diagram_prompt_is_the_write_prompt_plus_one_section(name):
    task = load_task(name)
    plain, with_facts = write_prompt(task), write_pd_prompt(task)
    assert len(with_facts) < 12_000
    start = with_facts.index(PD_HEADING)
    end = with_facts.index("# Architecture")
    assert with_facts[:start] + with_facts[end:] == plain
    section = with_facts[start:end]
    assert "binary systems only" in section
    facts = calphad_binary_facts(calphad_system(name)[0])
    assert all(f"\n{key}: " in section for key in facts["binaries"])


@pytest.mark.parametrize("name", CALPHAD_TASK_NAMES)
def test_references_reproduce_the_facts_they_are_built_from(name):
    task = load_task(name)
    system, target = calphad_system(name)
    facts = calphad_binary_facts(system)
    elements = facts["elements"]
    rom, pairwise = rom_prior(task), binary_extrapolation_prior(task)
    pure = np.eye(len(elements))
    expected = [facts["melting_point_K"][el] if target == "solidus" else 0.0 for el in elements]
    assert np.allclose(rom(pure), expected) and np.allclose(pairwise(pure), expected)
    for binary in facts["binaries"].values():  # the 50 at.% alloy of each binary gets the binary's own value back
        point = binary["points"]["50"]
        x = np.zeros((1, len(elements)))
        x[0, [elements.index(el) for el in binary["elements"]]] = 0.5
        if target == "solidus":
            want = point["solidus_K"]
        elif target == "freezing_range":
            want = None if point["solidus_K"] is None else point["liquidus_K"] - point["solidus_K"]
        else:
            want = float(any(p["kind"] == "intermetallic" for p in point["phases"]))
        if want is not None:
            assert pairwise(x)[0] == pytest.approx(want, abs=1e-6)
    assert set(reference_priors(task)) == {"rom", "binary_extrapolation"}


def test_reference_for_a_public_task_is_still_the_handbook():
    assert set(reference_priors(load_task("ti_alloy_youngs_modulus"))) == {"handbook"}


def test_bo_script_keeps_the_e1_arms_and_adds_the_e7_ones(tmp_path):
    bo = script("experiments/e1_surrogate_head/run_bo_select.py")
    assert bo.arms_for("ti_alloy_hardness", None, None) == bo.ARMS  # E1 tasks: untouched
    assert bo.RUN.fullmatch("write__mpea_yield_strength")["model"] is None  # round-1 folder names still parse
    m = bo.RUN.fullmatch("writepd__cantor_al_solidus__opus__rep2")
    assert (m["arm"], m["task"], m["model"], m["rep"]) == ("writepd", "cantor_al_solidus", "opus", "2")
    assert bo.goal("cantor_al_solidus") == 1.0 and bo.goal("ti_alloy_youngs_modulus") == -1.0
    # with no reply on disk the LLM arms are left out; a constant rule of mixtures too
    assert bo.arms_for("cantor_al_solidus", None, tmp_path) == ("random", "gp", "rom", "binary_extrapolation")
    assert bo.arms_for("cantor_al_freezing_range", None, tmp_path) == ("random", "gp", "binary_extrapolation")
    # a reply to the phase-diagram prompt becomes a candidate of the _pd arm only
    from wsp import MLPHead, dump_weights

    task = load_task("cantor_al_solidus")
    head = MLPHead(task.X.shape[1], (16,), 1)
    folder = tmp_path / "writepd__cantor_al_solidus__opus__rep1"
    folder.mkdir()
    (folder / "reply.txt").write_text(dump_weights(head.state_dict()))
    found = bo.candidates("cantor_al_solidus", tmp_path)
    assert list(found["select_opus_pd"]) == [folder.name] and not found["select_opus"]
    assert "select_opus_pd" in bo.arms_for("cantor_al_solidus", None, tmp_path)
