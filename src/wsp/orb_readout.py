"""ORB-v3's energy head as a small editable network (experiment E2, second potential).

orb_v3_conservative_inf_omat computes the energy of a structure as

    E = A * ( w2 . silu(W1 x + b1) + b2 ) + C

x is the mean over atoms of the 256 node features after the last message-passing
layer, A is the normaliser's standard deviation times the number of atoms, and C
holds everything that does not pass through the head (normaliser mean, per-element
reference energies, pair repulsion). W1 (256 x 256), b1 (256), w2 (256) and b2 (1)
are the 66,049 numbers of the head.

x, A and the model's own energies come from
experiments/e2_mlip_readout_edit/cache_features_orb.py. C is recovered per geometry
from those energies, so the unedited head reproduces them exactly.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[2]
HEAD_FILE = ROOT / "data" / "mlip_reference" / "orb_v3_energy_head.npz"
NAMES = {"W1": "NN-0.weight", "b1": "NN-0.bias", "w2": "NN-1.weight", "b2": "NN-1.bias"}


def load_head() -> dict[str, torch.Tensor]:
    data = np.load(HEAD_FILE)
    head = {k: torch.tensor(data[v], dtype=torch.float64) for k, v in NAMES.items()}
    head["w2"] = head["w2"].reshape(-1)
    head["b2"] = head["b2"].reshape(1)
    return head


@dataclass(frozen=True)
class Structure:
    name: str
    K_ref: float
    n_atoms: int
    A: float
    volumes: torch.Tensor  # (7,)
    x: torch.Tensor  # (7, 256)
    rest: torch.Tensor  # (7,) C at each geometry
    model_energies: torch.Tensor  # (7,)

    @property
    def mace_energies(self) -> torch.Tensor:  # name used by the shared fitting code
        return self.model_energies


def hidden(params: dict[str, torch.Tensor], x: torch.Tensor) -> torch.Tensor:
    return torch.nn.functional.silu(x @ params["W1"].T + params["b1"])


def head_output(params: dict[str, torch.Tensor], x: torch.Tensor) -> torch.Tensor:
    return hidden(params, x) @ params["w2"] + params["b2"]


def energies(params: dict[str, torch.Tensor], s: Structure) -> torch.Tensor:
    """Total energy at the seven cached geometries under `params`."""
    return s.A * head_output(params, s.x) + s.rest


def load_cache(name: str, base: dict[str, torch.Tensor] | None = None) -> list[Structure]:
    base = base or load_head()
    out = []
    for path in sorted((ROOT / "data" / "large" / "mlip_cache_orb" / name).glob("*.npz")):
        d = np.load(path)
        x = torch.tensor(d["x"], dtype=torch.float64)
        e = torch.tensor(d["energies"], dtype=torch.float64)
        A = float(d["A"])
        out.append(Structure(str(d["name"]), float(d["K_ref"]), int(d["n_atoms"]), A,
                             torch.tensor(d["volumes"], dtype=torch.float64), x, e - A * head_output(base, x), e))
    return out


def head_mismatch(name: str = "elastic") -> float:
    """Largest difference between this file's formula and the head output recorded
    from the real model, over a cached set (float32 model against float64 here)."""
    base = load_head()
    worst = 0.0
    for path in sorted((ROOT / "data" / "large" / "mlip_cache_orb" / name).glob("*.npz")):
        d = np.load(path)
        o = head_output(base, torch.tensor(d["x"], dtype=torch.float64)).numpy()
        worst = max(worst, float(np.abs(o - d["head_out"]).max()))
    return worst
