"""E2 for eSEN-30M-OAM: run the model once per structure and keep what its energy head sees.

eSEN's energy head is a small network applied to each atom's scalar features and
summed over atoms. This script finds that network inside the loaded model (the module
whose name ends in `energy_block`), records its input for every atom at each of the
seven strained geometries, and measures by how much the total energy moves when the
head's last bias moves, which fixes the scale between head output and energy:

    E = scale * sum over atoms of head(s_i) + rest

`scale` is measured, not assumed. `rest` is recovered later from the stored energies.
Runs on FASTER (fairchem is not in the local environment); see hprc/esen_cache.slurm.
Resumable; one file per structure under <out>/<set>/.

    python cache_features_esen.py --set elastic --reference <dir with elastic.extxyz> --out <dir>
"""

from __future__ import annotations

import argparse
import os
import warnings
from pathlib import Path

import numpy as np
import torch
from ase import Atoms
from ase.io import read
from ase.optimize import FIRE

STRAINS = np.array([-0.03, -0.02, -0.01, 0.0, 0.01, 0.02, 0.03])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--set", choices=("dft15", "elastic"), required=True)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()
    warnings.filterwarnings("ignore")
    try:
        from ase.filters import ExpCellFilter
    except ImportError:
        from ase.constraints import ExpCellFilter
    from fairchem.core import OCPCalculator

    calc = OCPCalculator(model_name="eSEN-30M-OAM", local_cache=os.environ["FAIRCHEM_LOCAL_CACHE"],
                         cpu=not torch.cuda.is_available())
    model = calc.trainer.model
    blocks = [(n, m) for n, m in model.named_modules() if n.endswith("energy_block")]
    print("parameters in the model:", sum(p.numel() for p in model.parameters()), flush=True)
    if len(blocks) != 1:
        print("could not find a single energy_block; modules are:")
        for n, m in model.named_modules():
            if n.count(".") <= 3:
                print(" ", n, type(m).__name__)
        raise SystemExit(1)
    name, block = blocks[0]
    print("energy head:", name, block, flush=True)
    print("head parameters:", {k: tuple(v.shape) for k, v in block.state_dict().items()}, flush=True)
    last = [m for m in block.modules() if isinstance(m, torch.nn.Linear)][-1]
    captured: dict[str, torch.Tensor] = {}
    hook = block.register_forward_hook(lambda m, i, o: captured.update(s=i[0].detach().cpu().clone(), o=o.detach().cpu().clone()))

    out = args.out / args.set
    out.mkdir(parents=True, exist_ok=True)
    np.savez(args.out / "esen_30m_oam_energy_head.npz",
             **{k: v.detach().cpu().double().numpy() for k, v in block.state_dict().items()})
    frames = read(args.reference / f"{args.set}.extxyz", index=":")[: args.limit]
    for k, atoms in enumerate(frames):
        target = out / f"{k:04d}.npz"
        if target.exists():
            continue
        try:
            a = atoms.copy()
            a.calc = calc
            FIRE(ExpCellFilter(a), logfile=None).run(fmax=0.05, steps=300)
            cell0, frac, symbols = a.get_cell().array.copy(), a.get_scaled_positions().copy(), a.get_chemical_symbols()
            feats, outs, volumes, energies = [], [], [], []
            for eps in STRAINS:
                s = Atoms(symbols=symbols, scaled_positions=frac, cell=cell0 * (1.0 + eps) ** (1.0 / 3.0), pbc=True)
                s.calc = calc
                energies.append(float(s.get_potential_energy()))
                volumes.append(s.get_volume())
                feats.append(captured["s"].float().numpy().reshape(len(s), -1))
                outs.append(float(captured["o"].double().sum()))
            with torch.no_grad():  # scale between summed head output and energy
                last.bias += 0.01
            s2 = Atoms(symbols=symbols, scaled_positions=frac, cell=cell0 * (1.0 + STRAINS[-1]) ** (1.0 / 3.0), pbc=True)
            s2.calc = calc
            shifted = float(s2.get_potential_energy())
            with torch.no_grad():
                last.bias -= 0.01
            scale = (shifted - energies[-1]) / (0.01 * len(a))
            np.savez_compressed(target, name=str(atoms.info.get("name", k)), K_ref=float(atoms.info["K_ref"]),
                                n_atoms=len(a), scale=scale, volumes=np.array(volumes), energies=np.array(energies),
                                s=np.stack(feats), head_out=np.array(outs))
            print(f"[{k + 1}/{len(frames)}] {atoms.info.get('name')} n={len(a)} scale={scale:.6f}", flush=True)
        except Exception as error:
            print(f"[{k + 1}/{len(frames)}] FAILED {atoms.info.get('name')}: {str(error)[:160]}", flush=True)
    hook.remove()
    print("CACHE_DONE", flush=True)


if __name__ == "__main__":
    main()
