"""E2 for ORB-v3: run the model once per structure and keep what its energy head sees.

ORB-v3 (orb_v3_conservative_inf_omat, the featurizer of the sibling paper) computes

    E = A * mlp(x) + C,     mlp(x) = W2 . silu(W1 x + b1) + b2

where x is the mean of the 256 node features over the atoms of the structure, A is
the normaliser's scale times the number of atoms, and C collects the normaliser's
mean, the per-element reference energies and the pair repulsion. W1, b1, W2, b2 are
the 66,049 numbers an edit may change; they act after x, so the energy of an edited
head at a cached geometry is exact.

For each reference structure: relax with the unedited model (FIRE, fmax 0.05), apply
the seven isotropic strains, store x, A, the head's output and the model's energy.
The first structure also checks A by shifting b2 inside the real model.

Resumable; one file per structure under data/large/mlip_cache_orb/<set>/. matinvent env.

    python experiments/e2_mlip_readout_edit/cache_features_orb.py --set elastic
"""

from __future__ import annotations

import argparse
import warnings
from pathlib import Path

import numpy as np
import torch
from ase.io import read
from ase.optimize import FIRE

ROOT = Path(__file__).resolve().parents[2]
STRAINS = np.array([-0.03, -0.02, -0.01, 0.0, 0.01, 0.02, 0.03])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--set", choices=("dft15", "elastic"), required=True)
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()
    warnings.filterwarnings("ignore")
    from ase.filters import FrechetCellFilter
    from orb_models.forcefield import pretrained
    from orb_models.forcefield.calculator import ORBCalculator

    model = pretrained.orb_v3_conservative_inf_omat(device="cpu", precision="float32-high")
    calc = ORBCalculator(model, device="cpu")
    head = model.heads["energy"]
    captured: dict[str, torch.Tensor] = {}
    hook = head.mlp.register_forward_hook(
        lambda m, i, o: captured.update(x=i[0].detach().clone(), o=o.detach().clone()))
    sigma = float(torch.sqrt(head.normalizer.bn.running_var + head.normalizer.bn.eps))

    out = ROOT / "data" / "large" / "mlip_cache_orb" / args.set
    out.mkdir(parents=True, exist_ok=True)
    np.savez(ROOT / "data" / "mlip_reference" / "orb_v3_energy_head.npz",
             **{k: v.detach().double().numpy() for k, v in head.mlp.state_dict().items()},
             sigma=sigma, atom_avg=bool(head.atom_avg))
    frames = read(ROOT / "data" / "mlip_reference" / f"{args.set}.extxyz", index=":")[: args.limit]
    checked = False
    for k, atoms in enumerate(frames):
        target = out / f"{k:04d}.npz"
        if target.exists():
            continue
        try:
            atoms = atoms.copy()
            atoms.calc = calc
            FIRE(FrechetCellFilter(atoms), logfile=None).run(fmax=0.05, steps=300)
            cell0, frac = atoms.get_cell().array.copy(), atoms.get_scaled_positions().copy()
            scale = sigma * (len(atoms) if head.atom_avg else 1)
            xs, os_, volumes, energies = [], [], [], []
            for eps in STRAINS:
                s = atoms.copy()
                s.set_cell(cell0 * (1.0 + eps) ** (1.0 / 3.0), scale_atoms=False)
                s.set_scaled_positions(frac)
                s.calc = calc
                energies.append(float(s.get_potential_energy()))
                volumes.append(s.get_volume())
                xs.append(captured["x"].flatten().double().numpy())
                os_.append(float(captured["o"].flatten()[0]))
            if not checked:  # E must move by A * delta when the output bias moves by delta
                with torch.no_grad():
                    head.mlp[-2].bias += 0.01
                s.calc = ORBCalculator(model, device="cpu")
                shifted = float(s.get_potential_energy())
                with torch.no_grad():
                    head.mlp[-2].bias -= 0.01
                print(f"check of A: predicted shift {scale * 0.01:.6f} eV, measured {shifted - energies[-1]:.6f} eV", flush=True)
                checked = True
            np.savez_compressed(target, name=str(atoms.info.get("name", k)), K_ref=float(atoms.info["K_ref"]),
                                n_atoms=len(atoms), A=scale, volumes=np.array(volumes), energies=np.array(energies),
                                x=np.stack(xs), head_out=np.array(os_))
            print(f"[{k + 1}/{len(frames)}] {atoms.info.get('name')} n={len(atoms)}", flush=True)
        except Exception as error:
            print(f"[{k + 1}/{len(frames)}] FAILED {atoms.info.get('name')}: {str(error)[:120]}", flush=True)
    hook.remove()


if __name__ == "__main__":
    main()
