"""Download the RL-fine-tuned generator checkpoints (E3, step C1).

Source: Hugging Face `SheikhAhnaf/apu-synthesizability-checkpoints`, folder
`finetuned_diffusion/` (59 runs, about 15 GB). Files land in
`data/large/finetuned_diffusion/`, which is not tracked in git. Re-running
skips files that are already complete, so an interrupted download resumes.

    python supplementary/e3_generator_task_vectors/download_checkpoints.py --backbone mg
    python supplementary/e3_generator_task_vectors/download_checkpoints.py --backbone cf adit
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from huggingface_hub import HfApi, hf_hub_download

REPO = "SheikhAhnaf/apu-synthesizability-checkpoints"
ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / "data" / "large" / "finetuned_diffusion"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--backbone", nargs="+", choices=("mg", "cf", "adit"), default=["mg"])
    args = parser.parse_args()

    files = [
        f for f in HfApi().list_repo_tree(REPO, path_in_repo="finetuned_diffusion", recursive=True)
        if getattr(f, "size", None)
    ]
    wanted = [
        f for f in files
        if f.path.endswith("MANIFEST.md") or any(f"_{b}_" in f.path for b in args.backbone)
    ]
    TARGET.mkdir(parents=True, exist_ok=True)
    listing = []
    for i, f in enumerate(wanted, 1):
        local = TARGET / Path(f.path).relative_to("finetuned_diffusion")
        if not (local.exists() and local.stat().st_size == f.size):
            hf_hub_download(REPO, f.path, local_dir=TARGET.parent)
        listing.append({"path": str(local.relative_to(ROOT)), "bytes": f.size,
                        "sha256": getattr(getattr(f, "lfs", None), "sha256", None)})
        print(f"[{i}/{len(wanted)}] {local.relative_to(ROOT)}", flush=True)
    index = Path(__file__).resolve().parent / "results" / f"downloaded_{'_'.join(sorted(args.backbone))}.json"
    index.parent.mkdir(exist_ok=True)
    index.write_text(json.dumps({"repo": REPO, "files": listing}, indent=2) + "\n")
    print(f"wrote {index.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
