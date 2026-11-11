"""Score every leak-repair reply and tabulate by model id (read from each run's meta.json).

    python scripts/harvest_run_usage.py && python experiments/e1_surrogate_head/score_repair_all.py
"""
import json
import warnings
from collections import defaultdict
from pathlib import Path

from wsp.arms import score_repair
from wsp.tasks import load_task

HERE = Path(__file__).resolve().parent
warnings.filterwarnings("ignore")
rows = []
for folder in sorted((HERE / "runs").glob("repair__*")):
    reply = folder / "reply.txt"
    if not reply.exists():
        continue
    meta = json.loads((folder / "meta.json").read_text())
    out = folder / "score.json"
    if out.exists() and out.stat().st_mtime >= reply.stat().st_mtime and "linear_gain_found_the_leak" in out.read_text():
        result = json.loads(out.read_text())
    else:
        try:
            result = score_repair(load_task(meta["task"]), meta["seed"], reply.read_text(), meta["shuffled"])
        except Exception as error:
            result = {"arm": "repair", "task": meta["task"], "seed": meta["seed"], "shuffled_control": meta["shuffled"],
                      "invalid": f"{type(error).__name__}: {str(error)[:160]}"}
    result["meta"] = meta
    out.write_text(json.dumps(result, indent=2) + "\n")
    rows.append({"run": folder.name, "model": str(meta.get("model")), **{k: result.get(k) for k in (
        "task", "seed", "shuffled_control", "invalid", "leak_position", "inputs_silenced_by_llm", "llm_found_the_leak",
        "column_norm_found_the_leak", "linear_gain_found_the_leak")},
        "r2": {k: result[k]["r2"] for k in ("unrepaired", "llm_repair", "linear_gain_repair", "true_column_zeroed") if k in result}})

real = [r for r in rows if not r["shuffled_control"]]
by_model = defaultdict(list)
for r in real:
    by_model[r["model"]].append(r)
lines = ["| Model | Runs | Invalid | Leak found | on bulk modulus | on heat capacity | Repairs that lowered test R² | Mean R²: unrepaired → model's edit → ideal |",
         "|---|---|---|---|---|---|---|---|"]
for model, rs in sorted(by_model.items()):
    ok = [r for r in rs if not r["invalid"]]
    found = lambda task: f"{sum(bool(r['llm_found_the_leak']) for r in ok if r['task'] == task)} / {sum(r['task'] == task for r in rs)}"
    worse = sum(r["r2"]["llm_repair"] < r["r2"]["unrepaired"] - 0.02 for r in ok)
    mean = lambda k: sum(r["r2"][k] for r in ok) / max(len(ok), 1)
    lines.append(f"| {model} | {len(rs)} | {len(rs) - len(ok)} | {sum(bool(r['llm_found_the_leak']) for r in ok)} / {len(rs)} "
                 f"| {found('loop_bulk_modulus')} | {found('loop_heat_capacity')} | {worse} "
                 f"| {mean('unrepaired'):.2f} → {mean('llm_repair'):.2f} → {mean('true_column_zeroed'):.2f} |")
nets = {(r["task"], r["seed"]): r for r in real if not r["invalid"]}
lines += ["", f"Weights-only statistics over the {len(nets)} networks: column norm {sum(bool(r['column_norm_found_the_leak']) for r in nets.values())}, "
          f"linear gain {sum(bool(r['linear_gain_found_the_leak']) for r in nets.values())}."]
out = HERE / "results" / "repair_arm"
out.mkdir(parents=True, exist_ok=True)
(out / "per_run.json").write_text(json.dumps(rows, indent=1) + "\n")
(out / "summary.md").write_text("\n".join(lines) + "\n")
print("\n".join(lines))
for r in real:
    print(f"  {r['run']:52s} leak {r['leak_position']} -> {r['inputs_silenced_by_llm']} {'INVALID ' + r['invalid'] if r['invalid'] else ''}")
