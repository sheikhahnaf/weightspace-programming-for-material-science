# Thermo-Calc targets: overview (35 targets)

## Ranking on the held-out half, mean Spearman ρ over targets

| Prior | Mean arm | Prior alone | 5 labels | 10 labels | 20 labels | 50 labels | 95% coverage at 5 / 10 |
|---|---|---|---|---|---|---|---|
| none | plain GP | | 0.37 | 0.56 | 0.69 | 0.82 | 0.86 / 0.78 |
| Sub-system extrapolation (no LLM) | two-stage | 0.70 | 0.66 | 0.72 | 0.76 | 0.84 | 0.75 / 0.74 |
| Sub-system extrapolation (no LLM) | learned a, b | 0.70 | 0.68 | 0.70 | 0.74 | 0.83 | 0.89 / 0.73 |
| Sub-system extrapolation (no LLM) | a, b integrated out | 0.70 | 0.68 | 0.71 | 0.75 | 0.83 | 0.90 / 0.78 |
| Opus 5.5 | two-stage | 0.67 | 0.61 | 0.68 | 0.75 | 0.83 | 0.74 / 0.74 |
| Opus 5.5 | learned a, b | 0.67 | 0.64 | 0.66 | 0.74 | 0.83 | 0.87 / 0.74 |
| Opus 5.5 | a, b integrated out | 0.67 | 0.64 | 0.67 | 0.74 | 0.83 | 0.88 / 0.77 |
| Opus 5.5 + facts | two-stage | 0.73 | 0.67 | 0.72 | 0.76 | 0.84 | 0.71 / 0.75 |
| Opus 5.5 + facts | learned a, b | 0.73 | 0.69 | 0.70 | 0.75 | 0.83 | 0.87 / 0.74 |
| Opus 5.5 + facts | a, b integrated out | 0.73 | 0.69 | 0.71 | 0.75 | 0.83 | 0.89 / 0.78 |
| Fable 5.2 | two-stage | 0.64 | 0.60 | 0.65 | 0.73 | 0.83 | 0.74 / 0.73 |
| Fable 5.2 | learned a, b | 0.64 | 0.62 | 0.64 | 0.73 | 0.83 | 0.86 / 0.74 |
| Fable 5.2 | a, b integrated out | 0.64 | 0.62 | 0.65 | 0.73 | 0.83 | 0.87 / 0.76 |
| Fable 5.2 + facts | two-stage | 0.71 | 0.67 | 0.71 | 0.75 | 0.83 | 0.75 / 0.75 |
| Fable 5.2 + facts | learned a, b | 0.71 | 0.69 | 0.69 | 0.74 | 0.83 | 0.88 / 0.74 |
| Fable 5.2 + facts | a, b integrated out | 0.71 | 0.68 | 0.70 | 0.74 | 0.83 | 0.89 / 0.78 |

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
| `ti_alloy_solidus` | 27.2 | 2.67 | 0.00* | 0.48* | 0.00* | 0.25* | 0.00* |
| `ti_alloy_freezing_range` | 5.63 | 4.45 | 0.08* | 0.07* | 0.11* | 0.19* | 0.11* |
| `ti_alloy_alpha_transus` | 9.33 | 1.60 | 1.17 | 0.68 | 1.20 | 0.74 | 1.06 |
| `ti_alloy_intermetallic_fraction` | 2.52e-05 | 7.00 | 0.00 | 0.00 | 3.00 | 0.00 | 0.00 |
| `refractory_solidus` | 46.9 | 4.92 | 0.09* | 0.15* | 0.10* | 0.16* | 0.11* |
| `refractory_freezing_range` | 28.8 | 2.75 | 0.03* | 0.22* | 0.00* | 0.65* | 0.09* |
| `refractory_main_phase_fraction` | 6.82e-05 | 4.35 | 1.00 | 0.00 | 1.00 | 0.00 | 1.09 |
| `steel_solidus` | 16.2 | 2.88 | 0.10* | 0.14* | 0.00* | 0.00* | 0.00* |
| `steel_freezing_range` | 5.84 | 1.80 | 0.51* | 0.11* | 0.35* | 0.76 | 0.35* |
| `steel_austenite_fraction` | 0.00164 | 0.89 | 1.00 | 0.43 | 0.79 | 0.53 | 0.77 |
| `steel_carbide_intermetallic_fraction` | 0.000247 | 0.67 | 0.75 | 0.48 | 0.49 | 0.14 | 0.00 |
| `al_alloy_solidus` | 10.8 | 2.98 | 0.00* | 0.00* | 0.00* | 0.19* | 0.04* |
| `al_alloy_freezing_range` | 13.2 | 2.21 | 0.04* | 0.00* | 0.00* | 0.00* | 0.01* |
| `al_alloy_second_phase_fraction` | 0.0043 | 8.28 | 0.88 | 0.00* | 0.02* | 0.03* | 0.02* |
| `hf_refractory_solidus` | 26.7 | 4.78 | 0.04* | 0.21* | 0.05* | 0.35* | 0.22* |
| `hf_refractory_freezing_range` | 8.37 | 3.73 | 0.17* | 0.86 | 0.16* | 0.89 | 0.59 |
| `hf_refractory_main_phase_fraction` | 0.000667 | 0.00 | 0.63 | 1.11 | 0.35 | 0.00 | 0.63 |
| `cu_ti_3d_solidus` | 174 | 1.24 | 0.05* | 0.03* | 0.07* | 0.04* | 0.01* |
| `cu_ti_3d_freezing_range` | 32.7 | 1.39 | 0.69 | 0.44* | 0.71 | 0.76 | 0.62 |
| `cu_ti_3d_intermetallic_fraction` | 0.00317 | 6.03 | 0.01 | 0.00 | 0.24 | 0.03 | 0.03 |
| `cu_ti_3d_main_phase_fraction` | 0.0437 | 2.89 | 0.62* | 0.59 | 0.32* | 0.39* | 0.61 |
| `al_refractory_solidus` | 58.6 | 2.99 | 0.00* | 0.65 | 0.15* | 0.61 | 0.21* |
| `al_refractory_freezing_range` | 23.5 | 1.55 | 1.19 | 0.88 | 1.12 | 0.99 | 0.93 |
| `al_refractory_intermetallic_fraction` | 0.023 | 1.92 | 0.02* | 0.29* | 0.01* | 0.29* | 0.48* |
| `al_refractory_main_phase_fraction` | 0.0118 | 1.43 | 0.26 | 0.32 | 0.20 | 0.71 | 0.50 |

Left out, plain-GP regret is zero: ti_alloy_alpha_fraction, refractory_intermetallic_fraction.

## BO: targets where an arm is significantly better / worse / not different from the plain GP

| Prior | two-stage | learned a, b | a, b integrated out | Median relative area (two-stage) |
|---|---|---|---|---|
| Sub-system extrapolation (no LLM) | 18 / 0 / 15 | 19 / 0 / 14 | 19 / 0 / 14 | 0.17 |
| Opus 5.5 | 16 / 0 / 17 | 14 / 0 / 19 | 17 / 0 / 16 | 0.43 |
| Opus 5.5 + facts | 18 / 0 / 15 | 19 / 0 / 14 | 18 / 0 / 15 | 0.24 |
| Fable 5.2 | 15 / 1 / 17 | 15 / 0 / 18 | 15 / 0 / 18 | 0.35 |
| Fable 5.2 + facts | 16 / 0 / 17 | 16 / 0 / 17 | 16 / 0 / 17 | 0.35 |
