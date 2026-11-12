"""The ORB-v3 energy head as rebuilt in wsp.orb_readout. Skipped without the cache."""

import numpy as np
import pytest
import torch

from wsp.mace_readout import bulk_modulus
from wsp.orb_readout import ROOT, energies, head_mismatch, load_cache, load_head

CACHE = ROOT / "data" / "large" / "mlip_cache_orb" / "dft15"
pytestmark = pytest.mark.skipif(not any(CACHE.glob("*.npz")), reason="ORB cache not built")


def test_head_has_66049_numbers():
    assert sum(v.numel() for v in load_head().values()) == 66_049


def test_formula_matches_the_recorded_head_output():
    assert head_mismatch("dft15") < 1e-5


def test_unedited_head_reproduces_model_energies():
    base = load_head()
    for s in load_cache("dft15", base):
        assert torch.allclose(energies(base, s), s.model_energies, atol=1e-9)


def test_output_bias_shifts_energy_and_not_bulk_modulus():
    base = load_head()
    s = load_cache("dft15", base)[0]
    moved = {k: v.clone() for k, v in base.items()}
    moved["b2"] = base["b2"] + 0.01
    shift = (energies(moved, s) - energies(base, s)).numpy()
    assert np.allclose(shift, s.A * 0.01)
    k0, k1 = bulk_modulus(s.volumes, energies(base, s)), bulk_modulus(s.volumes, energies(moved, s))
    assert abs(float(k0 - k1)) < 1e-6
