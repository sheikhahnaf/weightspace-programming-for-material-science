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

# E3 prep and smoke test for one backbone (sbatch --export=ALL,BACKBONE=cf prep.slurm; default mg):
# download its fine-tuned checkpoints, build the variants, then sample 4 crystals from the
# base and score 2 of them with both oracles. For cf and adit the task-vector statistics are
# computed here too, after the smoke test, because their base checkpoints live on the cluster.
source /scratch/group/arroyave_lab/ahnafalvi/wsp/weighspace-programming/supplementary/e3_generator_task_vectors/hprc/env.sh
echo "host $(hostname)  $(date)"; nvidia-smi --query-gpu=name,memory.total --format=csv,noheader || true

echo "backbone $BACKBONE"
$PY -u $E3/download_checkpoints.py --backbone $BACKBONE
$PY -u $E3/hprc/make_variants.py --backbone $BACKBONE --base-dir $BASE_MODEL --finetuned $FINETUNED --out $VARIANTS
$PY -u $E3/hprc/sample_and_score.py --backbone $BACKBONE --variant-dir $VARIANTS/base --out $SMOKE --n 4 --batch 4 --limit 2
echo "SMOKE_DONE $(date)"
if [ "$BACKBONE" != mg ]; then
  $PY -u $E3/task_vectors.py --backbone $BACKBONE --base "$BASE_CKPT" --finetuned $FINETUNED --out $WORK/task_vectors
fi
echo "PREP_DONE $(date)"
