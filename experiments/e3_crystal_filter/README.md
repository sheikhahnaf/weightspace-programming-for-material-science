# E3: a written network as a screening filter for crystal generators

A language model writes a 15 → 16 → 1 network on named descriptors of a crystal (volume per atom, mean atomic mass, mean electronegativity, mean elemental melting point, 11 composition-group fractions) from materials knowledge, with no data. The network scores crystals sampled from a generative model before any oracle call; the top quarter is kept.

- `filter_arm.py prompt --target {K,Cp} --tag <model>__rep<k>` writes a run folder; `WRAPPER.md` is the instruction given to the model under test.
- `filter_arm.py score [--backbone cf]` scores every reply on the sampled crystals: `results/filter_arm/` (MatterGen, 11 variants × 128 crystals) and `results/filter_arm_cf/` (CrystalFlow, 11 variants × 128 crystals).
- The crystals and their oracle values are in `supplementary/e3_generator_task_vectors/results/hprc{,_cf}/`; they were sampled for the task-vector study there.
- The same replies are reused, with no new model runs, as the prior mean and as inputs of the closed-loop GP (`experiments/e1_surrogate_head/run_structure_prior.py`, `run_structure_features.py`) and as the mean of a Bayesian neural network (`experiments/e5_bnn_start/`).

Controls: a one-line rule with no LLM (small volume per atom for bulk modulus; Dulong–Petit for heat capacity) and an MLP of the same size trained on 400 Materials Project structures. The MLP first scored 0.29 and 0.12 because of an input-scaling bug in `trained_k_scorer` (descriptors that are zero in all 400 structures were divided by 1e-8); fixed on 2026-11-12 it scores 0.89 and 0.88. A ridge regression on log K and a random forest trained on the same 400 structures also rank as well as the written networks (`experiments/e1_surrogate_head/robustness.py filter`).

**Status (2026-11-12).** 18 replies from four models (Opus 5.5, Fable 5.2, Sonnet 5.5, Haiku 5.5): three per model for bulk modulus, and two (Opus, Fable) or one (Sonnet, Haiku) for heat capacity; all valid; scored on MatterGen and CrystalFlow samples. Bulk modulus, base samples: ρ with the oracle 0.92, 0.88 and 0.80 (MatterGen) and 0.88 (CrystalFlow) for Opus, Fable and Sonnet, against 0.82 and 0.77 for the volume rule and 0.89 and 0.88 for the trained MLP. Heat capacity: the Dulong–Petit rule already ranks perfectly and the networks match it.
