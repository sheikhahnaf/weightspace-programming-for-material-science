# Thermo-Calc-computed alloy pools (experiment E7)

Built by `experiments/e7_calphad_prior/make_tc_data.py`; nothing here was copied from a sibling repo.
This file is rewritten by `--stage export`; it describes what is on disk now.

- Software: Thermo-Calc 2025b through TC-Python 2025.2.30, on this machine.
- Databases: TCHEA8, TCNI12, TCTI6, TCFE10, TCAL9 as shipped with Thermo-Calc 2025b. The minor version of a database is not exposed by TC-Python and is not recorded.
- Last calculation: 2026-11-12.
- Conditions: 101325 Pa, one mole of atoms, global minimisation, default phases of the database for the elements present, **gas phase removed** (with it, Mn-bearing melts boil below 3,100 K and no liquidus exists in the sense meant here).
- Each composition is calculated in the system of its present elements only.
- Sampling: all compositions allowed by a system's rule were enumerated and its pool drawn without replacement with `numpy.random.default_rng(0)`.

## Systems

| System | Database | Elements | Fixed T, K | Sampling rule | Pool | Status |
|---|---|---|---|---|---|---|
| `cantor_al` | TCHEA8 | Al-Co-Cr-Fe-Mn-Ni | 1273 | every element between 0 and 35 at.% on a 5 at.% grid, at least four elements present | 400 | complete |
| `ni_superalloy` | TCNI12 | Ni-Al-Co-Cr-Mo-Ti-W | 1173 | Ni is the balance and at least 50 at.%; solutes in at.%: Al 0 to 12 (step 2), Co 0 to 20 (step 5), Cr 0 to 20 (step 5), Mo 0 to 6 (step 2), Ti 0 to 6 (step 2), W 0 to 6 (step 2); at least 4 elements present | 250 | complete |
| `ti_alloy` | TCTI6 | Ti-Al-Mo-Nb-Sn-V-Zr | 973 | Ti is the balance and at least 60 at.%; solutes in at.%: Al 0 to 12 (step 3), Mo 0 to 9 (step 3), Nb 0 to 12 (step 3), Sn 0 to 4 (step 2), V 0 to 12 (step 3), Zr 0 to 8 (step 4); at least 4 elements present | 200 | **in progress**: 120 of 200 rows, facts 43 of 43 |
| `refractory` | TCHEA8 | Mo-Nb-Ta-Ti-V-W-Zr | 1473 | every element between 0 and 35 at.% on a 5 at.% grid, at least four elements present | 200 | complete |
| `steel` | TCFE10 | Fe-Al-C-Cr-Mn-Mo-Ni | 1173 | Fe is the balance and at least 50 at.%; solutes in at.%: Al 0 to 6 (step 3), C 0 to 2 (step 1), Cr 0 to 24 (step 4), Mn 0 to 20 (step 5), Mo 0 to 4 (step 2), Ni 0 to 20 (step 4); at least 4 elements present | 200 | complete |
| `cu_ti_3d` | TCHEA8 | Co-Cr-Cu-Fe-Ni-Ti | 1173 | every element between 0 and 35 at.% on a 5 at.% grid, at least four elements present | 200 | **in progress**: 19 of 200 rows, facts 71 of 71 |

Not started yet: `al_alloy`, `hf_refractory`, `al_refractory`.

## Targets

A target is dropped (not registered as a task) when more than 80% of the pool has the same value or it computed for fewer than 90% of the rows.

| System | Target | Unit | Goal in BO | Rows | Min | Median | Max | Share at the most common value | Dropped |
|---|---|---|---|---|---|---|---|---|---|
| `cantor_al` | `solidus`: equilibrium solidus temperature | K | maximise | 400 | 1415 | 1618 | 1832 | 0.01 |  |
| `cantor_al` | `freezing_range`: equilibrium freezing range (liquidus temperature minus solidus temperature) | K | minimise | 400 | 1.7 | 71.95 | 319.8 | 0.01 |  |
| `cantor_al` | `intermetallic_fraction`: equilibrium mole fraction, at 1273 K, of all phases other than liquid and the disordered fcc, bcc and hcp solid solutions (that is: sigma, Laves and other intermetallic phases, and ordered B2 or L12) | mole | minimise | 397 | 0 | 0.593 | 1 | 0.16 |  |
| `cantor_al` | `main_phase_fraction`: equilibrium mole fraction, at 1273 K, of the single most abundant phase (1 for a single-phase alloy; two bcc phases of a miscibility gap count as two phases) | mole | maximise | 397 | 0.3348 | 0.7616 | 1 | 0.26 |  |
| `ni_superalloy` | `solidus`: equilibrium solidus temperature | K | maximise | 250 | 1454 | 1625 | 1766 | 0.01 |  |
| `ni_superalloy` | `freezing_range`: equilibrium freezing range (liquidus temperature minus solidus temperature) | K | minimise | 250 | 0.2 | 42.4 | 518.9 | 0.01 |  |
| `ni_superalloy` | `gamma_prime_fraction`: equilibrium mole fraction of the ordered L12 phase (gamma prime) at 1173 K | mole | maximise | 249 | 0 | 0.2766 | 1 | 0.33 |  |
| `ni_superalloy` | `other_phase_fraction`: equilibrium mole fraction, at 1173 K, of all phases other than gamma (fcc) and gamma prime (L12): sigma, mu, P, R, Laves, eta, B2 and bcc | mole | minimise | 249 | 0 | 0 | 0.3648 | 0.58 |  |
| `ti_alloy` | `solidus`: equilibrium solidus temperature | K | maximise | 120 | 1586 | 1902 | 2091 | 0.02 |  |
| `ti_alloy` | `freezing_range`: equilibrium freezing range (liquidus temperature minus solidus temperature) | K | minimise | 120 | 10.8 | 152 | 453 | 0.02 |  |
| `ti_alloy` | `alpha_transus`: temperature above which no hcp alpha phase is stable at equilibrium (the beta transus when no other phase is present); reported as 773 K when no alpha is stable at 773 K | K | minimise | 115 | 773 | 969.7 | 1219 | 0.07 |  |
| `ti_alloy` | `alpha_fraction`: equilibrium mole fraction of the hcp alpha phase at 973 K | mole | minimise | 118 | 0 | 0.0055 | 0.8094 | 0.49 |  |
| `ti_alloy` | `intermetallic_fraction`: equilibrium mole fraction, at 973 K, of all phases other than the disordered bcc (beta) and hcp (alpha) solid solutions, for example Ti3Al | mole | minimise | 118 | 0 | 0 | 0.9905 | 0.52 |  |
| `refractory` | `solidus`: equilibrium solidus temperature | K | maximise | 200 | 1665 | 1948 | 2883 | 0.01 |  |
| `refractory` | `freezing_range`: equilibrium freezing range (liquidus temperature minus solidus temperature) | K | minimise | 200 | 115 | 547.7 | 1174 | 0.01 |  |
| `refractory` | `intermetallic_fraction`: equilibrium mole fraction, at 1473 K, of all phases other than liquid and the disordered fcc, bcc and hcp solid solutions (that is: sigma, Laves and other intermetallic phases, and ordered B2 or L12) | mole | minimise | 200 | 0 | 0 | 0.8956 | 0.69 |  |
| `refractory` | `main_phase_fraction`: equilibrium mole fraction, at 1473 K, of the single most abundant phase (1 for a single-phase alloy; two bcc phases of a miscibility gap count as two phases) | mole | maximise | 200 | 0.44 | 0.8951 | 1 | 0.35 |  |
| `steel` | `solidus`: equilibrium solidus temperature | K | maximise | 200 | 1452 | 1619 | 1803 | 0.01 |  |
| `steel` | `freezing_range`: equilibrium freezing range (liquidus temperature minus solidus temperature) | K | minimise | 200 | 1 | 74.55 | 238.9 | 0.01 |  |
| `steel` | `austenite_fraction`: equilibrium mole fraction of austenite (fcc) at 1173 K | mole | maximise | 200 | 0 | 0.9459 | 1 | 0.21 |  |
| `steel` | `carbide_intermetallic_fraction`: equilibrium mole fraction, at 1173 K, of all phases other than austenite (fcc) and ferrite (bcc): carbides, sigma, Laves and other intermetallic phases | mole | minimise | 200 | 0 | 0.0306 | 0.3995 | 0.34 |  |
| `cu_ti_3d` | `solidus`: equilibrium solidus temperature | K | maximise | 19 | 1194 | 1389 | 1695 | 0.05 |  |
| `cu_ti_3d` | `freezing_range`: equilibrium freezing range (liquidus temperature minus solidus temperature) | K | minimise | 19 | 9.1 | 173.5 | 397.5 | 0.05 |  |
| `cu_ti_3d` | `intermetallic_fraction`: equilibrium mole fraction, at 1173 K, of all phases other than liquid and the disordered fcc, bcc and hcp solid solutions (that is: sigma, Laves and other intermetallic phases, and ordered B2 or L12) | mole | minimise | 18 | 0 | 0.7674 | 1 | 0.22 |  |
| `cu_ti_3d` | `main_phase_fraction`: equilibrium mole fraction, at 1173 K, of the single most abundant phase (1 for a single-phase alloy; two bcc phases of a miscibility gap count as two phases) | mole | maximise | 18 | 0.3444 | 0.6421 | 1 | 0.06 |  |

## Files

- `<system>.csv`: one row per pool composition. `x_<element>` atomic fractions; `solidus_K`, `liquidus_K`, `freezing_range_K`; the fraction targets of the system; `liquid_fraction` at the fixed temperature; `density_fixedT_g_cm3` and `density_298K_g_cm3` (mass / molar volume of the equilibrium state; the 298 K value is the full equilibrium assemblage, which a real alloy does not reach, and is not used as a task); `phases_fixedT`, JSON with every stable phase, its fraction, group and order parameter, so the grouping can be audited; `melting_method`.
- `<system>_facts.json`: the sub-system calculations given as context (below).
- `systems.json`: the registry read by `src/wsp/tasks.py`.
- `raw/`: every calculation as it was returned, one JSON line per composition, and `slow_points.jsonl`, the equilibria that exceeded the time limit.

**Solidus and liquidus.** Each is first solved directly as a phase boundary (liquid fixed at amount 0 or 1, temperature free) and accepted only if global equilibria 1 K below and 1 K above agree with it. Otherwise it is bracketed by bisection on the liquid fraction of global equilibria to 4 K (assuming the liquid fraction rises with temperature) and solved inside the bracket; if that fails the middle of the bracket is reported. `melting_method` says which.

**Ordered or disordered.** The databases describe A2/B2 and A1/L1₂ with one phase each. A composition set is counted as ordered when the site fractions of its two sublattices differ by more than 0.05 for some element. The threshold is a convention; the order parameter is kept so the grouping can be redone.

**Sub-system facts and the no-leak rule.** The context given to a language model, and to the no-LLM references, is computed only for pure elements, binaries and ternaries: for the high-entropy systems every pure element, every binary at 25, 50 and 75 at.%, and every equimolar ternary; for the balance systems the pure base element, the base with one solute at half and the whole of its range, and the base with two solutes, both at half and both at the whole of their ranges. Every pool composition has at least four elements, so no fact can be a pool composition; `check_no_leak` stops the build otherwise and `tests/test_calphad.py` checks the files.

## What was built

| System | Rows in CSV | Failed quantities (rows) | Melting from a bracket (rows) | Rows with liquid at fixed T | Facts computed | Facts with a failed quantity | Equilibria (pool) | Hours |
|---|---|---|---|---|---|---|---|---|
| `cantor_al` | 400 of 400 | {'phases': 3, 'density_298K': 1} | 29 | 0 | 71 of 71 | none | 4,741 | 2.03 |
| `ni_superalloy` | 250 of 250 | {'phases': 1} | 27 | 0 | 43 of 43 | none | 3,041 | 1.41 |
| `ti_alloy` | 120 of 200 | {'phases': 2, 'transus': 5} | 107 | 0 | 43 of 43 | none | 2,678 | 1.28 |
| `refractory` | 200 of 200 | {'density_298K': 1} | 26 | 0 | 105 of 105 | 1 | 2,462 | 1.27 |
| `steel` | 200 of 200 | none | 61 | 0 | 43 of 43 | none | 2,771 | 0.75 |
| `cu_ti_3d` | 19 of 200 | {'phases': 1} | 12 | 0 | 71 of 71 | none | 376 | 0.52 |

A failed quantity is left empty in the CSV; the row is kept for the quantities that did compute.

## Anchor checks

Melting points of the elements from a one-element system of the database, against the SGTE values (Dinsdale, Calphad 15:317, 1991), and the density at 298.15 K against handbook values:

| Database | Element | Melting point here, K | SGTE, K | Density at 298 K here, g/cm³ | Handbook |
|---|---|---|---|---|---|
| TCHEA8 | Al | 933.5 | 933.5 | 2.70 | 2.70 |
| TCHEA8 | Co | 1768.0 | 1768.0 | 8.84 | 8.90 |
| TCHEA8 | Cr | 2180.0 | 2180.0 | 7.20 | 7.19 |
| TCHEA8 | Cu | 1357.8 | 1357.8 | 8.94 | 8.96 |
| TCHEA8 | Fe | 1811.0 | 1811.0 | 7.87 | 7.87 |
| TCHEA8 | Mn | 1519.0 | 1519.0 | 7.47 | 7.47 |
| TCHEA8 | Mo | 2896.0 | 2896.0 | 10.22 | 10.28 |
| TCHEA8 | Nb | 2750.0 | 2750.0 | 8.58 | 8.57 |
| TCHEA8 | Ni | 1728.2 | 1728.3 | 8.91 | 8.91 |
| TCHEA8 | Ta | 3290.0 | 3290.0 | 16.68 | 16.65 |
| TCHEA8 | Ti | 1941.0 | 1941.0 | 4.50 | 4.51 |
| TCHEA8 | V | 2183.1 | 2183.0 | 6.12 | 6.11 |
| TCHEA8 | W | 3694.9 | 3695.0 | 19.26 | 19.25 |
| TCHEA8 | Zr | 2127.9 | 2127.8 | 6.51 | 6.51 |
| TCFE10 | Fe | 1811.0 | 1811.0 | 7.87 | 7.87 |
| TCNI12 | Ni | 1728.3 | 1728.3 | 8.91 | 8.91 |
| TCTI6 | Ti | 1941.0 | 1941.0 | 4.50 | 4.51 |

Equiatomic alloys (TCHEA8):

| Alloy | Solidus, K | Liquidus, K | Phases at fixed T (fraction) | Density 298 K, g/cm³ | Failed |
|---|---|---|---|---|---|
| CoCrFeMnNi | 1557 | 1595 | 1273 K: FCC_L12#1 1.00 | 8.02 |  |
| CoCrFeNi | 1719 | 1722 | 1273 K: FCC_L12#1 1.00 | 8.12 |  |
| AlCoCrFeNi | 1632 | 1682 | 1273 K: BCC_B2#2 ordered 0.72, BCC_B2#1 0.28 | 7.32 |  |
| MoNbTaW | 3077 | 3137 | 1473 K: BCC_B2#1 1.00 | 13.88 |  |
| MoNbTaVW | 2731 | 2938 | 1473 K: BCC_B2#1 1.00 | 12.44 |  |
| TiZrNbTa (no Hf) | 2064 | 2359 | 1473 K: BCC_B2#1 1.00 | 8.91 |  |

Literature values for comparison (not computed here):

- CoCrFeMnNi: melting interval measured by DTA about 1,553 to 1,613 K (Laplanche et al., Acta Mater. 2016 report a
  solidus near 1,562 K); single-phase FCC at 1,273 K. Density about 7.9 to 8.0 g/cm³.
- CoCrFeNi: single-phase FCC, melting near 1,690 to 1,720 K.
- AlCoCrFeNi: A2 + B2 at high temperature, with sigma and FCC appearing at intermediate temperatures in
  experiments; melting near 1,620 to 1,680 K.
- MoNbTaW: single-phase BCC; rule-of-mixtures melting point 3,158 K; reported density 13.75 g/cm³ (Senkov et al.,
  Intermetallics 2010). MoNbTaVW: single-phase BCC, 12.36 g/cm³, rule-of-mixtures melting point 2,963 K.

These literature numbers are quoted from memory of the papers and were not re-checked against the sources in this run.
