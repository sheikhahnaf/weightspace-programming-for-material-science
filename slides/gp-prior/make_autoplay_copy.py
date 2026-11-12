"""Write a copy of the deck in which every embedded video starts by itself when its slide appears
in Slide Show (PowerPoint's "Start: Automatically"), instead of waiting for a click.

    python make_autoplay_copy.py [in.pptx] [out.pptx]
    (defaults: deck.json's "output" -> <stem>_autoplay.pptx next to it)

PptxGenJS embeds a video with no <p:timing> on its slide, which PowerPoint reads as "When Clicked
On". This adds the timing tree PowerPoint itself writes for an automatic start: a media call
playFrom(0.0) on the video shape, triggered with the slide (onBegin, delay 0), plus the media node.
The input file is never modified. Proven on the MS&T 2026 talk (2026-10-05): verify in PowerPoint itself
(no repair prompt; Slide Show starts the video), since python-pptx and unzip -t accept a deck PowerPoint repairs."""
from __future__ import annotations

import re
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

TIMING = ("<p:timing><p:tnLst><p:par><p:cTn id=\"1\" dur=\"indefinite\" restart=\"never\" nodeType=\"tmRoot\"><p:childTnLst>"
          # the main sequence PowerPoint writes for slide animations (a bare <p:par> here makes PowerPoint "repair" the file)
          "<p:seq concurrent=\"1\" nextAc=\"seek\"><p:cTn id=\"2\" dur=\"indefinite\" nodeType=\"mainSeq\"><p:childTnLst>"
          "<p:par><p:cTn id=\"3\" fill=\"hold\"><p:stCondLst><p:cond delay=\"indefinite\"/>"
          "<p:cond evt=\"onBegin\" delay=\"0\"><p:tn val=\"2\"/></p:cond></p:stCondLst><p:childTnLst>"
          "<p:par><p:cTn id=\"4\" fill=\"hold\"><p:stCondLst><p:cond delay=\"0\"/></p:stCondLst><p:childTnLst>"
          "<p:par><p:cTn id=\"5\" presetID=\"1\" presetClass=\"mediacall\" presetSubtype=\"0\" fill=\"hold\" nodeType=\"afterEffect\">"
          "<p:stCondLst><p:cond delay=\"0\"/></p:stCondLst><p:childTnLst>"
          "<p:cmd type=\"call\" cmd=\"playFrom(0.0)\"><p:cBhvr><p:cTn id=\"6\" dur=\"{dur}\" fill=\"hold\"/>"
          "<p:tgtEl><p:spTgt spid=\"{spid}\"/></p:tgtEl></p:cBhvr></p:cmd>"
          "</p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn></p:par>"
          "</p:childTnLst></p:cTn>"
          "<p:prevCondLst><p:cond evt=\"onPrev\" delay=\"0\"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>"
          "<p:nextCondLst><p:cond evt=\"onNext\" delay=\"0\"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst></p:seq>"
          "<p:video><p:cMediaNode vol=\"80000\"><p:cTn id=\"7\" fill=\"hold\" display=\"0\"><p:stCondLst><p:cond delay=\"indefinite\"/></p:stCondLst></p:cTn>"
          "<p:tgtEl><p:spTgt spid=\"{spid}\"/></p:tgtEl></p:cMediaNode></p:video>"
          "</p:childTnLst></p:cTn></p:par></p:tnLst></p:timing>")

NS = {"p": "http://schemas.openxmlformats.org/presentationml/2006/main",
      "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
      "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}


def unique_video_id(slide_xml: str) -> tuple[str, str]:
    """Give the <p:pic> that carries <a:videoFile> a shape id no other shape on the slide uses, and return
    (slide_xml, id). PptxGenJS numbers the video like a text box (both id="4"); a timing target on a
    duplicated id makes PowerPoint "repair" the file and drop the timing."""
    pics = [m for m in re.finditer(r"<p:pic>.*?</p:pic>", slide_xml, flags=re.S) if "<a:videoFile" in m.group(0)]
    if len(pics) != 1:
        raise ValueError(f"expected one video shape, found {len(pics)}")
    ids = [int(i) for i in re.findall(r'<p:cNvPr id="(\d+)"', slide_xml)]
    new_id = str(max(ids) + 1)
    pic = re.sub(r'<p:cNvPr id="\d+"', f'<p:cNvPr id="{new_id}"', pics[0].group(0), count=1)
    slide_xml = slide_xml[:pics[0].start()] + pic + slide_xml[pics[0].end():]
    all_ids = re.findall(r'<p:cNvPr id="(\d+)"', slide_xml)
    assert len(all_ids) == len(set(all_ids)), all_ids
    return slide_xml, new_id


def video_target(rels_xml: str) -> str:
    m = re.search(r'Type="[^"]*/relationships/video" Target="\.\./media/([^"]+)"', rels_xml)
    if not m:
        raise ValueError("no video relationship")
    return m.group(1)


def duration_ms(mp4_bytes: bytes) -> int:
    with tempfile.NamedTemporaryFile(suffix=".mp4") as f:
        f.write(mp4_bytes)
        f.flush()
        out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f.name],
                             capture_output=True, text=True, check=True).stdout.strip()
    return int(round(float(out) * 1000))


def add_autoplay(slide_xml: str, spid: str, dur: int) -> str:
    if "<p:timing" in slide_xml:
        raise ValueError("slide already has a timing tree; merge by hand")
    timing = TIMING.format(spid=spid, dur=dur)
    # schema order: cSld, clrMapOvr, transition, timing, extLst
    m = re.search(r"<p:extLst>(?:(?!<p:extLst>).)*</p:extLst>\s*</p:sld>\s*$", slide_xml, flags=re.S)
    cut = m.start() if m else slide_xml.rindex("</p:sld>")
    return slide_xml[:cut] + timing + slide_xml[cut:]


def main(argv=None) -> list[tuple[str, str, int]]:
    argv = sys.argv[1:] if argv is None else argv
    here = Path(__file__).resolve().parent
    import json
    src = Path(argv[0]) if argv else here / json.loads((here / "deck.json").read_text())["output"]
    dst = Path(argv[1]) if len(argv) > 1 else src.with_name(src.stem + "_autoplay.pptx")
    if src.resolve() == dst.resolve():
        raise SystemExit("refusing to overwrite the input deck")
    done = []
    with zipfile.ZipFile(src) as zin, zipfile.ZipFile(dst, "w") as zout:
        names = zin.namelist()
        for info in zin.infolist():
            data = zin.read(info.filename)
            if re.fullmatch(r"ppt/slides/slide\d+\.xml", info.filename) and b"<a:videoFile" in data:
                xml = data.decode("utf-8")
                rels = zin.read(info.filename.replace("slides/", "slides/_rels/") + ".rels").decode("utf-8")
                media = "ppt/media/" + video_target(rels)
                assert media in names, media
                xml, spid = unique_video_id(xml)
                dur = duration_ms(zin.read(media))
                xml = add_autoplay(xml, spid, dur)
                root = ET.fromstring(xml.encode("utf-8"))                       # well-formed
                tgt = root.findall(".//p:timing//p:spTgt", NS)
                assert [t.get("spid") for t in tgt] == [spid, spid], tgt
                tags = [c.tag.split("}")[1] for c in root]
                assert tags.index("timing") == tags.index("transition") + 1, tags   # schema order
                data = xml.encode("utf-8")
                done.append((info.filename, spid, dur))
            zout.writestr(info, data, compress_type=info.compress_type)
    for name, spid, dur in done:
        print(f"{name}: video shape {spid}, starts automatically, {dur / 1000:.1f} s")
    print(f"wrote {dst} ({len(done)} video slides set to autoplay); {src.name} unchanged")
    return done


if __name__ == "__main__":
    main()
