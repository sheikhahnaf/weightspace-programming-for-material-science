"""E3 step C4b: sample crystals from one MatterGen variant and score them.

Sampling uses the stock MatterGen generator with a fixed seed, so every variant
starts from the same noise. Scoring uses the two oracles of the published loop,
vendored unmodified: eSEN-30M-OAM bulk modulus (relax, seven strains,
Birch-Murnaghan) and phonon heat capacity at 300 K.

Resumable: the samples are generated once; scores.csv gains one row per
structure and finished rows are skipped on a rerun.

    python sample_and_score.py --variant-dir <variants>/bm_mean5 --out <results>/bm_mean5 --n 128
"""

from __future__ import annotations

import argparse
import csv
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "vendor" / "matgen_bo" / "closed_loop" / "calculators"))
FIELDS = ["index", "formula", "n_atoms", "K_GPa", "K_seconds", "Cp_J_per_gK", "Cp_seconds"]


def generate(variant_dir: Path, out: Path, n: int, batch: int, seed: int) -> Path:
    target = out / "generated_crystals.extxyz"
    if target.exists():
        return target
    import torch
    from mattergen.common.utils.data_classes import MatterGenCheckpointInfo
    from mattergen.generator import CrystalGenerator

    torch.manual_seed(seed)
    np.random.seed(seed)
    info = MatterGenCheckpointInfo(
        model_path=variant_dir.resolve(), load_epoch="last", config_overrides=[],
        strict_checkpoint_loading=True,
    )
    generator = CrystalGenerator(
        checkpoint_info=info, properties_to_condition_on=None, batch_size=batch,
        num_batches=int(np.ceil(n / batch)), sampling_config_name="default",
        record_trajectories=False, diffusion_guidance_factor=0.0,
    )
    start = time.time()
    generator.generate(output_dir=out)
    (out / "sampling_seconds.txt").write_text(f"{time.time() - start:.1f}\n")
    return target


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--variant-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--n", type=int, default=128)
    parser.add_argument("--batch", type=int, default=64)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--skip-cp", action="store_true")
    parser.add_argument("--limit", type=int, default=None, help="score only the first k structures")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    from ase.io import read
    structures = read(generate(args.variant_dir, args.out, args.n, args.batch, args.seed), index=":")
    structures = structures[: args.limit or args.n]
    print(f"{len(structures)} structures to score", flush=True)

    scores = args.out / "scores.csv"
    done = set()
    if scores.exists():
        with scores.open() as handle:
            done = {int(row["index"]) for row in csv.DictReader(handle)}
    else:
        with scores.open("w", newline="") as handle:
            csv.DictWriter(handle, FIELDS).writeheader()

    from local_esen import LocalESEN
    from local_esen_bm import LocalESEN_BM

    bm = LocalESEN_BM(root_dir=str(args.out / "oracle_tmp"))
    cp = LocalESEN(root_dir=str(args.out / "oracle_tmp"))
    cp._calc = bm._load_calculator()  # one eSEN model for both oracles

    for i, atoms in enumerate(structures):
        if i in done:
            continue
        row = {"index": i, "formula": atoms.get_chemical_formula(), "n_atoms": len(atoms)}
        start = time.time()
        try:
            row["K_GPa"] = bm._bm_task(atoms)
        except Exception as error:
            print(f"[{i}] bulk modulus failed: {type(error).__name__}: {error}", file=sys.stderr)
            row["K_GPa"] = float("nan")
        row["K_seconds"] = round(time.time() - start, 1)
        if not args.skip_cp:
            start = time.time()
            try:
                row["Cp_J_per_gK"] = cp._phonon_task(atoms)
            except Exception as error:
                print(f"[{i}] heat capacity failed: {type(error).__name__}: {error}", file=sys.stderr)
                row["Cp_J_per_gK"] = float("nan")
            row["Cp_seconds"] = round(time.time() - start, 1)
        with scores.open("a", newline="") as handle:
            csv.DictWriter(handle, FIELDS).writerow(row)
        print(f"[{i + 1}/{len(structures)}] {row}", flush=True)


if __name__ == "__main__":
    main()
