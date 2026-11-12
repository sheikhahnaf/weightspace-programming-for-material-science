#!/bin/bash
#SBATCH --job-name=wsp_e2_esen
#SBATCH --output=/scratch/group/arroyave_lab/ahnafalvi/wsp/logs/esen_cache_%j.out
#SBATCH --error=/scratch/group/arroyave_lab/ahnafalvi/wsp/logs/esen_cache_%j.err
#SBATCH --time=06:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --gres=gpu:1
#SBATCH --partition=gpu
#SBATCH --mem=48G
#SBATCH --account=142705330300

# E2, eSEN-30M-OAM: cache the energy head's inputs for the 15 DFT-validated crystals
# and the 400 crystals of the elastic set. Resumable: submit again if it hits the limit.
source /scratch/group/arroyave_lab/ahnafalvi/wsp/weighspace-programming/experiments/e3_generator_task_vectors/hprc/env.sh
echo "host $(hostname)  $(date)"; nvidia-smi --query-gpu=name,memory.total --format=csv,noheader || true
E2=$REPO/experiments/e2_mlip_readout_edit
for set in dft15 elastic; do
  $PY -u $E2/cache_features_esen.py --set $set --reference $REPO/data/mlip_reference --out $WORK/mlip_cache_esen
done
echo "ESEN_DONE $(date)"
