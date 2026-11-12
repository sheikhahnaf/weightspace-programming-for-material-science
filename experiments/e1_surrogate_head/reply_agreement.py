"""Do replies of one model agree more with each other than with other models' replies?

For each experimental alloy task: the Spearman correlation between the predictions of every
pair of valid written networks on all candidates, averaged within a model and across models.

    python experiments/e1_surrogate_head/reply_agreement.py   # -> results/standalone/agreement.json
"""

from __future__ import annotations

import itertools
import json
import re
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parent
RUN = re.compile(r"write__(?P<task>.+?)(?:__(?P<model>opus|fable|sonnet|haiku))?(?:__rep\d+)?$")


def main() -> None:
    from wsp.arms import written_head
    from wsp.baselines import predict, prepare
    from wsp.tasks import load_task

    by_task: dict[str, list[tuple[str, np.ndarray]]] = {}
    for folder in sorted((HERE / "runs").glob("write__*")):
        match, reply = RUN.fullmatch(folder.name), folder / "reply.txt"
        if not match or not reply.exists():
            continue
        task = load_task(match["task"])
        data = prepare(task, 0)
        U = np.vstack([data.U_train, data.U_test])
        try:
            by_task.setdefault(task.name, []).append((match["model"] or "fable", predict(written_head(task, reply.read_text()), U)))
        except Exception:
            continue  # an invalid reply
    out = {}
    for name, replies in by_task.items():
        within, across = [], []
        for (ma, a), (mb, b) in itertools.combinations(replies, 2):
            (within if ma == mb else across).append(float(spearmanr(a, b).statistic))
        out[name] = {"replies": len(replies), "within_model": float(np.mean(within)), "across_models": float(np.mean(across))}
        print(name, out[name])
    (HERE / "results" / "standalone" / "agreement.json").write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
