# E3: task vectors of the RL-steered crystal generators (generative model)

**Question.** The published loop left 59 fine-tuned generator checkpoints. Is the change each run made to the weights low-rank, does it agree across seeds, and can two changes be added to steer toward two properties at once?

**Why here.** Measured on the locally cached MatterGen base checkpoint on 2026-11-11: 53,737,595 entries in its state dict, of which 27.6 million sit in the output blocks and 21.7 million in the interaction blocks. No LLM has been shown to edit a network of that size from its weights, so the narrow sense of weight-space programming does not apply to the generator. The broad sense does: the checkpoints are a ready zoo.

**Prior work.** No paper adds or merges fine-tuned crystal generators. For force fields, GFFMerge (arXiv 2606.03232, preprint) merges separately fine-tuned graph networks in closed form and reports performance "approaching gold standard joint training" on MD17, MD22 and LiPS20; its alignment step is the method to try if plain addition in step 4 fails.

**Data.** `finetuned_diffusion/` on Hugging Face (DOI 10.57967/hf/9893): 3 backbones (MatterGen, CrystalFlow, ADiT) × 2 targets (heat capacity, bulk modulus) × 2 policies (gated, ungated) × 5 seeds, each with per-cycle reward logs. The base checkpoints are public.

**Steps.**
1. Task vector τ = fine-tuned − base, per run. Report its norm per layer and the singular-value spectrum of each weight matrix's change: what rank keeps 90% of the energy?
2. Agreement: cosine similarity of τ between seeds of the same cell, between policies, and between targets.
3. Compression: replace τ by its rank-r truncation, sample, and score with the same oracle. This says whether a LoRA adapter could have done the RL run's job.
4. Arithmetic: base + α·τ(heat capacity) + β·τ(bulk modulus), sample, score both properties. Baseline: the two single-target checkpoints, and seed-averaged weights.
5. Only if step 1 shows low rank: hand the low-rank factors of one layer to an LLM with the reward log and ask for an edit, which is the narrow sense applied to an adapter.

**Measures.** Fraction of the run's reward gain kept at rank r; stable-unique-novel rate after arithmetic (a merged generator that produces invalid crystals has failed, whatever its reward); both property means against the single-target checkpoints.

**Cost.** Steps 1 and 2 are linear algebra on downloaded checkpoints: no GPU hours, no oracle calls. Steps 3 and 4 need sampling plus the eSEN oracle, on the cluster.

**Main risk.** Full-parameter REINFORCE over 20 cycles at learning rate 1e-5 may move the weights too little, or too noisily, for τ to carry a direction. Step 2 answers that before any GPU time is spent.

**Status.** Specification only. Checkpoints not downloaded.
