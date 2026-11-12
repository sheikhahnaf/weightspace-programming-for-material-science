"""The same standalone metrics for every written network on every task. No labels are used.

    python experiments/e1_surrogate_head/standalone_metrics.py

For each task, every valid reply (alloy tasks: this folder's runs; Thermo-Calc tasks:
experiments/e7_calphad_prior/runs; crystal tasks: the filter networks of E3) and every
no-LLM rule is evaluated on all rows of the task. For the crystal tasks the rows are the
crystals added during the loops, each counted once: every run starts from the same set of
Materials Project crystals with DFT labels, and scoring "all rows" would count that set
once per run (robustness.py crystals gives every split):

  rho          Spearman rank correlation with the target
  recall       share of the best tenth of the rows found in the predictor's best tenth
  error_raw    RMSE of the prediction as written, in units of the target's standard deviation
  error_fit    the same after the best straight-line rescaling, sqrt(1 - r^2)

Writes results/standalone/summary.md and per_reply.json. Means are over a model's replies.
"""

from __future__ import annotations

import json
import re
import sys
import warnings
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import pearsonr, spearmanr

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
E3 = ROOT / "experiments" / "e3_crystal_filter"
E7 = ROOT / "experiments" / "e7_calphad_prior"
OUT = HERE / "results" / "standalone"
# The first Fable replies of two tasks were stored without a replicate suffix; they count as replies too.
RUN = re.compile(r"(?P<arm>write|writepd)__(?P<task>.+?)(?:__(?P<model>opus|fable|sonnet|haiku))?(?:__rep(?P<rep>\d+))?$")
ORDER = ("rule", "rom", "subsystem_extrapolation", "handbook", "opus", "opus + facts", "fable", "fable + facts", "sonnet", "haiku")


def metrics(y: np.ndarray, m: np.ndarray, goal: float = 1.0) -> dict:
    ok = np.isfinite(m)
    if ok.sum() < 3 or np.std(m[ok]) == 0:
        return {"rho": float("nan"), "recall": float("nan"), "error_raw": float("nan"), "error_fit": 1.0}
    y, m = y[ok], m[ok]
    k = max(1, int(round(0.1 * len(y))))
    recall = len(set(np.argsort(-goal * y)[:k]) & set(np.argsort(-goal * m)[:k])) / k
    r = pearsonr(m, y).statistic
    return {"rho": float(spearmanr(m, y).statistic), "recall": float(recall),
            "error_raw": float(np.sqrt(np.mean((m - y) ** 2)) / y.std()), "error_fit": float(np.sqrt(max(0.0, 1 - r**2)))}


def composition_tasks() -> dict:
    from wsp.arms import reference_priors, written_head
    from wsp.baselines import predict, prepare
    from wsp.tasks import CALPHAD_GOALS, TASK_NAMES, load_task

    rows = defaultdict(dict)
    skipped: set[str] = set()
    for runs in (HERE / "runs", E7 / "runs"):
        for folder in sorted(runs.glob("write*__*")):
            match, reply = RUN.fullmatch(folder.name), folder / "reply.txt"
            if not match or not reply.exists():
                continue
            name = match["task"]
            if name not in TASK_NAMES:  # e.g. Thermo-Calc targets when data/calphad/ is absent
                skipped.add(name)
                continue
            task = load_task(name)
            data = prepare(task, 0)
            U, y = np.vstack([data.U_train, data.U_test]), np.concatenate([data.y_train, data.y_test])
            goal = CALPHAD_GOALS.get(name, 1.0)
            if not rows[name]:
                try:
                    for rule, m in reference_priors(task).items():
                        rows[name][rule] = [metrics(y, np.asarray(m(U), float), goal)]
                except Exception:
                    pass
            source = (match["model"] or "fable") + (" + facts" if match["arm"] == "writepd" else "")
            try:
                value = metrics(y, predict(written_head(task, reply.read_text()), U), goal)
            except Exception:
                continue  # an invalid reply was rejected when it was first scored
            rows[name].setdefault(source, []).append(value | {"run": folder.name})
    if skipped:
        print(f"skipped {len(skipped)} tasks whose data is not in this copy (Thermo-Calc pools): rerun after make_tc_data.py")
    return rows


def crystal_tasks() -> dict:
    sys.path.insert(0, str(E3))
    import filter_arm

    from wsp import tasks
    from wsp.tasks import load_task

    rows = defaultdict(dict)
    for name, key in {"loop_bulk_modulus": "K", "loop_heat_capacity": "Cp"}.items():
        table, _ = tasks._closed_loop_table(*tasks._CLOSED_LOOPS[name])
        added = (~table["structure_id"].duplicated() & (table["oracle_source"] != "warm_start")).to_numpy()
        D = np.load(HERE / "results" / "structure_prior" / f"descriptors__{name}.npy")[added]
        y = load_task(name).y[added]
        rows[name]["rule"] = [metrics(y, 1.0 / D[:, 0] if key == "K" else 3 * 8.314462618 / D[:, 1])]
        for folder in sorted((E3 / "runs").glob(f"filter_{key}__*")):
            reply = folder / "reply.txt"
            if reply.exists():
                try:
                    value = metrics(y, filter_arm.scorer(reply.read_text())(D))
                except Exception:
                    continue
                rows[name].setdefault(folder.name.replace(f"filter_{key}__", "").split("__")[0], []).append(value | {"run": folder.name})
    return rows


def main() -> None:
    warnings.filterwarnings("ignore")
    rows = composition_tasks() | crystal_tasks()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "per_reply.json").write_text(json.dumps(rows, indent=1) + "\n")
    lines = ["| Task | Source | Replies | ρ | Best tenth found | Error as written (σ) | Error after rescaling (σ) |", "|---|---|---|---|---|---|---|"]
    summary = {}
    for name in sorted(rows):
        for source in sorted(rows[name], key=lambda s: ORDER.index(s) if s in ORDER else 99):
            values = rows[name][source]
            mean = {k: float(np.nanmean([v[k] for v in values])) for k in ("rho", "recall", "error_raw", "error_fit")}
            summary[f"{name}|{source}"] = mean | {"replies": len(values)}
            lines.append(f"| `{name}` | {source} | {len(values)} | {mean['rho']:.2f} | {mean['recall']:.2f} | {mean['error_raw']:.3g} | {mean['error_fit']:.2f} |")
    (OUT / "summary.json").write_text(json.dumps(summary, indent=1) + "\n")
    (OUT / "summary.md").write_text("\n".join(lines) + "\n\nAll rows of each task (crystal tasks: the crystals added during the loops, each once); no labels used. A rule that is constant on a task has no ρ.\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
