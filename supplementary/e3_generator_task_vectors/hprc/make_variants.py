"""E3 step C4a: build generator model folders from the base and task vectors.

A task vector is tau = fine-tuned weights - base weights for one RL run. Each
variant below is the base plus some combination of task vectors, written as a
folder the backbone's own loader can read:

  mg    config.yaml + checkpoints/last.ckpt          (stock MatterGen sampler)
  cf    hparams.yaml + epoch=*.ckpt + scaler files   (the loop's CrystalFlowSuite)
  adit  ldm.ckpt; the frozen autoencoder stays in the base folder (the loop's ADiTSuite)

For cf and adit the variant checkpoint is the base Lightning checkpoint with its
state dict changed and the optimizer state dropped, so it loads through the same
code path as the base did in the loop. A task vector covers the tensors present
in both state dicts; anything else keeps its base value.

  base               the published model, untouched
  bm_seed17          one bulk-modulus run, as fine-tuned         (what RL achieved)
  hcap_seed17        one heat-capacity run, as fine-tuned
  bm_mean5           mean bulk-modulus vector over five seeds    (merging across seeds)
  hcap_mean5         mean heat-capacity vector over five seeds
  sum_seed17         both single-seed vectors added              (task arithmetic)
  sum_mean5          both mean vectors added
  bm_seed17_rank8    the single-seed vector cut to rank 8 per weight matrix  (compression)
  bm_seed17_rank32   the same at rank 32
  bm_seed17_neg      the single-seed vector subtracted           (negation)
  bm_mean5_x3        three times the mean vector                 (scaling)

Runs wherever the checkpoints are (a cluster or a laptop). Existing variants are kept.

    python make_variants.py --base-dir <mattergen_base> --finetuned <finetuned_diffusion> --out <variants>
    python make_variants.py --backbone cf   --base-dir <.../DNG-mp-20>       --finetuned <...> --out <variants_cf>
    python make_variants.py --backbone adit --base-dir <.../checkpoints/adit> --finetuned <...> --out <variants_adit>
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path

import torch

RUN = r"(bm|hcap)_p3v4_(?:bm_)?{backbone}_(accel|baseline)_seed(\d+)_(\d+)"
FINETUNED_FILE = {"mg": "last.ckpt", "cf": "last.ckpt", "adit": "ldm_finetuned.ckpt"}
DROP = ("optimizer_states", "lr_schedulers")  # not needed to sample, and half the file


def alias_adit_package() -> None:
    """The released ADiT checkpoint was pickled when its package was called `src`; the copy on
    the cluster is called `adit`. Make the old names resolve, as the loop's ADiTSuite does."""
    import importlib
    import os
    import sys

    repo = os.environ.get("ADIT_REPO")
    if repo and repo not in sys.path:
        sys.path.insert(0, repo)
    import adit

    sys.modules.setdefault("src", adit)
    for tail in ("models", "data", "utils", "tools", "eval"):
        try:
            sys.modules.setdefault(f"src.{tail}", importlib.import_module(f"adit.{tail}"))
        except ImportError:
            pass


def base_checkpoint(backbone: str, base_dir: Path) -> Path:
    if backbone == "mg":
        return base_dir / "checkpoints" / "last.ckpt"
    if backbone == "adit":
        return base_dir / "ldm.ckpt"
    epochs = sorted(base_dir.glob("epoch=*.ckpt"), key=lambda f: int(f.name.split("-")[0].split("=")[1]))
    if not epochs:
        raise SystemExit(f"no epoch=*.ckpt under {base_dir}")
    return epochs[-1]  # the file CrystalFlowSuite.load_model picks


def write_variant(backbone: str, base_dir: Path, base_file: Path, base_ckpt: dict, sd: dict, folder: Path) -> Path:
    if backbone == "mg":
        (folder / "checkpoints").mkdir(parents=True, exist_ok=True)
        shutil.copy2(base_dir / "config.yaml", folder / "config.yaml")
        target = folder / "checkpoints" / "last.ckpt"
        torch.save({"state_dict": sd}, target)
        return target
    folder.mkdir(parents=True, exist_ok=True)
    if backbone == "cf":
        for extra in list(base_dir.glob("*.yaml")) + list(base_dir.glob("*.pt")):
            shutil.copy2(extra, folder / extra.name)
    target = folder / base_file.name
    torch.save({**{k: v for k, v in base_ckpt.items() if k not in DROP}, "state_dict": sd}, target)
    return target


def floats(sd):
    return {k: v for k, v in sd.items() if torch.is_tensor(v) and v.is_floating_point()}


def low_rank(tau: dict, rank: int) -> dict:
    out = {}
    for k, t in tau.items():
        if t.dim() >= 2 and min(t.shape[0], t[0].numel()) > rank:
            u, s, vh = torch.linalg.svd(t.reshape(t.shape[0], -1).double(), full_matrices=False)
            out[k] = ((u[:, :rank] * s[:rank]) @ vh[:rank]).reshape(t.shape).to(t.dtype)
        else:
            out[k] = t.clone()
    return out


def combine(*terms):
    """terms: (coefficient, tau) pairs -> one tau."""
    keys = terms[0][1].keys()
    return {k: sum(c * t[k] for c, t in terms) for k in keys}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--base-dir", type=Path, required=True)
    parser.add_argument("--finetuned", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--policy", default="baseline", choices=("baseline", "accel"))
    parser.add_argument("--seed", type=int, default=17)
    parser.add_argument("--backbone", default="mg", choices=tuple(FINETUNED_FILE))
    args = parser.parse_args()

    run_name = re.compile(RUN.format(backbone=args.backbone))
    ft_file = FINETUNED_FILE[args.backbone]
    base_file = base_checkpoint(args.backbone, args.base_dir)
    if args.backbone == "adit":
        alias_adit_package()
    base_ckpt = torch.load(base_file, map_location="cpu", weights_only=False)
    base = base_ckpt["state_dict"]
    base_f = floats(base)
    covered = None
    taus: dict[str, dict[int, dict]] = {"bm": {}, "hcap": {}}
    used = []
    for folder in sorted(args.finetuned.iterdir()):
        m = run_name.fullmatch(folder.name)
        if not m or m.group(2) != args.policy or not (folder / ft_file).exists():
            continue
        target, seed = m.group(1), int(m.group(3))
        if seed in taus[target]:  # a resubmission of the same seed: keep the later job id
            continue
        sd = torch.load(folder / ft_file, map_location="cpu", weights_only=False)["state_dict"]
        if covered is None:
            covered = [k for k in base_f if k in sd and sd[k].shape == base_f[k].shape]
            print(f"task vector covers {len(covered)} of {len(base_f)} floating tensors of the base; "
                  f"{len([k for k in sd if k not in base])} fine-tuned tensors have no base counterpart")
        taus[target][seed] = {k: sd[k].float() - base_f[k].float() for k in covered}
        used.append(folder.name)
        if target == "bm" and seed == args.seed:
            single = {k: sd[k] for k in covered}
    for target in taus:
        if args.seed not in taus[target]:
            raise SystemExit(f"no {target} {args.policy} run with seed {args.seed}; have {sorted(taus[target])}")
    print(f"task vectors: bm seeds {sorted(taus['bm'])}, hcap seeds {sorted(taus['hcap'])}")

    def mean(target):
        runs = list(taus[target].values())
        return combine(*[(1.0 / len(runs), t) for t in runs])

    bm, hc = taus["bm"][args.seed], taus["hcap"][args.seed]
    bm_mean, hc_mean = mean("bm"), mean("hcap")
    recipes = {
        "base": None,
        f"bm_seed{args.seed}": bm,
        f"hcap_seed{args.seed}": hc,
        "bm_mean5": bm_mean,
        "hcap_mean5": hc_mean,
        f"sum_seed{args.seed}": combine((1.0, bm), (1.0, hc)),
        "sum_mean5": combine((1.0, bm_mean), (1.0, hc_mean)),
        f"bm_seed{args.seed}_rank8": low_rank(bm, 8),
        f"bm_seed{args.seed}_rank32": low_rank(bm, 32),
        f"bm_seed{args.seed}_neg": combine((-1.0, bm)),
        "bm_mean5_x3": combine((3.0, bm_mean)),
    }
    base_norm = sum(float((v.float() ** 2).sum()) for v in base_f.values()) ** 0.5
    # Norm of the base over the tensors RL touched: cf and adit carry large fixed buffers.
    touched = [k for k, t in bm.items() if float(t.abs().max()) > 0]
    touched_norm = sum(float((base_f[k].float() ** 2).sum()) for k in touched) ** 0.5
    rebuilt = max(float((base_f[k].float() + bm[k] - single[k].float()).abs().max()) for k in bm)
    print(f"base + tau against the fine-tuned checkpoint (bm seed {args.seed}): max abs difference {rebuilt:.2e}")
    manifest = {"backbone": args.backbone, "base_checkpoint": str(base_file), "policy": args.policy,
                "seed": args.seed, "runs_used": used, "tensors_in_task_vector": len(bm),
                "tensors_changed_by_rl": len(touched), "variants": {}}
    args.out.mkdir(parents=True, exist_ok=True)
    for name, tau in recipes.items():
        folder = args.out / name
        norm = 0.0 if tau is None else sum(float((v.float() ** 2).sum()) for v in tau.values()) ** 0.5
        manifest["variants"][name] = {"relative_norm_of_change": norm / base_norm,
                                      "relative_norm_over_changed_tensors": norm / touched_norm}
        if (folder / "DONE").exists() or (args.backbone == "mg" and (folder / "checkpoints" / "last.ckpt").exists()):
            print(f"keep  {name}")
            continue
        sd = {k: v.clone() for k, v in base.items()}
        if tau is not None:
            for k, t in tau.items():
                sd[k] = (base_f[k].float() + t).to(base[k].dtype)
        write_variant(args.backbone, args.base_dir, base_file, base_ckpt, sd, folder)
        (folder / "DONE").write_text("complete\n")  # a checkpoint cut off mid-write is rebuilt
        print(f"wrote {name}  relative norm of change {norm / base_norm:.5f} "
              f"({norm / touched_norm:.5f} of the tensors RL changed)", flush=True)
    (args.out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    (args.out / "variants.txt").write_text("\n".join(recipes) + "\n")


if __name__ == "__main__":
    main()
