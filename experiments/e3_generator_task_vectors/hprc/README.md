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
