| Task | Arm | Candidates | Regret after 5 | after 10 | after 25 | Area under regret | vs GP: seeds better / worse | Wilcoxon p (Holm) | Steps with a prior |
|---|---|---|---|---|---|---|---|---|---|
| `ti_alloy_youngs_modulus` (GPa) | random |  | 10.5 | 7.5 | 7.5 | 10.6 ± 4.6 | 1 / 1 |  | 0.00 |
| `ti_alloy_youngs_modulus` (GPa) | gp |  | 10.6 | 10.6 | 10.6 | 11.4 ± 2.8 |  |  | 0.00 |
| `ti_alloy_youngs_modulus` (GPa) | handbook | 1 | 10.6 | 6.05 | 6.05 | 9.54 ± 1.1 | 2 / 0 | 0.5 (1) | 0.15 |
| `ti_alloy_youngs_modulus` (GPa) | select_fable | 3 | 11.5 | 11.5 | 11.5 | 12 ± 2 | 1 / 1 | 1 (1) | 1.00 |
| `ti_alloy_youngs_modulus` (GPa) | select_opus | 3 | 12.6 | 6.4 | 6.4 | 10.8 ± 3.7 | 1 / 1 | 1 (1) | 1.00 |
| `ti_alloy_youngs_modulus` (GPa) | select_sonnet | 3 | 9.05 | 7.55 | 7.55 | 9.73 ± 1.1 | 1 / 0 | 1 (1) | 0.05 |
| `ti_alloy_youngs_modulus` (GPa) | select_haiku | 2 | 12.6 | 9.05 | 9.05 | 11.8 ± 3.2 | 0 / 1 | 1 (1) | 0.70 |
| `ti_alloy_youngs_modulus` (GPa) | select_all | 11 | 13.5 | 7.5 | 7.5 | 11.1 ± 1.1 | 1 / 1 | 1 (1) | 1.00 |
| `ti_alloy_yield_strength` (MPa) | random |  | 521 | 521 | 521 | 521 ± 2.2e+02 | 0 / 2 |  | 0.00 |
| `ti_alloy_yield_strength` (MPa) | gp |  | 90 | 0 | 0 | 164 ± 74 |  |  | 0.00 |
| `ti_alloy_yield_strength` (MPa) | handbook | 1 | 90 | 0 | 0 | 164 ± 74 | 0 / 0 | 1 (1) | 0.00 |
| `ti_alloy_yield_strength` (MPa) | select_fable | 3 | 180 | 90 | 90 | 135 ± 45 | 1 / 1 | 1 (1) | 1.00 |
| `ti_alloy_yield_strength` (MPa) | select_opus | 3 | 386 | 85 | 85 | 328 ± 1.5e+02 | 0 / 2 | 0.5 (1) | 1.00 |
| `ti_alloy_yield_strength` (MPa) | select_sonnet | 3 | 90 | 0 | 0 | 158 ± 1 | 1 / 1 | 1 (1) | 1.00 |
| `ti_alloy_yield_strength` (MPa) | select_haiku | 3 | 90 | 0 | 0 | 151 ± 7.3 | 1 / 1 | 1 (1) | 0.90 |
| `ti_alloy_yield_strength` (MPa) | select_all | 12 | 180 | 90 | 90 | 135 ± 45 | 1 / 1 | 1 (1) | 1.00 |
| `ti_alloy_hardness` (HV) | random |  | 18.5 | 18.5 | 18.5 | 22.1 ± 20 | 0 / 1 |  | 0.00 |
| `ti_alloy_hardness` (HV) | gp |  | 2 | 2 | 2 | 17.5 ± 15 |  |  | 0.00 |
| `ti_alloy_hardness` (HV) | handbook | 1 | 2 | 2 | 2 | 17.5 ± 15 | 0 / 0 | 1 (1) | 0.00 |
| `ti_alloy_hardness` (HV) | select_fable | 3 | 2 | 2 | 2 | 7.5 ± 5.5 | 1 / 0 | 1 (1) | 1.00 |
| `ti_alloy_hardness` (HV) | select_opus | 3 | 2 | 2 | 2 | 7.5 ± 5.5 | 1 / 0 | 1 (1) | 1.00 |
| `ti_alloy_hardness` (HV) | select_sonnet | 2 | 2 | 2 | 2 | 7.5 ± 5.5 | 1 / 0 | 1 (1) | 1.00 |
| `ti_alloy_hardness` (HV) | select_haiku | 3 | 2 | 2 | 2 | 18.5 ± 16 | 0 / 1 | 1 (1) | 1.00 |
| `ti_alloy_hardness` (HV) | select_all | 11 | 2 | 2 | 2 | 7.5 ± 5.5 | 1 / 0 | 1 (1) | 1.00 |
| `mpea_yield_strength` (MPa) | random |  | 818 | 818 | 818 | 818 ± 8.1e+02 | 0 / 2 |  | 0.00 |
| `mpea_yield_strength` (MPa) | gp |  | 470 | 466 | 466 | 538 ± 5.3e+02 |  |  | 0.00 |
| `mpea_yield_strength` (MPa) | handbook | 1 | 466 | 466 | 466 | 555 ± 5.5e+02 | 1 / 1 | 1 (1) | 0.35 |
| `mpea_yield_strength` (MPa) | select_fable | 3 | 641 | 466 | 466 | 555 ± 5.5e+02 | 1 / 1 | 1 (1) | 0.40 |
| `mpea_yield_strength` (MPa) | select_opus | 3 | 644 | 466 | 466 | 590 ± 5.9e+02 | 1 / 1 | 1 (1) | 0.75 |
| `mpea_yield_strength` (MPa) | select_sonnet | 2 | 466 | 466 | 466 | 537 ± 5.4e+02 | 1 / 0 | 1 (1) | 0.65 |
| `mpea_yield_strength` (MPa) | select_haiku | 3 | 466 | 466 | 466 | 537 ± 5.4e+02 | 1 / 0 | 1 (1) | 0.60 |
| `mpea_yield_strength` (MPa) | select_all | 11 | 641 | 466 | 466 | 590 ± 5.9e+02 | 1 / 1 | 1 (1) | 1.00 |
| `mpea_hardness` (HV) | random |  | 422 | 422 | 422 | 437 ± 1.4e+02 | 0 / 1 |  | 0.00 |
| `mpea_hardness` (HV) | gp |  | 374 | 318 | 318 | 376 ± 76 |  |  | 0.00 |
| `mpea_hardness` (HV) | handbook | 1 | 374 | 206 | 206 | 323 ± 23 | 1 / 0 | 1 (1) | 0.50 |
| `mpea_hardness` (HV) | select_fable | 3 | 200 | 200 | 200 | 235 ± 65 | 1 / 0 | 1 (1) | 1.00 |
| `mpea_hardness` (HV) | select_opus | 3 | 258 | 99 | 99 | 186 ± 87 | 2 / 0 | 0.5 (1) | 0.95 |
| `mpea_hardness` (HV) | select_sonnet | 3 | 400 | 400 | 400 | 409 ± 1.1e+02 | 0 / 1 | 1 (1) | 0.55 |
| `mpea_hardness` (HV) | select_haiku | 3 | 384 | 352 | 352 | 381 ± 81 | 0 / 1 | 1 (1) | 0.85 |
| `mpea_hardness` (HV) | select_all | 12 | 289 | 200 | 200 | 262 ± 38 | 1 / 0 | 1 (1) | 1.00 |
