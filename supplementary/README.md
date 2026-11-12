# Supplementary experiments

Work that is not part of the main case (a language model writes a small property-prediction network from knowledge alone). Each folder keeps its own README, run records and results. Paths inside the scripts are relative to the repository root, as before the move from `experiments/`.

| Folder | What it tests | State |
|---|---|---|
| `e2_mlip_readout_edit/` | Editing the readout of interatomic potentials (MACE, ORB, eSEN, GRACE) with and without measured feedback; an error-risk predictor | run; see `docs/results/2026-11-11-round3.md` to `round5.md` |
| `e8_formation_enthalpy/` | A written per-element correction of a potential's formation enthalpies | data and baselines built; no model runs |
| `e3_generator_task_vectors/` | Averaging, scaling and truncating the weight changes of RL-fine-tuned generators (MatterGen, CrystalFlow; ADiT prepared) | MatterGen and CrystalFlow sampled and scored; ADiT sampling not submitted |
| `e4_surrogate_zoo/` | Learning from 30,360 fitted surrogates (weight-space learning in the broad sense) | step 2 run |

The crystals sampled in `e3_generator_task_vectors/results/hprc{,_cf}/` are also the test set of the main screening-filter experiment, `experiments/e3_crystal_filter/`.
