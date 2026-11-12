"""E6 real papers: a table-reading test set from the public ORCHID literature release.

Labels: orchid-literature.jsonl.gz (CC BY 4.0, data.orchid-project.org/literature/), the
values the ORCHID readers took from tables of CALPHAD assessment papers. Images: crops of
the publisher PDFs, re-rendered here with the pipeline's crop rule. The PDFs are read in
place and never written to; every image goes to data/large/orchid_real/ (git-ignored) and
nowhere else.

    env/ocr-venv/bin/python supplementary/e6_extraction_reader/build_real_set.py

Steps (deterministic, seed 0; rerunning skips crops that exist):
  1  keep table records that are extraction-accepted, multi-reader, with claude-opus-5.5
     among the readers and at least one printed numeric value (see `targets`); group them
     by paper + page + table label; keep tables with >= 4 such records and a local PDF.
  2  sample 400 tables, at most 3 per paper, stratified by record kind x property group;
     split the sampled papers in half: "train" (errors shown to the editing model), "test".
  3  crop: `locator.page` is the 1-based PDF page. Find the caption line ("Table <label>")
     in the page's text layer; crop the full page width from 6 pt above it to the next
     "Table / Fig." caption on the same side of the page, else the page bottom; 160 dpi.
     A caption set vertically means a landscape table: whole page, rotated upright.
     No caption found, or no text layer: whole page. The route is recorded per crop.
  4  write crops/<table_id>.png (+ .json), index.jsonl, and the tracked image-free
     manifest results/real_set_manifest.json.

For each crop the share of labelled values found in the PDF text layer of the cropped
region is recorded: a check of the page mapping and the crop. `text_layer_share` ignores
the sign, because many text layers encode the minus as a control character;
`text_layer_share_signed` uses the scoring rule unchanged.
"""

from __future__ import annotations

import argparse
import collections
import gzip
import hashlib
import json
import random
import re
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REAL = ROOT / "data" / "large" / "orchid_real"
PDFS = ROOT.parent / "PD-extraction" / "references" / "pdfs"  # read-only
RELEASE_URL = "https://data.orchid-project.org/literature/orchid-literature.jsonl.gz"
DPI = 160
SEED = 0
N_TABLES = 400
PER_PAPER = 3
MIN_RECORDS = 4
STRATUM_FLOOR = 15
READER = "claude-opus-5.5"

sys.path.insert(0, str(HERE))
import score_real as sr  # noqa: E402


# ---------------------------------------------------------------- labels

def release() -> list[dict]:
    path = REAL / "release" / "orchid-literature.jsonl.gz"
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(RELEASE_URL, path)
    with gzip.open(path, "rt") as f:
        return [json.loads(line) for line in f]


def targets(record: dict) -> list[dict]:
    """The printed numeric values of a record that a transcription can be checked against.

    `value_printed` is a JSON number in the release (printed formatting lost): form "number".
    `temperature_printed` is a string as printed: kept when it is a bare number, form "string".
    """
    out = []
    value = record.get("value_printed")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        out.append({"s": repr(value), "form": "number", "source": "value_printed"})
    temperature = record.get("temperature_printed")
    if isinstance(temperature, str) and sr.BARE_NUMBER.fullmatch(temperature.strip()):
        out.append({"s": temperature.strip(), "form": "string", "source": "temperature_printed"})
    return out


def accepted(record: dict) -> bool:
    return (record["locator"].get("artifact") == "table"
            and record.get("flags", {}).get("extraction_accepted") is True
            and READER in (record.get("readers") or [])
            and record.get("reader_agreement") == "multi_reader")


def doi_key(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", text.lower())


def pdf_hashes() -> dict[str, str]:
    """sha256 of every local PDF (cached); the release's `asset` ids carry a 16-hex prefix of it."""
    cache = REAL / "pdf_sha256.json"
    known = json.loads(cache.read_text()) if cache.exists() else {}
    names = sorted(p.name for p in PDFS.glob("*.pdf") if not p.name.startswith("."))
    for name in names:
        if name not in known:
            known[name] = hashlib.sha256((PDFS / name).read_bytes()).hexdigest()
    cache.write_text(json.dumps(known, indent=0) + "\n")
    return {name: known[name] for name in names}


def group_tables(records: list[dict]) -> tuple[list[dict], dict]:
    hashes = pdf_hashes()
    by_doi: dict[str, list[str]] = collections.defaultdict(list)
    by_hash: dict[str, str] = {}
    for name, digest in hashes.items():
        by_doi[doi_key(name.split("_", 1)[1][:-4])].append(name)
        by_hash.setdefault(digest[:16], name)

    groups: dict[tuple, list[dict]] = collections.defaultdict(list)
    counts = collections.Counter(records=len(records))
    for r in records:
        if r["locator"].get("artifact") != "table":
            continue
        counts["table_records"] += 1
        if not accepted(r):
            continue
        counts["accepted_multi_reader_opus"] += 1
        if not targets(r):
            continue
        counts["with_printed_number"] += 1
        groups[(r["paper"], r["locator"]["page"], str(r["locator"]["label"]))].append(r)
    counts["tables_any"] = len(groups)

    tables = []
    for (paper, page, label), rows in sorted(groups.items()):
        if len(rows) < MIN_RECORDS:
            continue
        counts["tables_min_records"] += 1
        asset = rows[0]["locator"].get("asset", "")
        prefix = asset.split(":")[1].split("/")[0] if asset.startswith("sha256:") else None
        candidates = by_doi.get(doi_key(paper[4:]), []) if paper.startswith("doi:") else []
        pdf, how = None, None
        if prefix and by_hash.get(prefix) and (not candidates or by_hash[prefix] in candidates):
            pdf, how = by_hash[prefix], "doi+sha256" if candidates else "sha256"
        elif candidates:
            pdf, how = candidates[0], "doi"
        if pdf is None:
            counts["tables_no_local_pdf"] += 1
            continue
        kinds = collections.Counter((r.get("record_kind"), r.get("property_group")) for r in rows)
        kind = sorted(kinds.items(), key=lambda kv: (-kv[1], str(kv[0])))[0][0]
        slug = re.sub(r"[^A-Za-z0-9]+", "-", label).strip("-") or "x"
        tables.append({
            "table_id": f"{pdf.split('_', 1)[0]}_p{page:03d}_t{slug}",
            "paper": paper, "doi": paper[4:] if paper.startswith("doi:") else None,
            "pdf": pdf, "pdf_match": how, "page": page, "label": label,
            "stratum": f"{kind[0]} / {kind[1]}",
            "caption": rows[0]["locator"].get("caption"),
            "records": [{"id": r["id"], "row": r["locator"].get("row"), "quantity": r.get("property"),
                         "quantity_printed": r.get("property_printed"),
                         "value_printed": r.get("value_printed"), "unit_printed": r.get("unit_printed"),
                         "temperature_printed": r.get("temperature_printed"), "targets": targets(r)}
                        for r in sorted(rows, key=lambda r: (r["locator"].get("row") is None, r["locator"].get("row") or 0, r["id"]))],
        })
    seen = collections.Counter(t["table_id"] for t in tables)
    assert max(seen.values()) == 1, [k for k, v in seen.items() if v > 1][:5]
    counts["tables_qualifying"] = len(tables)
    counts["papers_qualifying"] = len({t["paper"] for t in tables})
    return tables, dict(counts)


# ---------------------------------------------------------------- sample and split

def sample(tables: list[dict]) -> list[dict]:
    rng = random.Random(SEED)
    order = sorted(tables, key=lambda t: t["table_id"])
    rng.shuffle(order)
    sizes = collections.Counter(t["stratum"] for t in order)
    # proportional quotas with a floor for the small strata, trimmed to N_TABLES
    quota = {s: max(min(n, STRATUM_FLOOR), round(N_TABLES * n / len(order))) for s, n in sizes.items()}
    while sum(quota.values()) > N_TABLES:
        quota[max(quota, key=lambda s: (quota[s], s))] -= 1
    chosen, per_paper, per_stratum = [], collections.Counter(), collections.Counter()
    for strict in (True, False):  # second pass fills what the paper cap left open
        for t in order:
            if len(chosen) == N_TABLES:
                break
            if t in chosen or per_paper[t["paper"]] >= PER_PAPER:
                continue
            if strict and per_stratum[t["stratum"]] >= quota[t["stratum"]]:
                continue
            chosen.append(t)
            per_paper[t["paper"]] += 1
            per_stratum[t["stratum"]] += 1
    papers = sorted({t["paper"] for t in chosen})
    rng.shuffle(papers)
    train = set(papers[: len(papers) // 2])
    for t in chosen:
        t["split"] = "train" if t["paper"] in train else "test"
    return sorted(chosen, key=lambda t: t["table_id"])


# ---------------------------------------------------------------- crops

_CAPTION = re.compile(r"^\s*(?:table|tab\.|fig\.?|figure|scheme)\s*\.?\s*[A-Za-z]?\.?\d|^\s*(?:table|tab\.)\s+[IVXLl]+\b", re.I)
_IN_TEXT = re.compile(r"^\s*(?:shows?|lists?|gives?|presents?|summari[sz]es?|compares?|contains?|reports?|and|is|are|was|were|in|of|the|that|with|for|as|also|has|have|can|it)\b", re.I)


def _lines(page) -> list[dict]:
    out = []
    for block in page.get_text("dict")["blocks"]:
        first = True
        for line in block.get("lines", []):
            text = "".join(span["text"] for span in line["spans"])
            if not text.strip():
                continue
            last = out[-1] if out and not first else None
            x0, y0, x1, y1 = line["bbox"]
            if (last and abs(line["dir"][0]) > 0.5 and abs(last["dir"][0]) > 0.5 and x0 >= last["bbox"][2] - 1
                    and abs((y0 + y1) / 2 - (last["bbox"][1] + last["bbox"][3]) / 2) < 0.4 * (y1 - y0)):
                # some PDFs give one "line" per word: join the pieces that share a baseline
                lx0, ly0, lx1, ly1 = last["bbox"]
                last["text"] += ("" if last["text"].endswith(" ") or text.startswith(" ") else " ") + text
                last["bbox"] = (lx0, min(ly0, y0), x1, max(ly1, y1))
                continue
            out.append({"text": text, "bbox": line["bbox"], "dir": line["dir"], "first": first})
            first = False
    return out


def _caption_pattern(label: str):
    variants = {label}
    if label == "l":  # a lower-case L in the release is a misread 1 or I
        variants |= {"1", "I"}
    alt = "|".join(re.escape(v) for v in sorted(variants))
    return re.compile(rf"^\s*(?:table|tab\.)\s*\.?\s*(?:{alt})(?![\w])(?!\.\d)(.*)$", re.I)


def _caption_rank(line: dict, rest: str) -> int:
    """0 a block that opens with the bare label, 1 with label + text, 2 with a sentence; 3 a line inside a paragraph."""
    rest = rest.lstrip(" .:-–—")
    if not line["first"]:
        return 3
    if not rest.strip():
        return 0
    return 2 if _IN_TEXT.match(rest) and not rest[:1].isupper() else 1


def find_caption(lines: list[dict], label: str) -> dict | None:
    """The caption line of the table: the best-ranked "Table <label>" line, first in reading order."""
    pattern = _caption_pattern(label)
    hits = []
    for line in lines:
        m = pattern.match(line["text"])
        if m:
            hits.append((_caption_rank(line, m.group(1)), line))
    if not hits:
        return None
    hits.sort(key=lambda h: h[0])  # stable: reading order within a rank
    return hits[0][1]


def crop_table(doc, table: dict):
    """(PIL image, meta) for one table by the pipeline rule."""
    import fitz
    from PIL import Image

    index = table["page"] - 1  # locator.page is the 1-based PDF page
    meta = {"page_index": index, "dpi": DPI}
    if not 0 <= index < len(doc):
        return None, {**meta, "crop_route": "page_out_of_range"}
    page = doc[index]
    rect = page.rect
    lines = _lines(page)
    has_text = sum(len(line["text"].strip()) for line in lines) >= 200
    caption = find_caption(lines, table["label"]) if has_text else None
    clip, rotate = rect, 0
    if not has_text:
        route = "whole_page_no_text_layer"
    elif caption is None:
        route = "whole_page_caption_not_found"
    elif abs(caption["dir"][0]) < 0.5:
        route = "landscape_whole_page"
        rotate = 270 if caption["dir"][1] < 0 else 90  # PIL rotates counter-clockwise; text running up the page turns clockwise
    else:
        route = "caption_crop"
        x0, y0, x1, y1 = caption["bbox"]
        mid = (rect.x0 + rect.x1) / 2
        side = "left" if x1 < mid + 10 else ("right" if x0 > mid - 10 else "full")
        bottom = rect.y1
        for line in lines:
            lx0, ly0, lx1, _ = line["bbox"]
            if ly0 <= y1 + 2 or abs(line["dir"][0]) < 0.5 or not _CAPTION.match(line["text"]):
                continue
            rest = re.sub(r"^\s*[A-Za-z]+\.?\s*[\w.]*\w", "", line["text"])
            if _caption_rank(line, rest) > 1:
                continue  # "Fig. 3 shows ...", or a mention inside a paragraph: not a caption
            same_side = side == "full" or (lx0 < mid if side == "left" else lx1 > mid)
            if same_side and ly0 < bottom:
                bottom = ly0 - 2
        top = max(rect.y0, y0 - 6)
        if bottom - top < 40:  # a caption below its table, or two captions stacked: do not trust the rule
            route, bottom, top = "whole_page_crop_too_short", rect.y1, rect.y0
        clip = fitz.Rect(rect.x0, top, rect.x1, bottom)
    pix = page.get_pixmap(dpi=DPI, clip=clip, colorspace=fitz.csRGB, alpha=False)
    image = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    if rotate:
        image = image.rotate(rotate, expand=True)
    wanted = sr.targets_of(table)
    region = sr.Transcription(page.get_text(clip=clip).splitlines())
    found = sum(region.has_unsigned(t) for t in wanted)
    signed = sum(region.has(t)[0] for t in wanted)
    meta.update(crop_route=route, clip_pt=[round(v, 1) for v in clip], rotate=rotate, size_px=list(image.size),
                page_text_chars=sum(len(line["text"].strip()) for line in lines),
                values=len(wanted), values_in_text_layer=found, text_layer_share=found / max(1, len(wanted)),
                values_in_text_layer_signed=signed, text_layer_share_signed=signed / max(1, len(wanted)))
    return image, meta


def page_offset_check(tables: list[dict], n: int = 40) -> dict:
    """Which PDF page holds the labelled values: index page-2, page-1, page or page+1?"""
    import fitz

    rng = random.Random(SEED + 1)
    best = collections.Counter()
    for t in rng.sample(tables, min(n, len(tables))):
        with fitz.open(PDFS / t["pdf"]) as doc:
            share = {}
            for offset in (-2, -1, 0, 1):
                i = t["page"] + offset
                if 0 <= i < len(doc):
                    region = sr.Transcription(doc[i].get_text().splitlines())
                    wanted = sr.targets_of(t)
                    share[offset] = sum(region.has_unsigned(x) for x in wanted) / len(wanted)
        top = max(share.values())
        if top < 0.5:
            best["no page has half the values (scan or wrong PDF)"] += 1
        else:
            best["index = page%+d" % min((o for o, s in share.items() if s == top), key=lambda o: abs(o + 1))] += 1
    return dict(best)


# ---------------------------------------------------------------- main

def main() -> None:
    import fitz

    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--no-crops", action="store_true", help="stop after sampling (no PDF is opened)")
    parser.add_argument("--redo", action="store_true", help="render every crop again (after a change of the crop rule)")
    args = parser.parse_args()

    tables, counts = group_tables(release())
    print(counts, flush=True)
    chosen = sample(tables)
    strata_all = collections.Counter(t["stratum"] for t in tables)
    print("sampled", len(chosen), "tables from", len({t["paper"] for t in chosen}), "papers", flush=True)
    if args.no_crops:
        return
    offsets = page_offset_check(chosen)
    print("page offset check:", offsets, flush=True)

    crops = REAL / "crops"
    crops.mkdir(parents=True, exist_ok=True)
    done = []
    for i, t in enumerate(chosen):
        png, side = crops / f"{t['table_id']}.png", crops / f"{t['table_id']}.json"
        if png.exists() and side.exists() and not args.redo:
            meta = json.loads(side.read_text())
        else:
            with fitz.open(PDFS / t["pdf"]) as doc:
                image, meta = crop_table(doc, t)
            if image is None:
                print("skipped", t["table_id"], meta["crop_route"], flush=True)
                continue
            image.save(png)
            side.write_text(json.dumps(meta) + "\n")
        done.append({**{k: t[k] for k in ("table_id", "doi", "paper", "pdf", "pdf_match", "page", "label", "split", "stratum")},
                     "crop": f"crops/{t['table_id']}.png", **meta, "caption": t["caption"], "records": t["records"]})
        if (i + 1) % 50 == 0:
            print(i + 1, "crops", flush=True)
    (REAL / "index.jsonl").write_text("".join(json.dumps(d, ensure_ascii=False) + "\n" for d in done))

    def by(key, rows=done):
        return dict(sorted(collections.Counter(r[key] for r in rows).items()))

    def share(rows, key="values_in_text_layer"):
        return sum(r[key] for r in rows) / max(1, sum(r["values"] for r in rows))

    with_text = [r for r in done if r["crop_route"] != "whole_page_no_text_layer"]
    manifest = {
        "source": {"labels": RELEASE_URL, "licence": "CC BY 4.0", "release_sha256": hashlib.sha256((REAL / "release" / "orchid-literature.jsonl.gz").read_bytes()).hexdigest(),
                   "pdfs": "PD-extraction/references/pdfs (publisher PDFs, not redistributed; crops stay in data/large/orchid_real/)"},
        "rule": {"record": f"table record, extraction_accepted, reader_agreement multi_reader, {READER} in readers, a printed numeric value",
                 "table": f"paper + page + label, >= {MIN_RECORDS} such records, local PDF found",
                 "sample": f"{N_TABLES} tables, <= {PER_PAPER} per paper, stratified by record_kind / property_group (floor {STRATUM_FLOOR}), seed {SEED}",
                 "split": "sampled papers shuffled and halved: train / test",
                 "page": "locator.page is the 1-based PDF page (PyMuPDF index = page - 1)", "dpi": DPI},
        "filter_counts": counts,
        "qualifying_tables_by_stratum": dict(sorted(strata_all.items())),
        "page_offset_check": offsets,
        "tables": len(done), "papers": len({r["paper"] for r in done}),
        "labelled_records": sum(len(r["records"]) for r in done), "labelled_values": sum(r["values"] for r in done),
        "labelled_values_by_field": dict(sorted(collections.Counter(x["source"] for r in done for x in sr.targets_of(r)).items())),
        "split_tables": by("split"), "split_papers": {s: len({r["paper"] for r in done if r["split"] == s}) for s in ("train", "test")},
        "split_values": {s: sum(r["values"] for r in done if r["split"] == s) for s in ("train", "test")},
        "crop_route": by("crop_route"), "stratum": by("stratum"), "pdf_match": by("pdf_match"),
        "text_layer_share": {"all": share(done), "crops_with_text_layer": share(with_text), "all_signed": share(done, "values_in_text_layer_signed"),
                             "by_crop_route": {k: share([r for r in done if r["crop_route"] == k]) for k in by("crop_route")},
                             "tables_below_0.5": sum(r["text_layer_share"] < 0.5 for r in done),
                             "note": "share of labelled values present as a number token in the PDF text layer of the cropped region, sign ignored; all_signed applies the scoring rule unchanged (many text layers encode the minus as a control character)"},
        "table_ids": [{"table_id": r["table_id"], "doi": r["doi"], "page": r["page"], "label": r["label"], "split": r["split"],
                       "stratum": r["stratum"], "crop_route": r["crop_route"], "records": len(r["records"]), "values": r["values"],
                       "text_layer_share": round(r["text_layer_share"], 3)} for r in done],
    }
    out = HERE / "results" / "real_set_manifest.json"
    out.write_text(json.dumps(manifest, indent=1) + "\n")
    print(json.dumps({k: v for k, v in manifest.items() if k not in ("table_ids", "source", "rule")}, indent=1))


if __name__ == "__main__":
    main()
