**bulk modulus (GPa); a hit is a crystal above 150; the filter keeps the top quarter**

| Scorer | Replies | Base samples: ρ | mean of all → kept (best possible) | hit share all → kept | oracle calls to half the hits (random) | All variants: ρ | mean all → kept |
|---|---|---|---|---|---|---|---|
| rule: small volume per atom | 1 | 0.82 | 71.6 → 133 (147) | 0.09 → 0.38 | 10 (60) | 0.85 | 95.5 → 164 |
| MLP trained on 400 MP structures | 1 | 0.29 | 71.6 → 51.2 (147) | 0.09 → 0.00 | 60 (60) | 0.27 | 95.5 → 74.3 |
| claude-fable-5-2 | 2 | 0.89 | 71.6 → 143 (147) | 0.09 → 0.38 | 7 (60) | 0.94 | 95.5 → 183 |
| claude-haiku-5-5 | 3 | 0.73 | 71.6 → 129 (147) | 0.09 → 0.29 | 9 (60) | 0.74 | 95.5 → 166 |
| claude-sonnet-5-5 | 3 | 0.80 | 71.6 → 143 (147) | 0.09 → 0.38 | 7 (60) | 0.89 | 95.5 → 179 |

**heat capacity at 300 K per gram (J/g/K); a hit is a crystal above 0.4; the filter keeps the top quarter**

| Scorer | Replies | Base samples: ρ | mean of all → kept (best possible) | hit share all → kept | oracle calls to half the hits (random) | All variants: ρ | mean all → kept |
|---|---|---|---|---|---|---|---|
| rule: Dulong-Petit, 1 / mean atomic mass | 1 | 1.00 | 0.263 → 0.44 (0.441) | 0.07 → 0.29 | 2 (23) | 1.00 | 0.277 → 0.483 |
| claude-fable-5-2 | 2 | 1.00 | 0.263 → 0.44 (0.441) | 0.07 → 0.29 | 2 (23) | 1.00 | 0.277 → 0.484 |
| claude-haiku-5-5 | 1 | 0.98 | 0.263 → 0.434 (0.441) | 0.07 → 0.29 | 2 (23) | 0.98 | 0.277 → 0.478 |
| claude-sonnet-5-5 | 1 | 1.00 | 0.263 → 0.44 (0.441) | 0.07 → 0.29 | 2 (23) | 1.00 | 0.277 → 0.483 |

