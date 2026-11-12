#!/bin/bash
#SBATCH --job-name=wsp_e6_reader
#SBATCH --output=/scratch/group/arroyave_lab/ahnafalvi/wsp/logs/reader_%j.out
#SBATCH --error=/scratch/group/arroyave_lab/ahnafalvi/wsp/logs/reader_%j.err
#SBATCH --time=02:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --gres=gpu:1
#SBATCH --partition=gpu
#SBATCH --mem=32G
#SBATCH --account=142705330300

# E6: GLM-OCR over the ORCHID-Bench table crops. Usage: sbatch reader.slurm <tag> [edit.json]
# Replies are cached per crop, so a resubmission only reads what is missing.
module purge
module load GCC/13.2.0 CUDA/12.2.0 Anaconda3/2024.02-1 WebProxy
WORK=/scratch/group/arroyave_lab/ahnafalvi/wsp
E6=$WORK/weighspace-programming/experiments/e6_extraction_reader
export HF_HOME=$WORK/hf_home PYTHONNOUSERSITE=1
cd $WORK/cwd
TAG=${1:-unedited}
EDIT=${2:+--edit $E6/$2}
for r in degraded_raster clean_raster; do
  $WORK/ocr-venv2/bin/python -u $E6/run_reader.py --rendering $r --tag $TAG $EDIT 2>&1 | grep -v "Warning\|Loading"
done
echo "READER_DONE $(date)"
