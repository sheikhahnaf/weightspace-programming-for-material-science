#!/bin/bash
#SBATCH --job-name=wsp_e3
#SBATCH --output=/scratch/group/arroyave_lab/ahnafalvi/wsp/logs/variant_%A_%a.out
#SBATCH --error=/scratch/group/arroyave_lab/ahnafalvi/wsp/logs/variant_%A_%a.err
#SBATCH --time=12:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --gres=gpu:1
#SBATCH --partition=gpu
#SBATCH --mem=48G
#SBATCH --account=142705330300
#SBATCH --array=0-10

# E3 step C4: one array task per variant of one backbone (sbatch --export=ALL,BACKBONE=cf
# array.slurm; default mg). Samples N crystals (same seed for every variant) and scores each
# with the eSEN bulk-modulus and heat-capacity oracles. Resubmitting continues where a task stopped.
source /scratch/group/arroyave_lab/ahnafalvi/wsp/weighspace-programming/experiments/e3_generator_task_vectors/hprc/env.sh
NAME=$(sed -n "$((SLURM_ARRAY_TASK_ID + 1))p" $VARIANTS/variants.txt)
echo "backbone $BACKBONE  variant $NAME  host $(hostname)  $(date)"; nvidia-smi --query-gpu=name,memory.total --format=csv,noheader || true
$PY -u $E3/hprc/sample_and_score.py --backbone $BACKBONE --variant-dir $VARIANTS/$NAME --out $RESULTS/$NAME --n ${N:-128} --batch 64 --seed ${SEED:-0}
echo "VARIANT_DONE $NAME $(date)"
