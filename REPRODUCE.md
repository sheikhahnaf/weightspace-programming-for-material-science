# Reproduce

Every number in `docs/` comes from the commands below, run from the repo root in the `matinvent` conda environment. The exact package versions used are in `env/matinvent.yml` and `env/matinvent-pip-freeze.txt` (macOS 26.6.2 arm64, Python 3.10.19, torch 2.4.1, CPU).

```bash
conda activate matinvent
export PYTHONPATH=src
```

## 1. Data and vendored algorithms

Already in the repo under `data/` and `vendor/`, with source paths and checksums in `data/PROVENANCE.md`. To rebuild them from the sibling repos, or to fetch the untracked `data/large/`:

```bash
python scripts/copy_from_siblings.py          # copies 84 files, rewrites data/PROVENANCE.md
python scripts/copy_from_siblings.py --check  # exits non-zero if any copy differs from its source
```

## 2. Tests

```bash
python -m pytest -q -W ignore                 # 43 tests; the MACE and ORB tests skip without data/large
```

## 3. Baselines (docs/results/2026-11-11-e1-pilot.md, section 2)

```bash
python experiments/e1_surrogate_head/run_baseline.py
# -> experiments/e1_surrogate_head/results/<task>/baseline.json, mlp_head_seed<k>.txt
# -> experiments/e1_surrogate_head/results/baseline_table.md
```

Seeds 0 to 4. Torch and NumPy seeds are fixed per seed. Bit-for-bit repeatability across machines or library versions was not tested.

## 4. LLM arms (sections 3 and 4)

```bash
E=experiments/e1_surrogate_head/llm_arm.py
python $E prompt write --task ti_alloy_youngs_modulus
python $E prompt write --task mpea_yield_strength
python $E prompt edit  --task loop_bulk_modulus --seed 0
python $E prompt edit  --task loop_bulk_modulus --seed 0 --shuffled
python $E prompt edit  --task ti_alloy_youngs_modulus --seed 0
# give runs/<id>/prompt.txt to the model, save its reply as runs/<id>/reply.txt, fill meta.json
for r in experiments/e1_surrogate_head/runs/*/; do python $E score $r; done
```

The prompts are regenerated exactly. The replies are not: a language model does not return the same text twice. The replies behind the reported numbers are stored as `runs/<id>/reply.txt`, and scoring them again reproduces `score.json`. How the model was called is in section 5 of the results page, and per run in `meta.json`.

## 4b. Round 2 (docs/results/2026-11-11-round2.md)

```bash
E=experiments/e1_surrogate_head/llm_arm.py
# section 1: leak repair
for a in "loop_heat_capacity --seed 0" "loop_heat_capacity --seed 1" "loop_bulk_modulus --seed 0" \
         "loop_bulk_modulus --seed 1" "loop_bulk_modulus --seed 0 --shuffled"; do
  python $E prompt repair --task ${=a}
done
# section 2: write-arm replicates use the same prompt as write__<task>; the replies are in
#   runs/write__<task>__rep2 and __rep3
for r in experiments/e1_surrogate_head/runs/*/; do python $E score $r; done
# record how a run was made (model, tokens, the model's own account)
python scripts/record_run.py experiments/e1_surrogate_head/runs/<id> --model ... --tokens ... --duration-ms ... --self-report "..."
# section 3: BO with the written priors (about 20 minutes on a laptop CPU)
python experiments/e1_surrogate_head/run_bo.py --seeds 8 --steps 25
# section 4: surrogate zoo (needs data/large; see section 1 above)
python supplementary/e4_surrogate_zoo/run_zoo.py
```

## 4c. Round 3 (docs/results/2026-11-11-round3.md)

```bash
E1=experiments/e1_surrogate_head; E2=supplementary/e2_mlip_readout_edit; E3=supplementary/e3_generator_task_vectors
# section 1: write arm, all models (prompts: llm_arm.py prompt write --task <t> --tag <model>__rep<k>)
python $E1/score_write_all.py                       # -> results/write_arm/summary.md
# section 2: BO with first-label selection (about 25 minutes on 8 cores)
python $E1/run_bo_select.py --seeds 20 --steps 25 --jobs 8
# section 3: MLIP
python $E2/prepare_reference.py                     # matinvent env; downloads the matminer set once
conda activate mlip-mace && python $E2/export_readout.py && python $E2/cache_features.py --set dft15 && python $E2/cache_features.py --set elastic
conda activate matinvent && python $E2/run_baselines.py && python $E2/run_frontier.py
python $E2/llm_arm.py prompt --tag <model>__rep<k> --version 2 ; python $E2/llm_arm.py score-all
# section 5: generator
python $E3/download_checkpoints.py --backbone mg && python $E3/task_vectors.py --backbone mg
#   sampling and scoring on a Slurm cluster: $E3/hprc/README.md ; then
python $E3/analyze_variants.py
# model ids, tokens, durations and the tool-call audit for every LLM run
python scripts/harvest_run_usage.py
```

How an LLM run is launched: a fresh Claude Code subagent with the model alias and the one-line prompt "Read <experiment>/WRAPPER.md and follow it exactly, including writing both files. RUN = <run folder>".

## 4d. Round 4 (docs/results/2026-11-11-round4.md)

```bash
E1=experiments/e1_surrogate_head; E2=supplementary/e2_mlip_readout_edit; E3=supplementary/e3_generator_task_vectors; E5=experiments/e5_bnn_start
# section 1: written filter in front of the generator (needs results/hprc from round 3)
F=experiments/e3_crystal_filter
python $F/filter_arm.py prompt --target K --tag <model>__rep<k> ; python $F/filter_arm.py score   # MatterGen samples
python $F/filter_arm.py score --backbone cf                                                            # CrystalFlow samples
# section 2: leak repair, all models
python $E1/llm_arm.py prompt repair --task <task> --seed <s> --tag <model> ; python $E1/score_repair_all.py
# section 3: BNN start, prior and prior mean (about 40 minutes on 8 cores; cells are cached, so it resumes)
python $E5/prepare_matbench.py
python $E5/run_bnn.py --seeds 5 --jobs 8            # -> results/bnn_summary.md
# section 4: ORB-v3 energy head
python $E2/cache_features_orb.py --set dft15 && python $E2/cache_features_orb.py --set elastic   # about 40 minutes
python $E2/orb_arm.py baselines                     # -> results/orb/frontier_seed0.json
python $E2/orb_arm.py prompt --tag <model>__rep<k> ; python $E2/orb_arm.py prompt --tag <model>__ctrl1 --control
python $E2/orb_arm.py score-all                     # -> results/orb/llm_edits.md
python scripts/harvest_run_usage.py
```

## 4f. Thermo-Calc tasks and the phase-diagram arm (experiments/e7_calphad_prior/README.md)

```bash
E1=experiments/e1_surrogate_head; E7=experiments/e7_calphad_prior
# data: needs Thermo-Calc 2025b with TC-Python and the databases TCHEA8, TCNI12, TCTI6, TCFE10, TCAL9
# (conda env tcpy). Resumable; every composition is cached in data/calphad/raw/. The CSVs and JSON are in the repo.
conda activate tcpy && python $E7/make_tc_data.py          # nine systems, in turn: facts, pool, export
#   two systems at a time:  E7_NAME=a python $E7/make_tc_data.py --system cantor_al ti_alloy ...  and  E7_NAME=b ... --system ni_superalloy ...
python $E7/make_tc_data.py --stage export                  # rebuild data/calphad/*.csv, *_facts.json, systems.json, README.md from the cache
# everything below: matinvent env, PYTHONPATH=src. A system's tasks exist once its pool is complete.
conda activate matinvent
python $E1/run_baseline.py --task calphad --out $E7/results/baseline     # GP, ridge, MLP -> baseline_table.md
python $E7/run_references.py                               # the two no-LLM references alone and as a two-stage prior
python $E7/run_priors.py static --jobs 4                   # every source x {plain GP, two-stage, map, marginal}: rho, coverage, NLL
python $E7/run_priors.py bo --seeds 20 --steps 25 --jobs 4 # BO, same arms -> results/bo/summary_init5_steps25_seeds20.md
python $E7/make_prompts.py                                 # runs/write__* and runs/writepd__*, opus and fable, reps 1 to 3
# after the replies are in ($E7/WRAPPER.md, launched as in section 4c), run the same three commands again:
python $E1/score_write_all.py --runs $E7/runs --out $E7/results/write_arm
python $E7/run_priors.py static --jobs 4 ; python $E7/run_priors.py bo --seeds 20 --steps 25 --jobs 4
```

The Thermo-Calc numbers are deterministic for a given database; they were not re-run on a second machine. A BO trace is cached with the candidate priors that existed when it ran, so an LLM source must be run only after all its replies are on disk.

## 4g. Written networks on crystal structures (docs/results/2026-11-12-round7.md, section 2)

```bash
E1=experiments/e1_surrogate_head
python $E1/run_structure_prior.py --jobs 6      # prior mean: rule and every written K / Cp network -> results/structure_prior/summary.md
python $E1/run_structure_features.py --jobs 6   # hidden layer as GP inputs -> results/structure_prior/features/summary.md
python experiments/e7_calphad_prior/summarise.py  # Thermo-Calc overview table -> experiments/e7_calphad_prior/results/overview.md
# on a Slurm cluster (48 cores): sbatch $E1/hprc_structure.slurm ; sbatch experiments/e7_calphad_prior/hprc/priors.slurm
```

No new model runs: the networks are the replies in `experiments/e3_crystal_filter/runs/filter_{K,Cp}__*`. Cells are cached one file each, so an interrupted run resumes.

## 4h. Size of the written network (experiments/e9_network_size/README.md)

```bash
E9=experiments/e9_network_size
python $E9/size_arm.py prompt     # run folders for 64 units and 32 + 32, four tasks, Opus, reps 1 and 2
# replies: $E9/WRAPPER.md, launched as in section 4c
python $E9/size_arm.py score      # -> $E9/results/summary.md
python experiments/e1_surrogate_head/reply_agreement.py   # agreement within and across models -> results/standalone/agreement.json
```

## 5. Parameter counts (docs/research-runs/2026-11-11-where-wsp-fits.md, section 2)

```bash
# MACE-MPA-0 medium, from the local MACE cache, in the mlip-mace env
conda activate mlip-mace && python - <<'EOF'
import torch, os, collections
m = torch.load(os.path.expanduser("~/.cache/mace/macempa0mediummodel"), map_location="cpu", weights_only=False)
print(sum(p.numel() for p in m.parameters()))
print({n: tuple(p.shape) for n, p in m.named_parameters() if n.startswith("readouts")})
EOF
# MatterGen base, from the local Hugging Face cache, in the matinvent env
conda activate matinvent && python - <<'EOF'
import torch, glob, os
f = glob.glob(os.path.expanduser("~/.cache/huggingface/hub/models--microsoft--mattergen/snapshots/*/checkpoints/mattergen_base/checkpoints/last.ckpt"))[0]
print(sum(v.numel() for v in torch.load(f, map_location="cpu", weights_only=False)["state_dict"].values()))
EOF
```

## 6. Literature

The brief, the Claude.ai Research report (266 sources), its source list, the Consensus results, the primary-source notes and the repo surveys are in `research/2026-11-11-wsp-fit/`. They are records of what was returned on 2026-11-11, not something to regenerate.

## 7. Generator task vectors on CrystalFlow and ADiT (E3, added 2026-11-11)

```bash
E3=supplementary/e3_generator_task_vectors
# CrystalFlow statistics on the laptop: copy the base (226 MB, untracked), then
rsync -a <cluster>:$WSP_USER_SCRATCH/checkpoints/crystalflow/ckpt-v1.0.0/DNG-mp-20/ data/large/base_checkpoints/crystalflow/DNG-mp-20/
python $E3/download_checkpoints.py --backbone cf && python $E3/task_vectors.py --backbone cf    # -> results/task_vectors_cf.json
# variants, sampling and scoring on a Slurm cluster, and the ADiT statistics: $E3/hprc/README.md, section "CrystalFlow and ADiT"
#   sbatch --export=ALL,BACKBONE=<cf|adit> prep.slurm ; then array.slurm ; rsync results_<bb>/ -> results/hprc_<bb>/
python $E3/analyze_variants.py --backbone cf        # -> results/variants_summary_cf.{md,json}
python $E3/analyze_variants.py --backbone adit      # -> results/variants_summary_adit.{md,json}
```
