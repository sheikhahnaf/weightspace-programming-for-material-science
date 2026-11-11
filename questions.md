# Questions

Every substantive question asked of this project, in the asker's words. Rows are appended; an old answer is never rewritten. A corrected answer is a new row that links the old one.

Status: **researched** (an evidence page answers it) · **answered from the repo** (read off existing pages) · **inference only** (reasoning, no page carries it) · **tooling**.

| Date | Question (verbatim) | One-line answer | Evidence | Status |
|---|---|---|---|---|
| 2026-11-11 | "find out where can weight space programming fit? either for BO surrogate,mlip or generative model" | The BO surrogate's readout head or prior mean now; the MLIP only at its scalar readout (2,283 of 9,063,204 weights for MACE-MPA-0 medium); not the generative model in the narrow sense, where task vectors of the existing fine-tuned checkpoints are the useful route. | [`docs/research-runs/2026-11-11-where-wsp-fits.md`](docs/research-runs/2026-11-11-where-wsp-fits.md); sources in `research/2026-11-11-wsp-fit/` | researched |
| 2026-11-11 | "set up a research campaign to set up and test this idea across different applications in computational material science , dataset ,algo everything is in the folders i named" | Four experiments over BO surrogate, MLIP and generator; five regression tasks built from the copied data; baselines and a first LLM pilot run on E1. The pilot found no weight reading in the edit arm and a small-data ranking gain from written prior means. | [`docs/results/2026-11-11-e1-pilot.md`](docs/results/2026-11-11-e1-pilot.md); `experiments/`; `REPRODUCE.md` | researched (pilot: single LLM runs) |
