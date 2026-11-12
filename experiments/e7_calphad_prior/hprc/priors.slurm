#!/bin/bash
#SBATCH --job-name=wsp_e7_priors
#SBATCH --output=/scratch/group/arroyave_lab/ahnafalvi/wsp/logs/e7_priors_%j.out
#SBATCH --time=12:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=48
#SBATCH --mem=120G
#SBATCH --partition=cpu
#SBATCH --account=142705330300
# E7: GP mean arms (static) and BO for every registered Thermo-Calc task. No Thermo-Calc
# is needed here: the pools are the CSV tables under data/calphad/. Results are cached per
# cell under experiments/e7_calphad_prior/results/, so the job resumes and can be merged
# with cells computed elsewhere.
cd /scratch/group/arroyave_lab/ahnafalvi/wsp/weighspace-programming
export PYTHONPATH=src OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
PY=/scratch/user/ahnafalvi/envs/matinvent-bo/bin/python
STAGE=${STAGE:-all}
if [ "$STAGE" != bo ]; then $PY -W ignore experiments/e7_calphad_prior/run_priors.py static --jobs 46; fi
if [ "$STAGE" != static ]; then $PY -W ignore experiments/e7_calphad_prior/run_priors.py bo --seeds 20 --steps 25 --jobs 46; fi
