# E2: editing the scalar readout of a foundation interatomic potential (MLIP)

**Question.** Can an LLM, shown only the readout weights, the element reference energies and the scale and shift of a MACE foundation model, correct a known systematic error with a handful of edits and at most 50 forward passes?

**Why here.** Measured on the locally cached `MACE-MPA-0 medium` on 2026-11-11:

| Part | Weights |
|---|---|
| whole model | 9,063,204 |
| interactions 0 and 1 | 7,701,780 |
| products 0 and 1 | 1,347,840 |
| node embedding | 11,392 |
| readout 0 (linear, 128) and readout 1 (2,048 + 16) | 2,192 |
| element reference energies (buffer) | 89 |
| scale and shift (buffers) | 2 |

The interaction blocks are far outside what an LLM has been shown to edit. The last three rows are 2,283 numbers. They are invariant scalars, so an edit there cannot break rotational equivariance, and forces stay the gradient of the energy.

**Target error.** Deng et al. (arXiv 2405.07105) report that universal potentials systematically underpredict the curvature of the energy surface, and that a small fine-tune removes it. Tompa et al. (arXiv 2606.12704) report that reference-energy initialisation matters more than the fine-tuning strategy. Both say the error sits in few degrees of freedom; this experiment tests whether an LLM can find them.

**Protocol.**
1. Reference: bulk modulus of the 15 structures for which the sibling repo has DFT (`matgen-BO/02_closed_loop_bo/validation/dft_validation/`), read-only.
2. Baselines: unedited model; a fine-tune of the readout only (same 2,283 numbers trainable) with the same data; MACE's own reference-energy re-estimation; rank-4 LoRA, which MACE has shipped since v0.3.15 (`--lora_rank=4`).
3. LLM arm: prompt with the 2,283 numbers, the architecture of the readout, the per-structure error table, and a sandbox that returns energies for 0, 10, 25 or 50 forward passes.
4. Check on held-out structures that energy–volume curves stay smooth and that forces still match finite differences of the energy.

**Measures.** Bulk modulus error against DFT before and after; number of weights changed; error on a set the edit never saw (forgetting); tokens.

**Main risk.** The softening may live in the interaction blocks, in which case no readout edit can fix it and the readout-only fine-tune baseline will fail too. That outcome is still a clean result: it bounds where the error lives.

**Status.** Specification only. The parameter table above is the only measurement made.
