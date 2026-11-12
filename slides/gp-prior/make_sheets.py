"""Contact sheets of the slide thumbnails (2 x 2 per sheet) for the read-back."""
from pathlib import Path
from PIL import Image
H = Path(__file__).resolve().parent
import json
files = [H / "thumbs" / r["file"].replace(".html", ".png") for r in json.loads((H / "slide_index.json").read_text())]
n = 0
for i in range(0, len(files), 4):
    sheet = Image.new("RGB", (1920 * 2 // 2 + 6, 1080 * 2 // 2 + 6), "#888888")
    for k, f in enumerate(files[i:i + 4]):
        im = Image.open(f).convert("RGB").resize((960, 540), Image.LANCZOS)
        sheet.paste(im, ((k % 2) * 966, (k // 2) * 546))
    n += 1
    sheet.save(H / "sheets" / f"sheet_{n:02d}.png")
print(n, "sheets from", len(files), "thumbnails")
