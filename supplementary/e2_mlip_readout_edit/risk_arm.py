"""E2, write arm: an LLM-written network that says where a universal potential's bulk
modulus is likely to be wrong, so that those crystals are sent to DFT.

    python risk_arm.py prompt --tag opus__rep1      # writes runs/risk__opus__rep1/prompt.txt
    python risk_arm.py score

The network is 16 -> 16 -> 1, written with no data. Inputs: the 15 composition and
volume descriptors of the generator filter arm, plus the bulk modulus the potential
itself predicts. Output: the expected absolute error of that prediction in GPa.

Scored on the 400 crystals of the elastic set for each potential that has been cached:
Spearman correlation with the true absolute error, and the share of the total absolute
error that sits in the quarter of crystals the network flags (0.25 for a random flag).
References: the rule "the error grows with the predicted bulk modulus", and the same
network trained on 50 or 200 labelled crystals (scored on the others).
"""

from __future__ import annotations

import argparse
import json
import sys
import warnings
from pathlib import Path

import numpy as np
import torch
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "experiments" / "e3_crystal_filter"))
import filter_arm  # noqa: E402

from wsp import MLPHead, build_prompt, estimate_tokens, load_weights, zero_  # noqa: E402
from wsp.linear_head import load, predict_moduli  # noqa: E402

FEATURES = (*filter_arm.FEATURES, "bulk_modulus_predicted_by_the_potential_GPa")


def prompt() -> str:
    head = zero_(MLPHead(len(FEATURES), (16,), 1))
    inputs = "\n".join(f"x[{i}] = {f}" for i, f in enumerate(FEATURES))
    groups = "\n".join(f"{g}: atomic fraction of {m}" for g, m in filter_arm.GROUPS.items())
    job = (
        "Write the weights of this network from what you know about materials and about machine-learned interatomic "
        "potentials. No training data is given. A universal potential trained on PBE calculations (one of MACE-MPA-0, "
        "ORB-v3, eSEN-30M-OAM, GRACE-2L-OAM) has relaxed an inorganic crystal from the Materials Project and predicted its "
        "bulk modulus from a fit of energy against volume. The output y must be your best estimate of the ABSOLUTE error "
        "of that prediction against the DFT (PBE) bulk modulus, in GPa. It is used to decide which crystals are checked "
        "with DFT, so what matters most is that crystals with a large true error get a large y.\n\n"
        f"Inputs, not standardised:\n{inputs}\n\n"
        "volume_per_atom_A3 is the DFT-relaxed cell volume divided by the number of atoms. The means are over the atoms "
        f"of the cell. The fractions are:\n{groups}\n"
        "Typical ranges: volume per atom 8 to 60, mean atomic mass 7 to 200, mean electronegativity 0.8 to 3.5, "
        "mean melting point 300 to 3700, predicted bulk modulus 10 to 350."
    )
    return build_prompt("write", job, head.describe(), head.state_dict())


def scorer(reply: str):
    head = MLPHead(len(FEATURES), (16,), 1)
    head.load_state_dict(load_weights(reply))
    head.eval()
    return lambda X: head(torch.tensor(X, dtype=torch.float32)).detach().squeeze(-1).numpy().astype(float)


def trained(X, y, rows, seed=0):
    mu, sd = X[rows].mean(0), X[rows].std(0) + 1e-8
    torch.manual_seed(seed)
    head = MLPHead(len(FEATURES), (16,), 1)
    opt = torch.optim.AdamW(head.parameters(), lr=3e-3, weight_decay=1e-2)
    Xt = torch.tensor((X[rows] - mu) / sd, dtype=torch.float32)
    yt = torch.tensor((y[rows] - y[rows].mean()) / (y[rows].std() + 1e-8), dtype=torch.float32).unsqueeze(-1)
    for _ in range(500):
        opt.zero_grad()
        torch.nn.functional.mse_loss(head(Xt), yt).backward()
        opt.step()
    head.eval()
    return head(torch.tensor((X - mu) / sd, dtype=torch.float32)).detach().squeeze(-1).numpy().astype(float)


def evaluate(score, error) -> dict:
    k = max(1, len(error) // 4)
    top = np.argsort(-score, kind="stable")[:k]
    return {"spearman": float(spearmanr(score, error).statistic) if np.ptp(score) > 0 else 0.0,
            "share_of_error_in_flagged_quarter": float(error[top].sum() / error.sum()),
            "best_possible_share": float(np.sort(error)[::-1][:k].sum() / error.sum())}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("prompt")
    p.add_argument("--tag", required=True)
    sub.add_parser("score")
    args = parser.parse_args()
    warnings.filterwarnings("ignore")
    if args.command == "prompt":
        folder = HERE / "runs" / f"risk__{args.tag}"
        folder.mkdir(parents=True, exist_ok=True)
        text = prompt()
        (folder / "prompt.txt").write_text(text)
        if not (folder / "meta.json").exists():
            (folder / "meta.json").write_text(json.dumps({"arm": "mlip_error_risk_write", "tag": args.tag, "model_alias": args.tag.split("__")[0],
                                                          "forward_passes": 0, "prompt_tokens_estimate": estimate_tokens(text)}, indent=2) + "\n")
        print(folder / "prompt.txt", len(text), "characters")
        return

    from ase.io import read
    frames = read(ROOT / "data" / "mlip_reference" / "elastic.extxyz", index=":")
    names = [str(a.info.get("name")) for a in frames]
    truth = np.array([a.info["K_ref"] for a in frames])
    D = np.array([filter_arm.describe(a) for a in frames])
    replies = {f.name.replace("risk__", ""): (f / "reply.txt").read_text()
               for f in sorted((HERE / "runs").glob("risk__*")) if (f / "reply.txt").exists()}
    table = {}
    for potential in ("mace", "orb", "esen", "grace"):
        try:
            base, structures = load(potential)
        except FileNotFoundError:
            continue
        if len(structures) < 300:
            continue
        by_name = {s.name: float(k) for s, k in zip(structures, predict_moduli(base, structures))}
        k = np.array([by_name.get(n, np.nan) for n in names])
        ok = np.isfinite(k)
        X, error = np.column_stack([D[ok], k[ok]]), np.abs(k[ok] - truth[ok])
        rows = {"rule: error grows with predicted bulk modulus": evaluate(k[ok], error)}
        for n in (50, 200):
            rs = []
            for seed in range(5):
                order = np.random.default_rng(seed).permutation(len(error))
                s = trained(X, error, order[:n], seed)
                rs.append(evaluate(s[order[n:]], error[order[n:]]))
            rows[f"same network trained on {n} labels"] = {m: float(np.mean([r[m] for r in rs])) for m in rs[0]}
        for tag, reply in replies.items():
            try:
                rows[f"written: {tag}"] = evaluate(scorer(reply)(X), error)
            except Exception as e:
                rows[f"written: {tag}"] = {"invalid": f"{type(e).__name__}: {str(e)[:120]}"}
        table[potential] = rows
    out = HERE / "results" / "risk"
    out.mkdir(parents=True, exist_ok=True)
    (out / "risk.json").write_text(json.dumps(table, indent=2) + "\n")
    lines = []
    for potential, rows in table.items():
        lines += [f"**{potential}**", "", "| Scorer | ρ with absolute error | Share of error in flagged quarter (best possible) |", "|---|---|---|"]
        for name, r in rows.items():
            lines.append(f"| {name} | invalid | |" if "invalid" in r else
                         f"| {name} | {r['spearman']:.2f} | {r['share_of_error_in_flagged_quarter']:.2f} ({r['best_possible_share']:.2f}) |")
        lines.append("")
    (out / "risk.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
