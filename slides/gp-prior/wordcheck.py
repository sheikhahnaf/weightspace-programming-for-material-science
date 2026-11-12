"""Word check on all slide text and speaker notes.

Scans every slides/*.html: the visible text (tags stripped) and the NOTES
comment. Flags the prose-contract banned words and constructions, the deck-
specific bans, em-dashes, and reports the notes word count per slide.
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SLIDES = HERE / "slides"
import json as _json
CFG = _json.loads((HERE / "deck.json").read_text())

BANNED_WORDS = [
    # prose contract: self-praise and LLM tics
    "leverage", "leverages", "leveraging", "delve", "delves", "robust", "robustly", "robustness",
    "seamless", "seamlessly", "cutting-edge", "paradigm", "novel", "comprehensive",
    "state-of-the-art", "transformative", "groundbreaking", "unprecedented", "holistic",
    "powerful", "showcase", "showcases", "underscore", "underscores", "tapestry",
    "navigate", "navigating", "landscape", "significantly", "notably", "interestingly",
    "crucially", "overall",
    # deck-specific additions come from deck.json "extra_banned_words"
]
BANNED_PHRASES = [
    "it is important to note", "it is worth noting", "in summary", "headline finding",
    "key insight", "not only", "serves as", "plays a crucial role", "a testament to",
    "in the realm of", "at the intersection of", "paves the way", "opens exciting avenues",
    "clearly demonstrates", "was able to", "successfully",
]


def visible_text(html: str) -> str:
    body = re.sub(r"<!--NOTES[\s\S]*?-->", " ", html)
    body = re.sub(r"<style[\s\S]*?</style>", " ", body)
    body = re.sub(r"<script[\s\S]*?</script>", " ", body)
    body = re.sub(r"<[^>]+>", " ", body)
    body = body.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    return re.sub(r"\s+", " ", body).strip()


def notes_text(html: str) -> str:
    m = re.search(r"<!--NOTES([\s\S]*?)-->", html)
    return re.sub(r"\s+", " ", m.group(1)).strip() if m else ""


# Proper names that must appear verbatim (the acknowledgments page names this funder).
ALLOWED_PHRASES = CFG.get("allowed_phrases", [])
BANNED_WORDS += CFG.get("extra_banned_words", [])
LO, HI = CFG.get("notes_words", [60, 120])


def check(text: str, where: str, name: str, problems: list):
    for a in ALLOWED_PHRASES:
        text = text.replace(a, " ")
    for w in BANNED_WORDS:
        flags = 0 if w.isupper() or w[:1].isupper() else re.IGNORECASE
        for m in re.finditer(r"(?<![\w-])" + re.escape(w) + r"(?![\w-])", text, flags):
            ctx = text[max(0, m.start() - 30): m.end() + 30]
            problems.append(f"{name} [{where}] banned word '{w}': ...{ctx}...")
    low = text.lower()
    for p in BANNED_PHRASES:
        i = low.find(p)
        if i >= 0:
            problems.append(f"{name} [{where}] banned phrase '{p}': ...{text[max(0, i-30): i+len(p)+30]}...")
    if "—" in text:
        problems.append(f"{name} [{where}] contains an em-dash")


def main():
    problems = []
    counts = []
    files = sorted(SLIDES.glob("*.html"))
    for f in files:
        html = f.read_text(encoding="utf-8")
        vis = visible_text(html)
        notes = notes_text(html)
        check(vis, "slide", f.name, problems)
        check(notes, "notes", f.name, problems)
        n = len(notes.split())
        counts.append((f.name, n))
        if not notes:
            problems.append(f"{f.name}: no speaker notes")
        elif n < LO or n > HI:
            problems.append(f"{f.name}: notes have {n} words (want {LO} to {HI})")
    print(f"checked {len(files)} slides")
    for name, n in counts:
        print(f"  {name}: {n} words of notes")
    if problems:
        print("\nPROBLEMS:")
        for p in problems:
            print("  " + p)
        sys.exit(1)
    print(f"\nno banned words, no em-dashes, all notes within {LO} to {HI} words")


if __name__ == "__main__":
    main()
