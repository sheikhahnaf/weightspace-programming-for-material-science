#!/bin/bash
#SBATCH --job-name=wsp_e6_edits
#SBATCH --output=edits_%j.out
#SBATCH --time=02:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --gres=gpu:1
#SBATCH --partition=gpu
#SBATCH --mem=32G

# E6: the edited open model on the ten test documents, one pass per edit file given.
# Cluster-specific settings come from the environment, nothing is hard-coded:
#   sbatch --account=<your account> --chdir=$WSP_WORK/logs --export=ALL <this file>
: "${WSP_WORK:?set WSP_WORK to the work directory that holds the repository copy}"
: "${WSP_USER_SCRATCH:?set WSP_USER_SCRATCH to the directory that holds the Python environments (envs/)}"
module purge
module load GCC/13.2.0 CUDA/12.2.0 WebProxy
WORK=${WSP_WORK}
E6=$WORK/weighspace-programming/supplementary/e6_extraction_reader
export HF_HUB_OFFLINE=1 HF_HOME=$WORK/hf_home PYTHONNOUSERSITE=1
cd $E6
$WORK/ocr-venv2/bin/python -u read_edits.py --rendering degraded_raster "$@" 2>&1 | grep --line-buffered -v "Warning\|Loading"
echo "EDITS_DONE $(date)"
