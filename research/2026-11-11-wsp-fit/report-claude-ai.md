# Where Weight-Space Programming Fits in Bayesian Crystal Discovery: BO Surrogate First, MLIP Readout Second, Generative Model Last

Weight-space programming fits your project best at the BO surrogate's readout layer. No published result shows it working on an MLIP backbone or on a crystal generative model. The best-documented WSP results are on networks of 17,253 to 171,664 weights. The one WSP paper closest to your setting, WeightLoop (arXiv 2611.07319), uses an LLM-written editor to change 16 of 128 readout weights on a frozen encoder after each batch of new measurements. That is almost exactly your "frozen foundation-model embedding + small head + expensive labels" design. Everything larger than about 0.2M weights (every universal MLIP and every crystal generator) has been touched only by conventional gradient-based weight-space methods: LoRA, adapters, RL fine-tuning, frozen-layer transfer. None of the narrow-sense WSP studies so far covers regression on scientific targets with calibrated uncertainty, equivariant networks, or crystals. All sources were accessed 2026-11-11.

## TL;DR

- **Where it fits now:** the surrogate head on frozen MACE/ORB/UMA embeddings. Use an LLM to write or edit a few hundred to a few thousand readout/mean-function weights between BO rounds. Treat it as a cheap, auditable alternative to refitting. It must beat GP refits, affine recalibration and TabPFN on regret and calibration. [Inference from WeightLoop arXiv 2611.07319 and the Sparks blog post; nothing on materials is published.]
- **MLIPs:** whole models (CHGNet ≈0.4M to UMA-M 50M active / 1.4B total) are 3 to 4 orders of magnitude beyond the no-tool WSP envelope. Only the final readout (an estimated ~2k weights for MACE; not stated in any primary source) is in range. LoRA (built into MACE since v0.3.15) is the working baseline. No task arithmetic, merging or hypernetwork-generated adapters for MLIPs were found.
- **Generative models:** MatterGen (46.8M), ADiT (32M to 450M denoiser plus 51M VAE) and CrystalFlow are steered today by gradient-trained adapters, RL fine-tuning or training-free guidance. Nobody has edited their weights with an LLM, done adapter arithmetic on them, or erased concepts from them. The realistic WSP entry point is an LLM-written small reward/guidance network, not editing the score network.

## 1. Verdict

WSP is a three-week-old idea with one viral blog post, about eight follow-up preprints, two critiques and no peer-reviewed paper. The evidence that holds up is narrow. A frontier LLM can (a) hand-write small networks that implement a program it can state, and (b) find and remove a single dominant failure direction in a larger model when given a Python sandbox and forward passes. The evidence that it "reads" trained weights is weaker: one critique finds it is mostly local arithmetic plus dataset priors (arXiv 2611.08070). It has also not beaten cheap baselines when the gains came from cheapness (arXiv 2611.09559).

For your three-part project:
- **A (BO surrogate)** is the right place to try narrow-sense WSP. The objects are small, the inputs are frozen embeddings, labels are scarce, and a weight edit can be checked against held-out DFT labels immediately.
- **B (MLIP)** is the right place for broad-sense methods (LoRA, multi-head, frozen transfer). Narrow-sense WSP is limited to readout heads.
- **C (generative)** should use WSP only for the small guidance/reward networks around the generator.

The most defensible novel contribution is the first WSP study on **regression with calibrated uncertainty inside a closed BO loop**. Nothing like it is published.

## 2. Section D: state of the art in weight-space programming (narrow sense)

The named blog post and all four arXiv ids in the brief exist and were fetched. The exception is 2611.12066, whose abstract page hit a rate limit; it was read only from search-result extracts of its abstract and HTML. Two further WSP preprints not named in the brief were also found (2611.07319, 2611.09559).

### 2.1 Core table

| Item | Authors / venue / date | Code & licence | LLM used | Target network & size | Tools allowed | Headline number vs baseline | Stated limit | Grade |
|---|---|---|---|---|---|---|---|---|
| Sparks of Weight-Space Programming | Takehi, Teoh, Zhang, Khattab (MIT CSAIL); blog, 2 Nov 2026 | Logs: github.com/RikiyaT/lm_understand-logs; edited model on Hugging Face; licence not stated | GPT-6 Astra | Exp 1: MLP 500→32→32→5, 17,253 weights. Exp 2: DDPM MLP, 23,824. Exp 3: 7.16M char-transformer (middle blocks only). Exp 4: Kinetix actor, 171,664. Exp 5: MinAtar 600→32→32→6. Exp 6: Go net, 1,480,274. Exp 7: Gemma 3 270M. Exp 8: Qwen3.5-0.8B | Exps 1, 2, 4, 5: weights as plain text in the prompt, no tools. Exps 3, 6, 7, 8: Python sandbox; Exps 6 and 8 also get forward-pass budgets | Exp 4: 0%→100% success over 1,024 episodes, editing 3.5% of weights in one reply. Exp 5: Breakout 517.4 vs 15.8 (PPO 100M steps) and 25.3 (PPO 500M). Exp 8: MATH-500 7.9%→48.1%, GSM8K 13.8%→67.1%, IFEval 21.0%→62.3%, editing 131,072 weights (0.016%) with 50 forward passes | Exp 7 failed from weights alone (succeeded only with attention-pattern tool). Gemma 3 270M math not improved (6.8%→≤7.7%). With 10/25 forward passes, loops barely went away. Authors: "capabilities are exciting but still limited… context length and harnesses" | OFFICIAL PAGE |
| Exploring WSP: Capabilities, Generalization, Limitations ("WSP-Scope") | Hu, Tang, Li, Zhu, Feng, Zhang, Chen, Hu; arXiv 2611.09382, 6 Nov 2026 | github.com/WSP-Scope/WSP-Scope-Project; homepage wsp-scope.github.io; code licence not checked; arXiv non-exclusive licence | Reasoning agent (model not named in abstract) | Qwen3.5-0.8B and Qwen3.5-9B; 16 editing trajectories, 7 benchmarks | Agentic, with validation | Up to +29.45 pts MATH-500, +4.42 GPQA Diamond, +36.72 IFEval, +17.11 SciBench; a 1,023-parameter edit gave +29.45. Math-edited checkpoint transfers: +3.03 GPQA, +12.18 IFEval, +20.10 SciBench; SciCode unchanged | 6 of 16 trajectories kept the original weights because improvements could not be validated; "outcomes vary substantially across trajectories" | PREPRINT |
| Can an LLM Actually Reason… or memorization on steroids? | N. S. Ahmed; arXiv 2611.08070, 5 Nov 2026; CC BY 4.0 | Not stated on abstract page | Claude Opus 5.5 | CNNs, ~125,000 parameters, 5 image datasets | None; all weights as text | Recovers CIFAR-10 vehicle/animal split from output-layer signs; infers ~3 optimizer steps from batch-norm statistics | Names CIFAR-10 for all three fast-food networks, calls KMNIST "MNIST" and a 99.57%-accurate SAT-6 network "CIFAR-10 animals". Under label permutation every interpreted class pair is wrong. Verdict: "local arithmetic plus dataset priors" rather than weight-flow tracing; mostly single runs | PREPRINT |
| WSP for auditing clinical decision networks | H. Nusrat, O. Nusrat; arXiv 2611.05341, 3 Nov 2026; CC BY 4.0 | github.com/hnusrat1/weightspace-rt | Claude Opus 5.5 | MLPs, 433–4,801 parameters | None (blind audit) | Named the broken rule in 16/18 flawed networks (95% CI 67–97%). Repaired each by changing a median of 3 parameters; fine-tuning also repaired all but "changed nearly every parameter" | Cleared only 2/5 healthy networks, found 1/3 hidden triggers. A simple per-flaw statistic found the same flaws, and black-box testing was faster. "cannot yet certify that a network is correct" | PREPRINT |
| WSP for Medical Imaging: Do We Still Need Training Data? | Lindholz, Ruppel et al. (14 authors); arXiv 2611.12066, 9 Nov 2026 | github.com/MaximilianLindholz/weight-space-programming-medical; licence not checked | Claude Opus 5.5 and GPT-6 Astra | Small LeNet-style CNN, 7 tasks in 4 modalities | None; single reply, no image access | Mean test AUC 0.719 (Opus) and 0.711 (Astra) on six MedMNIST tasks, above chance; compared with zero-shot MedSigLIP and Adam-trained same architecture | Authors conclude LLM-written weights do "not yet replace training data" | PREPRINT (UNVERIFIED: abstract page not re-fetched, read from search extracts) |
| WeightLoop: WSP with Experimental Feedback | M. Li, B. Li, … V. Leung, S. Z. Li; arXiv 2611.07319, 5 Nov 2026; CC BY 4.0 | Not stated | GPT-6 Astra writes a reusable editor once; no further LLM calls | ReLU-MLP encoder → 128-d embedding → linear readout. Only the 128 readout weights are editable. Full predictor 3,604,535 parameters. Also ridge coefficients and XGBoost leaf values | LLM writes code; editor runs numerically on cached activations | Edited readout beats random edits in 8/8 ranking settings and beats the original in 7/8. Sequential discovery D100: LC3 0.1757→0.2091, NBR1 0.1671→0.1878, HuH7 0.0038→0.0185. Ridge MSE −10.0%/−13.0%. HepG2 update changes 16 weights (0.00044%) | Gains small vs full 100-label refit (e.g., HepG2 B=20 edited 0.5419 vs full 0.6254); offline replay only; biology, not materials | PREPRINT |
| Can a Language Model Write the Weights? (MILP branching) | R. Butkeraites; arXiv 2611.09559, 6 Nov 2026; CC BY 4.0; text generated by Claude Opus 5.5 | github.com/butkeraites/llm-written-weights-or | Claude Opus 5.5 | Small MLP scorers; weights as JSON with a free-text note per weight | Forward-pass feedback | Independent-set branching 0.37× SCIP default time (18 instances, p<10⁻⁵). MARTA crew scheduling 0.63× | MIPLIB 2017: 19 vs 24 solved. On MARTA plain pseudocost did "exactly as well" (0.99, p=0.19): "the gains came from being cheap, not from what the LLM wrote" | PREPRINT |
| WSP from scratch on simple tasks | C. Singh; blog, 2 Nov 2026 | github.com/csinva/weight-space-programming-autoresearch | Claude (coding agent) | Hand-written small transformers, e.g., parity in 174 parameters (35 nonzero) | Full coding agent; no training allowed | 959 programs over 13 tasks; all 10 algorithmic tasks reached 100% within 3 attempts | On language tasks the agent fitted logistic regression on the eval pool, so the SNLI 100% is invalid: "the agent moved from writing mechanisms to fitting them" | BLOG-PRESS |
| Qwen 3.8 27B on my laptop can interpret model weights, too | S. Willison; blog, 3 Nov 2026 | Uses the Sparks prompts | Qwen 3.8 27B (local); Kimi K3.1 Pro | Exp 1 networks (17,253 weights) | None | Qwen identified Pac-Man, Pong and Breakout (3/4), failed Freeway. Kimi got Breakout in 9m41s / 19,493 reasoning tokens; Qwen took 46–65 min and 43,506 reasoning tokens per run | A "sufficiently experienced human… with a notepad and a pencil could get there" | BLOG-PRESS |
| "The 'Astra can read and write weights to improve Qwen' post is misleading" | M. Honnibal; blog, 3 Nov 2026 | n/a | n/a | n/a | n/a | Only Exps 1, 2 and 4 read raw weights, on 17K–172K-weight networks; the Qwen result used Python and forward-pass batches | Says the result shows Astra "can be prompted to devise and perform tasks that a human ML engineer could do" | THIRD-PARTY (UNVERIFIED: read via aggregators and Wikipedia, original not fetched) |
| OpenWSP | GitHub openwsp/openwsp | Repository; licence not checked | GPT-6 Astra via API | Targets Sparks Exp 8 replication | Modal + Hugging Face | No result yet; logs an "incompatible vLLM interface" for weight updates | Tooling incomplete | REPOSITORY |

### 2.2 What D establishes for your purposes

- **Serialisation.** Three formats are in use:
  - raw floats as text in one prompt (Sparks Exps 1, 2, 4, 5; arXiv 2611.08070; 2611.05341; 2611.12066);
  - JSON with a per-weight justification (2611.09559);
  - tensors in a Python kernel/sandbox that the LLM inspects with numpy (Sparks Exps 3, 6, 8; WSP-Scope; WeightLoop).

  The no-tool envelope tops out at 171,664 weights, and Honnibal's critique as reported puts the raw-weight-reading experiments at "17K to 172K". [OFFICIAL PAGE; THIRD-PARTY]
- **Token cost.** None of the primary WSP papers reports token or dollar cost. The only measured figures are Willison's: 19,493 reasoning tokens (Kimi K3.1 Pro) and 43,506 (Qwen 3.8 27B, 46 min on a laptop) to read one 17,253-weight network. [BLOG-PRESS]
- **Replication.**
  - The Qwen edit was rebuilt from logs and re-evaluated by Hugging Face's Ahsen Khaliq (stated by the Sparks authors). [OFFICIAL PAGE]
  - WSP-Scope reproduced large gains on Qwen3.5 but with high variance. [PREPRINT]
  - Willison partially reproduced Exp 1 with an open model. [BLOG-PRESS]
  - An alphaXiv commenter claims a reproduction. [THIRD-PARTY, UNVERIFIED]
- **Mechanism caution.** The headline Qwen gain comes from removing a looping failure. On a model that does not loop (Gemma 3 270M), Astra "could not improve it". The authors themselves state: "Editing weights could remove an obstacle that hid an ability, but it could not add an ability the model lacked." [OFFICIAL PAGE] For materials this means WSP is likely to fix identifiable pathologies, such as a head that ignores a feature or a mis-scaled output. It is unlikely to add predictive skill the embedding does not already carry. [Inference]
- **Regression, scientific ML, graph or equivariant networks.**
  - WeightLoop is the only regression/ranking use on scientific data (gene-perturbation assays).
  - The image-restoration "conjectures" note on ResearchGate proposes WSP for regression-type diffusion models but reports no results. [UNVERIFIED]
  - No WSP study on GNNs, equivariant networks, MLIPs, GPs or crystals was found.

## 3. Section A: BO surrogate

### 3.1 Prior work

| Item | Venue / id | Sense | What it does | Headline vs baseline | Limit | Grade |
|---|---|---|---|---|---|---|
| WeightLoop | arXiv 2611.07319 | Narrow WSP | LLM writes an editor that halves selected readout weights (k∈{4,8,16}, α∈{0.25,0.5}) using a pairwise ranking loss on new measurements; validated on support folds | See §2.1. Also beats affine recalibration in 3/4 ridge/XGBoost settings | No uncertainty; no GP; biology only; edits are attenuations only | PREPRINT |
| CAKE / CAKES (LLM-evolved GP kernels) | NeurIPS 2025 (arXiv 2509.17998); code github.com/richardcsuwandi/cake | LLM-written kernel expressions (not weights) | LLM acts as crossover/mutation operator over kernel grammar; BAKER ranks by BIC + EI | Suwandi et al. (NeurIPS 2025) state CAKE "consistently outperforms established baselines across a range of real-world tasks, including hyperparameter optimization, controller tuning, and photonic chip design"; the ~36% figure attributed to the earlier CAKES OpenReview version was not re-verified | Only discrete kernel expressions | PEER-REVIEWED (NeurIPS); REPOSITORY |
| Kernel Manifold | arXiv 2601.05371 | Counter-evidence | Compares BO over kernel space with an LLM-GA (modified CAKE, gpt-4o-mini) | LLM-GA "trail[s] by a wide margin"; "even pure exploration… generally outperforms the LLM-based approach" | Single weak LLM | PREPRINT |
| PFNs4BO | ICML 2023 (PMLR 202) | Broad sense: weight-free in-context surrogate | Transformer approximates the GP/HEBO posterior predictive in one forward pass | Strong on HPO benchmarks | Released model limited to 18 input dimensions; single-objective; EI/PI/UCB only | PEER-REVIEWED |
| TabPFN | Nature 2025 | Broad sense | Tabular PFN; in-context regression | Outperforms prior methods on datasets up to 10,000 samples | Out-of-distribution behaviour axis-dependent (next row) | PEER-REVIEWED |
| TabPFN on 1,346 HOIPs, leave-one-group-out | NeurIPS 2026 | Broad sense, materials | TabPFN vs RF/XGBoost under chemical out-of-distribution splits | Leave-one-cation-out MAE 0.222 eV vs 0.276/0.282 eV | Reverses when Pb is held out: "systematic prediction compression" | PEER-REVIEWED (conference page) |
| ICL foundation models for materials | npj Comput. Mater. 2026 | Broad sense | TabPFN on composition descriptors and on GNN embeddings | Surpasses SOTA composition models (authors' claim) | Small datasets | PEER-REVIEWED |
| GOLLuM | arXiv 2504.06265 | Broad sense | Deep-kernel GP whose LLM feature extractor is fine-tuned by marginal likelihood | — | Gradient-based | PREPRINT |

### 3.2 What has been shown to work

- LLMs can propose GP kernel structures that sometimes help (CAKE). An independent comparison found the opposite with a weak LLM. Treat it as unsettled. [PEER-REVIEWED; PREPRINT]
- Weight-free adaptation via PFNs works at small n. Two limits matter for you:
  - PFNs4BO's 18-dimension cap: frozen MACE/ORB embeddings must be reduced (PCA/PLS) first.
  - TabPFN's documented out-of-distribution compression on a held-out chemistry axis. That axis is your situation when a generator proposes new chemistries. [PEER-REVIEWED]
- LLM-written editors of a 128-weight readout can turn new measurements into persistent model updates without retraining (WeightLoop). [PREPRINT]

### 3.3 Open gaps (A)

1. No WSP study produces or preserves **predictive uncertainty**. WeightLoop edits point predictors only. Calibration after a weight edit (NLL, coverage, ENCE) is entirely unmeasured.
2. No LLM-written **mean function** or **monotone/symmetric readout** for a GP has been published. Weight edits as a carrier for physical constraints (Born stability, ε∞ ≥ 1, non-negative phonon free-energy curvature) are untested.
3. No hypernetwork emits a GP/deep-kernel head per materials task. The nearest analogue is Text-to-LoRA (Charakorn, Cetin, Tang, Lange, ICML 2025, PMLR 267, arXiv 2506.06105), which "can efficiently encode hundreds of LoRA adapters… While the compression is lossy, T2L maintains the performance of task-specifically tuned LoRA adapters"; its hypernetwork variants are reportedly about 5M–55M parameters (press figure, not confirmed in the paper). [PEER-REVIEWED; BLOG-PRESS]
4. No comparison of an LLM-proposed kernel against an LLM-written weight edit on the same BO budget.
5. LLM-written **acquisition functions** exist in the general BO literature: FunBO (Aglietti et al., Google DeepMind, arXiv 2406.04824, ICML 2025) builds on FunSearch to "learn new AFs written in computer code" and reports AFs that "generalize well in and out of the training distribution of functions, thus outperforming established general-purpose AFs" such as EI, UCB and probability of improvement. It writes acquisition-function code, not network weights. [PEER-REVIEWED]

## 4. Section B: MLIP

### 4.1 Model sizes vs the WSP envelope

| Model | Total parameters | Source | Readout/head parameters | Within no-tool WSP envelope (17K–172K)? |
|---|---|---|---|---|
| CHGNet v0.3.0 | 400,438 (Matbench lists 413k) | CHGNet paper / Matbench Discovery [PEER-REVIEWED; OFFICIAL PAGE] | Not stated | No (≈2.3× above) |
| SevenNet-0 | 842k (16.24M in GNoME reduced to 0.84M) | Matbench Discovery [OFFICIAL PAGE] | Not stated | No |
| SevenNet-omat / mf-ompa | 26M | arXiv 2507.21297 Table S1 [PREPRINT] | Not stated | No |
| MACE-MP-0 small / medium / large | 3,847,696 / 4,688,656 / 5,725,072 | mace-foundations release page [REPOSITORY] | Not stated. Architecture: linear readouts on all layers except the last, which is a one-layer MLP (16 hidden in the MACE paper) [PEER-REVIEWED]. My estimate: ≈2.2k weights, <0.1% of the model [Inference] | Head yes (estimated); model no |
| MACE-MPA-0 | ~9M | UMA paper Table 3 (secondary) [PREPRINT] | Not stated | No |
| MatterSim v1 5M / Graphormer | 4.55M / 182M | Matbench / MatterSim paper [OFFICIAL PAGE; PREPRINT] | Stress head trained separately after freezing (no count) | No |
| ORB-v3 | ~25M (Matbench: 25.5M) | Orb-v3 paper; Matbench [PREPRINT; OFFICIAL PAGE] | Confidence head with hidden width 128; no counts for energy/force/stress heads | No |
| eSEN-30M-OAM | 30M | UMA paper [PEER-REVIEWED, NeurIPS 2025] | Not stated | No |
| UMA-S / UMA-S-1.2 / UMA-M / UMA-L | 150M / 290M / 1.4B / 700M total; ~6M (6.6M in Table 3) / 6M / ~50M / 700M active | UMA paper [PEER-REVIEWED] | "a single task-independent node-wise feed-forward block" (no count) | No |

The upshot: no-tool WSP can reach only the final readout of a MACE-class model, never the message-passing layers. Tool-assisted WSP has reached 0.8B–9B parameters in LLMs, but only for a single-direction failure. Nobody has tried it on equivariant tensors, where an edit must respect irreps to preserve E(3)-equivariance. [Inference]

### 4.2 Prior work (broad sense)

| Item | Venue | Method | Finding | Grade |
|---|---|---|---|---|
| MACE v0.3.15 release | GitHub ACEsuit/mace | LoRA in equivariant o3.Linear, nn.Linear and FullyConnectedNet layers; merged back after training | `--lora_rank=4` example on MACE-MH-1 | REPOSITORY |
| Fine-tuning MLIP foundation models: strategies | arXiv 2606.12704 | Equivariant LoRA, pseudo-labelled replay, E0 re-estimation in MACE | Rank-4 LoRA ≈3% of MACE-OMat-medium trainable parameters. "foundation model quality, correct E0 initialisation, and well-chosen hyperparameters… routinely exceeds that of the fine-tuning strategy itself"; parameter-efficiency motivation "much weaker" for MLIPs | PREPRINT |
| ELoRA / efficient fine-tuning of atomistic foundation models | ChemRxiv 2025 | Equivariant LoRA for MACE and SevenNet vs full, partial-freeze, from-scratch | (E)LoRA comparable to or better than full fine-tuning | PREPRINT |
| PEFT of MLIPs for phonon and thermal properties | arXiv 2604.01017 | Transfer learning, multi-head, LoRA (Equitrain) on MACE-MP-0b3 | All strategies improve phonons, thermal and elastic properties; material-specific gains exceed differences between foundation models | PREPRINT |
| Frozen transfer learning (mace-freeze) | npj Comput. Mater. 2025 | Freeze lower layers, refit the rest | Matches from-scratch models with less data | PEER-REVIEWED |
| Meta-learning across levels of theory (Reptile) | npj Comput. Mater. 2024 | Pre-train across multiple QM levels, refit to MP2 | Better than naive joint fitting | PEER-REVIEWED |
| UMA Mixture of Linear Experts | NeurIPS 2025 | y = Σ αₖ Wₖ x, routing on a global embedding that includes the DFT task, charge and spin | Effectively composes per-system weights from 32 experts; this is the closest existing analogue to "weights generated per level of theory" | PEER-REVIEWED |

### 4.3 Open gaps (B)

1. **Task arithmetic / merging of fine-tuned MLIPs:** no paper found. LoRA deltas (e.g., Nb-Ti and Nb-Hf fine-tunes from the same MACE base) have never been added, negated or merged and tested on forces, phonons or elastic constants.
2. **Hypernetwork-generated MLIP adapters** conditioned on composition or functional: none found. UMA's MoLE is the nearest thing, but it is trained end-to-end, not an external hypernetwork.
3. **Weight-space interpretability of equivariant GNNs** (reading MACE's product-basis or readout weights): nothing published, with or without LLMs.
4. **Multi-fidelity heads edited without gradients**, e.g., an LLM-written correction head from PBE to r2SCAN on top of MACE's shared descriptor: none.
5. Exact readout-head parameter counts are not published for any of the named models. They must be counted from checkpoints.

## 5. Section C: generative model

### 5.1 Prior work

| Item | Venue | Size | Steering method | Sense | Grade |
|---|---|---|---|---|---|
| MatterGen | Nature 2025; arXiv 2312.03687 | 46.8M (Hugging Face model card; not split into base vs adapters) | Adapters: property embedding + one two-layer MLP adapter before each of 4 message-passing layers + zero-initialised mix-in; classifier-free guidance; fine-tuned with labelled sets such as bulk modulus N≈5,000 | Broad (gradient-trained adapters) | PEER-REVIEWED; REPOSITORY |
| DiffCrysGen property adapters | arXiv 2607.21849 | Not stated | MatterGen-style property-specific adapter branches in a U-Net; all weights optimised jointly | Broad | PREPRINT |
| MatInvent | ICLR 2025 | — | RL fine-tuning of a crystal diffusion model with reward-weighted KL | Broad | PEER-REVIEWED |
| SPARC | arXiv 2609.13468 | — | RL fine-tuning in a symmetry-constrained asymmetric-unit representation | Broad | PREPRINT |
| CrystalFormer RL fine-tuning | arXiv 2504.02367 | — | MLIP / property-model rewards for an autoregressive crystal transformer | Broad | PREPRINT |
| Training-free adaptive constraint guidance | arXiv 2604.13354 | — | Inference-time guidance on volume and coordination motifs; "complementary to fine-tuning" and effects sometimes "do[] not survive" energy filters | Guidance (no weight change) | PREPRINT |
| CrystalREPA | arXiv 2605.08960 | — | Aligns generator representations to universal-MLIP features; MatterGen adapter baseline (200 epochs) | Broad | PREPRINT |
| ADiT | ICML 2025 (arXiv 2503.03965) | VAE 51M; DiT-S 32M, DiT-B 130M (also stated as 150M in Appendix D), DiT-L 450M | Latent diffusion transformer | — | PEER-REVIEWED |
| CrystalFlow | Nat. Commun. 2025 / arXiv 2412.11693 | Not stated in arXiv (GNN hidden 512, 6 layers) | Flow matching, pressure-conditioned | — | PEER-REVIEWED |
| Unified concept editing / ESD / meta-unlearning | ICCV 2025, NeurIPS 2024 (image diffusion) | — | Closed-form or fine-tuning concept erasure | Broad, not crystals | PEER-REVIEWED |

### 5.2 Open gaps (C)

1. **No LLM weight edit of any crystal generator.** At 32M–450M parameters these sit in the tool-assisted regime, where WSP has only removed a single failure direction in LLMs.
2. **No adapter arithmetic for multi-property conditioning.** MatterGen fine-tunes multi-property adapters jointly. Summing separately trained adapters (e.g., bulk-modulus + chemical-system) is untested.
3. **No concept erasure or unlearning carried to crystals.** Examples would be erasing a toxic element, a known structure prototype, or a radioactive species.
4. **No LLM-written guidance or reward network.** All reward models are trained property predictors or MLIPs. The Sparks MinAtar result (zero-shot policy networks of about 20k weights) suggests an LLM could write a small physics-rule scorer, for example a Pettifor/radius-ratio plausibility net. Untested. [Inference]

## 6. Ranked research ideas

Context for all ideas:
- Your frozen embeddings would be per-structure pooled invariant (L=0) features, e.g., MACE-MP-0 medium with 128 scalar channels per interaction layer → about 256-d after concatenating 2 layers and mean-pooling. [Inference; check the actual dimension in your pipeline]
- Datasets: Matbench `matbench_log_kvrh` / `log_gvrh` (10,987 entries each), `matbench_dielectric` (4,764), `matbench_phonons` (1,265). [Sizes from the Materials Project "Benchmark info for matbench_v0.1" page and the matminer dataset summary]
- For the refractory focus: Nb-Ti-Zr-Hf-W-Mo BCC subsets of Materials Project/Alexandria with elastic tensors. C103 (Nb-10Hf-1Ti wt%) is the anchor composition.

An analogy used below: if gradient fine-tuning is "re-sanding the whole table", WSP is "tightening one specific screw you can name". It only helps when a single screw is loose.

### Idea 1 (rank 1): WeightLoop for crystals — LLM-written readout editor inside the BO loop
- **Hypothesis.** An LLM-written, fixed editing program updates a small head on frozen embeddings between BO rounds. It matches GP refitting on regret at lower latency, and preserves calibration when paired with a residual GP.
- **Smallest experiment.**
  - Data: `matbench_log_kvrh`. Hold out the top 5% as "discoveries"; start with 50 labels; 10 rounds × 20 acquisitions.
  - Model: head = linear or 256→32→1 MLP (≈8.2k weights; well inside the 17k–172k no-tool envelope) on MACE-MP-0 medium embeddings, plus an exact GP on the head's residuals for uncertainty.
  - Editor: GPT-6 Astra or Claude Opus 5.5 writes the editor once (WeightLoop recipe: cached activations, candidate rescalings of top-k output weights, 3-fold support validation).
  - Loss: pairwise ranking loss (WeightLoop Eq. 3) plus MSE.
  - Metrics: simple regret, top-5% recall at 200 labels, NLL, 90% interval coverage, ENCE.
- **Baselines to beat.**
  - GP (Matérn-5/2, ARD) refit each round on the same embeddings (current standard);
  - affine recalibration of the head;
  - last-layer Adam fine-tune;
  - TabPFN on 18 PCA components;
  - random-coordinate edits (WeightLoop's permuted control).
- **Compute.** CPU or 1 GPU-hour for embeddings. LLM cost is one editor-writing session.
- **Main risk.** As in arXiv 2611.09559, any gain may come from "being cheap", not from the LLM. Only the permuted-edit control can separate the two.

### Idea 2 (rank 2): LLM-written physics prior mean for the GP
- **Hypothesis.** A GP whose prior mean is a small LLM-written network encoding known trends beats a constant-mean GP in the first 20–50 iterations. Example trends: bulk modulus rising with valence electron concentration and cohesive energy in BCC refractories; ε∞ ≥ 1; positive Born-stability determinants.
- **Smallest experiment.**
  - Input: 20–40 composition descriptors (VEC, mean atomic radius, electronegativity spread, mixing enthalpy). Output: 1 scalar.
  - Network: 40→16→1 (≈680 weights), written zero-shot from a natural-language rule sheet, then frozen.
  - Task: elastic moduli on refractory BCC alloys (Nb/Mo/W/Ta/Ti/Zr/Hf), 20 seeds.
  - Metrics: regret at 10/20/50 labels; NLL.
- **Baselines.** Constant and linear-mean GP; a GP with the same mean fitted by gradient descent on the same initial labels; a CAKE-style LLM kernel.
- **Main risk.** The Gemma result: WSP cannot add knowledge the LLM does not have. Wrong priors cost early iterations, so log marginal likelihood must be able to down-weight the mean (add a learnable scale).

### Idea 3 (rank 3): Weight-space audit of your GP-routing gate and deep-kernel head
- **Hypothesis.** As in arXiv 2611.05341 (16/18 flaws found), an LLM reading the weights of your small deep-kernel feature extractor or routing classifier can flag shortcut features before they mislead the loop. Example shortcuts: reliance on cell volume or on a single element channel.
- **Smallest experiment.**
  - Plant 3 flaws (a confound, a threshold shift, a trigger element) in 18 copies of a ≤5k-weight gate trained on your MLIP-vs-DFT routing data.
  - The LLM audits blind. Repairs are tested on held-out structures.
- **Baselines.** Per-flaw summary statistics and black-box behavioural tests. Both matched or beat the LLM in 2611.05341.
- **Main risk.** Low marginal value over simple statistics. The 2611.05341 authors note it "cannot yet certify that a network is correct".

### Idea 4 (rank 4): Zero-gradient multi-fidelity readout edit on MACE
- **Hypothesis.** The final MACE readout (estimated ≈2k weights) can be edited by an LLM in a Python sandbox to map PBE energies/stresses to a higher-fidelity functional for your alloy chemistries. The analogy is the WSP-Scope 1,023-parameter edit.
- **Smallest experiment.**
  - Data: 200 r2SCAN (or PBEsol) labels on Nb-Hf-Ti BCC/SQS cells near C103; 50 forward-pass budget.
  - Target: elastic constants C11, C12, C44 via finite strain.
  - Loss: energy/stress MAE, plus C_ij MAE vs DFT.
- **Baselines.**
  - MACE multi-head fine-tune with replay;
  - LoRA rank 4 (`--lora=True --lora_rank=4`);
  - frozen-backbone readout refit by Adam (the honest gradient baseline).
- **Compute.** 1 GPU, hours.
- **Main risk.** Readout-only capacity may be insufficient. Arxiv 2606.12704 shows fine-tuning strategy matters less than E0 and hyperparameters, so the LLM may only rediscover E0 re-estimation.

### Idea 5 (rank 5): Task arithmetic on MACE LoRA deltas for refractory alloys (broad sense)
- **Hypothesis.** LoRA deltas ΔNb-Ti, ΔNb-Hf and ΔNb-Zr from one MACE base can be summed (θ = θ₀ + λΣΔ) to give a usable Nb-Hf-Ti potential without joint training.
- **Smallest experiment.**
  - Data: three binary fine-tunes (500 DFT frames each); 200 ternary test frames.
  - Metrics: force MAE, C_ij, phonon DOS.
  - Sweep: λ ∈ {0.3…1.0}.
- **Baselines.** Joint LoRA on the union data; base MACE; per-binary models.
- **Main risk.** Equivariant LoRA deltas may interfere strongly. There is no prior evidence either way. This is a clean "first paper" gap.

### Idea 6 (rank 6): LLM-written guidance/reward net for the crystal generator
- **Hypothesis.** An LLM can zero-shot write a small plausibility/property scorer that, used as a guidance or rejection gate in front of your expected-improvement gate, raises the SUN-and-in-target yield. Inputs: composition one-hot plus a pooled embedding (~300-d); network about 300→32→1, ≈9.7k weights. Encoded rules: radius ratios, VEC windows, avoidance of known unstable prototypes.
- **Smallest experiment.** 10k MatterGen samples, filtered by (i) the LLM-written net and (ii) a trained MLP of equal size. Measure the MLIP-relaxed E_hull<0.1 eV fraction and the property-hit rate per DFT call.
- **Baselines.** Trained classifier of equal size; MatterGen property adapter with classifier-free guidance; training-free guidance (2604.13354).
- **Main risk.** The "cheapness" confound again. Also, the LLM's rule sheet may simply restate what MatterGen already learned.

### Idea 7 (rank 7): Adapter arithmetic on MatterGen (broad sense)
- **Hypothesis.** Separately trained MatterGen adapters (e.g., bulk modulus; chemical system Nb-Ti-Hf) can be summed for joint conditioning.
- **Smallest experiment.** Two adapters at 200 epochs each; generate 2,000 structures; compare against a jointly trained two-property adapter.
- **Main risk.** The zero-initialised mix-in outputs add in the atom-embedding stream, so interference is likely. Compute: one to a few GPU-days.

**Ranking logic.** Ideas 1–3 sit inside the documented WSP envelope and give a publishable answer in weeks. Ideas 4–5 test the envelope's edge on equivariant models. Ideas 6–7 are useful but compete with mature gradient-based steering.

## 7. What is not published

Nothing exists, as far as this search found, for any of the following:
- WSP (narrow sense) on a GP, deep kernel, kernel hyperparameters or acquisition function;
- WSP on any MLIP, any equivariant network or any GNN;
- WSP on any crystal or molecular generative model;
- WSP with uncertainty calibration measured after the edit;
- task arithmetic or model merging of fine-tuned MLIPs;
- hypernetwork-generated MLIP adapters conditioned on chemistry or functional;
- adapter arithmetic or concept erasure in crystal generators;
- a peer-reviewed WSP paper of any kind;
- reported token or dollar cost in any primary WSP paper;
- published readout-head parameter counts for MACE, ORB-v3, UMA, eSEN, MatterSim, SevenNet or CHGNet;
- a stated total parameter count for CrystalFlow.

The authors' WSP benchmark and harness were announced but are not released.

## 8. Caveats

- **Source quality.**
  - The founding WSP work is a blog post, and every follow-up is an un-reviewed preprint from the last nine days. Several are single-author.
  - One (2611.09559) was itself written by Claude Opus 5.5.
  - Results mostly come from single runs and two frontier models (GPT-6 Astra, Claude Opus 5.5).
- **Conflicts.**
  - ADiT DiT-B is stated as both 130M and 150M in the same paper.
  - UMA-S active parameters are given as 6M and 6.6M.
  - CHGNet appears as 400,438 and 413k.
  - In each case both figures are reported above.
- **Unverified items.** The Honnibal critique (read via aggregators), the 2611.12066 abstract (search extracts only), the ~36% CAKES figure, the 5M–55M Text-to-LoRA size range, and all code licences except arXiv text licences were not re-fetched or not checked. FunBO (arXiv 2406.04824) and the Matbench dataset sizes were verified at the enrichment stage.
- **Inferences.** The ≈2.2k MACE readout estimate, the ≈256-d embedding dimension and the network sizes proposed in §6 are inferences, not paper numbers.
- **Source list.** A numbered source list is omitted here because of the output format of this report. Every source is named inline by arXiv id, venue or URL host, and all were accessed 2026-11-11.