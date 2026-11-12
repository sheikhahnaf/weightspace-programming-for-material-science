"""Scale a deck built with this skill (10 x 5.625 in) to the 13.333 x 7.5 in page, and optionally save a .potx.

PowerPoint's own 16:9 page is 13.333 x 7.5 in. Use this for a deck that others will extend in PowerPoint, and for a
group template: build a starter deck (one example of each slide type, rules in the notes), then
  python scale.py --built deck.pptx --out Template.pptx --potx
writes Template.pptx and Template.potx (the same package; only the main part's content type differs).
Do not hand-build masters and layouts with python-pptx for a template: such a file hung Quick Look in October 2026,
a sign PowerPoint may offer to repair it; the html2pptx deck opens cleanly.
"""
import argparse
import re
import zipfile
from fractions import Fraction
from pathlib import Path

K = Fraction(4, 3)
SLD_W, SLD_H = 12192000, 6858000

# element -> attributes holding lengths (EMU) or font sizes (1/100 pt) that scale with the page
SCALE = {"a:off": ("x", "y"), "a:chOff": ("x", "y"), "a:ext": ("cx", "cy"), "a:chExt": ("cx", "cy"),
         "a:rPr": ("sz",), "a:defRPr": ("sz",), "a:endParaRPr": ("sz",), "a:ln": ("w",),
         "a:bodyPr": ("lIns", "tIns", "rIns", "bIns"), "a:spcPts": ("val",), "a:gridCol": ("w",), "a:tr": ("h",),
         "a:tcPr": ("marL", "marR", "marT", "marB"), "a:pPr": ("marL", "marR", "indent"),
         "a:outerShdw": ("blurRad", "dist"), "a:innerShdw": ("blurRad", "dist")}
SCALE.update({f"a:lvl{i}pPr": ("marL", "marR", "indent") for i in range(1, 10)})
TAG = re.compile(r"<(" + "|".join(re.escape(t) for t in SCALE) + r")(\s[^>]*?)?(/?)>")




def put_notes(xml, text):
    """Write text into the body placeholder of a notes slide (its first paragraph)."""
    text = " ".join(text.split()).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    start = xml.find('type="body"')
    sp0 = xml.rfind("<p:sp>", 0, start)
    sp1 = xml.find("</p:sp>", start)
    sp = xml[sp0:sp1]
    if "<a:t></a:t>" in sp:
        sp = sp.replace("<a:t></a:t>", f"<a:t>{text}</a:t>", 1)
    elif "<a:t/>" in sp:
        sp = sp.replace("<a:t/>", f"<a:t>{text}</a:t>", 1)
    else:
        sp = sp.replace("</a:p>", f"<a:r><a:t>{text}</a:t></a:r></a:p>", 1)
    return xml[:sp0] + sp + xml[sp1:]

NS_R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
CT = {"slide": "application/vnd.openxmlformats-officedocument.presentationml.slide+xml",
      "notesSlide": "application/vnd.openxmlformats-officedocument.presentationml.notesSlide+xml",
      "slideLayout": "application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml",
      "slideMaster": "application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml",
      "theme": "application/vnd.openxmlformats-officedocument.theme+xml"}
REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/"

# element -> attributes holding lengths (EMU) or font sizes (1/100 pt) that scale with the page
SCALE = {"a:off": ("x", "y"), "a:chOff": ("x", "y"), "a:ext": ("cx", "cy"), "a:chExt": ("cx", "cy"),
         "a:rPr": ("sz",), "a:defRPr": ("sz",), "a:endParaRPr": ("sz",), "a:ln": ("w",),
         "a:bodyPr": ("lIns", "tIns", "rIns", "bIns"), "a:spcPts": ("val",), "a:gridCol": ("w",), "a:tr": ("h",),
         "a:tcPr": ("marL", "marR", "marT", "marB"), "a:pPr": ("marL", "marR", "indent"),
         "a:outerShdw": ("blurRad", "dist"), "a:innerShdw": ("blurRad", "dist")}
SCALE.update({f"a:lvl{i}pPr": ("marL", "marR", "indent") for i in range(1, 10)})
TAG = re.compile(r"<(" + "|".join(re.escape(t) for t in SCALE) + r")(\s[^>]*?)?(/?)>")


def scale_xml(xml):
    def tag(m):
        name, attrs, close = m.group(1), m.group(2) or "", m.group(3)
        for a in SCALE[name]:
            attrs = re.sub(rf'(\s{a}=")(-?\d+)(")', lambda n: f"{n.group(1)}{round(int(n.group(2)) * K)}{n.group(3)}",
                           attrs)
        return f"<{name}{attrs}{close}>"
    return TAG.sub(tag, xml)



def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--built", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--potx", action="store_true", help="also write <out>.potx")
    a = ap.parse_args()
    zin = zipfile.ZipFile(a.built)
    parts = {}
    for n in zin.namelist():
        b = zin.read(n)
        if re.match(r"ppt/(slides|slideLayouts|slideMasters)/[^/]+\.xml$", n):
            b = scale_xml(b.decode("utf-8")).encode("utf-8")
        elif n == "ppt/presentation.xml":
            b = re.sub(rb"<p:sldSz[^>]*/>", f'<p:sldSz cx="{SLD_W}" cy="{SLD_H}"/>'.encode(), b)
        parts[n] = b
    outs = [(Path(a.out), None)]
    if a.potx:
        outs.append((Path(a.out).with_suffix(".potx"), b"presentationml.template.main+xml"))
    for out, ctype in outs:
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
            for n, b in parts.items():
                if n == "[Content_Types].xml" and ctype:
                    b = b.replace(b"presentationml.presentation.main+xml", ctype)
                z.writestr(n, b)
        print("wrote", out)


if __name__ == "__main__":
    main()
