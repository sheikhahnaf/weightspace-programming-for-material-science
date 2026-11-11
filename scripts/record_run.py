"""Record how an LLM run was made, next to its prompt and reply.

    python scripts/record_run.py experiments/e1_surrogate_head/runs/<id> \
        --model claude-fable-5-2 --tokens 67249 --duration-ms 45354 \
        --self-report "I judged input 46 to be the leak ..."

Fills meta.json and writes model_self_report.md. The reply itself is never touched.
"""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

HARNESS = "Claude Code subagent, general-purpose type, fresh context"
TOOLS = (
    "Read once (the prompt file) and Write once (the reply file), by instruction; "
    "audited afterwards by the harness's tool-call count; no code execution"
)
TOKEN_NOTE = (
    "subagent_total_tokens is the harness's count for the whole subagent session, including "
    "its system prompt and reasoning; the prompt and reply were not counted separately"
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("run", type=Path)
    parser.add_argument("--model", required=True)
    parser.add_argument("--tokens", type=int, required=True)
    parser.add_argument("--duration-ms", type=int, required=True)
    parser.add_argument("--tool-calls", type=int, default=2)
    parser.add_argument("--forward-passes", type=int, default=0)
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--self-report", required=True)
    args = parser.parse_args()

    if not (args.run / "reply.txt").exists():
        raise SystemExit(f"{args.run} has no reply.txt")
    path = args.run / "meta.json"
    meta = json.loads(path.read_text())
    meta.update(
        {
            "model": f"{args.model} ({HARNESS})",
            "date": args.date,
            "tools_allowed": TOOLS,
            "tool_calls_observed": args.tool_calls,
            "forward_passes": args.forward_passes,
            "subagent_total_tokens": args.tokens,
            "duration_ms": args.duration_ms,
            "token_note": TOKEN_NOTE,
        }
    )
    path.write_text(json.dumps(meta, indent=2) + "\n")
    (args.run / "model_self_report.md").write_text(
        "# What the model said it did\n\n"
        "Reported by the model after writing its reply; not verified beyond the scored reply itself.\n\n"
        f"> {args.self_report.strip()}\n"
    )
    print(f"recorded {args.run.name}")


if __name__ == "__main__":
    main()
