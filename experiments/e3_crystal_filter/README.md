# E3: a written network as a screening filter for crystal generators

A language model writes a 15 → 16 → 1 network on named descriptors of a crystal (volume per atom, mean atomic mass, mean electronegativity, mean elemental melting point, 11 composition-group fractions) from materials knowledge, with no data. The network scores crystals sampled from a generative model before any oracle call; the top quarter is kept.

- `filter_arm.py prompt --target {K,Cp} --tag <model>__rep<k>` writes a run folder; `WRAPPER.md` is the instruction given to the model under test.
- `filter_arm.py score [--backbone cf]` scores every reply on the sampled crystals: `results/filter_arm/` (MatterGen, 11 variants × 128 crystals) and `results/filter_arm_cf/` (CrystalFlow, 11 variants × 128 crystals).
- The crystals and their oracle values are in `supplementary/e3_generator_task_vectors/results/hprc{,_cf}/`; they were sampled for the task-vector study there.
- The same replies are reused, with no new model runs, as the prior mean and as inputs of the closed-loop GP (`experiments/e1_surrogate_head/run_structure_prior.py`, `run_structure_features.py`) and as the mean of a Bayesian neural network (`experiments/e5_bnn_start/`).

Controls: a one-line rule with no LLM (small volume per atom for bulk modulus; Dulong–Petit for heat capacity) and an MLP of the same size trained on 400 Materials Project structures.

**Status (2026-11-12).** 12 replies per target requested from four models (Opus 5.5, Fable 5.2, Sonnet 5.5, Haiku 5.5); scored on MatterGen and CrystalFlow samples. Bulk modulus: ρ with the oracle 0.94 (MatterGen) and 0.88 (CrystalFlow) for Opus, Fable and Sonnet, against 0.77 for the volume rule on CrystalFlow. Heat capacity: the Dulong–Petit rule already ranks perfectly and the networks match it.
