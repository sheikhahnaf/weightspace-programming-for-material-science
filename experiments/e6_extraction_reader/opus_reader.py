"""E6 baseline: a frontier model reads the same table crops as the open model.

    env/ocr-venv/bin/python experiments/e6_extraction_reader/opus_reader.py prepare --rendering degraded_raster
    env/ocr-venv/bin/python experiments/e6_extraction_reader/opus_reader.py score

`prepare` writes, per document and rendering, a run folder runs/read__<rendering>__<doc>__<model>/
with the table crops as PNG files and a prompt.txt that lists them. A fresh session of the
model (see WRAPPER.md) looks at each image and writes one HTML table per crop to reply.txt.
`score` parses the replies with the same parser as the open model and scores them with
the benchmark's score_tables.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run_reader as rr  # noqa: E402

RUN = re.compile(r"read__(clean_raster|degraded_raster)__(.+)__(opus|fable|sonnet|haiku)")


def prepare(rendering: str, model: str, docs: list[str] | None) -> None:
    for path in sorted((rr.BENCH / "truth").glob("*.json")):
        truth = json.loads(path.read_text())
        if docs and truth["doc_id"] not in docs:
            continue
        folder = HERE / "runs" / f"read__{rendering}__{truth['doc_id']}__{model}"
        folder.mkdir(parents=True, exist_ok=True)
        lines = []
        for table in truth["tables"]:
            for k, image in enumerate(rr.crop(truth, table, rendering)):
                name = f"{table['id']}__{k}.png"
                image.save(folder / name)
                lines.append(name)
        (folder / "prompt.txt").write_text(
            "Each file below is an image of one table cropped from a page of a paper on a binary alloy phase diagram.\n"
            "Look at each image with the Read tool and transcribe the table exactly as printed: every header and body cell, "
            "character for character (digits, signs, decimal points, units, arrows, subscripts written inline). Do not correct, "
            "convert or complete anything; if a cell is unreadable, give your best reading.\n\n"
            "Images (in this run folder):\n" + "\n".join(lines) + "\n\n"
            "# Reply format\nFor each image, in the order above, one line with `### ` followed by the file name, then the table as HTML "
            "(<table><tr><td>…</td></tr></table>, with rowspan/colspan where cells are merged). No other text.\n")
        (folder / "meta.json").write_text(json.dumps({"arm": "table_reader_baseline", "rendering": rendering, "doc_id": truth["doc_id"],
                                                      "model_alias": model, "crops": lines}, indent=2) + "\n")
        print(folder.name)


def score() -> None:
    import score as bench_score

    groups: dict[tuple, dict] = {}
    for folder in sorted((HERE / "runs").glob("read__*")):
        m = RUN.fullmatch(folder.name)
        if not m or not (folder / "reply.txt").exists():
            continue
        rendering, doc, model = m.groups()
        truth = json.loads((rr.BENCH / "truth" / f"{doc}.json").read_text())
        pred = []
        for block in re.split(r"^###\s*", (folder / "reply.txt").read_text(), flags=re.M)[1:]:
            name, _, body = block.partition("\n")
            pred.append({"table_id": name.strip().split("__")[0], "cells": rr.parse_cells(body)})
        s = bench_score.score_tables(truth, pred)
        g = groups.setdefault((model, rendering), {"cells": 0, "exact": 0, "exact_norm": 0, "num_cells": 0, "num_exact": 0, "documents": 0})
        for k in ("cells", "exact", "exact_norm", "num_cells", "num_exact"):
            g[k] += s["_tot"][k]
        g["documents"] += 1
        (folder / "score.json").write_text(json.dumps({k: s[k] for k in ("cell_exact", "cell_exact_normalised", "numeric_exact")}, indent=2) + "\n")
    out = {f"{m}|{r}": {"documents": g["documents"], "cell_exact": g["exact"] / max(1, g["cells"]),
                        "cell_exact_normalised": g["exact_norm"] / max(1, g["cells"]),
                        "numeric_exact": g["num_exact"] / max(1, g["num_cells"]), "cells": g["cells"]} for (m, r), g in groups.items()}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "frontier_reader.json").write_text(json.dumps(out, indent=2) + "\n")
    for k, v in out.items():
        print(k, {a: (round(b, 3) if isinstance(b, float) else b) for a, b in v.items()})


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("prepare")
    p.add_argument("--rendering", choices=("clean_raster", "degraded_raster"), required=True)
    p.add_argument("--model", default="opus")
    p.add_argument("--docs", nargs="*")
    sub.add_parser("score")
    args = parser.parse_args()
    prepare(args.rendering, args.model, args.docs) if args.command == "prepare" else score()


if __name__ == "__main__":
    main()
