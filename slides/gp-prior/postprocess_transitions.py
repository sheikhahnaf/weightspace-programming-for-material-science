"""Add a medium-speed fade transition to every slide of the built deck.

For each ppt/slides/slideN.xml, insert <p:transition spd="med"><p:fade/></p:transition>
before </p:sld>, after <p:clrMapOvr> when present (the schema order puts the
transition after clrMapOvr and before timing), then rezip in place. A slide that
already carries a transition is left alone, so the script can be rerun.
"""
import json
import re
import shutil
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
DECK = HERE / json.loads((HERE / "deck.json").read_text())["output"]
TRANS = '<p:transition spd="med"><p:fade/></p:transition>'


def patch(xml: str) -> str:
    if "<p:transition" in xml:
        return xml
    m = re.search(r"</p:clrMapOvr>", xml)
    if m:
        return xml[:m.end()] + TRANS + xml[m.end():]
    m = re.search(r"<p:timing[ >]", xml)
    if m:
        return xml[:m.start()] + TRANS + xml[m.start():]
    return xml.replace("</p:sld>", TRANS + "</p:sld>")


def main():
    deck = Path(sys.argv[1]) if len(sys.argv) > 1 else DECK
    tmp = deck.with_suffix(".tmp.pptx")
    n = 0
    with zipfile.ZipFile(deck) as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if re.fullmatch(r"ppt/slides/slide\d+\.xml", item.filename):
                xml = data.decode("utf-8")
                new = patch(xml)
                if new != xml:
                    n += 1
                data = new.encode("utf-8")
            zout.writestr(item, data)
    shutil.move(tmp, deck)
    with zipfile.ZipFile(deck) as z:
        slides = [f for f in z.namelist() if re.fullmatch(r"ppt/slides/slide\d+\.xml", f)]
        have = sum('<p:transition spd="med"><p:fade/></p:transition>' in z.read(f).decode() for f in slides)
    print(f"{deck.name}: fade added to {n} slides; {have} of {len(slides)} slides carry the medium fade")


if __name__ == "__main__":
    main()
