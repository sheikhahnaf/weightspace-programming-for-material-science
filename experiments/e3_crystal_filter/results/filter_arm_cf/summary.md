**bulk modulus (GPa); a hit is a crystal above 150; the filter keeps the top quarter**

| Scorer | Replies | Base samples: ρ | mean of all → kept (best possible) | hit share all → kept | oracle calls to half the hits (random) | All variants: ρ | mean all → kept |
|---|---|---|---|---|---|---|---|
| rule: small volume per atom | 1 | 0.77 | 90.1 → 136 (168) | 0.16 → 0.38 | 28 (59) | 0.74 | 92.2 → 129 |
| MLP trained on 400 MP structures | 1 | 0.88 | 90.1 → 153 (168) | 0.16 → 0.53 | 13 (59) | 0.88 | 92.2 → 152 |
| claude-fable-5-2 | 3 | 0.88 | 90.1 → 153 (168) | 0.16 → 0.54 | 18 (59) | 0.87 | 92.2 → 151 |
| claude-haiku-5-5 | 3 | 0.65 | 90.1 → 141 (168) | 0.16 → 0.46 | 11 (59) | 0.64 | 92.2 → 142 |
| claude-opus-5-5 | 3 | 0.88 | 90.1 → 151 (168) | 0.16 → 0.52 | 17 (59) | 0.87 | 92.2 → 146 |
| claude-sonnet-5-5 | 3 | 0.88 | 90.1 → 156 (168) | 0.16 → 0.56 | 17 (59) | 0.87 | 92.2 → 154 |

**heat capacity at 300 K per gram (J/g/K); a hit is a crystal above 0.4; the filter keeps the top quarter**

| Scorer | Replies | Base samples: ρ | mean of all → kept (best possible) | hit share all → kept | oracle calls to half the hits (random) | All variants: ρ | mean all → kept |
|---|---|---|---|---|---|---|---|
| rule: Dulong-Petit, 1 / mean atomic mass | 1 | 1.00 | 0.291 → 0.477 (0.478) | 0.18 → 0.73 | 4 (20) | 1.00 | 0.299 → 0.513 |
| claude-fable-5-2 | 2 | 1.00 | 0.291 → 0.477 (0.478) | 0.18 → 0.73 | 4 (20) | 1.00 | 0.299 → 0.514 |
| claude-haiku-5-5 | 1 | 0.97 | 0.291 → 0.466 (0.478) | 0.18 → 0.73 | 4 (20) | 0.98 | 0.299 → 0.502 |
| claude-opus-5-5 | 2 | 1.00 | 0.291 → 0.477 (0.478) | 0.18 → 0.73 | 4 (20) | 1.00 | 0.299 → 0.513 |
| claude-sonnet-5-5 | 1 | 1.00 | 0.291 → 0.477 (0.478) | 0.18 → 0.73 | 4 (20) | 1.00 | 0.299 → 0.513 |

