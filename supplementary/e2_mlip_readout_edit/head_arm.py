"""E2, all four potentials: edit the last layer of the energy readout, with feedback.

    python head_arm.py baselines --potential orb         # unedited, gradient curve, budgeted optimisers
    python head_arm.py next --potential orb --model opus --chain 1   # writes the next round's prompt
    python head_arm.py score                              # scores every chain, writes results/head/

The single-shot arm (llm_arm.py for MACE, orb_arm.py for ORB) gave the model one try
and no measurement. Here a chain is ROUNDS tries. After each try the harness applies
the edit, evaluates it on the training half (200 crystals, one evaluation of the
potential's energy-volume curves) and puts the result into the next prompt. Round 1
is the single-shot arm again.

The reported edit of a chain is the round with the lowest training error among those
that keep the training energy change within the limit; it is then scored on the test
half. The reference optimisers get the same number of evaluations and the same rule:

  linesearch   the direction the table alone suggests, tried at ROUNDS step sizes
  spsa         simultaneous-perturbation stochastic approximation, also run with 10x
               and 100x the evaluations to show what a black-box optimiser needs
  gradient     Adam with exact gradients and an energy penalty (no budget; the ceiling)
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import numpy as np
import torch
from scipy.stats import spearmanr

from wsp import estimate_tokens
from wsp.edit import apply_edits, parse_edits
from wsp.linear_head import FULL_NAME, POTENTIALS, TOTAL_WEIGHTS, energies, load, predict_moduli
from wsp.mace_readout import bulk_modulus

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results" / "head"
RUNS = HERE / "runs"
SEED = 0
ROUNDS = 5
LIMIT = 5.0  # meV per atom
STEP = {"mace": 0.02, "orb": 0.002, "esen": 0.002, "grace": 0.02}
PENALTIES = (0.0, 0.001, 0.003, 0.01, 0.03, 0.1, 0.3, 1.0)
CHAIN = re.compile(r"head_(mace|orb|esen|grace)__(fable|opus|sonnet|haiku)__c(\d+)__r(\d+)")
_cache: dict = {}


def setup(potential: str):
    if potential not in _cache:
        base, structures = load(potential)
        k0 = predict_moduli(base, structures).numpy()
        structures = [s for s, k in zip(structures, k0) if np.isfinite(k)]
        k_ref = np.array([s.K_ref for s in structures])
        order = np.random.default_rng(SEED).permutation(len(structures))
        half = len(order) // 2
        _cache[potential] = (base, [structures[i] for i in order[:half]], k_ref[order[:half]],
                             [structures[i] for i in order[half:]], k_ref[order[half:]])
    return _cache[potential]


def report(params, base, structures, k_ref) -> dict:
    k = predict_moduli(params, structures).detach().numpy()
    ok = np.isfinite(k)
    error = k[ok] - k_ref[ok]
    de = [float((energies(params, s) - energies(base, s)).detach().abs().mean() / s.n_atoms * 1000) for s in structures]
    return {"n": int(ok.sum()), "failed_fits": int((~ok).sum()), "mae_GPa": float(np.abs(error).mean()),
            "bias_GPa": float(error.mean()), "spearman": float(spearmanr(k[ok], k_ref[ok]).statistic),
            "energy_change_meV_per_atom": float(np.mean(de))}


def bands(params, structures, k_ref) -> list[str]:
    k = predict_moduli(params, structures).detach().numpy()
    edges = np.quantile(k_ref, [0, 0.25, 0.5, 0.75, 1.0])
    out = []
    for i in range(4):
        rows = (k_ref >= edges[i]) & ((k_ref <= edges[i + 1]) if i == 3 else (k_ref < edges[i + 1])) & np.isfinite(k)
        out.append(f"DFT {edges[i]:.0f} to {edges[i + 1]:.0f} GPa: mean error {np.mean(k[rows] - k_ref[rows]):+.1f} GPa "
                   f"({100 * np.mean((k[rows] - k_ref[rows]) / k_ref[rows]):+.1f}%)")
    return out


def clone(base):
    return {k: v.clone() for k, v in base.items()}


def fit(base, train, k_ref, keep_energy=0.0, steps=400, penalty=1e-2):
    """Adam on w (and b) with exact gradients, early-stopped on a fifth of the training half."""
    order = np.random.default_rng(SEED).permutation(len(train))
    n_val = max(1, len(train) // 5)
    val, rows = order[:n_val], order[n_val:]
    names = ["w"] + (["b"] if any(float(s.c.abs().sum()) > 0 for s in train[:1]) else [])
    params = {k: v.clone().requires_grad_(k in names) for k, v in base.items()}
    lr = 0.02 * float(base["w"].abs().mean())
    optimizer = torch.optim.Adam([params[k] for k in names], lr=lr)
    target = torch.tensor(k_ref)

    def loss_on(idx):
        k = torch.stack([bulk_modulus(train[i].volumes, energies(params, train[i])) for i in idx])
        ok = torch.isfinite(k)
        loss = (((k[ok] - target[idx][ok]) / 100.0) ** 2).mean()
        if keep_energy:
            shift = torch.stack([((energies(params, train[i]) - train[i].model_energies) / train[i].n_atoms).pow(2).mean() for i in idx])
            loss = loss + keep_energy * (shift / 0.01**2).mean()
        return loss

    best, best_state, since = float("inf"), clone(base), 0
    for step in range(steps):
        optimizer.zero_grad()
        drift = ((params["w"] - base["w"]) ** 2).sum() / (base["w"] ** 2).sum()
        (loss_on(rows) + penalty * drift).backward()
        optimizer.step()
        if step % 10 == 0:
            with torch.no_grad():
                v = float(loss_on(val))
            if v < best - 1e-6:
                best, best_state, since = v, {k: p.detach().clone() for k, p in params.items()}, 0
            else:
                since += 1
                if since >= 6:
                    break
    return best_state


def table(potential: str):
    """Per weight j: change of the fitted bulk modulus per unit increase (finite difference,
    so it includes the shift of the equilibrium volume) and of the energy per atom (exact),
    mean and standard deviation over the training crystals. Cached."""
    cache = RESULTS / f"sensitivity_{potential}_seed{SEED}.json"
    if cache.exists():
        d = json.loads(cache.read_text())
        return tuple(np.array(d[k]) for k in ("dK_mean", "dK_sd", "dE_mean", "dE_sd"))
    base, train, _, _, _ = setup(potential)
    k0 = predict_moduli(base, train).numpy()
    dE = np.array([(s.h[3] / s.n_atoms).numpy() for s in train])
    mean, sd = [], []
    for j in range(base["w"].numel()):
        params = clone(base)
        params["w"][j] += STEP[potential]
        dk = (predict_moduli(params, train).numpy() - k0) / STEP[potential]
        mean.append(float(np.nanmean(dk)))
        sd.append(float(np.nanstd(dk)))
    RESULTS.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps({"step": STEP[potential], "dK_mean": mean, "dK_sd": sd,
                                 "dE_mean": dE.mean(0).tolist(), "dE_sd": dE.std(0).tolist()}) + "\n")
    return np.array(mean), np.array(sd), dE.mean(0), dE.std(0)


def has_bias(potential: str) -> bool:
    return potential != "grace"


def cancel_mean_energy(potential, params, base, train):
    """Set b so that the mean change of energy per atom over the training half is zero."""
    if not has_bias(potential):
        return params
    shift = np.mean([float(((s.h[3] @ (params["w"] - base["w"])) / s.n_atoms)) for s in train])
    per_unit = np.mean([float(s.c[3] / s.n_atoms) for s in train])
    params["b"] = base["b"] - shift / per_unit
    return params


def select(candidates, base, train, ktr):
    """The rule every budgeted method shares: lowest training error among edits that keep
    the training energy change within the limit; the unedited weights if none does."""
    best, best_mae = clone(base), report(base, base, train, ktr)["mae_GPa"]
    for params in candidates:
        r = report(params, base, train, ktr)
        if r["energy_change_meV_per_atom"] <= LIMIT and r["failed_fits"] == 0 and r["mae_GPa"] < best_mae:
            best, best_mae = params, r["mae_GPa"]
    return best


def linesearch(potential: str, budget: int = ROUNDS):
    """Direction from the table alone: bulk-modulus gain per unit of squared energy spread,
    signed to reduce the mean error. Step sizes are fixed in advance so that the energy
    spread the table predicts (treating the weights as independent) is 1 to 8 meV per atom."""
    base, train, ktr, _, _ = setup(potential)
    gK, _, _, sE = table(potential)
    bias = float(np.nanmean(predict_moduli(base, train).numpy() - ktr))
    d = -np.sign(bias) * gK / (sE**2 + 1e-12)
    spread = float(np.sqrt(((d * sE) ** 2).sum()))
    out = []
    for target in np.geomspace(1e-3, 8e-3, budget):
        params = clone(base)
        params["w"] = base["w"] + torch.tensor(d * target / spread)
        out.append(cancel_mean_energy(potential, params, base, train))
    return select(out, base, train, ktr)


def spsa(potential: str, budget: int, seed: int = 0):
    base, train, ktr, _, _ = setup(potential)
    rng = np.random.default_rng(seed)
    scale = float(base["w"].abs().mean())

    def objective(params):
        r = report(params, base, train, ktr)
        return r["mae_GPa"] + 10.0 * max(0.0, r["energy_change_meV_per_atom"] - LIMIT) + 100.0 * r["failed_fits"]

    w, tried = base["w"].clone(), []
    steps = max(1, budget // 3)  # two evaluations for the gradient estimate, one for the new point
    for t in range(steps):
        ck, ak = 0.02 * scale / (t + 1) ** 0.101, 0.0005 * scale**2 / (t + 1) ** 0.602
        delta = torch.tensor(rng.choice([-1.0, 1.0], size=w.numel()))
        plus, minus = clone(base), clone(base)
        plus["w"], minus["w"] = w + ck * delta, w - ck * delta
        g = (objective(cancel_mean_energy(potential, plus, base, train)) - objective(cancel_mean_energy(potential, minus, base, train))) / (2 * ck) * delta
        w = w - ak * g / scale**2 * scale
        params = clone(base)
        params["w"] = w.clone()
        tried.append(cancel_mean_energy(potential, params, base, train))
    return select(tried, base, train, ktr)


def evolution(potential: str, budget: int, seed: int = 0, k: int = 10):
    """A (1+1) evolution strategy restricted to the k weights the table ranks highest
    (bulk-modulus gain per unit of energy spread), started at the line-search direction's
    smallest step. A stronger budgeted reference than SPSA: it is told where to look."""
    base, train, ktr, _, _ = setup(potential)
    gK, _, _, sE = table(potential)
    bias = float(np.nanmean(predict_moduli(base, train).numpy() - ktr))
    top = np.argsort(-np.abs(gK) / (sE + 1e-12))[:k]
    unit = 1e-3 / sE[top]  # a step that moves the energy spread of one weight by 1 meV per atom
    rng = np.random.default_rng(seed)

    def build(z):
        params = clone(base)
        delta = np.zeros(len(gK))
        delta[top] = z * unit
        params["w"] = base["w"] + torch.tensor(delta)
        return cancel_mean_energy(potential, params, base, train)

    def objective(params):
        r = report(params, base, train, ktr)
        return r["mae_GPa"] + 10.0 * max(0.0, r["energy_change_meV_per_atom"] - LIMIT) + 100.0 * r["failed_fits"]

    z = -np.sign(bias) * np.sign(gK[top]) * 0.5
    tried = [build(z)]
    best, sigma = objective(tried[0]), 0.5
    for _ in range(budget - 1):
        cand = z + sigma * rng.standard_normal(k)
        params = build(cand)
        tried.append(params)
        value = objective(params)
        if value < best:
            z, best, sigma = cand, value, sigma * 1.3
        else:
            sigma *= 0.85
    return select(tried, base, train, ktr)


def baselines(potential: str) -> None:
    base, train, ktr, test, kte = setup(potential)
    rows = [{"arm": "unedited", **report(base, base, test, kte)}]
    for penalty in PENALTIES:
        rows.append({"arm": "gradient", "penalty": penalty, **report(fit(base, train, ktr, keep_energy=penalty), base, test, kte)})
    free = fit(base, train, ktr, keep_energy=0.0)
    for lam in (0.02, 0.05, 0.1, 0.2, 0.5):
        params = clone(base)
        params["w"] = base["w"] + lam * (free["w"] - base["w"])
        params["b"] = base["b"] + lam * (free["b"] - base["b"])
        rows.append({"arm": "scaled_unconstrained_fit", "lambda": lam, **report(params, base, test, kte)})
    rows.append({"arm": "linesearch", "evaluations": ROUNDS, **report(linesearch(potential), base, test, kte)})
    for budget in (ROUNDS, 10 * ROUNDS, 100 * ROUNDS):
        for seed in range(3):
            rows.append({"arm": "spsa", "evaluations": budget, "seed": seed, **report(spsa(potential, budget, seed), base, test, kte)})
    for budget in (ROUNDS, 10 * ROUNDS, 100 * ROUNDS):
        for seed in range(3):
            rows.append({"arm": "evolution_top10", "evaluations": budget, "seed": seed, **report(evolution(potential, budget, seed), base, test, kte)})
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / f"baselines_{potential}.json").write_text(json.dumps(rows, indent=2) + "\n")
    for r in rows:
        extra = " ".join(f"{k}={r[k]}" for k in ("penalty", "lambda", "evaluations", "seed") if k in r)
        print(f"{potential} {r['arm']:26} {extra:28} MAE {r['mae_GPa']:.2f} bias {r['bias_GPa']:+.2f} rho {r['spearman']:.3f} "
              f"dE {r['energy_change_meV_per_atom']:.2f} meV/atom", flush=True)


def apply_reply(base, text: str):
    shown = {"w": base["w"].clone(), "b": base["b"].reshape(1).clone()}
    edited = apply_edits(shown, parse_edits(text))
    return {"w": edited["w"].to(torch.float64), "b": edited["b"].reshape(()).to(torch.float64)}


def chain_folder(potential, model, chain, rnd) -> Path:
    return RUNS / f"head_{potential}__{model}__c{chain}__r{rnd}"


def history(potential, model, chain, upto: int) -> list[dict]:
    """Training-half feedback for rounds 1..upto of a chain (computed and stored once)."""
    base, train, ktr, _, _ = setup(potential)
    out = []
    for r in range(1, upto + 1):
        folder = chain_folder(potential, model, chain, r)
        fb = folder / "feedback.json"
        if not fb.exists():
            text = (folder / "reply.txt").read_text()
            try:
                params = apply_reply(base, text)
                entry = {"round": r, "valid": True, "train": report(params, base, train, ktr), "bands": bands(params, train, ktr)}
            except Exception as error:
                entry = {"round": r, "valid": False, "error": f"{type(error).__name__}: {str(error)[:200]}"}
            fb.write_text(json.dumps(entry, indent=2) + "\n")
        out.append(json.loads(fb.read_text()) | {"reply": (folder / "reply.txt").read_text().strip()})
    return out


def build_prompt(potential: str, past: list[dict]) -> str:
    base, train, ktr, _, _ = setup(potential)
    u = report(base, base, train, ktr)
    gK, sK, gE, sE = table(potential)
    w = base["w"].numpy()
    rows = "\n".join(f"{j} | {w[j]:.5g} | {gK[j]:+.4g} | {sK[j]:.3g} | {gE[j]:+.4g} | {sE[j]:.3g}" for j in range(len(w)))
    if has_bias(potential):
        per_unit = np.mean([float(s.c[3] / s.n_atoms) for s in train])
        bias_text = (f"You can change w ({len(w)} numbers) and b (1 number). b is a uniform term: increasing it by one unit raises the "
                     f"energy per atom of every crystal by {per_unit:.6g} eV and cannot change a bulk modulus.")
        other = f"\n# The other number\n## b shape=(1,)\n{float(base['b']):.6g}\n"
        names = "w and b"
    else:
        bias_text = f"You can change w ({len(w)} numbers). There is no uniform energy term in this readout."
        other, names = "", "w only"
    if past:
        blocks = []
        for p in past:
            if not p["valid"]:
                blocks.append(f"## Attempt {p['round']}\nYour reply:\n{p['reply']}\nResult: rejected, {p['error']}")
                continue
            t = p["train"]
            verdict = "within the limit" if t["energy_change_meV_per_atom"] <= LIMIT else "ABOVE the limit: a failure"
            blocks.append(f"## Attempt {p['round']}\nYour reply:\n{p['reply']}\nMeasured on the same {len(train)} crystals: bulk modulus "
                          f"mean error {t['bias_GPa']:+.2f} GPa, mean absolute error {t['mae_GPa']:.2f} GPa; mean absolute change of "
                          f"energy per atom {t['energy_change_meV_per_atom']:.2f} meV ({verdict}).\n" + "\n".join(p["bands"]))
        left = ROUNDS - len(past)
        feedback = (f"\n# Your earlier attempts\nThis is attempt {len(past) + 1} of {ROUNDS}. Each earlier reply was applied to the original "
                    f"numbers and measured. Edits do not accumulate: every reply is applied to the original numbers. "
                    f"{'After this one you have ' + str(left - 1) + ' more.' if left > 1 else 'This is your last attempt.'} "
                    f"The reply that counts is the one with the lowest mean absolute error among those within the energy limit.\n\n"
                    + "\n\n".join(blocks) + "\n")
    else:
        feedback = (f"\n# Attempts\nThis is attempt 1 of {ROUNDS}. After each attempt your edit is applied and measured on these "
                    f"{len(train)} crystals, and you are shown the result before the next attempt. Every reply is applied to the "
                    f"original numbers. The reply that counts is the one with the lowest mean absolute error among those within the energy limit.\n")
    return f"""You are given the last layer of the energy readout of a machine-learned interatomic potential ({FULL_NAME[potential]}, {TOTAL_WEIGHTS[potential]:,} weights in total) as raw numbers. You cannot run it and you cannot train it.

# How the last layer works
The energy of a crystal is
  E = h . w + (uniform term) + (terms that do not depend on these numbers)
h is a vector of {len(w)} numbers computed for the crystal by the frozen layers before; it changes when the crystal is strained. {bias_text}

# The fault
On {len(train)} crystals with DFT bulk moduli (Materials Project elastic tensors), this potential's bulk modulus, from a fit of energy against volume over +-3%, is wrong by {u['bias_GPa']:+.1f} GPa on average (mean absolute error {u['mae_GPa']:.1f} GPa). By range of the DFT value:
{chr(10).join(bands(base, train, ktr))}

# The task
Edit the numbers so that the bulk modulus error on NEW crystals is smaller, while the energy per atom of every crystal stays where it is: a mean absolute change above {LIMIT:.0f} meV per atom counts as a failure, because formation energies depend on it.

# What each weight does
For each weight j of w: its value; the change of the bulk modulus in GPa per unit increase of the weight, mean over the {len(train)} crystals and standard deviation across them; the change of the energy per atom in eV per unit increase, mean and standard deviation. The bulk-modulus numbers are measured by changing the weight by {STEP[potential]} and refitting energy against volume, so they include the shift of the equilibrium volume. They hold for small changes; the energy numbers are exact, because the energy is linear in w.
j | w[j] | dK mean | dK sd | dE mean | dE sd
{rows}
{other}{feedback}
# Reply format
Reply with a JSON list of edits and no other text. Each edit is {{"tensor": name, "index": [i], "value": number}} with zero-based indices; `value` is the new value, not the change. Tensor names: {names}.
"""


def next_round(potential: str, model: str, chain: int) -> None:
    done = 0
    while (chain_folder(potential, model, chain, done + 1) / "reply.txt").exists():
        done += 1
    if done >= ROUNDS:
        print(f"chain {potential} {model} c{chain}: all {ROUNDS} rounds done")
        return
    folder = chain_folder(potential, model, chain, done + 1)
    if (folder / "prompt.txt").exists():
        print(f"waiting for {folder.name}")
        return
    folder.mkdir(parents=True, exist_ok=True)
    text = build_prompt(potential, history(potential, model, chain, done))
    (folder / "prompt.txt").write_text(text)
    if not (folder / "meta.json").exists():
        (folder / "meta.json").write_text(json.dumps(
            {"arm": "head_edit_with_feedback", "potential": potential, "model_alias": model, "chain": chain, "round": done + 1,
             "forward_passes": done, "prompt_chars": len(text), "prompt_tokens_estimate": estimate_tokens(text)}, indent=2) + "\n")
    print(f"NEW {folder.name}")


def score() -> None:
    chains: dict[tuple, int] = {}
    for run in RUNS.iterdir():
        m = CHAIN.fullmatch(run.name)
        if m and (run / "reply.txt").exists():
            key = (m[1], m[2], int(m[3]))
            chains[key] = max(chains.get(key, 0), int(m[4]))
    lines = ["| Potential | Model | Chain | Rounds | Round 1: MAE / bias / energy change | Chosen round | Chosen: MAE / bias / energy change |",
             "|---|---|---|---|---|---|---|"]
    out = []
    for (potential, model, chain), rounds in sorted(chains.items()):
        base, train, ktr, test, kte = setup(potential)
        past = history(potential, model, chain, rounds)
        per_round = []
        for p in past:
            if p["valid"]:
                params = apply_reply(base, p["reply"])
                per_round.append({"round": p["round"], "train": p["train"], "test": report(params, base, test, kte)})
            else:
                per_round.append({"round": p["round"], "invalid": p["error"]})
        ok = [r for r in per_round if "train" in r and r["train"]["energy_change_meV_per_atom"] <= LIMIT and r["train"]["failed_fits"] == 0]
        unedited = report(base, base, test, kte)
        chosen = min(ok, key=lambda r: r["train"]["mae_GPa"]) if ok else None
        if chosen and chosen["train"]["mae_GPa"] >= report(base, base, train, ktr)["mae_GPa"]:
            chosen = None
        final = chosen["test"] if chosen else unedited
        row = {"potential": potential, "model": model, "chain": chain, "rounds": rounds, "per_round": per_round,
               "chosen_round": chosen["round"] if chosen else None, "final_test": final, "unedited_test": unedited}
        out.append(row)
        fmt = lambda t: f"{t['mae_GPa']:.2f} / {t['bias_GPa']:+.2f} / {t['energy_change_meV_per_atom']:.1f}"
        first = fmt(per_round[0]["test"]) if "test" in per_round[0] else "invalid"
        lines.append(f"| {potential} | {model} | {chain} | {rounds} | {first} | {row['chosen_round'] or 'none (unedited)'} | {fmt(final)} |")
        print(lines[-1])
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "chains.json").write_text(json.dumps(out, indent=2) + "\n")
    (RESULTS / "chains.md").write_text("\n".join(lines) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    b = sub.add_parser("baselines")
    b.add_argument("--potential", choices=POTENTIALS, required=True)
    n = sub.add_parser("next")
    n.add_argument("--potential", choices=POTENTIALS)
    n.add_argument("--model")
    n.add_argument("--chain", type=int)
    n.add_argument("--all", action="store_true", help="advance every chain that has a finished round")
    sub.add_parser("score")
    args = parser.parse_args()
    if args.command == "baselines":
        baselines(args.potential)
    elif args.command == "next" and args.all:
        for key in sorted({(m[1], m[2], int(m[3])) for m in map(CHAIN.fullmatch, (r.name for r in RUNS.iterdir())) if m}):
            next_round(*key)
    elif args.command == "next":
        next_round(args.potential, args.model, args.chain)
    else:
        score()


if __name__ == "__main__":
    main()
