# E3 on FASTER: sample from merged MatterGen checkpoints and score them

Everything is written under `/scratch/group/arroyave_lab/ahnafalvi/wsp/` (user scratch and
home are over quota). The conda env `matinvent-hcap-bo`, the base MatterGen model and the
cached eSEN-30M-OAM weights are read from user scratch, as the published loop's jobs do.

```bash
# from the repo root on the laptop, with an open `ssh faster` master connection
W=/scratch/group/arroyave_lab/ahnafalvi/wsp/weighspace-programming
rsync -avz --relative experiments/e3_generator_task_vectors/ vendor/matgen_bo/closed_loop/calculators/ faster:$W/
ssh faster "sbatch $W/experiments/e3_generator_task_vectors/hprc/prep.slurm"      # download, variants, smoke test
ssh faster "sbatch $W/experiments/e3_generator_task_vectors/hprc/array.slurm"     # 11 variants x 128 crystals
ssh faster "squeue -u \$USER"

# results back (small text files only)
rsync -avz --include='*/' --include='scores.csv' --include='sampling_seconds.txt' --include='generated_crystals.extxyz' \
      --include='manifest.json' --exclude='*' \
      faster:/scratch/group/arroyave_lab/ahnafalvi/wsp/results/ experiments/e3_generator_task_vectors/results/hprc/
python experiments/e3_generator_task_vectors/analyze_variants.py
```

Both jobs are safe to resubmit: downloads, variants, samples and per-structure scores that
already exist are kept.

## CrystalFlow and ADiT

The same two jobs take a backbone: `sbatch --export=ALL,BACKBONE=cf` or `BACKBONE=adit`
(default `mg`, which keeps the folders above). Each backbone has its own folders under
`/scratch/group/arroyave_lab/ahnafalvi/wsp/`: `variants_<bb>/`, `results_<bb>/`, `smoke_<bb>/`.

What is read from user scratch, never written:

| | CrystalFlow | ADiT |
|---|---|---|
| base checkpoint | `checkpoints/crystalflow/ckpt-v1.0.0/DNG-mp-20/epoch=2694-step=72765.ckpt` | `checkpoints/adit/ldm.ckpt` (denoiser), `vae.ckpt` (frozen autoencoder) |
| model and sampler | the loop's `src.p3_models.crystalflow_suite` in `matinvent-hcap-bo/` | the loop's `src.p3_models.adit_suite` |
| upstream code | `diffusion-zoo-repos/CrystalFlow` | `diffusion-zoo-repos/all-atom-diffusion-transformer` |

A variant is the base Lightning checkpoint with its state dict changed, so it loads through
the loop's own `load_model`. The loop's sampler is called with `oversample_factor=1`, in
chunks of 64, after one `torch.manual_seed(0)`: 128 crystals, the same noise for every
variant of a backbone, no validity filter. The prep job also writes the task-vector
statistics to `wsp/task_vectors/task_vectors_<bb>.json` (the ADiT base is 2.5 GB and is not
copied to the laptop).

```bash
W=/scratch/group/arroyave_lab/ahnafalvi/wsp/weighspace-programming
H=$W/experiments/e3_generator_task_vectors/hprc
rsync -avz --relative --exclude results --exclude runs --exclude __pycache__ experiments/e3_generator_task_vectors/ faster:$W/
ssh faster "cd $H && sbatch --export=ALL,BACKBONE=cf prep.slurm"
ssh faster "cd $H && sbatch --export=ALL,BACKBONE=adit --time=04:00:00 --mem=64G prep.slurm"
# when logs/prep_<job>.out shows SMOKE_DONE (variants built, 2 crystals scored):
ssh faster "cd $H && sbatch --export=ALL,BACKBONE=cf array.slurm"
ssh faster "cd $H && sbatch --export=ALL,BACKBONE=adit array.slurm"

# results back, per backbone (scores and structures only), then the table
for bb in cf adit; do
  rsync -avz --include='*/' --include='scores.csv' --include='generated_crystals.extxyz' --exclude='*' \
        faster:/scratch/group/arroyave_lab/ahnafalvi/wsp/results_$bb/ experiments/e3_generator_task_vectors/results/hprc_$bb/
  python experiments/e3_generator_task_vectors/analyze_variants.py --backbone $bb
done
rsync -avz faster:/scratch/group/arroyave_lab/ahnafalvi/wsp/task_vectors/task_vectors_adit.json experiments/e3_generator_task_vectors/results/
```

The CrystalFlow statistics can also be made on the laptop, after copying the 226 MB base
checkpoint folder: `rsync -a faster:/scratch/user/ahnafalvi/checkpoints/crystalflow/ckpt-v1.0.0/DNG-mp-20/
data/large/base_checkpoints/crystalflow/DNG-mp-20/`, then `task_vectors.py --backbone cf`.
