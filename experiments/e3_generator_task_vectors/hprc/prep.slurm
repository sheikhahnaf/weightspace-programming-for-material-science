#!/bin/bash
#SBATCH --job-name=wsp_e3_prep
#SBATCH --output=/scratch/group/arroyave_lab/ahnafalvi/wsp/logs/prep_%j.out
#SBATCH --error=/scratch/group/arroyave_lab/ahnafalvi/wsp/logs/prep_%j.err
#SBATCH --time=01:30:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --gres=gpu:1
#SBATCH --partition=gpu
#SBATCH --mem=48G
#SBATCH --account=142705330300

# E3 prep and smoke test: download the fine-tuned MatterGen checkpoints, build the
# variants, then sample 4 crystals from the base and score 2 of them with both oracles.
source /scratch/group/arroyave_lab/ahnafalvi/wsp/weighspace-programming/experiments/e3_generator_task_vectors/hprc/env.sh
echo "host $(hostname)  $(date)"; nvidia-smi --query-gpu=name,memory.total --format=csv,noheader || true

$PY -u $E3/download_checkpoints.py --backbone mg
$PY -u $E3/hprc/make_variants.py --base-dir $BASE_MODEL --finetuned $FINETUNED --out $VARIANTS
$PY -u $E3/hprc/sample_and_score.py --variant-dir $VARIANTS/base --out $WORK/smoke --n 4 --batch 4 --limit 2
echo "PREP_DONE $(date)"
