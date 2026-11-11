"""E3 step C4a: build MatterGen model folders from the base and task vectors.

A task vector is tau = fine-tuned weights - base weights for one RL run. Each
variant below is the base plus some combination of task vectors, written as a
folder the stock MatterGen sampler can load (config.yaml + checkpoints/last.ckpt).

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

Runs wherever the checkpoints are (FASTER or a laptop). Existing variants are kept.

    python make_variants.py --base-dir <mattergen_base> --finetuned <finetuned_diffusion> --out <variants>
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path

import torch

RUN = re.compile(r"(bm|hcap)_p3v4_(?:bm_)?mg_(accel|baseline)_seed(\d+)_(\d+)")


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
    args = parser.parse_args()

    base = torch.load(args.base_dir / "checkpoints" / "last.ckpt", map_location="cpu", weights_only=False)["state_dict"]
    base_f = floats(base)
    taus: dict[str, dict[int, dict]] = {"bm": {}, "hcap": {}}
    used = []
    for folder in sorted(args.finetuned.iterdir()):
        m = RUN.fullmatch(folder.name)
        if not m or m.group(2) != args.policy or not (folder / "last.ckpt").exists():
            continue
        target, seed = m.group(1), int(m.group(3))
        if seed in taus[target]:  # a resubmission of the same seed: keep the later job id
            continue
        sd = torch.load(folder / "last.ckpt", map_location="cpu", weights_only=False)["state_dict"]
        taus[target][seed] = {k: sd[k].float() - base_f[k].float() for k in base_f}
        used.append(folder.name)
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
    manifest = {"policy": args.policy, "seed": args.seed, "runs_used": used, "variants": {}}
    args.out.mkdir(parents=True, exist_ok=True)
    for name, tau in recipes.items():
        folder = args.out / name
        norm = 0.0 if tau is None else sum(float((v.float() ** 2).sum()) for v in tau.values()) ** 0.5
        manifest["variants"][name] = {"relative_norm_of_change": norm / base_norm}
        if (folder / "checkpoints" / "last.ckpt").exists():
            print(f"keep  {name}")
            continue
        (folder / "checkpoints").mkdir(parents=True, exist_ok=True)
        shutil.copy2(args.base_dir / "config.yaml", folder / "config.yaml")
        sd = {k: v.clone() for k, v in base.items()}
        if tau is not None:
            for k, t in tau.items():
                sd[k] = (base_f[k].float() + t).to(base[k].dtype)
        torch.save({"state_dict": sd}, folder / "checkpoints" / "last.ckpt")
        print(f"wrote {name}  relative norm of change {norm / base_norm:.5f}", flush=True)
    (args.out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    (args.out / "variants.txt").write_text("\n".join(recipes) + "\n")


if __name__ == "__main__":
    main()
