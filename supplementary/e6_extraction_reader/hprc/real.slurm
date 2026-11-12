#!/bin/bash
#SBATCH --job-name=wsp_e6_real
#SBATCH --output=real_%j.out
#SBATCH --time=04:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --gres=gpu:1
#SBATCH --partition=gpu
#SBATCH --mem=32G

# E6, real papers: GLM-OCR over the 400 table crops, unedited and with each edit given.
# The crops are publisher material: they live only in the private folder below and are
# linked, not copied, into the repo copy on the cluster. Usage: sbatch real.slurm [tag ...]
# Cluster-specific settings come from the environment, nothing is hard-coded:
#   sbatch --account=<your account> --chdir=$WSP_WORK/logs --export=ALL <this file>
: "${WSP_WORK:?set WSP_WORK to the work directory that holds the repository copy}"
: "${WSP_USER_SCRATCH:?set WSP_USER_SCRATCH to the directory that holds the Python environments (envs/)}"
module purge
module load GCC/13.2.0 CUDA/12.2.0 WebProxy
WORK=${WSP_WORK}
REPO=$WORK/weighspace-programming
export HF_HUB_OFFLINE=1 HF_HOME=$WORK/hf_home PYTHONNOUSERSITE=1
mkdir -p $REPO/data/large
[ -e $REPO/data/large/orchid_real ] || ln -s $WORK/orchid_real_private $REPO/data/large/orchid_real
cd $REPO
E6=supplementary/e6_extraction_reader
for split in test train; do
  $WORK/ocr-venv2/bin/python -u $E6/read_real.py --split $split --tag unedited 2>&1 | grep --line-buffered -v "Warning\|Loading" | tail -n 3
done
for tag in "$@"; do
  $WORK/ocr-venv2/bin/python -u $E6/read_real.py --split test --tag $tag --edit $E6/edits/$tag.json 2>&1 | grep --line-buffered -v "Warning\|Loading" | tail -n 3
done
echo "REAL_DONE $(date)"
