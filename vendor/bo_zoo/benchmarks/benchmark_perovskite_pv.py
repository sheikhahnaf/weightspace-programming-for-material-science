"""Benchmark: Sun 2019 perovskite-inspired PV — composition + processing (real data, 13D, 2-obj).

Source: Sun, S., Hartono, N.T.P., Ren, Z.D., et al. "Accelerated Development
of Perovskite-Inspired Materials via High-Throughput Synthesis and Machine-
Learning Diagnosis." Joule 3:1437 (2019).
DOI: 10.1016/j.joule.2019.05.014
Data: https://github.com/acceleratedmaterials/campaign1 (Tables S2/S3, MIT licence).

76 hybrid lead-free perovskite-inspired compositions with measured Tauc-plot
direct + indirect bandgaps and full processing conditions.

Inputs (13D, X ∈ [0, 1]^13):
  X[0:10]  — Magpie composition descriptor PCA-reduced and min-max
             normalised (parses Cs3Bi2I9, (MA)CuBr2Cl2, FAPbI3:MAPbBr3=9:1
             style mixed-compound strings via pymatgen + a custom mix parser)
  X[10]    — preheat temperature (rescaled to [25, 150] °C)
  X[11]    — annealing temperature (rescaled to [70, 200] °C)
  X[12]    — annealing time (rescaled to [5, 60] min)

Objectives (negated for maximisation):
  -|E_g_direct - 1.5|              (target bandgap 1.5 eV)
  -|E_g_direct - E_g_indirect|     (alignment — direct ≈ indirect → PV-friendly)

Surrogate: Random Forest (200 trees) fitted on the joined Tables S2 + S3
(matched on Sample #) with the 13D feature vector.
"""
from __future__ import annotations

from functools import lru_cache

import numpy as np
import pandas as pd
import torch

from _dataset_surrogate import (
    DatasetSurrogate, DATA_DIR,
    composition_to_magpie_features, reduce_pca_unit, parse_compound_mix,
)

# Target single-junction-PV bandgap
_E_G_TARGET = 1.5

# Processing-parameter ranges (true physical units; BO drives [0,1] then rescales)
_PROC_LO = np.array([ 25.0,  70.0,   5.0])   # preheat (°C), anneal (°C), anneal time (min)
_PROC_HI = np.array([150.0, 200.0,  60.0])
_N_PROC = 3
_N_PCA = 10
_N_VAR = _N_PCA + _N_PROC


def _to_celsius(val) -> float:
    """Parse a processing-temperature cell. 'RT' / 'rt' → 25; numeric → float; else NaN."""
    if isinstance(val, (int, float)):
        return float(val) if pd.notna(val) else np.nan
    if not isinstance(val, str):
        return np.nan
    s = val.strip().lower()
    if s in ("rt", "room temperature", "room temp"):
        return 25.0
    try:
        return float(s)
    except ValueError:
        return np.nan


@lru_cache(maxsize=1)
def _build():
    csv_s2 = DATA_DIR / "perovskite_Sample_ID_Table_S2.csv"
    csv_s3 = DATA_DIR / "perovskite_Processing_Conditions_Table_S3.csv"
    s2 = pd.read_csv(csv_s2, header=1, encoding="latin-1")
    s3 = pd.read_csv(csv_s3, header=1, encoding="latin-1")
    s2 = s2.rename(columns={s2.columns[0]: "Sample"})
    s3 = s3.rename(columns={s3.columns[0]: "Sample"})
    s2["Sample"] = pd.to_numeric(s2["Sample"], errors="coerce")
    s3["Sample"] = pd.to_numeric(s3["Sample"], errors="coerce")
    df = s2.merge(s3, on="Sample", how="inner", suffixes=("", "_s3"))
    df = df[df["Direct"].notna() & df["Indirect"].notna()
            & df["Synthesized Compound"].notna()].copy()

    rows: list[dict] = []
    for _, r in df.iterrows():
        try:
            d, i = float(r["Direct"]), float(r["Indirect"])
        except Exception:
            continue
        if not (0.5 < d < 5 and 0.5 < i < 5):
            continue
        preheat_c = _to_celsius(r.get("Preheat"))
        anneal_c = _to_celsius(r.get("Annealing"))
        try:
            anneal_min = float(r.get("Annealing time/min"))
        except Exception:
            anneal_min = np.nan
        if np.isnan([preheat_c, anneal_c, anneal_min]).any():
            continue
        rows.append({
            "compound": str(r["Synthesized Compound"]),
            "preheat": preheat_c, "anneal": anneal_c, "anneal_min": anneal_min,
            "d": d, "i": i,
        })
    if not rows:
        raise RuntimeError("Failed to parse any perovskite rows.")

    # Featurise compounds (uses pymatgen via parse_compound_mix for the
    # mixed-compound + percent-additive syntax of Sun 2019).
    formulas = [row["compound"] for row in rows]
    feats = composition_to_magpie_features(formulas, parse_fn=parse_compound_mix)
    Xu, valid, pca, lo, hi = reduce_pca_unit(feats, n_components=_N_PCA)

    # Append processing parameters (scaled to [0, 1]) AFTER PCA; processing
    # is independent of composition, so it should not feed into PCA.
    rows_v = [r for r, ok in zip(rows, valid) if ok]
    proc = np.stack([
        (np.array([r["preheat"], r["anneal"], r["anneal_min"]]) - _PROC_LO)
        / (_PROC_HI - _PROC_LO)
        for r in rows_v
    ])
    proc = np.clip(proc, 0.0, 1.0)
    X_full = np.concatenate([Xu, proc], axis=1)

    Y_min = np.stack([
        np.array([abs(r["d"] - _E_G_TARGET) for r in rows_v]),
        np.array([abs(r["d"] - r["i"]) for r in rows_v]),
    ], axis=1)
    return DatasetSurrogate(X_full, Y_min), pca, lo, hi


def perovskite_pv(X: np.ndarray) -> np.ndarray:
    """Sun 2019 perovskite: Magpie-PCA-10D + processing-3D → 2-obj.

    Returns -|E_g_direct - 1.5| and -|E_direct - E_indirect| so BO maximisation
    aligns with the underlying "minimise distance from target" formulation.
    """
    surr, _pca, _lo, _hi = _build()
    Xn = np.asarray(X, dtype=np.float64).reshape(-1, _N_VAR)
    Xn = np.clip(Xn, 0.0, 1.0)
    Y_min = surr.predict(Xn)
    return -Y_min


def compute_hv(Y: np.ndarray, ref_point: np.ndarray) -> float:
    from bo_zoo.utils.pareto import compute_hypervolume
    return compute_hypervolume(
        torch.tensor(Y, dtype=torch.float64),
        torch.tensor(ref_point, dtype=torch.float64),
    )
