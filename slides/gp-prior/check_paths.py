"""Fail the build if any slide references a missing or unsuitable image.

Every <img src> and body background-image in slides/*.html must resolve to an
existing file under this folder, be PNG or JPEG by content, carry the matching
extension, and be 8-bit RGB (PowerPoint shows "The picture can't be displayed"
for some palette, alpha and mislabeled files). PDFs are never placed.
"""
import re
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
bad, n = [], 0
for f in sorted((HERE / "slides").glob("*.html")):
    html = f.read_text()
    for a, b in re.findall(r'src="([^"]+)"|url\(\'([^\']+)\'\)', html):
        ref = a or b
        path = (f.parent / ref).resolve()
        n += 1
        if HERE not in path.parents:
            bad.append(f"{f.name}: {ref} lies outside the deck folder")
            continue
        if not path.exists():
            bad.append(f"{f.name}: {ref} does not exist")
            continue
        try:
            im = Image.open(path)
        except Exception as e:
            bad.append(f"{f.name}: {ref} unreadable ({e})")
            continue
        ext = path.suffix.lower()
        want = {"PNG": {".png"}, "JPEG": {".jpg", ".jpeg"}}.get(im.format)
        if not want:
            bad.append(f"{f.name}: {ref} is {im.format}, not PNG or JPEG")
        elif ext not in want:
            bad.append(f"{f.name}: {ref} is {im.format} data under a {ext} name")
        if im.mode != "RGB":
            bad.append(f"{f.name}: {ref} has mode {im.mode}, not RGB")
if bad:
    print("IMAGE CHECK FAILED:")
    for b in bad:
        print("  " + b)
    sys.exit(1)
print(f"image check: {n} references in {len(list((HERE / 'slides').glob('*.html')))} slides, all existing 8-bit RGB PNG or JPEG with matching extensions")
