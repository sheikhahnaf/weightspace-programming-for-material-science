"""Benchmark: Matbench bulk + shear modulus — real DFT data, 10D, 2-obj.

Source: Dunn, A., Wang, Q., Ganose, A., Dopp, D., Jain, A.
"Benchmarking materials property prediction methods: the Matbench test set
and Automatminer reference algorithm." npj Comput. Mater. 6:138 (2020).
DOI: 10.1038/s41524-020-00406-3
Tasks: matbench_log_kvrh + matbench_log_gvrh — both have 10,987 inorganic
crystal structures (same set, identical row order). Originally from the
Materials Project DFT-PBE elastic-tensor calculations.

Inputs (10D): PCA-reduced Magpie-style composition descriptor (mean +
range over the 4 most-informative element properties: AtomicWeight,
AtomicRadius, MeltingT, Electronegativity). Computed once at module load
and cached.

Objectives (negated for maximisation):
  -log10(K_VRH)   bulk modulus, log10 GPa
  -log10(G_VRH)   shear modulus, log10 GPa

Surrogate: Random Forest on the full 10,987-point dataset.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from _dataset_surrogate import DatasetSurrogate, DATA_DIR

# Cache featurised composition matrix to disk so we don't refeaturise 10K
# structures on every BO worker startup.
_CACHE = DATA_DIR / "matbench_bulk_shear_features.npz"
N_PCA = 10


def _featurise_and_cache():
    """One-time featurisation: download Matbench, extract Magpie features,
    PCA-reduce to 10D, save to disk."""
    print("[matbench_bulk_shear] First-time featurisation: this can take a few minutes ...")
    from matminer.datasets import load_dataset
    from matminer.featurizers.composition import ElementProperty
    from sklearn.decomposition import PCA

    k = load_dataset("matbench_log_kvrh")
    g = load_dataset("matbench_log_gvrh")
    assert len(k) == len(g), "Matbench k_vrh and g_vrh have different lengths"
    # Both rows are aligned (same Material Project IDs, identical order).
    comps = [s.composition for s in k["structure"].values]
    feat = ElementProperty.from_preset("magpie")
    feat.set_n_jobs(1)
    X_full = feat.featurize_many(comps, ignore_errors=True)
    X_full = np.asarray(X_full, dtype=np.float64)
    # Some rows may be all-zero on featurisation failure — drop them
    valid = ~np.all(np.isnan(X_full) | (X_full == 0), axis=1)
    X_full = X_full[valid]
    Y_full = np.stack([
        k["log10(K_VRH)"].values[valid],
        g["log10(G_VRH)"].values[valid],
    ], axis=1)
    # PCA
    pca = PCA(n_components=N_PCA, random_state=0)
    X_pca = pca.fit_transform(X_full)
    # Min-max normalise PCA features to [0,1] so BO can search a clean box
    lo = X_pca.min(axis=0)
    hi = X_pca.max(axis=0)
    X_norm = (X_pca - lo) / np.maximum(hi - lo, 1e-9)
    np.savez_compressed(_CACHE, X=X_norm, Y=Y_full,
                        pca_lo=lo, pca_hi=hi)
    print(f"[matbench_bulk_shear] Cached {len(X_norm)} featurised rows to {_CACHE}")


@lru_cache(maxsize=1)
def _build() -> DatasetSurrogate:
    if not _CACHE.exists():
        _featurise_and_cache()
    z = np.load(_CACHE)
    return DatasetSurrogate(z["X"], z["Y"], n_estimators=200)


def matbench_bulk_shear(X: np.ndarray) -> np.ndarray:
    """Matbench K+G on PCA-reduced composition: returns -log10(K), -log10(G)."""
    surr = _build()
    Xn = np.asarray(X, dtype=np.float64).reshape(-1, N_PCA)
    return -surr.predict(Xn)


def compute_hv(Y: np.ndarray, ref_point: np.ndarray) -> float:
    from bo_zoo.utils.pareto import compute_hypervolume
    return compute_hypervolume(
        torch.tensor(Y, dtype=torch.float64),
        torch.tensor(ref_point, dtype=torch.float64),
    )
