"""Shared utilities for surrogate-backed materials-data benchmarks.

For each new "real-data" benchmark we:
1. Load a public CSV (cached locally in `_datasets/`)
2. Featurise each composition into a Magpie-style descriptor and PCA-reduce
3. Fit a Random Forest regressor on (PCA features → target properties)
4. Wrap that RF as the BO objective function — the BO loop queries it as
   if it were the experiment.

This is the same convention used in BoTorch tutorials and the Olympus benchmark
suite — the dataset becomes a frozen oracle, not real-time experimentation.

Each benchmark file documents:
  * source dataset DOI + license
  * surrogate model and leave-one-out CV error
  * input parametrisation
"""
from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent / "_datasets"


# ---------------------------------------------------------------------------
# Composition parsing
# ---------------------------------------------------------------------------


def parse_composition_to_dict(formula: str) -> dict[str, float] | None:
    """Parse a chemical formula string into an element→fraction dict using
    pymatgen's parser, which correctly handles parentheses, group multipliers,
    decimal subscripts, and whitespace (`Ti0.78 Fe0.02 Zr0.06 Nb0.14`,
    `Cs3Bi2I9`, `Cs2NaSb(IBr)6`, etc.).

    Returns None if pymatgen cannot parse the string.
    """
    if not isinstance(formula, str):
        return None
    try:
        from pymatgen.core import Composition
        comp = Composition(formula.strip())
        # fraction dict — element symbol → mole fraction (sums to 1)
        return {str(el): float(comp.get_atomic_fraction(el)) for el in comp.elements}
    except Exception:
        return None


def parse_compound_mix(s: str) -> dict[str, float] | None:
    """Parse Sun-2019-style mixed-compound strings:

      "FAPbI3:MAPbBr3 = 9:1"        → 0.9 × FAPbI3 + 0.1 × MAPbBr3
      "Cs3Bi2I9:Cs3Sb2I9=9:1"       → 0.9 × Cs3Bi2I9 + 0.1 × Cs3Sb2I9
      "%5CsI, 5%RbI, FAPbI3:MAPbBr3 = 9:1"   → 5% additives + 90% mix

    For the percent-additive prefix (e.g. "5%RbI") we treat the additive as
    a per-mole-fraction increment to the final composition. Returns None on
    parse failure.

    Note: organic cations FA (formamidinium, HC(NH2)2+) and MA (methylammonium,
    CH3NH3+) are intentionally treated as single "elements" because their
    underlying C/H/N/O elements are common to both and would mask the chemistry.
    pymatgen handles this implicitly when the formula uses the group symbols.
    """
    if not isinstance(s, str):
        return None
    s = s.strip()
    if not s:
        return None

    # Step 1 — pull off any leading "X%RbI, Y%CsI, ..." additive list.
    # The Sun dataset prefixes additives this way; remainder is the main compound.
    additives: list[tuple[float, str]] = []
    main = s
    while True:
        m = re.match(r"\s*[%]?(\d+\.?\d*)%([A-Z][A-Za-z0-9.()]*)\s*,\s*", main)
        if not m:
            break
        additives.append((float(m.group(1)) / 100.0, m.group(2)))
        main = main[m.end():]

    # Step 2 — split "A:B = a:b" mix
    out: dict[str, float] = {}
    if "=" in main and ":" in main:
        try:
            compounds_str, ratios_str = main.split("=", 1)
            a_str, b_str = compounds_str.split(":", 1)
            ra, rb = ratios_str.split(":", 1)
            ra, rb = float(ra), float(rb)
            tot = ra + rb
            for compound_str, weight in [
                (a_str.strip(), ra / tot),
                (b_str.strip(), rb / tot),
            ]:
                cd = parse_composition_to_dict(compound_str)
                if cd is None:
                    return None
                for k, v in cd.items():
                    out[k] = out.get(k, 0.0) + weight * v
        except Exception:
            return None
    else:
        cd = parse_composition_to_dict(main)
        if cd is None:
            return None
        out.update(cd)

    # Step 3 — fold in additives. Each adds to the composition proportional
    # to its percent fraction; renormalise at the end.
    for frac, compound_str in additives:
        cd = parse_composition_to_dict(compound_str)
        if cd is None:
            continue
        for k, v in cd.items():
            out[k] = out.get(k, 0.0) + frac * v

    # Renormalise so element fractions sum to 1
    total = sum(out.values())
    if total <= 0:
        return None
    return {k: v / total for k, v in out.items()}


# Legacy parser (kept for backward compatibility — uses pymatgen now)
_FORMULA_TOKEN = re.compile(r"([A-Z][a-z]?)\s*([\d.]*)")


def parse_formula_fractions(formula: str, elements: list[str]) -> np.ndarray:
    """Parse a chemical formula and return fractions for the given basis,
    DROPPING any other elements and renormalising. Use only when you really
    want this lossy projection — for surrogate training prefer the full
    Magpie featurisation in `composition_to_magpie_features`.
    """
    cd = parse_composition_to_dict(formula)
    if cd is None:
        return np.full(len(elements), np.nan)
    vec = np.array([cd.get(e, 0.0) for e in elements])
    s = vec.sum()
    if s <= 0:
        return np.full(len(elements), np.nan)
    return vec / s


# ---------------------------------------------------------------------------
# Magpie + PCA composition encoder (lossless across all elements)
# ---------------------------------------------------------------------------


def composition_to_magpie_features(
    formulas: list[str],
    *,
    parse_fn=parse_composition_to_dict,
) -> np.ndarray:
    """Featurise each formula via matminer's ElementProperty('magpie') preset
    (132-D vector of element-wise statistical descriptors). Returns a
    (n, 132) numpy array; rows where the formula could not be parsed are
    filled with NaN.
    """
    from matminer.featurizers.composition import ElementProperty
    from pymatgen.core import Composition

    feat = ElementProperty.from_preset("magpie")
    feat.set_n_jobs(1)
    rows: list[np.ndarray | None] = []
    for f in formulas:
        cd = parse_fn(f)
        if not cd:
            rows.append(None)
            continue
        try:
            comp = Composition(cd)
            v = feat.featurize(comp)
            rows.append(np.asarray(v, dtype=np.float64))
        except Exception:
            rows.append(None)
    n = len(rows)
    fdim = next((len(r) for r in rows if r is not None), 132)
    out = np.full((n, fdim), np.nan, dtype=np.float64)
    for i, r in enumerate(rows):
        if r is not None:
            out[i] = r
    return out


def reduce_pca_unit(X: np.ndarray, n_components: int = 10, random_state: int = 0):
    """PCA-reduce X to `n_components` then min-max normalise each component
    to [0, 1]. Returns (X_unit, pca_model, lo, hi) so callers can apply the
    same transform to new points later if needed.
    """
    from sklearn.decomposition import PCA
    valid = ~np.any(np.isnan(X), axis=1)
    Xv = X[valid]
    pca = PCA(n_components=n_components, random_state=random_state).fit(Xv)
    Xp = pca.transform(Xv)
    lo = Xp.min(axis=0)
    hi = Xp.max(axis=0)
    rng = np.maximum(hi - lo, 1e-9)
    Xu_v = (Xp - lo) / rng
    return Xu_v, valid, pca, lo, hi


# ---------------------------------------------------------------------------
# Surrogate wrapper
# ---------------------------------------------------------------------------


class DatasetSurrogate:
    """Random-Forest surrogate fitted on (X_train, Y_train).

    Caches a single fitted estimator. Provides:
      * .predict(X)  – inference
      * .loo_rmse()  – leave-one-out RMSE per output column for validation
    """

    def __init__(self, X_train: np.ndarray, Y_train: np.ndarray,
                 *, n_estimators: int = 200, random_state: int = 0):
        from sklearn.ensemble import RandomForestRegressor
        self.X_train = np.asarray(X_train, dtype=np.float64)
        self.Y_train = np.asarray(Y_train, dtype=np.float64)
        self.model = RandomForestRegressor(
            n_estimators=n_estimators, random_state=random_state, n_jobs=1,
        ).fit(self.X_train, self.Y_train)
        self.n_obj = self.Y_train.shape[1] if self.Y_train.ndim > 1 else 1

    def predict(self, X: np.ndarray) -> np.ndarray:
        Y = self.model.predict(np.asarray(X, dtype=np.float64))
        if Y.ndim == 1:
            Y = Y.reshape(-1, 1)
        return Y

    def loo_rmse(self) -> np.ndarray:
        """Leave-one-out RMSE per output column. Slow — call once at build."""
        from sklearn.ensemble import RandomForestRegressor
        n = len(self.X_train)
        preds = np.zeros_like(self.Y_train)
        for i in range(n):
            mask = np.arange(n) != i
            m = RandomForestRegressor(
                n_estimators=100, random_state=0, n_jobs=1,
            ).fit(self.X_train[mask], self.Y_train[mask])
            preds[i] = m.predict(self.X_train[i:i + 1])[0]
        rmse = np.sqrt(((preds - self.Y_train) ** 2).mean(axis=0))
        return np.atleast_1d(rmse)
