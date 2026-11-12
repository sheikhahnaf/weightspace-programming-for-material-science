"""E3 step C4b: sample crystals from one generator variant and score them.

Sampling uses a fixed seed, so every variant of a backbone starts from the same
noise: the stock MatterGen generator for mg, and for cf and adit the published
loop's own model suites and samplers (CrystalFlowSuite, ADiTSuite), imported
read-only from the loop's folder on the cluster (LOOP_PROJECT, LOOP_PRISTINE in
env.sh). The loop drew four times the crystals it needed and filtered them; here
exactly --n are drawn and none is filtered. Scoring uses the two oracles of the published loop,
vendored unmodified: eSEN-30M-OAM bulk modulus (relax, seven strains,
Birch-Murnaghan) and phonon heat capacity at 300 K.

Resumable: the samples are generated once; scores.csv gains one row per
structure and finished rows are skipped on a rerun.

    python sample_and_score.py --variant-dir <variants>/bm_mean5 --out <results>/bm_mean5 --n 128
    python sample_and_score.py --backbone cf --variant-dir <variants_cf>/bm_mean5 --out <results_cf>/bm_mean5 --n 128
"""

from __future__ import annotations

import argparse
import csv
import json
import os
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


def load_loop_model(backbone: str, variant_dir: Path, batch: int):
    """The loop's suite for cf or adit, pointed at a variant folder. Returns (model, sampler)."""
    import torch
    from omegaconf import OmegaConf

    for folder in (os.environ.get("LOOP_PRISTINE"), os.environ.get("LOOP_PROJECT")):  # project first on the path
        if folder and folder not in sys.path:
            sys.path.insert(0, folder)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    common = dict(sample_cfg=OmegaConf.create({"batch_size": batch, "num_batches": 1}),
                  finetune_cfg=OmegaConf.create({"lr": 1e-5, "epochs": 3, "batch_size": batch, "timesteps": 4,
                                                 "accum_steps": 1, "sigma": 1e-3}),  # required by the suite, unused here
                  device=device)
    if backbone == "cf":
        from src.p3_models.crystalflow_suite import CrystalFlowSuite
        suite = CrystalFlowSuite(model_name="crystalflow_mp20", model_path=str(variant_dir.resolve()), **common)
    else:
        from src.p3_models.adit_suite import ADiTSuite
        suite = ADiTSuite(model_name="adit_mp20", dit_checkpoint=str(variant_dir.resolve() / "ldm.ckpt"),
                          vae_checkpoint=os.environ["ADIT_VAE"], **common)
    model = suite.load_model().to(device).eval()
    interpolant = getattr(model, "interpolant", None)  # ADiT draws its noise on interpolant.device
    if interpolant is not None and hasattr(interpolant, "device"):
        interpolant.device = model.device
    return model, suite.get_sampler()


def generate_loop(backbone: str, variant_dir: Path, out: Path, n: int, batch: int, seed: int) -> Path:
    target = out / "generated_crystals.extxyz"
    if target.exists():
        return target
    import torch
    from ase.io import write
    from pymatgen.io.ase import AseAtomsAdaptor

    model, sampler = load_loop_model(backbone, variant_dir, batch)
    torch.manual_seed(seed)
    np.random.seed(seed)
    start, structures = time.time(), []
    for first in range(0, n, batch):
        _, chunk = sampler.generate(model, batch_size=min(batch, n - first), num_batches=1, oversample_factor=1)
        structures += chunk
    # The loop's samplers drop a crystal they cannot build, without saying which one. Sample
    # indices then stop lining up between variants, and paired tests must not be used.
    aligned = len(structures) == n
    atoms = []
    for i, structure in enumerate(structures):
        a = AseAtomsAdaptor.get_atoms(structure)
        a.info.update({"sample_index": i, "n_requested": n, "n_returned": len(structures), "aligned": aligned})
        atoms.append(a)
    tmp = out / "generated_crystals.partial.extxyz"
    write(tmp, atoms, format="extxyz")
    tmp.rename(target)
    (out / "sampling_seconds.txt").write_text(f"{time.time() - start:.1f}\n")
    (out / "sampling_meta.json").write_text(json.dumps({
        "backbone": backbone, "variant": variant_dir.name, "seed": seed, "n_requested": n,
        "n_returned": len(structures), "aligned": aligned, "batch": batch,
        "sampler": type(sampler).__name__, "model": type(model).__name__}, indent=2) + "\n")
    print(f"sampled {len(structures)} of {n} crystals in {time.time() - start:.0f} s", flush=True)
    del model
    torch.cuda.empty_cache()
    return target


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--variant-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--n", type=int, default=128)
    parser.add_argument("--batch", type=int, default=64)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--backbone", default="mg", choices=("mg", "cf", "adit"))
    parser.add_argument("--skip-cp", action="store_true")
    parser.add_argument("--limit", type=int, default=None, help="score only the first k structures")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    from ase.io import read
    if args.backbone == "mg":
        samples = generate(args.variant_dir, args.out, args.n, args.batch, args.seed)
    else:
        samples = generate_loop(args.backbone, args.variant_dir, args.out, args.n, args.batch, args.seed)
    structures = read(samples, index=":")
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
