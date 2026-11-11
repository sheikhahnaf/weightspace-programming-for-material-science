# E4: learning from the zoo of fitted surrogates (BO surrogate, broad sense)

**Question.** Do a surrogate's fitted parameters, on their own, predict how well it will rank candidates and how much hypervolume the run will gain, and can that be used to warm-start the next fit?

**Why here.** `autoresearch-bo` saved the full fitted parameters of every surrogate at every iteration: 130 JSON files, 8.3 GB, under `autoresearch-bo/autoresearch-bo/results/posthoc_hyperparams/`, with a tidy table `analysis/df_hyperparams.parquet` and labels (hypervolume, Spearman) in `analysis/df_iter.parquet`. Both that loop and the materials loop refit their surrogate from nothing every iteration.

**Steps.**
1. Read the two parquet files, read-only. Build one row per (benchmark, surrogate, seed, iteration): parameter vector (lengthscales, task covariance, noise, inducing-point summaries) and labels.
2. Predict the surrogate's holdout Spearman and the next-iteration hypervolume gain from the parameter vector, leaving one benchmark out. Baselines: predict from iteration number and surrogate name alone.
3. If step 2 beats its baseline: initialise each refit from the previous iteration's parameters, and separately from the leave-one-benchmark-out prediction, and compare wall time and final hypervolume with the from-scratch refit.
4. Show the same parameter tables to an LLM (they are tens of numbers, not thousands) and ask it to flag surrogates that have collapsed, such as a lengthscale at its bound. Compare with the label.

**Measures.** Leave-one-benchmark-out R² for step 2; paired Wilcoxon over seeds for step 3, the same test the source repo uses.

**Main risk.** Parameters may predict quality only through the benchmark's identity, which the leave-one-out split is there to expose.

**Status.** Specification only.
