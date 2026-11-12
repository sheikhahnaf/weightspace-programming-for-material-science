"""One interface for the last layer of four potentials (experiment E2).

In MACE-MPA-0, ORB-v3, eSEN-30M-OAM and GRACE-2L-OAM the total energy is linear in
the weights w of the final layer of the energy readout:

    E(geometry) = h(geometry) . w  +  c(geometry) * b  +  rest(geometry)

h is the derivative of the energy with respect to each weight (computed from cached
features, or measured on the real model for GRACE), b is an optional uniform term
(an output bias), c its derivative, and rest is everything else, recovered from the
model's own energies so that the unedited weights reproduce them exactly. Because the
relation is linear, the energy of any edit of (w, b) at a cached geometry is exact.

    potential   w                                   size   b
    mace        readouts.0.linear.weight            128    scale_shift.shift
    orb         energy head, output layer           256    its bias
    esen        energy block, output layer          128    its bias
    grace       MLPOut2ScalarTarget, output layer    64    none
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import torch

from wsp.mace_readout import bulk_modulus

ROOT = Path(__file__).resolve().parents[2]
LARGE = ROOT / "data" / "large"
POTENTIALS = ("mace", "orb", "esen", "grace")
FULL_NAME = {"mace": "MACE-MPA-0 medium", "orb": "ORB-v3 (orb_v3_conservative_inf_omat)",
             "esen": "eSEN-30M-OAM", "grace": "GRACE-2L-OAM"}
TOTAL_WEIGHTS = {"mace": 9_063_204, "orb": 25_510_582, "esen": 30_161_153, "grace": 12_597_695}


@dataclass(frozen=True)
class Structure:
    name: str
    K_ref: float
    n_atoms: int
    volumes: torch.Tensor  # (7,)
    h: torch.Tensor  # (7, H)
    c: torch.Tensor  # (7,) derivative with respect to b; zeros if the potential has none
    rest: torch.Tensor  # (7,)
    model_energies: torch.Tensor  # (7,)


def energies(params: dict[str, torch.Tensor], s: Structure) -> torch.Tensor:
    return s.h @ params["w"] + s.c * params["b"] + s.rest


def predict_moduli(params: dict[str, torch.Tensor], structures: list[Structure]) -> torch.Tensor:
    return torch.stack([bulk_modulus(s.volumes, energies(params, s)) for s in structures])


def _t(a) -> torch.Tensor:
    return torch.tensor(np.asarray(a), dtype=torch.float64)


def _build(d, h, c, w, b) -> Structure:
    e = _t(d["energies"])
    return Structure(str(d["name"]), float(d["K_ref"]), int(d["n_atoms"]) if "n_atoms" in d.files else int(len(d["Z"])),
                     _t(d["volumes"]), h, c, e - h @ w - c * b, e)


def _mace(name):
    from wsp.mace_readout import load_readout
    r = load_readout()
    w, b, scale = r["readouts.0.linear.weight"].clone(), r["scale_shift.shift"].reshape(()).clone(), float(r["scale_shift.scale"])
    out = []
    for path in sorted((LARGE / "mlip_cache" / name).glob("*.npz")):
        d = np.load(path)
        f0 = _t(d["f0"])
        out.append(_build(d, scale * f0.sum(1) / np.sqrt(f0.shape[-1]), torch.full((7,), float(f0.shape[1]), dtype=torch.float64), w, b))
    return {"w": w, "b": b}, out


def _orb(name):
    from wsp.orb_readout import hidden, load_head
    head = load_head()
    w, b = head["w2"].clone(), head["b2"].reshape(()).clone()
    out = []
    for path in sorted((LARGE / "mlip_cache_orb" / name).glob("*.npz")):
        d = np.load(path)
        A = float(d["A"])
        out.append(_build(d, A * hidden(head, _t(d["x"])), torch.full((7,), A, dtype=torch.float64), w, b))
    return {"w": w, "b": b}, out


def _esen(name):
    head = np.load(ROOT / "data" / "mlip_reference" / "esen_30m_oam_energy_head.npz")
    W0, b0, W2, b2 = (_t(head[k]) for k in ("0.weight", "0.bias", "2.weight", "2.bias"))
    w, b = _t(head["4.weight"]).reshape(-1), _t(head["4.bias"]).reshape(())
    silu = torch.nn.functional.silu
    out = []
    for path in sorted((LARGE / "mlip_cache_esen" / name).glob("*.npz")):
        d = np.load(path)
        scale = float(d["scale"])
        z = silu(silu(_t(d["s"]) @ W0.T + b0) @ W2.T + b2)  # (7, n_atoms, 128)
        out.append(_build(d, scale * z.sum(1), torch.full((7,), scale * int(d["n_atoms"]), dtype=torch.float64), w, b))
    return {"w": w, "b": b}, out


def _grace(name):
    w = _t(np.load(ROOT / "data" / "mlip_reference" / "grace_2l_oam_output_layer.npz")["w"]).reshape(-1)
    b = torch.zeros((), dtype=torch.float64)
    out = []
    for path in sorted((LARGE / "mlip_cache_grace_GRACE-2L-OAM_v2" / name).glob("*.npz")):
        g = path.with_suffix(".G.npy")
        if not g.exists():
            continue
        out.append(_build(np.load(path), _t(np.load(g)), torch.zeros(7, dtype=torch.float64), w, b))
    return {"w": w, "b": b}, out


def load(potential: str, name: str = "elastic") -> tuple[dict[str, torch.Tensor], list[Structure]]:
    """Unedited last-layer weights and the cached structures of one potential."""
    return {"mace": _mace, "orb": _orb, "esen": _esen, "grace": _grace}[potential](name)
