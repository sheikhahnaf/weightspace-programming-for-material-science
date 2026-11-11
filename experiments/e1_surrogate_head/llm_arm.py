"""Write the prompt for an LLM arm, or score a reply to it.

    # 1. write the prompt
    python experiments/e1_surrogate_head/llm_arm.py prompt edit  --task loop_bulk_modulus --seed 0
    python experiments/e1_surrogate_head/llm_arm.py prompt edit  --task loop_bulk_modulus --seed 0 --shuffled
    python experiments/e1_surrogate_head/llm_arm.py prompt write --task ti_alloy_youngs_modulus

    # 2. give runs/<id>/prompt.txt to a model, save its reply as runs/<id>/reply.txt,
    #    and fill in runs/<id>/meta.json (model, tools allowed, forward passes, tokens)

    # 3. score it
    python experiments/e1_surrogate_head/llm_arm.py score runs/<id>

A malformed reply raises an error and scores nothing.
"""

from __future__ import annotations

import argparse
import json
import warnings
from pathlib import Path

from wsp import estimate_tokens
from wsp.arms import edit_prompt, score_edit, score_write, write_prompt
from wsp.tasks import TASK_NAMES, load_task

HERE = Path(__file__).resolve().parent


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    commands = parser.add_subparsers(dest="command", required=True)
    prompt = commands.add_parser("prompt")
    prompt.add_argument("arm", choices=("edit", "write"))
    prompt.add_argument("--task", choices=TASK_NAMES, required=True)
    prompt.add_argument("--seed", type=int, default=0)
    prompt.add_argument("--shuffled", action="store_true", help="edit arm: shuffled-weights control")
    prompt.add_argument("--runs", type=Path, default=HERE / "runs")
    scorer = commands.add_parser("score")
    scorer.add_argument("run", type=Path)
    args = parser.parse_args()
    warnings.filterwarnings("ignore")

    if args.command == "prompt":
        task = load_task(args.task)
        if args.arm == "edit":
            text = edit_prompt(task, args.seed, args.shuffled)
            run_id = f"edit__{task.name}__seed{args.seed}" + ("__shuffled" if args.shuffled else "")
        else:
            text = write_prompt(task)
            run_id = f"write__{task.name}"
        folder = args.runs / run_id
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "prompt.txt").write_text(text)
        meta = {
            "arm": args.arm, "task": task.name, "seed": args.seed, "shuffled": args.shuffled,
            "prompt_chars": len(text), "prompt_tokens_estimate": estimate_tokens(text),
            "model": None, "tools_allowed": None, "forward_passes": None,
            "prompt_tokens": None, "reply_tokens": None,
        }
        if not (folder / "meta.json").exists():
            (folder / "meta.json").write_text(json.dumps(meta, indent=2) + "\n")
        print(f"{folder / 'prompt.txt'}  ({len(text):,} characters, about {estimate_tokens(text):,} tokens)")
        return

    meta = json.loads((args.run / "meta.json").read_text())
    reply = (args.run / "reply.txt").read_text()
    task = load_task(meta["task"])
    if meta["arm"] == "edit":
        result = score_edit(task, meta["seed"], reply, meta["shuffled"])
    else:
        result = score_write(task, reply)
    result["meta"] = meta
    (args.run / "score.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k not in ("per_seed", "meta")}, indent=2))
    print(f"wrote {args.run / 'score.json'}")


if __name__ == "__main__":
    main()
