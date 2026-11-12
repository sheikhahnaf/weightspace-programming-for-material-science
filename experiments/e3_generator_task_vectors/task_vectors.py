"""E3 steps C2 and C3: what did RL fine-tuning change in the generator's weights?

For every fine-tuned checkpoint of one backbone, the task vector is
tau = fine-tuned weights - base weights. This script reports

  per run     norm of tau relative to the base weights; share of tau's energy per module
  per matrix  rank needed to hold 90% of the change's energy (singular values), against
              the same number for the base weight matrix
  between runs  cosine similarity of the full task vectors, summarised by whether two
              runs share target, policy and seed

Checkpoints are read from data/large/finetuned_diffusion/ (download_checkpoints.py).

    python experiments/e3_generator_task_vectors/task_vectors.py --backbone mg
    python experiments/e3_generator_task_vectors/task_vectors.py --backbone cf     # base copied from FASTER, see README
    python task_vectors.py --backbone adit --base <ldm.ckpt> --finetuned <dir> --out <dir>   # on FASTER

Only tensors present in both the base and the fine-tuned state dict are compared (the ADiT
fine-tunes hold the denoiser only; the frozen autoencoder is not in them). CrystalFlow and
ADiT keep large fixed buffers in the state dict, so besides the norm relative to all
floating tensors (the MatterGen number) the norm relative to the tensors that changed in at
least one run is reported, and ranks are taken only over matrices that changed.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
from collections import defaultdict
from pathlib import Path

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[2]
CKPT = ROOT / "data" / "large" / "finetuned_diffusion"
BASES = {
    "mg": "~/.cache/huggingface/hub/models--microsoft--mattergen/snapshots/*/checkpoints/mattergen_base/checkpoints/last.ckpt",
    "cf": str(ROOT / "data" / "large" / "base_checkpoints" / "crystalflow" / "DNG-mp-20" / "epoch=*.ckpt"),
    "adit": str(ROOT / "data" / "large" / "base_checkpoints" / "adit" / "ldm.ckpt"),
}
# Which parts of a state-dict key name the module, for the share-of-change table.
MODULE_PARTS = {"mg": slice(3, 5), "cf": slice(0, 2), "adit": slice(0, 3)}
RUN = re.compile(r"(bm|hcap)_p3v4_(?:bm_)?(mg|cf|adit)_(accel|baseline)_seed(\d+)_(\d+)")


def state(path: str) -> dict[str, torch.Tensor]:
    ckpt = torch.load(path, map_location="cpu", weights_only=False)
    sd = ckpt.get("state_dict", ckpt)
    return {k: v.float() for k, v in sd.items() if torch.is_tensor(v) and v.is_floating_point()}


def rank90(matrix: torch.Tensor) -> int:
    s = torch.linalg.svdvals(matrix.reshape(matrix.shape[0], -1).double())
    energy = torch.cumsum(s**2, 0) / (s**2).sum().clamp_min(1e-300)
    return int((energy < 0.9).sum().item()) + 1


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--backbone", choices=tuple(BASES), default="mg")
    parser.add_argument("--base", default=None, help="path to the base checkpoint (default: local copy)")
    parser.add_argument("--finetuned", type=Path, default=CKPT, help="folder with one sub-folder per run")
    parser.add_argument("--out", type=Path, default=Path(__file__).resolve().parent / "results")
    args = parser.parse_args()

    found = glob.glob(os.path.expanduser(args.base or BASES[args.backbone]))
    if not found:
        raise SystemExit(f"no base checkpoint for {args.backbone}: {args.base or BASES[args.backbone]}")
    base_path = found[0]
    base = state(base_path)
    runs = []
    for folder in sorted(args.finetuned.iterdir()):
        m = RUN.fullmatch(folder.name)
        if m and m.group(2) == args.backbone:
            files = list(folder.glob("*.ckpt"))
            if files:
                runs.append({"name": folder.name, "target": m.group(1), "policy": m.group(3),
                             "seed": int(m.group(4)), "path": str(files[0])})
    print(f"{len(runs)} runs of {args.backbone}; base {base_path}")

    if not runs:
        raise SystemExit(f"no fine-tuned {args.backbone} checkpoints under {args.finetuned}")
    first = state(runs[0]["path"])
    keys = [k for k in base if base[k].numel() > 1 and k in first and first[k].shape == base[k].shape]
    skipped = sorted(k for k in base if base[k].numel() > 1 and k not in keys)
    del first
    base_norm2 = sum(float((base[k] ** 2).sum()) for k in keys)
    n = len(runs)
    gram = np.zeros((n, n))
    module_energy = [defaultdict(float) for _ in runs]
    rank_tau, rank_base, rel_by_key = defaultdict(list), {}, defaultdict(list)
    matrices = [k for k in keys if base[k].dim() >= 2 and min(base[k].shape[0], base[k][0].numel()) >= 32]

    taus: list[dict[str, torch.Tensor]] = []
    for i, run in enumerate(runs):
        ft = state(run["path"])
        tau = {k: ft[k] - base[k] for k in keys}
        taus.append(tau)
        run["rel_norm"] = float(np.sqrt(sum(float((tau[k] ** 2).sum()) for k in keys) / base_norm2))
        for k in keys:
            energy = float((tau[k] ** 2).sum())
            module_energy[i][".".join(k.split(".")[MODULE_PARTS[args.backbone]])] += energy
            rel_by_key[k].append(np.sqrt(energy / max(float((base[k] ** 2).sum()), 1e-30)))
        for k in matrices:
            if float(tau[k].abs().max()) > 0:  # an untouched buffer has no spectrum
                rank_tau[k].append(rank90(tau[k]))
        print(f"  [{i + 1}/{n}] {run['name']} relative norm {run['rel_norm']:.5f}", flush=True)
    matrices = [k for k in matrices if rank_tau[k]]
    for k in matrices:
        rank_base[k] = rank90(base[k])
    changed = [k for k in keys if max(rel_by_key[k]) > 0]
    changed_norm2 = sum(float((base[k] ** 2).sum()) for k in changed)
    for run in runs:
        run["rel_norm_changed_tensors"] = float(run["rel_norm"] * np.sqrt(base_norm2 / changed_norm2))
    for k in keys:  # Gram matrix one tensor at a time, to stay within memory
        stack = torch.stack([t[k].flatten() for t in taus]).double()
        gram += (stack @ stack.T).numpy()
    norms = np.sqrt(np.diag(gram))
    cosine = gram / np.outer(norms, norms)

    groups = defaultdict(list)
    for i in range(n):
        for j in range(i + 1, n):
            a, b = runs[i], runs[j]
            label = ("same target" if a["target"] == b["target"] else "different target") + ", " + (
                "same policy" if a["policy"] == b["policy"] else "different policy") + ", " + (
                "same seed" if a["seed"] == b["seed"] else "different seed")
            groups[label].append(float(cosine[i, j]))

    full = np.array([min(base[k].shape[0], base[k][0].numel()) for k in matrices])
    rt = np.array([np.mean(rank_tau[k]) for k in matrices])
    rb = np.array([rank_base[k] for k in matrices])
    totals = defaultdict(float)
    for me in module_energy:
        total = sum(me.values())
        for module, energy in me.items():
            totals[module] += energy / total / n
    summary = {
        "backbone": args.backbone,
        "runs": [{k: v for k, v in r.items() if k != "path"} for r in runs],
        "base_checkpoint": os.path.basename(base_path),
        "tensors_compared": len(keys),
        "tensors_changed_in_some_run": len(changed),
        "base_tensors_absent_from_fine_tunes": len(skipped),
        "relative_norm": {"mean": float(np.mean([r["rel_norm"] for r in runs])),
                          "min": float(np.min([r["rel_norm"] for r in runs])),
                          "max": float(np.max([r["rel_norm"] for r in runs]))},
        "relative_norm_over_changed_tensors": {
            "mean": float(np.mean([r["rel_norm_changed_tensors"] for r in runs])),
            "min": float(np.min([r["rel_norm_changed_tensors"] for r in runs])),
            "max": float(np.max([r["rel_norm_changed_tensors"] for r in runs]))},
        "share_of_change_by_module": dict(sorted(totals.items(), key=lambda kv: -kv[1])),
        "rank_for_90pct_energy": {
            "matrices": len(matrices),
            "task_vector_rank_over_full_rank": {"mean": float((rt / full).mean()), "median": float(np.median(rt / full))},
            "base_weight_rank_over_full_rank": {"mean": float((rb / full).mean()), "median": float(np.median(rb / full))},
            "matrices_where_change_is_lower_rank_than_base": int((rt < rb).sum()),
        },
        "cosine_between_runs": {g: {"n": len(v), "mean": float(np.mean(v)), "min": float(np.min(v)),
                                    "max": float(np.max(v))} for g, v in sorted(groups.items())},
        "cosine_matrix": cosine.round(4).tolist(),
    }
    out = args.out
    out.mkdir(parents=True, exist_ok=True)
    (out / f"task_vectors_{args.backbone}.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({k: v for k, v in summary.items() if k not in ("runs", "cosine_matrix")}, indent=2))


if __name__ == "__main__":
    main()
