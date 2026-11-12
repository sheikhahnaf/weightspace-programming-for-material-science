"""E8: a written per-element correction to a potential's formation enthalpy.

A potential's formation enthalpy is H = E(compound) - sum_i x_i E(element i), all from
the potential. Shifting the potential's per-element reference energies cannot change H:
the shift enters the compound and the elemental phase alike and cancels. What can be
written is a correction layer on the composition,

    H_corrected = H + sum_i x_i c_i + b,

one weight per element. The model writes c and b from knowledge, with no data. The
same layer fitted by least squares on n experimental enthalpies is the reference, and
the written layer is also used as the centre of that fit (ridge toward the written
weights instead of toward zero).

    python experiments/e8_formation_enthalpy/correction_arm.py prompt
    python experiments/e8_formation_enthalpy/correction_arm.py score

Run folders: runs/correct__<potential>__<model>__rep<k>/ (prompt.txt, reply.txt, self_report.txt).
"""

from __future__ import annotations

import json
import re
import sys
import warnings
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DATA = ROOT / "data" / "formation"
RUNS = HERE / "runs"
OUT = HERE / "results"
POTENTIALS = {"mace": "MACE-MPA-0 (medium), trained on Materials Project relaxation trajectories and sAlex: PBE, with PBE+U for the oxides and fluorides of V, Cr, Mn, Fe, Co, Ni, Mo and W",
              "orb": "ORB-v3 (orb_v3_conservative_inf_omat), trained on OMat24: PBE, with PBE+U for the oxides and fluorides of V, Cr, Mn, Fe, Co, Ni, Mo and W"}
RUN = re.compile(r"correct__(mace|orb)__(fable|opus|sonnet|haiku)__rep(\d+)")
SIZES = (10, 20, 50, 100, 200, 400)
DRAWS = 20
RIDGE = 1e-2  # in (eV/atom)^2 units of the fraction-weighted design; see fit()


def load(potential: str):
    """Elements, composition matrix, potential formation enthalpy, experimental enthalpy, names."""
    from ase.io import read

    energies = json.loads((DATA / f"energies_{potential}.json").read_text())
    frames = read(DATA / "compounds.extxyz", index=":")
    # extxyz reads the info value "F" back as the boolean False; restore the symbol
    energies["elements"] = {("F" if k == "False" else k): v for k, v in energies["elements"].items()}
    elements = sorted(energies["elements"])
    X, h, y, names = [], [], [], []
    for atoms in frames:
        symbols = atoms.get_chemical_symbols()
        x = np.array([symbols.count(e) / len(symbols) for e in elements])
        name = str(atoms.info["name"])
        X.append(x)
        h.append(energies["compounds"][name] - x @ np.array([energies["elements"][e] for e in elements]))
        y.append(float(atoms.info["H_expt"]))
        names.append(name)
    return elements, np.array(X), np.array(h), np.array(y), names


def split(n: int):
    order = np.random.default_rng(0).permutation(n)
    return order[: n // 2], order[n // 2:]


def prompt(potential: str) -> str:
    from wsp.heads import MLPHead, zero_
    from wsp.prompts import build_prompt

    elements, X, _, _, _ = load(potential)
    head = zero_(MLPHead(len(elements), (), 1))
    counts = (X > 0).sum(0)
    inputs = "\n".join(f"x[{i}] = atomic fraction of {e}" for i, e in enumerate(elements))
    job = (
        f"Write the weights of this one-layer network from what you know. No data is given.\n\n"
        f"A machine-learned interatomic potential ({POTENTIALS[potential]}) is used to compute the formation "
        f"enthalpy of inorganic compounds: the potential's energy per atom of the compound minus the "
        f"composition-weighted potential energies per atom of the elements, each element in the lowest-energy "
        f"phase the Materials Project lists for it (for H, N, O, F and Cl that is a cell of molecules). The "
        f"result differs from the experimental formation enthalpy at 298 K in a way that depends on which "
        f"elements the compound contains.\n\n"
        f"The network's output y is added to the potential's formation enthalpy, in eV per atom of compound: "
        f"y = sum over elements of (atomic fraction x weight) + bias. Choose the weights so that the corrected "
        f"value is as close as possible to experiment over binary and ternary compounds of these elements "
        f"(oxides, halides, chalcogenides, nitrides, hydrides, intermetallics and others). A weight of zero "
        f"leaves an element uncorrected.\n\nInputs (they sum to 1):\n{inputs}\n\n"
        f"Elements by how many of the {len(X)} compounds contain them: "
        + ", ".join(f"{e} {c}" for c, e in sorted(zip(counts, elements), reverse=True)) + "."
    )
    return build_prompt("write", job, head.describe(), head.state_dict())


def written(reply: str, d: int):
    from wsp.heads import MLPHead
    from wsp.serialize import load_weights

    head = MLPHead(d, (), 1)
    head.load_state_dict(load_weights(reply))
    return head.net[0].weight.detach().numpy().astype(float).ravel(), float(head.net[0].bias.detach())


def fit(X, r, rows, centre=None, lam=RIDGE):
    """Least squares for [c, b] on the rows, shrunk toward `centre` (zeros when None)."""
    A = np.column_stack([X[rows], np.ones(len(rows))])
    c0 = np.zeros(A.shape[1]) if centre is None else centre
    theta = np.linalg.solve(A.T @ A + lam * np.eye(A.shape[1]), A.T @ (r[rows] - A @ c0))
    return c0 + theta


def mae(a):
    return float(np.mean(np.abs(a)))


def score() -> None:
    warnings.filterwarnings("ignore")
    result, lines = {}, []
    for potential in POTENTIALS:
        if not (DATA / f"energies_{potential}.json").exists():
            continue
        elements, X, h, y, _ = load(potential)
        A = np.column_stack([X, np.ones(len(X))])
        r = y - h  # what the correction should equal
        train, test = split(len(y))
        replies = {}
        for folder in sorted(RUNS.glob(f"correct__{potential}__*")):
            m = RUN.fullmatch(folder.name)
            if m and (folder / "reply.txt").exists():
                try:
                    c, b = written((folder / "reply.txt").read_text(), len(elements))
                    replies[f"{m[2]}__rep{m[3]}"] = np.append(c, b)
                except Exception as error:
                    result.setdefault("rejected", {})[folder.name] = f"{type(error).__name__}: {str(error)[:80]}"
        zero = {"potential as shipped": {"mae": mae(r[test]), "bias": float(-np.mean(r[test]))}}
        for name, theta in replies.items():
            e = r[test] - A[test] @ theta
            shuffled = [mae(r[test] - A[test] @ np.append(np.random.default_rng(k).permutation(theta[:-1]), theta[-1])) for k in range(20)]
            zero[f"written: {name}"] = {"mae": mae(e), "bias": float(-np.mean(e)), "mae_weights_shuffled_over_elements": float(np.mean(shuffled)),
                                        "nonzero_weights": int(np.sum(theta[:-1] != 0))}
        few: dict[str, dict] = {}
        models = sorted({k.split("__")[0] for k in replies})
        for n in SIZES:
            cols: dict[str, list] = {}
            for draw in range(DRAWS):
                rows = train[np.random.default_rng(1000 * n + draw).permutation(len(train))[:n]]
                cols.setdefault("fitted, shrunk toward zero", []).append(mae(r[test] - A[test] @ fit(X, r, rows)))
                cols.setdefault("offset only", []).append(mae(r[test] - np.mean(r[rows])))
                for model in models:
                    both = [mae(r[test] - A[test] @ fit(X, r, rows, theta)) for k, theta in replies.items() if k.startswith(model)]
                    cols.setdefault(f"fitted, shrunk toward the written weights: {model}", []).append(float(np.mean(both)))
            few[str(n)] = {k: float(np.mean(v)) for k, v in cols.items()}
        result[potential] = {"compounds": len(y), "elements": len(elements), "test": len(test), "no_labels": zero, "with_labels": few}
        lines += [f"**{potential}: {len(test)} held-out compounds, {len(elements)} elements**", "",
                  "| No experimental labels | MAE, eV/atom | Bias, eV/atom | MAE with the weights shuffled over elements |", "|---|---|---|---|"]
        for name, v in zero.items():
            lines.append(f"| {name} | {v['mae']:.3f} | {v['bias']:+.3f} | {v.get('mae_weights_shuffled_over_elements', float('nan')):.3f} |".replace("nan", ""))
        arms = list(next(iter(few.values())))
        lines += ["", "| With n labels: MAE, eV/atom | " + " | ".join(f"n = {n}" for n in SIZES) + " |", "|---|" + "---|" * len(SIZES)]
        for arm in arms:
            lines.append(f"| {arm} | " + " | ".join(f"{few[str(n)][arm]:.3f}" for n in SIZES) + " |")
        lines.append("")
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "correction.json").write_text(json.dumps(result, indent=2) + "\n")
    (OUT / "correction.md").write_text("\n".join(lines) + f"\nLabels are drawn from the training half, {DRAWS} draws; ridge strength {RIDGE}.\n")
    print("\n".join(lines))


def main() -> None:
    if sys.argv[1] == "prompt":
        for potential in POTENTIALS:
            if not (DATA / f"energies_{potential}.json").exists():
                continue
            text = prompt(potential)
            for model, reps in (("opus", 3), ("fable", 3), ("sonnet", 2), ("haiku", 2)):
                for k in range(1, reps + 1):
                    folder = RUNS / f"correct__{potential}__{model}__rep{k}"
                    folder.mkdir(parents=True, exist_ok=True)
                    if not (folder / "reply.txt").exists():
                        (folder / "prompt.txt").write_text(text)
                    if not (folder / "reply.txt").exists():
                        print(folder.name)
    else:
        score()


if __name__ == "__main__":
    main()
