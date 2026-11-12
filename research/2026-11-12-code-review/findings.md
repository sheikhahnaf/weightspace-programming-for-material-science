# Critical review of the code base, 2026-11-12

Request (verbatim): "ok analyze the whole code base critically to find any mistake, short coming, reward hacking, corner cutting that invalidate our finding".

Method: one read-only review by a Claude Opus 5.5 agent over `src/`, `experiments/`, the result files and the paper's claims, with its own check scripts; then each finding was re-derived independently in `experiments/e1_surrogate_head/robustness.py`, whose outputs are in `experiments/e1_surrogate_head/results/robustness/`. Numbers below are from that script.

## Findings that changed a claim

1. **Screening filter: the trained reference was a straw man.** The paper compared the written network with one 15 → 16 → 1 MLP trained on 400 Materials Project crystals (ρ 0.29 on MatterGen samples, 0.12 on CrystalFlow) and concluded that training on known crystals does not transfer. A ridge regression on log K and a random forest, trained on the same 400 crystals and descriptors, rank at 0.93 and 0.92 (MatterGen) and 0.89 and 0.90 (CrystalFlow); the Opus networks rank at 0.92 and 0.88. The MLP fails because generated crystals reach volumes per atom outside its training range (up to 91 Å³ against 55 Å³). Claim changed from "better than a trained network" to "as well as a ridge regression or random forest trained on 400 labelled crystals".
2. **Crystal tasks: starting set counted once per run, and its labels are not the oracle's.** All six bulk-modulus runs start from the same 500 crystals (five heat-capacity runs: 445). "3,479 crystals" were 979 unique; "2,437" were 657. The bulk-modulus starting set is `bm_seed_elastic_tensor_2015`: Materials Project crystals with DFT K_VRH, not eSEN values. Zero-label ρ for bulk modulus: all rows 0.93 (Opus) against 0.74 (volume rule), as first reported; each crystal once 0.94 against 0.81; crystals added during the runs 0.95 against 0.89. The paper now reports the last pair, states the label sources, and says that the 500-label GP (0.88) is trained on DFT labels of known crystals and tested on eSEN labels of generated ones. 63 of the 479 added bulk-modulus crystals are marked `seed_pool`, not generator proposals; their label source is not recorded in the files copied here.
3. **Pseudo-replication.** "18 of 18 cells, p = 8e-6" (working notes and slides; not in the paper) treated run × draw cells as independent. With the run as the unit: 6 of 6 runs, p = 0.031.
4. **Alloy reference too weak.** The rule of mixtures (elemental Young's modulus or Vickers hardness) ranks at −0.72 to 0.27. Atomic size mismatch δ ranks the four strength and hardness tasks at 0.57 to 0.62 and Ti modulus at 0.16; Opus 0.64 to 0.79. As a BO prior δ gives a regret area of 5.7 on Ti hardness (Opus 5.95, plain GP 40.1) and is not significantly better than the plain GP on the other four; Opus is significantly ahead of δ on Ti modulus, Ti yield strength and MPEA hardness (p = 0.049, 0.018, < 0.001). δ was chosen after seeing the targets.
5. **Multiple tests.** Thermo-Calc BO counts use Holm within a target. Opus: 16 targets within target, 15 across the 33 targets, 13 across all 165 tests; Fable 15 / 13 / 11; extrapolation 18 / 18 / 17. All p values are over 20 seeds with the written replies fixed.
6. **Phase-fraction lead not significant.** Mean ρ 0.69 (Opus) and 0.67 (Fable) against 0.63 for the extrapolation; Opus ahead on 7 of 16 targets (paired Wilcoxon p = 0.50), Fable on 9 (p = 0.60).
7. **Bug in one control.** `run_structure_prior.py` z-scored descriptors with `std + 1e-8`; one composition-group fraction is zero in the whole starting set, so a test crystal with a non-zero value was sent to about 1e7. Fixed (constant columns dropped), cached cells refitted. Embedding + descriptors: 0.60 at 20 labels and 0.80 at 500 (were 0.52 and 0.66). Still below the embedding alone from 10 labels on.

## Findings that are now stated as limits

- Recall: the experimental alloy sets are public and named in the prompts, and the models' self-reports calibrate against remembered values of alloys in the pools.
- The "with facts" prompts carry the same sub-system values as the extrapolation plus the model's own knowledge, so that arm is not a like-for-like comparison of methods.

## What the review found sound

- Prompts regenerate from code; input conventions of prompts and scoring agree.
- The rule that selects among replies during BO uses only labels seen so far.
- Cached BO traces recompute exactly; the transcript audit covers every reply.
- Single Opus replies used without the selection gate still help on 4 of 5 alloy tasks (the reviewer's own check, not re-derived in `robustness.py`).

## Not done

- The seed-pool crystals' label source was not traced in the sibling repository.
- No new language-model runs; no test of variation between replies in BO beyond the per-reply scores already reported.
