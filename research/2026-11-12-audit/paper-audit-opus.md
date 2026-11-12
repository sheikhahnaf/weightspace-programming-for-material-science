# Pre-submission audit of `weightspace-programming-for-material-science-paper`

The paper changed while I was auditing it. Commits `cfdaa01` (10:39, title) and `a68d092` (10:41, table-reader experiment removed) landed after I started, so I dropped my findings on the table reader. `methods.tex` also has an uncommitted edit (10:45) that I read as it stands. Every other section I checked was unchanged after I read it.

## A. Wrong numbers

**A1. Cost paragraph (results.tex:153).**
- Text: "Opus 5.5 took a median of 7 minutes and about 130,000 output tokens on the experimental alloy tasks … Fable 5.2 took about one minute and 16,000".
- Source: `runs_audit.json`, the 15 alloy write runs per model:
  - Opus: median 229 s, 72,563 output tokens.
  - Fable: 47 s, 9,377 tokens.
  - Sonnet 16 s; Haiku 21 s.
- The paper's figures match no subset. The closest is Opus writing with facts on Thermo-Calc (8.8 min, 158k tokens).
- Fix: "a median of about 4 minutes and 73,000 output tokens …; Fable 5.2 under a minute and about 9,400".

**A2. Fable values left over from before commit `1bf45a02`.** That commit (10:24) added the two unsuffixed Fable replies, so Fable now has 3 replies on these tasks. The BO Fable arm already used all 3.
- tab_regression.tex:13, Fable, Ti Young's modulus: R² 0.04 → 0.02; rescaled 0.26 → 0.25.
- tab_regression.tex:17, Fable, MPEA yield strength: rescaled 0.34 → 0.35.
- results.tex:146, "they find 0.31 and 0.15 of it": Fable 0.15 → 0.17 (`standalone/summary.json`, `mpea_yield_strength|fable`, recall).

**A3. Rule-of-mixtures range (abstract:1, results.tex:12).**
- Text: "−0.72 to 0.28".
- Source: `mpea_yield_strength|handbook` ρ = 0.2746; Table 1 itself prints 0.27.
- Fix: "−0.72 to 0.27".

**A4. "One target defeats every predictor" (results.tex:14).**
- Text: "One target defeats every predictor: the α transus of titanium alloys (ρ ≤ 0.30)".
- Source: the Co–Cr–Cu–Fe–Ni–Ti freezing range scores lower for every predictor: 0.21, 0.20, 0.10, 0.06, 0.07 (supp_tables.tex:73).
- Fix: "Two targets defeat every predictor: the freezing range of Co–Cr–Cu–Fe–Ni–Ti (ρ ≤ 0.21) and the α transus of titanium alloys (ρ ≤ 0.30)."
- Related, results.tex:148: "(relative areas 0.88 to 1.19)" fits only the Al–Cr–Mo–Nb–Ti freezing range. The α transus spans 0.68–1.20. Give both ranges.

**A5. Titanium-hardness regret (results.tex:88).**
- Text: "the regret on titanium-alloy hardness is gone after three steps".
- Source: `bo_select/init5_steps25/ti_alloy_hardness/select_opus__seed*.json`.
  - Mean regret goes 139.6 → 89.8 → 7.5 → 7.5 → 2.0 HV, then stays at 2.0.
  - Every Opus seed ends at 2.0 HV; none finds the best alloy.
  - The plain GP reaches 1.6 HV at step 21 and finds the best alloy in 4 of 20 seeds.
- Fix: "falls from 140 to 2 HV within four steps (no Opus seed finds the single best alloy), where the plain process needs about twenty steps".

**A6. Regression R² of the rule (results.tex:20).**
- Text: "where the rule of mixtures is far below zero because its scale is wrong".
- Source: MPEA yield strength R² = +0.06; Ti yield strength −0.79.
- Fix: "below zero on four of the five tasks".

**A7. BNN starting weights (results.tex:131).**
- Text: "… nothing for Hamiltonian Monte Carlo".
- Source: `bnn_summary.json`, mean at 10 and 20 labels: HMC with written start 0.40 vs zero-centred 0.45; better in only 2 of 24 cells.
- Fix: "slightly lowers it for Hamiltonian Monte Carlo (0.45 to 0.40)".

**A8. BNN at 50+ labels (supp_tables.tex:11).**
- Text: "With 50 labels or more all differences shrink to a few hundredths."
- Source: at 50 and 200 labels:
  - Dropout with written start: ρ 0.68 vs 0.74.
  - HMC with written prior: 0.61 vs 0.67.
  - Dropout coverage with written start: 0.96 vs 0.78.
  - MPEA hardness at 200 labels, dropout with written start: 0.67 vs 0.82.
- Fix: "With 50 labels or more the prior-mean differences shrink to a few hundredths; starting weights still lower ranking by about 0.05 and raise dropout coverage from 0.78 to 0.96."

**A9. Heat-capacity descriptors (supp_tables.tex:40).**
- Text: the raw descriptors help "once it has 20 labels or more".
- Source: `structure_prior` heat capacity, descriptors vs plain GP: 0.38 vs 0.15 at 5 labels (13/2, p = 3e-4); 0.66 vs 0.31 at 10.
- Fix: "help at every label count".

**A10. MLIP edits (supp_other.tex:44).**
- Text: "Six of the sixteen chosen edits sit at 5.2 meV/atom".
- Source: `chains.json`, test-half energy of the chosen edits: 5.16, 5.18, 5.25, 5.17, 5.24, which is five.
- Fix: "Five".

## B. Claims the results contradict

**B1. "Matches the extrapolation everywhere".**
- Where:
  - abstract: "the model matches the extrapolation everywhere";
  - introduction.tex:20: "match or exceed … on every kind of target";
  - results.tex:14: "at least as well as the extrapolation on every kind of target".
- Source:
  - Table 1 by kind: Opus + facts 0.82 vs 0.84 (solidus) and 0.74 vs 0.76 (freezing range); Fable + facts 0.82 and 0.70.
  - Per target: Opus + facts is more than 0.05 below the extrapolation on 9 of 35 targets; Fable + facts on 12.
  - BO: Fable + facts wins 16 targets vs 18 for the extrapolation; median relative areas 0.24 and 0.35 vs 0.17.
- Fix: "comes within 0.02 (Opus) and 0.06 (Fable) of the extrapolation on solidus and freezing range, exceeds it on phase fractions (0.71 vs 0.63) and overall (0.73 vs 0.70); per target it trails by more than 0.05 on 9 (Opus) and 12 (Fable) of 35".

**B2. "Improves from there" (results.tex:31).**
- Text: "starts where the network alone stands and improves from there: 0.69 … 0.95 on crystals".
- Source:
  - Figure 3a, Opus: 0.69 / 0.67 / 0.69 / 0.75 at 5 / 10 / 20 / 50 labels.
  - Figure 3c: 0.95 / 0.94 / 0.90 / 0.90, which falls.
  - Only Thermo-Calc rises (0.64 → 0.83).
- Fix: "starts where the network alone stands and changes little up to 20 labels on alloys and crystals (crystals fall from 0.95 to 0.90); on Thermo-Calc targets it rises from 0.64 to 0.83 at 50".

**B3. Raised regret (abstract).**
- Text: "they raise it on the fifth experimental task, though not significantly, and on no computed target".
- Source: Opus's relative area is above 1 (not significant) on four computed targets: Al–Co–Cr–Fe–Mn–Ni solidus 1.18 and main phase 2.32, Ni γ′ 1.45, Hf–Mo–Nb–Ta–Ti–Zr main phase 1.11 (supp_tables.tex:113–135).
- Fix: "raise it, not significantly, on the fifth experimental task and on four computed targets, and significantly on none".

**B4. Rule ranks backwards (results.tex:12).**
- Text: "on hardness and yield strength it ranks alloys backwards".
- Source: MPEA yield strength ρ = +0.27.
- Fix: "on both hardness tasks and on titanium yield strength".

**B5. Prompt contents (methods.tex:4; results.tex:14).**
- Text: "No data is shown: … no statistic of the pool" and "with nothing but the names of the elements and the definition of the target".
- Source, the prompts:
  - Alloys name the dataset with its reference and the pool size, e.g. "Measured titanium alloys (Salvador et al., Sci. Data 9:188, 2022). 237 alloys." and "(Borg et al., Sci. Data 7:430, 2020). 530 alloys."
  - Thermo-Calc prompts give the pool's composition range and step, the database, and the row count.
  - Crystal prompts give typical input ranges (`filter_arm.py` `prompt()`).
- Fix: "No labelled example is shown. The prompt names the data source (for measured sets, the published dataset and its reference), the number of candidates, the composition range of computed pools and typical input ranges for crystals."
- Also add to Limits that naming the dataset invites recall.

**B6. Replies per model (methods.tex:6).**
- Text: "with two or three replies per model and task".
- Source: heat capacity has 1 reply each from Sonnet and Haiku. The folders `filter_Cp__{sonnet,haiku}__rep2/3` and `filter_Cp__{opus,fable}__rep3` hold only `prompt.txt` and `meta.json`; they were never run.
- Fix: "… except one reply each from Sonnet and Haiku on heat capacity".

**B7. Hidden-unit sparsity (results.tex:16).**
- Text: "about a third of the 16 hidden units (median … 10 on crystals)".
- I recomputed the medians (5, 6, 10); they are correct, but 10 of 16 is not a third.
- Fix: "5 or 6 of the 16 hidden units on alloys and Thermo-Calc targets, 10 on crystals".

## C. Claims stronger than the results

**C1. Phase fractions.**
- Where: abstract "better on phase fractions"; introduction.tex:18 "ahead of it on phase fractions"; results.tex:14; discussion.tex:3 "worth more than a polynomial".
- Source: per target, Opus beats the extrapolation on 7 of 16 phase-fraction targets and Fable on 9. The mean lead comes from three targets: Al second phase (0.98 vs 0.58), steel austenite (0.76 vs 0.28), Ni other phase (0.83 vs 0.48).
- Fix: "ahead on average (0.69 vs 0.63), on 7 of 16 targets for Opus".

**C2. Calibration.**
- Where: results.tex:37 "restores coverage to 0.79, 0.88 and 0.98"; abstract "for the error bars to hold".
- Source: nominal coverage is 0.95; plain GP covers 0.76 / 0.86 / 0.86. On alloys at 20 labels every fit covers only 0.66–0.69 (`joint_mean/static_summary.md`).
- Fix: "raises coverage of the 95% interval to 0.79, 0.88 and 0.98 (plain process 0.76, 0.86, 0.86)". Abstract: "or the intervals are narrower than the plain process's".

**C3. "Simple rule" vs the extrapolation.**
- Where: results.tex:150 "a short rule that uses no labels"; abstract "targets for which no simple rule exists"; introduction.tex:14 "the cheapest rule that uses the same information".
- Problem: the extrapolation uses 31–105 Thermo-Calc sub-system calculations per system (`data/calphad/README.md`, "Facts computed"). The no-facts arm does not see that information.
- Fix: call it "an extrapolation from computed sub-system data".

**C4. "Exact labels" (introduction.tex:14; methods.tex:11).**
- Source, `data/calphad/README.md`:
  - The solidus is taken from a 4 K bisection bracket for 180/200 Ti, 162/200 Al and 149/200 Co–Cr–Cu–Fe–Ni–Ti rows ("if that fails the middle of the bracket is reported").
  - The α transus is censored at 773 K.
  - Rows whose quantity failed are dropped (α transus: 191 of 200).
- Fix: "equilibrium values from one database, solidus and liquidus to within 4 K".

**C5. Smaller models (discussion.tex:9).**
- Text: "the two smaller models wrote clearly weaker networks".
- Source:
  - Sonnet ranks Ti Young's modulus at 0.65 vs Opus 0.64.
  - Sonnet has the best CrystalFlow hit share (0.56); its CrystalFlow ρ is 0.88, the same as Opus.
- Fix: "weaker on average and less even".

**C6. Follow-up work (introduction.tex:5).**
- Text: follow-up work tested it on "classifiers, control policies, clinical risk scores and combinatorial solvers".
- Problem: control policies are in the original Takehi et al. work. The follow-ups are language-model editing (Hu), CNN classifiers (Ahmed), clinical networks (Nusrat), assay readouts (Li) and MILP scoring (Butkeraites).

**C7. Task vectors (supp_other.tex:4).**
- Text: "the weight changes of fine-tuned crystal generators add, scale and compress".
- Source: no CrystalFlow variant is significant (`variants_summary_cf.md`).
- Fix: "of MatterGen".

## D. Not disclosed

**D1. Repeated sessions (methods.tex:6, "all 358 runs … passed").**
- 7 of the 358 main-text runs have `attempts = 2` in `runs_audit.json`:
  - `write__ti_alloy_hardness__opus__rep1`
  - `write__ti_alloy_yield_strength__sonnet__rep1`
  - `write__ni_superalloy_gamma_prime_fraction__opus__rep1`
  - `write__steel_austenite_fraction__opus__rep1`
  - `writepd__al_refractory_freezing_range__opus__rep1`
  - `writepd__al_refractory_solidus__opus__rep1`
  - `writepd__steel_austenite_fraction__opus__rep1`
- In three of them (γ′ and both steel-austenite runs) both launches wrote a complete reply and one was overwritten. Commit `966f9b82`: "Steel austenite reply from the first launch (overwrites the relaunch's reply)".
- For the two steel-austenite runs, `meta.json` (tokens, duration, audited transcript) describes the relaunch, but the kept `reply.txt` was written after that session ended, i.e. by the first launch.
- Two first attempts stopped at the 5-hour usage limit before writing anything. One (Sonnet) read the files and stopped. I did not inspect the first attempt of `ti_alloy_hardness__opus__rep1`.
- 31 transcripts contain a harness `<synthetic>` usage-limit message. In the one I checked, it came after the reply was written.
- `harvest_run_usage.py` audits only the final transcript of each run.

**D2. Fable missing from two tasks in Table 2 and Figure 3a.**
- Table 2 caption: "five experimental alloy tasks with the Opus and Fable networks (120 cells per row)".
- Source: `joint_mean/static` has no Fable cells for Ti Young's modulus or MPEA yield strength. The regex in `run_joint_mean.static` requires a model tag, which the first Fable replies of those two tasks lack. The 120 cells are 75 Opus + 45 Fable.
- Figure 3a shows only Opus, but its legend lists Fable.

**D3. Titanium alloy dataset is not cited** (methods.tex:9). The source is Salvador, C. A. F. et al., Sci. Data 9, 188 (2022), doi:10.1038/s41597-022-01283-9 (confirmed by web search). It is not in `refs.bib`.

**D4. Models and software the work depends on are not cited.**
- Main text: the crystal embedding is ORB-v3 (`tasks.py`) and the oracle is eSEN-30M-OAM; the paper says only "pretrained graph-network embedding" and "machine-learned potential".
- Supplement: MACE, ORB, eSEN and GRACE are named without citations, although `batatia2022mace`, `batatia2023foundation`, `rhodes2025orbv3`, `fu2025esen`, `bochkarev2024grace` and `barroso2024omat` are all in `refs.bib`.
- pymatgen (descriptors and elemental tables), GPyTorch and TC-Python are not cited.

**D5. BO protocol details.**
- Ti Young's modulus is minimised (`run_bo_select.GOALS = -1`, "implants"); neither the Method section nor Table 3 says so.
- Table 3 and Figure 4 do not say the two-stage fit is used.
- The random, rule-of-mixtures and all-replies arms were run but are not reported. On MPEA yield strength the rule-of-mixtures prior is ahead of the GP (676 vs 772, not significant), while both LLM priors lose.
- The selection rule was designed after a round-2 BO failure on the same tasks and replies (`run_bo_select.py` docstring).
- The area definitions differ:
  - Table 3 averages steps 1–25.
  - The joint comparison averages steps 0–25 (plain GP 7.68 vs 7.90).
  - The "0.69 / 0.68" are means of per-task ratios; the ratio of sums is 0.91 / 0.90.

**D6. Tool access (methods.tex:6).**
- Text: "It has no code execution, calculator or web access".
- Problem: the sessions were Claude Code subagents told by `WRAPPER.md` not to use those tools. `tools_allowed` is null and they also received harness reminders. Whether tools were actually unavailable is not recorded.
- Fix: "is instructed not to use …, and the transcript is audited".

**D7. Session protocol varied.**
- The 15 Opus alloy runs never read `WRAPPER.md` (3 tool calls).
- The two first Fable replies have no self-report (2 tool calls).
- This contradicts methods.tex:6 ("writes one reply file and a short account") and the supplement's "Each session receives one line naming an instruction file".

**D8. MLP filter baseline.** It is trained once (seed 0) on DFT K_VRH of relaxed Materials Project structures, then scored against the eSEN oracle on as-generated crystals, so its training labels and the oracle differ.

**D9. Matbench BNN task.** It reuses the networks written for generated crystals.

## E. Inconsistencies

- **E1.** Plain GP at 5 labels on alloys: 0.35 (abstract, results.tex:31) vs 0.34 (Table 2), from the same cells. 0.35 is a mean of per-task means; 0.34 is pooled over cells.
- **E2.** The abstract's 5-label gains mix fits without saying so: alloys and Thermo-Calc use the fit with a and b integrated out, crystals use a and b learned.
- **E3.** results.tex:35 compares the rule's two-stage fit (0.93) with the networks' learned-a, b fit (0.90). The networks' own two-stage values are 0.91 / 0.89, and the rule with a, b learned is 0.82.
- **E4.** supp_tables.tex:139 is missing the "Ti alloys" system label. Its four rows (α transus, freezing range, intermetallic, solidus) print under "Ni superalloys", which then has duplicate solidus and freezing-range rows. The values match `overview.md`.
- **E5.** In supp_other.tex:9 the R² change "0.35 to 0.21 / 0.14" is the mean over all 11 networks, but the text attributes it to the bulk-modulus networks.

## F. Unclear

- **F1.** `methods.tex:4` (uncommitted) contains the literal string `SIZE_SENTENCE`, which will print.
- **F2.** results.tex:16, "Replies of one model agree with each other more than models agree" — no result file records this. I recomputed it on the alloys: mean pairwise ρ is 0.87–0.94 within a model and 0.60–0.78 across models. The claim holds; add the numbers and a file.
- **F3.** results.tex:148, "On two further targets no prior of any kind helps" — no prior is significant on more than ten phase-fraction targets either. Restrict the sentence to targets with real regret.
- **F4.** methods.tex:9, "(15 to 24 elements)" → "15 to 24 inputs (14 to 23 elements and the summed fraction of the rest)".
- **F5.** results.tex:142, "0.52–0.56" and "17 or 18 oracle calls" cover Opus, Fable and Sonnet only. Haiku gives 0.46 and 11 calls.

## G. Figures

- `fig_bnn`: bar axes start at 0.15 and 0.30, which exaggerates the differences. Start at 0 or use dots.
- `fig_fewlabels` (a): no Fable curve and a caption that is silent about it (see D2).
- All other main figures match their captions and data. `fig_bo_calphad` clips values at 0.01, but the axis is labelled "≤0.01".

## H. Citations

- All 24 cited keys resolve; `main.blg` has 0 warnings.
- I confirmed the Takehi et al. blog post (secondary coverage) and the Salvador dataset by web search.
- `ha2017hypernetworks` is cited for "weight arithmetic"; hypernetworks are a different technique.
- `andersson2002thermocalc` is a software paper, cited for the practice of sub-system extrapolation; a CALPHAD methods reference fits better.
- Eight bib entries are uncited: the six MLIP entries in D4, plus `hallstedt2025sgte` and `glmocr2026` after the table-reader removal.

## I. Prose

"The limits are clear." · "carry real materials knowledge" · "separates knowledge from information" · "Function space is the safe place." · "has no training distribution to leave" (the model's knowledge also comes from relaxed crystals).

## What I checked and found correct

- **Table 1:** every other cell matches `standalone/per_reply.json`, recomputed as the mean of per-reply R².
- **Thermo-Calc rows:** the 35-target means and medians, and all 175 ρ values in Table S (calphadrho).
- **Tables 2, 3 and 4:** all values, and the 14 / 15 / 16 / 12 / 14 solidus and freezing-range win counts.
- **Table S (calphadbo):** all values (labels aside, E4).
- **Table S (crystal):** all values and run counts.
- **Counts:** 60 / 280 / 18 / 358 runs; 3 rejected replies (shape errors); 9 pools of 200–400; 35 targets after one dropped; 113–417 weights; dataset sizes; 3,479 / 2,437 crystals.
- **Results paragraphs:**
  - Few labels: 0.37 → 0.64, 0.15 → 0.95, 0.88 at 500, the ~50 and ~20 label crossovers.
  - Calibration: 0.63 / 0.74 / 0.69–0.73 and 0.79 / 0.88 / 0.98.
  - BO counts and medians, and MPEA yield strength p = 0.03 / 0.02 with 14 of 20 seeds worse.
  - Features: 0.43, 0.94 / 0.88 / 0.66, 0.92–0.94.
  - BNN: 0.54 → 0.65, 0.53 → 0.69, 22 / 23 of 24, 0.50 → 0.58, 0.45 → 0.21; coverage 0.66 / 0.39 and 0.45 → 0.88.
  - Filter: 0.92 / 0.88, 0.82 / 0.77, 0.29 / 0.12, 144 / 72 / 147, 0.36 / 0.38 / 0.09.
  - Sparsity medians; R² = 0.81 from `baseline_table.md`.
- **Method vs code:** the sub-system extrapolation, the three fits of the mean, the selection rule (Pearson, 0.3, fixed in a commit), Holm over arms, and the drop rule all match.
- **Supplementary experiments:** the leak counts and the task-vector numbers match.

## What I could not verify

- The arXiv 2611.* and 2606.03232 entries; web search found nothing yet. The repo's source notes summarise Hu, Ahmed and Nusrat.
- Takehi et al.'s "~10^5 weights" claim, beyond the repo's source notes.
- The first attempt of `write__ti_alloy_hardness__opus__rep1`.
- Whether the subject sessions technically had code tools available.
- The supplementary MLIP numbers other than the chain values; I did not open the potentials table, the gradient-fit curve or the ORB refit.
- The "127 distinct formulas".
- The typeset PDF after the 10:41 recompile.
