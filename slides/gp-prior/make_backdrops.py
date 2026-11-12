"""Title, outline and divider backgrounds from the maroon low-polygon backdrop.

  figures/title_bg.png    backdrop with the white slanted banner across the right (the wordmark sits on it)
  figures/outline_bg.png  backdrop, optionally with one figure blended faintly on the right
  figures/dark_bg.png     backdrop alone, for dividers

Usage: python make_backdrops.py [blend_figure.png]
The backdrop is figures/backdrop.png (the skill's assets/backdrops/lowpoly_maroon.png,
copied in by new_deck.sh); replace it with another approved backdrop if wanted.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
FIG = HERE / "figures"
W, H = 1920, 1080


def cover(im, w, h):
    s = max(w / im.width, h / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x, y = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((x, y, x + w, y + h))


def main():
    back = cover(Image.open(FIG / "backdrop.png").convert("RGB"), W, H)
    t = back.copy()
    ImageDraw.Draw(t).polygon([(800, 200), (W, 200), (W, 430), (690, 430)], fill="white")
    t.save(FIG / "title_bg.png")
    o = back.copy()
    if len(sys.argv) > 1:
        a = cover(Image.open(sys.argv[1]).convert("RGB"), 1150, 650)
        ramp = np.clip((np.arange(a.width) - 80) / 520.0, 0, 1) * 0.24
        yy = np.arange(a.height)
        vfeather = np.clip(np.minimum(yy, a.height - 1 - yy) / 140.0, 0, 1)
        mask = Image.fromarray((np.outer(vfeather, ramp) * 255).astype("uint8"))
        region = o.crop((W - a.width - 20, 230, W - 20, 230 + a.height))
        o.paste(Image.composite(a, region, mask), (W - a.width - 20, 230))
    o.save(FIG / "outline_bg.png")
    back.save(FIG / "dark_bg.png")
    print("wrote title_bg.png, outline_bg.png, dark_bg.png")


if __name__ == "__main__":
    main()
