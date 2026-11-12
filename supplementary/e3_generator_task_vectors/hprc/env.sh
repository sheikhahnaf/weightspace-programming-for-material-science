# Sourced by the E3 jobs on the cluster. Paths follow the published loop's own job scripts.
# User scratch is over its inode quota, so everything is WRITTEN under group scratch;
# the conda env, the base model and the cached eSEN weights are only READ from user scratch.
set -euo pipefail
module purge
module load GCC/13.2.0 CUDA/12.2.0 Anaconda3/2024.02-1 WebProxy

export USER_SCRATCH="${WSP_USER_SCRATCH:?set WSP_USER_SCRATCH}"
export WORK="${WSP_WORK:?set WSP_WORK}"
export REPO=$WORK/weighspace-programming
export E3=$REPO/supplementary/e3_generator_task_vectors
export PY=$USER_SCRATCH/envs/matinvent-hcap-bo/bin/python
export FINETUNED=$REPO/data/large/finetuned_diffusion

# One backbone per job: BACKBONE=mg (default), cf or adit, passed with sbatch --export=ALL,BACKBONE=cf.
# MatterGen keeps the folders it had before the other backbones were added.
export BACKBONE=${BACKBONE:-mg}
case "$BACKBONE" in
  mg)   export BASE_MODEL=$USER_SCRATCH/matinvent-bo/src/mattergen/checkpoints/mattergen_base
        export VARIANTS=$WORK/variants RESULTS=$WORK/results SMOKE=$WORK/smoke ;;
  cf)   export BASE_MODEL=$USER_SCRATCH/checkpoints/crystalflow/ckpt-v1.0.0/DNG-mp-20
        export BASE_CKPT="$BASE_MODEL/epoch=*.ckpt" ;;
  adit) export BASE_MODEL=$USER_SCRATCH/checkpoints/adit
        export BASE_CKPT=$BASE_MODEL/ldm.ckpt ADIT_VAE=$BASE_MODEL/vae.ckpt ;;
  *)    echo "unknown BACKBONE $BACKBONE" >&2; exit 2 ;;
esac
if [ "$BACKBONE" != mg ]; then
  export VARIANTS=$WORK/variants_$BACKBONE RESULTS=$WORK/results_$BACKBONE SMOKE=$WORK/smoke_$BACKBONE
  # CrystalFlow and ADiT are loaded and sampled with the published loop's own classes, read in
  # place (never written): its project folder, the MatInvent tree it ran in, and the upstream repos.
  export SCRATCH=$USER_SCRATCH
  export LOOP_PROJECT=$USER_SCRATCH/matinvent-hcap-bo LOOP_PRISTINE=$USER_SCRATCH/matinvent-pristine
  export CRYSTALFLOW_REPO=$USER_SCRATCH/diffusion-zoo-repos/CrystalFlow
  export ADIT_REPO=$USER_SCRATCH/diffusion-zoo-repos/all-atom-diffusion-transformer
  export PROJECT_ROOT=$CRYSTALFLOW_REPO HYDRA_JOBS=$WORK/hydra WABDB=offline   # what CrystalFlow's .env sets
  export PYTHONDONTWRITEBYTECODE=1 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
fi

# The token file is the one the loop's jobs source; it is read here, never printed.
if [ -f "$USER_SCRATCH/.secrets/hf_token.env" ]; then set -a; . "$USER_SCRATCH/.secrets/hf_token.env"; set +a; fi
export FAIRCHEM_LOCAL_CACHE="$USER_SCRATCH/.cache/huggingface"
export HF_HOME=$WORK/hf_home          # keep Hugging Face metadata out of $HOME (10 GB, full)
export PYTHONNOUSERSITE=1
export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK:-8}
mkdir -p "$WORK/logs" "$VARIANTS" "$RESULTS" "$HF_HOME" "$WORK/cwd"
cd "$WORK/cwd"                        # anything a library drops in the working directory lands here
