"""Benchmark: Ti-alloy YS, UTS, hardness — real data, 10D, 3-obj.

Source: Salvador, C.A.F., Maia, E.L., Costa, F.H., Escobar, J.D. & Oliveira, J.P.
"A compilation of experimental data on the mechanical properties and
microstructural features of Ti-alloys." Scientific Data 9:188 (2022).
DOI: 10.1038/s41597-022-01283-9
Data: https://zenodo.org/records/6089749  (dax-ti-static.csv, CC-BY-4.0).

282 Ti-based alloy entries with continuous composition (Ti, Nb, Ta, Mo, Zr,
Cu, Hf, Al, V, Sn, Cr, Fe, ...). Three objectives (negated for maximisation):
  - YS  (yield strength, MPa)
  - UTS (ultimate tensile strength, MPa)
  - HV  (Vickers hardness)

Inputs (10D, X ∈ [0,1]^10): Magpie composition descriptor PCA-reduced and
min-max-normalised. Lossless w.r.t. all alloying elements present in the
dataset (avoids the silent Nb / Ta mass loss of a fixed-element basis).

Surrogate: Random Forest (200 trees) on (Magpie-PCA-10D → [YS, UTS, HV]).
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
    csv = DATA_DIR / "ti_alloy_dax-ti-static.csv"
    df = pd.read_csv(csv)
    df = df[df["YS"].notna() & df["UTS"].notna() & df["HV"].notna()].copy()
    feats = composition_to_magpie_features(df["formula"].astype(str).tolist())
    Y_full = df[["YS", "UTS", "HV"]].values
    Xu, valid, pca, lo, hi = reduce_pca_unit(feats, n_components=_N_PCA)
    Y = Y_full[valid]
    return DatasetSurrogate(Xu, Y), pca, lo, hi


def ti_alloy_3obj(X: np.ndarray) -> np.ndarray:
    """Ti-alloy: Magpie-PCA-10D → (-YS, -UTS, -HV)."""
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
