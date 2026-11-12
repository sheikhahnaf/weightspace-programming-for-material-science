"""E2 step 1: build the reference set of structures with DFT bulk moduli.

Two sources, written as one extxyz file each under data/mlip_reference/:

  dft15.extxyz     the 15 generated structures of the sibling paper with our own
                   VASP Birch-Murnaghan K0 (data/causal_replay/esen_vs_dft_bm.csv)
  elastic.extxyz   matminer elastic_tensor_2015 (Materials Project PBE elastic
                   tensors), K_VRH as the reference, cells of at most --max-atoms

Run in the matinvent env (needs matminer). First run downloads the matminer dataset.

    python supplementary/e2_mlip_readout_edit/prepare_reference.py
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import numpy as np
import pandas as pd
from ase.io import read, write

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "mlip_reference"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--max-atoms", type=int, default=12)
    parser.add_argument("--n", type=int, default=400, help="size of the random elastic subset")
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)

    table = pd.read_csv(ROOT / "data/causal_replay/esen_vs_dft_bm.csv").set_index("rank")
    frames = []
    for cif in sorted((ROOT / "data/dft_validation/structures").glob("bm_*.cif")):
        rank = int(re.search(r"bm_top(\d+)_", cif.name).group(1))
        if rank not in table.index:
            continue
        atoms = read(cif)
        atoms.info.update(name=cif.stem, K_ref=float(table.loc[rank, "dft_K0"]),
                          K_esen=float(table.loc[rank, "esen_K0"]), source="dft15")
        frames.append(atoms)
    write(OUT / "dft15.extxyz", frames)
    print(f"dft15: {len(frames)} structures")

    from matminer.datasets import load_dataset
    from pymatgen.io.ase import AseAtomsAdaptor

    df = load_dataset("elastic_tensor_2015")
    df = df[(df["nsites"] <= args.max_atoms) & (df["K_VRH"] > 5) & np.isfinite(df["K_VRH"])]
    df = df.sample(n=min(args.n, len(df)), random_state=args.seed)
    frames = []
    for _, row in df.iterrows():
        atoms = AseAtomsAdaptor.get_atoms(row["structure"])
        atoms.info.update(name=str(row["material_id"]), K_ref=float(row["K_VRH"]),
                          formula=str(row["formula"]), source="elastic_tensor_2015")
        frames.append(atoms)
    write(OUT / "elastic.extxyz", frames)
    print(f"elastic: {len(frames)} structures, K_VRH {df['K_VRH'].min():.0f} to {df['K_VRH'].max():.0f} GPa")


if __name__ == "__main__":
    main()
