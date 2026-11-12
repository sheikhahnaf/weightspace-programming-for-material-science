# E1: an LLM-programmed readout head on frozen ORB embeddings (BO surrogate)

**Question.** Can an LLM write or edit the weights of a small readout head on frozen ORB embeddings so that it predicts an elastic property as well as the same head trained by gradient descent, and does a deep-kernel GP built on that head keep its calibration?

**Why here.** The head `50 -> 32 -> 32 -> 1` has 2,721 weights, about 17,500 characters as text. That is below every size at which weight-space programming has been reported to work from raw weights (17,253 to 171,664). The sibling paper names the frozen embedding and the missing calibration study as its own limits.

**Nearest prior work.** WeightLoop (arXiv 2611.07319, preprint): an LLM writes, once, a program that edits the 128 readout weights of a frozen encoder after each batch of assay measurements. Its edited readout beat the original in seven of eight settings but stayed below a full refit, it carries no uncertainty, and its data are biological assays. Butkeraites (arXiv 2611.09559, preprint) found that where LLM-written scoring networks won, "the gains came from being cheap, not from what the LLM wrote". Both shape the controls below.

**Data.** matminer `elastic_tensor_2015` (1,181 structures), target `K_VRH`, mean-pooled `orb_v3_conservative_inf_omat` embeddings, PCA 50 fitted on each training split, n_train = 500, five seeds. `make_features.py` computes the embeddings with the published benchmark's featurizer, imported read-only.

**Baselines** (`run_baseline.py`): exact GP, ridge, and the MLP head trained with AdamW. The published reference for ORB + GP at PCA50 on the eight elastic targets is mean R² 0.803, Spearman 0.842; `run_baseline.py` must reproduce that neighbourhood on `K_VRH` before any LLM arm is run.

**Arms.** Each arm is a prompt built by `wsp.build_prompt` and a reply parsed by `wsp.load_weights` or `wsp.parse_edits`.

| Arm | What the LLM gets | What it returns | Forward passes allowed |
|---|---|---|---|
| A. read | trained head, no task name | what the head predicts and which inputs drive it | 0 |
| B. repair | head trained on data with a planted flaw (label shift above a threshold; one input duplicated as a leak) | edits | 0 |
| C. edit for bias | trained head plus its residuals on the top decile of the training set | edits that remove the underprediction of high values | 0, then 10, 25, 50 |
| D. write | zero head, the PCA loadings' meaning is not available, 20 labelled training rows as text | full weights | 0, then 50 |
| E. prior mean | zero network `d -> 16 -> 1` on named composition descriptors (valence electron concentration, mean radius, electronegativity spread) and a sheet of known trends | full weights, used as the GP's mean function with a learnable scale | 0 |

Arm E keeps the GP, so its uncertainty is the GP's own; the learnable scale lets the marginal likelihood switch a wrong prior off. Arm C targets a measured failure of the published loop: its GP underpredicts the best candidates by about 42.5 GPa.

**Measures.** Holdout R² and Spearman per arm against the three baselines; number and fraction of weights changed (`wsp.diff`); for the deep-kernel variant (GP on the head's last hidden layer), 95% interval coverage before and after the edit; prompt and reply tokens counted with the model's own tokenizer.

**Controls.** The same prompt with weights shuffled within each tensor (the memorisation control of arXiv 2611.08070). Random edits of the same count and size (WeightLoop's control). Affine recalibration of the head's output, which is the cheapest fix for a bias. A "gradient with the same budget" arm: AdamW given the same number of forward passes as arm C or D. For arm E, a constant-mean GP and the same mean network fitted by gradient descent on the initial labels.

**Stop rule.** If arm A cannot name the dominant inputs of a trained head better than the shuffled control in five of five seeds, arms B to D are not run and the result is written up as a negative.

**Tasks actually wired up** (`src/wsp/tasks.py`, from data copied into `data/`): `loop_bulk_modulus`, `loop_heat_capacity`, `mpea_yield_strength`, `ti_alloy_youngs_modulus`, `matbench_log_bulk_modulus`. The matminer elastic set described under **Data** is a sixth task that still needs its ORB features computed with `make_features.py`.

**Scripts.** `run_baseline.py` (GP, ridge, trained head on every task); `llm_arm.py prompt|score` (arms B as a planted leak, C and E; code in `src/wsp/arms.py`); `run_bo.py` (pool-based BO with and without a written prior). Arms A and D have no prompt builder yet.

**Status (2026-11-11).** Baselines run on five tasks, five seeds. Pilot of arm C (three single runs, one a shuffled control) and arm E (two tasks, one reply each) with Claude Fable 5.2 and no code execution. Results and what they change: `docs/results/2026-11-11-e1-pilot.md`. Short version: arm C as prompted showed no weight reading (the model made the same output-layer stretch on shuffled weights); arm E gave networks that rank alloys at ρ 0.54 and 0.63 with no data and raised GP ranking at 10 to 20 labels, inside seed noise on R².

**Status, round 2 (2026-11-11).** Arm B run as a planted-leak repair (four runs and a shuffled control), arm E replicated (three replies per task) and tested inside BO (eight seeds). Results: `docs/results/2026-11-11-round2.md`. Short version: the model found the leak in 2 of 4 runs, the same two a weight-norm statistic finds; the written priors' ranking gain at few labels did not carry into BO except for one reply of three on the titanium task.

**Status, round 7 (2026-11-12).** Written 15 → 16 → 1 networks on crystal descriptors used as the prior mean, and their hidden layer as inputs, of the closed-loop embedding GP (bulk modulus 6 runs, heat capacity 5 runs; no new model runs). Results: `docs/results/2026-11-12-round7.md` section 2.
