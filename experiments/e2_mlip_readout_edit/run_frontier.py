"""E2: the trade-off a gradient fit of the readout can reach between bulk-modulus
error and change of energy, on the same split the LLM arm uses (seed 0).

Each point is `fit_readout` with a different weight on the energy-change penalty.
An LLM edit is worth something only if it sits on or below this curve.

    python experiments/e2_mlip_readout_edit/run_frontier.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import llm_arm  # noqa: E402
from run_baselines import fit_readout, report  # noqa: E402

PENALTIES = (0.0, 0.0003, 0.001, 0.003, 0.01, 0.03, 0.1, 0.3, 1.0)


def main() -> None:
    base, train, ktr, test, kte = llm_arm.setup()
    rows = [{"penalty": None, "arm": "unedited", **report(base, base, test, kte)}]
    for penalty in PENALTIES:
        params = fit_readout(base, train, ktr, llm_arm.SEED, keep_energy=penalty)
        row = {"penalty": penalty, "arm": "gradient", **report(params, base, test, kte)}
        rows.append(row)
        print(f"penalty {penalty:<7} MAE {row['mae_GPa']:.2f}  bias {row['bias_GPa']:+.2f}  "
              f"energy change {row['energy_change_meV_per_atom']:.2f} meV/atom", flush=True)
    for version in (1, 2):
        params = llm_arm.table_solve(base, train, ktr, version)
        rows.append({"penalty": None, "arm": f"table_solve_v{version}", **report(params, base, test, kte)})
    (HERE / "results" / "frontier_seed0.json").write_text(json.dumps(rows, indent=2) + "\n")


if __name__ == "__main__":
    main()
