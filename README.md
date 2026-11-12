# Weight-space programming for materials science

A language model writes property-prediction networks from knowledge alone.

A language model is given a task in words, the names of the inputs and an empty 16-unit network, and writes every weight. No data, no training run, no tools. This repository tests what such a network is good for in materials discovery, and records every prompt, reply and score.

This is **weight-space programming** (WSP) in the narrow sense: a language model acting on weights directly, with no gradient descent (Takehi, Teoh, Zhang, Khattab, MIT CSAIL, 2 November 2026). Methods that treat weights as data without a language model (task vectors, merging, learning on weight zoos) are **weight-space learning** and are kept apart, under `supplementary/`.

## What a written network is good for

| Use | Result | Where |
|---|---|---|
| Predictor with no labels | Opus 5.5 ranks experimental alloys at Spearman ρ 0.64 to 0.79 (rule of mixtures: −0.72 to 0.28) and crystal bulk modulus at 0.93 (1/volume rule: 0.74). | `experiments/e1_surrogate_head/results/standalone/summary.md` |
| Prior mean of a Gaussian process, few labels | At 5 labels ρ rises from 0.35 to 0.69 on alloys and from 0.15 to 0.95 on crystal bulk modulus. The plain GP catches up near 50 labels (alloys) or 20 (crystals). | `docs/results/2026-11-11-round6.md`, `docs/results/2026-11-12-round7.md` |
| Bayesian optimization | Lower regret on 4 of 5 experimental alloy tasks (20 seeds, Holm p ≤ 0.047), higher on one. On 33 Thermo-Calc targets: significantly lower on 16 (Opus) and 15 (Fable), higher on 0 and 1. | `docs/results/2026-11-11-round3.md`, `experiments/e7_calphad_prior/results/overview.md` |
| Hidden layer as GP inputs | With 500 labels a GP on the 16 written hidden units ranks crystal bulk modulus at 0.94, against 0.89 for the GP on a 50-dimensional learned embedding. | `docs/results/2026-11-12-round7.md` |
| Mean of a Bayesian neural network | MC dropout 0.54 to 0.65 at 10 to 20 labels. As starting weights or as a weight-space prior it does not help. | `docs/results/2026-11-11-round4.md` |
| Screening filter for crystal generators | ρ 0.92 (MatterGen samples) and 0.88 (CrystalFlow samples) with the oracle, against 0.82 and 0.77 for the volume rule; the share of CrystalFlow samples above 150 GPa in the kept quarter rises from 0.16 to 0.52. | `experiments/e3_crystal_filter/results/` |

**Against computed thermodynamics.** On 35 Thermo-Calc targets in nine alloy systems (solidus, freezing range, phase fractions), the no-LLM reference is an extrapolation from computed binary and ternary values. With no labels it ranks the pools at a mean ρ of 0.70; networks written with no data reach 0.67 (Opus) and 0.64 (Fable), and are ahead on the 16 phase-fraction targets (0.69 and 0.67 against 0.63). With the same binary and ternary values in the prompt the networks reach 0.73 and 0.71. In BO the extrapolation is significantly better than the plain GP on 18 of 33 targets, Opus on 16, Opus with facts on 18; median regret area relative to the plain GP 0.17, 0.43 and 0.24.

Where it fails or adds nothing:

- Yield strength of multi-principal-element alloys: the networks rank the pool well (ρ 0.69) and still make BO worse in 14 of 20 seeds.
- Heat capacity per gram: the Dulong–Petit rule ranks perfectly and the network only matches it.
- With the two-stage fit of the slope and offset the error bars are too narrow at 5 labels; a joint fit restores coverage and should be the default.
- With hundreds of labels the plain GP catches up.
- All language-model results use one vendor's models (Claude Opus 5.5, Fable 5.2, Sonnet 5.5, Haiku 5.5).

## Experiments

| Folder | What it holds |
|---|---|
| [`experiments/e1_surrogate_head/`](experiments/e1_surrogate_head/) | Experimental alloy tasks and crystal tasks: write arm, GP prior mean (two-stage and joint), BO, hidden layer as inputs, standalone metrics |
| [`experiments/e7_calphad_prior/`](experiments/e7_calphad_prior/) | Thermo-Calc targets for nine alloy systems: data builder, write arm with and without phase-diagram facts, no-LLM sub-system extrapolation, GP and BO |
| [`experiments/e3_crystal_filter/`](experiments/e3_crystal_filter/) | Written networks on crystal descriptors as a screening filter for MatterGen and CrystalFlow samples |
| [`experiments/e5_bnn_start/`](experiments/e5_bnn_start/) | Written networks in Bayesian neural networks: mean, start, weight prior |
| [`supplementary/`](supplementary/) | Other weight-space experiments: readout edits of interatomic potentials, formation-enthalpy correction, generator task vectors, learning from fitted surrogates, editing an open table reader |

Every model run has a folder `experiments/<experiment>/runs/<arm>__<task>__<model>__rep<k>/` with the prompt, the raw reply, the model's own account and the score.

## Records

- Results pages, in order: [`docs/results/`](docs/results/). Literature and fit analysis: [`docs/research-runs/2026-11-11-where-wsp-fits.md`](docs/research-runs/2026-11-11-where-wsp-fits.md).
- The command behind every number: [`REPRODUCE.md`](REPRODUCE.md). Environment: `env/`.
- Every question asked of this project, with status: [`questions.md`](questions.md). Work log: [`PROGRESS.md`](PROGRESS.md).
- The paper is in a separate repository.

## Layout

```
src/wsp/            harness: weights <-> text, heads, prompts, tasks, baselines, GP arms
tests/              212 tests
experiments/        the main case: written networks (see the table above)
supplementary/      other weight-space experiments
data/               datasets, with PROVENANCE.md; data/calphad/ holds the Thermo-Calc pools
vendor/             algorithms copied unmodified from the sibling repos
scripts/            copy_from_siblings.py
docs/               results pages and the research run
research/           brief, research reports, source lists
slides/             slide deck on the GP-prior case
```

The tables in `data/calphad/` were computed with Thermo-Calc 2025b and its commercial databases. Whether they may be redistributed has not been checked; this repository is private, and that must be settled before any public release.

## Run

```bash
eval "$(/Users/alvi/miniconda3/bin/conda shell.zsh hook)" && conda activate matinvent
export PYTHONPATH=src
python -m pytest -q -W ignore
python experiments/e1_surrogate_head/run_baseline.py
```

Data and algorithms come from `matgen-BO`, `matinvent-bo` and `autoresearch-bo`, which this project only reads. Third-party datasets keep their own licences (see the headers in `vendor/bo_zoo/benchmarks/`).
