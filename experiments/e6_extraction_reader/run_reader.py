"""E6: an open-weights document model reading thermodynamic tables, scored on ORCHID-Bench.

ORCHID-Bench (github.com/orchid-calphad/orchid-bench, commit 584d34a; code MIT, documents
and truth keys CC BY 4.0) has 20 synthetic CALPHAD papers with exact truth keys, each
rendered as a clean 300 dpi page image and a degraded 150 dpi scan. This script crops
every table with the truth key's region (the same oracle crop the benchmark's Tesseract
baseline gets), asks GLM-OCR (zai-org/GLM-OCR, MIT, pinned revision) for the table, parses
the reply into cells and scores it with the benchmark's own `score_tables`.

    env/ocr-venv/bin/python experiments/e6_extraction_reader/run_reader.py --rendering clean_raster
    env/ocr-venv/bin/python experiments/e6_extraction_reader/run_reader.py --rendering degraded_raster

Replies are cached per crop under results/<tag>/<rendering>/, so reruns only score.
`--edit file.json` applies a logit-bias edit (see edit_arm.py) before reading.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BENCH = ROOT / "data" / "large" / "orchid_bench" / "bench"
MODEL = "zai-org/GLM-OCR"
REVISION = "2e85a62840ccac27daa451df36c736c4636b8628"
sys.path.insert(0, str(BENCH))


class _Table(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows, self.cell, self.span = [], None, (1, 1)

    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self.rows.append([])
        elif tag in ("td", "th"):
            a = dict(attrs)
            self.cell, self.span = "", (int(a.get("rowspan", 1) or 1), int(a.get("colspan", 1) or 1))

    def handle_data(self, data):
        if self.cell is not None:
            self.cell += data

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self.cell is not None:
            if not self.rows:
                self.rows.append([])
            self.rows[-1].append((self.cell.strip(), *self.span))
            self.cell = None


def parse_cells(reply: str) -> list[dict]:
    """HTML or Markdown table -> [{row, col, text}], spans expanded to their top-left cell."""
    cells = []
    if "<td" in reply or "<th" in reply:
        parser = _Table()
        parser.feed(reply)
        taken: set[tuple[int, int]] = set()
        for r, row in enumerate(parser.rows):
            c = 0
            for text, rs, cs in row:
                while (r, c) in taken:
                    c += 1
                cells.append({"row": r, "col": c, "text": html.unescape(text)})
                for dr in range(rs):
                    for dc in range(cs):
                        taken.add((r + dr, c + dc))
                c += cs
        return cells
    r = 0
    for line in reply.splitlines():
        line = line.strip()
        if not line.startswith("|") or re.fullmatch(r"[|\s:\-]+", line):
            continue
        for c, text in enumerate(line.strip("|").split("|")):
            cells.append({"row": r, "col": c, "text": text.strip()})
        r += 1
    return cells


def crop(truth, table, rendering: str, margin: float = 0.02):
    from PIL import Image

    info = truth["renderings"][rendering]
    out = []
    for seg in table["segments"]:
        entry = info["files"][seg["page"]]
        name = Path(entry["file"] if isinstance(entry, dict) else entry).name
        page = BENCH / "docs" / truth["doc_id"] / ("clean" if rendering == "clean_raster" else "degraded") / name
        image = Image.open(page).convert("RGB")
        pts = np.array(seg["corners"][rendering])
        x0, y0, x1, y1 = pts[:, 0].min(), pts[:, 1].min(), pts[:, 0].max(), pts[:, 1].max()
        mx, my = margin * image.width, margin * image.height * 0.5
        out.append(image.crop((max(0, x0 - mx), max(0, y0 - my), min(image.width, x1 + mx), min(image.height, y1 + my))))
    return out


class Reader:
    def __init__(self, edit: dict | None = None):
        import torch
        from transformers import AutoModelForImageTextToText, AutoProcessor

        cache = ROOT / "data" / "large" / "hf"
        self.torch = torch
        self.device = "cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu")
        self.processor = AutoProcessor.from_pretrained(MODEL, revision=REVISION, cache_dir=cache)
        self.model = AutoModelForImageTextToText.from_pretrained(MODEL, revision=REVISION, cache_dir=cache, dtype=torch.float32).to(self.device).eval()
        self.bias = None
        if edit:
            self.set_bias(edit)

    def set_bias(self, edit: dict[str, float]) -> None:
        """A logit bias per vocabulary entry, added to the output layer (token id -> value)."""
        vocab = self.model.config.text_config.vocab_size
        bias = self.torch.zeros(vocab)
        for token_id, value in edit.items():
            bias[int(token_id)] = float(value)
        self.bias = bias.to(self.device)

    def read(self, image, prompt: str = "Table Recognition:", max_new_tokens: int = 2048) -> str:
        messages = [{"role": "user", "content": [{"type": "image", "image": image}, {"type": "text", "text": prompt}]}]
        inputs = self.processor.apply_chat_template(messages, tokenize=True, add_generation_prompt=True, return_dict=True, return_tensors="pt").to(self.device)
        inputs.pop("token_type_ids", None)
        processors = []
        if self.bias is not None:
            bias = self.bias
            processors.append(lambda ids, scores: scores + bias.to(scores.dtype))
        with self.torch.no_grad():
            out = self.model.generate(**inputs, max_new_tokens=max_new_tokens, do_sample=False, logits_processor=processors or None)
        return self.processor.decode(out[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)


def run(rendering: str, tag: str, docs: list[str] | None = None, edit: dict | None = None, limit: int | None = None, cached_only: bool = False) -> dict:
    import score as bench_score

    out = HERE / "results" / tag / rendering
    out.mkdir(parents=True, exist_ok=True)
    reader = None
    per_doc, total = {}, {"cells": 0, "exact": 0, "exact_norm": 0, "num_cells": 0, "num_exact": 0}
    by_id: dict[str, dict] = {}
    truths = sorted((BENCH / "truth").glob("*.json"))
    for path in truths[:limit]:
        truth = json.loads(path.read_text())
        if docs and truth["doc_id"] not in docs:
            continue
        pred = []
        if cached_only and not all((out / f"{truth['doc_id']}__{t['id']}.json").exists() for t in truth["tables"]):
            continue
        for table in truth["tables"]:
            cache = out / f"{truth['doc_id']}__{table['id']}.json"
            if cache.exists():
                replies = json.loads(cache.read_text())["replies"]
            else:
                reader = reader or Reader(edit)
                replies = [reader.read(image) for image in crop(truth, table, rendering)]
                cache.write_text(json.dumps({"doc_id": truth["doc_id"], "table": table["id"], "rendering": rendering, "replies": replies}, indent=1, ensure_ascii=False) + "\n")
            for reply in replies:
                pred.append({"table_id": table["id"], "cells": parse_cells(reply)})
        s = bench_score.score_tables(truth, pred)
        per_doc[truth["doc_id"]] = {k: s[k] for k in ("cell_exact", "cell_exact_normalised", "numeric_exact")}
        for k in total:
            total[k] += s["_tot"][k]
        for tid, b in s["_by_id"].items():
            agg = by_id.setdefault(tid, {"cells": 0, "exact": 0, "num_cells": 0, "num_exact": 0})
            for k in agg:
                agg[k] += b[k]
        print(truth["doc_id"], per_doc[truth["doc_id"]], flush=True)
    summary = {"model": MODEL, "revision": REVISION, "rendering": rendering, "tag": tag, "documents": len(per_doc),
               "cell_exact": total["exact"] / max(1, total["cells"]), "cell_exact_normalised": total["exact_norm"] / max(1, total["cells"]),
               "numeric_exact": total["num_exact"] / max(1, total["num_cells"]), "cells": total["cells"], "numeric_cells": total["num_cells"],
               "by_table": {k: {"cell_exact": v["exact"] / max(1, v["cells"]), "numeric_exact": v["num_exact"] / max(1, v["num_cells"]), "cells": v["cells"]} for k, v in by_id.items()},
               "per_doc": per_doc}
    (HERE / "results" / tag / f"summary_{rendering}{'_partial' if cached_only else ''}.json").write_text(json.dumps(summary, indent=2) + "\n")
    print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in summary.items() if k not in ("per_doc", "by_table")})
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--rendering", choices=("clean_raster", "degraded_raster"), required=True)
    parser.add_argument("--tag", default="unedited")
    parser.add_argument("--edit", type=Path, default=None)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--cached-only", action="store_true", help="score the documents already read; load no model")
    args = parser.parse_args()
    run(args.rendering, args.tag, edit=json.loads(args.edit.read_text()) if args.edit else None, limit=args.limit, cached_only=args.cached_only)


if __name__ == "__main__":
    main()
