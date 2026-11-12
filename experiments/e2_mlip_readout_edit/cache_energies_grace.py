"""E2 for GRACE: energy against volume for the reference crystals, model used as shipped.

GRACE foundation models are distributed as TensorFlow saved models. This script uses
one through its ASE calculator: relax (FIRE, fmax 0.05), apply the seven isotropic
strains, store volumes, energies and the relaxed
geometry (so later scripts can re-evaluate an edited model at the same points). Resumable. grace-mac env.

    python experiments/e2_mlip_readout_edit/cache_energies_grace.py --set elastic --model GRACE-2L-OAM
"""

from __future__ import annotations

import argparse
import warnings
from pathlib import Path

import numpy as np
from ase.io import read
from ase.optimize import FIRE

ROOT = Path(__file__).resolve().parents[2]
STRAINS = np.array([-0.03, -0.02, -0.01, 0.0, 0.01, 0.02, 0.03])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--set", choices=("dft15", "elastic"), required=True)
    parser.add_argument("--model", default="GRACE-2L-OAM")
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()
    warnings.filterwarnings("ignore")
    from ase.filters import FrechetCellFilter
    from tensorpotential.calculator import grace_fm

    calc = grace_fm(args.model)
    out = ROOT / "data" / "large" / f"mlip_cache_grace_{args.model}_v2" / args.set
    out.mkdir(parents=True, exist_ok=True)
    frames = read(ROOT / "data" / "mlip_reference" / f"{args.set}.extxyz", index=":")[: args.limit]
    for k, atoms in enumerate(frames):
        target = out / f"{k:04d}.npz"
        if target.exists():
            continue
        try:
            a = atoms.copy()
            a.calc = calc
            FIRE(FrechetCellFilter(a), logfile=None).run(fmax=0.05, steps=300)
            cell0, frac = a.get_cell().array.copy(), a.get_scaled_positions().copy()
            volumes, energies = [], []
            for eps in STRAINS:
                s = a.copy()
                s.set_cell(cell0 * (1.0 + eps) ** (1.0 / 3.0), scale_atoms=False)
                s.set_scaled_positions(frac)
                s.calc = calc
                energies.append(float(s.get_potential_energy()))
                volumes.append(s.get_volume())
            np.savez_compressed(target, name=str(atoms.info.get("name", k)), K_ref=float(atoms.info["K_ref"]),
                                n_atoms=len(a), volumes=np.array(volumes), energies=np.array(energies),
                                cell0=cell0, frac=frac, numbers=a.get_atomic_numbers())
            print(f"[{k + 1}/{len(frames)}] {atoms.info.get('name')} n={len(a)}", flush=True)
        except Exception as error:
            print(f"[{k + 1}/{len(frames)}] FAILED {atoms.info.get('name')}: {str(error)[:160]}", flush=True)
    print("CACHE_DONE", flush=True)


if __name__ == "__main__":
    main()
