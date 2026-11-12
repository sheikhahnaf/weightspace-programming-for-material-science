# Reproduce

Every number in `docs/` comes from the commands below, run from the repo root in the `matinvent` conda environment. The exact package versions used are in `env/matinvent.yml` and `env/matinvent-pip-freeze.txt` (macOS 26.6.2 arm64, Python 3.10.19, torch 2.4.1, CPU).

```bash
eval "$(/Users/alvi/miniconda3/bin/conda shell.zsh hook)" && conda activate matinvent
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
python experiments/e4_surrogate_zoo/run_zoo.py
```

## 4c. Round 3 (docs/results/2026-11-11-round3.md)

```bash
E1=experiments/e1_surrogate_head; E2=experiments/e2_mlip_readout_edit; E3=experiments/e3_generator_task_vectors
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
#   sampling and scoring on FASTER: $E3/hprc/README.md ; then
python $E3/analyze_variants.py
# model ids, tokens, durations and the tool-call audit for every LLM run
python scripts/harvest_run_usage.py
```

How an LLM run is launched: a fresh Claude Code subagent with the model alias and the one-line prompt "Read <experiment>/WRAPPER.md and follow it exactly, including writing both files. RUN = <run folder>".

## 4d. Round 4 (docs/results/2026-11-11-round4.md)

```bash
E1=experiments/e1_surrogate_head; E2=experiments/e2_mlip_readout_edit; E3=experiments/e3_generator_task_vectors; E5=experiments/e5_bnn_start
# section 1: written filter in front of the generator (needs results/hprc from round 3)
python $E3/filter_arm.py prompt --target K --tag <model>__rep<k> ; python $E3/filter_arm.py score
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
