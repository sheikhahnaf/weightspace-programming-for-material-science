# Research brief: where can weight-space programming fit in Bayesian materials discovery?

Date: 2026-11-11

## The question (verbatim)

"find out where can weight space programming fit? either for BO surrogate, mlip or generative model"

## Definitions

**Weight-space programming (WSP)**, narrow sense: a general-purpose LLM reads and directly writes another neural network's weights, around a natural-language specification, without gradient descent. Introduced in "Sparks of Weight-Space Programming" (Takehi, Teoh, Zhang, Khattab, MIT CSAIL, blog post of 2 Nov 2026). Follow-ups: arXiv 2611.09382 (WSP-Scope), 2611.08070, 2611.05341, 2611.12066.

**Weight-space learning**, broad sense: any method that treats weights as data: hypernetworks, generated LoRA adapters (Text-to-LoRA, LoRAGen, W2T), task arithmetic and model merging, neural functionals and equivariant weight-space networks, model editing (ROME-style), compiled networks (Tracr), prior-fitted networks (TabPFN, PFNs4BO).

Cover both, and keep them apart in every section.

## The project

We run Bayesian optimisation for inorganic crystal discovery. Three pieces: (1) probabilistic surrogates (GP, multi-task GP, deep GP, deep kernel) on frozen embeddings from atomistic foundation models (MACE, ORB, UMA, SOAP baseline) for elastic, dielectric and phonon-thermodynamic targets with a few hundred to a few thousand DFT labels; (2) a closed loop where a crystal generative model (MatterGen, CrystalFlow, ADiT) proposes structures and a GP-routed expected-improvement gate decides which go to an MLIP or to DFT; (3) an LLM-driven loop that searches over surrogate-selection policies for multi-objective BO. Compute is a university GPU cluster. Labels are expensive, so anything that adapts a model with few or zero gradient steps matters.

## What to cover

For each of the three targets below, find what has been done, what has been shown to work, and what is open.

**A. BO surrogate.** LLM-written or LLM-edited small networks as surrogates, kernels, mean functions or acquisition functions; hypernetworks that emit a surrogate per task; prior-fitted networks as weight-free adaptation; LLM-proposed GP kernels or priors; weight edits as a way to inject physical constraints (monotonicity, symmetry, known limits) into a readout head; calibration of uncertainty after a weight edit.

**B. MLIP.** Editing or generating weights of MACE, ORB, UMA, MatterSim, SevenNet, CHGNet, eSEN: LoRA and other parameter-efficient fine-tuning; task arithmetic or merging of fine-tuned MLIPs; hypernetwork-generated adapters conditioned on chemistry or level of theory; weight-space analysis or interpretability of equivariant GNNs; multi-fidelity heads. State the parameter counts of these models and of their readout heads, because the reported WSP limit without tools is about 17,000 to 172,000 weights.

**C. Generative model.** Steering MatterGen, DiffCSP, CrystalFlow, FlowMM, ADiT or crystal LLMs by weight edits instead of fine-tuning or guidance: adapter generation per property target, adapter arithmetic for multi-property conditioning, concept editing or unlearning in diffusion models carried to crystals, LLM-written guidance or reward networks.

**D. WSP itself.** Every paper, post, repository and critique since 2 Nov 2026: models used, how weights are serialised, network sizes, tools allowed, numbers, failures, token cost, replication status. Any use on regression, scientific ML, graph or equivariant networks.

## What to record per item

Title, authors, venue or arXiv id, date, code URL and licence, model and parameter count, task, the headline number with its baseline, and the stated limit.

## Grading

Tag every claim: PEER-REVIEWED / PREPRINT / OFFICIAL PAGE / REPOSITORY / BLOG-PRESS / THIRD-PARTY. Tag UNVERIFIED anything you could not re-fetch. An inference is labelled as an inference, never printed as a paper's number.

## Output shape

Cited Markdown report with: 1. one-paragraph verdict; 2. WSP state of the art (section D) with a table; 3. sections A, B, C, each with a table of prior work and a list of open gaps; 4. a ranked list of five to eight concrete research ideas, each with the smallest experiment that would test it, the baseline it must beat, the network size involved, and the main risk; 5. what is not published: say plainly where nothing exists; 6. numbered sources with full URL and access date.
