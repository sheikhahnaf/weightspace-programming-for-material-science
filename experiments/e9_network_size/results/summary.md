| Task | Hidden layers | Weights | Replies (valid) | ρ, no labels | R² as written | R² rescaled | Hidden units used | GP ρ at 5 labels: plain → with the network |
|---|---|---|---|---|---|---|---|---|
| `mpea_hardness` | 16 | 385 | 3 (3) | 0.79 | 0.45 | 0.55 | 8.7 of 16 | 0.06 → 0.66 |
| `mpea_hardness` | 64 | 1,537 | 2 (2) | 0.76 | 0.38 | 0.49 | 9.5 of 64 | 0.06 → 0.46 |
| `mpea_hardness` | 32 + 32 | 1,825 | 2 (2) | 0.78 | 0.46 | 0.54 | 7.5 of 32 | 0.06 → 0.50 |
| `ti_alloy_yield_strength` | 16 | 273 | 3 (3) | 0.69 | 0.42 | 0.46 | 10.0 of 16 | 0.26 → 0.70 |
| `ti_alloy_yield_strength` | 64 | 1,089 | 2 (1) | 0.64 | 0.34 | 0.34 | 28.0 of 64 | 0.26 → 0.67 |
| `ti_alloy_yield_strength` | 32 + 32 | 1,601 | 2 (2) | 0.69 | 0.44 | 0.46 | 9.0 of 32 | 0.26 → 0.71 |
| `ni_superalloy_solidus` | 16 | 145 | 2 (2) | 0.84 | 0.62 | 0.68 | 2.5 of 16 | 0.54 → 0.83 |
| `ni_superalloy_solidus` | 64 | 577 | 2 (2) | 0.85 | 0.64 | 0.69 | 3.0 of 64 | 0.54 → 0.84 |
| `ni_superalloy_solidus` | 32 + 32 | 1,345 | 2 (2) | 0.82 | 0.61 | 0.65 | 5.0 of 32 | 0.54 → 0.81 |
| `steel_austenite_fraction` | 16 | 145 | 2 (2) | 0.76 | 0.72 | 0.77 | 14.5 of 16 | 0.23 → 0.69 |
| `steel_austenite_fraction` | 64 | 577 | 2 (2) | 0.80 | 0.83 | 0.85 | 5.5 of 64 | 0.23 → 0.45 |
| `steel_austenite_fraction` | 32 + 32 | 1,345 | 2 (2) | 0.82 | 0.75 | 0.76 | 8.0 of 32 | 0.23 → 0.68 |

Opus 5.5; means over valid replies. Units used: first-layer units with a non-zero path to the output.
