"""E8: experimental formation enthalpies with the crystal each one belongs to.

Source of the enthalpies: matminer dataset `expt_formation_enthalpy_kingsbury`
(Kingsbury et al., the set the Materials Project 2020 corrections were fitted on;
values in eV/atom at 298 K, with the Materials Project id of the matching phase).
Structures are fetched from the Materials Project with the user's
own API key (environment variable MP_API_KEY; never written to disk).

    python experiments/e8_formation_enthalpy/build_set.py

Writes data/formation/compounds.extxyz (one frame per compound, info: name, formula,
H_expt, H_expt_unc, E_mp_raw, H_mp), data/formation/elements.extxyz (lowest-energy
Materials Project phase of every element that occurs, info: name, element, E_mp_raw)
and data/formation/README.md.
"""

from __future__ import annotations

import json
import warnings
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "formation"
MAX_SITES = 40
N_COMPOUNDS = 800


def fetch(params: dict) -> list:
    """Summary documents from the Materials Project REST API (the mp_api client does not import in this env)."""
    import os
    from types import SimpleNamespace

    import requests
    from pymatgen.core import Structure

    reply = requests.get("https://api.materialsproject.org/materials/summary/", params=params,
                         headers={"X-API-KEY": os.environ["MP_API_KEY"]}, timeout=120)
    reply.raise_for_status()
    return [SimpleNamespace(material_id=str(d["material_id"]), structure=Structure.from_dict(d["structure"]),
                            uncorrected_energy_per_atom=d.get("uncorrected_energy_per_atom"),
                            formation_energy_per_atom=d.get("formation_energy_per_atom"), nsites=d["nsites"])
            for d in reply.json()["data"]]


def main() -> None:
    warnings.filterwarnings("ignore")
    from ase.io import write
    from matminer.datasets import load_dataset
    from pymatgen.core import Composition
    from pymatgen.io.ase import AseAtomsAdaptor

    table = load_dataset("expt_formation_enthalpy_kingsbury")
    table = table[table["likely_mpid"].notna() & np.isfinite(table["expt_form_e"])].drop_duplicates("likely_mpid")
    ids = sorted(table["likely_mpid"])
    fields = "material_id,structure,uncorrected_energy_per_atom,formation_energy_per_atom,nsites"
    # The API now answers with ids in a new format, so a batch reply cannot be matched back
    # to the requested ids: one request per compound, in a seed-0 order, until enough pass.
    by_id = {r["likely_mpid"]: r for _, r in table.iterrows()}
    rows = []
    for i in np.random.default_rng(0).permutation(len(ids)):
        if len(rows) == N_COMPOUNDS:
            break
        r = by_id[ids[i]]
        found = fetch({"material_ids": ids[i], "_fields": fields, "_limit": 5})
        if len(found) != 1:
            continue
        doc = found[0]
        doc.material_id = ids[i]
        comp = Composition(r["formula"])
        if doc.nsites > MAX_SITES or doc.uncorrected_energy_per_atom is None or len(comp) < 2:
            continue
        if comp.reduced_formula != doc.structure.composition.reduced_formula:
            continue
        rows.append((r, doc))
    rows.sort(key=lambda x: x[1].material_id)
    elements = sorted({str(e) for _, doc in rows for e in doc.structure.composition.elements})
    refs = {}
    for el in elements:
        found = fetch({"chemsys": el, "_fields": fields, "_limit": 1000})
        found = [d for d in found if d.uncorrected_energy_per_atom is not None and d.nsites <= MAX_SITES]
        refs[el] = min(found, key=lambda d: d.uncorrected_energy_per_atom)

    frames = []
    for r, doc in rows:
        atoms = AseAtomsAdaptor.get_atoms(doc.structure)
        atoms.info = {"name": str(doc.material_id), "formula": r["formula"], "H_expt": float(r["expt_form_e"]),
                      "H_expt_unc": float(r["uncertainty"]) if np.isfinite(r["uncertainty"]) else -1.0,
                      "E_mp_raw": float(doc.uncorrected_energy_per_atom),
                      "H_mp": float(doc.formation_energy_per_atom) if doc.formation_energy_per_atom is not None else float("nan")}
        atoms.calc = None
        frames.append(atoms)
    ref_frames = []
    for el, doc in refs.items():
        atoms = AseAtomsAdaptor.get_atoms(doc.structure)
        atoms.info = {"name": str(doc.material_id), "element": el, "E_mp_raw": float(doc.uncorrected_energy_per_atom)}
        atoms.calc = None
        ref_frames.append(atoms)
    OUT.mkdir(parents=True, exist_ok=True)
    write(OUT / "compounds.extxyz", frames)
    write(OUT / "elements.extxyz", ref_frames)
    (OUT / "README.md").write_text(
        "# Experimental formation enthalpies with structures (experiment E8)\n\n"
        "Built by `experiments/e8_formation_enthalpy/build_set.py`.\n\n"
        f"- `compounds.extxyz`: {len(frames)} compounds, a seed-0 sample of the rows of matminer's "
        "`expt_formation_enthalpy_kingsbury` that carry a Materials Project id, have at most "
        f"{MAX_SITES} sites and whose formula matches the Materials Project phase. `H_expt` is the "
        "experimental formation enthalpy at 298 K in eV/atom; `E_mp_raw` the uncorrected energy per atom "
        "as the Materials Project serves it (not used by the experiment); `H_mp` the Materials Project's own formation "
        "energy as served.\n"
        f"- `elements.extxyz`: the lowest-energy Materials Project phase of each of the {len(ref_frames)} elements present.\n"
        "- Enthalpies: Kingsbury et al., matminer dataset `expt_formation_enthalpy_kingsbury` "
        "(figshare file 28232538). Structures and energies: Materials Project, CC BY 4.0, fetched "
        f"{__import__('datetime').date.today().isoformat()}.\n")
    print(json.dumps({"compounds": len(frames), "elements": len(ref_frames)}))


if __name__ == "__main__":
    main()
