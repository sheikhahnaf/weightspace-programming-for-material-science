"""Schematic of the written network (d -> 16 -> 1, ReLU) for the Ti alloy Young's modulus task.

Input names come from src/wsp/tasks.py, the layer sizes and tensor names from src/wsp/heads.py
(MLPHead, describe) and src/wsp/arms.py (WRITE_HIDDEN), and the highlighted units and edges from
experiments/e1_surrogate_head/runs/write__ti_alloy_youngs_modulus__opus__rep1/reply.txt.

    PYTHONDONTWRITEBYTECODE=1 python plots/make_architecture.py
"""
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(HERE))
from wsp.arms import WRITE_HIDDEN, written_head  # noqa: E402
from wsp.tasks import load_task  # noqa: E402

plt.rcParams.update({"font.family": "Helvetica", "font.size": 10})
task = load_task("ti_alloy_youngs_modulus")
names = list(task.feature_names)
d, H = len(names), WRITE_HIDDEN[0]
run = ROOT / "experiments/e1_surrogate_head/runs/write__ti_alloy_youngs_modulus__opus__rep1"
head = written_head(task, (run / "reply.txt").read_text())
sd = {k: v.numpy() for k, v in head.state_dict().items()}
W1, b1, w2, b2 = sd["net.0.weight"], sd["net.0.bias"], sd["net.2.weight"][0], sd["net.2.bias"]
shapes = {k: tuple(v.shape) for k, v in sd.items()}
total = sum(v.size for v in sd.values())
assert shapes == {"net.0.weight": (H, d), "net.0.bias": (H,), "net.2.weight": (1, H), "net.2.bias": (1,)}
print("shapes", shapes, "total", total)
used = [i for i in range(H) if np.any(W1[i] != 0) or b1[i] != 0]

NAVY, MAROON, TEAL, AMBER, GREY = "#1F3A5F", "#500000", "#2A8C8C", "#C47F17", "#8A8F98"
fig, ax = plt.subplots(figsize=(10.2, 4.75))
ax.set_xlim(0, 10.2)
ax.set_ylim(-0.75, 4.55)
ax.axis("off")
xi, xh, xo = 1.75, 4.35, 6.35
yi = np.linspace(4.0, 0.0, d)
yh = np.linspace(4.0, 0.0, H)
yo = 2.0
for j in range(d):
    for i in range(H):
        on = W1[i, j] != 0
        col = (MAROON if i == 0 else TEAL) if on else "#D0D0D0"
        ax.plot([xi + 0.08, xh - 0.08], [yi[j], yh[i]], color=col, lw=0.55 if on else 0.3, alpha=0.75 if on else 0.6, zorder=1)
for i in range(H):
    on = w2[i] != 0
    ax.plot([xh + 0.08, xo - 0.12], [yh[i], yo], color=(MAROON if i == 0 else TEAL) if on else "#D0D0D0",
            lw=1.3 if on else 0.4, zorder=1)
for j, n in enumerate(names):
    ax.scatter(xi, yi[j], s=70, color="white", edgecolor=NAVY, lw=1.2, zorder=3)
    ax.text(xi - 0.16, yi[j], f"x[{j}] = {n}", ha="right", va="center", fontsize=9)
for i in range(H):
    c = (MAROON if i == 0 else TEAL) if i in used else GREY
    ax.scatter(xh, yh[i], s=70, color=c if i in used else "white", edgecolor=c, lw=1.2, zorder=3)
ax.scatter(xo, yo, s=190, color="white", edgecolor=AMBER, lw=1.8, zorder=3)
ax.text(xo + 0.2, yo - 0.05, "y = Young's modulus (GPa)", ha="left", va="center", fontsize=10.5, fontweight="bold")
ax.text(xo + 0.2, yo - 0.32, "one linear output, no activation", ha="left", va="center", fontsize=9, color="#444")

ax.text(xi, 4.36, f"Input: {d} atomic fractions", ha="center", fontsize=10.5, fontweight="bold", color=NAVY)
ax.text(xh, 4.36, f"Hidden: {H} ReLU units", ha="center", fontsize=10.5, fontweight="bold", color="#333")
ax.text(xo + 0.1, 4.36, "Output: 1", ha="left", fontsize=10.5, fontweight="bold", color=AMBER)

# what the reply of Opus 5.5 put where (the model's self-report)
ax.text(xh + 0.3, (yh[5] + yh[15]) / 2 - 0.55, "units 5 to 15:\nleft at zero", fontsize=9, color="#666", va="center",
        bbox=dict(facecolor="white", edgecolor="none", pad=1.5))
lx = 6.75
ax.text(lx, 4.02, "Reply 1 of Opus 5.5 (the model's own account)", fontsize=9.5, fontweight="bold", color="#333", va="center")
ax.scatter(lx + 0.07, 3.68, s=60, color=MAROON, zorder=3)
ax.text(lx + 0.25, 3.68, "unit 0: rule of mixtures, pure Ti at\n106 GPa, a slope per element", fontsize=9, color=MAROON, va="center")
ax.scatter(lx + 0.07, 3.16, s=60, color=TEAL, zorder=3)
ax.text(lx + 0.25, 3.16, "units 1 to 4: hinges on one molybdenum-\nequivalent index of beta stability,\nat 0, 5, 12 and 16", fontsize=9, color=TEAL, va="center")
ax.plot([lx, lx + 0.16], [2.72, 2.72], color="#C8C8C8", lw=1)
ax.text(lx + 0.25, 2.72, "grey: weight left at zero", fontsize=9, color="#666", va="center")

# tensor names as the prompt gives them
ty = -0.42
for x, name, shp, n in ((0.5 * (xi + xh), "net.0.weight", f"{H} × {d}", W1.size), (xh, "net.0.bias", f"{H}", b1.size),
                        (0.5 * (xh + xo) + 0.25, "net.2.weight", f"1 × {H}", w2.size), (xo + 0.9, "net.2.bias", "1", b2.size)):
    ax.text(x, ty, f"{name}\n{shp} = {n}" if "×" in shp else f"{name}\n{shp}", ha="center", va="center", fontsize=9.5, family="Helvetica",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="#F6F2EC", edgecolor="#999", lw=0.7))
ax.text(8.55, ty, f"total {total} weights", ha="center", va="center", fontsize=10.5, fontweight="bold")
fig.savefig(HERE.parent / "figures" / "network_architecture.png", dpi=300, bbox_inches="tight", facecolor="white")
print("wrote network_architecture.png; units used", used)
