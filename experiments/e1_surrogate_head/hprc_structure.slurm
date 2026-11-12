#!/bin/bash
#SBATCH --job-name=wsp_e1_struct
#SBATCH --output=e1_struct_%j.out
#SBATCH --time=08:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=48
#SBATCH --mem=120G
#SBATCH --partition=cpu
# E1: written networks as prior mean and as GP inputs for the structure-based surrogates.
# Cells are cached under results/structure_prior/, so the job resumes.
# Cluster-specific settings come from the environment, nothing is hard-coded:
#   sbatch --account=<your account> --chdir=$WSP_WORK/logs --export=ALL <this file>
: "${WSP_WORK:?set WSP_WORK to the work directory that holds the repository copy}"
: "${WSP_USER_SCRATCH:?set WSP_USER_SCRATCH to the directory that holds the Python environments (envs/)}"
cd ${WSP_WORK}/weighspace-programming
export PYTHONPATH=src:${WSP_WORK}/pylibs OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
PY=${WSP_USER_SCRATCH}/envs/matinvent-bo/bin/python
$PY -W ignore experiments/e1_surrogate_head/run_structure_features.py --jobs 46
$PY -W ignore experiments/e1_surrogate_head/run_structure_prior.py --jobs 46
