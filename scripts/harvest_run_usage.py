"""Fill each LLM run's meta.json from the stored subagent transcripts, and audit tool use.

Claude Code keeps a transcript of every subagent under
~/.claude/projects/<project>/<session>/subagents/agent-*.jsonl. For each run folder
this finds the transcript that produced it and records what the harness logged,
instead of what the model said about itself:

  model id, start time, duration, output tokens, context size at the last turn,
  and every tool call with the file it touched.

The audit passes when the only tools used were Read and Write, the only files read
were the wrapper and the run's own prompt, and the only files written were in the
run's own folder. Runs that fail it are listed and marked in meta.json.

    python scripts/harvest_run_usage.py                      # this session's transcripts
    python scripts/harvest_run_usage.py --subagents <dir>    # another session's
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT = Path.home() / ".claude/projects/-Volumes-SSD1-SMAAA-weighspace-programming"
RUN_PATH = re.compile(r"experiments/(e\d_[a-z_]+)/runs/([A-Za-z0-9_]+)/prompt\.txt")
RUN_VAR = re.compile(r"experiments/(e\d_[a-z_]+)/WRAPPER\.md.*?RUN\s*=\s*([A-Za-z0-9_]+)", re.S)
RUN_VAR_OLD = re.compile(r"RUN=\S*experiments/(e\d_[a-z_]+)/runs/([A-Za-z0-9_]+)")


def text_of(message) -> str:
    content = message.get("content") if isinstance(message, dict) else None
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return " ".join(c.get("text", "") for c in content if isinstance(c, dict))
    return ""


def parse(path: Path) -> dict | None:
    rows = [json.loads(line) for line in path.open() if line.strip()]
    first = next((r for r in rows if r.get("type") == "user"), None)
    if first is None:
        return None
    prompt = text_of(first.get("message", {}))
    match = RUN_VAR.search(prompt) or RUN_VAR_OLD.search(prompt) or RUN_PATH.search(prompt)
    if not match:
        return None
    experiment, run = match.group(1), match.group(2)
    models, tools, out_tokens, context = set(), [], 0, 0
    for r in rows:
        m = r.get("message", {})
        if r.get("type") != "assistant" or not isinstance(m, dict):
            continue
        if m.get("model"):
            models.add(m["model"])
        usage = m.get("usage") or {}
        out_tokens += usage.get("output_tokens", 0)
        context = max(context, usage.get("input_tokens", 0) + usage.get("cache_creation_input_tokens", 0)
                      + usage.get("cache_read_input_tokens", 0))
        for item in m.get("content") or []:
            if isinstance(item, dict) and item.get("type") == "tool_use":
                tools.append({"tool": item.get("name"), "file": (item.get("input") or {}).get("file_path")})
    stamps = [datetime.fromisoformat(r["timestamp"].replace("Z", "+00:00")) for r in rows if r.get("timestamp")]
    folder = ROOT / "experiments" / experiment / "runs" / run
    allowed_read = {str(folder / "prompt.txt"), str(ROOT / "experiments" / experiment / "WRAPPER.md")}
    problems = []
    for call in tools:
        if call["tool"] == "Read" and call["file"] in allowed_read:
            continue
        if call["tool"] == "Write" and call["file"] and Path(call["file"]).parent == folder:
            continue
        problems.append(call)
    return {
        "experiment": experiment, "run": run, "transcript": path.name,
        "model_id": sorted(models)[0] if len(models) == 1 else sorted(models),
        "started_utc": stamps[0].isoformat() if stamps else None,
        "duration_ms": int((stamps[-1] - stamps[0]).total_seconds() * 1000) if stamps else None,
        "output_tokens": out_tokens, "context_tokens_last_turn": context,
        "tool_calls": tools, "audit_ok": not problems, "audit_problems": problems,
        "wrote_reply": any(c["tool"] == "Write" and c["file"] == str(folder / "reply.txt") for c in tools),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--subagents", type=Path, default=None)
    args = parser.parse_args()
    folders = [args.subagents] if args.subagents else sorted(DEFAULT.glob("*/subagents"))

    by_run: dict[tuple[str, str], list[dict]] = {}
    for folder in folders:
        for path in sorted(folder.glob("agent-*.jsonl")):
            record = parse(path)
            if record:
                by_run.setdefault((record["experiment"], record["run"]), []).append(record)

    audit, failed = [], []
    for (experiment, run), records in sorted(by_run.items()):
        folder = ROOT / "experiments" / experiment / "runs" / run
        if not (folder / "meta.json").exists():
            continue
        records.sort(key=lambda r: r["started_utc"] or "")
        final = next((r for r in reversed(records) if r["wrote_reply"]), records[-1])
        meta = json.loads((folder / "meta.json").read_text())
        meta.update({
            "model": final["model_id"],
            "harness": "Claude Code subagent, fresh context",
            "date": (final["started_utc"] or "")[:10],
            "started_utc": final["started_utc"], "duration_ms": final["duration_ms"],
            "output_tokens": final["output_tokens"],
            "context_tokens_last_turn": final["context_tokens_last_turn"],
            "tool_calls": final["tool_calls"], "tool_calls_observed": len(final["tool_calls"]),
            "forward_passes": 0, "attempts": len(records),
            "audit_ok": final["audit_ok"], "audit_problems": final["audit_problems"],
            "transcript": final["transcript"],
            "token_note": "output_tokens and context size are read from the harness transcript; "
                          "output tokens include the model's reasoning",
        })
        (folder / "meta.json").write_text(json.dumps(meta, indent=2) + "\n")
        report = folder / "self_report.txt"
        if report.exists() and not (folder / "model_self_report.md").exists():
            (folder / "model_self_report.md").write_text(
                "# What the model said it did\n\nWritten by the model after its reply; not verified beyond "
                "the scored reply itself.\n\n> " + report.read_text().strip().replace("\n", "\n> ") + "\n")
        audit.append({k: final[k] for k in ("experiment", "run", "model_id", "started_utc", "duration_ms",
                                             "output_tokens", "context_tokens_last_turn", "audit_ok")}
                     | {"tool_calls": len(final["tool_calls"]), "attempts": len(records)})
        if not final["audit_ok"]:
            failed.append((experiment, run, final["audit_problems"]))
    (ROOT / "experiments" / "runs_audit.json").write_text(json.dumps(audit, indent=1) + "\n")

    models: dict[str, list] = {}
    for a in audit:
        models.setdefault(str(a["model_id"]), []).append(a)
    print(f"{len(audit)} runs matched to transcripts; {len(failed)} failed the tool audit")
    for model, rows in sorted(models.items()):
        out = sorted(r["output_tokens"] for r in rows)
        dur = sorted(r["duration_ms"] / 1000 for r in rows)
        print(f"  {model:28s} {len(rows):3d} runs  output tokens median {out[len(out) // 2]:6d} (max {out[-1]})  "
              f"duration median {dur[len(dur) // 2]:.0f} s (max {dur[-1]:.0f} s)")
    for experiment, run, problems in failed:
        print(f"  AUDIT FAILED {experiment}/{run}: {problems}")


if __name__ == "__main__":
    main()
