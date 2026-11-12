"""Write a clean copy of the repository for a public release. It publishes nothing.

    python scripts/make_release.py --out release_build
    python scripts/make_release.py --out release_build --without-thermocalc

The copy has no git history (a release must start from a fresh history: this repository's
history holds files that are left out here). The script only copies and rewrites text; it
never deletes, never runs git, and refuses to write into a folder that already has files.

Left out always:
  working notes (PROGRESS.md, questions.md, CLAUDE.md, research/), slides/, site/,
  the page crops of the table-reader experiment (images of third-party benchmark pages).

Left out with --without-thermocalc (values computed with Thermo-Calc and its databases):
  data/calphad/, every per-cell result of experiments/e7_calphad_prior/results/ (the
  summaries and the overview stay), and the sub-system facts inside the prompts of the
  `writepd__*` runs (the rest of each prompt stays, with a marker where the facts were).

Rewritten in every text file: the absolute paths of the machine the work was done on.
After copying, the script searches the copy for anything that still looks machine- or
person-specific and lists what it finds in RELEASE_MANIFEST.md, with the items that need
a decision by the authors (licence, third-party data).
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ALWAYS_OUT = ("PROGRESS.md", "questions.md", "CLAUDE.md", "research/", "slides/", "site/", ".superpowers/")
CROPS = re.compile(r"supplementary/e6_extraction_reader/.*\.(png|jpg|jpeg)$")
TC_DATA = "data/calphad/"
TC_RESULTS = "experiments/e7_calphad_prior/results/"
TC_RESULTS_KEEP = re.compile(r"(overview\.md|summary[^/]*\.(md|json)|baseline_table\.md)$")
TC_FACTS_PROMPT = re.compile(r"experiments/e7_calphad_prior/runs/writepd__[^/]+/prompt\.txt$")
FACTS_BLOCK = re.compile(r"(\n# Phase-diagram facts[^\n]*\n)(.*?)(\n# Architecture\n)", re.S)

REWRITE = [
    (re.compile(r"/Volumes/SSD1_SMAAA/weighspace-programming"), "<REPO>"),
    (re.compile(r"/Volumes/SSD1_SMAAA/weightspace-programming-for-material-science-paper"), "<PAPER_REPO>"),
    (re.compile(r"/Volumes/SSD1_SMAAA"), "<WORKSPACE>"),
    (re.compile(r"/private/tmp/claude-\d+/[^\s\"']*"), "<TMP>"),
    (re.compile(r"/Users/[A-Za-z0-9_.-]+"), "<HOME>"),
    (re.compile(r"^-e git\+ssh://[^\n]*\n", re.M), "# (a private editable install was listed here)\n"),
]
LEFTOVER = {
    "absolute path": re.compile(r"/Volumes/|/Users/|/scratch/(user|group)/"),
    "cluster account or user name": re.compile(r"142705330300|ahnafalvi|arroyave_lab"),
    "email address": re.compile(r"[A-Za-z0-9_.+-]+@[A-Za-z0-9-]+\.(edu|com|org)\b"),
    "token-like string": re.compile(r"\b(sk-[A-Za-z0-9]{20,}|hf_[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{20,})\b|API_KEY\s*=\s*['\"][^'\"]+['\"]"),
}
THIRD_PARTY = [
    ("vendor/", "algorithms copied unmodified from the authors' other repositories; each keeps its own licence"),
    ("data/alloys/", "experimental alloy sets from the literature (see data/PROVENANCE.md)"),
    ("data/closed_loop_bm/, data/closed_loop_cp/, data/causal_replay/, data/dft_validation/", "from the authors' closed-loop study"),
    ("data/mlip_reference/, data/formation/", "structures and DFT values from the Materials Project"),
    ("data/bnn/, data/surrogate_zoo/, data/phonon/, data/synthesizability/", "see data/PROVENANCE.md"),
]


def is_text(data: bytes) -> bool:
    if b"\0" in data[:4096]:
        return False
    try:
        data.decode("utf-8")
        return True
    except UnicodeDecodeError:
        return False


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--without-thermocalc", action="store_true")
    args = parser.parse_args()
    out = args.out if args.out.is_absolute() else ROOT / args.out
    if out.exists() and any(out.iterdir()):
        raise SystemExit(f"{out} already has files; choose an empty or new folder (this script never deletes)")
    out.mkdir(parents=True, exist_ok=True)

    tracked = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.split("\n")
    left_out: dict[str, int] = {}
    redacted, rewritten, copied = 0, 0, 0

    def skip(reason: str) -> None:
        left_out[reason] = left_out.get(reason, 0) + 1

    for name in filter(None, tracked):
        source = ROOT / name
        if not source.is_file():
            continue
        if name.startswith(ALWAYS_OUT):
            skip("working notes, slides, site")
            continue
        if CROPS.search(name):
            skip("page crops of the table-reader experiment")
            continue
        if args.without_thermocalc:
            if name.startswith(TC_DATA):
                skip("Thermo-Calc tables (data/calphad/)")
                continue
            if name.startswith(TC_RESULTS) and not TC_RESULTS_KEEP.search(name):
                skip("Thermo-Calc per-cell results")
                continue
        target = out / name
        target.parent.mkdir(parents=True, exist_ok=True)
        data = source.read_bytes()
        if len(data) < 5_000_000 and is_text(data):
            text = data.decode("utf-8")
            new = text
            for pattern, replacement in REWRITE:
                new = pattern.sub(replacement, new)
            if args.without_thermocalc and TC_FACTS_PROMPT.search(name):
                new, n = FACTS_BLOCK.subn(r"\1[The sub-system values computed with Thermo-Calc are not redistributed. "
                                          r"They can be regenerated with experiments/e7_calphad_prior/make_tc_data.py "
                                          r"and make_prompts.py by a holder of a Thermo-Calc licence.]\3", new)
                redacted += n
            rewritten += new != text
            target.write_text(new)
        else:
            shutil.copy2(source, target)
        copied += 1

    findings: dict[str, list[str]] = {k: [] for k in LEFTOVER}
    for path in sorted(out.rglob("*")):
        if not path.is_file() or path.stat().st_size > 5_000_000:
            continue
        data = path.read_bytes()
        if not is_text(data):
            continue
        text = data.decode("utf-8")
        for label, pattern in LEFTOVER.items():
            if pattern.search(text):
                findings[label].append(str(path.relative_to(out)))

    lines = ["# Release manifest", "",
             "Written by `scripts/make_release.py`. Nothing has been published; this folder has no git history.", "",
             f"- Files copied: {copied}; text files with machine paths rewritten: {rewritten}.",
             f"- Thermo-Calc data: {'left out' if args.without_thermocalc else 'INCLUDED (data/calphad/ and the facts in the writepd prompts)'}."
             + (f" Facts blocks replaced in {redacted} prompts." if args.without_thermocalc else ""), "",
             "## Left out", ""]
    lines += [f"- {reason}: {count} files" for reason, count in sorted(left_out.items())] or ["- nothing"]
    lines += ["", "## Still in the copy and worth a look", ""]
    for label, files in findings.items():
        lines.append(f"- {label}: {len(files)} files" + ("" if not files else "; first: " + ", ".join(f"`{f}`" for f in files[:8])))
    lines += ["", "## Decisions the authors have to make before publishing", "",
              "- LICENSE is MIT and covers the code in src/, scripts/, experiments/ and supplementary/. Say whether the run records (prompts, replies, scores) are under the same licence; third-party data and `vendor/` are not.",
              "- Thermo-Calc: check the licence agreement on redistributing computed values"
              + (" (this copy leaves them out; the self-reports of `writepd__*` runs are the models' own words and may quote a value)."
                 if args.without_thermocalc else " before publishing this copy, which includes them."),
              "- Third-party material that keeps its own licence:"]
    lines += [f"  - `{path}`: {what}" for path, what in THIRD_PARTY]
    lines += ["- Fine-tuned generator checkpoints are not in the repository; say where they are hosted.", ""]
    (out / "RELEASE_MANIFEST.md").write_text("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
