"""Copy the datasets and algorithms this campaign uses out of the sibling repos.

The sibling repos are only read. Every copied file is listed in
data/PROVENANCE.md with its source path, size and SHA-256, so a later reader
can tell whether a copy has drifted from its source.

    python scripts/copy_from_siblings.py            # copy and write provenance
    python scripts/copy_from_siblings.py --check    # compare copies with sources
"""

from __future__ import annotations

import argparse
import glob
import hashlib
import re
import shutil
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SIBLINGS = ROOT.parent
MG = "matgen-BO"
AR = "autoresearch-bo"
LOOP = f"{MG}/02_closed_loop_bo"
REPLAY = f"{LOOP}/validation/three_way_comparison/results"
HCAP = f"{MG}/archive/matinvent-hcap-bo/data"
BENCH = f"{AR}/bo-zoo/tests/benchmarks"
ZOO = f"{AR}/bo-zoo/src/bo_zoo/surrogates"
ANALYSIS = f"{AR}/autoresearch-bo/analysis"

# (source glob relative to the siblings' parent, destination folder relative to this repo)
MANIFEST: list[tuple[str, str]] = [
    # Closed-loop surrogate memories: ORB PCA-50 embeddings with oracle labels.
    (f"{LOOP}/data/hcap_data/bm/*.parquet", "data/closed_loop_bm"),
    (f"{HCAP}/ltm_seed_pool_v3.parquet", "data/closed_loop_cp"),
    (f"{HCAP}/ltm_hcap_p3v4_*.parquet", "data/closed_loop_cp"),
    # Causal replay of the published GP, and the DFT check of the MLIP oracle.
    (f"{REPLAY}/gp_causal_allpreds_bm_seeded.csv", "data/causal_replay"),
    (f"{REPLAY}/gp_causal_allpreds_cp_seeded.csv", "data/causal_replay"),
    (f"{REPLAY}/esen_vs_dft_bm.csv", "data/causal_replay"),
    (f"{LOOP}/validation/dft_validation/structures/*.cif", "data/dft_validation/structures"),
    (f"{LOOP}/validation/dft_validation/results/ehull_summary_corrected.csv", "data/dft_validation"),
    # Composition datasets behind the bo-zoo materials benchmarks.
    (f"{BENCH}/_datasets/*", "data/alloys"),
    # Fitted-surrogate zoo.
    (f"{ANALYSIS}/df_hyperparams.parquet", "data/surrogate_zoo"),
    (f"{ANALYSIS}/df_run.parquet", "data/surrogate_zoo"),
    (f"{ANALYSIS}/df_iter.parquet", "data/large/surrogate_zoo"),
    # Phonon thermodynamics (structures and DFPT targets; pickled with numpy 2).
    (f"{MG}/01_static_benchmark/data/dfpt_phonon_thermo.pkl", "data/phonon"),
    # Synthesizability scores of the generated winners.
    (f"{MG}/03_synthesizability/results/generated_scores/scores.csv", "data/synthesizability"),
    # Algorithms, vendored unmodified.
    (f"{MG}/LICENSE", "vendor/matgen_bo"),
    (f"{MG}/01_static_benchmark/src/*.py", "vendor/matgen_bo/static_benchmark"),
    (f"{LOOP}/src/surrogate.py", "vendor/matgen_bo/closed_loop"),
    (f"{LOOP}/src/featurizer.py", "vendor/matgen_bo/closed_loop"),
    (f"{REPLAY}/../drivers/three_way_causal_seeded.py", "vendor/matgen_bo/closed_loop"),
    (f"{ZOO}/*.py", "vendor/bo_zoo/surrogates"),
    (f"{BENCH}/_dataset_surrogate.py", "vendor/bo_zoo/benchmarks"),
    (f"{BENCH}/benchmark_mpea_strength.py", "vendor/bo_zoo/benchmarks"),
    (f"{BENCH}/benchmark_ti_alloy_3obj.py", "vendor/bo_zoo/benchmarks"),
    (f"{BENCH}/benchmark_perovskite_pv.py", "vendor/bo_zoo/benchmarks"),
    (f"{BENCH}/benchmark_matbench_bulk_shear.py", "vendor/bo_zoo/benchmarks"),
]


_TOKEN = re.compile(rb'"hf_[A-Za-z0-9]{20,}"')
_TOKEN_FROM_ENV = b'__import__("os").environ.get("HF_TOKEN", "")'


def clean(path: Path) -> tuple[bytes, bool]:
    """The file's bytes with any hard-coded Hugging Face token replaced by an
    environment lookup. A secret is never copied into this repo."""
    raw = path.read_bytes()
    cleaned = _TOKEN.sub(_TOKEN_FROM_ENV, raw) if path.suffix == ".py" else raw
    return cleaned, cleaned != raw


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def pairs() -> list[tuple[Path, Path]]:
    found = []
    for pattern, destination in MANIFEST:
        sources = sorted(Path(p) for p in glob.glob(str(SIBLINGS / pattern)))
        sources = [s for s in sources if s.is_file() and s.name != ".DS_Store"]
        if not sources:
            raise SystemExit(f"nothing matches {pattern}")
        found += [(s.resolve(), ROOT / destination / s.name) for s in sources]
    return found


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--check", action="store_true", help="report drift, copy nothing")
    args = parser.parse_args()

    rows, drift = [], 0
    for source, target in pairs():
        if ROOT in source.parents:
            raise SystemExit(f"refusing to treat {source} as a sibling source")
        content, redacted = clean(source)
        if args.check:
            same = target.exists() and target.read_bytes() == content
            drift += not same
            if not same:
                print(f"DRIFT {target.relative_to(ROOT)}")
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        if redacted:
            target.write_bytes(content)
        else:
            shutil.copy2(source, target)
        note = " (token replaced by `HF_TOKEN` lookup)" if redacted else ""
        rows.append(
            f"| `{target.relative_to(ROOT)}`{note} | `{source.relative_to(SIBLINGS)}` "
            f"| {len(content):,} | `{sha256(content)[:16]}` |"
        )
    if args.check:
        print("no drift" if not drift else f"{drift} file(s) differ from their source")
        raise SystemExit(1 if drift else 0)

    header = [
        "# Provenance of copied files",
        "",
        f"Copied on {date.today().isoformat()} by `scripts/copy_from_siblings.py` from the sibling repos under",
        f"`{SIBLINGS}`. The sources were read, never written. Files under `vendor/` are unmodified,",
        "except where a row says a hard-coded token was replaced; any change to an algorithm is made in",
        "`src/wsp/`, not there. `data/large/` is not tracked in git.",
        "",
        "| Copy | Source | Bytes | SHA-256 (first 16) |",
        "|---|---|---|---|",
    ]
    (ROOT / "data").mkdir(exist_ok=True)
    (ROOT / "data" / "PROVENANCE.md").write_text("\n".join(header + rows) + "\n")
    print(f"copied {len(rows)} files; wrote data/PROVENANCE.md")


if __name__ == "__main__":
    main()
