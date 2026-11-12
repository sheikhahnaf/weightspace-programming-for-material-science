#!/bin/bash
#SBATCH --job-name=wsp_e1_struct
#SBATCH --output=/scratch/group/arroyave_lab/ahnafalvi/wsp/logs/e1_struct_%j.out
#SBATCH --time=08:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=48
#SBATCH --mem=120G
#SBATCH --partition=cpu
#SBATCH --account=142705330300
# E1: written networks as prior mean and as GP inputs for the structure-based surrogates.
# Cells are cached under results/structure_prior/, so the job resumes.
cd /scratch/group/arroyave_lab/ahnafalvi/wsp/weighspace-programming
export PYTHONPATH=src:/scratch/group/arroyave_lab/ahnafalvi/wsp/pylibs OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
PY=/scratch/user/ahnafalvi/envs/matinvent-bo/bin/python
$PY -W ignore experiments/e1_surrogate_head/run_structure_features.py --jobs 46
$PY -W ignore experiments/e1_surrogate_head/run_structure_prior.py --jobs 46
