"""E6: read the ORCHID-Bench test documents once per logit-bias edit, loading the model once.

    python read_edits.py --rendering degraded_raster edits/counts.json edits/opus__rep1.json ...

Each edit file <tag>.json is read into results/<tag>/<rendering>/ (cached per crop).
Only the test documents of edit_arm.split() are read.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run_reader as rr  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--rendering", default="degraded_raster")
    parser.add_argument("edits", nargs="+", type=Path)
    args = parser.parse_args()
    truths = sorted((rr.BENCH / "truth").glob("*.json"))[10:]
    reader = rr.Reader()
    for path in args.edits:
        tag = path.stem
        reader.set_bias(json.loads(path.read_text()))
        out = HERE / "results" / tag / args.rendering
        out.mkdir(parents=True, exist_ok=True)
        for t in truths:
            truth = json.loads(t.read_text())
            for table in truth["tables"]:
                cache = out / f"{truth['doc_id']}__{table['id']}.json"
                if cache.exists():
                    continue
                replies = [reader.read(image) for image in rr.crop(truth, table, args.rendering)]
                cache.write_text(json.dumps({"doc_id": truth["doc_id"], "table": table["id"], "rendering": args.rendering,
                                             "edit": tag, "replies": replies}, indent=1, ensure_ascii=False) + "\n")
        print("done", tag, flush=True)


if __name__ == "__main__":
    main()
