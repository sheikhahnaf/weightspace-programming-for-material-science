"""Score every write-arm reply and tabulate by task and model.

For each `runs/write__<task>[__<model>]__rep<k>/reply.txt` this scores the
written network alone and as a GP prior mean (both slope rules), then writes

  results/write_arm/per_run.json     one row per reply
  results/write_arm/summary.json     mean over replies per task and model, with the
                                     plain GP and the no-LLM handbook baseline
  results/write_arm/summary.md       the same as a table

A reply that does not parse is recorded as invalid and scored as nothing.
Resumable: a run with a score.json newer than its reply is not rescored.

    python experiments/e1_surrogate_head/score_write_all.py
"""

from __future__ import annotations

import json
import re
import warnings
from collections import defaultdict
from pathlib import Path

import numpy as np

from wsp.arms import handbook_prior, score_prior, score_write
from wsp.tasks import load_task

HERE = Path(__file__).resolve().parent
RUN = re.compile(r"write__(?P<task>.+?)(?:__(?P<model>fable|opus|sonnet|haiku))?(?:__rep(?P<rep>\d+))?$")
SIZES = ("n5", "n10", "n20", "n50")


def mean(rows, *path):
    values = []
    for row in rows:
        v = row
        for key in path:
            v = v.get(key) if isinstance(v, dict) else None
            if v is None:
                break
        if v is not None:
            values.append(v)
    return float(np.mean(values)) if values else float("nan")


def main() -> None:
    warnings.filterwarnings("ignore")
    per_run = []
    for folder in sorted((HERE / "runs").glob("write__*")):
        m = RUN.fullmatch(folder.name)
        reply = folder / "reply.txt"
        if not m or not reply.exists():
            continue
        task_name, model, rep = m["task"], m["model"] or "fable", int(m["rep"] or 1)
        score_file = folder / "score.json"
        meta = json.loads((folder / "meta.json").read_text()) if (folder / "meta.json").exists() else {}
        meta.setdefault("model_alias", model)
        if score_file.exists() and score_file.stat().st_mtime >= reply.stat().st_mtime and "n5" in json.dumps(json.loads(score_file.read_text()).get("per_seed", [{}])[0]):
            result = json.loads(score_file.read_text())
        else:
            try:
                result = score_write(load_task(task_name), reply.read_text())
            except Exception as error:  # malformed reply: keep the record, score nothing
                result = {"arm": "write", "task": task_name, "invalid": f"{type(error).__name__}: {str(error)[:200]}"}
            result["meta"] = meta
            score_file.write_text(json.dumps(result, indent=2) + "\n")
        per_run.append({"run": folder.name, "task": task_name, "model": model, "rep": rep,
                        "invalid": result.get("invalid"), "per_seed": result.get("per_seed")})
        print(f"{folder.name}: {'INVALID ' + result['invalid'] if result.get('invalid') else 'ok'}", flush=True)

    out = HERE / "results" / "write_arm"
    out.mkdir(parents=True, exist_ok=True)
    (out / "per_run.json").write_text(json.dumps(per_run, indent=1) + "\n")

    summary, lines = {}, [
        "| Task | Source | Replies (valid) | Alone ρ | ρ at 5 labels: GP → +prior (fitted / one) | at 10 | at 20 | at 50 |",
        "|---|---|---|---|---|---|---|---|",
    ]
    by_task = defaultdict(lambda: defaultdict(list))
    for row in per_run:
        by_task[row["task"]][row["model"]].append(row)
    for task_name, models in by_task.items():
        task = load_task(task_name)
        handbook = score_prior(task, handbook_prior(task))
        summary[task_name] = {}

        def entry(label, replies_seedrows, n_valid, n_total):
            # replies_seedrows: list (one per reply) of per-seed rows
            flat = [r for rows in replies_seedrows for r in rows]
            item = {"replies": n_total, "valid": n_valid, "alone_spearman": mean(flat, "written_alone", "spearman"),
                    "alone_spearman_per_reply": [mean(rows, "written_alone", "spearman") for rows in replies_seedrows]}
            cells = []
            for n in SIZES:
                item[n] = {"gp": mean(flat, n, "gp", "spearman"),
                           "prior_fitted": mean(flat, n, "gp_with_prior_fitted", "spearman"),
                           "prior_one": mean(flat, n, "gp_with_prior_one", "spearman"),
                           "gp_r2": mean(flat, n, "gp", "r2"),
                           "prior_fitted_r2": mean(flat, n, "gp_with_prior_fitted", "r2"),
                           "prior_one_r2": mean(flat, n, "gp_with_prior_one", "r2")}
                cells.append(f"{item[n]['gp']:.2f} → {item[n]['prior_fitted']:.2f} / {item[n]['prior_one']:.2f}")
            summary[task_name][label] = item
            lines.append(f"| `{task_name}` | {label} | {n_total} ({n_valid}) | {item['alone_spearman']:.2f} | " + " | ".join(cells) + " |")

        entry("handbook (no LLM)", [handbook], 1, 1)
        for model in ("fable", "opus", "sonnet", "haiku"):
            rows = models.get(model, [])
            valid = [r["per_seed"] for r in rows if not r["invalid"]]
            if rows:
                entry(model, valid, len(valid), len(rows))
    (out / "summary.json").write_text(json.dumps(summary, indent=1) + "\n")
    (out / "summary.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
