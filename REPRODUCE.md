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
python -m pytest -q -W ignore                 # 36 tests
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
