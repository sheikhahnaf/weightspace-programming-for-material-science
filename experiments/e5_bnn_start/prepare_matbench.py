"""E5 data: the 15 named descriptors of the generator-filter arm for every
structure of matbench_log_kvrh (10,987 Materials Project crystals, DFT K_VRH).

Writes data/bnn/matbench_kvrh_descriptors.npz (X, K_GPa, feature names). The
first run downloads the matminer dataset.
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments" / "e3_crystal_filter"))
from filter_arm import FEATURES, describe  # noqa: E402

from matminer.datasets import load_dataset
from pymatgen.io.ase import AseAtomsAdaptor

df = load_dataset("matbench_log_kvrh")
X = np.array([describe(AseAtomsAdaptor.get_atoms(s)) for s in df["structure"]])
K = 10.0 ** df["log10(K_VRH)"].to_numpy(dtype=float)
keep = np.isfinite(X).all(1) & np.isfinite(K) & (K > 1)
out = ROOT / "data" / "bnn"
out.mkdir(parents=True, exist_ok=True)
np.savez_compressed(out / "matbench_kvrh_descriptors.npz", X=X[keep], K_GPa=K[keep], features=np.array(FEATURES))
print(X[keep].shape, "K range", K[keep].min().round(1), K[keep].max().round(1))
