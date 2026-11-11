"""E2 step B2: how far can MACE's bulk moduli be corrected through its readout alone?

Reference: DFT K_VRH of the matminer elastic set (data/mlip_reference/elastic.extxyz).
Each seed splits the cached structures in half. On the training half we fit

  scale    one number: a multiplier on the energy scale (K is proportional to it)
  readout  every readout weight and the scale (2,193 numbers) by Adam on the squared
           error of the bulk modulus, with a penalty that keeps the weights near the
           originals, early-stopped on a fifth of the training half
  readout_keep_energy  the same fit with a penalty on any change of energy per atom

and report on the test half, with the unedited model for comparison. Besides the
bulk-modulus error it reports what an edit costs elsewhere: the change in energy
per atom at the cached geometries, and the shift of the equilibrium volume.

    python experiments/e2_mlip_readout_edit/run_baselines.py
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import torch
from scipy.stats import spearmanr

from wsp.mace_readout import bulk_modulus, energies, load_cache, load_readout, predict_moduli

HERE = Path(__file__).resolve().parent
TRAINABLE = ("readouts.0.linear.weight", "readouts.1.linear_1.weight", "readouts.1.linear_2.weight", "scale_shift.scale")


def report(params, base, structures, k_ref) -> dict:
    k = predict_moduli(params, structures).detach().numpy()
    ok = np.isfinite(k)
    error = k[ok] - k_ref[ok]
    de = [float(((energies(params, s) - energies(base, s)).detach().abs().mean() / s.element.numel()) * 1000) for s in structures]
    return {
        "n": int(ok.sum()), "failed_fits": int((~ok).sum()),
        "mae_GPa": float(np.abs(error).mean()), "bias_GPa": float(error.mean()),
        "rmse_GPa": float(np.sqrt((error**2).mean())),
        "mape_pct": float(100 * np.mean(np.abs(error) / k_ref[ok])),
        "spearman": float(spearmanr(k[ok], k_ref[ok]).statistic),
        "energy_change_meV_per_atom": float(np.mean(de)),
    }


def fit_scale(base, train, k_ref):
    k = predict_moduli(base, train).detach().numpy()
    ok = np.isfinite(k)
    multiplier = float((k[ok] * k_ref[ok]).sum() / (k[ok] ** 2).sum())
    params = {key: v.clone() for key, v in base.items()}
    params["scale_shift.scale"] = base["scale_shift.scale"] * multiplier
    return params, multiplier


def fit_readout(base, train, k_ref, seed, steps=400, lr=2e-3, penalty=1e-2, keep_energy=0.0):
    """`keep_energy` > 0 adds a penalty on the change of energy per atom (in units of
    10 meV) at the cached geometries, so the fit may not buy bulk modulus with energy."""
    rng = np.random.default_rng(seed)
    order = rng.permutation(len(train))
    n_val = max(1, len(train) // 5)
    val, fit = order[:n_val], order[n_val:]
    params = {k: v.clone().requires_grad_(k in TRAINABLE) for k, v in base.items()}
    optimizer = torch.optim.Adam([params[k] for k in TRAINABLE], lr=lr)
    target = torch.tensor(k_ref)

    def loss_on(rows):
        k = torch.stack([bulk_modulus(train[i].volumes, energies(params, train[i])) for i in rows])
        ok = torch.isfinite(k)
        loss = (((k[ok] - target[rows][ok]) / 100.0) ** 2).mean()
        if keep_energy:
            shift = torch.stack([((energies(params, train[i]) - train[i].mace_energies) / train[i].element.numel()).pow(2).mean() for i in rows])
            loss = loss + keep_energy * (shift / 0.01**2).mean()
        return loss

    best, best_state, since = float("inf"), None, 0
    for step in range(steps):
        optimizer.zero_grad()
        drift = sum(((params[k] - base[k]) ** 2).sum() / (base[k] ** 2).sum() for k in TRAINABLE)
        (loss_on(fit) + penalty * drift).backward()
        optimizer.step()
        if step % 10 == 0:
            with torch.no_grad():
                v = float(loss_on(val))
            if v < best - 1e-6:
                best, best_state, since = v, {k: p.detach().clone() for k, p in params.items()}, 0
            else:
                since += 1
                if since >= 6:
                    break
    return best_state


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--set", default="elastic")
    parser.add_argument("--seeds", type=int, default=5)
    args = parser.parse_args()

    base = load_readout()
    structures = load_cache(args.set, base)
    k0 = predict_moduli(base, structures).numpy()
    structures = [s for s, k in zip(structures, k0) if np.isfinite(k)]
    k_ref = np.array([s.K_ref for s in structures])
    print(f"{len(structures)} structures with a valid base fit ({int((~np.isfinite(k0)).sum())} dropped)")

    rows = []
    for seed in range(args.seeds):
        order = np.random.default_rng(seed).permutation(len(structures))
        half = len(order) // 2
        train = [structures[i] for i in order[:half]]
        test = [structures[i] for i in order[half:]]
        ktr, kte = k_ref[order[:half]], k_ref[order[half:]]
        scale_params, multiplier = fit_scale(base, train, ktr)
        readout_params = fit_readout(base, train, ktr, seed)
        kept_params = fit_readout(base, train, ktr, seed, keep_energy=1.0)
        changed = sum(int((readout_params[k] != base[k]).sum()) for k in base)
        row = {
            "seed": seed, "n_train": len(train), "n_test": len(test),
            "unedited": report(base, base, test, kte),
            "scale": report(scale_params, base, test, kte) | {"multiplier": multiplier},
            "readout": report(readout_params, base, test, kte) | {"weights_changed": changed},
            "readout_keep_energy": report(kept_params, base, test, kte),
        }
        rows.append(row)
        print(json.dumps({k: (v if not isinstance(v, dict) else {m: round(x, 3) for m, x in v.items()}) for k, v in row.items()}), flush=True)

    def mean_std(arm, metric):
        v = [r[arm][metric] for r in rows]
        return {"mean": float(np.mean(v)), "std": float(np.std(v))}

    metrics = ("mae_GPa", "bias_GPa", "rmse_GPa", "mape_pct", "spearman", "energy_change_meV_per_atom")
    summary = {"set": args.set, "structures": len(structures), "seeds": args.seeds,
               **{arm: {m: mean_std(arm, m) for m in metrics} for arm in ("unedited", "scale", "readout", "readout_keep_energy")},
               "scale_multiplier": mean_std("scale", "multiplier"), "per_seed": rows}
    out = HERE / "results"
    out.mkdir(exist_ok=True)
    (out / f"baselines_{args.set}.json").write_text(json.dumps(summary, indent=2) + "\n")
    for arm in ("unedited", "scale", "readout", "readout_keep_energy"):
        print(arm, {m: f"{summary[arm][m]['mean']:.2f} ± {summary[arm][m]['std']:.2f}" for m in metrics})


if __name__ == "__main__":
    main()
