# Campaign ledger — read this first when resuming

Updated after every completed unit of work and committed with it. If a session ends mid-task (usage limit, crash), the state below plus `git log` is enough to continue. Rules for whoever resumes: `CLAUDE.md`. Commands: `REPRODUCE.md`.

Instruction in force (Alvi, 2026-11-11): keep going without stopping; cover all three problem types (BO surrogate, MLIP, generative model) with extensive benchmarking; use HPRC when needed; record everything; commit and push after each unit; report results in chat as they land.

## Done

| Unit | Where the result is | Commit |
|---|---|---|
| Research: where WSP fits | `docs/research-runs/2026-11-11-where-wsp-fits.md` | 98f2fa2 |
| Data and algorithms copied with provenance | `data/`, `vendor/`, `scripts/copy_from_siblings.py` | 98f2fa2 |
| E1 baselines, 5 tasks × 5 seeds | `experiments/e1_surrogate_head/results/`, `docs/results/2026-11-11-e1-pilot.md` | 98f2fa2 |
| E1 pilot: edit arm (3 runs), write arm (2 runs) | same page; `experiments/e1_surrogate_head/runs/` | 98f2fa2 |
| E1 round 2: repair arm (4 + control), write replicates (3 per task), BO loop | `docs/results/2026-11-11-round2.md` | 41f57da |
| E4 step 2: surrogate zoo, leave one benchmark out | same page; `supplementary/e4_surrogate_zoo/results/` | 41f57da |

## Round 3 plan (in order; tick as done)

### A. BO surrogate (E1), extensive
- [x] A1. More tasks with named inputs for the write arm (MPEA hardness, Ti yield strength, Ti hardness).
- [x] A2. Handbook baseline with no LLM: rule of mixtures from elemental property tables (pymatgen), scored exactly like a written network.
- [ ] A3. Write arm at scale: 3 replies × 4 models (fable, opus, sonnet, haiku) × 5 alloy tasks, run folders `runs/write__<task>__<model>__rep<k>/`. Launch with `Agent(model=<alias>, prompt='Read .../WRAPPER.md and follow it exactly... RUN = <folder>')`; at most 20 subagents at once. `python scripts/pending_runs.py` lists what still has no reply. Then `python experiments/e1_surrogate_head/score_write_all.py` scores everything and writes `results/write_arm/`.
- [ ] A4. Selection rule: choose among replies with the first n labels; BO with the chosen prior; 20 seeds; paired test against the plain GP.
- [ ] A5. Repair arm at scale: seeds 0 to 5 on both loop tasks × models, plus the column-norm and gradient-attribution statistics as baselines.

### B. MLIP (E2)
- [x] B1. MACE-MPA-0 medium bulk modulus on the 15 DFT-validated structures: MACE is +26.4 GPa (8%) above DFT on average, MAE 35.0 GPa; not softening on this set. Reference set widened to 400 structures of matminer `elastic_tensor_2015` (`data/mlip_reference/`). Readout features cached per structure under `data/large/mlip_cache/<set>/` by `cache_features.py` (resumable; rerun the same command to continue). Edited readouts are scored from the cache by `src/wsp/mace_readout.py`; unedited weights reproduce MACE energies to 1e-14 eV.
- [ ] B2. Cheap references: one global energy scale fitted on a train split; readout-only gradient fit to the bulk moduli.
- [ ] B3. LLM arm, no forward passes: prompt with the 2,283 readout numbers and the error table; score on the held-out structures.
- [ ] B4. LLM arm with a forward-pass budget (10, 25, 50 calls to an evaluation script).
- [ ] B5. If B1 shows too little bias to fix on 15 structures: widen to the matminer elastic set on HPRC.

### C. Generative model (E3)
- [x] C1 (MatterGen and CrystalFlow done; ADiT not downloaded). Download the fine-tuned checkpoints (Hugging Face `SheikhAhnaf/apu-synthesizability-checkpoints`, `finetuned_diffusion/`, about 15 GB) to `data/large/finetuned_diffusion/` (untracked). MatterGen first (base checkpoint is in the local HF cache).
- [x] C2, C3 for MatterGen (`task_vectors.py --backbone mg`, results in `supplementary/e3_generator_task_vectors/results/task_vectors_mg.json`): relative norm of the change 0.4 to 0.6%; rank for 90% energy is 32% of full rank (median) against 48% for the base weights; cosine between seeds of the same target and policy 0.21 mean, between targets 0.11 to 0.17. CrystalFlow needs its base checkpoint (not found locally yet).
- [ ] C4. On FASTER: 11 MatterGen variants (base, single-seed, seed-mean, sums, rank-8 and rank-32 truncations, negation, 3x scaling), 128 crystals each from the same noise seed, scored with the loop's eSEN bulk-modulus and heat-capacity oracles. See HPRC jobs below. After the array finishes: rsync results (command in the hprc README), then write `analyze_variants.py`.

## Running now

- Local background: `supplementary/e2_mlip_readout_edit/run_baselines.py` (B2). Rerun if no `results/baselines_elastic.json`.
- Subagents: write arm A3 (see `scripts/pending_runs.py`).

## HPRC jobs

Cluster FASTER, billing account `142705330300` (Arroyave, FY2027, 150,000 SU; no default account is set on FASTER, so jobs name it). Working folder `/scratch/group/arroyave_lab/ahnafalvi/wsp/` (user scratch and home are over quota). Scripts and exact commands: `supplementary/e3_generator_task_vectors/hprc/README.md`.

| Job id | Script | What | State when last checked | When it finishes |
|---|---|---|---|---|
| 3257269 | `hprc/prep.slurm` | download 20 MatterGen fine-tunes, build 11 variants, smoke test (4 samples, 2 scored) | submitted 2026-11-11, running on fc101 | check `logs/prep_3257269.out` ends with `PREP_DONE`; then `sbatch hprc/array.slurm` |

## Notes for resuming

- LLM runs are made as Claude Code subagents with the wrapper in `docs/results/2026-11-11-e1-pilot.md` §5; after each, `scripts/record_run.py` then `llm_arm.py score`.
- A run folder with `prompt.txt` but no `reply.txt` was started and not finished: just run it again.
- `data/large/` is untracked; rebuild with `scripts/copy_from_siblings.py` and the download script of C1.

## State at the usage-limit stop (2026-11-11, round 3 in progress)

Everything below is committed. Nothing is lost if the session ends here.

### Finished in round 3 (results on disk, not yet written up in `docs/results/`)

- **A1, A2, A3 done.** Write arm: 5 alloy tasks × 4 models × 3 replies (60 replies, 3 invalid). Table: `experiments/e1_surrogate_head/results/write_arm/summary.md`. Headline: priors written by Opus 5.5 and Fable 5.2 rank alloys at ρ 0.53 to 0.79 with no data (handbook rule of mixtures: −0.75 to 0.27) and raise GP ranking at 5 labels on every task (for example `mpea_hardness` 0.06 → 0.66 / 0.78, `ti_alloy_yield_strength` 0.26 → 0.70); Sonnet 5.5 and Haiku 5.5 are weaker and Haiku sometimes hurts.
- **Run metadata harvested** (`scripts/harvest_run_usage.py`, `experiments/runs_audit.json`): 92 runs matched to transcripts, all passed the tool audit. The `sonnet` alias ran claude-sonnet-5-5 for the write arm and MLIP prompt v1, but claude-sonnet-4-6 for MLIP prompt v2: label those rows by model id.
- **B1, B2, B3 done (E2, MLIP).** 400 structures. Unedited MACE: MAE 16.2 GPa, bias +6.4 on the test half. Gradient fit of the readout, trade-off curve in `results/frontier_seed0.json`: MAE 12.4 at 190 meV/atom energy change; 13.9 at 5.2 meV/atom; 14.4 at 2.9; 15.9 at 0.3. LLM edits, prompt v1 (misleading fixed-volume table, my design error): all 11 scored replies made the bias worse. Prompt v2 (finite-difference table): Opus 5.5 ×3 MAE 15.8 to 15.9, bias +4.8 to +4.9, energy change 3.8 to 4.3 meV/atom; Fable 5.2 ×3 MAE 15.8, bias +4.5, 5.2 to 6.0 meV/atom; Haiku and Sonnet 4.6 broke the 5 meV limit (15 to 69 meV/atom). So the best LLM edits respect the constraint but sit above the gradient curve (14.4 at 2.9 meV/atom). Rescore any time with `llm_arm.py score-all`.
- **C1, C2, C3 done (E3)** for MatterGen; see above.
- Leak-repair statistics over all 11 networks: column norm finds the leak in 4, linear path gain in 6 (`score_repair` now reports both).

### Running or pending

| What | Where | How to pick up |
|---|---|---|
| BO with first-label prior selection, 20 seeds (A4) | local background process, cache `experiments/e1_surrogate_head/results/bo_select/init5_steps25/` | rerun `python experiments/e1_surrogate_head/run_bo_select.py --seeds 20 --steps 25 --jobs 8`; finished traces are reused; it prints and writes `summary_init5_steps25_seeds20.md` |
| FASTER array **3257271** (11 variants × 128 crystals, tasks 0 to 10, all running on T4 nodes when last seen) | `/scratch/group/arroyave_lab/ahnafalvi/wsp/results/<variant>/scores.csv` | `ssh faster "squeue -u \$USER"`; if tasks hit the 12 h limit, `sbatch hprc/array.slurm` again (resumes); then the rsync in `hprc/README.md` and `python supplementary/e3_generator_task_vectors/analyze_variants.py` (written, not yet run on data) |
| MLIP run `edit_v2__sonnet__rep3` | subagent, may or may not have written `reply.txt` | `llm_arm.py score-all` picks it up if present |
| Leak-repair arm at scale (A5): 40 prompts generated, **no agent launched** | `python scripts/pending_runs.py` lists them (`repair__*__{opus,sonnet,haiku,fable}`) | launch each with `Agent(model=<alias>, prompt="Read .../e1_surrogate_head/WRAPPER.md and follow it exactly... RUN = <name>")`, then `harvest_run_usage.py` and `llm_arm.py score` per run |

### Still to do after those

1. Write `docs/results/2026-11-11-round3.md` from the files named above; add a `questions.md` row; update `README.md`.
2. B4 (MLIP edits with a forward-pass budget) and CrystalFlow/ADiT task vectors (need their base checkpoints) are not started.

## State on 2026-11-11, evening (round 4 in progress)

- Remote is now `origin` = `sheikhahnaf/weightspace-programming-for-material-science` (private, history without Claude lines). `old-origin` still points at the first repo, which keeps the old history until Alvi deletes it or approves a force-push. Commit messages carry no Claude attribution.
- Paper repo: `/Volumes/SSD1_SMAAA/weightspace-programming-for-material-science-paper` → `sheikhahnaf/weightspace-programming-for-material-science-paper` (private). First draft compiles.
- Results page: `site/index.html`, published privately at https://claude.ai/artifact/S9fPA66YFMW3oux1sPqLkh. Republish the same file to update.
- Leak repair finished: Fable 6/11, Opus 5/11, Sonnet 1/11, Haiku 1/11; linear-gain statistic 6/11. `results/repair_arm/summary.md`.
- Generator filter arm (E3, `filter_arm.py`): written scorers rank bulk modulus of base samples at rho 0.94 (Opus), 0.88 (Fable), 0.80 (Sonnet), 0.73 (Haiku) against 0.82 for the volume-per-atom rule. `results/filter_arm/summary.md`. Six of the 24 prompts (heat capacity replicates) were not launched; heat capacity is solved by the Dulong-Petit rule.
- E5 BNN (`experiments/e5_bnn_start/run_bnn.py`): MC dropout, deep ensemble and HMC, each with and without the written network as start, anchor, weight-space prior or prior mean. Running locally in the background; cells cached under `results/cells/`; rerun the command to resume and print `bnn_summary.md`. IBNN was dropped at Alvi's request; HMC follows Li, Rudner and Wilson's bnn-bo study, re-implemented because that repo has no licence.
- ORB-v3 readout (E2): `cache_features_orb.py --set elastic` running (resumable; needs `compile=False`, already set). Next: an ORB version of `mace_readout.py`, baselines, LLM edits. eSEN and GRACE on FASTER not started.
- Not yet in `docs/results/`: filter arm, final leak counts, E5, ORB.

## State on 2026-11-11, night (round 5 written; expansions running). READ THIS FIRST WHEN RESUMING

Committed and pushed unless marked. Paper repo also pushed (second draft, 10 pages, tag `pristine-pre-restyle-2026-11-11`).

**Finished and written up** (`docs/results/2026-11-11-round5.md`): four potentials (MACE, ORB, eSEN, GRACE) through `src/wsp/linear_head.py`; single-shot ORB edits with permuted-value control; five-attempt feedback chains (`supplementary/e2_mlip_readout_edit/head_arm.py`, all 16 chains complete, `results/head/chains.md`); budgeted optimiser baselines; outside-the-readout references (`beyond_readout.py`, `risk_arm.py`).

**Slide deck:** `slides/gp-prior/gp-prior-weight-space-programming.pptx` (54 slides, architecture slides 18–19). NOT yet committed (`git add slides` after checking size; `slides/*/node_modules/` is ignored). Never rebuild while it is open in PowerPoint. One cosmetic fault on slide 54 (caption touches table).

**Running or half done, with how to resume:**

| What | State | Resume |
|---|---|---|
| E6 table reader, synthetic ORCHID-Bench (`supplementary/e6_extraction_reader/`) | Unedited GLM-OCR read on FASTER, both renderings (degraded: 72.2% cells exact, 81.3% ignoring spaces, numbers 100% by the bench scorer; Opus baseline 97.4% / 100%). Edits (`edits/*.json`: counts, opus rep1–2, fable rep1–2) being read by FASTER job 3259965; first scores on the 10 test papers, exact cells: unedited 0.714, counts 0.741, opus 0.733 / 0.747, fable rep1 0.758, fable rep2 incomplete | `rsync` `results/` back from `faster:/scratch/group/arroyave_lab/ahnafalvi/wsp/weighspace-programming/supplementary/e6_extraction_reader/results/`, then `env/ocr-venv/bin/python supplementary/e6_extraction_reader/edit_arm.py score`. If the job died: `sbatch supplementary/e6_extraction_reader/hprc/edits.slurm edits/<tag>.json ...` (cached per crop). Model load on FASTER takes 6 minutes; that is normal |
| E6 real papers | 400 crops in `data/large/orchid_real/` (untracked, publisher material, never commit); code `build_real_set.py`, `read_real.py`, `score_real.py`; manifest `results/real_set_manifest.json`. Open model NOT yet run on them | copy `data/large/orchid_real/{crops,index.jsonl}` to FASTER group scratch (private), run `read_real.py --tag unedited` with `ocr-venv2`, then with each edit; Opus baseline on a subset through `opus_reader.py`-style runs |
| Joint BoTorch mean (`src/wsp/joint_mean.py`, `experiments/e1_surrogate_head/run_joint_mean.py`) | static done (`results/joint_mean/static_summary.md`: at 5 labels ρ / coverage: two-stage 0.64 / 0.63, learned 0.66 / 0.75, integrated 0.68 / 0.79); BO part running locally (cached per trace) | `python experiments/e1_surrogate_head/run_joint_mean.py bo --seeds 20 --steps 25 --jobs 6` prints the table |
| E7 Thermo-Calc tasks (`experiments/e7_calphad_prior/`, `data/calphad/`) | agent `tc-tasks` building ≥ 8 alloy systems with TC-Python (env `tcpy`), tasks, references, prompts for `write` and `write_pd`; all four mean arms required | read `experiments/e7_calphad_prior/README.md`; rerun `make_tc_data.py` (resumable); then launch the listed run names as subagents (`WRAPPER.md` there), score, run BO |
| E3 more backbones | agent `gen-backbones`; FASTER prep jobs 3259982 (CrystalFlow), 3259983 (ADiT) | see the entry that agent appends below and `supplementary/e3_generator_task_vectors/hprc/README.md` |

**Not done yet:** round-6 results page (E6, joint mean, E7, backbones); README, questions.md and REPRODUCE sections for rounds 4–5 additions (`REPRODUCE.md` has 4d; add 4e for round 5); webpage `site/index.html` is updated locally with round 5 but NOT republished (republish the same path to https://claude.ai/artifact/S9fPA66YFMW3oux1sPqLkh); paper lacks E6, joint mean, E7, backbones.

**User decisions on record (2026-11-11):** authors Alvi then Arróyave; figures in the figures4papers style; table crops from publisher PDFs never go to GitHub, code and results do; force-push to the old repo was approved and done; phase-diagram context must never contain the target; test on many alloy systems.

## E3 more backbones (agent `gen-backbones`, 2026-11-11 night)

Inventory of RL fine-tunes (HF `finetuned_diffusion/`, 59 runs): MatterGen 20, CrystalFlow 20, ADiT 19 (no `hcap`/`accel` seed 99); each 2 targets x 2 policies x seeds 7, 17, 23, 99, 113. No other backbone has fine-tunes. Base checkpoints and samplers, all on FASTER user scratch (read only): CrystalFlow `checkpoints/crystalflow/ckpt-v1.0.0/DNG-mp-20/` + the loop's `CrystalFlowSuite`; ADiT `checkpoints/adit/{ldm,vae}.ckpt` + the loop's `ADiTSuite`. The CrystalFlow base (226 MB) is also copied to `data/large/base_checkpoints/crystalflow/DNG-mp-20/` (untracked).

Code: `task_vectors.py`, `hprc/{env.sh,prep.slurm,array.slurm,make_variants.py,sample_and_score.py}` and `analyze_variants.py` take a backbone (`--backbone`, or `BACKBONE=` for the slurm scripts); MatterGen output re-checked identical. Commands: `supplementary/e3_generator_task_vectors/hprc/README.md`, section "CrystalFlow and ADiT".

| Job | What | State when last checked |
|---|---|---|
| 3259982 | CrystalFlow prep: variants, smoke test (4 sampled, 2 scored), task-vector statistics | COMPLETED, 30 min |
| 3259983 | ADiT prep | FAILED after 5 min: base `ldm.ckpt` pickles classes under the package name `src`; fixed with `alias_adit_package()` |
| 3260069 | CrystalFlow array, 11 variants x 128 crystals, tasks 0 to 10 | all 11 running on fc101 to fc104 (MatterGen took 3 to 4 h per task) |
| 3260080 | ADiT prep, resubmitted with the fix (`--time=04:00:00 --mem=64G`) | pending |

Done: `results/task_vectors_cf.json` (change is 0.04 to 0.07% of the norm of the tensors RL touched, against 0.4 to 0.6% for MatterGen; 90% of the energy at a median 1.4% of full rank over the 25 changed matrices; cosine between seeds of the same target and policy 0.28, between targets 0.02 to 0.08). Side finding: the MatterGen rank figure "32% of full rank (median)" counts 70 matrices that no run changed as full rank; over the 139 changed matrices it is 25% (base 45%). `results/task_vectors_mg.json` was left as it was; rerun `task_vectors.py --backbone mg` to add the new block.

To resume:
1. `ssh faster "squeue -u \$USER; sacct -j 3260069,3260080 -X -n --format=JobID%14,State,Elapsed"`. If array tasks timed out, `sbatch --export=ALL,BACKBONE=cf array.slurm` again (it continues).
2. CrystalFlow results: the `rsync` loop and `analyze_variants.py --backbone cf` in the hprc README -> `results/hprc_cf/`, `results/variants_summary_cf.{md,json}`.
3. ADiT: when `logs/prep_3260080.out` shows `SMOKE_DONE`, `sbatch --export=ALL,BACKBONE=adit array.slurm`; when it shows `PREP_DONE`, fetch `wsp/task_vectors/task_vectors_adit.json`. If the prep fails again, read `logs/prep_3260080.err` and stop on ADiT with the exact error.
4. Then update the Status line of the E3 README and this table.

## 2026-11-12: focus on the GP-prior case; other cases paused

User decision: Claude usage goes only to the GP-prior case. Jobs that need no Claude usage keep running.

Paused, with what is on disk:
- **E8 formation enthalpy** (`supplementary/e8_formation_enthalpy/`): 800 compounds and 78 elemental references in `data/formation/`; MACE energies done, ORB energies computing locally; MACE as shipped 0.195 eV/atom MAE on the 400 held-out compounds (`results/correction.md`); prompts written under `runs/correct__mace__*`; **no model runs launched**. To resume: `correction_arm.py prompt` (adds ORB), launch the runs with `WRAPPER.md`, then `correction_arm.py score`. The least-squares reference needs its ridge strength chosen properly before it is used as a baseline.
- **E6 real-paper tables**: FASTER job 3260081 and continuations 3260491, 3260492 keep reading; replies in `orchid_real_private/replies/` on scratch. Not yet fetched or scored.
- **E3 backbones**: CrystalFlow sampling array 3260069 running; ADiT not started. See the E3 section.
- **E2**: nothing running.

Active: E7 Thermo-Calc prior case (two repeats per cell, Opus and Fable, with and without phase-diagram facts) and `experiments/e1_surrogate_head/run_structure_prior.py`.

### Paused 2026-11-12 (E3 more backbones)

Work stopped at the user's request; nothing was cancelled. State when last checked (2026-11-11 night, not re-checked at the pause):

- Still on FASTER: array **3260069** (CrystalFlow, 11 variants x 128 crystals, tasks 0 to 10, were running) and **3260080** (ADiT prep with the unpickling fix, was pending; the fix is untested). The ADiT sampling array has NOT been submitted. A local background watcher for 3260080 may still be alive; it only reads logs.
- Results land in `/scratch/group/arroyave_lab/ahnafalvi/wsp/results_cf/<variant>/{scores.csv,generated_crystals.extxyz}`; ADiT variants in `wsp/variants_adit/`, its statistics in `wsp/task_vectors/task_vectors_adit.json`, logs in `wsp/logs/{variant_3260069_<k>,prep_3260080}.{out,err}`.

To pick up, from the repo root with an open `ssh faster` connection:

```bash
W=/scratch/group/arroyave_lab/ahnafalvi/wsp; H=$W/weighspace-programming/supplementary/e3_generator_task_vectors/hprc
ssh faster "sacct -j 3260069,3260080 -X -n --format=JobID%14,State,Elapsed; wc -l $W/results_cf/*/scores.csv; tail -5 $W/logs/prep_3260080.out; tail -20 $W/logs/prep_3260080.err"
# CrystalFlow: every scores.csv should have 129 lines; if tasks timed out: ssh faster "cd $H && sbatch --export=ALL,BACKBONE=cf array.slurm"
rsync -avz --include='*/' --include='scores.csv' --include='generated_crystals.extxyz' --exclude='*' \
      faster:$W/results_cf/ supplementary/e3_generator_task_vectors/results/hprc_cf/
python supplementary/e3_generator_task_vectors/analyze_variants.py --backbone cf     # matinvent env -> results/variants_summary_cf.{md,json}
# ADiT, only if prep_3260080.out shows SMOKE_DONE (otherwise stop on ADiT and report the error in the .err file):
ssh faster "cd $H && sbatch --export=ALL,BACKBONE=adit array.slurm"
rsync -avz faster:$W/task_vectors/task_vectors_adit.json supplementary/e3_generator_task_vectors/results/   # after PREP_DONE
# after the ADiT array: same rsync with results_adit/ -> results/hprc_adit/, then analyze_variants.py --backbone adit
```

Then update the E3 README Status line. Uncommitted: all edits of this section (no git was run by this agent).

Update at the pause (from the watcher, 2026-11-11 23:52 CST): ADiT prep 3260080 reached `SMOKE_DONE` — the unpickling fix works, 11 ADiT variants are built in `wsp/variants_adit/` (task vector covers 132 of 348 base tensors, the denoiser; single-seed change 0.27% of the tensors RL touched), 4 crystals sampled and 2 scored. Its task-vector statistics step was still running. The ADiT sampling array is still NOT submitted: the `sbatch --export=ALL,BACKBONE=adit array.slurm` line above is the next step. CrystalFlow array 3260069 was 21 min in, about 4 crystals scored per variant.

## 2026-11-12: restructuring plan (user decision; NOT started, do after all GP-prior runs finish)

- Paper and website become entirely about one case: an LLM writes a network that is used as a GP prior mean.
- Everything else (MLIP readout edits, generator task vectors, table reader, earlier rounds, archive) moves to the supplement, at its end.
- In the repo, MLIP and generative-model material moves into a folder named `supplementary/`.
- Open: whether the Thermo-Calc data tables (`data/calphad/`) may be in a public repo. They are committed in the private repo's history now. Decide before any public release (licence check; fallback is to ship only `make_tc_data.py` and scores, from a fresh history).
- Supplement requirement (user, 2026-11-12): the supplement OPENS with, for every Thermo-Calc task and every ordinary-dataset task, the prompt, the model's output and the network architecture drawn as in the slide deck (slides 18-19). MLIP, generator and archive material come after, at the end.

## 2026-11-12: paper framing and placement decisions (agreed with the user; writing NOT started)

Claim: a language model can write a small property-prediction network from knowledge alone, with no data; the paper shows what such a network is good for. The GP prior mean is one use, not the framing.

Flow: (1) introduction; (2) method: prompt, architecture, controls; (3) the written networks as predictors on every task (experimental alloys, Thermo-Calc systems, crystals): ranking, scale, four models, against rules; (4) uses: GP prior mean and BO, GP inputs (hidden layer), BNN surrogates; (5) context: phase-diagram facts; (6) where it fails (MPEA yield strength, absolute scale, rules that already work).

Placement:
- BNN: one short main-text paragraph (the prior-mean benefit carries over to BNN surrogates; starting-point and weight-prior negatives in a sentence); tables in the supplement.
- Generator filter: main text only if it holds on CrystalFlow as well as MatterGen (CrystalFlow sampling array 3260069 still running; scoring the existing written networks on its crystals needs no model runs). Otherwise supplement.
- Error-risk predictor for a potential: supplement.
- Supplement opens with prompt, output and architecture for every task; MLIP, generator, table reader and archive at the end.
- To compute before writing: uniform standalone metrics for every written network on every task (rho, error after a two-point scale fix, best-tenth recall).

## 2026-11-12 (later): GP-prior runs finished; repo, paper and site refocused

- **All model runs for the main case are done.** Thermo-Calc: 280 replies (9 systems, 35 targets; Opus and Fable; with and without facts; reps 1 and 2; rep3 folders hold unrun prompts). Static arms and 20-seed BO for all nine systems ran on FASTER (job 3260906); results in `experiments/e7_calphad_prior/results/`, summary in `docs/results/2026-11-12-round7.md` section 4.
- **Crystal filter on CrystalFlow** scored (`experiments/e3_crystal_filter/results/filter_arm_cf/`): it holds, so the filter is in the paper's main text. CrystalFlow task vectors do not move bulk modulus significantly (`supplementary/e3_generator_task_vectors/results/variants_summary_cf.md`).
- **Repo layout:** main case under `experiments/` (e1, e3_crystal_filter, e5, e7); `supplementary/` holds e2, e3_generator_task_vectors, e4, e6, e8. The copy on FASTER (`/scratch/group/arroyave_lab/ahnafalvi/wsp/weighspace-programming`) still has the old layout; sync only the folders a job needs.
- **Paper** (separate repo, branch `refocus-written-networks-2026-11-12`, not merged to main): rewritten around the written network as a property predictor and its uses; 66 pages with the supplement, which opens with prompt, reply and network diagram for all 42 tasks and ends with the other weight-space experiments. Regenerate: `python figures_src/make_figures.py`, `python figures_src/make_supplement.py /Volumes/SSD1_SMAAA/weighspace-programming`, then pdflatex, bibtex, pdflatex twice.
- **Site:** `site/index.html` rewritten the same way and republished to the private artifact link.
- **Slides:** Thermo-Calc section being added to `slides/gp-prior/`, built to `gp-prior-weight-space-programming-v2.pptx` because the first file was open in PowerPoint.

Open:
1. Thermo-Calc licence: whether `data/calphad/` may be redistributed is unchecked; needed before any public release (the tables are in the git history).
2. The paper branch needs the authors' read and a merge to main (main syncs to Overleaf).
3. Not run: rep3 Thermo-Calc replies; Sonnet and Haiku on Thermo-Calc targets; other vendors' models; E8 formation enthalpy; E6 real-paper tables (computed on FASTER, unscored); ADiT sampling.
