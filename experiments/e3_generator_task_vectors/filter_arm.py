"""E3 filter arm: an LLM-written scoring network in front of the crystal generator.

The generator is left untouched. A small network, written by an LLM from materials
knowledge with no data, scores each generated crystal from 15 named descriptors of
its composition and as-generated volume; only the best-scored crystals would be sent
to the expensive oracle. Tested on the crystals already sampled and scored on FASTER
(results/hprc/: 11 MatterGen variants x 128, eSEN bulk modulus and heat capacity).

  python filter_arm.py prompt --target K --tag opus__rep1     # writes runs/filter_K__opus__rep1/prompt.txt
  python filter_arm.py score                                  # scores every reply, writes results/filter_arm/

References given the same inputs and no LLM: for bulk modulus, an MLP of the same size
trained on 400 Materials Project structures (data/mlip_reference/elastic.extxyz) and the
one-line rule "smaller volume per atom is stiffer"; for heat capacity, the Dulong-Petit
rule 3R / mean atomic mass.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import warnings
from pathlib import Path

import numpy as np
import torch
from scipy.stats import spearmanr

from wsp import MLPHead, build_prompt, estimate_tokens, load_weights, zero_

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
HPRC = HERE / "results" / "hprc"
GROUPS = {
    "frac_alkali": "Li Na K Rb Cs", "frac_alkaline_earth": "Be Mg Ca Sr Ba",
    "frac_3d_transition": "Sc Ti V Cr Mn Fe Co Ni Cu Zn",
    "frac_4d_5d_transition": "Y Zr Nb Mo Tc Ru Rh Pd Ag Cd Hf Ta W Re Os Ir Pt Au Hg",
    "frac_lanthanide_actinide": "La Ce Pr Nd Pm Sm Eu Gd Tb Dy Ho Er Tm Yb Lu Ac Th Pa U Np Pu",
    "frac_p_block_metal": "Al Ga In Sn Tl Pb Bi", "frac_metalloid": "B Si Ge As Sb Te",
    "frac_C_N_O": "C N O", "frac_S_Se_P": "S Se P", "frac_halogen": "F Cl Br I", "frac_H": "H",
}
FEATURES = ("volume_per_atom_A3", "mean_atomic_mass_u", "mean_pauling_electronegativity",
            "mean_elemental_melting_point_K", *GROUPS)
TARGETS = {"K": ("K_GPa", "bulk modulus", "GPa", 150.0), "Cp": ("Cp_J_per_gK", "heat capacity at 300 K per gram", "J/g/K", 0.4)}
RUN = re.compile(r"filter_(K|Cp)__(fable|opus|sonnet|haiku)__rep(\d+)")


def describe(atoms) -> np.ndarray:
    from pymatgen.core import Element

    symbols = atoms.get_chemical_symbols()
    elements = [Element(s) for s in symbols]
    row = [atoms.get_volume() / len(atoms), np.mean([e.atomic_mass for e in elements]),
           np.mean([e.X if e.X == e.X else 1.5 for e in elements]),
           np.mean([e.melting_point or 1000.0 for e in elements])]
    row += [np.mean([s in members.split() for s in symbols]) for members in GROUPS.values()]
    return np.array(row, dtype=float)


def crystals() -> list[dict]:
    from ase.io import read

    rows = []
    for folder in sorted(HPRC.iterdir()):
        if not (folder / "scores.csv").exists():
            continue
        frames = read(folder / "generated_crystals.extxyz", index=":")
        with (folder / "scores.csv").open() as handle:
            for r in csv.DictReader(handle):
                i = int(r["index"])
                value = lambda k: float(r[k]) if r.get(k) not in (None, "", "nan") else float("nan")
                rows.append({"variant": folder.name, "index": i, "x": describe(frames[i]),
                             "K": value("K_GPa"), "Cp": value("Cp_J_per_gK")})
    return rows


def prompt(target: str) -> str:
    column, name, unit, _ = TARGETS[target]
    head = zero_(MLPHead(len(FEATURES), (16,), 1))
    inputs = "\n".join(f"x[{i}] = {f}" for i, f in enumerate(FEATURES))
    groups = "\n".join(f"{g}: atomic fraction of {m}" for g, m in GROUPS.items())
    job = (
        f"Write the weights of this network from what you know about materials. No training data is given. "
        f"The network scores crystals proposed by a generative model (inorganic, up to 20 atoms per cell, any "
        f"elements) so that only the most promising are sent to an expensive calculation. The output y must be "
        f"your best estimate of the crystal's {name} in {unit}; what matters most is that crystals with a high "
        f"true value get a high score.\n\nInputs, not standardised:\n{inputs}\n\n"
        f"volume_per_atom_A3 is the cell volume divided by the number of atoms, as generated (not relaxed). "
        f"The means are over the atoms of the cell. The fractions are:\n{groups}\n"
        f"Typical ranges: volume per atom 8 to 60, mean atomic mass 7 to 200, mean electronegativity 0.8 to 3.5, "
        f"mean melting point 300 to 3700."
    )
    return build_prompt("write", job, head.describe(), head.state_dict())


def scorer(reply: str):
    head = MLPHead(len(FEATURES), (16,), 1)
    head.load_state_dict(load_weights(reply))
    head.eval()
    return lambda X: head(torch.tensor(X, dtype=torch.float32)).detach().squeeze(-1).numpy().astype(float)


def trained_k_scorer(seed: int = 0):
    """An MLP of the same size trained on 400 Materials Project structures with DFT K_VRH."""
    from ase.io import read

    frames = read(ROOT / "data" / "mlip_reference" / "elastic.extxyz", index=":")
    X = np.array([describe(a) for a in frames])
    y = np.array([a.info["K_ref"] for a in frames])
    mu, sd = X.mean(0), X.std(0) + 1e-8
    torch.manual_seed(seed)
    head = MLPHead(len(FEATURES), (16,), 1)
    opt = torch.optim.AdamW(head.parameters(), lr=3e-3, weight_decay=1e-2)
    Xt = torch.tensor((X - mu) / sd, dtype=torch.float32)
    yt = torch.tensor((y - y.mean()) / y.std(), dtype=torch.float32).unsqueeze(-1)
    for _ in range(800):
        opt.zero_grad()
        torch.nn.functional.mse_loss(head(Xt), yt).backward()
        opt.step()
    head.eval()
    return lambda Z: head(torch.tensor((Z - mu) / sd, dtype=torch.float32)).detach().squeeze(-1).numpy().astype(float)


def evaluate(score: np.ndarray, truth: np.ndarray, threshold: float, keep: float = 0.25) -> dict:
    ok = np.isfinite(truth)
    s, t = score[ok], truth[ok]
    order = np.argsort(-s, kind="stable")
    k = max(1, int(round(keep * len(t))))
    hits = np.cumsum(t[order] > threshold)
    n_hits = int((t > threshold).sum())
    want = max(1, n_hits // 2)
    calls = int(np.argmax(hits >= want)) + 1 if n_hits else None
    return {
        "n": int(len(t)), "spearman": float(spearmanr(s, t).statistic) if np.ptp(s) > 0 else 0.0,
        "mean_all": float(t.mean()), "mean_kept": float(t[order[:k]].mean()),
        "mean_best_possible": float(np.sort(t)[::-1][:k].mean()),
        "share_above_all": float((t > threshold).mean()), "share_above_kept": float((t[order[:k]] > threshold).mean()),
        "hits_total": n_hits, "calls_to_half_the_hits": calls,
        "calls_to_half_the_hits_random": float(want * (len(t) + 1) / (n_hits + 1)) if n_hits else None,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("prompt")
    p.add_argument("--target", choices=tuple(TARGETS), required=True)
    p.add_argument("--tag", required=True)
    p = sub.add_parser("score")
    p.add_argument("--backbone", choices=("mg", "cf"), default="mg", help="whose samples to score: MatterGen or CrystalFlow")
    args = parser.parse_args()
    warnings.filterwarnings("ignore")

    if args.command == "prompt":
        folder = HERE / "runs" / f"filter_{args.target}__{args.tag}"
        folder.mkdir(parents=True, exist_ok=True)
        text = prompt(args.target)
        (folder / "prompt.txt").write_text(text)
        if not (folder / "meta.json").exists():
            (folder / "meta.json").write_text(json.dumps({"arm": "generator_filter", "target": args.target, "tag": args.tag,
                                                          "prompt_tokens_estimate": estimate_tokens(text)}, indent=2) + "\n")
        print(folder / "prompt.txt", len(text), "characters")
        return

    global HPRC
    suffix = "" if args.backbone == "mg" else f"_{args.backbone}"
    HPRC = HERE / "results" / f"hprc{suffix}"
    rows = crystals()
    X = np.array([r["x"] for r in rows])
    is_base = np.array([r["variant"] == "base" for r in rows])
    out = HERE / "results" / f"filter_arm{suffix}"
    out.mkdir(parents=True, exist_ok=True)
    table, lines = [], []
    for target, (_, name, unit, threshold) in TARGETS.items():
        truth = np.array([r[target] for r in rows])
        arms = {}
        if target == "K":
            arms["rule: small volume per atom"] = -X[:, 0]
            arms["MLP trained on 400 MP structures"] = trained_k_scorer()(X)
        else:
            arms["rule: Dulong-Petit, 1 / mean atomic mass"] = 1.0 / X[:, 1]
        for folder in sorted((HERE / "runs").glob(f"filter_{target}__*")):
            if not (folder / "reply.txt").exists():
                continue
            meta = json.loads((folder / "meta.json").read_text())
            label = f"{meta.get('model', RUN.fullmatch(folder.name).group(2))} | {folder.name}"
            try:
                arms[label] = scorer((folder / "reply.txt").read_text())(X)
            except Exception as error:
                table.append({"target": target, "arm": label, "invalid": f"{type(error).__name__}: {str(error)[:120]}"})
        for label, score in arms.items():
            table.append({"target": target, "arm": label,
                          "base_128": evaluate(score[is_base], truth[is_base], threshold),
                          "all_variants": evaluate(score, truth, threshold)})
        lines += [f"**{name} ({unit}); a hit is a crystal above {threshold:g}; the filter keeps the top quarter**", "",
                  "| Scorer | Replies | Base samples: ρ | mean of all → kept (best possible) | hit share all → kept | oracle calls to half the hits (random) | All variants: ρ | mean all → kept |",
                  "|---|---|---|---|---|---|---|---|"]
        groups: dict[str, list] = {}
        for row in table:
            if row["target"] == target and "invalid" not in row:
                groups.setdefault(row["arm"].split(" | ")[0], []).append(row)
        for label, rs in groups.items():
            m = lambda scope, key: float(np.mean([r[scope][key] for r in rs if r[scope][key] is not None]))
            lines.append(
                f"| {label} | {len(rs)} | {m('base_128', 'spearman'):.2f} | {m('base_128', 'mean_all'):.3g} → {m('base_128', 'mean_kept'):.3g} "
                f"({m('base_128', 'mean_best_possible'):.3g}) | {m('base_128', 'share_above_all'):.2f} → {m('base_128', 'share_above_kept'):.2f} "
                f"| {m('base_128', 'calls_to_half_the_hits'):.0f} ({m('base_128', 'calls_to_half_the_hits_random'):.0f}) "
                f"| {m('all_variants', 'spearman'):.2f} | {m('all_variants', 'mean_all'):.3g} → {m('all_variants', 'mean_kept'):.3g} |")
        lines.append("")
    (out / "per_run.json").write_text(json.dumps(table, indent=1) + "\n")
    (out / "summary.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    for row in table:
        if "invalid" in row:
            print("INVALID", row["arm"], row["invalid"])


if __name__ == "__main__":
    main()
