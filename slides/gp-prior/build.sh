#!/bin/bash
# Full rebuild, in order. Run from anywhere. Close the PPTX in PowerPoint first:
# PowerPoint loads pictures lazily from the file on disk, and a rebuild underneath
# an open deck shows "The picture can't be displayed" on the later slides.
set -e -o pipefail
cd "$(dirname "$0")"
eval "$(/Users/alvi/miniconda3/bin/conda shell.bash hook)"
conda activate matinvent
[ -f figures/title_bg.png ] || python make_backdrops.py
python make_slides.py                       # slides/*.html, tables.json, slide_index.json
python -c "import pathlib; [f.unlink() for f in pathlib.Path('thumbs').glob('*.png')]" 2>/dev/null || true
node thumbs.js > /dev/null                  # render every slide at 1920 x 1080
python make_recaps.py > /dev/null           # blur the slide before each recap
node thumbs.js $(ls slides | grep -- '-recap-' | cut -c1-3) > /dev/null
python check_paths.py                       # every image exists, 8-bit RGB PNG or JPEG
node build.js | tail -3
python postprocess_transitions.py           # medium fade on every slide
python wordcheck.py | tail -1
python readback.py | tail -1
