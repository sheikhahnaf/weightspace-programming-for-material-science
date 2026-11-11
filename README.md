# weighspace-programming

Where weight-space programming fits in Bayesian materials discovery, and a campaign to test it across applications.

**Weight-space programming** (WSP): an LLM reads, writes or edits a network's weights directly, with no gradient descent. Introduced in a blog post of 2 November 2026 (Takehi, Teoh, Zhang, Khattab, MIT CSAIL). Preprints only; no peer-reviewed paper.

## What the research found

| Target | Fit | Why |
|---|---|---|
| BO surrogate | fits now | The readout head or prior mean on frozen embeddings is 300 to 2,700 weights; WSP has been shown from raw weights up to about 172,000. |
| MLIP | readout only | MACE-MPA-0 medium has 9,063,204 weights; its readouts, reference energies and scale and shift are 2,283 (measured here). |
| Generative model | not the narrow sense | MatterGen's base checkpoint holds 53.7 million values. The useful work is on the 59 fine-tuned checkpoints that already exist (task vectors, merging). |

Full account with sources, checks and corrections: [`docs/research-runs/2026-11-11-where-wsp-fits.md`](docs/research-runs/2026-11-11-where-wsp-fits.md).

## What has been run

Baselines on five tasks and a first pilot of two LLM arms: [`docs/results/2026-11-11-e1-pilot.md`](docs/results/2026-11-11-e1-pilot.md).

- The GP underpredicts the best tenth of candidates on all five tasks, and its 95% intervals cover only 79% and 85% of the generated structures in the two closed-loop tasks.
- Asked to edit a trained head, the model rescaled the output layer, and did the same on a network with shuffled weights. No evidence of weight reading in that arm.
- Asked to write a network from materials knowledge with no data, the model produced networks that rank alloys at Spearman 0.54 and 0.63. As a GP prior they raised ranking at 10 to 20 labels.

The LLM cells are single runs with one model. They are a pilot.

## Campaign

| Experiment | Application | Data in this repo | State |
|---|---|---|---|
| [E1](experiments/e1_surrogate_head/) readout head and prior mean | BO surrogate: closed-loop bulk modulus and heat capacity, alloy strength, titanium alloys, composition screening | `data/closed_loop_bm`, `data/closed_loop_cp`, `data/alloys` | baselines run; pilot run |
| [E2](experiments/e2_mlip_readout_edit/) scalar readout edit of MACE | MLIP | `data/causal_replay/esen_vs_dft_bm.csv`, `data/dft_validation` | specified |
| [E3](experiments/e3_generator_task_vectors/) task vectors of fine-tuned generators | generative model | checkpoints on Hugging Face, not downloaded | specified |
| [E4](experiments/e4_surrogate_zoo/) learning from fitted surrogates | BO surrogate, broad sense | `data/surrogate_zoo` (30,360 fitted surrogates) | specified |

## Layout

```
src/wsp/            harness: weights <-> text, edits, heads, prompts, tasks, baselines, LLM arms
tests/              35 tests
experiments/        one folder per experiment; E1 holds results/ and runs/<id>/ (prompt, reply, meta, score)
data/               copied datasets, with PROVENANCE.md (source path, size, checksum per file)
vendor/             algorithms copied unmodified from the sibling repos
scripts/            copy_from_siblings.py
docs/research-runs/ the literature and fit analysis
docs/results/       results pages
research/           brief, research reports, source lists, repo surveys
env/                exact environment
questions.md        every question asked of this project, with status
REPRODUCE.md        the command behind every number
```

## Run

```bash
eval "$(/Users/alvi/miniconda3/bin/conda shell.zsh hook)" && conda activate matinvent
export PYTHONPATH=src
python -m pytest -q -W ignore
python experiments/e1_surrogate_head/run_baseline.py
```

Data and algorithms come from `matgen-BO`, `matinvent-bo` and `autoresearch-bo`, which this project only reads. Third-party datasets keep their own licences (see the headers in `vendor/bo_zoo/benchmarks/`).
