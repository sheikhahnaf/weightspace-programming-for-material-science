# Thermo-Calc targets: overview (16 targets)

## Ranking on the held-out half, mean Spearman ρ over targets

| Prior | Mean arm | Prior alone | 5 labels | 10 labels | 20 labels | 50 labels | 95% coverage at 5 / 10 |
|---|---|---|---|---|---|---|---|
| none | plain GP | | 0.37 | 0.56 | 0.69 | 0.81 | 0.88 / 0.77 |
| Sub-system extrapolation (no LLM) | two-stage | 0.76 | 0.71 | 0.74 | 0.78 | 0.85 | 0.74 / 0.74 |
| Sub-system extrapolation (no LLM) | learned a, b | 0.76 | 0.74 | 0.72 | 0.75 | 0.83 | 0.90 / 0.73 |
| Sub-system extrapolation (no LLM) | a, b integrated out | 0.76 | 0.74 | 0.73 | 0.76 | 0.83 | 0.90 / 0.77 |
| Opus 5.5 | two-stage | 0.73 | 0.67 | 0.72 | 0.77 | 0.84 | 0.77 / 0.74 |
| Opus 5.5 | learned a, b | 0.73 | 0.69 | 0.70 | 0.74 | 0.83 | 0.89 / 0.73 |
| Opus 5.5 | a, b integrated out | 0.73 | 0.68 | 0.70 | 0.75 | 0.83 | 0.90 / 0.77 |
| Opus 5.5 + facts | two-stage | 0.79 | 0.72 | 0.75 | 0.78 | 0.84 | 0.74 / 0.74 |
| Opus 5.5 + facts | learned a, b | 0.79 | 0.75 | 0.73 | 0.76 | 0.84 | 0.90 / 0.73 |
| Opus 5.5 + facts | a, b integrated out | 0.79 | 0.74 | 0.73 | 0.76 | 0.84 | 0.90 / 0.78 |
| Fable 5.2 | two-stage | 0.71 | 0.66 | 0.69 | 0.75 | 0.83 | 0.76 / 0.72 |
| Fable 5.2 | learned a, b | 0.71 | 0.68 | 0.68 | 0.74 | 0.83 | 0.89 / 0.73 |
| Fable 5.2 | a, b integrated out | 0.71 | 0.67 | 0.68 | 0.73 | 0.83 | 0.90 / 0.76 |
| Fable 5.2 + facts | two-stage | 0.76 | 0.69 | 0.74 | 0.76 | 0.83 | 0.75 / 0.74 |
| Fable 5.2 + facts | learned a, b | 0.76 | 0.73 | 0.71 | 0.74 | 0.83 | 0.90 / 0.74 |
| Fable 5.2 + facts | a, b integrated out | 0.76 | 0.72 | 0.72 | 0.74 | 0.83 | 0.90 / 0.78 |

## BO: area under the regret curve relative to the plain GP (20 seeds, 5 initial labels, 25 steps; two-stage arm)

Below 1 is better than the plain GP. * marks Holm-corrected p < 0.05 within the target.

| Target | Plain GP, absolute | Random | Sub-system extrapolation (no LLM) | Opus 5.5 | Opus 5.5 + facts | Fable 5.2 | Fable 5.2 + facts |
|---|---|---|---|---|---|---|---|
| `cantor_al_solidus` | 50.8 | 1.81 | 0.17* | 1.18 | 0.66 | 1.12 | 0.52 |
| `cantor_al_freezing_range` | 6.37 | 2.12 | 0.09* | 0.44* | 0.09* | 0.26* | 0.30* |
| `cantor_al_intermetallic_fraction` | 0.00968 | 1.37 | 0.74 | 0.61 | 0.89 | 0.46 | 0.47 |
| `cantor_al_main_phase_fraction` | 0.000632 | 1.36 | 0.00 | 2.32 | 0.74 | 3.22 | 1.10 |
| `ni_superalloy_solidus` | 10.7 | 3.65 | 0.00* | 0.49* | 0.38* | 0.47* | 0.17* |
| `ni_superalloy_freezing_range` | 3.45 | 2.03 | 0.59* | 0.67* | 0.60* | 0.59* | 0.57* |
| `ni_superalloy_gamma_prime_fraction` | 0.016 | 5.83 | 1.12 | 1.45 | 0.79 | 1.82* | 0.68 |
| `ni_superalloy_other_phase_fraction` | 1.72e-05 | 0.73 | 1.00 | 0.00 | 0.00 | 0.00 | 1.00 |
| `refractory_solidus` | 46.9 | 4.92 | 0.09* | 0.15* | 0.10* | 0.16* | 0.11* |
| `refractory_freezing_range` | 28.8 | 2.75 | 0.03* | 0.22* | 0.00* | 0.65* | 0.09* |
| `refractory_main_phase_fraction` | 6.82e-05 | 4.35 | 1.00 | 0.00 | 1.00 | 0.00 | 1.09 |
| `steel_solidus` | 16.2 | 2.88 | 0.10* | 0.14* | 0.00* | 0.00* | 0.00* |
| `steel_freezing_range` | 5.84 | 1.80 | 0.51* | 0.11* | 0.35* | 0.76 | 0.35* |
| `steel_austenite_fraction` | 0.00164 | 0.89 | 1.00 | 0.43 | 0.79 | 0.53 | 0.77 |
| `steel_carbide_intermetallic_fraction` | 0.000247 | 0.67 | 0.75 | 0.48 | 0.49 | 0.14 | 0.00 |

Left out, plain-GP regret is zero: refractory_intermetallic_fraction.

## BO: targets where an arm is significantly better / worse / not different from the plain GP

| Prior | two-stage | learned a, b | a, b integrated out | Median relative area (two-stage) |
|---|---|---|---|---|
| Sub-system extrapolation (no LLM) | 8 / 0 / 7 | 8 / 0 / 7 | 8 / 0 / 7 | 0.51 |
| Opus 5.5 | 7 / 0 / 8 | 7 / 0 / 8 | 7 / 0 / 8 | 0.44 |
| Opus 5.5 + facts | 7 / 0 / 8 | 8 / 0 / 7 | 7 / 0 / 8 | 0.49 |
| Fable 5.2 | 6 / 1 / 8 | 6 / 0 / 9 | 6 / 0 / 9 | 0.47 |
| Fable 5.2 + facts | 7 / 0 / 8 | 7 / 0 / 8 | 7 / 0 / 8 | 0.47 |
