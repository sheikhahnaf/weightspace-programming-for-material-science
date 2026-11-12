**No DFT labels (400 crystals)**

| Predictor | MAE, GPa | Bias, GPa | ρ |
|---|---|---|---|
| potential: mace | 15.4 | +5.6 | 0.962 |
| potential: orb | 13.0 | -7.7 | 0.970 |
| mean of the potentials | 10.5 | -1.1 | 0.971 |
| written network: opus (mean of 3 replies) | 26.3 | -1.8 | 0.924 |
| written network: fable (mean of 3 replies) | 24.9 | +4.4 | 0.929 |
| written network: sonnet (mean of 3 replies) | 55.3 | -50.4 | 0.894 |
| written network: haiku (mean of 3 replies) | 101.0 | +65.7 | 0.886 |
| rule: small volume per atom (rank only) |  |  | 0.739 |

**With n DFT labels: MAE in GPa (ρ)**

| Method | n = 10 | n = 20 | n = 50 | n = 100 |
|---|---|---|---|---|
| affine: mace | 15.9 (0.96) | 15.6 (0.96) | 15.0 (0.96) | 14.8 (0.96) |
| gp, prior mean mace | 17.9 (0.95) | 18.9 (0.95) | 16.1 (0.96) | 14.3 (0.96) |
| affine: orb | 11.4 (0.97) | 10.6 (0.97) | 10.0 (0.97) | 9.6 (0.97) |
| gp, prior mean orb | 12.4 (0.97) | 12.6 (0.97) | 10.9 (0.96) | 9.9 (0.97) |
| affine: written:opus__rep1 | 25.6 (0.93) | 24.4 (0.93) | 25.4 (0.93) | 26.6 (0.93) |
| gp, prior mean written:opus__rep1 | 23.1 (0.93) | 23.5 (0.93) | 18.7 (0.95) | 14.2 (0.96) |
| affine: written:fable__rep1 | 23.6 (0.93) | 22.7 (0.93) | 22.8 (0.93) | 22.2 (0.94) |
| gp, prior mean written:fable__rep1 | 21.1 (0.94) | 21.7 (0.94) | 20.1 (0.93) | 14.1 (0.96) |
| mixture of the potentials | 12.2 (0.97) | 10.6 (0.97) | 10.1 (0.97) | 9.6 (0.97) |
| gp, no prior mean | 36.0 (0.82) | 22.9 (0.92) | 18.6 (0.93) | 13.4 (0.96) |
