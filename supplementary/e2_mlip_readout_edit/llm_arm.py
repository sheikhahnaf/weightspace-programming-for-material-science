"""E2 LLM arm: edit MACE's readout to correct its bulk moduli, without forward passes.

    python supplementary/e2_mlip_readout_edit/llm_arm.py prompt --tag opus__rep1
    python supplementary/e2_mlip_readout_edit/llm_arm.py score runs/edit__opus__rep1
    python supplementary/e2_mlip_readout_edit/llm_arm.py score-all

The prompt gives the model the readout's formulas and all 2,283 numbers, the
size and direction of the bulk-modulus error on the training half, and one
table: for each of the 128 weights of the linear readout, how much the mean
bulk modulus and the mean energy per atom move per unit change of that weight.
The same table feeds the cheap reference, `table_solve`: the smallest change
of those 128 weights that removes the mean bias and leaves the mean energy
where it was. Both are scored on the test half.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import torch

from wsp import estimate_tokens
from wsp.edit import apply_edits, diff, parse_edits
from wsp.mace_readout import EV_PER_A3_TO_GPA, load_cache, load_readout, predict_moduli

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_baselines import report  # noqa: E402

HERE = Path(__file__).resolve().parent
SEED = 0


def setup():
    base = load_readout()
    structures = load_cache("elastic", base)
    k0 = predict_moduli(base, structures).numpy()
    structures = [s for s, k in zip(structures, k0) if np.isfinite(k)]
    k_ref = np.array([s.K_ref for s in structures])
    order = np.random.default_rng(SEED).permutation(len(structures))
    half = len(order) // 2
    train, test = [structures[i] for i in order[:half]], [structures[i] for i in order[half:]]
    return base, train, k_ref[order[:half]], test, k_ref[order[half:]]


def sensitivity_table(base, train):
    """Per weight j of the linear readout: change of bulk modulus (GPa) and of energy
    per atom (eV) per unit change of the weight, mean and spread over the structures."""
    scale = float(base["scale_shift.scale"])
    dK, dE = [], []
    for s in train:
        F = s.f0.sum(1)  # (7, 128) summed over atoms
        v = (s.volumes - s.volumes.mean()) / s.volumes.std()
        A = torch.stack([torch.ones_like(v), v, v**2, v**3], dim=1)
        c = torch.linalg.lstsq(A, F).solution  # (4, 128): cubic fit of each feature in volume
        e = torch.linalg.lstsq(A, s.mace_energies.unsqueeze(-1)).solution.squeeze(-1)
        root = (-e[2] + torch.sqrt(e[2] ** 2 - 3 * e[3] * e[1])) / (3 * e[3])
        v0 = root * s.volumes.std() + s.volumes.mean()
        curvature = (2 * c[2] + 6 * c[3] * root) / s.volumes.std() ** 2
        value = c[0] + c[1] * root + c[2] * root**2 + c[3] * root**3
        factor = scale / np.sqrt(F.shape[1])
        dK.append((v0 * curvature * EV_PER_A3_TO_GPA * factor).numpy())
        dE.append((value * factor / s.element.numel()).numpy())
    dK, dE = np.array(dK), np.array(dE)
    return dK.mean(0), dK.std(0), dE.mean(0), dE.std(0)


def full_table(base, train, step: float = 0.02):
    """The same four columns, but the bulk-modulus column is the finite-difference
    derivative of the fitted bulk modulus, which includes the shift of the
    equilibrium volume. Version 1 of the prompt used the fixed-volume column of
    `sensitivity_table`; checked afterwards, that column agrees in sign with this
    one for only 9 of 16 weights tested, so version 1 gave the models a misleading guide.
    Cached in results/, since it takes 128 refits of every training structure."""
    cache = HERE / "results" / f"full_sensitivity_seed{SEED}.json"
    if cache.exists():
        d = json.loads(cache.read_text())
        return tuple(np.array(d[k]) for k in ("dK_mean", "dK_sd", "dE_mean", "dE_sd"))
    k0 = predict_moduli(base, train).numpy()
    _, _, gE, sE = sensitivity_table(base, train)
    mean, sd = [], []
    for j in range(base["readouts.0.linear.weight"].numel()):
        params = {key: v.clone() for key, v in base.items()}
        params["readouts.0.linear.weight"][j] += step
        dk = (predict_moduli(params, train).numpy() - k0) / step
        mean.append(float(np.nanmean(dk)))
        sd.append(float(np.nanstd(dk)))
    cache.parent.mkdir(exist_ok=True)
    cache.write_text(json.dumps({"step": step, "dK_mean": mean, "dK_sd": sd,
                                 "dE_mean": gE.tolist(), "dE_sd": sE.tolist()}) + "\n")
    return np.array(mean), np.array(sd), gE, sE


def table_for(version: int, base, train):
    return sensitivity_table(base, train) if version == 1 else full_table(base, train)


def dump(base) -> str:
    def row(values):
        return " ".join(f"{v:.5g}" for v in values)

    lines = []
    for name in ("scale_shift.scale", "scale_shift.shift", "readouts.0.linear.weight",
                 "readouts.1.linear_2.weight", "atomic_energies"):
        t = base[name]
        lines += [f"## {name} shape=({t.numel()},)", row(t.tolist())]
    w1 = base["readouts.1.linear_1.weight"]
    lines.append(f"## readouts.1.linear_1.weight shape=({w1.shape[0]}, {w1.shape[1]})")
    lines += [row(r) for r in w1.tolist()]
    return "\n".join(lines)


def build_prompt(version: int = 1) -> str:
    base, train, ktr, _, _ = setup()
    k = predict_moduli(base, train).numpy()
    gK, sK, gE, sE = table_for(version, base, train)
    caveat = (
        "These are first-order numbers at each crystal's current equilibrium volume: they do not include "
        "the shift of the equilibrium volume that an edit causes, and the bulk modulus depends on that volume."
        if version == 1 else
        "The bulk-modulus numbers are measured by changing the weight by 0.02 and refitting energy against "
        "volume, so they include the shift of the equilibrium volume. They hold for small changes; the energy "
        "numbers are exact, because the energy is linear in w0."
    )
    edges = np.quantile(ktr, [0, 0.25, 0.5, 0.75, 1.0])
    bands = []
    for i in range(4):
        rows = (ktr >= edges[i]) & ((ktr <= edges[i + 1]) if i == 3 else (ktr < edges[i + 1]))
        bands.append(f"DFT {edges[i]:.0f} to {edges[i + 1]:.0f} GPa: mean error {np.mean(k[rows] - ktr[rows]):+.1f} GPa "
                     f"({100 * np.mean((k[rows] - ktr[rows]) / ktr[rows]):+.1f}%)")
    table = "\n".join(
        f"{j} | {float(base['readouts.0.linear.weight'][j]):.5g} | {gK[j]:+.4g} | {sK[j]:.3g} | {gE[j]:+.4g} | {sE[j]:.3g}"
        for j in range(len(gK))
    )
    return f"""You are given the readout of a machine-learned interatomic potential (MACE-MPA-0 medium) as raw numbers. You cannot run it and you cannot train it.

# How the readout works
The energy of a crystal is
  E = sum over atoms i of [ E0[Z_i] + scale * (pair_i + r0_i + r1_i) + shift ]
  r0_i = (f0_i . w0) / sqrt(128)
  r1_i = ({1.6791768:.7f} * silu(f1_i @ W1 / sqrt(128)) . w2) / sqrt(16)
f0_i and f1_i are 128 scalar features of atom i computed by the frozen message-passing layers; pair_i is a fixed pair repulsion. You can change E0 = atomic_energies (89 numbers, one per element), w0 = readouts.0.linear.weight (128), W1 = readouts.1.linear_1.weight (128 x 16), w2 = readouts.1.linear_2.weight (16), scale and shift. Nothing else.

# The fault
On {len(train)} crystals with DFT bulk moduli (Materials Project elastic tensors), this potential's bulk modulus, from a fit of energy against volume over +-3%, is wrong by {np.mean(k - ktr):+.1f} GPa on average (mean absolute error {np.mean(np.abs(k - ktr)):.1f} GPa). By range of the DFT value:
{chr(10).join(bands)}

# The task
Edit the numbers so that the bulk modulus error on NEW crystals is smaller, while the energy per atom of every crystal stays where it is: an average change above 5 meV per atom counts as a failure, because formation energies depend on it. Note that the bulk modulus is proportional to `scale`, but so is the whole interaction energy, so changing `scale` alone moves energies by hundreds of meV per atom.

# What each weight of w0 does
For each weight j of w0: its value; the change of the bulk modulus in GPa per unit increase of the weight, mean over the {len(train)} crystals and standard deviation across them; the change of the energy per atom in eV per unit increase, mean and standard deviation. {caveat}
j | w0[j] | dK mean | dK sd | dE mean | dE sd
{table}

# All the numbers
{dump(base)}

# Reply format
Reply with a JSON list of edits and no other text. Each edit is {{"tensor": name, "index": [i, ...], "value": number}} with zero-based indices; `value` is the new value, not the change. Tensor names are exactly those in the headers above. Change as few numbers as the task needs.
"""


def table_solve(base, train, ktr, version: int = 1):
    """Least-norm change of w0 that removes the mean bias and keeps the mean energy,
    using the same table the prompt of that version shows."""
    k = predict_moduli(base, train).numpy()
    gK, _, gE, _ = table_for(version, base, train)
    A = np.stack([gK, gE])
    delta = np.linalg.lstsq(A, np.array([-np.mean(k - ktr), 0.0]), rcond=None)[0]
    params = {key: v.clone() for key, v in base.items()}
    params["readouts.0.linear.weight"] = base["readouts.0.linear.weight"] + torch.tensor(delta)
    return params


def version_of(run: Path) -> int:
    return 2 if run.name.startswith("edit_v2__") else 1


def score(run: Path) -> dict:
    base, train, ktr, test, kte = setup()
    version = version_of(run)
    try:
        edits = parse_edits((run / "reply.txt").read_text())
        after = apply_edits(base, edits)
        change = diff(base, after)
        result = {"weights_changed": change.changed, "changed_by_tensor": change.changed_by_tensor,
                  "llm_edit": report(after, base, test, kte), "llm_edit_on_train": report(after, base, train, ktr)}
    except Exception as error:
        result = {"invalid": f"{type(error).__name__}: {str(error)[:200]}"}
    result |= {"prompt_version": version, "unedited": report(base, base, test, kte),
               "table_solve": report(table_solve(base, train, ktr, version), base, test, kte)}
    if (run / "meta.json").exists():
        result["meta"] = json.loads((run / "meta.json").read_text())
    (run / "score.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("prompt")
    p.add_argument("--tag", required=True)
    p.add_argument("--version", type=int, choices=(1, 2), default=2)
    s = sub.add_parser("score")
    s.add_argument("run", type=Path)
    sub.add_parser("score-all")
    args = parser.parse_args()

    if args.command == "prompt":
        folder = HERE / "runs" / (f"edit__{args.tag}" if args.version == 1 else f"edit_v2__{args.tag}")
        folder.mkdir(parents=True, exist_ok=True)
        text = build_prompt(args.version)
        (folder / "prompt.txt").write_text(text)
        if not (folder / "meta.json").exists():
            (folder / "meta.json").write_text(json.dumps(
                {"arm": "mace_readout_edit", "prompt_version": args.version, "tag": args.tag, "model_alias": args.tag.split("__")[0],
                 "forward_passes": 0, "prompt_chars": len(text), "prompt_tokens_estimate": estimate_tokens(text)}, indent=2) + "\n")
        print(f"{folder / 'prompt.txt'} ({len(text):,} characters, about {estimate_tokens(text):,} tokens)")
    else:
        runs = [args.run] if args.command == "score" else sorted(r for r in (HERE / "runs").iterdir() if (r / "reply.txt").exists())
        for run in runs:
            r = score(run)
            if "invalid" in r:
                print(f"{run.name}: INVALID {r['invalid']}")
            else:
                e, u, t = r["llm_edit"], r["unedited"], r["table_solve"]
                print(f"{run.name}: changed {r['weights_changed']} {r['changed_by_tensor']} | MAE {u['mae_GPa']:.1f} -> {e['mae_GPa']:.1f} "
                      f"(table solve {t['mae_GPa']:.1f}) | bias {u['bias_GPa']:+.1f} -> {e['bias_GPa']:+.1f} ({t['bias_GPa']:+.1f}) | "
                      f"energy change {e['energy_change_meV_per_atom']:.1f} meV/atom ({t['energy_change_meV_per_atom']:.1f})")


if __name__ == "__main__":
    main()
