"""Recap backgrounds: the previous slide's thumbnail, Gaussian-blurred and lightened.

For every slide whose file name holds "-recap-", take thumbs/<previous slide>.png
(rendered by thumbs.js), blur it, blend it toward white, and save it as
figures/recaps/<recap file stem>.png, which the recap slide sets as its body
background. Run thumbs.js first so the previous slides are current.
"""
from pathlib import Path

from PIL import Image, ImageFilter

HERE = Path(__file__).resolve().parent
SLIDES = HERE / "slides"
THUMBS = HERE / "thumbs"
OUT = HERE / "figures" / "recaps"
OUT.mkdir(parents=True, exist_ok=True)

files = sorted(f.name for f in SLIDES.glob("*.html"))
for i, f in enumerate(files):
    if "-recap-" not in f:
        continue
    prev = files[i - 1]
    src = THUMBS / prev.replace(".html", ".png")
    im = Image.open(src).convert("RGB")
    im = im.filter(ImageFilter.GaussianBlur(radius=7))
    white = Image.new("RGB", im.size, "white")
    im = Image.blend(im, white, 0.35)
    dst = OUT / f.replace(".html", ".png")
    im.save(dst)
    print(f"{f}: blurred {prev}")
