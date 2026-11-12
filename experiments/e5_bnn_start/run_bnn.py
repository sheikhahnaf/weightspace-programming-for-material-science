"""E5: can an LLM-written network be the starting point, or the prior, of a Bayesian neural network?

A BNN trained on a handful of labels depends heavily on where it starts and on
its prior. This experiment hands it a network that a language model wrote from
materials knowledge (replies of the write arm and of the generator-filter arm;
no new model runs) and compares with the usual zero-centred setup.

Three finite-width BNNs, all d -> 16 -> 1 so a written network maps onto them exactly:

  MC dropout (the `pbnn` design of the multi-surrogate BO repo: heteroscedastic head, dropout at test time)
    mcd_random       random start
    mcd_llm_init     starts at the written weights
    mcd_llm_anchor   starts there and is penalised for leaving
    mcd_llm_mean     random start, fitted to y - (a*m(x)+b): the written network as prior mean
  Deep ensemble of five networks
    ens_random       random starts
    ens_llm_init     starts at the written weights plus small noise
  Hamiltonian Monte Carlo over the weights (the best-performing BNN in Li, Rudner and
  Wilson's study of BNN surrogates for BO; re-implemented here, their repo has no licence)
    hmc_zero         Gaussian prior centred at zero, chain started from a short MAP fit
    hmc_llm_init     the same zero-centred prior, chain started at the written weights
    hmc_llm_prior    Gaussian prior centred at the written weights, chain started there

Reference: gp (default Matern GP) and gp_llm_mean (written network as its prior mean).

All models see standardised inputs and targets. The written network is folded into
those coordinates and its hidden units are rescaled so that incoming and outgoing
weights have equal size; both steps leave its function unchanged (checked per cell).

Tasks: five alloy tasks (element fractions) and matbench_log_kvrh (10,973 crystals,
15 named descriptors). Training sizes 10, 20, 50, 200; five seeds; held-out test rows.

    python experiments/e5_bnn_start/run_bnn.py --jobs 8
"""

from __future__ import annotations

import argparse
import json
import re
import warnings
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = HERE / "results"
ALLOY_TASKS = ("ti_alloy_youngs_modulus", "ti_alloy_yield_strength", "ti_alloy_hardness",
               "mpea_yield_strength", "mpea_hardness")
TASKS = (*ALLOY_TASKS, "matbench_kvrh")
MODELS = ("opus", "fable")
SIZES = (10, 20, 50, 200)
BASE_ARMS = ("gp", "mcd_random", "ens_random", "hmc_zero")
LLM_ARMS = ("gp_llm_mean", "mcd_llm_init", "mcd_llm_anchor", "mcd_llm_mean", "ens_llm_init", "hmc_llm_init", "hmc_llm_prior")
BASELINE_OF = {"gp_llm_mean": "gp", "mcd_llm_init": "mcd_random", "mcd_llm_anchor": "mcd_random",
               "mcd_llm_mean": "mcd_random", "ens_llm_init": "ens_random", "hmc_llm_init": "hmc_zero",
               "hmc_llm_prior": "hmc_zero"}
HIDDEN = 16
NOISE = 0.3   # observation noise of the ensemble and HMC likelihoods, in standardised target units
PRIOR = 1.0   # prior standard deviation of every weight


def load(task: str, seed: int):
    if task == "matbench_kvrh":
        d = np.load(ROOT / "data" / "bnn" / "matbench_kvrh_descriptors.npz")
        X, y = d["X"], d["K_GPa"]
        order = np.random.default_rng(seed).permutation(len(y))
        return X, y, order[2000:], order[:2000]
    from wsp.tasks import load_task

    t = load_task(task)
    train, test = t.split(seed)
    return t.X, t.y, train, test


def replies(task: str) -> dict[str, list[dict]]:
    from wsp import load_weights

    if task == "matbench_kvrh":
        folder, pattern = ROOT / "experiments/e3_crystal_filter/runs", r"filter_K__(opus|fable)__rep\d+"
    else:  # the three earliest Fable replies of two tasks carry no model tag in their folder name
        folder, pattern = ROOT / "experiments/e1_surrogate_head/runs", rf"write__{task}(?:__(opus|fable))?(?:__rep\d+)?"
    out: dict[str, list[dict]] = {m: [] for m in MODELS}
    for run in sorted(folder.iterdir()):
        m = re.fullmatch(pattern, run.name)
        if not m or not (run / "reply.txt").exists():
            continue
        try:
            s = load_weights((run / "reply.txt").read_text())
            net = {"name": run.name, "W1": s["net.0.weight"].double().numpy(), "b1": s["net.0.bias"].double().numpy(),
                   "w2": s["net.2.weight"].double().numpy()[0], "b2": float(s["net.2.bias"][0])}
            assert net["W1"].shape[0] == HIDDEN
            out[m.group(1) or "fable"].append(net)
        except Exception:
            continue
    return out


def forward_np(net: dict, X: np.ndarray) -> np.ndarray:
    return np.maximum(X @ net["W1"].T + net["b1"], 0) @ net["w2"] + net["b2"]


def fold(net: dict, mx, sx, my, sy) -> dict:
    """The same function in standardised coordinates, with each hidden unit rescaled
    (relu(c*u)/c = relu(u) for c > 0) so its incoming and outgoing weights are the same size."""
    W1, b1 = net["W1"] * sx, net["b1"] + net["W1"] @ mx
    w2, b2 = net["w2"] / sy, (net["b2"] - my) / sy
    incoming = np.sqrt((W1**2).sum(1) + b1**2)
    c = np.ones(HIDDEN)
    live = (incoming > 0) & (np.abs(w2) > 0)
    c[live] = np.sqrt(np.abs(w2[live]) / incoming[live])
    return {"W1": W1 * c[:, None], "b1": b1 * c, "w2": w2 / c, "b2": b2}


def metrics(y, mean, std) -> dict:
    from scipy.stats import spearmanr
    from sklearn.metrics import r2_score

    std = np.maximum(std, 1e-9)
    rho = spearmanr(y, mean).statistic if np.ptp(mean) > 0 else 0.0
    return {"r2": float(r2_score(y, mean)), "spearman": float(rho),
            "nll": float(np.mean(0.5 * np.log(2 * np.pi * std**2) + 0.5 * ((y - mean) / std) ** 2)),
            "coverage95": float(np.mean(np.abs(y - mean) <= 1.96 * std))}


def gp_predict(Ztr, ttr, Zte):
    import torch
    from botorch.fit import fit_gpytorch_mll
    from botorch.models import SingleTaskGP
    from botorch.models.transforms.input import Normalize
    from gpytorch.mlls import ExactMarginalLogLikelihood

    X = torch.tensor(Ztr, dtype=torch.float64)
    model = SingleTaskGP(X, torch.tensor(ttr, dtype=torch.float64).unsqueeze(-1), input_transform=Normalize(d=X.shape[-1]))
    fit_gpytorch_mll(ExactMarginalLogLikelihood(model.likelihood, model))
    model.eval()
    with torch.no_grad():
        p = model.posterior(torch.tensor(Zte, dtype=torch.float64), observation_noise=True)
    return p.mean.detach().squeeze(-1).numpy(), p.variance.detach().squeeze(-1).sqrt().numpy()


def _init_layers(d, start, seed, jitter=0.0):
    import torch
    from torch import nn

    torch.manual_seed(seed)
    first, head = nn.Linear(d, HIDDEN), nn.Linear(HIDDEN, 1)
    if start is not None:
        with torch.no_grad():
            first.weight.copy_(torch.tensor(start["W1"], dtype=torch.float32))
            first.bias.copy_(torch.tensor(start["b1"], dtype=torch.float32))
            head.weight.copy_(torch.tensor(start["w2"], dtype=torch.float32).unsqueeze(0))
            head.bias.fill_(start["b2"])
            for p in (*first.parameters(), *head.parameters()):
                p.add_(jitter * torch.randn_like(p))
    return first, head


def mcd_predict(Ztr, ttr, Zte, seed, start=None, anchor=0.0, epochs=600, dropout=0.1, passes=50):
    import torch
    from torch import nn

    first, head = _init_layers(Ztr.shape[1], start, seed)
    std_head = nn.Linear(HIDDEN, 1)
    with torch.no_grad():
        std_head.weight.zero_()
        std_head.bias.fill_(float(np.log(0.5)))
    core = (*first.parameters(), *head.parameters())
    anchors = [p.detach().clone() for p in core]
    drop = nn.Dropout(dropout)

    def f(x):
        h = drop(torch.relu(first(x)))
        return head(h).squeeze(-1), std_head(h).squeeze(-1).clamp(-5, 3)

    X, t = torch.tensor(Ztr, dtype=torch.float32), torch.tensor(ttr, dtype=torch.float32)
    opt = torch.optim.AdamW([*core, *std_head.parameters()], lr=1e-3 if start is not None else 3e-3, weight_decay=1e-4)
    for _ in range(epochs):
        opt.zero_grad()
        mu, log_std = f(X)
        loss = (log_std + 0.5 * ((t - mu) / log_std.exp()) ** 2).mean()
        if anchor:
            loss = loss + anchor * sum(((p - a) ** 2).mean() for p, a in zip(core, anchors))
        loss.backward()
        opt.step()
    with torch.no_grad():
        draws = [f(torch.tensor(Zte, dtype=torch.float32)) for _ in range(passes)]
    mus = torch.stack([m for m, _ in draws]).numpy()
    var = mus.var(0) + np.mean([np.exp(2 * s.numpy()) for _, s in draws], axis=0)
    return mus.mean(0).astype(float), np.sqrt(var).astype(float)


def ensemble_predict(Ztr, ttr, Zte, seed, start=None, members=5, epochs=600):
    import torch

    X, t = torch.tensor(Ztr, dtype=torch.float32), torch.tensor(ttr, dtype=torch.float32)
    preds = []
    for k in range(members):
        first, head = _init_layers(Ztr.shape[1], start, 100 * seed + k, jitter=0.05 if start is not None else 0.0)
        opt = torch.optim.AdamW([*first.parameters(), *head.parameters()], lr=1e-3 if start is not None else 3e-3, weight_decay=1e-4)
        for _ in range(epochs):
            opt.zero_grad()
            torch.nn.functional.mse_loss(head(torch.relu(first(X))).squeeze(-1), t).backward()
            opt.step()
        with torch.no_grad():
            preds.append(head(torch.relu(first(torch.tensor(Zte, dtype=torch.float32)))).squeeze(-1).numpy())
    preds = np.array(preds)
    return preds.mean(0).astype(float), np.sqrt(preds.var(0) + NOISE**2).astype(float)


def hmc_predict(Ztr, ttr, Zte, seed, start=None, prior_mean=None, burn=200, samples=200, leapfrog=20):
    """HMC over all weights with a Gaussian likelihood (sd NOISE) and a Gaussian prior (sd PRIOR)
    centred at `prior_mean` (zero if None). The chain starts at `start`, or at a short MAP fit."""
    import torch

    torch.manual_seed(seed)
    d = Ztr.shape[1]
    X, t = torch.tensor(Ztr, dtype=torch.float64), torch.tensor(ttr, dtype=torch.float64)
    shapes = [(HIDDEN, d), (HIDDEN,), (HIDDEN,), (1,)]
    sizes = [int(np.prod(s)) for s in shapes]
    pack = lambda n: torch.tensor(np.concatenate([n["W1"].ravel(), n["b1"], n["w2"], [n["b2"]]]), dtype=torch.float64)  # noqa: E731
    mu0 = pack(prior_mean) if prior_mean is not None else torch.zeros(sum(sizes), dtype=torch.float64)

    def f(theta, x):
        W1, b1, w2, b2 = [p.reshape(s) for p, s in zip(torch.split(theta, sizes), shapes)]
        return torch.relu(x @ W1.T + b1) @ w2 + b2

    def logp(theta):
        return -0.5 * ((t - f(theta, X)) ** 2).sum() / NOISE**2 - 0.5 * ((theta - mu0) ** 2).sum() / PRIOR**2

    def grad(theta):
        theta = theta.detach().requires_grad_(True)
        value = logp(theta)
        return value.detach(), torch.autograd.grad(value, theta)[0]

    if start is not None:
        theta = pack(start)
    else:
        theta = (torch.randn(sum(sizes), dtype=torch.float64) / np.sqrt(d)).requires_grad_(True)
        opt = torch.optim.Adam([theta], lr=1e-2)
        for _ in range(300):
            opt.zero_grad()
            (-logp(theta)).backward()
            opt.step()
        theta = theta.detach()
    step, kept, accepted = 1e-3, [], 0
    value, g = grad(theta)
    for it in range(burn + samples):
        momentum = torch.randn_like(theta)
        new, new_g, p = theta.clone(), g.clone(), momentum + 0.5 * step * g
        for _ in range(leapfrog):
            new = new + step * p
            new_value, new_g = grad(new)
            p = p + step * new_g
        p = p - 0.5 * step * new_g
        log_ratio = (new_value - 0.5 * (p**2).sum()) - (value - 0.5 * (momentum**2).sum())
        ok = bool(torch.isfinite(log_ratio)) and float(torch.rand(())) < float(torch.exp(log_ratio.clamp(max=0)))
        if ok:
            theta, value, g = new.detach(), new_value, new_g
        if it < burn:
            step *= 1.1 if ok else 0.7
        else:
            accepted += ok
            kept.append(theta.clone())
    Zt = torch.tensor(Zte, dtype=torch.float64)
    with torch.no_grad():
        preds = torch.stack([f(k, Zt) for k in kept[::4]]).numpy()
    return preds.mean(0), np.sqrt(preds.var(0) + NOISE**2), accepted / samples


def cell(task: str, n: int, seed: int) -> dict:
    cache = OUT / "cells" / f"{task}__n{n}__seed{seed}.json"
    if cache.exists():
        return json.loads(cache.read_text())
    import torch

    warnings.filterwarnings("ignore")
    torch.set_num_threads(1)
    X, y, pool, test = load(task, seed)
    train = np.random.default_rng(1000 + seed).permutation(pool)[:n]
    mx, sx = X[train].mean(0), X[train].std(0)
    sx = np.where(sx < 1e-6, 1.0, sx)  # an input that is constant in a small sample is left unscaled
    my, sy = float(y[train].mean()), float(y[train].std() + 1e-8)
    Ztr, Zte, ttr = (X[train] - mx) / sx, (X[test] - mx) / sx, (y[train] - my) / sy
    yte = y[test]
    back = lambda m, s: (m * sy + my, s * sy)  # noqa: E731
    out = {"task": task, "n": n, "seed": seed, "arms": {}, "hmc_acceptance": {}}
    out["arms"]["gp"] = metrics(yte, *back(*gp_predict(Ztr, ttr, Zte)))
    out["arms"]["mcd_random"] = metrics(yte, *back(*mcd_predict(Ztr, ttr, Zte, seed)))
    out["arms"]["ens_random"] = metrics(yte, *back(*ensemble_predict(Ztr, ttr, Zte, seed)))
    m, s, acc = hmc_predict(Ztr, ttr, Zte, seed)
    out["arms"]["hmc_zero"] = metrics(yte, *back(m, s))
    out["hmc_acceptance"]["hmc_zero"] = acc
    for model, nets in replies(task).items():
        for net in nets:
            m_tr, m_te = forward_np(net, X[train]), forward_np(net, X[test])
            folded = fold(net, mx, sx, my, sy)
            assert np.allclose(forward_np(folded, Zte) * sy + my, m_te, rtol=1e-6, atol=1e-6 * (abs(m_te).max() + 1))
            slope, intercept = np.polyfit(m_tr, y[train], 1) if np.ptp(m_tr) > 0 else (0.0, my)
            res = y[train] - (slope * m_tr + intercept)
            rm, rs = float(res.mean()), float(res.std() + 1e-8)
            lift = lambda mm, ss: (mm * rs + rm + slope * m_te + intercept, ss * rs)  # noqa: E731
            arms = {
                "written_alone": metrics(yte, m_te, np.full(len(yte), sy)),
                "gp_llm_mean": metrics(yte, *lift(*gp_predict(Ztr, (res - rm) / rs, Zte))),
                "mcd_llm_mean": metrics(yte, *lift(*mcd_predict(Ztr, (res - rm) / rs, Zte, seed))),
                "mcd_llm_init": metrics(yte, *back(*mcd_predict(Ztr, ttr, Zte, seed, start=folded))),
                "mcd_llm_anchor": metrics(yte, *back(*mcd_predict(Ztr, ttr, Zte, seed, start=folded, anchor=1.0))),
                "ens_llm_init": metrics(yte, *back(*ensemble_predict(Ztr, ttr, Zte, seed, start=folded))),
            }
            for arm, prior in (("hmc_llm_init", None), ("hmc_llm_prior", folded)):
                m, s, acc = hmc_predict(Ztr, ttr, Zte, seed, start=folded, prior_mean=prior)
                arms[arm] = metrics(yte, *back(m, s))
                out["hmc_acceptance"][f"{arm}|{net['name']}"] = acc
            out["arms"][f"{model}|{net['name']}"] = arms
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps(out) + "\n")
    return out


def summarise(seeds: int) -> None:
    arms = (*BASE_ARMS, *LLM_ARMS)
    order = ("gp", "gp_llm_mean", "mcd_random", "mcd_llm_init", "mcd_llm_anchor", "mcd_llm_mean",
             "ens_random", "ens_llm_init", "hmc_zero", "hmc_llm_init", "hmc_llm_prior")
    lines, summary = [], {}
    for metric, better in (("spearman", "higher"), ("nll", "lower"), ("coverage95", "0.95 is calibrated")):
        lines += [f"**{metric} ({better}); mean over seeds and replies (median for nll)**", "",
                  "| Task (model) | Labels | " + " | ".join(order) + " |", "|---|---|" + "---|" * len(order)]
        for model in MODELS:
            for task in TASKS:
                for n in SIZES:
                    cells = [json.loads(p.read_text()) for p in sorted((OUT / "cells").glob(f"{task}__n{n}__seed*.json"))][:seeds]
                    row = {}
                    for arm in arms:
                        values = ([c["arms"][arm][metric] for c in cells] if arm in BASE_ARMS else
                                  [v[arm][metric] for c in cells for k, v in c["arms"].items() if k.startswith(model + "|")])
                        if values:
                            row[arm] = float(np.median(values)) if metric == "nll" else float(np.mean(values))
                    if len(row) < len(arms):
                        continue
                    summary[f"{metric}|{model}|{task}|{n}"] = row
                    lines.append(f"| `{task}` ({model}) | {n} | " + " | ".join(f"{row[a]:.2f}" for a in order) + " |")
        lines.append("")
    wins = {a: [0, 0] for a in LLM_ARMS}
    for key, row in summary.items():
        metric, _, _, n = key.split("|")
        if metric == "spearman":
            for a in LLM_ARMS:
                small = int(n) <= 20
                wins[a][0 if small else 1] += row[a] > row[BASELINE_OF[a]] + 0.01
    cells_small = sum(k.startswith("spearman|") and int(k.split("|")[3]) <= 20 for k in summary)
    cells_large = sum(k.startswith("spearman|") and int(k.split("|")[3]) > 20 for k in summary)
    lines += ["**How often the LLM version ranks better than its own baseline (ρ higher by more than 0.01), over model × task cells**", "",
              f"| Arm | Baseline | At 10 or 20 labels (of {cells_small}) | At 50 or 200 labels (of {cells_large}) |", "|---|---|---|---|"]
    lines += [f"| {a} | {BASELINE_OF[a]} | {w[0]} | {w[1]} |" for a, w in wins.items()]
    (OUT / "bnn_summary.json").write_text(json.dumps(summary, indent=1) + "\n")
    (OUT / "bnn_summary.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--seeds", type=int, default=5)
    parser.add_argument("--jobs", type=int, default=8)
    args = parser.parse_args()
    from joblib import Parallel, delayed

    work = []
    for task in TASKS:
        for seed in range(args.seeds):
            _, _, pool, _ = load(task, seed)
            work += [(task, n, seed) for n in SIZES if n <= len(pool)]
    Parallel(n_jobs=args.jobs, verbose=5)(delayed(cell)(*w) for w in work)
    summarise(args.seeds)


if __name__ == "__main__":
    main()
