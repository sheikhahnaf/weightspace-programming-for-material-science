"""The campaign's applications: one regression task per materials problem.

Every task is built from files under data/, which scripts/copy_from_siblings.py
copied from the sibling repos (see data/PROVENANCE.md). A task fixes what the
inputs mean, what is predicted, and how train and test are split, so that every
method — GP, gradient-trained head, LLM-written or LLM-edited head — is scored
on the same rows.

The `<system>_*` tasks of experiment E7 are the exception to "copied": their
targets were computed here with Thermo-Calc (data/calphad/README.md).
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Callable

import numpy as np

DATA = Path(__file__).resolve().parents[2] / "data"


@dataclass(frozen=True)
class Task:
    name: str
    application: str
    target: str
    unit: str
    X: np.ndarray
    y: np.ndarray
    feature_names: tuple[str, ...]
    named_features: bool  # True when a feature has a physical meaning an LLM can reason about
    split_kind: str  # "shift": fixed train/test with distribution shift; "random": drawn per seed
    description: str
    _split: Callable[[int], tuple[np.ndarray, np.ndarray]]

    def split(self, seed: int) -> tuple[np.ndarray, np.ndarray]:
        """Row indices (train, test) for this seed."""
        return self._split(seed)


def _random_split(n: int, n_train: int) -> Callable[[int], tuple[np.ndarray, np.ndarray]]:
    def split(seed: int) -> tuple[np.ndarray, np.ndarray]:
        order = np.random.default_rng(seed).permutation(n)
        return order[:n_train], order[n_train:]

    return split


def _closed_loop_table(folder: str, seed_file: str):
    """Rows of every run of one closed loop, in the order the task uses."""
    import pandas as pd

    # Each run fitted its own PCA basis, so the same structure has different
    # coordinates in different runs. Rows of different runs are never mixed in
    # one fit: a seed selects one run, and train and test both come from it.
    frames = []
    for run, path in enumerate(p for p in sorted((DATA / folder).glob("*.parquet")) if p.name != seed_file):
        frame = pd.read_parquet(path).drop_duplicates("structure_id")
        frame = frame[np.isfinite(frame["y_cp"]) & (frame["y_cp"] > 0)]  # 0 marks a failed oracle call
        frames.append(frame.assign(run=run, pool=frame["oracle_source"] == "warm_start"))
    return pd.concat(frames, ignore_index=True), len(frames)


_CLOSED_LOOPS = {"loop_bulk_modulus": ("closed_loop_bm", "ltm_bm_seed_pool.parquet"),
                 "loop_heat_capacity": ("closed_loop_cp", "ltm_seed_pool_v3.parquet")}


def closed_loop_atoms(task_name: str) -> list:
    """The crystal behind each row of a closed-loop task (ase Atoms), in row order.

    The task's inputs are embedding coordinates with no physical meaning; this
    gives access to the structure so that named descriptors can be computed."""
    from ase.io.jsonio import decode

    table, _ = _closed_loop_table(*_CLOSED_LOOPS[task_name])
    return [decode(text) for text in table["atoms_json"]]


def _closed_loop(folder: str, seed_file: str, name: str, target: str, unit: str, what: str) -> Task:
    """Surrogate memory of the published closed loop: train on the warm-start
    pool, test on what the generators later proposed and the oracle scored."""
    table, n_runs = _closed_loop_table(folder, seed_file)
    run_of, in_pool = table["run"].to_numpy(), table["pool"].to_numpy()
    n_pool = int(in_pool[run_of == 0].sum())
    n_test = [int((~in_pool[run_of == r]).sum()) for r in range(n_runs)]

    def split(seed: int) -> tuple[np.ndarray, np.ndarray]:
        rows = run_of == seed % n_runs
        return np.flatnonzero(rows & in_pool), np.flatnonzero(rows & ~in_pool)

    X = np.stack(table["Z_pca50"].to_numpy()).astype(np.float64)
    return Task(
        name=name,
        application="BO surrogate in a generative discovery loop",
        target=target,
        unit=unit,
        X=X,
        y=table["y_cp"].to_numpy(dtype=np.float64),
        feature_names=tuple(f"pc{i}" for i in range(X.shape[1])),
        named_features=False,
        split_kind="shift",
        description=(
            f"Inputs are the first 50 principal components of mean-pooled ORB-v3 node "
            f"embeddings of a crystal. The target is {what}, computed with the eSEN-30M-OAM "
            f"potential. Training rows are the loop's warm-start pool ({n_pool} known "
            f"structures); test rows are the structures a generator (MatterGen, CrystalFlow or "
            f"ADiT) proposed in one run while being steered toward high values "
            f"({min(n_test)} to {max(n_test)} per run, {n_runs} runs; the seed picks the run)."
        ),
        _split=split,
    )


def _fractions(formulas: list[str]) -> list[dict[str, float] | None]:
    from pymatgen.core import Composition

    out: list[dict[str, float] | None] = []
    for formula in formulas:
        try:
            comp = Composition(str(formula).strip())
            out.append({str(el): float(comp.get_atomic_fraction(el)) for el in comp.elements})
        except Exception:
            out.append(None)
    return out


def _composition_task(
    name: str, application: str, formulas: list[str], y: np.ndarray, target: str, unit: str,
    source: str, n_train: int, min_count: int = 5,
) -> Task:
    """Element atomic fractions as inputs; rare elements are summed into 'other'."""
    parsed = _fractions(formulas)
    ok = np.array([p is not None for p in parsed]) & np.isfinite(y)
    parsed = [p for p, keep in zip(parsed, ok) if keep]
    y = y[ok]
    counts: dict[str, int] = {}
    for p in parsed:
        for el in p:
            counts[el] = counts.get(el, 0) + 1
    elements = sorted(el for el, c in counts.items() if c >= min_count)
    X = np.zeros((len(parsed), len(elements) + 1))
    for i, p in enumerate(parsed):
        for el, fraction in p.items():
            X[i, elements.index(el) if el in elements else -1] += fraction
    return Task(
        name=name,
        application=application,
        target=target,
        unit=unit,
        X=X,
        y=y,
        feature_names=tuple(f"x_{el}" for el in elements) + ("x_other",),
        named_features=True,
        split_kind="random",
        description=(
            f"Inputs are atomic fractions of {', '.join(elements)}, and the summed fraction of "
            f"all other elements; each row sums to 1. The target is {target} in {unit}. "
            f"{source} {len(y)} alloys."
        ),
        _split=_random_split(len(y), n_train),
    )


def _mpea() -> Task:
    import pandas as pd

    df = pd.read_csv(DATA / "alloys" / "MPEA_dataset.csv")
    temperature = next(c for c in df.columns if "Test temperature" in c)
    strength = next(c for c in df.columns if "YS (" in c)
    df = df[df[temperature].between(20, 30) & df[strength].notna()]
    return _composition_task(
        "mpea_yield_strength", "alloy design from composition",
        df["FORMULA"].astype(str).tolist(), df[strength].to_numpy(dtype=float),
        "room-temperature yield strength", "MPa",
        "Measured multi-principal-element alloys (Borg et al., Sci. Data 7:430, 2020).",
        n_train=200,
    )


def _ti(column: str = "YM", name: str = "ti_alloy_youngs_modulus", target: str = "Young's modulus",
        unit: str = "GPa", n_train: int = 120) -> Task:
    import pandas as pd

    df = pd.read_csv(DATA / "alloys" / "ti_alloy_dax-ti-static.csv")
    df = df[df[column].notna()]
    return _composition_task(
        name, "alloy design from composition",
        df["formula"].astype(str).tolist(), df[column].to_numpy(dtype=float),
        target, unit,
        "Measured titanium alloys (Salvador et al., Sci. Data 9:188, 2022).",
        n_train=n_train, min_count=4,
    )


def _mpea_hardness() -> Task:
    import pandas as pd

    df = pd.read_csv(DATA / "alloys" / "MPEA_dataset.csv")
    hardness = next(c for c in df.columns if c.strip() == "PROPERTY: HV")
    df = df[df[hardness].notna()]
    return _composition_task(
        "mpea_hardness", "alloy design from composition",
        df["FORMULA"].astype(str).tolist(), df[hardness].to_numpy(dtype=float),
        "Vickers hardness", "HV",
        "Measured multi-principal-element alloys (Borg et al., Sci. Data 7:430, 2020).",
        n_train=200,
    )


def _matbench() -> Task:
    data = np.load(DATA / "alloys" / "matbench_bulk_shear_features.npz", allow_pickle=False)
    X, y = data["X"].astype(np.float64), data["Y"][:, 0].astype(np.float64)
    return Task(
        name="matbench_log_bulk_modulus",
        application="property screening from composition",
        target="log10 of the DFT bulk modulus K_VRH",
        unit="log10(GPa)",
        X=X,
        y=y,
        feature_names=tuple(f"pc{i}" for i in range(X.shape[1])),
        named_features=False,
        split_kind="random",
        description=(
            "Inputs are 10 principal components, scaled to [0, 1], of composition statistics "
            "(mean and range of atomic weight, atomic radius, melting temperature and "
            "electronegativity). The target is log10 of the Materials Project bulk modulus "
            f"(matbench_log_kvrh, {len(y)} crystals)."
        ),
        _split=_random_split(len(y), 500),
    )


# Experiment E7: pools computed with Thermo-Calc (experiments/e7_calphad_prior/make_tc_data.py).
# data/calphad/systems.json lists every system built so far, its targets, and which of them
# were dropped as degenerate. A system becomes a set of tasks once its pool is complete.


def _calphad_registry() -> dict:
    import json

    path = DATA / "calphad" / "systems.json"
    return json.loads(path.read_text()) if path.exists() else {}


CALPHAD_SYSTEMS = {name: spec for name, spec in _calphad_registry().items() if spec["complete"]}
_CALPHAD_TASKS = {
    f"{system}_{target['name']}": (system, target)
    for system, spec in CALPHAD_SYSTEMS.items() for target in spec["targets"] if not target["dropped"]
}
CALPHAD_GOALS = {name: target["goal"] for name, (_, target) in _CALPHAD_TASKS.items()}  # +1 maximise, -1 minimise
CALPHAD_TASK_NAMES = tuple(_CALPHAD_TASKS)


def calphad_system(task_name: str) -> tuple[str, str]:
    """(system, target) of an E7 task name."""
    if task_name not in _CALPHAD_TASKS:
        raise KeyError(f"{task_name!r} is not a Thermo-Calc task")
    system, target = _CALPHAD_TASKS[task_name]
    return system, target["name"]


def _calphad(task_name: str) -> Task:
    import pandas as pd

    system, target = _CALPHAD_TASKS[task_name]
    spec = CALPHAD_SYSTEMS[system]
    df = pd.read_csv(DATA / "calphad" / f"{system}.csv")
    df = df[df[target["column"]].notna()]  # a quantity Thermo-Calc failed on is empty for that row
    names = tuple(f"x_{el}" for el in spec["elements"])
    return Task(
        name=task_name,
        application="alloy design from composition, computed target",
        target=target["wording"],
        unit=target["unit"],
        X=df[list(names)].to_numpy(dtype=np.float64),
        y=df[target["column"]].to_numpy(dtype=np.float64),
        feature_names=names,
        named_features=True,
        split_kind="random",
        description=(
            f"Inputs are atomic fractions of {', '.join(spec['elements'])} in {spec['alloys']}; each row sums "
            f"to 1. Composition range: {spec['sampling']}. The target is the {target['wording']} in "
            f"{target['unit']}, calculated at 1 atm with the CALPHAD method (Thermo-Calc, {spec['database']} "
            f"database). {len(df)} alloys."
        ),
        _split=_random_split(len(df), len(df) // 2),
    )


@lru_cache(maxsize=None)
def calphad_facts(system: str) -> dict:
    """Calculations for the sub-systems (pure elements, binaries, ternaries) of a system: the
    phase-diagram context. None of its points is a pool composition."""
    import json

    return json.loads((DATA / "calphad" / f"{system}_facts.json").read_text())


_BUILDERS: dict[str, Callable[[], Task]] = {
    "loop_bulk_modulus": lambda: _closed_loop(
        "closed_loop_bm", "ltm_bm_seed_pool.parquet", "loop_bulk_modulus",
        "bulk modulus", "GPa", "the bulk modulus from a Birch-Murnaghan fit",
    ),
    "loop_heat_capacity": lambda: _closed_loop(
        "closed_loop_cp", "ltm_seed_pool_v3.parquet", "loop_heat_capacity",
        "heat capacity at 300 K", "J/g/K", "the phonon heat capacity at 300 K",
    ),
    "mpea_yield_strength": _mpea,
    "ti_alloy_youngs_modulus": _ti,
    "ti_alloy_yield_strength": lambda: _ti("YS", "ti_alloy_yield_strength", "yield strength", "MPa", 100),
    "ti_alloy_hardness": lambda: _ti("HV", "ti_alloy_hardness", "Vickers hardness", "HV", 100),
    "mpea_hardness": _mpea_hardness,
    "matbench_log_bulk_modulus": _matbench,
    **{name: (lambda name=name: _calphad(name)) for name in _CALPHAD_TASKS},
}

TASK_NAMES = tuple(_BUILDERS)


@lru_cache(maxsize=None)
def load_task(name: str) -> Task:
    if name not in _BUILDERS:
        raise KeyError(f"unknown task {name!r}; choose from {', '.join(TASK_NAMES)}")
    return _BUILDERS[name]()
