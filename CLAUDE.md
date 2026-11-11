# weighspace-programming: project rules

## Boundaries

- **Write only inside this folder.** The sibling repos `../matinvent-bo`, `../matgen-BO` and `../autoresearch-bo` are read-only: import from them, read their data, never edit, never run anything that writes there (their scripts write results next to themselves, so call their functions, do not run their scripts).
- Do not reuse the sibling repos' feature caches for any model whose weights were changed: the phonon cache is keyed by model name only and will serve stale vectors.
- Never copy a token or key out of a sibling repo.

## Environment

All Python runs in the `matinvent` conda env (torch 2.4.1, botorch 0.16.1, orb-models, matminer, pytest):

```bash
eval "$(/Users/alvi/miniconda3/bin/conda shell.zsh hook)" && conda activate matinvent && python -m pytest -q
```

MACE is not in `matinvent`; use `mlip-mace` for anything that loads a MACE model. `mat-zoo-modern` has `peft` for LoRA work.

## Terms

- **Weight-space programming (WSP)**, narrow sense: an LLM reads and writes weights directly, no gradient descent. Say "WSP" only for this.
- **Weight-space learning**, broad sense: hypernetworks, generated adapters, task vectors, merging, learning on weight zoos. Never call these WSP.

## Experiment rules

- Every LLM arm has a shuffled-weights control and a gradient baseline given the same number of forward passes.
- Record for every LLM call: model id, tools allowed, forward passes used, prompt and reply tokens from the model's tokenizer, and the raw reply.
- A reply is applied only through `wsp.load_weights` or `wsp.apply_edits`, which reject malformed output without changing anything.
- Report weights changed with `wsp.diff`, and uncertainty calibration before and after any edit to a surrogate.

## Copies

- Datasets and algorithms from the sibling repos are copied only through `scripts/copy_from_siblings.py`, which writes `data/PROVENANCE.md` and replaces any hard-coded token with an environment lookup. Add a line to its manifest; do not copy by hand.
- `vendor/` is never edited. Changes go in `src/wsp/`.
- In the closed-loop tasks every run has its own PCA basis: never fit one model on rows from two runs.

## Records

- Everything needed to rebuild a number is committed: the command in `REPRODUCE.md`, the environment in `env/`, and for every LLM run its prompt, raw reply, meta and score under `experiments/<e>/runs/<id>/`.
- Commit after each completed step and push to `origin` (private GitHub repo).

- `questions.md` at the root indexes every substantive question asked of this project, verbatim, with status. Append rows; never rewrite an old answer.
- Research briefs, reports and source lists live in `research/<date>-<topic>/` and are tracked. The page that draws conclusions from them lives in `docs/research-runs/`.
- Each experiment folder's README ends with a **Status** line that says what has actually been run.
