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
- [ ] C4. On HPRC: sample from base + α·τ(heat capacity) + β·τ(bulk modulus) and from rank-r truncations; score with the eSEN oracle.

## Running now

- Local background: `experiments/e2_mlip_readout_edit/run_baselines.py` (B2). Rerun if no `results/baselines_elastic.json`.
- Subagents: write arm A3 (see `scripts/pending_runs.py`).

## HPRC jobs

None submitted yet. Record here: cluster, job id, script path, output path, what to do when it finishes.

## Notes for resuming

- LLM runs are made as Claude Code subagents with the wrapper in `docs/results/2026-11-11-e1-pilot.md` §5; after each, `scripts/record_run.py` then `llm_arm.py score`.
- A run folder with `prompt.txt` but no `reply.txt` was started and not finished: just run it again.
- `data/large/` is untracked; rebuild with `scripts/copy_from_siblings.py` and the download script of C1.
