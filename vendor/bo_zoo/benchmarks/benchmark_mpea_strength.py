"""Benchmark: MPEA strength vs ductility (real materials data, 10D, 2-obj).

Source: Borg, C.K.H., et al. "Expanded dataset of mechanical properties and
observed phases of multi-principal element alloys." Scientific Data 7:430 (2020).
DOI: 10.1038/s41597-020-00768-9
Repo: https://github.com/CitrineInformatics/MPEA_dataset (CC-BY-4.0).

Dataset: ~1545 alloy entries with composition + mechanical properties.
After filtering for entries with both yield-strength (YS) and elongation
measured at room temperature, ~470 alloys remain.

Inputs (10D, X ∈ [0,1]^10): PCA-reduced Magpie composition descriptor
(matminer `ElementProperty('magpie')`, 132 features → 10 PCs, then
min-max normalised to [0,1]). This encoding is **lossless** across all
elements present in the dataset (Ti, Nb, Zr, Ta, Hf, Mo, V, W, etc.) —
unlike a fixed N-element basis which silently drops mass.

Objectives (negated for maximisation):
  -YS_MPa   yield strength (MPa)
  -elong    elongation (%)

The objective is a Random Forest (200 trees) on (Magpie-PCA-10D → [YS, elong]).
"""
from __future__ import annotations

from functools import lru_cache

import numpy as np
import pandas as pd
import torch

from _dataset_surrogate import (
    DatasetSurrogate, DATA_DIR,
    composition_to_magpie_features, reduce_pca_unit,
)

_N_PCA = 10


@lru_cache(maxsize=1)
def _build():
    csv = DATA_DIR / "MPEA_dataset.csv"
    df = pd.read_csv(csv)
    # Locate the awkwardly-named columns once
    temp_col = next(c for c in df.columns if "Test temperature" in c)
    ys_col = next(c for c in df.columns if "YS (" in c)
    el_col = next(c for c in df.columns if "Elongation (%)" in c)
    df = df[df[temp_col].between(20, 30, inclusive="both")
            & df[ys_col].notna() & df[el_col].notna()].copy()
    feats = composition_to_magpie_features(df["FORMULA"].astype(str).tolist())
    Y_full = df[[ys_col, el_col]].values
    Xu, valid, pca, lo, hi = reduce_pca_unit(feats, n_components=_N_PCA)
    Y = Y_full[valid]
    return DatasetSurrogate(Xu, Y), pca, lo, hi


def mpea_strength(X: np.ndarray) -> np.ndarray:
    """MPEA: Magpie-PCA-10D → (-YS_MPa, -elongation_%)."""
    surr, _pca, _lo, _hi = _build()
    Xn = np.asarray(X, dtype=np.float64).reshape(-1, _N_PCA)
    Xn = np.clip(Xn, 0.0, 1.0)
    return -surr.predict(Xn)


def compute_hv(Y: np.ndarray, ref_point: np.ndarray) -> float:
    from bo_zoo.utils.pareto import compute_hypervolume
    return compute_hypervolume(
        torch.tensor(Y, dtype=torch.float64),
        torch.tensor(ref_point, dtype=torch.float64),
    )
