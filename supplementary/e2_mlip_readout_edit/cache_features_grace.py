"""E2 for GRACE-2L-OAM: the derivative of the energy with respect to each weight of the
output layer, measured on the real model.

GRACE's readout ends in instructions/MLPOut2ScalarTarget: scale (12), layer0 (12 x 64),
layer1 (64 x 1), 844 numbers. The model ships as a TensorFlow saved model, whose inner
activations are not exposed, but its variables can be reassigned. The energy is linear
in layer1, so for every cached geometry this script moves each of the 64 weights by
0.1 in turn and records the change of energy divided by 0.1. The first structure also
checks linearity with a second step.

Needs cache_energies_grace.py first. Resumable; shard with --shard i --of n. grace-mac env.

    python supplementary/e2_mlip_readout_edit/cache_features_grace.py --set elastic
"""

from __future__ import annotations

import argparse
import warnings
from pathlib import Path

import numpy as np
from ase import Atoms

ROOT = Path(__file__).resolve().parents[2]
STRAINS = np.array([-0.03, -0.02, -0.01, 0.0, 0.01, 0.02, 0.03])
STEP = 0.1


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--set", choices=("dft15", "elastic"), required=True)
    parser.add_argument("--model", default="GRACE-2L-OAM")
    parser.add_argument("--shard", type=int, default=0)
    parser.add_argument("--of", type=int, default=1)
    parser.add_argument("--reverse", action="store_true", help="work from the last structure down (second machine)")
    args = parser.parse_args()
    warnings.filterwarnings("ignore")
    from tensorpotential.calculator import grace_fm

    calc = grace_fm(args.model)
    readout = calc.models[0].instructions["MLPOut2ScalarTarget"]
    w = readout.mlp.layer1.w
    base = w.numpy().copy()
    if args.shard == 0:
        np.savez(ROOT / "data" / "mlip_reference" / "grace_2l_oam_output_layer.npz", w=base.astype(np.float64),
                 layer0=readout.mlp.layer0.w.numpy().astype(np.float64), scale=readout.scale.numpy().astype(np.float64))

    def energy(atoms) -> float:
        calc.reset()
        atoms.calc = calc
        return float(atoms.get_potential_energy())

    folder = ROOT / "data" / "large" / f"mlip_cache_grace_{args.model}_v2" / args.set
    checked = False
    todo = list(enumerate(sorted(folder.glob("*.npz"))))
    for k, path in (reversed(todo) if args.reverse else todo):
        target = path.with_suffix(".G.npy")
        if k % args.of != args.shard or target.exists():
            continue
        d = np.load(path)
        G = np.zeros((len(STRAINS), base.shape[0]))
        for i, eps in enumerate(STRAINS):
            s = Atoms(numbers=d["numbers"], scaled_positions=d["frac"], cell=d["cell0"] * (1.0 + eps) ** (1.0 / 3.0), pbc=True)
            e0 = energy(s)
            for j in range(base.shape[0]):
                moved = base.copy()
                moved[j, 0] += STEP
                w.assign(moved)
                G[i, j] = (energy(s) - e0) / STEP
                if not checked:
                    moved[j, 0] += STEP
                    w.assign(moved)
                    print(f"linearity check: first step {G[i, j]:.8f}, second step {(energy(s) - e0) / STEP - G[i, j]:.8f} eV per unit;"
                          f" energy against cache {e0 - float(d['energies'][i]):+.2e} eV", flush=True)
                    checked = True
            w.assign(base)
        np.save(target, G)
        print(f"[{k + 1}] {d['name']} n={int(d['n_atoms'])}", flush=True)
    print("FEATURES_DONE", flush=True)


if __name__ == "__main__":
    main()
