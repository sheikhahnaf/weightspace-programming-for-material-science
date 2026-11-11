"""E2: export the 2,283 numbers of MACE-MPA-0 medium that the experiment edits.

Writes data/mlip_reference/mace_mpa0_medium_readout.npz, so that everything
after feature caching runs without MACE installed. Run in the mlip-mace env.
"""

import os
from pathlib import Path

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[2]
model = torch.load(os.path.expanduser("~/.cache/mace/macempa0mediummodel"), map_location="cpu", weights_only=False)
r0, r1 = model.readouts
out = {
    "readouts.0.linear.weight": r0.linear.weight.detach().double().numpy(),
    "readouts.1.linear_1.weight": r1.linear_1.weight.detach().double().numpy().reshape(-1, r1.linear_2.weight.numel()),
    "readouts.1.linear_2.weight": r1.linear_2.weight.detach().double().numpy(),
    "scale_shift.scale": np.array([float(model.scale_shift.scale)]),
    "scale_shift.shift": np.array([float(model.scale_shift.shift)]),
    "atomic_energies": model.atomic_energies_fn.atomic_energies.detach().double().numpy().flatten(),
    "atomic_numbers": np.array(model.atomic_numbers.tolist()),
}
target = ROOT / "data" / "mlip_reference" / "mace_mpa0_medium_readout.npz"
np.savez(target, **out)
print({k: v.shape for k, v in out.items()}, "total edited numbers:",
      sum(v.size for k, v in out.items() if k != "atomic_numbers"))
