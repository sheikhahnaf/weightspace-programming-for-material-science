# E9: does the size of the written network matter?

The networks of the main study have one hidden layer of 16 units (113 to 417 weights). The original weight-space programming work wrote networks of about 20,500 weights in one reply. This experiment asks whether a larger written network is a better predictor.

- Same write prompt as E1 and E7 with only the architecture changed: one hidden layer of 64 units, or two hidden layers of 32 (577 to 1,825 weights).
- Four tasks: MPEA hardness, Ti alloy yield strength (measured); Ni superalloy solidus, steel austenite fraction (Thermo-Calc, no facts).
- Opus 5.5 only, two replies per task and size; the 16-unit Opus replies of E1 and E7 are the reference.
- `size_arm.py prompt` writes the run folders, `size_arm.py score` writes `results/summary.md`.

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

- Ranking with no labels is within 0.05 of the 16-unit networks on three tasks and a little higher on steel austenite fraction (0.80 and 0.82 against 0.76).
- The extra capacity is not used: with 64 units, six of seven valid replies give 3 to 10 units a path to the output.
- One of 16 larger replies was malformed (a 64-unit bias written with 65 numbers).
- As a two-stage GP mean at 5 labels the 64-unit networks are worse on two tasks; with two replies per cell this is not established.

**Status (2026-11-12).** 16 replies collected and scored; all sessions pass the tool-use audit. No BO, no crystal task, no other model.
