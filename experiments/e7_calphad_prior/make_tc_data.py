"""E7 data: alloy properties computed with Thermo-Calc, for the written-prior test.

The public alloy tables of E1 may be recalled by a language model. These pools are
computed here with TC-Python and have never been published as tables.

Nine alloy spaces in five databases (`SYSTEMS` below). For each:

  pool    200 to 400 multicomponent compositions (at least four elements present):
          solidus, liquidus, phases at the system's fixed temperature, a transus
          where one is defined, density at the fixed temperature and at 298.15 K
  facts   the same calculation for SUB-systems only: pure elements, binaries and
          ternaries. These are the "phase-diagram information" given to a language
          model and to the no-LLM references. No fact is computed at a composition
          of the pool; `check_no_leak` enforces it.
  export  data/calphad/<system>.csv, <system>_facts.json, systems.json, README.md
          (needs no Thermo-Calc)

    conda activate tcpy
    python experiments/e7_calphad_prior/make_tc_data.py                       # every system, in ORDER
    python experiments/e7_calphad_prior/make_tc_data.py --system ni_superalloy ti_alloy
    python experiments/e7_calphad_prior/make_tc_data.py --stage export        # no Thermo-Calc

Raw results are appended to data/calphad/raw/*.jsonl, one line per composition;
the last line of a key counts. A composition with a failed quantity is tried a
second time on the next run and then kept as it is. Everything is resumable.

A single equilibrium close to an invariant reaction can take minutes or never
return. The calculations therefore run in a worker process that reports what it
is about to solve; when one solve exceeds its time limit the supervisor kills the
worker and its Thermo-Calc engine, writes that point to raw/slow_points.jsonl,
and starts a new worker, which steps around the points listed there. Two
supervisors may run at once on different systems if each is given its own
heartbeat file through the environment variable E7_NAME.
"""

from __future__ import annotations

import argparse
import datetime
import itertools
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

DATA = Path(__file__).resolve().parents[2] / "data" / "calphad"
RAW = DATA / "raw"
PRESSURE = 101325.0
SEED = 0
ORDER_THRESHOLD = 0.05  # an A2/B2 or A1/L12 composition set is "ordered" above this site-fraction difference
ORDERABLE = ("BCC_B2", "FCC_L12", "L12_FCC", "B2_BCC")
SOLUTION_FAMILIES = ("BCC_B2", "BCC_A2", "FCC_L12", "FCC_A1", "HCP_A3")
COARSE = 4.0  # K, width at which a bisection on the liquid fraction stops
WIDEST = 10.0  # K, a boundary known less well than this is recorded as failed
EPS = 1e-6
PROCEDURE = 2  # version of the melting procedure; 1 (trial) bisected to 0.5 K and stalled at invariant reactions
SLOW = RAW / "slow_points.jsonl"
HEARTBEAT = RAW / f"heartbeat_{os.environ.get('E7_NAME', 'main')}.json"
CALC_LIMIT, BUILD_LIMIT = 45.0, 400.0  # seconds allowed for one equilibrium; for starting or building a system

# Melting points used only to choose starting temperatures (SGTE, Dinsdale 1991; C is the
# metastable melting point of graphite). The melting points reported as facts are computed.
TM_GUESS = {"Al": 933.47, "Co": 1768.0, "Cr": 2180.0, "Fe": 1811.0, "Mn": 1519.0, "Ni": 1728.3, "Mo": 2896.0,
            "Nb": 2750.0, "Ta": 3290.0, "Ti": 1941.0, "V": 2183.0, "W": 3695.0, "Zr": 2127.85, "Cu": 1357.77,
            "Hf": 2506.0, "Sn": 505.08, "Mg": 923.0, "Si": 1687.0, "Zn": 692.68, "C": 4765.0}
ELEMENT_DENSITY = {"Al": 2.70, "Co": 8.90, "Cr": 7.19, "Fe": 7.87, "Mn": 7.47, "Ni": 8.91, "Mo": 10.28, "Nb": 8.57,
                   "Ta": 16.65, "Ti": 4.51, "V": 6.11, "W": 19.25, "Zr": 6.51, "Cu": 8.96, "Hf": 13.31}


# -------------------------------------------------------------------- targets
# A target is (name, kind, wording, unit, goal). goal +1: maximise in BO, -1: minimise.
# kind: "solidus", "freezing_range", "transus", or a function of one phase entry that says
# whether the phase counts ("fraction" targets), or "largest".


def family(phase: dict) -> str:
    return phase["phase"].split("#")[0]


def is_liquid(phase: dict) -> bool:
    return family(phase) == "LIQUID"


def is_ordered(phase: dict) -> bool:
    return family(phase) in ORDERABLE and (phase.get("order") or 0.0) > ORDER_THRESHOLD


def is_solution(phase: dict) -> bool:
    """Disordered fcc, bcc or hcp solid solution."""
    return family(phase) in SOLUTION_FAMILIES and not is_ordered(phase)


def is_intermetallic(phase: dict) -> bool:
    return not is_liquid(phase) and not is_solution(phase)


SOLIDUS = ("solidus", "solidus", "equilibrium solidus temperature", "K", +1.0)
FREEZING = ("freezing_range", "freezing_range",
            "equilibrium freezing range (liquidus temperature minus solidus temperature)", "K", -1.0)
INTERMETALLIC = (
    "intermetallic_fraction", is_intermetallic,
    "equilibrium mole fraction, at {T} K, of all phases other than liquid and the disordered fcc, bcc and hcp "
    "solid solutions (that is: sigma, Laves and other intermetallic phases, and ordered B2 or L12)",
    "mole fraction between 0 and 1", -1.0)
LARGEST = (
    "main_phase_fraction", "largest",
    "equilibrium mole fraction, at {T} K, of the single most abundant phase (1 for a single-phase alloy; "
    "two bcc phases of a miscibility gap count as two phases)",
    "mole fraction between 0 and 1", +1.0)
HEA_TARGETS = (SOLIDUS, FREEZING, INTERMETALLIC, LARGEST)

HEA = {"kind": "hea", "step": 0.05, "max": 0.35, "min_present": 4}

SYSTEMS = {
    "cantor_al": {
        "database": "TCHEA8", "elements": ("Al", "Co", "Cr", "Fe", "Mn", "Ni"), "T": 1273.0, "size": 400,
        "sampling": HEA, "targets": HEA_TARGETS, "alloys": "Al-Co-Cr-Fe-Mn-Ni high-entropy alloys"},
    "refractory": {
        "database": "TCHEA8", "elements": ("Mo", "Nb", "Ta", "Ti", "V", "W", "Zr"), "T": 1473.0, "size": 250,
        "sampling": HEA, "targets": HEA_TARGETS, "alloys": "Mo-Nb-Ta-Ti-V-W-Zr refractory high-entropy alloys"},
    "hf_refractory": {
        "database": "TCHEA8", "elements": ("Hf", "Mo", "Nb", "Ta", "Ti", "Zr"), "T": 1273.0, "size": 250,
        "sampling": HEA, "targets": HEA_TARGETS, "alloys": "Hf-Mo-Nb-Ta-Ti-Zr refractory high-entropy alloys"},
    "al_refractory": {
        "database": "TCHEA8", "elements": ("Al", "Cr", "Mo", "Nb", "Ti"), "T": 1273.0, "size": 250,
        "sampling": HEA, "targets": HEA_TARGETS, "alloys": "Al-Cr-Mo-Nb-Ti refractory high-entropy alloys"},
    "cu_ti_3d": {
        "database": "TCHEA8", "elements": ("Co", "Cr", "Cu", "Fe", "Ni", "Ti"), "T": 1173.0, "size": 250,
        "sampling": HEA, "targets": HEA_TARGETS, "alloys": "Co-Cr-Cu-Fe-Ni-Ti high-entropy alloys"},
    "ni_superalloy": {
        "database": "TCNI12", "elements": ("Ni", "Al", "Co", "Cr", "Mo", "Ti", "W"), "T": 1173.0, "size": 250,
        "sampling": {"kind": "balance", "base": "Ni", "base_min": 0.50, "min_present": 4,  # solute: (max, step)
                     "solutes": {"Al": (0.12, 0.02), "Co": (0.20, 0.05), "Cr": (0.20, 0.05), "Mo": (0.06, 0.02),
                                 "Ti": (0.06, 0.02), "W": (0.06, 0.02)}},
        "alloys": "nickel-base superalloys Ni-Al-Co-Cr-Mo-Ti-W",
        "targets": (
            SOLIDUS, FREEZING,
            ("gamma_prime_fraction", lambda p: family(p) == "FCC_L12" and is_ordered(p),
             "equilibrium mole fraction of the ordered L12 phase (gamma prime) at {T} K",
             "mole fraction between 0 and 1", +1.0),
            ("other_phase_fraction", lambda p: not is_liquid(p) and family(p) != "FCC_L12",
             "equilibrium mole fraction, at {T} K, of all phases other than gamma (fcc) and gamma prime (L12): "
             "sigma, mu, P, R, Laves, eta, B2 and bcc",
             "mole fraction between 0 and 1", -1.0))},
    "ti_alloy": {
        "database": "TCTI6", "elements": ("Ti", "Al", "Mo", "Nb", "Sn", "V", "Zr"), "T": 973.0, "size": 250,
        "sampling": {"kind": "balance", "base": "Ti", "base_min": 0.60, "min_present": 4,
                     "solutes": {"Al": (0.12, 0.03), "Mo": (0.09, 0.03), "Nb": (0.12, 0.03), "Sn": (0.04, 0.02),
                                 "V": (0.12, 0.03), "Zr": (0.08, 0.04)}},
        "alloys": "titanium alloys Ti-Al-Mo-Nb-Sn-V-Zr",
        "transus": {"family": "HCP_A3", "floor": 773.0},
        "targets": (
            SOLIDUS, FREEZING,
            ("alpha_transus", "transus",
             "temperature above which no hcp alpha phase is stable at equilibrium (the beta transus when no other "
             "phase is present); reported as 773 K when no alpha is stable at 773 K", "K", -1.0),
            ("alpha_fraction", lambda p: family(p) == "HCP_A3",
             "equilibrium mole fraction of the hcp alpha phase at {T} K", "mole fraction between 0 and 1", -1.0),
            ("intermetallic_fraction", is_intermetallic,
             "equilibrium mole fraction, at {T} K, of all phases other than the disordered bcc (beta) and hcp "
             "(alpha) solid solutions, for example Ti3Al", "mole fraction between 0 and 1", -1.0))},
    "steel": {
        "database": "TCFE10", "elements": ("Fe", "Al", "C", "Cr", "Mn", "Mo", "Ni"), "T": 1173.0, "size": 250,
        "sampling": {"kind": "balance", "base": "Fe", "base_min": 0.50, "min_present": 4,
                     "solutes": {"Al": (0.06, 0.03), "C": (0.02, 0.01), "Cr": (0.24, 0.04), "Mn": (0.20, 0.05),
                                 "Mo": (0.04, 0.02), "Ni": (0.20, 0.04)}},
        "alloys": "high-alloy steels Fe-Al-C-Cr-Mn-Mo-Ni",
        "targets": (
            SOLIDUS, FREEZING,
            ("austenite_fraction", lambda p: family(p) == "FCC_A1",
             "equilibrium mole fraction of austenite (fcc) at {T} K", "mole fraction between 0 and 1", +1.0),
            ("carbide_intermetallic_fraction", is_intermetallic,
             "equilibrium mole fraction, at {T} K, of all phases other than austenite (fcc) and ferrite (bcc): "
             "carbides, sigma, Laves and other intermetallic phases", "mole fraction between 0 and 1", -1.0))},
    "al_alloy": {
        "database": "TCAL9", "elements": ("Al", "Cu", "Mg", "Mn", "Si", "Zn"), "T": 673.0, "size": 250,
        "sampling": {"kind": "balance", "base": "Al", "base_min": 0.85, "min_present": 4,
                     "solutes": {"Cu": (0.04, 0.01), "Mg": (0.04, 0.01), "Mn": (0.01, 0.005), "Si": (0.04, 0.01),
                                 "Zn": (0.04, 0.01)}},
        "alloys": "aluminium alloys Al-Cu-Mg-Mn-Si-Zn",
        "targets": (
            SOLIDUS, FREEZING,
            ("second_phase_fraction", lambda p: not is_liquid(p) and family(p) != "FCC_A1",
             "equilibrium mole fraction, at {T} K, of all solid phases other than the fcc aluminium solid solution "
             "(silicon, Al2Cu, Mg2Si, MgZn2 and other compounds)", "mole fraction between 0 and 1", -1.0))},
}
ORDER = ("cantor_al", "ni_superalloy", "ti_alloy", "refractory", "steel", "al_alloy", "hf_refractory", "cu_ti_3d",
         "al_refractory")
ANCHORS = {  # name -> (elements, fractions); literature values are quoted in the README
    "CoCrFeMnNi": (("Co", "Cr", "Fe", "Mn", "Ni"), (0.2,) * 5),
    "CoCrFeNi": (("Co", "Cr", "Fe", "Ni"), (0.25,) * 4),
    "AlCoCrFeNi": (("Al", "Co", "Cr", "Fe", "Ni"), (0.2,) * 5),
    "MoNbTaW": (("Mo", "Nb", "Ta", "W"), (0.25,) * 4),
    "MoNbTaVW": (("Mo", "Nb", "Ta", "V", "W"), (0.2,) * 5),
    "TiZrNbTa (no Hf)": (("Nb", "Ta", "Ti", "Zr"), (0.25,) * 4),
}


class Unsolved(Exception):
    """An equilibrium that Thermo-Calc could not solve, or not within the time limit."""


def beat(what: dict, allow: float) -> None:
    """Tell the supervisor what is about to be calculated and how long it may take."""
    HEARTBEAT.parent.mkdir(parents=True, exist_ok=True)
    HEARTBEAT.write_text(json.dumps({**what, "allow": allow}))


# ------------------------------------------------------------------ sampling


def sample_pool(n_elements: int, size: int = 400, seed: int = SEED) -> np.ndarray:
    """High-entropy sampling: `size` distinct compositions drawn uniformly, without
    replacement, from all points of the 5 at.% grid with every element at most
    35 at.% and at least four elements present. Integer units of 5 at.% (rows sum to 20)."""

    def parts(k: int, total: int):
        if k == 1:
            if total <= 7:
                yield (total,)
            return
        for first in range(min(7, total) + 1):
            for rest in parts(k - 1, total - first):
                yield (first, *rest)

    grid = np.array([p for p in parts(n_elements, 20) if sum(u > 0 for u in p) >= 4])
    rows = np.random.default_rng(seed).choice(len(grid), size=size, replace=False)
    return grid[np.sort(rows)]


def pool_compositions(system: str) -> list[dict[str, float]]:
    """The pool of a system, in row order: {element: atomic fraction} for every element."""
    spec = SYSTEMS[system]
    elements, sampling = spec["elements"], spec["sampling"]
    if sampling["kind"] == "hea":
        return [{el: int(u) / 20 for el, u in zip(elements, row)} for row in sample_pool(len(elements), spec["size"])]
    # balance: every solute on its own grid from 0 to its maximum, the base element the rest
    base, solutes = sampling["base"], sampling["solutes"]
    levels = [[round(k * step, 4) for k in range(int(round(top / step)) + 1)] for top, step in solutes.values()]
    grid = [combo for combo in itertools.product(*levels)
            if 1 - sum(combo) >= sampling["base_min"] - 1e-9 and sum(c > 0 for c in combo) + 1 >= sampling["min_present"]]
    rows = np.sort(np.random.default_rng(SEED).choice(len(grid), size=spec["size"], replace=False))
    out = []
    for r in rows:
        x = dict(zip(solutes, grid[r]))
        x[base] = round(1 - sum(grid[r]), 4)
        out.append({el: x[el] for el in elements})
    return out


def fact_compositions(system: str) -> list[dict[str, float]]:
    """The sub-system compositions whose calculation is given as context: at most three elements each.

    High-entropy systems: every pure element; every binary at 25, 50 and 75 at.%; every equimolar ternary.
    Balance systems: the pure base element; base + one solute at half and at the whole of that solute's
    range; base + two solutes, each at half its range.
    """
    spec = SYSTEMS[system]
    elements, sampling = spec["elements"], spec["sampling"]
    points: list[dict[str, float]] = []
    if sampling["kind"] == "hea":
        points += [{el: 1.0} for el in elements]
        for a, b in itertools.combinations(elements, 2):
            points += [{a: 1 - xb, b: xb} for xb in (0.25, 0.5, 0.75)]
        points += [{a: 1 / 3, b: 1 / 3, c: 1 / 3} for a, b, c in itertools.combinations(elements, 3)]
    else:
        base, solutes = sampling["base"], sampling["solutes"]
        points.append({base: 1.0})
        for el, (top, _) in solutes.items():
            points += [{base: round(1 - c, 4), el: round(c, 4)} for c in (top / 2, top)]
        for (a, (ta, _)), (b, (tb, _)) in itertools.combinations(solutes.items(), 2):
            points.append({base: round(1 - ta / 2 - tb / 2, 4), a: round(ta / 2, 4), b: round(tb / 2, 4)})
    return points


def label(composition: dict[str, float]) -> str:
    return "".join(f"{el}{composition[el]:.4f}" for el in sorted(composition) if composition[el] > 0)


def check_no_leak(system: str) -> None:
    """No context fact may be a composition of the pool, nor have as many elements as a pool row."""
    pool, facts = pool_compositions(system), fact_compositions(system)
    fewest = min(sum(v > 0 for v in x.values()) for x in pool)
    most = max(sum(v > 0 for v in x.values()) for x in facts)
    if most >= fewest or {label(x) for x in pool} & {label(x) for x in facts}:
        raise SystemExit(f"{system}: a context fact coincides with the pool (facts up to {most} elements, pool from {fewest})")


# ---------------------------------------------------------------- Thermo-Calc


class Engine:
    """One Thermo-Calc session. Systems are built for the present elements only
    (an absent element floored at a tiny fraction makes some equilibria fail)."""

    def __init__(self, session):
        self.session = session
        self._key, self._system = None, None
        self.calcs = 0
        self.slow = {json.loads(line)["tag"] for line in SLOW.read_text().splitlines()} if SLOW.exists() else set()

    def system(self, database: str, elements: tuple[str, ...]):
        if (database, elements) != self._key:
            beat({"build": [database, *elements]}, BUILD_LIMIT)
            builder = self.session.select_database_and_elements(database, list(elements)).deselect_phase("GAS")
            self._system, self._key = builder.get_system(), (database, elements)
        return self._system


class Alloy:
    """One composition. Every call is a global-minimisation equilibrium at one temperature."""

    def __init__(self, engine: Engine, database: str, composition: dict[str, float]):
        from tc_python import ThermodynamicQuantity as TQ

        self.TQ = TQ
        self.engine = engine
        self.elements = tuple(sorted(el for el, x in composition.items() if x > 0))
        self.x = {el: float(composition[el]) for el in self.elements}
        self.label = ("" if database == "TCHEA8" else database + ":") + "".join(f"{el}{self.x[el]:.4f}" for el in self.elements)
        self.system = engine.system(database, self.elements)
        self.dependent = max(self.elements, key=lambda el: self.x[el])
        self.calc = self._new()

    def _new(self):
        calc = self.system.with_single_equilibrium_calculation()
        calc.set_condition(self.TQ.pressure(), PRESSURE)
        for el in self.elements:
            if el != self.dependent:
                calc.set_condition(self.TQ.mole_fraction_of_a_component(el), self.x[el])
        return calc

    def _solve(self, T: float):
        """Result at T. A solve that fails, or that timed out in an earlier worker, is
        retried on a fresh calculation 0.4 K higher, then 0.4 K lower."""
        from tc_python.exceptions import CalculationException

        error = None
        for shift in (0.0, 0.4, -0.4):
            tag = f"{self.label}|eq|{T + shift:.2f}"
            if tag in self.engine.slow:
                error = f"timed out at {T + shift:.2f} K"
                continue
            beat({"tag": tag}, CALC_LIMIT)
            try:
                self.engine.calcs += 1
                self.calc.set_condition(self.TQ.temperature(), T + shift)
                return self.calc.calculate()
            except CalculationException as e:
                error = str(e)[:200]
                self.calc = self._new()
        raise Unsolved(error)

    def fraction(self, T: float, counts) -> float:
        """Summed mole fraction at T of the phases whose family `counts` accepts."""
        r = self._solve(T)
        return float(sum(r.get_value_of(f"NP({p})") for p in r.get_stable_phases() if counts(p.split("#")[0])))

    def liquid(self, T: float) -> float:
        return self.fraction(T, lambda fam: fam == "LIQUID")

    def state(self, T: float) -> dict:
        """Phases (fraction, composition, order parameter) and density at T."""
        r = self._solve(T)
        phases = []
        for name in r.get_stable_phases():
            entry = {
                "phase": name, "fraction": float(r.get_value_of(f"NP({name})")),
                "x": {el: round(float(r.get_value_of(f"X({name},{el})")), 5) for el in self.elements},
            }
            if name.split("#")[0] in ORDERABLE:
                # two substitutional sublattices; equal site fractions mean the disordered A2 / A1 state
                gaps = []
                for el in self.elements:
                    try:
                        gaps.append(abs(float(r.get_value_of(f"Y({name},{el}#1)")) - float(r.get_value_of(f"Y({name},{el}#2)"))))
                    except Exception:  # the element is not on both sublattices
                        continue
                entry["order"] = round(max(gaps), 5) if gaps else 0.0
            entry["kind"] = "liquid" if is_liquid(entry) else "solid solution" if is_solution(entry) else "intermetallic"
            phases.append(entry)
        density = float(r.get_value_of("BM")) / float(r.get_value_of("VM")) * 1e-6  # g/mol / (m3/mol) -> g/cm3
        return {"phases": sorted(phases, key=lambda p: -p["fraction"]), "density_g_cm3": density}

    def _fixed_liquid(self, start_T: float, amount: float) -> float:
        """Temperature at which the liquid amount is `amount` (0 solidus, 1 liquidus),
        solved directly from a converged state at start_T. May be a metastable
        boundary; the caller checks it against global equilibria."""
        from tc_python.exceptions import CalculationException

        tag = f"{self.label}|fixed{amount:.0f}|{start_T:.2f}"
        if tag in self.engine.slow:
            raise Unsolved(f"phase-boundary solve from {start_T:.2f} K timed out")
        beat({"tag": tag}, CALC_LIMIT)
        try:
            calc = self._new()
            self.engine.calcs += 2
            calc.set_condition(self.TQ.temperature(), start_T)
            calc.calculate()
            calc.set_phase_to_fixed("LIQUID", amount)
            calc.remove_condition(self.TQ.temperature())
            return float(calc.calculate().get_value_of("T"))
        except CalculationException as e:
            raise Unsolved(str(e)[:200]) from None

    def _bisect(self, lo: float, hi: float, above, width: float, measure=None) -> tuple[float, float]:
        """Narrow [lo, hi], where `above(measure(T))` is False at lo and True at hi, to
        `width`. A temperature that cannot be solved is stepped around; if that
        fails too the bracket is returned as wide as it is."""
        measure = measure or self.liquid
        while hi - lo > width:
            value = None
            for split in (0.5, 0.35, 0.65):
                mid = lo + split * (hi - lo)
                try:
                    value = measure(mid)
                    break
                except Unsolved:
                    continue
            if value is None:
                break
            if above(value):
                hi = mid
            else:
                lo = mid
        return lo, hi

    def _boundary(self, amount: float, start: float, low, hi: float) -> tuple[float, str]:
        """Liquidus (amount 1) or solidus (amount 0), and how it was obtained.

        1. Solve the phase boundary directly from the state at `start`; accept it if
           global equilibria 1 K below and 1 K above agree.
        2. Otherwise bracket it by bisection on the liquid fraction of global
           equilibria to 4 K (this assumes the fraction rises with temperature),
           solve the phase boundary from the upper end of the bracket, and accept
           it if it lies inside the bracket.
        3. Otherwise report the middle of the bracket.
        """
        above = (lambda f: f >= 1 - EPS) if amount == 1.0 else (lambda f: f > EPS)
        try:
            T = self._fixed_liquid(start, amount)
            if T <= hi + 0.01 and above(self.liquid(T + 1.0)) and not above(self.liquid(T - 1.0)):
                return T, "phase boundary, checked 1 K either side"
        except Unsolved:
            pass
        a, b = self._bisect(low(), hi, above, COARSE)
        if b - a > WIDEST:
            raise Unsolved(f"bracket {a:.1f} to {b:.1f} K could not be narrowed")
        try:
            T = self._fixed_liquid(b, amount)
            if a - 0.01 <= T <= b + 0.01:
                return T, f"phase boundary inside a {b - a:.1f} K bracket"
        except Unsolved:
            pass
        return 0.5 * (a + b), f"middle of a {b - a:.1f} K bracket"

    def solidus_liquidus(self, T_guess_high: float, T_guess_low: float) -> dict:
        """Solidus = highest temperature with no liquid; liquidus = lowest with only liquid."""
        hi = T_guess_high
        while self.liquid(hi) < 1 - EPS:
            hi += 250.0
            if hi > 5500:
                raise Unsolved("no fully liquid state below 5500 K")
        found = []

        def low() -> float:  # a temperature with no liquid, looked for only when a bisection needs it
            if not found:
                lo = T_guess_low
                while self.liquid(lo) > EPS:
                    lo -= 150.0
                    if lo < 300:
                        raise Unsolved("liquid still present at 300 K")
                found.append(lo)
            return found[0]

        liquidus, liquidus_method = self._boundary(1.0, hi, low, hi)
        solidus, solidus_method = self._boundary(0.0, liquidus - 0.5, low, liquidus + 1.0)
        return {"liquidus_K": liquidus, "liquidus_method": liquidus_method,
                "solidus_K": min(solidus, liquidus), "solidus_method": solidus_method}

    def melting_point(self) -> float:
        """Pure element: the temperature at which the stable state becomes liquid, to 0.05 K."""
        lo, hi = 300.0, 4500.0
        while hi - lo > 0.05:
            mid = 0.5 * (lo + hi)
            lo, hi = (lo, mid) if self.liquid(mid) > 0.5 else (mid, hi)
        return round(0.5 * (lo + hi), 2)

    def transus(self, phase_family: str, floor: float, ceiling: float) -> tuple[float, str]:
        """Temperature above which no phase of `phase_family` is stable, by bisection to 2 K
        between `floor` and `ceiling` (assumes the phase, once gone, does not return on heating)."""
        present = lambda T: self.fraction(T, lambda fam: fam == phase_family)  # noqa: E731
        if present(floor) <= EPS:
            return floor, f"no {phase_family} at {floor:.0f} K: reported as {floor:.0f} K"
        if present(ceiling) > EPS:
            raise Unsolved(f"{phase_family} still present at {ceiling:.0f} K")
        a, b = self._bisect(floor, ceiling, lambda f: f <= EPS, 2.0, present)
        if b - a > WIDEST:
            raise Unsolved(f"transus bracket {a:.1f} to {b:.1f} K could not be narrowed")
        return 0.5 * (a + b), f"middle of a {b - a:.1f} K bracket"


# -------------------------------------------------------------------- caching


def all_records(path: Path, melting: bool = True) -> dict[str, dict]:
    """key -> last record of the current procedure, failed ones included, with the number of attempts."""
    out, attempts = {}, {}
    if path.exists():
        for line in path.read_text().splitlines():
            if line.strip():
                record = json.loads(line)
                if not melting or record.get("procedure") == PROCEDURE:
                    attempts[record["key"]] = attempts.get(record["key"], 0) + 1
                    out[record["key"]] = {**record, "attempts": attempts[record["key"]]}
    return out


def read_cache(path: Path, melting: bool = True) -> dict[str, dict]:
    """The records that count as done: without an error, or already tried twice."""
    return {k: v for k, v in all_records(path, melting).items() if not v.get("error") or v["attempts"] >= 2}


def append(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as f:
        f.write(json.dumps({**record, "procedure": PROCEDURE}) + "\n")


def element_key(database: str, element: str) -> str:
    return element if database == "TCHEA8" else f"{database}:{element}"


def melting_point(engine: Engine, database: str, element: str) -> float:
    """Melting point of an element from a one-element system of the database; cached."""
    path = RAW / "elements.jsonl"
    done = read_cache(path, melting=False)
    key = element_key(database, element)
    if key not in done:
        alloy = Alloy(engine, database, {element: 1.0})
        tm = alloy.melting_point()
        solid = alloy.state(298.15)
        record = {"key": key, "melting_point_K": tm, "phase_298K": solid["phases"][0]["phase"],
                  "density_298K_g_cm3": solid["density_g_cm3"]}
        append(path, record)
        print(record, flush=True)
        return tm
    return done[key]["melting_point_K"]


# --------------------------------------------------------------------- stages


def compute_alloy(engine: Engine, spec: dict, composition: dict[str, float]) -> dict:
    """Everything recorded for one composition. Each quantity fails on its own."""
    database, T_fixed = spec["database"], spec["T"]
    alloy = Alloy(engine, database, composition)
    out, errors = {}, {}
    present = [TM_GUESS[el] for el in alloy.elements]
    try:
        if len(alloy.elements) == 1:
            tm = melting_point(engine, database, alloy.elements[0])
            alloy = Alloy(engine, database, composition)  # the engine may have been used for another system
            out.update(solidus_K=tm, liquidus_K=tm, solidus_method="pure element", liquidus_method="pure element")
        else:
            base = spec["sampling"].get("base")
            high = (TM_GUESS[base] + 300.0) if base in alloy.elements else max(present) + 250.0
            out.update(alloy.solidus_liquidus(high, min(min(present), T_fixed) - 100.0))
        out["freezing_range_K"] = out["liquidus_K"] - out["solidus_K"]
    except Unsolved as e:
        errors["melting"] = str(e)
    try:
        state = alloy.state(T_fixed)
        out["phases"] = state["phases"]
        out["density_T_g_cm3"] = state["density_g_cm3"]
    except Unsolved as e:
        errors["phases"] = str(e)
    if "transus" in spec:
        try:
            if "solidus_K" not in out:
                raise Unsolved("no solidus to bound the transus")
            rule = spec["transus"]
            out["transus_K"], out["transus_method"] = alloy.transus(rule["family"], rule["floor"], out["solidus_K"] - 5.0)
        except Unsolved as e:
            errors["transus"] = str(e)
    try:
        cold = alloy.state(298.15)
        out["density_298K_g_cm3"] = cold["density_g_cm3"]
        out["phases_298K"] = [p["phase"] for p in cold["phases"]]
    except Unsolved as e:
        errors["density_298K"] = str(e)
    out["failed"] = errors
    return out


def stage_anchors(engine: Engine) -> None:
    path = RAW / "anchors.jsonl"
    done = read_cache(path)
    for name, (elements, x) in ANCHORS.items():
        if name in done:
            continue
        T = 1273.0 if set(elements) & {"Co", "Fe", "Ni"} else 1473.0
        spec = {"database": "TCHEA8", "T": T, "sampling": HEA}
        record = {"key": name, "composition": dict(zip(elements, x)), "T_fixed_K": T,
                  **compute_alloy(engine, spec, dict(zip(elements, x)))}
        append(path, record)
        print(name, {k: v for k, v in record.items() if k.endswith("_K") or k == "failed"}, flush=True)


def run_points(engine: Engine, system: str, what: str, points: list[tuple[str, dict]], limit: int | None) -> None:
    """Compute and cache the compositions `points` = [(key, composition)] of the pool or of the facts."""
    spec, path = SYSTEMS[system], RAW / f"{system}_{what}.jsonl"
    done = read_cache(path)
    # one Thermo-Calc system per set of present elements: do each set in one go
    order = sorted(range(len(points)), key=lambda i: (len([v for v in points[i][1].values() if v > 0]),
                                                      tuple(sorted(el for el, v in points[i][1].items() if v > 0))))
    todo = [i for i in order if points[i][0] not in done][:limit]
    print(f"{system} {what}: {len(done)} done, {len(todo)} to do", flush=True)
    for count, i in enumerate(todo, 1):
        key, composition = points[i]
        start, before = time.time(), engine.calcs
        result = compute_alloy(engine, spec, composition)
        record = {"key": key, "row": i, "composition": composition, **result,
                  "equilibria": engine.calcs - before, "seconds": round(time.time() - start, 1)}
        if result["failed"]:
            record["error"] = result["failed"]
        append(path, record)
        print(f"[{count}/{len(todo)}] {key} solidus {result.get('solidus_K', float('nan')):.1f} "
              f"liquidus {result.get('liquidus_K', float('nan')):.1f} "
              f"{[(p['phase'], round(p['fraction'], 2)) for p in result.get('phases', [])][:4]} "
              f"{record['equilibria']} equilibria {record['seconds']} s {result['failed'] or ''}", flush=True)


def stage_system(engine: Engine, system: str, limit: int | None) -> None:
    check_no_leak(system)
    run_points(engine, system, "facts", [(label(x), x) for x in fact_compositions(system)], limit)
    run_points(engine, system, "pool", [(f"{system}-{i:03d}", x) for i, x in enumerate(pool_compositions(system))], limit)


# --------------------------------------------------------------------- export


def targets_of(spec: dict, record: dict) -> dict[str, float | None]:
    """The system's targets for one calculated composition (None where the calculation failed)."""
    out = {}
    for name, kind, *_ in spec["targets"]:
        if kind == "solidus":
            value = record.get("solidus_K")
        elif kind == "freezing_range":
            value = record.get("freezing_range_K")
        elif kind == "transus":
            value = record.get("transus_K")
        elif "phases" not in record:
            value = None
        elif kind == "largest":
            value = max((p["fraction"] for p in record["phases"] if not is_liquid(p)), default=0.0)
        else:
            value = sum(p["fraction"] for p in record["phases"] if kind(p))
        out[name] = None if value is None else round(float(value), 1 if kind in ("solidus", "freezing_range", "transus") else 4)
    return out


def slim_phases(record: dict) -> list[dict]:
    return [{"phase": p["phase"], "fraction": round(p["fraction"], 4), "kind": p["kind"],
             **({"order": p["order"]} if "order" in p else {})} for p in record.get("phases", [])]


def sampling_text(spec: dict) -> str:
    s = spec["sampling"]
    if s["kind"] == "hea":
        return ("every element between 0 and 35 at.% on a 5 at.% grid, at least four elements present")
    ranges = ", ".join(f"{el} 0 to {100 * top:g} (step {100 * step:g})" for el, (top, step) in s["solutes"].items())
    return (f"{s['base']} is the balance and at least {100 * s['base_min']:g} at.%; solutes in at.%: {ranges}; "
            f"at least {s['min_present']} elements present")


def stage_export(tc_version: str | None = None) -> None:
    import pandas as pd

    info_path = RAW / "run_info.json"
    info = json.loads(info_path.read_text()) if info_path.exists() else {}
    if tc_version:
        info.update(tc_python_version=tc_version, last_calculation_date=datetime.date.today().isoformat())
        info_path.write_text(json.dumps(info, indent=1) + "\n")
    registry, summary = {}, {}
    for system in ORDER:
        spec = SYSTEMS[system]
        check_no_leak(system)
        elements, T = spec["elements"], int(spec["T"])
        pool = pool_compositions(system)
        records = all_records(RAW / f"{system}_pool.jsonl")
        fact_points = fact_compositions(system)
        fact_records = all_records(RAW / f"{system}_facts.jsonl")
        if not records:
            continue
        rows = []
        for i, x in enumerate(pool):
            r = records.get(f"{system}-{i:03d}")
            if r is None:
                continue
            assert label(r["composition"]) == label(x), f"{system} row {i}: cached composition differs from the sampler"
            row = {"id": r["key"], **{f"x_{el}": x[el] for el in elements}}
            for column in ("solidus_K", "liquidus_K", "freezing_range_K", "transus_K"):
                if column != "transus_K" or "transus" in spec:
                    row[column] = round(r[column], 1) if column in r else np.nan
            for name, value in targets_of(spec, r).items():
                if name not in ("solidus", "freezing_range"):
                    row[name] = np.nan if value is None else value
            row["liquid_fraction"] = round(sum(p["fraction"] for p in r["phases"] if is_liquid(p)), 4) if "phases" in r else np.nan
            row["density_fixedT_g_cm3"] = round(r["density_T_g_cm3"], 4) if "density_T_g_cm3" in r else np.nan
            row["density_298K_g_cm3"] = round(r["density_298K_g_cm3"], 4) if "density_298K_g_cm3" in r else np.nan
            row["phases_fixedT"] = json.dumps(slim_phases(r))
            row["melting_method"] = "; ".join(
                f"{k.split('_')[0]}: {r[k]}" for k in ("solidus_method", "liquidus_method", "transus_method") if k in r)
            rows.append(row)
        table = pd.DataFrame(rows)
        complete = len(table) == len(pool) and all(label(x) in fact_records for x in fact_points)
        table.to_csv(DATA / f"{system}.csv", index=False)

        targets = []
        for name, kind, wording, unit, goal in spec["targets"]:
            column = {"solidus": "solidus_K", "freezing_range": "freezing_range_K", "transus": "transus_K"}.get(kind, name) \
                if isinstance(kind, str) else name
            values = table[column].dropna()
            share = float((values == values.mode().iloc[0]).mean()) if len(values) else 1.0
            reason = None
            if len(values) < 0.9 * len(table):
                reason = f"computed for only {len(values)} of {len(table)} rows"
            elif share > 0.8:
                reason = f"{100 * share:.0f}% of the pool has the same value ({values.mode().iloc[0]:g})"
            targets.append({"name": name, "column": column, "wording": wording.format(T=T), "unit": unit, "goal": goal,
                            "rows": int(len(values)), "share_at_most_common_value": round(share, 3),
                            "min": float(values.min()) if len(values) else None,
                            "median": float(values.median()) if len(values) else None,
                            "max": float(values.max()) if len(values) else None, "dropped": reason})
        failed = {}
        for r in records.values():
            for what in r.get("failed", {}):
                failed[what] = failed.get(what, 0) + 1
        fact_failed = {k: r["failed"] for k, r in fact_records.items() if r.get("failed")}
        registry[system] = {
            "database": spec["database"], "elements": list(elements), "fixed_temperature_K": spec["T"],
            "alloys": spec["alloys"], "sampling": sampling_text(spec), "kind": spec["sampling"]["kind"],
            "base": spec["sampling"].get("base"), "pool_size": len(pool), "rows": int(len(table)),
            "complete": bool(complete), "targets": targets,
        }
        summary[system] = {
            "rows": len(table), "sampled": len(pool), "failed": failed, "complete": complete,
            "bracket": int(table["melting_method"].str.contains("bracket").sum()),
            "liquid_at_T": int((table["liquid_fraction"] > 0).sum()),
            "equilibria": int(sum(r.get("equilibria", 0) for r in records.values())),
            "seconds": float(sum(r.get("seconds", 0) for r in records.values())
                             + sum(r.get("seconds", 0) for r in fact_records.values())),
            "facts": f"{sum(label(x) in fact_records for x in fact_points)} of {len(fact_points)}",
            "facts_failed": fact_failed,
        }

        facts = {
            "system": system, "database": spec["database"], "pressure_Pa": PRESSURE, "fixed_temperature_K": spec["T"],
            "elements": list(elements), "kind": spec["sampling"]["kind"], "base": spec["sampling"].get("base"),
            "solute_max": {el: top for el, (top, _) in spec["sampling"].get("solutes", {}).items()},
            "note": ("Sub-systems only: pure elements, binaries and ternaries. No point has more than three elements; "
                     "every pool composition has at least four. Gas phase excluded. 'order' is the largest "
                     "site-fraction difference between the two sublattices of an A2/B2 or A1/L12 phase; above "
                     f"{ORDER_THRESHOLD} the phase is counted as ordered."),
            "points": [],
        }
        for x in fact_points:
            r = fact_records.get(label(x))
            if r is None:
                continue
            present = {el: x[el] for el in elements if x.get(el, 0) > 0}
            facts["points"].append({
                "x": present, "n_elements": len(present),
                "solidus_K": round(r["solidus_K"], 1) if "solidus_K" in r else None,
                "liquidus_K": round(r["liquidus_K"], 1) if "liquidus_K" in r else None,
                **({"transus_K": round(r["transus_K"], 1) if "transus_K" in r else None} if "transus" in spec else {}),
                "phases": slim_phases(r), "targets": targets_of(spec, r),
            })
        old = all_records(RAW / f"{system}_binaries.jsonl")  # first build: liquidus on a 5 at.% grid along each binary
        if old:
            facts["binary_liquidus_minimum"] = {
                key: {"K": b["liquidus_min_K"], "at_pct_second": b["liquidus_min_at_pct_b"]} for key, b in old.items()}
        (DATA / f"{system}_facts.json").write_text(json.dumps(facts, indent=1) + "\n")
    (DATA / "systems.json").write_text(json.dumps(registry, indent=1) + "\n")
    write_readme(registry, summary, info)
    for system, s in summary.items():
        print(system, s, [(t["name"], t["dropped"]) for t in registry[system]["targets"]], flush=True)


def write_readme(registry: dict, summary: dict, info: dict) -> None:
    elements = all_records(RAW / "elements.jsonl", melting=False)
    anchors = all_records(RAW / "anchors.jsonl")
    lines = [
        "# Thermo-Calc-computed alloy pools (experiment E7)",
        "",
        "Built by `experiments/e7_calphad_prior/make_tc_data.py`; nothing here was copied from a sibling repo.",
        "This file is rewritten by `--stage export`; it describes what is on disk now.",
        "",
        f"- Software: Thermo-Calc 2025b through TC-Python {info.get('tc_python_version', '?')}, on this machine.",
        "- Databases: TCHEA8, TCNI12, TCTI6, TCFE10, TCAL9 as shipped with Thermo-Calc 2025b. The minor version of a "
        "database is not exposed by TC-Python and is not recorded.",
        f"- Last calculation: {info.get('last_calculation_date', '?')}.",
        f"- Conditions: {PRESSURE:.0f} Pa, one mole of atoms, global minimisation, default phases of the database "
        "for the elements present, **gas phase removed** (with it, Mn-bearing melts boil below 3,100 K and no "
        "liquidus exists in the sense meant here).",
        "- Each composition is calculated in the system of its present elements only.",
        f"- Sampling: all compositions allowed by a system's rule were enumerated and its pool drawn without "
        f"replacement with `numpy.random.default_rng({SEED})`.",
        "",
        "## Systems",
        "",
        "| System | Database | Elements | Fixed T, K | Sampling rule | Pool | Status |",
        "|---|---|---|---|---|---|---|",
    ]
    for name, s in registry.items():
        status = "complete" if s["complete"] else f"**in progress**: {s['rows']} of {s['pool_size']} rows, facts {summary[name]['facts']}"
        lines.append(f"| `{name}` | {s['database']} | {'-'.join(s['elements'])} | {s['fixed_temperature_K']:.0f} | {s['sampling']} "
                     f"| {s['pool_size']} | {status} |")
    missing = [name for name in ORDER if name not in registry]
    if missing:
        lines += ["", "Not started yet: " + ", ".join(f"`{m}`" for m in missing) + "."]
    lines += [
        "", "## Targets", "",
        "A target is dropped (not registered as a task) when more than 80% of the pool has the same value or it "
        "computed for fewer than 90% of the rows.", "",
        "| System | Target | Unit | Goal in BO | Rows | Min | Median | Max | Share at the most common value | Dropped |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for name, s in registry.items():
        for t in s["targets"]:
            number = lambda v: "" if v is None else f"{v:.4g}"  # noqa: E731
            lines.append(f"| `{name}` | `{t['name']}`: {t['wording']} | {t['unit'].split(' ')[0]} | "
                         f"{'maximise' if t['goal'] > 0 else 'minimise'} | {t['rows']} | {number(t['min'])} | "
                         f"{number(t['median'])} | {number(t['max'])} | {t['share_at_most_common_value']:.2f} | {t['dropped'] or ''} |")
    lines += [
        "", "## Files", "",
        "- `<system>.csv`: one row per pool composition. `x_<element>` atomic fractions; `solidus_K`, `liquidus_K`, "
        "`freezing_range_K`; the fraction targets of the system; `liquid_fraction` at the fixed temperature; "
        "`density_fixedT_g_cm3` and `density_298K_g_cm3` (mass / molar volume of the equilibrium state; the 298 K "
        "value is the full equilibrium assemblage, which a real alloy does not reach, and is not used as a task); "
        "`phases_fixedT`, JSON with every stable phase, its fraction, group and order parameter, so the grouping "
        "can be audited; `melting_method`.",
        "- `<system>_facts.json`: the sub-system calculations given as context (below).",
        "- `systems.json`: the registry read by `src/wsp/tasks.py`.",
        "- `raw/`: every calculation as it was returned, one JSON line per composition, and `slow_points.jsonl`, "
        "the equilibria that exceeded the time limit.",
        "",
        "**Solidus and liquidus.** Each is first solved directly as a phase boundary (liquid fixed at amount 0 or 1, "
        "temperature free) and accepted only if global equilibria 1 K below and 1 K above agree with it. Otherwise "
        "it is bracketed by bisection on the liquid fraction of global equilibria to 4 K (assuming the liquid "
        "fraction rises with temperature) and solved inside the bracket; if that fails the middle of the bracket "
        "is reported. `melting_method` says which.",
        "",
        "**Ordered or disordered.** The databases describe A2/B2 and A1/L1₂ with one phase each. A composition set "
        f"is counted as ordered when the site fractions of its two sublattices differ by more than {ORDER_THRESHOLD} "
        "for some element. The threshold is a convention; the order parameter is kept so the grouping can be redone.",
        "",
        "**Sub-system facts and the no-leak rule.** The context given to a language model, and to the no-LLM "
        "references, is computed only for pure elements, binaries and ternaries: for the high-entropy systems every "
        "pure element, every binary at 25, 50 and 75 at.%, and every equimolar ternary; for the balance systems the "
        "pure base element, the base with one solute at half and the whole of its range, and the base with two "
        "solutes each at half its range. Every pool composition has at least four elements, so no fact can be a "
        "pool composition; `check_no_leak` stops the build otherwise and `tests/test_calphad.py` checks the files.",
        "",
        "## What was built",
        "",
        "| System | Rows in CSV | Failed quantities (rows) | Melting from a bracket (rows) | Rows with liquid at fixed T | Facts computed | Facts with a failed quantity | Equilibria (pool) | Hours |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for system, s in summary.items():
        lines.append(
            f"| `{system}` | {s['rows']} of {s['sampled']} | {s['failed'] or 'none'} | {s['bracket']} | {s['liquid_at_T']} "
            f"| {s['facts']} | {len(s['facts_failed']) or 'none'} | {s['equilibria']:,} | {s['seconds'] / 3600:.2f} |")
    lines += ["", "A failed quantity is left empty in the CSV; the row is kept for the quantities that did compute.", "",
              "## Anchor checks", "",
              "Melting points of the elements from a one-element system of the database, against the SGTE values "
              "(Dinsdale, Calphad 15:317, 1991), and the density at 298.15 K against handbook values:", "",
              "| Database | Element | Melting point here, K | SGTE, K | Density at 298 K here, g/cm³ | Handbook |",
              "|---|---|---|---|---|---|"]
    for key in sorted(elements, key=lambda k: (":" in k, k)):
        e = elements[key]
        database, el = key.split(":") if ":" in key else ("TCHEA8", key)
        lines.append(f"| {database} | {el} | {e['melting_point_K']:.1f} | {TM_GUESS[el]:.1f} | {e['density_298K_g_cm3']:.2f} "
                     f"| {ELEMENT_DENSITY.get(el, float('nan')):.2f} |")
    lines += ["", "Equiatomic alloys (TCHEA8):", "",
              "| Alloy | Solidus, K | Liquidus, K | Phases at fixed T (fraction) | Density 298 K, g/cm³ | Failed |",
              "|---|---|---|---|---|---|"]
    for name, a in anchors.items():
        phases = ", ".join(f"{p['phase']} {'ordered ' if is_ordered(p) else ''}{p['fraction']:.2f}" for p in a.get("phases", []))
        lines.append(f"| {name} | {a.get('solidus_K', float('nan')):.0f} | {a.get('liquidus_K', float('nan')):.0f} "
                     f"| {int(a['T_fixed_K'])} K: {phases} | {a.get('density_298K_g_cm3', float('nan')):.2f} | {a.get('failed') or ''} |")
    lines += ["", ANCHOR_NOTES, ""]
    (DATA / "README.md").write_text("\n".join(lines))


ANCHOR_NOTES = """Literature values for comparison (not computed here):

- CoCrFeMnNi: melting interval measured by DTA about 1,553 to 1,613 K (Laplanche et al., Acta Mater. 2016 report a
  solidus near 1,562 K); single-phase FCC at 1,273 K. Density about 7.9 to 8.0 g/cm³.
- CoCrFeNi: single-phase FCC, melting near 1,690 to 1,720 K.
- AlCoCrFeNi: A2 + B2 at high temperature, with sigma and FCC appearing at intermediate temperatures in
  experiments; melting near 1,620 to 1,680 K.
- MoNbTaW: single-phase BCC; rule-of-mixtures melting point 3,158 K; reported density 13.75 g/cm³ (Senkov et al.,
  Intermetallics 2010). MoNbTaVW: single-phase BCC, 12.36 g/cm³, rule-of-mixtures melting point 2,963 K.

These literature numbers are quoted from memory of the papers and were not re-checked against the sources in this run."""


# ----------------------------------------------------------------- supervisor


def run_stages(stage: str, systems: tuple[str, ...], limit: int | None) -> None:
    """The Thermo-Calc stages, in one session (the worker process)."""
    import tc_python
    from tc_python import LoggingPolicy, TCPython

    beat({"start": "session"}, BUILD_LIMIT)
    with TCPython(logging_policy=LoggingPolicy.NONE) as session:
        engine = Engine(session)
        if stage == "all":
            stage_anchors(engine)
        for system in systems:
            stage_system(engine, system, limit)
            beat({"export": system}, BUILD_LIMIT)
            stage_export(getattr(tc_python, "__version__", None))


def supervise(argv: list[str]) -> None:
    """Run the worker; kill and restart it whenever one solve exceeds its time limit."""
    stalls = 0
    while True:
        beat({"start": "worker"}, BUILD_LIMIT)
        worker = subprocess.Popen([sys.executable, "-u", __file__, *argv, "--worker"], start_new_session=True)
        while worker.poll() is None:
            time.sleep(1.0)
            try:
                state = json.loads(HEARTBEAT.read_text())
            except (OSError, ValueError):
                continue  # caught mid-write
            if time.time() - HEARTBEAT.stat().st_mtime <= state["allow"]:
                continue
            os.killpg(worker.pid, signal.SIGKILL)  # the worker and its Thermo-Calc engine
            worker.wait()
            if "tag" in state:
                append(SLOW, {"tag": state["tag"], "limit_s": state["allow"], "date": datetime.date.today().isoformat()})
                print(f"TIMEOUT {state['tag']}: worker restarted", flush=True)
                stalls = 0
            else:
                stalls += 1
                print(f"TIMEOUT while {state}: worker restarted ({stalls})", flush=True)
            break
        else:
            if worker.returncode == 0:
                return
            stalls += 1
            print(f"worker exited with code {worker.returncode} ({stalls})", flush=True)
        if stalls >= 3:
            raise SystemExit("the worker failed three times in a row without reaching a calculation")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--stage", choices=("all", "export"), default="all")
    parser.add_argument("--system", nargs="+", choices=ORDER, default=list(ORDER))
    parser.add_argument("--limit", type=int, default=None, help="stop each stage of a system after this many compositions")
    parser.add_argument("--worker", action="store_true", help="internal: run the calculations in this process")
    args = parser.parse_args()
    if args.worker:
        run_stages(args.stage, tuple(args.system), args.limit)
    elif args.stage == "export":
        stage_export()
    else:
        supervise(sys.argv[1:])
        stage_export()


if __name__ == "__main__":
    main()
