"""MACE's scalar readout as a small editable network (experiment E2).

MACE-MPA-0 medium computes the energy of a structure as

    E = sum_i E0[Z_i] + sum_i ( scale * (pair_i + r0_i + r1_i) + shift )
    r0_i = (f0_i . w0) / sqrt(128)
    r1_i = (ACT * silu(f1_i @ W1 / sqrt(128)) . w2) / sqrt(16)

f0_i and f1_i are the 128 scalar features of atom i after the first and second
interaction; pair_i is a fixed pair repulsion. E0 (89), w0 (128), W1 (128 x 16),
w2 (16), scale and shift are the 2,283 numbers this experiment edits. The
formulas were checked against the model to 1e-15 (r0) and 5e-7 (r1, limited by
the printed precision of ACT).

The features come from supplementary/e2_mlip_readout_edit/cache_features.py. The
summed pair term is recovered from MACE's own cached energies, so the unedited
weights reproduce those energies exactly.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[2]
READOUT_FILE = ROOT / "data" / "mlip_reference" / "mace_mpa0_medium_readout.npz"
ACT = 1.6791767923989418  # e3nn's second-moment normalisation of silu
EV_PER_A3_TO_GPA = 160.21766208
EDITABLE = (
    "readouts.0.linear.weight", "readouts.1.linear_1.weight", "readouts.1.linear_2.weight",
    "scale_shift.scale", "scale_shift.shift", "atomic_energies",
)


def load_readout() -> dict[str, torch.Tensor]:
    data = np.load(READOUT_FILE)
    return {k: torch.tensor(data[k], dtype=torch.float64) for k in EDITABLE}


def atomic_numbers() -> list[int]:
    return np.load(READOUT_FILE)["atomic_numbers"].tolist()


@dataclass(frozen=True)
class Structure:
    name: str
    K_ref: float
    volumes: torch.Tensor  # (7,)
    f0: torch.Tensor  # (7, n_atoms, 128)
    f1: torch.Tensor  # (7, n_atoms, 128)
    element: torch.Tensor  # (n_atoms,) index into atomic_energies
    pair: torch.Tensor  # (7,) summed pair repulsion, before scaling
    mace_energies: torch.Tensor  # (7,)


def _unscaled(params: dict[str, torch.Tensor], f0: torch.Tensor, f1: torch.Tensor) -> torch.Tensor:
    r0 = (f0 @ params["readouts.0.linear.weight"]) / np.sqrt(f0.shape[-1])
    hidden = ACT * torch.nn.functional.silu(f1 @ params["readouts.1.linear_1.weight"] / np.sqrt(f1.shape[-1]))
    r1 = (hidden @ params["readouts.1.linear_2.weight"]) / np.sqrt(hidden.shape[-1])
    return (r0 + r1).sum(-1)  # summed over atoms -> (7,)


def energies(params: dict[str, torch.Tensor], s: Structure) -> torch.Tensor:
    """Total energy at the seven cached geometries under `params`."""
    n = s.element.numel()
    return (
        params["atomic_energies"][s.element].sum()
        + params["scale_shift.scale"] * (s.pair + _unscaled(params, s.f0, s.f1))
        + params["scale_shift.shift"] * n
    )


def load_cache(name: str, base: dict[str, torch.Tensor] | None = None) -> list[Structure]:
    base = base or load_readout()
    table = atomic_numbers()
    out = []
    for path in sorted((ROOT / "data" / "large" / "mlip_cache" / name).glob("*.npz")):
        d = np.load(path)
        f0 = torch.tensor(d["f0"], dtype=torch.float64)
        f1 = torch.tensor(d["f1"], dtype=torch.float64)
        element = torch.tensor([table.index(int(z)) for z in d["Z"]])
        mace = torch.tensor(d["energies"], dtype=torch.float64)
        n = element.numel()
        inter = (mace - base["atomic_energies"][element].sum() - base["scale_shift.shift"] * n) / base["scale_shift.scale"]
        out.append(Structure(str(d["name"]), float(d["K_ref"]), torch.tensor(d["volumes"], dtype=torch.float64),
                             f0, f1, element, inter - _unscaled(base, f0, f1), mace))
    return out


def bulk_modulus(volumes: torch.Tensor, e: torch.Tensor) -> torch.Tensor:
    """Bulk modulus in GPa from a cubic fit of E(V), at the fitted minimum.

    Differentiable in the energies, so it can be used as a training loss.
    Returns NaN when the cubic has no minimum inside the sampled volumes.
    """
    v = (volumes - volumes.mean()) / volumes.std()
    A = torch.stack([torch.ones_like(v), v, v**2, v**3], dim=1)
    c = torch.linalg.lstsq(A, e.unsqueeze(-1)).solution.squeeze(-1)
    disc = c[2] ** 2 - 3 * c[3] * c[1]
    if disc < 0:
        return torch.tensor(float("nan"), dtype=e.dtype)
    root = (-c[2] + torch.sqrt(disc)) / (3 * c[3]) if abs(c[3]) > 1e-14 else -c[1] / (2 * c[2])
    if not (v.min() <= root <= v.max()):
        return torch.tensor(float("nan"), dtype=e.dtype)
    curvature = (2 * c[2] + 6 * c[3] * root) / volumes.std() ** 2
    v0 = root * volumes.std() + volumes.mean()
    return v0 * curvature * EV_PER_A3_TO_GPA


def predict_moduli(params: dict[str, torch.Tensor], structures: list[Structure]) -> torch.Tensor:
    return torch.stack([bulk_modulus(s.volumes, energies(params, s)) for s in structures])
