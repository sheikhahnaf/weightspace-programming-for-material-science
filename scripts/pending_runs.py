"""List LLM runs that have a prompt but no reply yet (to resume after an interruption).

    python scripts/pending_runs.py            # run names, one per line
    python scripts/pending_runs.py --done     # runs with a reply but no score
"""
import sys
from pathlib import Path

RUNS = Path(__file__).resolve().parents[1] / "experiments" / "e1_surrogate_head" / "runs"
done = "--done" in sys.argv
for folder in sorted(RUNS.iterdir()):
    if not (folder / "prompt.txt").exists():
        continue
    has_reply, has_score = (folder / "reply.txt").exists(), (folder / "score.json").exists()
    if (done and has_reply and not has_score) or (not done and not has_reply):
        print(folder.name)
