"""Print the facts used on the slides, read from the project's result files (read-only)."""
import json, re, sys
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
E1 = ROOT / "experiments/e1_surrogate_head"
from wsp.tasks import load_task
GOALS = {"ti_alloy_youngs_modulus": -1, "ti_alloy_yield_strength": 1, "ti_alloy_hardness": 1, "mpea_yield_strength": 1, "mpea_hardness": 1}
print("== tasks")
for t, g in GOALS.items():
    k = load_task(t); d = k.X.shape[1]
    tr, te = k.split(0)
    print(t, "n", len(k.y), "d", d, "weights", d*16+16+16+1, "train/test", len(tr), len(te), "unit", k.unit,
          "min %.4g max %.4g median %.4g" % (k.y.min(), k.y.max(), np.median(k.y)), "best", (k.y.max() if g > 0 else k.y.min()))
    print("   ", k.feature_names)
print("== audit, write runs")
aud = json.load(open(ROOT / "experiments/runs_audit.json"))
print("total runs", len(aud), "audit_ok", sum(a["audit_ok"] for a in aud), "keys", list(aud[0].keys()))
w = [a for a in aud if a["experiment"] == "e1_surrogate_head" and a["run"].startswith("write__")]
print("write runs", len(w))
by = {}
for a in w:
    by.setdefault(a["model_id"], []).append(a)
for m, L in by.items():
    ot = np.array([a["output_tokens"] for a in L]); du = np.array([a["duration_ms"] for a in L]) / 1000
    ct = np.array([a["context_tokens_last_turn"] for a in L])
    print(m, "n", len(L), "out tokens median %.0f min %.0f max %.0f" % (np.median(ot), ot.min(), ot.max()),
          "seconds median %.0f min %.0f max %.0f" % (np.median(du), du.min(), du.max()), "context median %.0f" % np.median(ct),
          "tool calls", sorted(set(a["tool_calls"] for a in L)), "attempts", sorted(set(a["attempts"] for a in L)), "ok", sum(a["audit_ok"] for a in L))
print("== per_run")
pr = json.load(open(E1 / "results/write_arm/per_run.json"))
print(len(pr), "keys", list(pr[0].keys()))
for r in pr:
    if r["invalid"]:
        print("INVALID", r["run"], r["invalid"])
from collections import Counter
print(Counter((r["model"]) for r in pr))
print("== summary.json")
s = json.load(open(E1 / "results/write_arm/summary.json"))
for t in s:
    for src, v in s[t].items():
        print(t, src, v["replies"], v["valid"], "alone %.3f" % v["alone_spearman"], ["%.2f" % x for x in v["alone_spearman_per_reply"]], [k for k in v if k.startswith("n")])
print(json.dumps(s["ti_alloy_hardness"]["opus"], indent=0)[:1500])
print("== bo summary")
b = json.load(open(E1 / "results/bo_select/summary_init5_steps25_seeds20.json"))
print({k: v for k, v in b.items() if k != "tasks"})
t0 = json.load(open(E1 / "results/bo_select/init5_steps25/mpea_yield_strength/select_opus__seed0.json"))
print(t0)
import os
print(sorted(os.listdir(E1 / "results/bo_select/init5_steps25/mpea_yield_strength"))[:12], len(os.listdir(E1 / "results/bo_select/init5_steps25/mpea_yield_strength")))
