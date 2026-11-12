"""E1: the written network as the GP's inputs, not only its prior mean.

Companion of run_structure_prior.py (same tasks, same rows, same draws). The written
15 -> 16 -> 1 networks have a hidden layer of 16 ReLU units. Here those units, evaluated
on the named descriptors of each crystal, are the inputs of the GP in place of (or next
to) the 50 embedding coordinates. No new LLM calls.

    python experiments/e1_surrogate_head/run_structure_features.py --jobs 3

Arms, per written network (Opus 5.5 and Fable 5.2 replies):
  hidden            GP on the hidden units, constant mean
  hidden+prior      GP on the hidden units, two-stage prior mean = the network's output
  emb+hidden        GP on embedding and hidden units, constant mean
  emb+hidden+prior  the same with the two-stage prior mean
References computed in run_structure_prior.py: plain GP on the embedding, GP on embedding
and raw descriptors, and the embedding GP with the written prior mean.
"""

from __future__ import annotations

import argparse
import json
import sys
import warnings
from dataclasses import replace
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run_structure_prior as sp  # noqa: E402

OUT = sp.OUT / "features"
MODELS = ("opus", "fable")
ARMS = ("hidden", "hidden+prior", "emb+hidden", "emb+hidden+prior")


def hidden_and_output(task_name: str) -> dict[str, tuple[np.ndarray, np.ndarray]]:
    import torch

    import filter_arm
    from wsp.heads import MLPHead
    from wsp.serialize import load_weights

    D = torch.tensor(sp.descriptors(task_name), dtype=torch.float32)
    key = sp.TASKS[task_name]
    out = {}
    for folder in sorted((sp.E3 / "runs").glob(f"filter_{key}__*")):
        name = folder.name.replace(f"filter_{key}__", "")
        if name.split("__")[0] not in MODELS or not (folder / "reply.txt").exists():
            continue
        try:
            head = MLPHead(len(filter_arm.FEATURES), (16,), 1)
            head.load_state_dict(load_weights((folder / "reply.txt").read_text()))
        except Exception:
            continue
        with torch.no_grad():
            h = torch.relu(head.net[0](D))
            out[name] = (h.numpy().astype(float), head.net[2](h).squeeze(-1).numpy().astype(float))
    return out


def cell(task_name: str, run: int, n: int, draw: int) -> dict:
    cache = OUT / "cells" / task_name / f"run{run}__n{n}__draw{draw}.json"
    if cache.exists():
        return json.loads(cache.read_text())
    import torch

    from wsp.arms import gp_with_prior
    from wsp.baselines import fit_gp, prepare, score
    from wsp.tasks import load_task

    warnings.filterwarnings("ignore")
    torch.set_num_threads(1)
    task = load_task(task_name)
    pool, test = task.split(run)
    train = pool[np.random.default_rng(1000 * run + draw).permutation(len(pool))[:n]] if n else pool
    y = task.y
    U = (task.X - task.X[pool].mean(0)) / (task.X[pool].std(0) + 1e-8)
    base = replace(prepare(task, run), y_train=y[train], y_test=y[test],
                   y_mean=float(y[train].mean()), y_std=float(y[train].std() + 1e-8))

    def measure(mean, std):
        return score(base.y_test, mean, std) | {"nll": sp.nll(base.y_test, mean, std), "top_recall": sp.top_recall(base.y_test, mean)}

    out = {"task": task_name, "run": run, "n": int(len(train)), "draw": draw, "nets": {}}
    for name, (H, m) in hidden_and_output(task_name).items():
        live = H[pool].std(0) > 1e-9  # units that are constant on the pool carry nothing
        Hz = (H[:, live] - H[pool][:, live].mean(0)) / H[pool][:, live].std(0)
        entry = {"live_units": int(live.sum())}
        for label, Z in (("hidden", Hz), ("emb+hidden", np.hstack([U, Hz]))):
            data = replace(base, U_train=Z[train], U_test=Z[test])
            try:
                entry[label] = measure(*fit_gp(data))
                entry[label + "+prior"] = measure(*gp_with_prior(data, m[train], m[test])[:2])
            except Exception as error:
                entry[label] = entry[label + "+prior"] = {"failed": type(error).__name__}
        out["nets"][name] = entry
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps(out) + "\n")
    return out


def main() -> None:
    from joblib import Parallel, delayed

    from wsp.tasks import _CLOSED_LOOPS, _closed_loop_table

    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--jobs", type=int, default=3)
    args = parser.parse_args()
    work = []
    for task_name in sp.TASKS:
        sp.descriptors(task_name)
        n_runs = _closed_loop_table(*_CLOSED_LOOPS[task_name])[1]
        work += [(task_name, r, n, d) for r in range(n_runs) for n in sp.SIZES for d in range(sp.DRAWS if n else 1)]
    cells = Parallel(n_jobs=args.jobs)(delayed(cell)(*w) for w in work)
    lines, summary = [], {}
    for task_name in sp.TASKS:
        lines += [f"**`{task_name}`**: ρ on the generated structures (best tenth found)", "",
                  "| Labels | Model | " + " | ".join(ARMS) + " |", "|---|---|" + "---|" * len(ARMS)]
        mine = [c for c in cells if c["task"] == task_name]
        for n in sorted({c["n"] for c in mine}):
            for model in MODELS:
                row = []
                for arm in ARMS:
                    vals = [v[arm] for c in mine if c["n"] == n for k, v in c["nets"].items() if k.startswith(model) and "failed" not in v[arm]]
                    rho, rec = float(np.mean([v["spearman"] for v in vals])), float(np.mean([v["top_recall"] for v in vals]))
                    summary[f"{task_name}|n{n}|{model}|{arm}"] = {"spearman": rho, "top_recall": rec, "fits": len(vals)}
                    row.append(f"{rho:.2f} ({rec:.2f})")
                lines.append(f"| {n} | {model} | " + " | ".join(row) + " |")
        lines.append("")
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    (OUT / "summary.md").write_text("\n".join(lines) + "\nMeans over runs, draws and the model's replies.\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
