"""E2, outside the readout: what fixes or replaces a potential's bulk modulus without
touching its weights. No new LLM calls: the written networks are the bulk-modulus
replies of the generator filter arm (E3), scored here on DFT-relaxed crystals.

On the 400 crystals of the elastic set (DFT K_VRH from the Materials Project):

  1. each potential as shipped; the plain mean of the potentials
  2. the written 15 -> 16 -> 1 networks, which cost no simulation at all
  3. with n DFT labels (n = 10 to 100, 20 random draws, scored on the other crystals):
     affine   K = a * m + b for one predictor m (a potential, or a written network)
     mixture  K = least squares over all potentials
     gp       a GP on the 15 descriptors with mean a * m + b; "none" is the plain GP

    python experiments/e2_mlip_readout_edit/beyond_readout.py
"""

from __future__ import annotations

import json
import sys
import warnings
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "experiments" / "e3_generator_task_vectors"))
import filter_arm  # noqa: E402

from wsp.linear_head import load, predict_moduli  # noqa: E402

SIZES = (10, 20, 50, 100)
DRAWS = 20


def metrics(pred, truth) -> dict:
    return {"mae_GPa": float(np.mean(np.abs(pred - truth))), "bias_GPa": float(np.mean(pred - truth)),
            "spearman": float(spearmanr(pred, truth).statistic)}


def gp_predict(X, y, rows, rest, prior=None):
    from sklearn.gaussian_process import GaussianProcessRegressor
    from sklearn.gaussian_process.kernels import RBF, ConstantKernel, WhiteKernel

    mu, sd = X[rows].mean(0), X[rows].std(0)
    sd[sd < 1e-9] = 1.0
    Z = (X - mu) / sd
    if prior is None:
        mean = np.full(len(y), y[rows].mean())
    else:
        a, b = np.polyfit(prior[rows], y[rows], 1) if np.ptp(prior[rows]) > 0 else (0.0, y[rows].mean())
        mean = a * prior + b
    r = y - mean
    scale = r[rows].std() + 1e-9
    kernel = ConstantKernel(1.0) * RBF(np.ones(X.shape[1]) * 3.0, (0.3, 100.0)) + WhiteKernel(0.1, (1e-3, 1.0))
    gp = GaussianProcessRegressor(kernel, normalize_y=False, n_restarts_optimizer=0, random_state=0)
    gp.fit(Z[rows], r[rows] / scale)
    return mean[rest] + scale * gp.predict(Z[rest])


def main() -> None:
    warnings.filterwarnings("ignore")
    from ase.io import read

    frames = read(ROOT / "data" / "mlip_reference" / "elastic.extxyz", index=":")
    names = [str(a.info.get("name")) for a in frames]
    truth_all = np.array([a.info["K_ref"] for a in frames])
    X_all = np.array([filter_arm.describe(a) for a in frames])
    K = {}
    for potential in ("mace", "orb", "esen", "grace"):
        try:
            base, structures = load(potential)
        except FileNotFoundError:
            continue
        if len(structures) < 300:
            continue
        by_name = {s.name: float(k) for s, k in zip(structures, predict_moduli(base, structures))}
        K[potential] = np.array([by_name.get(n, np.nan) for n in names])
    ok = np.all([np.isfinite(v) for v in K.values()], axis=0)
    truth, X = truth_all[ok], X_all[ok]
    K = {k: v[ok] for k, v in K.items()}
    written = {}
    for folder in sorted((ROOT / "experiments" / "e3_generator_task_vectors" / "runs").glob("filter_K__*")):
        if (folder / "reply.txt").exists():
            try:
                written[folder.name.replace("filter_K__", "")] = filter_arm.scorer((folder / "reply.txt").read_text())(X)
            except Exception:
                pass
    print(f"{int(ok.sum())} crystals; potentials {list(K)}; written networks {len(written)}")

    zero = {f"potential: {p}": metrics(v, truth) for p, v in K.items()}
    if len(K) > 1:
        zero["mean of the potentials"] = metrics(np.mean(list(K.values()), axis=0), truth)
    for model in ("opus", "fable", "sonnet", "haiku"):
        rs = [metrics(v, truth) for k, v in written.items() if k.startswith(model)]
        if rs:
            zero[f"written network: {model} (mean of {len(rs)} replies)"] = {m: float(np.mean([r[m] for r in rs])) for m in rs[0]}
    zero["rule: small volume per atom (rank only)"] = {"mae_GPa": None, "bias_GPa": None, "spearman": float(spearmanr(-X[:, 0], truth).statistic)}

    predictors = dict(K)
    for model in ("opus", "fable"):
        key = next((k for k in sorted(written) if k.startswith(model)), None)
        if key:
            predictors[f"written:{key}"] = written[key]
    few: dict[str, dict] = {}

    def add(arm, n, m):
        few.setdefault(arm, {}).setdefault(str(n), []).append(m)

    for n in SIZES:
        for draw in range(DRAWS):
            order = np.random.default_rng(1000 * n + draw).permutation(len(truth))
            rows, rest = order[:n], order[n:]
            for name, m in predictors.items():
                a, b = np.polyfit(m[rows], truth[rows], 1)
                add(f"affine: {name}", n, metrics(a * m[rest] + b, truth[rest]))
                if draw < 5:
                    add(f"gp, prior mean {name}", n, metrics(gp_predict(X, truth, rows, rest, m), truth[rest]))
            if len(K) > 1:
                A = np.column_stack([*K.values(), np.ones(len(truth))])
                coef = np.linalg.lstsq(A[rows], truth[rows], rcond=None)[0]
                add("mixture of the potentials", n, metrics(A[rest] @ coef, truth[rest]))
            if draw < 5:
                add("gp, no prior mean", n, metrics(gp_predict(X, truth, rows, rest), truth[rest]))
    few = {arm: {n: {m: float(np.mean([r[m] for r in rs])) for m in rs[0]} for n, rs in by_n.items()} for arm, by_n in few.items()}

    out = HERE / "results" / "beyond"
    out.mkdir(parents=True, exist_ok=True)
    (out / "beyond_readout.json").write_text(json.dumps({"n_crystals": int(ok.sum()), "zero_labels": zero, "few_labels": few}, indent=2) + "\n")
    lines = [f"**No DFT labels ({int(ok.sum())} crystals)**", "", "| Predictor | MAE, GPa | Bias, GPa | ρ |", "|---|---|---|---|"]
    for name, m in zero.items():
        lines.append(f"| {name} | {'' if m['mae_GPa'] is None else format(m['mae_GPa'], '.1f')} | "
                     f"{'' if m['bias_GPa'] is None else format(m['bias_GPa'], '+.1f')} | {m['spearman']:.3f} |")
    lines += ["", "**With n DFT labels: MAE in GPa (ρ)**", "", "| Method | " + " | ".join(f"n = {n}" for n in SIZES) + " |", "|---|" + "---|" * len(SIZES)]
    for arm, by_n in few.items():
        lines.append(f"| {arm} | " + " | ".join(f"{by_n[str(n)]['mae_GPa']:.1f} ({by_n[str(n)]['spearman']:.2f})" for n in SIZES) + " |")
    (out / "beyond_readout.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
