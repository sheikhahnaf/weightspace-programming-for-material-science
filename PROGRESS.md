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
| E4 step 2: surrogate zoo, leave one benchmark out | same page; `experiments/e4_surrogate_zoo/results/` | 41f57da |

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
- [x] C2, C3 for MatterGen (`task_vectors.py --backbone mg`, results in `experiments/e3_generator_task_vectors/results/task_vectors_mg.json`): relative norm of the change 0.4 to 0.6%; rank for 90% energy is 32% of full rank (median) against 48% for the base weights; cosine between seeds of the same target and policy 0.21 mean, between targets 0.11 to 0.17. CrystalFlow needs its base checkpoint (not found locally yet).
- [ ] C4. On FASTER: 11 MatterGen variants (base, single-seed, seed-mean, sums, rank-8 and rank-32 truncations, negation, 3x scaling), 128 crystals each from the same noise seed, scored with the loop's eSEN bulk-modulus and heat-capacity oracles. See HPRC jobs below. After the array finishes: rsync results (command in the hprc README), then write `analyze_variants.py`.

## Running now

- Local background: `experiments/e2_mlip_readout_edit/run_baselines.py` (B2). Rerun if no `results/baselines_elastic.json`.
- Subagents: write arm A3 (see `scripts/pending_runs.py`).

## HPRC jobs

Cluster FASTER, billing account `142705330300` (Arroyave, FY2027, 150,000 SU; no default account is set on FASTER, so jobs name it). Working folder `/scratch/group/arroyave_lab/ahnafalvi/wsp/` (user scratch and home are over quota). Scripts and exact commands: `experiments/e3_generator_task_vectors/hprc/README.md`.

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
| FASTER array **3257271** (11 variants × 128 crystals, tasks 0 to 10, all running on T4 nodes when last seen) | `/scratch/group/arroyave_lab/ahnafalvi/wsp/results/<variant>/scores.csv` | `ssh faster "squeue -u \$USER"`; if tasks hit the 12 h limit, `sbatch hprc/array.slurm` again (resumes); then the rsync in `hprc/README.md` and `python experiments/e3_generator_task_vectors/analyze_variants.py` (written, not yet run on data) |
| MLIP run `edit_v2__sonnet__rep3` | subagent, may or may not have written `reply.txt` | `llm_arm.py score-all` picks it up if present |
| Leak-repair arm at scale (A5): 40 prompts generated, **no agent launched** | `python scripts/pending_runs.py` lists them (`repair__*__{opus,sonnet,haiku,fable}`) | launch each with `Agent(model=<alias>, prompt="Read .../e1_surrogate_head/WRAPPER.md and follow it exactly... RUN = <name>")`, then `harvest_run_usage.py` and `llm_arm.py score` per run |

### Still to do after those

1. Write `docs/results/2026-11-11-round3.md` from the files named above; add a `questions.md` row; update `README.md`.
2. B4 (MLIP edits with a forward-pass budget) and CrystalFlow/ADiT task vectors (need their base checkpoints) are not started.
