"""E2 step 2: run MACE once per structure and keep what its readout sees.

For each reference structure: relax cell and positions with the unedited
MACE-MPA-0 medium (FIRE, fmax 0.05 eV/A), apply the seven isotropic strains of
the sibling paper's protocol (-3% to +3% in volume, fractional coordinates
frozen), and store the scalar node features that enter the two readout blocks,
with the volumes and MACE's own energies.

Every weight the experiment edits (readouts, reference energies, scale, shift)
acts after these features, so the energy of any edited model at these seven
geometries can be recomputed from the cache without running MACE again. The
geometries stay those of the unedited model.

Resumable: one file per structure under data/large/mlip_cache/; finished ones
are skipped. Run in the mlip-mace env.

    python supplementary/e2_mlip_readout_edit/cache_features.py --set dft15
    python supplementary/e2_mlip_readout_edit/cache_features.py --set elastic
"""

from __future__ import annotations

import argparse
import os
import warnings
from pathlib import Path

import numpy as np
import torch
from ase.io import read
from ase.optimize import FIRE

ROOT = Path(__file__).resolve().parents[2]
MODEL = Path(os.path.expanduser("~/.cache/mace/macempa0mediummodel"))
STRAINS = np.array([-0.03, -0.02, -0.01, 0.0, 0.01, 0.02, 0.03])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--set", choices=("dft15", "elastic"), required=True)
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()
    warnings.filterwarnings("ignore")
    from ase.filters import FrechetCellFilter
    from mace.calculators import MACECalculator

    calc = MACECalculator(model_paths=str(MODEL), device="cpu", default_dtype="float64")
    model = calc.models[0]
    captured: dict[str, torch.Tensor] = {}
    hooks = [
        model.readouts[0].register_forward_hook(lambda m, i, o: captured.__setitem__("f0", i[0].detach().clone())),
        model.readouts[1].register_forward_hook(lambda m, i, o: captured.__setitem__("f1", i[0].detach().clone())),
    ]
    n0 = model.readouts[0].linear.weight.numel()  # scalar channels read by the first readout
    n1 = model.readouts[1].linear_1.weight.numel() // model.readouts[1].linear_2.weight.numel()

    out = ROOT / "data" / "large" / "mlip_cache" / args.set
    out.mkdir(parents=True, exist_ok=True)
    frames = read(ROOT / "data" / "mlip_reference" / f"{args.set}.extxyz", index=":")[: args.limit]
    for k, atoms in enumerate(frames):
        target = out / f"{k:04d}.npz"
        if target.exists():
            continue
        try:
            atoms = atoms.copy()
            atoms.calc = calc
            FIRE(FrechetCellFilter(atoms), logfile=None).run(fmax=0.05, steps=300)
            cell0, frac = atoms.get_cell().array.copy(), atoms.get_scaled_positions().copy()
            f0, f1, volumes, energies = [], [], [], []
            for eps in STRAINS:
                strained = atoms.copy()
                strained.set_cell(cell0 * (1.0 + eps) ** (1.0 / 3.0), scale_atoms=False)
                strained.set_scaled_positions(frac)
                strained.calc = calc
                energies.append(strained.get_potential_energy())
                volumes.append(strained.get_volume())
                f0.append(captured["f0"][:, :n0].numpy().astype(np.float32))
                f1.append(captured["f1"][:, :n1].numpy().astype(np.float32))
            np.savez_compressed(
                target, name=str(atoms.info.get("name", k)), K_ref=float(atoms.info["K_ref"]),
                Z=atoms.get_atomic_numbers(), volumes=np.array(volumes), energies=np.array(energies),
                f0=np.stack(f0), f1=np.stack(f1),
            )
            print(f"[{k + 1}/{len(frames)}] {atoms.info.get('name')} n={len(atoms)}", flush=True)
        except Exception as error:  # a structure that fails to relax is reported and skipped
            print(f"[{k + 1}/{len(frames)}] FAILED {atoms.info.get('name')}: {str(error)[:120]}", flush=True)
    for hook in hooks:
        hook.remove()


if __name__ == "__main__":
    main()
