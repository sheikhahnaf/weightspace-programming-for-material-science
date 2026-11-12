"""E6 edit arm: can a language model write a weight edit that brings a small open
document model closer to a frontier reader on thermodynamic tables?

The edit is the smallest one the open model's output layer admits: a bias per
vocabulary entry, added to the logits (59,392 numbers, all zero as shipped). It is a
weight edit in the strict sense, applied through `Reader.set_bias`.

    env/ocr-venv/bin/python supplementary/e6_extraction_reader/edit_arm.py prompt --tag opus__rep1
    env/ocr-venv/bin/python supplementary/e6_extraction_reader/edit_arm.py export     # replies -> edits/<tag>.json (+ references)
    #   read with each edit:  sbatch hprc/reader.slurm <tag> edits/<tag>.json   (on FASTER)
    env/ocr-venv/bin/python supplementary/e6_extraction_reader/edit_arm.py score

Split: the first 10 documents (alphabetical) are shown to the model as errors; the other
10 are the test. The prompt lists, for the degraded scans of the 10 training documents,
every cell the open model got wrong (printed text, model text, and both token
sequences), how often each token appears in correct cells, and the task.

References given the same information:
  counts   bias +b on tokens over-represented in the printed text of wrong cells and -b on
           tokens over-represented in the model's text, b fixed at 2.0 (no forward passes)
  rule     no weight edit: a fixed text clean-up fitted on the training cells
           (the cheapest fix; what a weight edit has to beat)
"""

from __future__ import annotations

import argparse
import collections
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run_reader as rr  # noqa: E402

RENDERING = "degraded_raster"


def split():
    truths = sorted((rr.BENCH / "truth").glob("*.json"))
    docs = [json.loads(p.read_text())["doc_id"] for p in truths]
    return docs[:10], docs[10:]


def tokenizer():
    from transformers import AutoTokenizer
    return AutoTokenizer.from_pretrained(rr.MODEL, revision=rr.REVISION, cache_dir=rr.ROOT / "data" / "large" / "hf")


def cells(tag: str, docs: list[str]):
    """(printed text, model text or None, is numeric cell) for every truth cell of `docs`."""
    import score as S
    out = []
    folder = HERE / "results" / tag / RENDERING
    for doc in docs:
        truth = json.loads((rr.BENCH / "truth" / f"{doc}.json").read_text())
        for t in truth["tables"]:
            f = folder / f"{doc}__{t['id']}.json"
            pred = [{"cells": rr.parse_cells(r)} for r in json.loads(f.read_text())["replies"]] if f.exists() else []
            for tc in S._segments(t):
                best = S.align_segment(tc, pred) if pred else None
                for (r, c), cell in tc.items():
                    got = best[1].get((r + best[2], c + best[3])) if best else None
                    out.append((cell["text"], got, cell.get("value") is not None))
    return out


def build_prompt() -> str:
    train, _ = split()
    tok = tokenizer()
    rows = cells("unedited", train)
    wrong = [(t, g) for t, g, _ in rows if g is None or g.strip() != t.strip()]
    right = [t for t, g, _ in rows if g is not None and g.strip() == t.strip()]
    numeric = [(t, g) for t, g, n in rows if n]
    numeric_ok = sum(1 for t, g in numeric if g is not None and g.strip() == t.strip())
    ids = lambda s: tok.encode(s, add_special_tokens=False)
    show = lambda s: " ".join(f"{i}:{tok.decode([i])!r}" for i in ids(s))
    pairs = collections.Counter((t, g) for t, g in wrong if g is not None)
    missing = sum(1 for t, g in wrong if g is None)
    lines = [f"{n}x | printed {t!r} = [{show(t)}] | model {g!r} = [{show(g)}]" for (t, g), n in pairs.most_common(140)]
    in_right = collections.Counter(i for t in right for i in ids(t))
    involved = sorted({i for (t, g), _ in pairs.most_common(140) for i in ids(t) + ids(g)})
    usage = "\n".join(f"{i} | {tok.decode([i])!r} | {in_right[i]}" for i in involved)
    return f"""You are given the behaviour of a small open-weights document model (GLM-OCR, 0.9 billion weights) that reads tables from scanned pages of papers on alloy phase diagrams and writes them as HTML. You cannot run it and you cannot train it.

# The one thing you can edit
The model's last layer turns a hidden vector into one score (logit) per vocabulary entry; the highest score is written next. You may add a constant to the score of any vocabulary entries: a bias vector b with {tok.vocab_size:,} entries, all 0.0 now. logit[token] becomes logit[token] + b[token] at every position of every table. Nothing else can change. A bias cannot look at context: it raises or lowers a token everywhere.

# What the model gets wrong
On the tables of 10 scanned papers ({len(rows)} cells), the model's cell matches the printed cell exactly in {len(right)} cells ({100 * len(right) / len(rows):.1f}%). A frontier reader on the same crops matches in about 97%. Cells that hold a number are already right in {numeric_ok} of {len(numeric)} cases; those must stay right. {missing} wrong cells were missing altogether (a table-structure error that a bias cannot fix). The other wrong cells, most frequent first; each side is also shown as the model's tokens (id:'text'):
{chr(10).join(lines)}

# How often the tokens above occur in cells the model already reads correctly
token id | text | occurrences in correct cells
{usage}

# The task
Write the bias entries that make the model's cells match the printed text on NEW scanned papers of the same kind, without breaking cells that are right now, numbers above all. Say nothing about entries you leave at 0.

# Reply format
Reply with one JSON object and no other text: {{"<token id>": <bias value>, ...}}. Token ids are the integers shown above (you may use others if you are sure of them). Values are real numbers; typical logit gaps between the first and second choice are 1 to 10.
"""


def counts_edit(b: float = 2.0) -> dict:
    train, _ = split()
    tok = tokenizer()
    ids = lambda s: tok.encode(s, add_special_tokens=False)
    plus, minus = collections.Counter(), collections.Counter()
    for t, g, _ in cells("unedited", train):
        if g is None or g.strip() == t.strip():
            continue
        a, c = collections.Counter(ids(t)), collections.Counter(ids(g))
        plus.update(a - c)
        minus.update(c - a)
    edit = {}
    for i in set(plus) | set(minus):
        d = plus[i] - minus[i]
        if abs(d) >= 5:
            edit[str(i)] = b if d > 0 else -b
    return edit


def fit_rule():
    """Text clean-up fitted on training cells: character substitutions that fix more cells than they break."""
    train, _ = split()
    rows = [(t, g) for t, g, _ in cells("unedited", train) if g is not None]
    candidates = [("-", "–"), ("℃", "°C"), ("-1", "⁻¹"), ("v", "ν")]
    kept = []
    for a, b in candidates:
        fixed = sum(1 for t, g in rows if g.strip() != t.strip() and g.replace(a, b).strip() == t.strip())
        broken = sum(1 for t, g in rows if g.strip() == t.strip() and g.replace(a, b).strip() != t.strip())
        if fixed > broken:
            kept.append((a, b))
    return kept


def rate(rows) -> dict:
    n = len(rows)
    numeric = [(t, g) for t, g, k in rows if k]
    return {"cells": n, "cell_exact": sum(1 for t, g, _ in rows if g is not None and g.strip() == t.strip()) / n,
            "cell_exact_normalised": sum(1 for t, g, _ in rows if g is not None and re.sub(r"\s+", "", g) == re.sub(r"\s+", "", t)) / n,
            "numeric_exact": sum(1 for t, g in numeric if g is not None and g.strip() == t.strip()) / max(1, len(numeric))}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("prompt")
    p.add_argument("--tag", required=True)
    sub.add_parser("export")
    sub.add_parser("score")
    args = parser.parse_args()
    if args.command == "prompt":
        folder = HERE / "runs" / f"bias__{args.tag}"
        folder.mkdir(parents=True, exist_ok=True)
        text = build_prompt()
        (folder / "prompt.txt").write_text(text)
        (folder / "meta.json").write_text(json.dumps({"arm": "reader_logit_bias_edit", "tag": args.tag, "model_alias": args.tag.split("__")[0],
                                                      "forward_passes": 0, "prompt_chars": len(text)}, indent=2) + "\n")
        print(folder / "prompt.txt", len(text), "characters")
    elif args.command == "export":
        out = HERE / "edits"
        out.mkdir(exist_ok=True)
        (out / "counts.json").write_text(json.dumps(counts_edit(), indent=1) + "\n")
        vocab = tokenizer().vocab_size
        for folder in sorted((HERE / "runs").glob("bias__*")):
            if not (folder / "reply.txt").exists():
                continue
            try:
                raw = json.loads(re.search(r"\{.*\}", (folder / "reply.txt").read_text(), re.S).group(0))
                edit = {str(int(k)): float(v) for k, v in raw.items() if 0 <= int(k) < vocab and abs(float(v)) <= 50}
                (out / f"{folder.name.replace('bias__', '')}.json").write_text(json.dumps(edit, indent=1) + "\n")
                print(folder.name, len(edit), "entries")
            except Exception as error:
                print(folder.name, "INVALID", type(error).__name__, str(error)[:100])
    else:
        _, test = split()
        rule = fit_rule()
        table = {}
        for folder in sorted((HERE / "results").iterdir()):
            if not (folder / RENDERING).is_dir() or folder.name == "smoke":
                continue
            rows = cells(folder.name, test)
            if sum(1 for _, g, _ in rows if g is not None) == 0:
                continue
            table[folder.name] = rate(rows)
            if folder.name == "unedited":
                fixed = [(t, None if g is None else _apply(rule, g), k) for t, g, k in rows]
                table["unedited + text rule (no weight edit)"] = rate(fixed) | {"rule": rule}
        frontier = HERE / "results" / "frontier_reader.json"
        (HERE / "results" / "edit_arm.json").write_text(json.dumps(table, indent=2, ensure_ascii=False) + "\n")
        for k, v in table.items():
            print(f"{k:42} cells {v['cells']}  exact {v['cell_exact']:.3f}  ignoring spaces {v['cell_exact_normalised']:.3f}  numbers {v['numeric_exact']:.3f}")
        if frontier.exists():
            print("frontier reader (all 20 documents):", json.loads(frontier.read_text()))


def _apply(rule, text):
    for a, b in rule:
        text = text.replace(a, b)
    return text


if __name__ == "__main__":
    main()
