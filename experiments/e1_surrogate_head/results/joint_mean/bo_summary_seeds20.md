| Task | Prior | Plain GP | Two-stage | Joint, learned a and b | Joint, a and b integrated out | Learned vs two-stage: better / worse (Wilcoxon p) | Integrated vs two-stage |
|---|---|---|---|---|---|---|---|
| `ti_alloy_youngs_modulus` | opus | 7.9 | 5.85 | 6.78 | 6.94 | 5 / 14 (0.0586) | 6 / 13 (0.0641) |
| `ti_alloy_youngs_modulus` | fable | 7.9 | 7.16 | 6.09 | 6.62 | 11 / 7 (0.112) | 9 / 9 (0.647) |
| `ti_alloy_yield_strength` | opus | 331 | 176 | 175 | 154 | 9 / 10 (0.888) | 11 / 8 (0.0585) |
| `ti_alloy_yield_strength` | fable | 331 | 172 | 175 | 163 | 8 / 10 (0.616) | 11 / 8 (0.398) |
| `ti_alloy_hardness` | opus | 43.9 | 11.1 | 11.5 | 11.1 | 3 / 3 (0.6) | 2 / 3 (0.686) |
| `ti_alloy_hardness` | fable | 43.9 | 15 | 15.1 | 14.1 | 1 / 2 (1) | 3 / 1 (0.144) |
| `mpea_yield_strength` | opus | 799 | 922 | 964 | 923 | 6 / 10 (0.501) | 7 / 10 (0.653) |
| `mpea_yield_strength` | fable | 799 | 985 | 1e+03 | 983 | 9 / 5 (0.73) | 8 / 9 (0.831) |
| `mpea_hardness` | opus | 235 | 150 | 149 | 151 | 9 / 3 (0.209) | 8 / 4 (0.347) |
| `mpea_hardness` | fable | 235 | 133 | 133 | 130 | 4 / 2 (0.917) | 6 / 1 (0.128) |

Area under the regret curve, mean over seeds; lower is better. p values are uncorrected.
