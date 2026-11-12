# Where weight-space programming fits: BO surrogate, MLIP or generative model

Research run of 2026-11-11. Question, verbatim: "find out where can weight space programming fit? either for BO surrogate,mlip or generative model".

## Verdict

Weight-space programming fits the **BO surrogate** now, at the small readout head or prior mean that sits on frozen foundation-model embeddings. It fits the **MLIP** only at the scalar readout, which for MACE is 2,283 numbers out of 9 million. It does not fit the **generative model** itself; there the useful work is the broad-sense kind, on the 59 fine-tuned checkpoints that already exist.

The method is nine days old: one blog post, about eight preprints, no peer-reviewed paper, no independent replication of the headline result beyond a rebuild from the authors' logs. Nothing published applies it to regression with uncertainty, to an equivariant network, or to crystals. That absence is the opening, and it is also the risk.

## How this was researched

| Arm | What it did | Record |
|---|---|---|
| Read-only survey of `matinvent-bo`, `matgen-BO`, `autoresearch-bo` | three agents, one per repo | `research/2026-11-11-wsp-fit/repo-surveys.md` |
| Primary sources on weight-space programming | blog and Wikipedia read in full; three arXiv pages | `…/wsp-primary-sources.md` |
| Claude.ai Research, Consensus connector only | 266 sources, 8 min 28 s | `…/report-claude-ai.md`, `…/sources-claude-ai.md`, brief in `…/brief.md` |
| Consensus paper search | three queries, 60 abstracts | `…/consensus.md` |
| Web search | six queries | cited inline below |
| Local measurement | parameter counts from cached checkpoints | §2 |

Evidence tags used below: **MEASURED** (counted here on 2026-11-11), **REPO** (stated in a sibling repo, not recomputed), **PREPRINT**, **PEER-REVIEWED**, **BLOG**, **CHECKED** (re-fetched from the live page after the research report cited it), **INFERENCE** (our reasoning; no source carries it).

## 1. What weight-space programming is and what has been shown

An LLM is given a network's weights and a task in words, and reads, writes or edits the weights without gradient descent. Introduced by Takehi, Teoh, Zhang and Khattab (MIT CSAIL) in a blog post of 2 November 2026 [BLOG].

| Setting | Largest network shown | Source |
|---|---|---|
| Raw weights as text, no tools | 171,664 weights (policy edit, 3.5% changed, 1,024 of 1,024 episodes) | Sparks post [BLOG] |
| Written from zero in one reply, no tools | about 20,500 weights (MinAtar policies; beat PPO on one of three games) | Sparks post [BLOG] |
| Python sandbox plus up to 50 forward passes | 1,480,274 written; 131,072 edited inside a 0.8 B model | Sparks post [BLOG] |
| Blind audit and repair, no tools | 433 to 4,801 weights; 16 of 18 planted flaws named; median 3 weights changed | arXiv 2611.05341 [PREPRINT] |
| Edit of a frozen encoder's readout after new measurements | 128 readout weights; better than the original in 7 of 8 settings, below a full refit | WeightLoop, arXiv 2611.07319 [PREPRINT, CHECKED for title, date and the 7-of-8 figure; the 128 and 16 come from the research report's reading of the full text] |

What cuts against it:

- A confident wrong reading on shuffled weights: the model still guessed CIFAR-10 at 7.78% accuracy; the author's verdict is local arithmetic plus dataset priors (arXiv 2611.08070) [PREPRINT].
- "The gains came from being cheap, not from what the LLM wrote": on one scheduling problem a plain rule did exactly as well (arXiv 2611.09559) [PREPRINT, CHECKED].
- Six of sixteen editing trajectories kept the original weights (arXiv 2611.09382) [PREPRINT].
- The edit that raised a small language model's maths score removed a looping failure; on a model without that failure the same method gained nothing. The authors: editing "could remove an obstacle that hid an ability, but it could not add an ability the model lacked" [BLOG, as quoted in the research report].
- No primary paper reports token cost.

Every target so far is a classifier, a policy or a language model. None is a regressor with an uncertainty estimate.

## 2. Sizes, measured against that envelope

| Object in our pipeline | Weights | Tag | Inside the no-tool envelope (up to about 172,000)? |
|---|---|---|---|
| Readout head `50 → 32 → 32 → 1` on PCA-50 ORB embeddings | 2,721 (17,537 characters as text at three decimals) | MEASURED | yes |
| Prior-mean network `40 → 16 → 1` on composition descriptors | 673 | INFERENCE (arithmetic) | yes |
| GP hyperparameters at PCA 50 (lengthscales, outputscale, noise) | about 52 | INFERENCE (arithmetic) | yes, but too few to be a weight-editing problem; this is kernel or prior choice, where LLM methods already exist |
| MACE-MPA-0 medium, whole model | 9,063,204 | MEASURED | no |
| MACE-MPA-0 medium, readouts (128 + 2,048 + 16) + 89 reference energies + scale and shift | 2,283 | MEASURED | yes |
| MACE-MP-0 medium, whole model | 4,688,656 | mace-foundations release page, via the research report | no |
| ORB-v3 | about 25 M | Orb-v3 paper, via the research report | no; readout size not published, not measured |
| eSEN-30M-OAM (our oracle) | 30 M | UMA paper, via the research report | no |
| MatterGen base checkpoint | 53,737,595 entries in the state dict; the model card says 46.8 M parameters | MEASURED; card via the research report | no |

The two MatterGen figures differ because a state dict also holds buffers; the split was not checked.

## 3. Fit by target

### A. BO surrogate — fits now

Why: the object is small, the embedding is frozen, labels are few, and an edit can be scored at once against held-out labels. The sibling paper lists the frozen embedding and the missing calibration study as its limits, and its loop GP underpredicts the best candidates by about 42.5 GPa [REPO].

Three places, in order of how well the evidence supports them:

1. **Edit a trained head to remove a named fault** (bias on high values, a planted leak). This is what the audit paper and WeightLoop show working at this size.
2. **Write a prior mean for the GP from stated physical trends.** The GP keeps its own uncertainty, and a learnable scale lets the marginal likelihood discard a wrong prior. Nothing like it is published [research report §3.3, gap 2].
3. **Write a head from zero.** Weakest: the one study that tried it on real data concluded that written weights do "not yet replace training data" (arXiv 2611.12066, not re-fetched).

Already published next door, and therefore baselines rather than contributions: LLM-proposed GP kernels (CAKE, NeurIPS 2025, arXiv 2509.17998 [PEER-REVIEWED]; a later comparison found a weak LLM trailing plain search, arXiv 2601.05371 [PREPRINT]); LLM-written acquisition functions (FunBO, arXiv 2406.04824 [CHECKED]); in-context surrogates (PFNs4BO, TabPFN [PEER-REVIEWED]). TabPFN is already in `autoresearch-bo` and won two of 18 benchmarks there [REPO].

What does not exist: any weight-space programming result with calibration measured after the edit.

### B. MLIP — fits at the readout only

The message-passing layers hold 99.97% of MACE's weights and are equivariant tensors; no LLM has edited anything like them. The readout, reference energies and scale and shift are invariant scalars: an edit there cannot break equivariance, and forces remain the gradient of the energy [INFERENCE].

Two published results say the error worth fixing is low-dimensional: softening of universal potentials "can be effectively rectified by fine-tuning with a single additional data point" (arXiv 2405.07105 [CHECKED]), and reference-energy initialisation "routinely exceeds" the choice of fine-tuning strategy (arXiv 2606.12704 [PREPRINT]). Whether that low-dimensional error lives in the readout is not known; experiment E2 tests it.

The working baseline is gradient-based: MACE has shipped LoRA since v0.3.15 [CHECKED].

Correction to the research report: it found no merging of fine-tuned potentials. GFFMerge (arXiv 2606.03232, 2 June 2026) merges separately fine-tuned graph force fields in closed form and reports results "approaching gold standard joint training" on MD17, MD22 and LiPS20 [CHECKED; found by our own web search]. Its abstract does not name MACE, so merging of foundation-model fine-tunes for inorganic solids is still open.

Not found anywhere: hypernetwork-generated adapters for a potential; an LLM reading or editing any potential.

### C. Generative model — broad sense only

MatterGen is some 300 times larger than the largest network edited from raw weights, and the tool-assisted results on large models removed one failure direction in a language model. There is no evidence to plan a weight edit of a crystal generator on.

What the sibling repos make cheap instead: 59 RL-fine-tuned checkpoints across three backbones, two targets, two policies and five seeds, with reward logs [REPO]. Their differences from the base are task vectors. Whether those are low-rank, whether seeds agree, and whether a heat-capacity vector and a bulk-modulus vector add, are open questions that cost no new training. No paper does adapter or task arithmetic on a crystal generator [research report §5.2].

The one narrow-sense entry point is small networks around the generator: an LLM-written plausibility scorer in front of the expected-improvement gate. It is ranked low because it meets the "cheapness" objection head-on.

## 4. What was built from this

| Experiment | Target | Sense | First step costs | Folder |
|---|---|---|---|---|
| E1 readout head and prior mean on frozen ORB embeddings | BO surrogate | narrow | CPU, plus LLM calls | `experiments/e1_surrogate_head/` |
| E2 scalar readout edit of MACE | MLIP | narrow, with forward passes | one GPU, hours | `supplementary/e2_mlip_readout_edit/` |
| E3 task vectors of the fine-tuned generators | generative | broad | download plus linear algebra | `supplementary/e3_generator_task_vectors/` |
| E4 learning from the zoo of fitted surrogates | BO surrogate | broad | CPU | `supplementary/e4_surrogate_zoo/` |

How this differs from the research report's ranking: its first three ideas (readout editor, prior mean, audit) are folded into E1 as arms; its MACE readout idea is E2 with softening as the target instead of a change of functional, because DFT references for that already exist in the sibling repo; its MatterGen adapter-arithmetic idea needs new adapter training, so E3 uses the checkpoints already made; E4 is not in the report and comes from the 8.3 GB parameter zoo found in `autoresearch-bo`. The report's refractory-alloy ideas (Nb-Ti-Hf LoRA arithmetic) were not taken up: that chemistry focus is not in the three repos and appears to come from the account's other work.

## 5. Checks

| Claim | Result |
|---|---|
| WeightLoop is arXiv 2611.07319, 5 Nov 2026 | confirmed; abstract gives 7 of 8 settings; 128 readout weights, 16 changed and the biology domain are not in the abstract |
| arXiv 2611.09559 "gains came from being cheap" | confirmed, quoted |
| MACE LoRA since v0.3.15 | confirmed from the release notes |
| Softening fixed by one data point, arXiv 2405.07105 | confirmed, quoted |
| FunBO, arXiv 2406.04824 | confirmed; venue not shown on arXiv |
| MACE readout is about 2,200 weights (report's estimate) | measured: 2,192, plus 91 buffer values |
| "No merging of fine-tuned potentials found" | wrong: GFFMerge, arXiv 2606.03232 |
| "WSP is a three-week-old idea" (report §1) | wrong: nine days at the time of writing; the report's own caveats say nine |
| MatInvent "ICLR 2025" | not settled: arXiv 2511.03112 is dated 5 Nov 2025 and shows no venue; the report cites an OpenReview PDF that was not opened |

## 6. Caveats

- §3 was written before any experiment here, as inference from other people's preprints. The first pilot, run the same day, is in `docs/results/2026-11-11-e1-pilot.md`; it weakens place 1 of §3A as prompted (the edit showed no weight reading) and gives place 2 (written prior mean) a small-data ranking signal.
- arXiv 2611.09382 and 2611.05341 were read as abstracts only; 2611.12066 and the Honnibal critique were not fetched at all.
- ORB-v3, eSEN and UMA readout sizes were not measured.
- The closed-loop code behind the published paper lives in two further repos that were not surveyed.
- Consensus returned abstracts only; no paper was read in full through it.
