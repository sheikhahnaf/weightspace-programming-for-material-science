"""E6 real papers: GLM-OCR reads the real-paper table crops; value recall against ORCHID.

    env/ocr-venv/bin/python experiments/e6_extraction_reader/read_real.py --split test --tag unedited
    env/ocr-venv/bin/python experiments/e6_extraction_reader/read_real.py --split test --tag opus__rep1 --edit experiments/e6_extraction_reader/edits/opus__rep1.json

Needs data/large/orchid_real/{index.jsonl,crops/} from build_real_set.py (copy that folder
to a CUDA machine as it is; the device is picked by `Reader`: cuda, else mps, else cpu).
Replies hold copied table text, so they are cached untracked under
data/large/orchid_real/replies/<tag>/<table_id>.json; rerunning reads only what is missing.
Only numbers go to the tracked summary results/real_<tag>.json.

`--limit N` takes the first N tables of the split in a fixed shuffled order (seed 0), so a
small run is a random sample and a larger run extends it.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run_reader as rr  # noqa: E402
import score_real as sr  # noqa: E402

REAL = sr.REAL


def tables(split: str, limit: int | None = None, ids: list[str] | None = None) -> list[dict]:
    rows = [json.loads(line) for line in (REAL / "index.jsonl").read_text().splitlines() if line.strip()]
    rows = [r for r in rows if split == "all" or r["split"] == split]
    if ids:
        return [r for r in rows if r["table_id"] in ids]
    rows.sort(key=lambda r: r["table_id"])
    random.Random(0).shuffle(rows)
    return rows[:limit]


def run(split: str, tag: str, edit: dict | None = None, limit: int | None = None, ids: list[str] | None = None,
        max_new_tokens: int = 4096, cached_only: bool = False) -> dict:
    from PIL import Image

    out = REAL / "replies" / tag
    out.mkdir(parents=True, exist_ok=True)
    todo = tables(split, limit, ids)
    reader, read_now, seconds = None, 0, 0.0
    for i, table in enumerate(todo):
        cache = out / f"{table['table_id']}.json"
        if cache.exists() or cached_only:
            continue
        reader = reader or rr.Reader(edit)
        start = time.time()
        reply = reader.read(Image.open(REAL / table["crop"]).convert("RGB"), max_new_tokens=max_new_tokens)
        took = time.time() - start
        new_tokens = len(reader.processor.tokenizer(reply, add_special_tokens=False)["input_ids"])
        cache.write_text(json.dumps({"table_id": table["table_id"], "model": rr.MODEL, "revision": rr.REVISION, "tag": tag,
                                     "prompt": "Table Recognition:", "max_new_tokens": max_new_tokens, "reply_tokens": new_tokens,
                                     "seconds": round(took, 1), "device": reader.device, "edit_entries": len(edit or {}),
                                     "replies": [reply]}, indent=1, ensure_ascii=False) + "\n")
        read_now += 1
        seconds += took
        print(f"{i + 1}/{len(todo)} {table['table_id']} {took:.0f}s {new_tokens} tokens", flush=True)

    wanted = {t["table_id"] for t in todo}
    summary = sr.score(out)
    kept = {k: v for k, v in summary["per_table"].items() if k in wanted}
    if len(kept) != len(summary["per_table"]):  # the folder holds replies outside this selection: score the selection only
        only = REAL / "replies" / f".{tag}.selection.jsonl"
        index = [json.loads(line) for line in (REAL / "index.jsonl").read_text().splitlines() if line.strip()]
        only.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in index if r["table_id"] in wanted))
        summary = sr.score(out, only)
    metas = [json.loads((out / f"{t['table_id']}.json").read_text()) for t in todo if (out / f"{t['table_id']}.json").exists()]
    summary = {"model": rr.MODEL, "revision": rr.REVISION, "tag": tag, "split": split, "tables_selected": len(todo),
               "edit_entries": len(edit or {}), "max_new_tokens": max_new_tokens,
               "read_this_run": read_now, "seconds_this_run": round(seconds, 1),
               "replies_at_token_limit": sum(m.get("reply_tokens", 0) >= m.get("max_new_tokens", 1 << 30) - 1 for m in metas),
               "forward_passes": sum(m.get("reply_tokens", 0) for m in metas),
               "devices": sorted({m.get("device", "?") for m in metas}), **summary}
    (HERE / "results" / f"real_{tag}.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({k: v for k, v in summary.items() if k not in ("per_table", "by_stratum")}, indent=1))
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--split", choices=("train", "test", "all"), default="test")
    parser.add_argument("--tag", default="unedited")
    parser.add_argument("--edit", type=Path, default=None, help="logit-bias edit {token id: value}, see edit_arm.py")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--ids", nargs="*", default=None, help="read exactly these table ids")
    parser.add_argument("--max-new-tokens", type=int, default=4096)
    parser.add_argument("--cached-only", action="store_true", help="score the replies already on disk; load no model")
    args = parser.parse_args()
    run(args.split, args.tag, edit=json.loads(args.edit.read_text()) if args.edit else None, limit=args.limit, ids=args.ids,
        max_new_tokens=args.max_new_tokens, cached_only=args.cached_only)


if __name__ == "__main__":
    main()
