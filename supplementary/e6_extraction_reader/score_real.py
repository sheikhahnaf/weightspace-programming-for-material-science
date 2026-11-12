"""E6 real papers: value recall of a table transcription against the ORCHID literature release.

The label is not a transcription of the table. It is the set of values the ORCHID readers
(Gemini Flash + Claude Opus 5.5 + PDF text layer, multi-reader agreement) took from it, so
the only fair score is recall: of the labelled printed values, how many appear in the
model's cells. Nothing here measures precision or table structure.

    env/ocr-venv/bin/python supplementary/e6_extraction_reader/score_real.py \
        --replies data/large/orchid_real/replies/unedited --out supplementary/e6_extraction_reader/results/real_unedited.json

A reply file is `<table_id>.json` holding `{"replies": [text, ...]}` (or `reply` / `text`:
one string), each text an HTML or Markdown table.

Two kinds of labelled value (the release decides which a record has):
  string   `temperature_printed`, a string exactly as printed. Kept only when it is a bare
           number ("612", "2263.0"); "0 K (static calculation)" and "2428±12" are not targets.
  number   `value_printed`, which the release stores as a JSON number, so the printed
           formatting is gone (1.50 and 1.5 are the same label, the minus glyph is unknown).
           A number label is matched by numeric equality with a number token in a cell.

Two scores per label:
  recall         the value is a number token inside some cell, after normalising only
                 whitespace and the minus sign (−, – or - before a digit become "-").
                 A string label must equal the token text ("2263.0" does not match "2263");
                 a number label must equal it numerically, and may be printed with digit
                 grouping ("26,400", "29 940"). A dash between two numbers ("612-640") is a
                 range, not a sign; a positive label does not match a token that carries a
                 sign.
  recall_strict  some cell is exactly the value and nothing else. For a string label the
                 cell, stripped of outer whitespace, equals the printed string with no
                 other normalisation. For a number label the whole cell is one number token
                 equal to it (minus sign normalised, because the printed glyph is not in
                 the release).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REAL = ROOT / "data" / "large" / "orchid_real"

BARE_NUMBER = re.compile(r"[-−–]?\d+(?:\.\d+)?")
_MINUS = re.compile(r"[−–‐‑-]\s*(?=\.?\d)")
_TOKEN = re.compile(r"(?<![\d.,])\d+(?:\.\d+)?(?!\d|[.,]\d)")
_GROUPED = re.compile(r"(?<![\d.,])\d{1,3}(?:[ ,\u2009\u202f]\d{3})+(?:\.\d+)?(?!\d|[.,]\d)")


def normalise(text: str) -> str:
    """Collapse whitespace; write every minus-like sign that stands before a digit as '-'."""
    return _MINUS.sub("-", " ".join(text.split()))


def tokens(text: str, pattern=_TOKEN) -> list[str]:
    """Number tokens of a normalised text, each with its sign if it has one."""
    out = []
    for m in pattern.finditer(text):
        start = m.start()
        signed = False
        if start and text[start - 1] == "-":
            before = text[: start - 1].rstrip()
            signed = not (before and (before[-1].isdigit() or before[-1] == ")"))  # "612-640", "(1)-5": a dash, not a sign
        out.append(("-" if signed else "") + m.group())
    return out


def _decimal(text: str):
    try:
        return Decimal(text)
    except InvalidOperation:
        return None


class Transcription:
    """The cells of a model reply, indexed for the two matching rules."""

    def __init__(self, cells: list[str]):
        self.raw = {c.strip() for c in cells}
        norm = [normalise(c) for c in cells]
        self.token_text: set[str] = set()
        self.token_number: set[Decimal] = set()
        self.whole_number: set[Decimal] = set()
        for cell in norm:
            toks = tokens(cell)
            self.token_text.update(toks)
            grouped = tokens(cell, _GROUPED)  # "26,400", "29 940": one number, for number labels only
            for tok in toks + grouped:
                d = _decimal(re.sub(r"[ ,\u2009\u202f]", "", tok))
                if d is not None:
                    self.token_number.add(d)
                    if cell == tok:
                        self.whole_number.add(d)
        self.abs_text = {t.lstrip("-") for t in self.token_text}
        self.abs_number = {abs(d) for d in self.token_number}

    def has(self, target: dict) -> tuple[bool, bool]:
        """(recall hit, strict hit) for one labelled value {s, form}."""
        if target["form"] == "number":
            d = _decimal(normalise(target["s"]))
            return d in self.token_number, d in self.whole_number
        return normalise(target["s"]) in self.token_text, target["s"].strip() in self.raw

    def has_unsigned(self, target: dict) -> bool:
        """The value with its sign ignored (PDF text layers often encode the minus as a control character)."""
        if target["form"] == "number":
            return abs(_decimal(normalise(target["s"]))) in self.abs_number
        return normalise(target["s"]).lstrip("-") in self.abs_text


def cells_of(replies: list[str]) -> tuple[list[str], bool]:
    """Cell texts of the replies; a reply with no table markup is split into lines (parsed=False)."""
    sys.path.insert(0, str(HERE))
    from run_reader import parse_cells

    cells, parsed = [], True
    for reply in replies:
        found = [c["text"] for c in parse_cells(reply)]
        if not found:
            parsed = False
            found = [line for line in re.sub(r"<[^>]+>", "\n", reply).splitlines() if line.strip()]
        cells.extend(found)
    return cells, parsed


def load_replies(path: Path) -> list[str]:
    data = json.loads(path.read_text())
    if isinstance(data, str):
        return [data]
    for key in ("replies", "reply", "text"):
        if key in data:
            return data[key] if isinstance(data[key], list) else [data[key]]
    raise ValueError(f"{path}: no replies / reply / text field")


def targets_of(table: dict) -> list[dict]:
    return [t for record in table["records"] for t in record["targets"]]


def score_table(table: dict, replies: list[str]) -> dict:
    cells, parsed = cells_of(replies)
    tr = Transcription(cells)
    out = {"values": 0, "hit": 0, "strict": 0, "parsed": parsed, "cells": len(cells), "by_source": {}}
    for t in targets_of(table):
        hit, strict = tr.has(t)
        out["values"] += 1
        out["hit"] += hit
        out["strict"] += strict
        b = out["by_source"].setdefault(t["source"], {"values": 0, "hit": 0, "strict": 0})
        b["values"] += 1
        b["hit"] += hit
        b["strict"] += strict
    return out


def _rates(rows: list[dict]) -> dict:
    n = sum(r["values"] for r in rows)
    return {"tables": len(rows), "values": n,
            "recall": sum(r["hit"] for r in rows) / max(1, n),
            "recall_strict": sum(r["strict"] for r in rows) / max(1, n),
            "recall_mean_per_table": sum(r["hit"] / r["values"] for r in rows) / max(1, len(rows)),
            "recall_strict_mean_per_table": sum(r["strict"] / r["values"] for r in rows) / max(1, len(rows)),
            "tables_all_values_found": sum(r["hit"] == r["values"] for r in rows),
            "tables_reply_not_a_table": sum(not r["parsed"] for r in rows)}


def score(replies_dir: Path, index: Path = REAL / "index.jsonl", split: str | None = None) -> dict:
    """Score every table of the index that has a reply file in `replies_dir`."""
    tables = [json.loads(line) for line in index.read_text().splitlines() if line.strip()]
    rows, missing = [], 0
    for table in tables:
        if split and table["split"] != split:
            continue
        path = replies_dir / f"{table['table_id']}.json"
        if not path.exists():
            missing += 1
            continue
        s = score_table(table, load_replies(path))
        s.update(table_id=table["table_id"], split=table["split"], crop_route=table["crop_route"], stratum=table["stratum"])
        rows.append(s)

    def group(key: str) -> dict:
        return {v: _rates([r for r in rows if r[key] == v]) for v in sorted({r[key] for r in rows})}

    sources: dict[str, dict] = {}
    for r in rows:
        for name, b in r["by_source"].items():
            agg = sources.setdefault(name, {"values": 0, "hit": 0, "strict": 0})
            for k in agg:
                agg[k] += b[k]
    return {"tables_scored": len(rows), "tables_without_reply": missing, "overall": _rates(rows),
            "by_split": group("split"), "by_crop_route": group("crop_route"), "by_stratum": group("stratum"),
            "by_label_field": {k: {"values": v["values"], "recall": v["hit"] / max(1, v["values"]), "recall_strict": v["strict"] / max(1, v["values"])} for k, v in sorted(sources.items())},
            "per_table": {r["table_id"]: {"split": r["split"], "crop_route": r["crop_route"], "values": r["values"], "recall": r["hit"] / r["values"], "recall_strict": r["strict"] / r["values"], "parsed": r["parsed"]} for r in rows}}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--replies", type=Path, required=True, help="folder of <table_id>.json reply files")
    parser.add_argument("--index", type=Path, default=REAL / "index.jsonl")
    parser.add_argument("--split", choices=("train", "test"), default=None)
    parser.add_argument("--out", type=Path, default=None, help="write the summary (numbers only) here")
    args = parser.parse_args()
    summary = score(args.replies, args.index, args.split)
    if args.out:
        args.out.write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({k: v for k, v in summary.items() if k != "per_table"}, indent=2))


if __name__ == "__main__":
    main()
