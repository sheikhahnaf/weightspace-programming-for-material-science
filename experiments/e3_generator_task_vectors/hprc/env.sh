# Sourced by the E3 jobs on FASTER. Paths follow the published loop's own job scripts.
# User scratch is over its inode quota, so everything is WRITTEN under group scratch;
# the conda env, the base model and the cached eSEN weights are only READ from user scratch.
set -euo pipefail
module purge
module load GCC/13.2.0 CUDA/12.2.0 Anaconda3/2024.02-1 WebProxy

export USER_SCRATCH=/scratch/user/ahnafalvi
export WORK=/scratch/group/arroyave_lab/ahnafalvi/wsp
export REPO=$WORK/weighspace-programming
export E3=$REPO/experiments/e3_generator_task_vectors
export PY=$USER_SCRATCH/envs/matinvent-hcap-bo/bin/python
export BASE_MODEL=$USER_SCRATCH/matinvent-bo/src/mattergen/checkpoints/mattergen_base
export FINETUNED=$REPO/data/large/finetuned_diffusion
export VARIANTS=$WORK/variants
export RESULTS=$WORK/results

# The token file is the one the loop's jobs source; it is read here, never printed.
if [ -f "$USER_SCRATCH/.secrets/hf_token.env" ]; then set -a; . "$USER_SCRATCH/.secrets/hf_token.env"; set +a; fi
export FAIRCHEM_LOCAL_CACHE="$USER_SCRATCH/.cache/huggingface"
export HF_HOME=$WORK/hf_home          # keep Hugging Face metadata out of $HOME (10 GB, full)
export PYTHONNOUSERSITE=1
export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK:-8}
mkdir -p "$WORK/logs" "$VARIANTS" "$RESULTS" "$HF_HOME" "$WORK/cwd"
cd "$WORK/cwd"                        # anything a library drops in the working directory lands here
