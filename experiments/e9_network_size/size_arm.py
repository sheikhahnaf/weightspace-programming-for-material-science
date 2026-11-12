"""E9: does the size of the written network matter?

The write prompt of E1 and E7, unchanged except for the architecture: one hidden layer of
64 units, or two hidden layers of 32. The 16-unit networks of E1 and E7 are the reference.
Opus 5.5 only, two replies per task and size, no data, no tools beyond reading the prompt
and writing the reply.

    python experiments/e9_network_size/size_arm.py prompt     # run folders under runs/
    python experiments/e9_network_size/size_arm.py score      # results/summary.md

Scored on every candidate of a task with no labels (rank correlation, R2 as written and
after the best straight-line rescaling, hidden units with a non-zero path to the output),
and as a GP prior mean at 5 labels (two-stage fit, five seeds, as in E1).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import warnings
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "experiments" / "e1_surrogate_head"))

TASKS = ("mpea_hardness", "ti_alloy_yield_strength", "ni_superalloy_solidus", "steel_austenite_fraction")
SIZES = {"h64": (64,), "h32x32": (32, 32)}
REPS = (1, 2)
RUN = re.compile(r"write__(?P<task>.+)__(?P<size>h64|h32x32|h16)__opus__rep(?P<rep>\d+)")
REFERENCE = {"mpea_hardness": "e1_surrogate_head", "ti_alloy_yield_strength": "e1_surrogate_head",
             "ni_superalloy_solidus": "e7_calphad_prior", "steel_austenite_fraction": "e7_calphad_prior"}


def prompts() -> None:
    from wsp import estimate_tokens
    from wsp.arms import write_prompt
    from wsp.tasks import load_task

    for task_name in TASKS:
        for size, hidden in SIZES.items():
            text = write_prompt(load_task(task_name), hidden)
            for rep in REPS:
                folder = HERE / "runs" / f"write__{task_name}__{size}__opus__rep{rep}"
                if (folder / "reply.txt").exists() and (folder / "prompt.txt").read_text() != text:
                    raise SystemExit(f"{folder.name} has a reply to a different prompt; not overwriting it")
                folder.mkdir(parents=True, exist_ok=True)
                (folder / "prompt.txt").write_text(text)
                if not (folder / "meta.json").exists():
                    (folder / "meta.json").write_text(json.dumps({
                        "arm": "write_size", "task": task_name, "hidden": list(hidden), "prompt_chars": len(text),
                        "prompt_tokens_estimate": estimate_tokens(text), "model": None, "tools_allowed": None,
                        "forward_passes": 0, "prompt_tokens": None, "reply_tokens": None}, indent=2) + "\n")
                print(folder.name, len(text), "characters")


def used_units(head) -> tuple[int, int]:
    """Hidden units of the first layer with a non-zero path to the output, and their total."""
    import torch

    layers = [m for m in head.net if isinstance(m, torch.nn.Linear)]
    reach = (layers[-1].weight.detach().abs().sum(0) > 0)
    for layer in reversed(layers[1:-1]):
        reach = ((layer.weight.detach().abs() * reach[:, None].float()).sum(0) > 0)
    alive = layers[0].weight.detach().abs().sum(1) + layers[0].bias.detach().abs() > 0
    return int((reach & alive).sum()), int(len(reach))


def one(task, reply: str, hidden: tuple[int, ...]) -> dict:
    from scipy.stats import pearsonr, spearmanr

    from wsp.arms import score_prior, written_head
    from wsp.baselines import predict, prepare

    head = written_head(task, reply, hidden)
    data = prepare(task, 0)
    U, y = np.vstack([data.U_train, data.U_test]), np.concatenate([data.y_train, data.y_test])
    m = predict(head, U)
    if np.std(m) == 0:
        return {"constant_output": True, "weights": sum(p.numel() for p in head.parameters())}
    rows = score_prior(task, lambda X: predict(head, X), seeds=5, sizes=(5,))
    used, total = used_units(head)
    return {"weights": sum(p.numel() for p in head.parameters()), "rho": float(spearmanr(m, y).statistic),
            "r2_as_written": float(1 - np.mean((m - y) ** 2) / y.var()), "r2_rescaled": float(pearsonr(m, y).statistic ** 2),
            "units_used": used, "units": total,
            "gp5": float(np.mean([r["n5"]["gp"]["spearman"] for r in rows])),
            "gp5_with_prior": float(np.mean([r["n5"]["gp_with_prior_fitted"]["spearman"] for r in rows]))}


def score() -> None:
    from wsp.tasks import load_task

    warnings.filterwarnings("ignore")
    rows = []
    for task_name in TASKS:
        task = load_task(task_name)
        folders = sorted((ROOT / "experiments" / REFERENCE[task_name] / "runs").glob(f"write__{task_name}__opus__rep*"))
        runs = [(f, "h16", (16,)) for f in folders]
        runs += [(f, RUN.fullmatch(f.name)["size"], SIZES[RUN.fullmatch(f.name)["size"]])
                 for f in sorted((HERE / "runs").glob(f"write__{task_name}__*")) if RUN.fullmatch(f.name)]
        for folder, size, hidden in runs:
            reply = folder / "reply.txt"
            if not reply.exists():
                continue
            try:
                result = one(task, reply.read_text(), hidden)
            except Exception as error:  # a malformed reply is recorded, not repaired
                result = {"invalid": f"{type(error).__name__}: {str(error)[:160]}"}
            rows.append({"task": task_name, "size": size, "run": folder.name} | result)
            print(rows[-1], flush=True)
    out = HERE / "results"
    out.mkdir(exist_ok=True)
    (out / "per_reply.json").write_text(json.dumps(rows, indent=1) + "\n")
    lines = ["| Task | Hidden layers | Weights | Replies (valid) | ρ, no labels | R² as written | R² rescaled | Hidden units used | GP ρ at 5 labels: plain → with the network |",
             "|---|---|---|---|---|---|---|---|---|"]
    names = {"h16": "16", "h64": "64", "h32x32": "32 + 32"}
    for task_name in TASKS:
        for size in ("h16", "h64", "h32x32"):
            mine = [r for r in rows if r["task"] == task_name and r["size"] == size]
            good = [r for r in mine if "rho" in r]
            if not mine:
                continue
            if not good:
                lines.append(f"| `{task_name}` | {names[size]} | | {len(mine)} (0) | | | | | |")
                continue
            mean = lambda k: float(np.mean([r[k] for r in good]))  # noqa: E731
            lines.append(f"| `{task_name}` | {names[size]} | {good[0]['weights']:,} | {len(mine)} ({len(good)}) | {mean('rho'):.2f} | "
                         f"{mean('r2_as_written'):.2f} | {mean('r2_rescaled'):.2f} | {mean('units_used'):.1f} of {good[0]['units']} | "
                         f"{mean('gp5'):.2f} → {mean('gp5_with_prior'):.2f} |")
    (out / "summary.md").write_text("\n".join(lines) + "\n\nOpus 5.5; means over valid replies. Units used: first-layer units with a non-zero path to the output.\n")
    print("\n".join(lines))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("command", choices=("prompt", "score"))
    {"prompt": prompts, "score": score}[parser.parse_args().command]()
