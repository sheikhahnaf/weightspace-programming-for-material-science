#!/bin/bash
#SBATCH --job-name=wsp_e2_grace
#SBATCH --output=/scratch/group/arroyave_lab/ahnafalvi/wsp/logs/grace_features_%j.out
#SBATCH --error=/scratch/group/arroyave_lab/ahnafalvi/wsp/logs/grace_features_%j.err
#SBATCH --time=04:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --gres=gpu:1
#SBATCH --partition=gpu
#SBATCH --mem=64G
#SBATCH --account=142705330300

# E2, GRACE-2L-OAM: output-layer sensitivities, from the last structure down, while the
# laptop works from the first one up. Geometries come from the laptop's cache.
module purge
module load GCC/13.2.0 CUDA/12.2.0 Anaconda3/2024.02-1 WebProxy
WORK=/scratch/group/arroyave_lab/ahnafalvi/wsp
REPO=$WORK/weighspace-programming
export GRACE_CACHE=$WORK/grace_cache
export PYTHONNOUSERSITE=1 TF_CPP_MIN_LOG_LEVEL=2
PY=/scratch/user/ahnafalvi/envs/grace-omat/bin/python
cd $WORK/cwd
echo "host $(hostname) $(date)"
for i in 0 1 2 3; do
  $PY -u $REPO/experiments/e2_mlip_readout_edit/cache_features_grace.py --set elastic --shard $i --of 4 --reverse > $WORK/logs/graceG_$i.log 2>&1 &
done
wait
tail -n 3 $WORK/logs/graceG_*.log
echo "GRACE_DONE $(date)"
