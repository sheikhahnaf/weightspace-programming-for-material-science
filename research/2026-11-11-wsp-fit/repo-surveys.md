# Read-only survey of the three sibling repos

Date: 2026-11-11. Three read-only agents, one per repo. Nothing in those repos was modified.
Paths are absolute under `/Volumes/SSD1_SMAAA/`. Numbers are as stated in the cited files; none were recomputed here.

## What exists

| Repo | What it is | Surrogates | Foundation models | Generators |
|---|---|---|---|---|
| `matgen-BO` | Reproduction repo of "Surrogate-Gated Generation and Foundation-Model Embeddings for Bayesian Materials Design" (arXiv 2606.28578) | GP, multi-task GP, two-layer deep GP (BoTorch) on PCA 10/25/50 of mean-pooled embeddings | MACE-MP-0 medium, ORB-v3 conservative, UMA-s-1p1, SOAP baseline; all frozen. eSEN-30M-OAM is the oracle | MatterGen, CrystalFlow, ADiT, steered by full-parameter RL (MatInvent), no adapters or guidance |
| `matinvent-bo` | The working tree behind that paper: older MatInvent fork, paper sources, DFT validation, Eq-JEPA | Same, plus a heteroscedastic GP router over ORB / ALIGNN / VASP | Same | Same |
| `autoresearch-bo` | LLM-driven search over surrogate-selection policies for multi-objective BO, 18 to 22 benchmarks | 13 surrogates: gp, mtgp, dgp, mtdgp, decoupled_dgp, and mlq_{br, rf, et, gbr, xgb, lq, pbnn, tabpfn} | none in the loop | none |

## Headline numbers (as stated in the repos)

- Static benchmark, elastic, n = 500: ORB + GP at PCA50 R² = 0.803, Spearman 0.842; SOAP + GP R² = 0.445. Dielectric and phonon R² ≤ 0.34 with Spearman 0.78 to 0.82. (`matgen-BO/archive/FME_paper_refresh_v1/`)
- Closed loop, MatterGen, bulk modulus, 4 oracle calls per cycle: 4 random survivors reach 233 ± 30 GPa, 4 picked by the GP reach 314 ± 31, all survivors reach 341 ± 30 at 4.8 times the calls. (`matinvent-bo/FoundationalEmbeddings_2026/sections/results_closedloop.tex`)
- The GP ranks 1,209 unseen generated structures at Spearman 0.94, but underpredicts the top winners by about 42.5 GPa; "the seed pool, not per-cycle accumulation, makes the surrogate rank well". (`matgen-BO/02_closed_loop_bo/validation/dft_validation/insights.md` §12)
- autoresearch-bo: ten LLM-written policies win 9 of 18 benchmarks on mean hypervolume but beat the best static surrogate significantly on 0 of 18; "9 of 10 LLM strategies converged on the same prompt template". (`autoresearch-bo/autoresearch-bo/analysis/REPORT.md`, `llm/g_hypotheses.md`)

## Stated limits that a weight-level method could address

1. "All foundation model embeddings are used as frozen, pre-trained representations. Task-specific fine-tuning—even a lightweight linear probe…" (`FME_paper_refresh_v1/sections/discussion.tex:322-324`)
2. "We also do not evaluate uncertainty calibration." (`FoundationalEmbeddings_2026/sections/discussion.tex:88`)
3. "Pushing past those ceilings will require either fine-tuning the diffusion priors against the target property … or a more exploratory acquisition rule." (`discussion.tex:263`)
4. Multi-task GP with eight targets "shows negative transfer". (`discussion.tex:70`)
5. The loop GP is refit from scratch each cycle, with no transfer across properties or runs. (`matgen-BO/02_closed_loop_bo/src/calculators/local_esen_bm_gp_routed_v4.py:282-300`)
6. autoresearch-bo builds a fresh surrogate every iteration; no warm start, no transfer across benchmarks. (`bo-zoo/src/bo_zoo/runner.py:241-242`)

## Assets that already exist and cost nothing to reuse

| Asset | Where | Why it matters here |
|---|---|---|
| 59 RL-fine-tuned generator checkpoints: 3 backbones × 2 targets × 2 policies × 5 seeds, with per-cycle reward logs | Hugging Face `finetuned_diffusion/` (see `matgen-BO/02_closed_loop_bo/results/results-paper-v4/README.md:27`, `docs/EXTERNAL.md`) | A labelled zoo of task vectors (fine-tuned minus prior) for arithmetic, merging and low-rank analysis |
| 130 JSON files, 8.3 GB, of fitted surrogate parameters per (config, seed, benchmark, iteration), each pairable with hypervolume and Spearman labels | `autoresearch-bo/autoresearch-bo/results/posthoc_hyperparams/`, tidy copy `analysis/df_hyperparams.parquet`, labels `df_iter.parquet` | A labelled zoo of surrogate "weights" for weight-space learning in the broad sense |
| Unimplemented `score_log_prob` / `update_weights` hooks on the generator adapter | `matgen-BO/02_closed_loop_bo/src/diffusion/adapters/mattergen.py:94-103` | The slot where a weight edit would enter the loop |
| ORB featurizer with decoder hook | `matgen-BO/01_static_benchmark/src/common.py:292` | Imported read-only by `experiments/e1_surrogate_head/make_features.py` |
| Three interchangeable MLIP oracles (eSEN, ORB, UMA) | `matgen-BO/02_closed_loop_bo/src/phases/oracle_3way.py` | Reference behaviour for any MLIP readout edit |
| `mat-zoo-modern` conda env with `peft 0.11.1` | `autoresearch-bo/env_records/` | LoRA tooling already installed |

## Things to watch

- The phonon benchmark's feature cache is keyed only by model name, so changing a checkpoint silently serves stale vectors (`matinvent-bo/phonon_thermo_benchmark/README.md`). Any experiment that edits featurizer weights must not reuse that cache.
- Only SOAP features are cached locally; ORB embeddings have to be recomputed.
- The closed-loop code that the paper reports lives outside these three repos, in `/Volumes/SSD1_SMAAA/mbo-publish/hcap_bo` and `/Volumes/SSD1_SMAAA/matinvent-hcap-bo`. Neither was opened.
- Two files hold a plaintext Hugging Face token: `matinvent-bo/docs/plans/2026-02-28-dielectric-constant-regression.md:60` and `autoresearch-bo/autoresearch-bo/engine.py:17`. Both should be revoked and removed by the owner.
