"""Compute frozen ORB embeddings for a matminer dataset and save them here.

Reuses the featurizer of the published benchmark by importing it, read-only,
from the sibling repo (matgen-BO/01_static_benchmark/src/common.py): the same
orb_v3_conservative_inf_omat decoder-hook, mean-pooled per structure. PCA is
left to run_baseline.py so that it is fitted on each training split.

First run downloads the matminer dataset and the ORB checkpoint.

    python experiments/e1_surrogate_head/make_features.py \
        --dataset elastic_tensor_2015 --target K_VRH --out data/orb_elastic_K_VRH.npz
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

SIBLING = Path("/Volumes/SSD1_SMAAA/matgen-BO/01_static_benchmark/src")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--dataset", default="elastic_tensor_2015")
    parser.add_argument("--target", default="K_VRH")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--benchmark-src", type=Path, default=SIBLING)
    args = parser.parse_args()

    if not (args.benchmark_src / "common.py").exists():
        raise SystemExit(f"benchmark featurizer not found at {args.benchmark_src}")
    sys.path.insert(0, str(args.benchmark_src))
    import common  # the sibling repo's module; imported, never modified

    df = common.load_matminer_dataset(args.dataset)
    if args.target not in df.columns:
        raise SystemExit(f"{args.target!r} is not a column of {args.dataset}: {list(df.columns)}")
    # n_train only sets where prepare_dataset cuts; we keep every row and its shuffle.
    train, holdout = common.prepare_dataset(df, n_train=len(df), seed=0)
    assert len(holdout) == 0

    featurizer = common.ORBFeaturizer(n_components=0, device=args.device)  # 0 = no PCA
    X = featurizer.fit_transform(train)
    y = train[args.target].to_numpy(dtype=float)
    failed = ~np.abs(X).sum(axis=1).astype(bool)  # the featurizer zero-fills failures
    print(f"{int(failed.sum())} of {len(y)} structures failed to embed and are dropped")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(args.out, X=X[~failed], y=y[~failed])
    print(f"wrote {args.out}: X {X[~failed].shape}, y {y[~failed].shape}")


if __name__ == "__main__":
    main()
