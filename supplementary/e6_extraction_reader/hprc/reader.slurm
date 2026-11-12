#!/bin/bash
#SBATCH --job-name=wsp_e6_reader
#SBATCH --output=reader_%j.out
#SBATCH --error=reader_%j.err
#SBATCH --time=02:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --gres=gpu:1
#SBATCH --partition=gpu
#SBATCH --mem=32G

# E6: GLM-OCR over the ORCHID-Bench table crops. Usage: sbatch reader.slurm <tag> [edit.json]
# Replies are cached per crop, so a resubmission only reads what is missing.
# Cluster-specific settings come from the environment, nothing is hard-coded:
#   sbatch --account=<your account> --chdir=$WSP_WORK/logs --export=ALL <this file>
: "${WSP_WORK:?set WSP_WORK to the work directory that holds the repository copy}"
: "${WSP_USER_SCRATCH:?set WSP_USER_SCRATCH to the directory that holds the Python environments (envs/)}"
module purge
module load GCC/13.2.0 CUDA/12.2.0 Anaconda3/2024.02-1 WebProxy
WORK=${WSP_WORK}
E6=$WORK/weighspace-programming/supplementary/e6_extraction_reader
export HF_HUB_OFFLINE=1 HF_HOME=$WORK/hf_home PYTHONNOUSERSITE=1
cd $WORK/cwd
TAG=${1:-unedited}
EDIT=${2:+--edit $E6/$2}
for r in degraded_raster clean_raster; do
  $WORK/ocr-venv2/bin/python -u $E6/run_reader.py --rendering $r --tag $TAG $EDIT 2>&1 | grep -v "Warning\|Loading"
done
echo "READER_DONE $(date)"
