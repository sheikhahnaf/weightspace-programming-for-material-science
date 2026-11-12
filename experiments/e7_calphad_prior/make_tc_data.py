"""E7 data: alloy properties computed with Thermo-Calc, for the written-prior test.

The public alloy tables of E1 may be recalled by a language model. These pools are
computed here with TC-Python and have never been published as tables.

Two systems, database TCHEA8, 1 atm, gas phase excluded:

  cantor_al    Al-Co-Cr-Fe-Mn-Ni        phase fractions at 1273 K
  refractory   Mo-Nb-Ta-Ti-V-W-Zr       phase fractions at 1473 K

Stages (each is cached and resumable; one Thermo-Calc process, one thread of work):

  elements   melting point of every element, from a one-element system
  anchors    equiatomic reference alloys, for checking against the literature
  pool       400 compositions per system: solidus, liquidus, phases at the fixed
             temperature, density at the fixed temperature and at 298.15 K
  binaries   for every constituent binary: solidus and liquidus at 25/50/75 at.%,
             the liquidus on a 5 at.% grid and its minimum, phases at the fixed
             temperature at 25/50/75 at.%. No multicomponent data.
  export     data/calphad/<system>.csv, <system>_binaries.json, README.md
             (needs no Thermo-Calc)

    conda activate tcpy
    python experiments/e7_calphad_prior/make_tc_data.py            # every stage
    python experiments/e7_calphad_prior/make_tc_data.py --stage pool --system cantor_al --limit 10

Raw results are appended to data/calphad/raw/*.jsonl, one line per calculation
target; the last line of a key counts. A line with an error, or written by an
earlier version of the melting procedure (`procedure` below), is redone on the
next run.

A single equilibrium close to an invariant reaction can take minutes or never
return. The calculations therefore run in a worker process that reports what it
is about to solve; when one solve exceeds its time limit the supervisor kills the
worker and its Thermo-Calc engine, writes that point to raw/slow_points.jsonl,
and starts a new worker, which steps around the points listed there.
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
DATABASE = "TCHEA8"
PRESSURE = 101325.0
SYSTEMS = {
    "cantor_al": {"elements": ("Al", "Co", "Cr", "Fe", "Mn", "Ni"), "T": 1273.0},
    "refractory": {"elements": ("Mo", "Nb", "Ta", "Ti", "V", "W", "Zr"), "T": 1473.0},
}
ANCHORS = {  # name -> (elements, fractions); literature values are quoted in the README
    "CoCrFeMnNi": (("Co", "Cr", "Fe", "Mn", "Ni"), (0.2,) * 5),
    "CoCrFeNi": (("Co", "Cr", "Fe", "Ni"), (0.25,) * 4),
    "AlCoCrFeNi": (("Al", "Co", "Cr", "Fe", "Ni"), (0.2,) * 5),
    "MoNbTaW": (("Mo", "Nb", "Ta", "W"), (0.25,) * 4),
    "MoNbTaVW": (("Mo", "Nb", "Ta", "V", "W"), (0.2,) * 5),
    "TiZrNbTa (no Hf)": (("Nb", "Ta", "Ti", "Zr"), (0.25,) * 4),
}
POOL_SIZE, GRID, MAX_UNITS, MIN_PRESENT, SEED = 400, 20, 7, 4, 0  # 5 at.% grid, each element 0 to 35 at.%
ORDER_THRESHOLD = 0.05  # a BCC_B2 or FCC_L12 composition set is "ordered" above this site-fraction difference
SOLUTION_FAMILIES = ("BCC_B2", "FCC_L12", "HCP_A3")
COARSE = 4.0  # K, width at which a bisection on the liquid fraction stops
WIDEST = 10.0  # K, a boundary known less well than this is recorded as failed
EPS = 1e-6
PROCEDURE = 2  # version of the melting procedure; 1 (trial) bisected to 0.5 K and stalled at invariant reactions
HEARTBEAT, SLOW = RAW / "heartbeat.json", RAW / "slow_points.jsonl"
CALC_LIMIT, BUILD_LIMIT = 45.0, 300.0  # seconds allowed for one equilibrium; for starting or building a system


class Unsolved(Exception):
    """An equilibrium that Thermo-Calc could not solve, or not within the time limit."""


def beat(what: dict, allow: float) -> None:
    """Tell the supervisor what is about to be calculated and how long it may take."""
    HEARTBEAT.parent.mkdir(parents=True, exist_ok=True)
    HEARTBEAT.write_text(json.dumps({**what, "allow": allow}))


# ------------------------------------------------------------------ sampling


def sample_pool(n_elements: int, size: int = POOL_SIZE, seed: int = SEED) -> np.ndarray:
    """`size` distinct compositions drawn uniformly, without replacement, from all
    points of the 5 at.% grid with every element at most 35 at.% and at least four
    elements present. Returned as integer units of 5 at.% (rows sum to 20)."""

    def parts(k: int, total: int):
        if k == 1:
            if total <= MAX_UNITS:
                yield (total,)
            return
        for first in range(min(MAX_UNITS, total) + 1):
            for rest in parts(k - 1, total - first):
                yield (first, *rest)

    grid = np.array([p for p in parts(n_elements, GRID) if sum(u > 0 for u in p) >= MIN_PRESENT])
    rows = np.random.default_rng(seed).choice(len(grid), size=size, replace=False)
    return grid[np.sort(rows)]


# ---------------------------------------------------------------- Thermo-Calc


class Engine:
    """One Thermo-Calc session. Systems are built for the present elements only
    (an absent element floored at a tiny fraction makes some equilibria fail)."""

    def __init__(self, session):
        self.session = session
        self._key, self._system = None, None
        self.calcs = 0
        self.slow = {json.loads(line)["tag"] for line in SLOW.read_text().splitlines()} if SLOW.exists() else set()

    def system(self, elements: tuple[str, ...]):
        if elements != self._key:
            beat({"build": list(elements)}, BUILD_LIMIT)
            builder = self.session.select_database_and_elements(DATABASE, list(elements)).deselect_phase("GAS")
            self._system, self._key = builder.get_system(), elements
        return self._system


class Alloy:
    """One composition. Every call is a global-minimisation equilibrium at one temperature."""

    def __init__(self, engine: Engine, composition: dict[str, float]):
        from tc_python import ThermodynamicQuantity as TQ

        self.TQ = TQ
        self.engine = engine
        self.elements = tuple(sorted(el for el, x in composition.items() if x > 0))
        self.x = {el: float(composition[el]) for el in self.elements}
        self.label = "".join(f"{el}{self.x[el]:.2f}" for el in self.elements)
        self.system = engine.system(self.elements)
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

    def liquid(self, T: float) -> float:
        r = self._solve(T)
        return float(sum(r.get_value_of(f"NP({p})") for p in r.get_stable_phases() if p.startswith("LIQUID")))

    def state(self, T: float) -> dict:
        """Phases (fraction, composition, order parameter) and density at T."""
        r = self._solve(T)
        phases = []
        for name in r.get_stable_phases():
            family = name.split("#")[0]
            entry = {
                "phase": name, "fraction": float(r.get_value_of(f"NP({name})")),
                "x": {el: round(float(r.get_value_of(f"X({name},{el})")), 5) for el in self.elements},
            }
            if family in ("BCC_B2", "FCC_L12"):
                # two substitutional sublattices; equal site fractions mean the disordered A2 / A1 state
                entry["order"] = round(max(
                    abs(float(r.get_value_of(f"Y({name},{el}#1)")) - float(r.get_value_of(f"Y({name},{el}#2)")))
                    for el in self.elements), 5) if len(self.elements) > 1 else 0.0
            entry["kind"] = kind(family, entry.get("order"))
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

    def _bisect(self, lo: float, hi: float, above, width: float) -> tuple[float, float]:
        """Narrow [lo, hi], where `above(liquid fraction)` is False at lo and True at hi,
        to `width`. A temperature that cannot be solved is stepped around; if that
        fails too the bracket is returned as wide as it is."""
        while hi - lo > width:
            fraction = None
            for split in (0.5, 0.35, 0.65):
                mid = lo + split * (hi - lo)
                try:
                    fraction = self.liquid(mid)
                    break
                except Unsolved:
                    continue
            if fraction is None:
                break
            if above(fraction):
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
            if hi > 5000:
                raise Unsolved("no fully liquid state below 5000 K")
        found = []

        def low() -> float:  # a temperature with no liquid, looked for only when a bisection needs it
            if not found:
                lo = T_guess_low
                while self.liquid(lo) > EPS:
                    lo -= 150.0
                    if lo < 350:
                        raise Unsolved("liquid still present at 350 K")
                found.append(lo)
            return found[0]

        liquidus, liquidus_method = self._boundary(1.0, hi, low, hi)
        solidus, solidus_method = self._boundary(0.0, liquidus - 0.5, low, liquidus + 1.0)
        return {"liquidus_K": liquidus, "liquidus_method": liquidus_method,
                "solidus_K": min(solidus, liquidus), "solidus_method": solidus_method}


def kind(family: str, order: float | None) -> str:
    """Grouping used for the two phase-fraction targets."""
    if family == "LIQUID":
        return "liquid"
    if family in SOLUTION_FAMILIES and (order is None or order <= ORDER_THRESHOLD):
        return "solid solution"
    return "intermetallic"


def fractions_by_kind(phases: list[dict]) -> dict[str, float]:
    out = {"liquid": 0.0, "solid solution": 0.0, "intermetallic": 0.0}
    for p in phases:
        out[p["kind"]] += p["fraction"]
    return out


# -------------------------------------------------------------------- caching


def all_records(path: Path, melting: bool = True) -> dict[str, dict]:
    """key -> last record of the current procedure, failed ones included."""
    out = {}
    if path.exists():
        for line in path.read_text().splitlines():
            if line.strip():
                record = json.loads(line)
                if not melting or record.get("procedure") == PROCEDURE:
                    out[record["key"]] = record
    return out


def read_cache(path: Path, melting: bool = True) -> dict[str, dict]:
    """The records that count as done: a record with an error does not."""
    return {k: v for k, v in all_records(path, melting).items() if not v.get("error")}


def append(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as f:
        f.write(json.dumps({**record, "procedure": PROCEDURE}) + "\n")


def melting_points() -> dict[str, float]:
    return {k: v["melting_point_K"] for k, v in read_cache(RAW / "elements.jsonl", melting=False).items()}


# --------------------------------------------------------------------- stages


def stage_elements(engine: Engine) -> None:
    path = RAW / "elements.jsonl"
    done = read_cache(path, melting=False)
    for el in sorted({el for s in SYSTEMS.values() for el in s["elements"]}):
        if el in done:
            continue
        alloy = Alloy(engine, {el: 1.0})
        lo, hi = 400.0, 4500.0
        while hi - lo > 0.05:
            mid = 0.5 * (lo + hi)
            lo, hi = (lo, mid) if alloy.liquid(mid) > 0.5 else (mid, hi)
        solid = alloy.state(298.15)
        record = {"key": el, "melting_point_K": round(0.5 * (lo + hi), 2),
                  "phase_298K": solid["phases"][0]["phase"], "density_298K_g_cm3": solid["density_g_cm3"]}
        append(path, record)
        print(record, flush=True)


def compute_alloy(engine: Engine, composition: dict[str, float], T_fixed: float, tm: dict[str, float]) -> dict:
    """Everything recorded for one composition. Each quantity fails on its own."""
    alloy = Alloy(engine, composition)
    out, errors = {}, {}
    present = [tm[el] for el in alloy.elements]
    try:
        out.update(alloy.solidus_liquidus(max(present) + 250.0, min(min(present), T_fixed) - 100.0))
        out["freezing_range_K"] = out["liquidus_K"] - out["solidus_K"]
    except Unsolved as e:
        errors["melting"] = str(e)
    try:
        state = alloy.state(T_fixed)
        out["phases"] = state["phases"]
        out["density_T_g_cm3"] = state["density_g_cm3"]
        out.update({f"{k.replace(' ', '_')}_fraction": v for k, v in fractions_by_kind(state["phases"]).items()})
    except Unsolved as e:
        errors["phases"] = str(e)
    try:
        cold = alloy.state(298.15)
        out["density_298K_g_cm3"] = cold["density_g_cm3"]
        out["phases_298K"] = [p["phase"] for p in cold["phases"]]
    except Unsolved as e:
        errors["density_298K"] = str(e)
    out["failed"] = errors
    return out


def stage_anchors(engine: Engine) -> None:
    path, tm = RAW / "anchors.jsonl", melting_points()
    done = read_cache(path)
    for name, (elements, x) in ANCHORS.items():
        if name in done:
            continue
        T = 1273.0 if set(elements) & {"Co", "Fe", "Ni"} else 1473.0
        record = {"key": name, "composition": dict(zip(elements, x)), "T_fixed_K": T,
                  **compute_alloy(engine, dict(zip(elements, x)), T, tm)}
        append(path, record)
        print(name, {k: v for k, v in record.items() if k.endswith("_K") or k == "failed"}, flush=True)


def stage_pool(engine: Engine, system: str, limit: int | None) -> None:
    spec, path, tm = SYSTEMS[system], RAW / f"{system}_pool.jsonl", melting_points()
    elements = spec["elements"]
    units = sample_pool(len(elements))
    done = read_cache(path)
    # one Thermo-Calc system per set of present elements: do each set in one go
    order = sorted(range(len(units)), key=lambda i: tuple(units[i] > 0))
    todo = [i for i in order if f"{system}-{i:03d}" not in done][:limit]
    print(f"{system}: {len(done)} done, {len(todo)} to do", flush=True)
    for count, i in enumerate(todo, 1):
        start, before = time.time(), engine.calcs
        composition = {el: int(u) / GRID for el, u in zip(elements, units[i])}
        result = compute_alloy(engine, composition, spec["T"], tm)
        record = {"key": f"{system}-{i:03d}", "row": i, "composition": composition, **result,
                  "equilibria": engine.calcs - before, "seconds": round(time.time() - start, 1)}
        if result["failed"]:
            record["error"] = result["failed"]  # retried on the next run; `--keep-failed` exports it anyway
        append(path, record)
        print(f"[{count}/{len(todo)}] {record['key']} solidus {result.get('solidus_K', float('nan')):.1f} "
              f"liquidus {result.get('liquidus_K', float('nan')):.1f} "
              f"intermetallic {result.get('intermetallic_fraction', float('nan')):.3f} "
              f"{record['equilibria']} equilibria {record['seconds']} s {result['failed'] or ''}", flush=True)


def stage_binaries(engine: Engine, system: str) -> None:
    spec, path, tm = SYSTEMS[system], RAW / f"{system}_binaries.jsonl", melting_points()
    done = read_cache(path)
    for a, b in itertools.combinations(spec["elements"], 2):
        key = f"{a}-{b}"
        if key in done:
            continue
        start = time.time()
        record = {"key": key, "elements": [a, b], "liquidus_curve": [], "points": {}, "failed": {}}
        for step in range(1, 20):  # at.% of b: 5, 10, ..., 95
            xb = step / 20
            alloy = Alloy(engine, {a: 1 - xb, b: xb})
            label = str(int(round(100 * xb)))
            try:
                melt = alloy.solidus_liquidus(max(tm[a], tm[b]) + 250.0, min(tm[a], tm[b], spec["T"]) - 100.0)
                record["liquidus_curve"].append([xb, round(melt["liquidus_K"], 1)])
            except Unsolved as e:
                record["failed"][f"melting {label}"] = str(e)
                melt = None
            if step in (5, 10, 15):
                point = {"x": {a: 1 - xb, b: xb}}
                if melt:
                    point.update(solidus_K=round(melt["solidus_K"], 1), liquidus_K=round(melt["liquidus_K"], 1),
                                 solidus_method=melt["solidus_method"], liquidus_method=melt["liquidus_method"])
                try:
                    point["phases"] = alloy.state(spec["T"])["phases"]
                except Unsolved as e:
                    record["failed"][f"phases {label}"] = str(e)
                record["points"][label] = point
        curve = [[0.0, tm[a]], *record["liquidus_curve"], [1.0, tm[b]]]
        xmin, tmin = min(curve, key=lambda p: p[1])
        record.update(liquidus_min_K=round(tmin, 1), liquidus_min_at_pct_b=round(100 * xmin),
                      seconds=round(time.time() - start, 1))
        if record["failed"]:
            record["error"] = record["failed"]
        append(path, record)
        print(key, "min liquidus", record["liquidus_min_K"], "at", record["liquidus_min_at_pct_b"], "% ", b,
              {k: (v.get("solidus_K"), v.get("liquidus_K"), [p["phase"] for p in v.get("phases", [])])
               for k, v in record["points"].items()}, record["failed"] or "", flush=True)


# --------------------------------------------------------------------- export


def stage_export(tc_version: str | None) -> None:
    import pandas as pd

    tm = melting_points()
    info_path = RAW / "run_info.json"
    info = json.loads(info_path.read_text()) if info_path.exists() else {}
    if tc_version:
        info.update(tc_python_version=tc_version, last_calculation_date=datetime.date.today().isoformat())
        info_path.write_text(json.dumps(info, indent=1) + "\n")
    summary = {}
    for system, spec in SYSTEMS.items():
        elements = spec["elements"]
        units = sample_pool(len(elements))
        records = all_records(RAW / f"{system}_pool.jsonl")
        rows = []
        for i in range(len(units)):
            r = records.get(f"{system}-{i:03d}")
            if r is None:
                continue
            row = {"id": r["key"], **{f"x_{el}": r["composition"][el] for el in elements}}
            for column in ("solidus_K", "liquidus_K", "freezing_range_K"):
                row[column] = round(r[column], 1) if column in r else np.nan
            for column in ("solid_solution_fraction", "intermetallic_fraction", "liquid_fraction"):
                row[f"{column}_{int(spec['T'])}K"] = round(r[column], 4) if column in r else np.nan
            row[f"density_{int(spec['T'])}K_g_cm3"] = round(r["density_T_g_cm3"], 4) if "density_T_g_cm3" in r else np.nan
            row["density_298K_g_cm3"] = round(r["density_298K_g_cm3"], 4) if "density_298K_g_cm3" in r else np.nan
            row[f"phases_{int(spec['T'])}K"] = json.dumps(
                [{"phase": p["phase"], "fraction": round(p["fraction"], 4), "kind": p["kind"],
                  **({"order": p["order"]} if "order" in p else {})} for p in r.get("phases", [])])
            row["melting_method"] = "; ".join(
                f"{k.split('_')[0]}: {r[k]}" for k in ("solidus_method", "liquidus_method") if k in r)
            rows.append(row)
        if not rows:
            continue
        table = pd.DataFrame(rows)
        table.to_csv(DATA / f"{system}.csv", index=False)
        failed = {}
        for r in records.values():
            for what in r.get("failed", {}):
                failed[what] = failed.get(what, 0) + 1
        inter = table[f"intermetallic_fraction_{int(spec['T'])}K"]
        summary[system] = {
            "rows": len(table), "sampled": len(units), "failed": failed,
            "bisection": int(table["melting_method"].str.contains("bracket").sum()),
            "midpoint": int(table["melting_method"].str.contains("middle").sum()),
            "liquid_at_T": int((table[f"liquid_fraction_{int(spec['T'])}K"] > 0).sum()),
            "intermetallic_zero": int((inter == 0).sum()), "intermetallic_finite": int(inter.notna().sum()),
            "equilibria": int(sum(r.get("equilibria", 0) for r in records.values())),
            "seconds": float(sum(r.get("seconds", 0) for r in records.values())),
            "describe": table[["solidus_K", "liquidus_K", "freezing_range_K", inter.name,
                               "density_298K_g_cm3"]].describe().loc[["count", "min", "50%", "max"]].round(3),
        }

        binaries = all_records(RAW / f"{system}_binaries.jsonl")
        if binaries:
            facts = {
                "system": system, "database": DATABASE, "pressure_Pa": PRESSURE,
                "fixed_temperature_K": spec["T"], "elements": list(elements),
                "note": ("Pure elements and binaries only; no ternary or higher-order calculation. "
                         "Compositions are at.% of the second element. Gas phase excluded. "
                         f"'order' is the largest site-fraction difference between the two sublattices of "
                         f"BCC_B2 / FCC_L12; above {ORDER_THRESHOLD} the phase is counted as ordered (intermetallic)."),
                "melting_point_K": {el: tm[el] for el in elements},
                "binaries": {
                    key: {
                        "elements": b["elements"],
                        "points": {
                            pct: {"solidus_K": p.get("solidus_K"), "liquidus_K": p.get("liquidus_K"),
                                  "phases": [{"phase": q["phase"], "fraction": round(q["fraction"], 4), "kind": q["kind"],
                                              **({"order": q["order"]} if "order" in q else {})}
                                             for q in p.get("phases", [])]}
                            for pct, p in b["points"].items()},
                        "liquidus_min_K": b["liquidus_min_K"], "liquidus_min_at_pct_second": b["liquidus_min_at_pct_b"],
                        "liquidus_curve_pct_second_K": [[round(100 * x), t] for x, t in b["liquidus_curve"]],
                    } for key, b in binaries.items()},
            }
            (DATA / f"{system}_binaries.json").write_text(json.dumps(facts, indent=1) + "\n")
            summary[system]["binaries"] = len(binaries)
            summary[system]["binaries_failed"] = {k: b["failed"] for k, b in binaries.items() if b.get("failed")}
    write_readme(summary, tm, all_records(RAW / "anchors.jsonl"), all_records(RAW / "elements.jsonl", melting=False), info)
    for system, s in summary.items():
        print(system, {k: v for k, v in s.items() if k != "describe"})
        print(s["describe"])


# Literature values used to judge the anchors. Sources in the README text.
ELEMENT_TM_SGTE = {"Al": 933.47, "Co": 1768.0, "Cr": 2180.0, "Fe": 1811.0, "Mn": 1519.0, "Ni": 1728.3, "Mo": 2896.0,
                   "Nb": 2750.0, "Ta": 3290.0, "Ti": 1941.0, "V": 2183.0, "W": 3695.0, "Zr": 2127.85}
ELEMENT_DENSITY = {"Al": 2.70, "Co": 8.90, "Cr": 7.19, "Fe": 7.87, "Mn": 7.47, "Ni": 8.91, "Mo": 10.28, "Nb": 8.57,
                   "Ta": 16.65, "Ti": 4.51, "V": 6.11, "W": 19.25, "Zr": 6.51}


def write_readme(summary: dict, tm: dict, anchors: dict, elements: dict, info: dict) -> None:
    lines = [
        "# Thermo-Calc-computed alloy pools (experiment E7)",
        "",
        "Built by `experiments/e7_calphad_prior/make_tc_data.py`; nothing here was copied from a sibling repo.",
        "",
        f"- Software: Thermo-Calc 2025b through TC-Python {info.get('tc_python_version', '?')}, on this machine.",
        f"- Database: {DATABASE} as shipped with Thermo-Calc 2025b (database files dated 2025-06-18; the minor "
        "version is not exposed by TC-Python and is not recorded).",
        f"- Last calculation: {info.get('last_calculation_date', '?')}.",
        f"- Conditions: {PRESSURE:.0f} Pa, one mole of atoms, global minimisation, default phases of the database "
        "for the elements present, **gas phase removed** (with it, Mn-bearing melts boil below 3,100 K and no "
        "liquidus exists in the sense meant here).",
        "- Each composition is calculated in the system of its present elements only.",
        f"- Sampling: all points of the 5 at.% grid with every element between 0 and 35 at.% and at least "
        f"{MIN_PRESENT} elements present were enumerated; {POOL_SIZE} were drawn without replacement with "
        f"`numpy.random.default_rng({SEED})`.",
        "",
        "## Quantities",
        "",
        "| Column | Meaning |",
        "|---|---|",
        "| `solidus_K` | highest temperature at which the equilibrium has no liquid |",
        "| `liquidus_K` | lowest temperature at which the equilibrium is all liquid |",
        "| `freezing_range_K` | liquidus − solidus |",
        "| `solid_solution_fraction_<T>K` | mole fraction of phases that are disordered BCC (A2), FCC (A1) or HCP (A3) at the fixed temperature |",
        "| `intermetallic_fraction_<T>K` | mole fraction of every other solid phase: sigma, Laves, mu, the Mn-type A12/A13 phases, and BCC_B2 / FCC_L12 composition sets that are ordered |",
        "| `liquid_fraction_<T>K` | mole fraction of liquid at the fixed temperature (the three fractions sum to 1) |",
        "| `phases_<T>K` | JSON: every stable phase with its fraction, its group, and for BCC_B2 / FCC_L12 the order parameter |",
        "| `density_<T>K_g_cm3` | mass / molar volume of the equilibrium state at the fixed temperature |",
        "| `density_298K_g_cm3` | the same for the full equilibrium at 298.15 K |",
        "| `melting_method` | how solidus and liquidus were obtained (below) |",
        "",
        "Fixed temperature: " + ", ".join(f"{int(s['T'])} K for `{n}`" for n, s in SYSTEMS.items()) + ".",
        "",
        "**Solidus and liquidus.** Each is first solved directly as a phase boundary (liquid fixed at amount 0 or 1, "
        "temperature free) and accepted only if global equilibria 1 K below and 1 K above agree with it. Otherwise "
        "it is found by bisection on the liquid fraction to 0.5 K, which assumes the liquid fraction rises with "
        "temperature. So every value is supported by global equilibria to within 1 K.",
        "",
        f"**Ordered or disordered.** {DATABASE} describes A2/B2 and A1/L1₂ with one phase each (`BCC_B2`, `FCC_L12`). "
        f"A composition set is counted as ordered when the site fractions of its two sublattices differ by more than "
        f"{ORDER_THRESHOLD} for some element. This threshold is a convention; the order parameter is kept in the "
        "JSON column so the grouping can be redone.",
        "",
        "**Density at 298.15 K** is that of the full equilibrium phase assemblage at room temperature, which a real "
        "alloy does not reach. It is recorded for completeness and is not used as a task.",
        "",
        "## What was built",
        "",
        "| System | Rows in CSV | Failed quantities (rows) | Melting by bisection (rows) | Rows with liquid at fixed T | Intermetallic fraction exactly 0 | Equilibria | Hours |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for system, s in summary.items():
        lines.append(
            f"| `{system}` | {s['rows']} of {s['sampled']} | {s['failed'] or 'none'} | {s['bisection']} | {s['liquid_at_T']} "
            f"| {s['intermetallic_zero']} of {s['intermetallic_finite']} | {s['equilibria']:,} | {s['seconds'] / 3600:.2f} |")
    lines += ["", "A failed quantity is left empty in the CSV; the row is kept for the quantities that did compute.", ""]
    for system, s in summary.items():
        lines += [f"`{system}` ranges:", "", "```", str(s["describe"]), "```", ""]
        if "binaries" in s:
            lines += [f"`{system}_binaries.json`: {s['binaries']} binaries; failures: {s['binaries_failed'] or 'none'}.", ""]
    lines += [
        "## Anchor checks",
        "",
        "Melting points of the elements from a one-element system of the same database, against the SGTE values "
        "(Dinsdale, Calphad 15:317, 1991), and the density at 298.15 K against handbook values:",
        "",
        "| Element | Melting point here, K | SGTE, K | Density at 298 K here, g/cm³ | Handbook |",
        "|---|---|---|---|---|",
    ]
    for el in sorted(elements):
        e = elements[el]
        lines.append(f"| {el} | {e['melting_point_K']:.1f} | {ELEMENT_TM_SGTE[el]:.1f} | {e['density_298K_g_cm3']:.2f} | {ELEMENT_DENSITY[el]:.2f} |")
    lines += ["", "Equiatomic alloys:", "",
              "| Alloy | Solidus, K | Liquidus, K | Phases at fixed T (fraction) | Density 298 K, g/cm³ | Failed |",
              "|---|---|---|---|---|---|"]
    for name, a in anchors.items():
        phases = ", ".join(f"{p['phase']} {'ordered ' if p.get('order', 0) > ORDER_THRESHOLD else ''}{p['fraction']:.2f}" for p in a.get("phases", []))
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


def run_stages(stage: str, systems: tuple[str, ...], limit: int | None) -> None:
    """The Thermo-Calc stages, in one session (the worker process)."""
    from tc_python import LoggingPolicy, TCPython

    beat({"start": "session"}, BUILD_LIMIT)
    with TCPython(logging_policy=LoggingPolicy.NONE) as session:
        engine = Engine(session)
        if stage in ("all", "elements"):
            stage_elements(engine)
        if stage in ("all", "anchors"):
            stage_anchors(engine)
        if stage in ("all", "binaries"):
            for system in systems:
                stage_binaries(engine, system)
        if stage in ("all", "pool"):
            for system in systems:
                stage_pool(engine, system, limit)


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
    parser.add_argument("--stage", choices=("all", "elements", "anchors", "pool", "binaries", "export"), default="all")
    parser.add_argument("--system", choices=(*SYSTEMS, "all"), default="all")
    parser.add_argument("--limit", type=int, default=None, help="pool stage: stop after this many compositions")
    parser.add_argument("--worker", action="store_true", help="internal: run the calculations in this process")
    args = parser.parse_args()
    systems = tuple(SYSTEMS) if args.system == "all" else (args.system,)
    if args.worker:
        run_stages(args.stage, systems, args.limit)
        return
    version = None
    if args.stage != "export":
        import tc_python

        version = getattr(tc_python, "__version__", None)
        supervise(sys.argv[1:])
    if args.stage in ("all", "export"):
        stage_export(version)


if __name__ == "__main__":
    main()
