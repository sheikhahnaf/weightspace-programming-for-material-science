| Task | Arm | Candidates | Regret after 5 | after 10 | after 25 | Area under regret | vs GP: seeds better / worse | Wilcoxon p (Holm) | Steps with a prior |
|---|---|---|---|---|---|---|---|---|---|
| `ti_alloy_youngs_modulus` (GPa) | random |  | 11.2 | 8.54 | 5.5 | 8.37 ± 0.86 | 8 / 10 |  | 0.00 |
| `ti_alloy_youngs_modulus` (GPa) | gp |  | 8.9 | 8.11 | 5.59 | 7.68 ± 0.67 |  |  | 0.00 |
| `ti_alloy_youngs_modulus` (GPa) | handbook | 1 | 8.55 | 7.29 | 5.23 | 7.02 ± 0.77 | 9 / 8 | 0.298 (1) | 0.30 |
| `ti_alloy_youngs_modulus` (GPa) | select_fable | 3 | 9.66 | 7.45 | 3.54 | 6.92 ± 0.93 | 12 / 6 | 0.327 (1) | 0.93 |
| `ti_alloy_youngs_modulus` (GPa) | select_opus | 3 | 9.07 | 6.38 | 1.61 | 5.55 ± 0.67 | 16 / 3 | 0.000837 (0.00434) | 1.00 |
| `ti_alloy_youngs_modulus` (GPa) | select_sonnet | 3 | 9.37 | 7.65 | 4.93 | 7.34 ± 0.68 | 10 / 7 | 0.478 (1) | 0.04 |
| `ti_alloy_youngs_modulus` (GPa) | select_haiku | 2 | 9.75 | 7.6 | 4.74 | 7.61 ± 0.69 | 10 / 9 | 0.984 (1) | 0.28 |
| `ti_alloy_youngs_modulus` (GPa) | select_all | 11 | 8.95 | 6.38 | 1.55 | 5.41 ± 0.61 | 17 / 2 | 0.000724 (0.00434) | 1.00 |
| `ti_alloy_yield_strength` (MPa) | random |  | 539 | 368 | 229 | 392 ± 50 | 8 / 11 |  | 0.00 |
| `ti_alloy_yield_strength` (MPa) | gp |  | 479 | 324 | 114 | 314 ± 61 |  |  | 0.00 |
| `ti_alloy_yield_strength` (MPa) | handbook | 1 | 495 | 348 | 114 | 327 ± 61 | 0 / 2 | 0.18 (0.359) | 0.06 |
| `ti_alloy_yield_strength` (MPa) | select_fable | 3 | 317 | 164 | 0 | 148 ± 21 | 15 / 4 | 0.00427 (0.0256) | 0.97 |
| `ti_alloy_yield_strength` (MPa) | select_opus | 3 | 331 | 114 | 17 | 153 ± 18 | 12 / 7 | 0.0158 (0.0473) | 0.99 |
| `ti_alloy_yield_strength` (MPa) | select_sonnet | 3 | 358 | 211 | 51.9 | 216 ± 53 | 13 / 5 | 0.0108 (0.0434) | 0.83 |
| `ti_alloy_yield_strength` (MPa) | select_haiku | 3 | 463 | 220 | 85.4 | 255 ± 55 | 9 / 7 | 0.352 (0.359) | 0.61 |
| `ti_alloy_yield_strength` (MPa) | select_all | 12 | 335 | 124 | 9 | 139 ± 20 | 15 / 4 | 0.00427 (0.0256) | 0.99 |
| `ti_alloy_hardness` (HV) | random |  | 103 | 63.8 | 35.4 | 66.9 ± 10 | 3 / 14 |  | 0.00 |
| `ti_alloy_hardness` (HV) | gp |  | 81.8 | 41 | 1.6 | 40.1 ± 7 |  |  | 0.00 |
| `ti_alloy_hardness` (HV) | handbook | 1 | 81.8 | 41 | 1.6 | 40.1 ± 7 | 0 / 0 | 1 (1) | 0.00 |
| `ti_alloy_hardness` (HV) | select_fable | 3 | 13 | 2 | 2 | 10 ± 2.7 | 15 / 1 | 0.00053 (0.00265) | 0.99 |
| `ti_alloy_hardness` (HV) | select_opus | 3 | 2 | 2 | 2 | 5.95 ± 0.61 | 15 / 1 | 0.000531 (0.00265) | 1.00 |
| `ti_alloy_hardness` (HV) | select_sonnet | 2 | 13.6 | 5.95 | 2 | 11.3 ± 4.1 | 14 / 2 | 0.000776 (0.00265) | 0.97 |
| `ti_alloy_hardness` (HV) | select_haiku | 3 | 67 | 22.6 | 1.7 | 27.2 ± 4.8 | 8 / 6 | 0.048 (0.096) | 0.79 |
| `ti_alloy_hardness` (HV) | select_all | 11 | 7.5 | 2 | 1.9 | 6.13 ± 1 | 16 / 0 | 0.000437 (0.00262) | 1.00 |
| `mpea_yield_strength` (MPa) | random |  | 1.24e+03 | 1.03e+03 | 790 | 1.01e+03 ± 1.2e+02 | 3 / 16 |  | 0.00 |
| `mpea_yield_strength` (MPa) | gp |  | 1.14e+03 | 753 | 522 | 772 ± 1.1e+02 |  |  | 0.00 |
| `mpea_yield_strength` (MPa) | handbook | 1 | 1.06e+03 | 676 | 246 | 676 ± 1.1e+02 | 10 / 8 | 0.157 (0.314) | 0.60 |
| `mpea_yield_strength` (MPa) | select_fable | 3 | 1.18e+03 | 1.02e+03 | 698 | 966 ± 1.3e+02 | 4 / 14 | 0.0176 (0.106) | 0.68 |
| `mpea_yield_strength` (MPa) | select_opus | 3 | 1.12e+03 | 988 | 499 | 900 ± 1.1e+02 | 4 / 14 | 0.0328 (0.149) | 0.89 |
| `mpea_yield_strength` (MPa) | select_sonnet | 2 | 1.17e+03 | 750 | 249 | 735 ± 1e+02 | 9 / 8 | 0.619 (0.619) | 0.86 |
| `mpea_yield_strength` (MPa) | select_haiku | 3 | 1.1e+03 | 665 | 157 | 641 ± 1.1e+02 | 12 / 5 | 0.0395 (0.149) | 0.84 |
| `mpea_yield_strength` (MPa) | select_all | 11 | 1.17e+03 | 1.07e+03 | 588 | 935 ± 1.2e+02 | 4 / 15 | 0.0298 (0.149) | 0.98 |
| `mpea_hardness` (HV) | random |  | 387 | 343 | 251 | 338 ± 22 | 3 / 17 |  | 0.00 |
| `mpea_hardness` (HV) | gp |  | 296 | 227 | 112 | 226 ± 24 |  |  | 0.00 |
| `mpea_hardness` (HV) | handbook | 1 | 291 | 219 | 123 | 216 ± 23 | 3 / 1 | 0.465 (0.553) | 0.08 |
| `mpea_hardness` (HV) | select_fable | 3 | 118 | 109 | 99 | 120 ± 4.5 | 16 / 3 | 0.00112 (0.0061) | 0.99 |
| `mpea_hardness` (HV) | select_opus | 3 | 178 | 99 | 94 | 137 ± 5.5 | 16 / 4 | 0.00102 (0.0061) | 1.00 |
| `mpea_hardness` (HV) | select_sonnet | 3 | 293 | 248 | 147 | 247 ± 27 | 5 / 10 | 0.233 (0.553) | 0.40 |
| `mpea_hardness` (HV) | select_haiku | 3 | 350 | 280 | 140 | 259 ± 22 | 6 / 13 | 0.184 (0.553) | 0.68 |
| `mpea_hardness` (HV) | select_all | 12 | 203 | 124 | 99 | 144 ± 8 | 16 / 3 | 0.00254 (0.0102) | 1.00 |
