# E7: written priors on Thermo-Calc-computed alloy pools

**Question.** In E1 a language model writes, with no data, the weights of a `d → 16 → 1` ReLU network that estimates an alloy property from element fractions; used as the prior mean of a GP it beat the plain GP in BO on 4 of 5 public alloy datasets. Those datasets are published measurements the model may recall. E7 repeats the test on targets computed here with Thermo-Calc over composition pools that have never been published as tables, and adds an arm in which the model is first given phase-diagram information about sub-systems.

## Data

`make_tc_data.py` (conda env `tcpy`, Thermo-Calc 2025b, TC-Python) builds nine alloy spaces in five databases. Full description, anchor checks and failure counts: `data/calphad/README.md`.

| System | Database | Elements | Pool |
|---|---|---|---|
| `cantor_al` | TCHEA8 | Al-Co-Cr-Fe-Mn-Ni | 400 |
| `refractory` | TCHEA8 | Mo-Nb-Ta-Ti-V-W-Zr | 250 |
| `hf_refractory` | TCHEA8 | Hf-Mo-Nb-Ta-Ti-Zr | 250 |
| `al_refractory` | TCHEA8 | Al-Cr-Mo-Nb-Ti | 250 |
| `cu_ti_3d` | TCHEA8 | Co-Cr-Cu-Fe-Ni-Ti | 250 |
| `ni_superalloy` | TCNI12 | Ni-Al-Co-Cr-Mo-Ti-W, Ni ≥ 50 at.% | 250 |
| `ti_alloy` | TCTI6 | Ti-Al-Mo-Nb-Sn-V-Zr, Ti ≥ 60 at.% | 250 |
| `steel` | TCFE10 | Fe-Al-C-Cr-Mn-Mo-Ni, Fe ≥ 50 at.% | 250 |
| `al_alloy` | TCAL9 | Al-Cu-Mg-Mn-Si-Zn, Al ≥ 85 at.% | 250 |

Every pool composition has at least four elements. Targets per system: solidus, freezing range, and phase fractions at a fixed temperature (intermetallic fraction and largest-phase fraction for the high-entropy systems; gamma-prime fraction for the nickel space; alpha transus and alpha fraction for titanium; austenite and carbide/intermetallic fraction for steel; second-phase fraction for aluminium). A target is dropped when more than 80% of the pool shares one value; `data/calphad/README.md` lists what was kept.

**Tasks.** `src/wsp/tasks.py` registers `<system>_<target>` for every kept target of every system whose pool is complete (`data/calphad/systems.json`). Inputs are the element atomic fractions; the train/test split is half and half per seed.

## Phase-diagram context and the no-leak rule

`<system>_facts.json` holds the same calculation for **sub-systems only**: pure elements, binaries and ternaries (at most three elements per point). `make_tc_data.check_no_leak` stops the build if a fact coincides with a pool composition, and `tests/test_calphad.py` checks the exported files. The facts never contain a target value of a pool alloy.

## Arms

| Prior source | What it is | Run folders |
|---|---|---|
| `select_<model>` | networks written from the E1 write prompt, unchanged | `runs/write__<task>__<model>__rep<k>` |
| `select_<model>_pd` | the same prompt plus the section "Phase-diagram facts for sub-systems (computed with CALPHAD)" (`wsp.arms.write_pd_prompt`) | `runs/writepd__<task>__<model>__rep<k>` |
| `rom` | no LLM: rule of mixtures of the pure-element values | |
| `subsystem_extrapolation` | no LLM: Redlich-Kister-Muggianu extrapolation of the binary and ternary facts (dilute-solution polynomial for the balance systems); gets exactly the facts the `_pd` prompt carries, fits nothing to multicomponent data | |

Each source enters the GP mean in three ways: two-stage (`wsp.arms.gp_with_prior`, fitted slope), joint `map` and joint `marginal` (`wsp.joint_mean.gp_joint_prior`); the plain GP is the baseline. Selection among a source's replies is the E1 rule: highest Pearson correlation with the labels so far, none below 0.3.

## Commands

`REPRODUCE.md` section 4f. In short:

```bash
E1=experiments/e1_surrogate_head; E7=experiments/e7_calphad_prior
conda activate tcpy && python $E7/make_tc_data.py                      # data (resumable)
conda activate matinvent && export PYTHONPATH=src
python $E1/run_baseline.py --task calphad --out $E7/results/baseline  # GP, ridge, MLP
python $E7/run_references.py                                           # the two references, E1 table format
python $E7/run_priors.py static --jobs 4                               # all sources x all mean arms: rho, coverage, NLL
python $E7/run_priors.py bo --seeds 20 --steps 25 --jobs 4             # BO, regret AUC, Wilcoxon vs plain GP
python $E7/make_prompts.py                                             # prompts for opus and fable, reps 1 to 3
# an LLM run: fresh subagent, "Read experiments/e7_calphad_prior/WRAPPER.md and follow it exactly,
# including writing both files. RUN = <run folder>"; then
python $E1/score_write_all.py --runs $E7/runs --out $E7/results/write_arm
python $E7/run_priors.py static --jobs 4 ; python $E7/run_priors.py bo --seeds 20 --steps 25 --jobs 4
```

## Results

Filled in by the commands above: `results/baseline/baseline_table.md`, `results/references/summary.md`, `results/static/summary.md`, `results/bo/summary_init5_steps25_seeds20.md`.

**Status (2026-11-12).** Pools computed for nine systems (200 to 400 compositions each). Written networks (Opus 5.5, Fable 5.2, with and without sub-system facts) scored statically and in 20-seed BO for four systems, 16 targets: `results/overview.md`, `docs/results/2026-11-12-round7.md`. Replies for the other five systems (19 targets) are being collected; their GP fits have not been run.
