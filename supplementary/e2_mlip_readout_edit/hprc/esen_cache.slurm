#!/bin/bash
#SBATCH --job-name=wsp_e2_esen
#SBATCH --output=esen_cache_%j.out
#SBATCH --error=esen_cache_%j.err
#SBATCH --time=06:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --gres=gpu:1
#SBATCH --partition=gpu
#SBATCH --mem=48G

# E2, eSEN-30M-OAM: cache the energy head's inputs for the 15 DFT-validated crystals
# and the 400 crystals of the elastic set. Resumable: submit again if it hits the limit.
# Cluster-specific settings come from the environment, nothing is hard-coded:
#   sbatch --account=<your account> --chdir=$WSP_WORK/logs --export=ALL <this file>
: "${WSP_WORK:?set WSP_WORK to the work directory that holds the repository copy}"
: "${WSP_USER_SCRATCH:?set WSP_USER_SCRATCH to the directory that holds the Python environments (envs/)}"
source ${WSP_WORK}/weighspace-programming/supplementary/e3_generator_task_vectors/hprc/env.sh
echo "host $(hostname)  $(date)"; nvidia-smi --query-gpu=name,memory.total --format=csv,noheader || true
E2=$REPO/supplementary/e2_mlip_readout_edit
for set in dft15 elastic; do
  $PY -u $E2/cache_features_esen.py --set $set --reference $REPO/data/mlip_reference --out $WORK/mlip_cache_esen_v3
done
echo "ESEN_DONE $(date)"
