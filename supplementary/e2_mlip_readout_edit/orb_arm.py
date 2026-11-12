"""E2 on a second potential: edit ORB-v3's energy head to correct its bulk moduli.

    python supplementary/e2_mlip_readout_edit/orb_arm.py baselines      # unedited, gradient fits, trade-off curve
    python supplementary/e2_mlip_readout_edit/orb_arm.py prompt --tag opus__rep1
    python supplementary/e2_mlip_readout_edit/orb_arm.py prompt --tag opus__ctrl1 --control
    python supplementary/e2_mlip_readout_edit/orb_arm.py score-all

Same protocol as the MACE arm (llm_arm.py, prompt version 2): the 400 crystals of the
matminer elastic set, split in half with seed 0; the model sees the error on the
training half and a finite-difference table, and is scored on the test half.

The head has 66,049 numbers, too many to show. The prompt shows the output layer
(w2, 256 numbers, and b2) and a table for w2; the first layer is frozen. The energy
is linear in w2, as it is in MACE's w0, so the two arms ask the same thing.

Control (`--control`): the w2 values shown are a fixed permutation of the true ones,
while the table still describes the true weights. A reply is then applied as changes
relative to the values shown. If control replies do as well, the edit came from the
table and not from the weights.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import torch
from scipy.stats import spearmanr

from wsp import estimate_tokens
from wsp.edit import apply_edits, parse_edits
from wsp.mace_readout import bulk_modulus
from wsp.orb_readout import energies, hidden, load_cache, load_head

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results" / "orb"
SEED = 0
STEP = 0.002
PENALTIES = (0.0, 0.001, 0.003, 0.01, 0.03, 0.1, 0.3, 1.0)


def predict_moduli(params, structures) -> torch.Tensor:
    return torch.stack([bulk_modulus(s.volumes, energies(params, s)) for s in structures])


def setup(name: str = "elastic"):
    base = load_head()
    structures = load_cache(name, base)
    k0 = predict_moduli(base, structures).numpy()
    structures = [s for s, k in zip(structures, k0) if np.isfinite(k)]
    k_ref = np.array([s.K_ref for s in structures])
    order = np.random.default_rng(SEED).permutation(len(structures))
    half = len(order) // 2
    train, test = [structures[i] for i in order[:half]], [structures[i] for i in order[half:]]
    return base, train, k_ref[order[:half]], test, k_ref[order[half:]]


def report(params, base, structures, k_ref) -> dict:
    k = predict_moduli(params, structures).detach().numpy()
    ok = np.isfinite(k)
    error = k[ok] - k_ref[ok]
    de = [float((energies(params, s) - energies(base, s)).detach().abs().mean() / s.n_atoms * 1000) for s in structures]
    return {
        "n": int(ok.sum()), "failed_fits": int((~ok).sum()),
        "mae_GPa": float(np.abs(error).mean()), "bias_GPa": float(error.mean()),
        "rmse_GPa": float(np.sqrt((error**2).mean())),
        "mape_pct": float(100 * np.mean(np.abs(error) / k_ref[ok])),
        "spearman": float(spearmanr(k[ok], k_ref[ok]).statistic),
        "energy_change_meV_per_atom": float(np.mean(de)),
    }


def fit(base, train, k_ref, trainable, keep_energy=0.0, steps=400, lr=1e-4, penalty=1e-2):
    """Adam on the squared bulk-modulus error of the training half, early-stopped on a
    fifth of it. `keep_energy` weights a penalty on the change of energy per atom
    (in units of 10 meV), as in the MACE arm."""
    order = np.random.default_rng(SEED).permutation(len(train))
    n_val = max(1, len(train) // 5)
    val, rows = order[:n_val], order[n_val:]
    params = {k: v.clone().requires_grad_(k in trainable) for k, v in base.items()}
    optimizer = torch.optim.Adam([params[k] for k in trainable], lr=lr)
    target = torch.tensor(k_ref)

    def loss_on(idx):
        k = torch.stack([bulk_modulus(train[i].volumes, energies(params, train[i])) for i in idx])
        ok = torch.isfinite(k)
        loss = (((k[ok] - target[idx][ok]) / 100.0) ** 2).mean()
        if keep_energy:
            shift = torch.stack([((energies(params, train[i]) - train[i].model_energies) / train[i].n_atoms).pow(2).mean() for i in idx])
            loss = loss + keep_energy * (shift / 0.01**2).mean()
        return loss

    best, best_state, since = float("inf"), {k: v.clone() for k, v in base.items()}, 0
    for step in range(steps):
        optimizer.zero_grad()
        drift = sum(((params[k] - base[k]) ** 2).sum() / (base[k] ** 2).sum() for k in trainable)
        (loss_on(rows) + penalty * drift).backward()
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


def table(base, train):
    """Per weight j of w2: change of the fitted bulk modulus (GPa) per unit increase,
    by finite difference (so it includes the shift of the equilibrium volume), and
    change of the energy per atom (eV) per unit increase, which is exact. Mean and
    standard deviation over the training crystals. Cached."""
    cache = RESULTS / f"sensitivity_seed{SEED}.json"
    if cache.exists():
        d = json.loads(cache.read_text())
        return tuple(np.array(d[k]) for k in ("dK_mean", "dK_sd", "dE_mean", "dE_sd"))
    k0 = predict_moduli(base, train).numpy()
    dE = np.array([(s.A / s.n_atoms * hidden(base, s.x[3])).numpy() for s in train])  # at zero strain
    mean, sd = [], []
    for j in range(base["w2"].numel()):
        params = {k: v.clone() for k, v in base.items()}
        params["w2"][j] += STEP
        dk = (predict_moduli(params, train).numpy() - k0) / STEP
        mean.append(float(np.nanmean(dk)))
        sd.append(float(np.nanstd(dk)))
    RESULTS.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps({"step": STEP, "dK_mean": mean, "dK_sd": sd,
                                 "dE_mean": dE.mean(0).tolist(), "dE_sd": dE.std(0).tolist()}) + "\n")
    return np.array(mean), np.array(sd), dE.mean(0), dE.std(0)


def table_solve(base, train, ktr):
    """Least-norm change of w2 that removes the mean bias and keeps the mean energy."""
    k = predict_moduli(base, train).numpy()
    gK, _, gE, _ = table(base, train)
    delta = np.linalg.lstsq(np.stack([gK, gE]), np.array([-np.mean(k - ktr), 0.0]), rcond=None)[0]
    params = {key: v.clone() for key, v in base.items()}
    params["w2"] = base["w2"] + torch.tensor(delta)
    return params


def permutation(n: int) -> np.ndarray:
    return np.random.default_rng(1234).permutation(n)


def build_prompt(control: bool = False) -> str:
    base, train, ktr, _, _ = setup()
    k = predict_moduli(base, train).numpy()
    gK, sK, gE, sE = table(base, train)
    w2 = base["w2"].numpy()
    shown = w2[permutation(len(w2))] if control else w2
    edges = np.quantile(ktr, [0, 0.25, 0.5, 0.75, 1.0])
    bands = []
    for i in range(4):
        rows = (ktr >= edges[i]) & ((ktr <= edges[i + 1]) if i == 3 else (ktr < edges[i + 1]))
        bands.append(f"DFT {edges[i]:.0f} to {edges[i + 1]:.0f} GPa: mean error {np.mean(k[rows] - ktr[rows]):+.1f} GPa "
                     f"({100 * np.mean((k[rows] - ktr[rows]) / ktr[rows]):+.1f}%)")
    rows = "\n".join(f"{j} | {shown[j]:.5g} | {gK[j]:+.4g} | {sK[j]:.3g} | {gE[j]:+.4g} | {sE[j]:.3g}" for j in range(len(w2)))
    sigma = train[0].A / train[0].n_atoms
    return f"""You are given the output layer of the energy head of a machine-learned interatomic potential (ORB-v3, orb_v3_conservative_inf_omat) as raw numbers. You cannot run it and you cannot train it.

# How the head works
The energy of a crystal with N atoms is
  E = {sigma:.6f} * N * ( w2 . h + b2 ) + C,     h = silu(W1 x + b1)
x is the mean over the atoms of 256 features computed by the frozen message-passing layers; W1 (256 x 256) and b1 (256) are frozen and not shown; C does not depend on the head (reference energies of the elements, pair repulsion). You can change w2 (256 numbers) and b2 (1 number). Nothing else. b2 moves the energy per atom of every crystal by the same amount and cannot change a bulk modulus.

# The fault
On {len(train)} crystals with DFT bulk moduli (Materials Project elastic tensors), this potential's bulk modulus, from a fit of energy against volume over +-3%, is wrong by {np.mean(k - ktr):+.1f} GPa on average (mean absolute error {np.mean(np.abs(k - ktr)):.1f} GPa). By range of the DFT value:
{chr(10).join(bands)}

# The task
Edit the numbers so that the bulk modulus error on NEW crystals is smaller, while the energy per atom of every crystal stays where it is: an average change above 5 meV per atom counts as a failure, because formation energies depend on it.

# What each weight of w2 does
For each weight j of w2: its value; the change of the bulk modulus in GPa per unit increase of the weight, mean over the {len(train)} crystals and standard deviation across them; the change of the energy per atom in eV per unit increase, mean and standard deviation. The bulk-modulus numbers are measured by changing the weight by {STEP} and refitting energy against volume, so they include the shift of the equilibrium volume. They hold for small changes; the energy numbers are exact, because the energy is linear in w2.
j | w2[j] | dK mean | dK sd | dE mean | dE sd
{rows}

# The other number
## b2 shape=(1,)
{float(base['b2']):.5g}

# Reply format
Reply with a JSON list of edits and no other text. Each edit is {{"tensor": name, "index": [i], "value": number}} with zero-based indices; `value` is the new value, not the change. Tensor names are w2 and b2. Change as few numbers as the task needs.
"""


def apply_reply(base, text: str, control: bool):
    """Returns the edited head and the number of weights changed."""
    w2 = base["w2"]
    shown = {"w2": w2[torch.tensor(permutation(w2.numel()))].clone() if control else w2.clone(), "b2": base["b2"].clone()}
    edited = apply_edits(shown, parse_edits(text))
    after = {k: v.clone() for k, v in base.items()}
    after["w2"] = w2 + (edited["w2"] - shown["w2"])
    after["b2"] = base["b2"] + (edited["b2"] - shown["b2"])
    changed = int((after["w2"] != w2).sum() + (after["b2"] != base["b2"]).sum())
    return after, changed


def score(run: Path, context=None) -> dict:
    base, train, ktr, test, kte = context or setup()
    control = "__ctrl" in run.name
    try:
        after, changed = apply_reply(base, (run / "reply.txt").read_text(), control)
        result = {"weights_changed": changed, "llm_edit": report(after, base, test, kte),
                  "llm_edit_on_train": report(after, base, train, ktr)}
    except Exception as error:
        result = {"invalid": f"{type(error).__name__}: {str(error)[:200]}"}
    result |= {"potential": "orb_v3_conservative_inf_omat", "control": control,
               "unedited": report(base, base, test, kte),
               "table_solve": report(table_solve(base, train, ktr), base, test, kte)}
    if (run / "meta.json").exists():
        result["meta"] = json.loads((run / "meta.json").read_text())
    (run / "score.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def baselines() -> None:
    base, train, ktr, test, kte = setup()
    rows = [{"arm": "unedited", **report(base, base, test, kte)},
            {"arm": "table_solve", **report(table_solve(base, train, ktr), base, test, kte)}]
    for name, trainable in (("gradient_w2", ("w2",)), ("gradient_head", ("W1", "b1", "w2", "b2"))):
        for penalty in PENALTIES:
            params = fit(base, train, ktr, trainable, keep_energy=penalty)
            row = {"arm": name, "penalty": penalty, **report(params, base, test, kte)}
            rows.append(row)
            print(f"{name:14} penalty {penalty:<6} MAE {row['mae_GPa']:.2f}  bias {row['bias_GPa']:+.2f}  "
                  f"energy change {row['energy_change_meV_per_atom']:.2f} meV/atom", flush=True)
    dbase = load_head()
    dft = load_cache("dft15", dbase)
    rows.append({"arm": "unedited_dft15", **report(dbase, dbase, dft, np.array([s.K_ref for s in dft]))})
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "frontier_seed0.json").write_text(json.dumps(rows, indent=2) + "\n")
    for r in rows:
        if r["arm"] in ("unedited", "table_solve", "unedited_dft15"):
            print(f"{r['arm']:14} n {r['n']} MAE {r['mae_GPa']:.2f}  bias {r['bias_GPa']:+.2f}  rho {r['spearman']:.3f}  "
                  f"energy change {r['energy_change_meV_per_atom']:.2f} meV/atom")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("baselines")
    p = sub.add_parser("prompt")
    p.add_argument("--tag", required=True)
    p.add_argument("--control", action="store_true")
    sub.add_parser("score-all")
    args = parser.parse_args()

    if args.command == "baselines":
        baselines()
    elif args.command == "prompt":
        if args.control != ("__ctrl" in args.tag):
            parser.error("control runs are tagged <model>__ctrl<k>, and only they")
        folder = HERE / "runs" / f"orb_edit__{args.tag}"
        folder.mkdir(parents=True, exist_ok=True)
        text = build_prompt(args.control)
        (folder / "prompt.txt").write_text(text)
        if not (folder / "meta.json").exists():
            (folder / "meta.json").write_text(json.dumps(
                {"arm": "orb_head_edit", "control": args.control, "tag": args.tag, "model_alias": args.tag.split("__")[0],
                 "forward_passes": 0, "prompt_chars": len(text), "prompt_tokens_estimate": estimate_tokens(text)}, indent=2) + "\n")
        print(f"{folder / 'prompt.txt'} ({len(text):,} characters, about {estimate_tokens(text):,} tokens)")
    else:
        context = setup()
        lines = ["| Run | Weights changed | MAE, GPa | Bias, GPa | Energy change, meV/atom |", "|---|---|---|---|---|"]
        for run in sorted(r for r in (HERE / "runs").iterdir() if r.name.startswith("orb_edit__") and (r / "reply.txt").exists()):
            r = score(run, context)
            if "invalid" in r:
                print(f"{run.name}: INVALID {r['invalid']}")
                lines.append(f"| {run.name} | invalid | | | |")
                continue
            e, u, t = r["llm_edit"], r["unedited"], r["table_solve"]
            print(f"{run.name}: changed {r['weights_changed']} | MAE {u['mae_GPa']:.1f} -> {e['mae_GPa']:.1f} (table solve {t['mae_GPa']:.1f}) | "
                  f"bias {u['bias_GPa']:+.1f} -> {e['bias_GPa']:+.1f} ({t['bias_GPa']:+.1f}) | "
                  f"energy change {e['energy_change_meV_per_atom']:.1f} meV/atom ({t['energy_change_meV_per_atom']:.1f})")
            lines.append(f"| {run.name} | {r['weights_changed']} | {e['mae_GPa']:.1f} | {e['bias_GPa']:+.1f} | {e['energy_change_meV_per_atom']:.1f} |")
        RESULTS.mkdir(parents=True, exist_ok=True)
        (RESULTS / "llm_edits.md").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
