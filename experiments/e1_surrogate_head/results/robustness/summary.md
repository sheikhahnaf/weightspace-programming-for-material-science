# Robustness checks

Written by `robustness.py`; see its docstring for what each check answers.

## Crystals, `loop_bulk_modulus`: each crystal once, starting set apart

6 runs, 3479 rows.

| Rows | Crystals | Predictor | ρ | R² as written | R² rescaled |
|---|---|---|---|---|---|
| all rows (starting set counted once per run) | 3479 | rule | 0.74 | -3.18 | 0.40 |
| all rows (starting set counted once per run) | 3479 | fable | 0.93 | 0.61 | 0.74 |
| all rows (starting set counted once per run) | 3479 | haiku | 0.84 | -2.35 | 0.65 |
| all rows (starting set counted once per run) | 3479 | opus | 0.93 | 0.64 | 0.73 |
| all rows (starting set counted once per run) | 3479 | sonnet | 0.89 | 0.20 | 0.68 |
| each crystal once | 979 | rule | 0.81 | -2.61 | 0.48 |
| each crystal once | 979 | fable | 0.94 | 0.68 | 0.78 |
| each crystal once | 979 | haiku | 0.79 | -1.80 | 0.61 |
| each crystal once | 979 | opus | 0.94 | 0.71 | 0.77 |
| each crystal once | 979 | sonnet | 0.90 | 0.26 | 0.70 |
| starting set (shared by all runs) | 500 | rule | 0.71 | -3.48 | 0.36 |
| starting set (shared by all runs) | 500 | fable | 0.92 | 0.57 | 0.72 |
| starting set (shared by all runs) | 500 | haiku | 0.85 | -2.62 | 0.67 |
| starting set (shared by all runs) | 500 | opus | 0.92 | 0.60 | 0.71 |
| starting set (shared by all runs) | 500 | sonnet | 0.88 | 0.16 | 0.68 |
| proposed by a generator and scored by the oracle (eSEN) | 416 | rule | 0.88 | -2.18 | 0.56 |
| proposed by a generator and scored by the oracle (eSEN) | 416 | fable | 0.94 | 0.77 | 0.83 |
| proposed by a generator and scored by the oracle (eSEN) | 416 | haiku | 0.71 | -1.20 | 0.54 |
| proposed by a generator and scored by the oracle (eSEN) | 416 | opus | 0.95 | 0.80 | 0.83 |
| proposed by a generator and scored by the oracle (eSEN) | 416 | sonnet | 0.90 | 0.26 | 0.73 |
| added from the seed pool during the loop | 63 | rule | 0.94 | -2.00 | 0.84 |
| added from the seed pool during the loop | 63 | fable | 0.93 | 0.70 | 0.79 |
| added from the seed pool during the loop | 63 | haiku | 0.54 | -1.93 | 0.28 |
| added from the seed pool during the loop | 63 | opus | 0.93 | 0.75 | 0.81 |
| added from the seed pool during the loop | 63 | sonnet | 0.84 | 0.26 | 0.65 |
| test rows of the task (oracle + seed pool) | 479 | rule | 0.89 | -2.13 | 0.58 |
| test rows of the task (oracle + seed pool) | 479 | fable | 0.94 | 0.77 | 0.83 |
| test rows of the task (oracle + seed pool) | 479 | haiku | 0.69 | -1.25 | 0.51 |
| test rows of the task (oracle + seed pool) | 479 | opus | 0.95 | 0.80 | 0.83 |
| test rows of the task (oracle + seed pool) | 479 | sonnet | 0.89 | 0.26 | 0.72 |

## Crystals, `loop_heat_capacity`: each crystal once, starting set apart

5 runs, 2437 rows.

| Rows | Crystals | Predictor | ρ | R² as written | R² rescaled |
|---|---|---|---|---|---|
| all rows (starting set counted once per run) | 2437 | rule | 1.00 | 0.94 | 0.98 |
| all rows (starting set counted once per run) | 2437 | fable | 1.00 | 0.96 | 0.98 |
| all rows (starting set counted once per run) | 2437 | haiku | 0.96 | -1.16 | 0.91 |
| all rows (starting set counted once per run) | 2437 | opus | 1.00 | 0.97 | 0.98 |
| all rows (starting set counted once per run) | 2437 | sonnet | 1.00 | 0.87 | 0.97 |
| each crystal once | 657 | rule | 1.00 | 0.94 | 0.98 |
| each crystal once | 657 | fable | 1.00 | 0.96 | 0.98 |
| each crystal once | 657 | haiku | 0.96 | -1.03 | 0.91 |
| each crystal once | 657 | opus | 1.00 | 0.97 | 0.98 |
| each crystal once | 657 | sonnet | 1.00 | 0.87 | 0.97 |
| starting set (shared by all runs) | 445 | rule | 1.00 | 0.94 | 0.98 |
| starting set (shared by all runs) | 445 | fable | 1.00 | 0.96 | 0.99 |
| starting set (shared by all runs) | 445 | haiku | 0.95 | -1.21 | 0.91 |
| starting set (shared by all runs) | 445 | opus | 1.00 | 0.97 | 0.98 |
| starting set (shared by all runs) | 445 | sonnet | 1.00 | 0.87 | 0.97 |
| proposed by a generator and scored by the oracle (eSEN) | 177 | rule | 1.00 | 0.93 | 0.97 |
| proposed by a generator and scored by the oracle (eSEN) | 177 | fable | 1.00 | 0.96 | 0.98 |
| proposed by a generator and scored by the oracle (eSEN) | 177 | haiku | 0.98 | -0.73 | 0.93 |
| proposed by a generator and scored by the oracle (eSEN) | 177 | opus | 1.00 | 0.97 | 0.98 |
| proposed by a generator and scored by the oracle (eSEN) | 177 | sonnet | 1.00 | 0.88 | 0.96 |
| added from the seed pool during the loop | 35 | rule | 1.00 | 0.96 | 0.99 |
| added from the seed pool during the loop | 35 | fable | 1.00 | 0.98 | 0.99 |
| added from the seed pool during the loop | 35 | haiku | 0.95 | -1.36 | 0.86 |
| added from the seed pool during the loop | 35 | opus | 1.00 | 0.97 | 0.99 |
| added from the seed pool during the loop | 35 | sonnet | 1.00 | 0.82 | 0.98 |
| test rows of the task (oracle + seed pool) | 212 | rule | 1.00 | 0.93 | 0.97 |
| test rows of the task (oracle + seed pool) | 212 | fable | 1.00 | 0.96 | 0.98 |
| test rows of the task (oracle + seed pool) | 212 | haiku | 0.98 | -0.75 | 0.93 |
| test rows of the task (oracle + seed pool) | 212 | opus | 1.00 | 0.97 | 0.98 |
| test rows of the task (oracle + seed pool) | 212 | sonnet | 1.00 | 0.88 | 0.96 |

## Screening filter: trained baselines

Trained on 400 Materials Project crystals (volume per atom 8.4 to 55.3 Å³).

**MatterGen**: 128 samples, volume per atom 7.2 to 90.6 Å³, share above 150 GPa 0.09, mean 72 GPa, best possible quarter 147 GPa.

| Scorer | ρ | Share above 150 GPa in top quarter | Mean K of top quarter (GPa) |
|---|---|---|---|
| volume rule | 0.82 | 0.38 | 133 |
| trained MLP (as in the paper) | 0.29 | 0.00 | 51 |
| ridge on log K | 0.93 | 0.34 | 139 |
| random forest | 0.92 | 0.38 | 143 |
| written, opus (mean) | 0.92 | 0.36 | 144 |
| written, fable (mean) | 0.88 | 0.38 | 143 |
| written, sonnet (mean) | 0.80 | 0.38 | 143 |
| written, haiku (mean) | 0.73 | 0.29 | 129 |

**CrystalFlow**: 128 samples, volume per atom 9.2 to 58.2 Å³, share above 150 GPa 0.16, mean 90 GPa, best possible quarter 168 GPa.

| Scorer | ρ | Share above 150 GPa in top quarter | Mean K of top quarter (GPa) |
|---|---|---|---|
| volume rule | 0.77 | 0.38 | 136 |
| trained MLP (as in the paper) | 0.12 | 0.06 | 71 |
| ridge on log K | 0.89 | 0.50 | 151 |
| random forest | 0.90 | 0.59 | 160 |
| written, opus (mean) | 0.88 | 0.52 | 151 |
| written, fable (mean) | 0.88 | 0.54 | 153 |
| written, sonnet (mean) | 0.88 | 0.56 | 156 |
| written, haiku (mean) | 0.65 | 0.46 | 141 |

## Alloys: other label-free rules (ρ over the whole pool)

| Task | rule of mixtures, melting point | rule of mixtures, shear modulus | rule of mixtures, Young's modulus | valence electron concentration (low = stronger) | atomic size mismatch | rule of mixtures used in the paper | opus | fable | sonnet | haiku |
|---|---|---|---|---|---|---|---|---|---|---|
| `ti_alloy_youngs_modulus` | -0.58 | 0.47 | 0.24 | 0.06 | 0.16 | 0.24 | 0.64 | 0.51 | 0.65 | 0.50 |
| `ti_alloy_yield_strength` | -0.39 | 0.26 | 0.23 | -0.20 | 0.62 | -0.52 | 0.69 | 0.64 | 0.45 | 0.19 |
| `ti_alloy_hardness` | -0.57 | 0.45 | 0.47 | -0.05 | 0.61 | -0.72 | 0.65 | 0.61 | 0.53 | -0.01 |
| `mpea_hardness` | -0.11 | -0.31 | -0.15 | 0.45 | 0.62 | -0.24 | 0.79 | 0.76 | 0.48 | 0.50 |
| `mpea_yield_strength` | 0.35 | -0.46 | -0.33 | 0.54 | 0.57 | 0.27 | 0.69 | 0.63 | 0.61 | 0.60 |

## Alloys: Bayesian optimization with atomic size mismatch as the prior mean

Area under the regret curve, 20 seeds, two-stage fit (lower is better).

| Task | Plain GP | Rule of mixtures | Size mismatch (seeds better / worse than GP, p) | Opus (p against size mismatch) | Fable (p against size mismatch) |
|---|---|---|---|---|---|
| `ti_alloy_youngs_modulus` | 7.68 | 7.02 | 6.95 (7 / 7, 0.64) | 5.55 (0.049) | 6.92 (0.59) |
| `ti_alloy_yield_strength` | 314 | 327 | 226 (11 / 7, 0.1) | 153 (0.018) | 148 (0.0062) |
| `ti_alloy_hardness` | 40.1 | 40.1 | 5.7 (18 / 0, 0.0002) | 5.95 (0.0052) | 10 (0.00072) |
| `mpea_hardness` | 226 | 216 | 243 (5 / 10, 0.53) | 137 (0.00062) | 120 (0.00013) |
| `mpea_yield_strength` | 772 | 676 | 890 (4 / 12, 0.13) | 900 (0.62) | 966 (0.41) |

## Crystal bulk modulus: plain GP on different inputs (ρ on generated crystals)

| Labels | embedding | embedding + descriptors, as first run | embedding + descriptors, constant column dropped | descriptors only |
|---|---|---|---|---|
| 5 | 0.15 | 0.30 | 0.23 | 0.22 |
| 10 | 0.57 | 0.37 | 0.38 | 0.36 |
| 20 | 0.82 | 0.52 | 0.60 | 0.36 |
| 50 | 0.85 | 0.48 | 0.62 | 0.57 |
| all 500 | 0.89 | 0.63 | 0.80 | 0.81 |

## Crystal bulk modulus: written mean against the plain GP, run as the unit

| Labels | Model | Fit | Plain GP ρ | With written mean ρ | Runs better | Wilcoxon p (6 runs; smallest possible 0.031) |
|---|---|---|---|---|---|---|
| 5 | opus | two_stage | 0.15 | 0.95 | 6 of 6 | 0.031 |
| 5 | opus | map | 0.15 | 0.95 | 6 of 6 | 0.031 |
| 5 | opus | marginal | 0.15 | 0.95 | 6 of 6 | 0.031 |
| 5 | fable | two_stage | 0.15 | 0.93 | 6 of 6 | 0.031 |
| 5 | fable | map | 0.15 | 0.93 | 6 of 6 | 0.031 |
| 5 | fable | marginal | 0.15 | 0.93 | 6 of 6 | 0.031 |
| 5 | sonnet | two_stage | 0.15 | 0.88 | 6 of 6 | 0.031 |
| 5 | sonnet | map | 0.15 | 0.88 | 6 of 6 | 0.031 |
| 5 | sonnet | marginal | 0.15 | 0.88 | 6 of 6 | 0.031 |
| 5 | haiku | two_stage | 0.15 | 0.66 | 6 of 6 | 0.031 |
| 5 | haiku | map | 0.15 | 0.66 | 6 of 6 | 0.031 |
| 5 | haiku | marginal | 0.15 | 0.67 | 6 of 6 | 0.031 |
| 10 | opus | two_stage | 0.57 | 0.93 | 6 of 6 | 0.031 |
| 10 | opus | map | 0.57 | 0.94 | 6 of 6 | 0.031 |
| 10 | opus | marginal | 0.57 | 0.93 | 6 of 6 | 0.031 |
| 10 | fable | two_stage | 0.57 | 0.92 | 6 of 6 | 0.031 |
| 10 | fable | map | 0.57 | 0.92 | 6 of 6 | 0.031 |
| 10 | fable | marginal | 0.57 | 0.92 | 6 of 6 | 0.031 |
| 10 | sonnet | two_stage | 0.57 | 0.88 | 6 of 6 | 0.031 |
| 10 | sonnet | map | 0.57 | 0.88 | 6 of 6 | 0.031 |
| 10 | sonnet | marginal | 0.57 | 0.89 | 6 of 6 | 0.031 |
| 10 | haiku | two_stage | 0.57 | 0.69 | 5 of 6 | 0.219 |
| 10 | haiku | map | 0.57 | 0.70 | 5 of 6 | 0.219 |
| 10 | haiku | marginal | 0.57 | 0.70 | 5 of 6 | 0.219 |
| 20 | opus | two_stage | 0.82 | 0.91 | 6 of 6 | 0.031 |
| 20 | opus | map | 0.82 | 0.90 | 6 of 6 | 0.031 |
| 20 | opus | marginal | 0.82 | 0.90 | 6 of 6 | 0.031 |
| 20 | fable | two_stage | 0.82 | 0.89 | 6 of 6 | 0.031 |
| 20 | fable | map | 0.82 | 0.90 | 6 of 6 | 0.031 |
| 20 | fable | marginal | 0.82 | 0.90 | 6 of 6 | 0.031 |
| 20 | sonnet | two_stage | 0.82 | 0.88 | 5 of 6 | 0.062 |
| 20 | sonnet | map | 0.82 | 0.90 | 6 of 6 | 0.031 |
| 20 | sonnet | marginal | 0.82 | 0.92 | 6 of 6 | 0.031 |
| 20 | haiku | two_stage | 0.82 | 0.75 | 1 of 6 | 0.156 |
| 20 | haiku | map | 0.82 | 0.79 | 3 of 6 | 0.562 |
| 20 | haiku | marginal | 0.82 | 0.82 | 4 of 6 | 1.000 |

## Thermo-Calc optimization: targets significantly better / worse than the plain GP, by correction (35 targets)

| Prior mean | Uncorrected | Holm within target (as reported) | Holm across targets | Holm across all tests |
|---|---|---|---|---|
| subsystem_extrapolation | 21 / 1 | 18 / 0 | 18 / 0 | 17 / 0 |
| select_opus | 21 / 1 | 16 / 0 | 15 / 0 | 13 / 0 |
| select_opus_pd | 20 / 0 | 18 / 0 | 18 / 0 | 14 / 0 |
| select_fable | 20 / 1 | 15 / 1 | 13 / 1 | 11 / 0 |
| select_fable_pd | 21 / 0 | 16 / 0 | 15 / 0 | 15 / 0 |

## Alloy optimization: tasks significantly better than the plain GP

| Prior mean | Holm within task (as reported) | Holm across the five tasks |
|---|---|---|
| handbook | 0 | 0 |
| select_opus | 4 | 4 |
| select_fable | 3 | 3 |

## Phase fractions: written networks against the sub-system extrapolation, paired over targets

| Model | Targets | Mean ρ written | Mean ρ extrapolation | Targets where written is ahead | Wilcoxon p |
|---|---|---|---|---|---|
| opus | 16 | 0.69 | 0.63 | 7 | 0.50 |
| fable | 16 | 0.67 | 0.63 | 9 | 0.60 |
| opus + facts | 16 | 0.71 | 0.63 | 10 | 0.19 |
| fable + facts | 16 | 0.68 | 0.63 | 9 | 0.35 |
