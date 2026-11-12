"""E8: energy per atom of every compound and elemental reference, from a potential as shipped.

Single points at the Materials Project geometries (no relaxation).

    conda activate mlip-mace  && python experiments/e8_formation_enthalpy/potential_energies.py mace
    conda activate matinvent  && python experiments/e8_formation_enthalpy/potential_energies.py orb

Writes data/formation/energies_<potential>.json: {"compounds": {name: eV/atom}, "elements": {symbol: eV/atom}}.
"""

from __future__ import annotations

import json
import sys
import warnings
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "formation"


def calculator(potential: str):
    if potential == "mace":
        from mace.calculators import mace_mp

        return mace_mp(model="medium-mpa-0", device="cpu", default_dtype="float64")
    if potential == "orb":
        from orb_models.forcefield import pretrained
        from orb_models.forcefield.calculator import ORBCalculator

        return ORBCalculator(pretrained.orb_v3_conservative_inf_omat(device="cpu", precision="float32-high", compile=False), device="cpu")
    raise SystemExit(f"unknown potential {potential}")


def main() -> None:
    warnings.filterwarnings("ignore")
    from ase.io import read

    potential = sys.argv[1]
    calc = calculator(potential)
    out = {"compounds": {}, "elements": {}}
    for key, file, label in (("compounds", "compounds.extxyz", "name"), ("elements", "elements.extxyz", "element")):
        for i, atoms in enumerate(read(DATA / file, index=":")):
            atoms.calc = calc
            calc.reset()
            out[key][str(atoms.info[label])] = float(atoms.get_potential_energy()) / len(atoms)
            if i % 100 == 0:
                print(key, i, flush=True)
    (DATA / f"energies_{potential}.json").write_text(json.dumps(out, indent=1) + "\n")
    print("wrote", len(out["compounds"]), len(out["elements"]))


if __name__ == "__main__":
    main()
