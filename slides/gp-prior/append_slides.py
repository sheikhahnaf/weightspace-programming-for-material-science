"""Append slides from a partner's deck, unchanged, to a deck built with this skill.

Use it when a joint deck must end (or continue) with another team's slides exactly as they made them.
1. The built deck (html2pptx, 10 x 5.625 in) is scaled to the partner deck's page (for 13.333 x 7.5 in exactly 4/3):
   offsets, extents, font sizes, line widths, insets, spacing, table grid and margins, shadows. Our slides are
   generated, so they absorb the change; the partner's slides stay byte-identical.
2. The chosen slides are copied with their pictures, notes pages, slide layout(s), slide master (pruned to the copied
   layouts), theme, and every table style they use. Optional presenter notes go into their notes pages only.

Pitfalls this handles (each one made PowerPoint offer to "repair" the file, or broke the partner's tables):
- html2pptx lists Overrides in [Content_Types].xml for slideMaster2..N that do not exist. A copied part named like
  one of them gives two Overrides for one part. Copied parts are named outside every listed name.
- Each new master is numbered before its layouts (master id < layout ids, all unique across the presentation).
- Tables that take their header fill from a table style render white-on-white unless the style is copied into
  ppt/tableStyles.xml.
Check the result offline (no duplicate PartName, every relationship target exists) before opening it in PowerPoint.

Usage:
  python append_slides.py --built deck.pptx --partner partner.pptx --slides 15,16,17 --out joint.pptx \
      [--notes notes.json]   # {"15": "notes text", ...}, keyed by the partner deck's slide number
"""
import argparse
import json
import posixpath
import re
import zipfile
from fractions import Fraction
from pathlib import Path

AP = argparse.ArgumentParser(description=__doc__.split("\n")[0])
AP.add_argument("--built", required=True)
AP.add_argument("--partner", required=True)
AP.add_argument("--slides", required=True, help="comma-separated slide numbers of the partner deck")
AP.add_argument("--out", required=True)
AP.add_argument("--notes", help="JSON file: partner slide number -> presenter notes")
ARGS = AP.parse_args()
BUILT, DRIVE, OUT = Path(ARGS.built), Path(ARGS.partner), Path(ARGS.out)
SOLVUS_SLIDES = [int(x) for x in ARGS.slides.split(",")]
SOLVUS_NOTES = {int(k): v for k, v in json.loads(Path(ARGS.notes).read_text()).items()} if ARGS.notes else {}


def _sld_size(path):
    xml = zipfile.ZipFile(path).read("ppt/presentation.xml").decode("utf-8")
    tag = re.search(r"<p:sldSz\b[^>]*>", xml).group(0)  # attribute order varies (Google exports cy first)
    return int(re.search(r'\bcx="(\d+)"', tag).group(1)), int(re.search(r'\bcy="(\d+)"', tag).group(1))


SLD_W, SLD_H = _sld_size(DRIVE)
_bw, _bh = _sld_size(BUILT)
K = Fraction(SLD_W, _bw)
assert Fraction(SLD_H, _bh) == K, "the partner deck must have the same aspect ratio as the built deck"


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


def rels_of(part):
    d, b = posixpath.split(part)
    return f"{d}/_rels/{b}.rels"


def parse_rels(xml):
    return [dict(re.findall(r'(\w+)="([^"]*)"', r)) for r in re.findall(r"<Relationship\b[^>]*/>", xml)]


def write_rels(rels):
    body = "".join(f'<Relationship Id="{r["Id"]}" Type="{r["Type"]}" Target="{r["Target"]}"'
                   + (f' TargetMode="{r["TargetMode"]}"' if "TargetMode" in r else "") + "/>" for r in rels)
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<Relationships xmlns="http://schemas.openxml'
            f'formats.org/package/2006/relationships">{body}</Relationships>')


def resolve(part, target):
    return posixpath.normpath(posixpath.join(posixpath.dirname(part), target))


def relpath(part, target_part):
    return posixpath.relpath(target_part, posixpath.dirname(part))


def free(names, prefix, ext):
    i = 1
    while f"{prefix}{i}{ext}" in names:
        i += 1
    return f"{prefix}{i}{ext}"


def main():
    zt = zipfile.ZipFile(BUILT)
    T = {n: zt.read(n) for n in zt.namelist()}
    zs = zipfile.ZipFile(DRIVE)
    S = {n: zs.read(n) for n in zs.namelist()}

    # 1. scale the built deck
    for n in list(T):
        if re.match(r"ppt/(slides|slideLayouts|slideMasters)/[^/]+\.xml$", n):
            T[n] = scale_xml(T[n].decode("utf-8")).encode("utf-8")
    pres = T["ppt/presentation.xml"].decode("utf-8")
    pres = re.sub(r"<p:sldSz[^>]*/>", f'<p:sldSz cx="{SLD_W}" cy="{SLD_H}"/>', pres)

    # 2. copy parts from the Drive deck, renaming on collision
    mapping = {}
    ct = T["[Content_Types].xml"].decode("utf-8")
    overrides = []
    # html2pptx lists Overrides for slideMaster2..N that do not exist; a copied part must not reuse one of those
    # names, or [Content_Types].xml holds two Overrides for one part and PowerPoint offers to repair the file
    listed = {pn.lstrip("/") for pn in re.findall(r'PartName="([^"]+)"', ct)}

    def new_name(src):
        d, b = posixpath.split(src)
        stem, ext = posixpath.splitext(b)
        if src not in T and src not in listed:
            return src
        return free(set(T) | listed, f"{d}/{re.sub(r'[0-9]+$', '', stem)}", ext)

    def copy_part(src, kind=None):
        if src in mapping:
            return mapping[src]
        dst = new_name(src)
        mapping[src] = dst
        T[dst] = b""  # reserve the name before following relationships
        data = S[src]
        if kind:
            overrides.append((dst, CT[kind]))
        rp = rels_of(src)
        if rp in S:
            rels = parse_rels(S[rp].decode("utf-8"))
            keep = []
            for r in rels:
                if r.get("TargetMode") == "External":
                    keep.append(r)
                    continue
                tgt = resolve(src, r["Target"])
                typ = r["Type"].rsplit("/", 1)[-1]
                if typ == "slideLayout" and kind == "slideMaster" and tgt not in LAYOUTS:
                    continue  # prune the master to the copied layouts
                if typ == "notesMaster":
                    nm = next(n for n in T if re.match(r"ppt/notesMasters/notesMaster\d+\.xml$", n))
                    keep.append({**r, "Target": relpath(dst, nm)})
                    continue
                if typ == "slide" and kind == "notesSlide":
                    keep.append({**r, "Target": relpath(dst, SLIDE_DST[tgt])})
                    continue
                sub = copy_part(tgt, typ if typ in CT else None)
                keep.append({**r, "Target": relpath(dst, sub)})
            if kind == "slideMaster":
                kept = {r["Id"] for r in keep}
                xml = data.decode("utf-8")
                xml = re.sub(r'<p:sldLayoutId\b[^>]*r:id="(rId\d+)"[^>]*/>',
                             lambda m: m.group(0) if m.group(1) in kept else "", xml)
                data = xml.encode("utf-8")
            T[rels_of(dst)] = write_rels(keep).encode("utf-8")
        T[dst] = data
        return dst

    srels = parse_rels(S["ppt/_rels/presentation.xml.rels"].decode("utf-8"))
    spres = S["ppt/presentation.xml"].decode("utf-8")
    sids = re.findall(r'<p:sldId\b[^>]*r:id="(rId\d+)"', spres)
    src_slides = [resolve("ppt/presentation.xml", next(r["Target"] for r in srels if r["Id"] == sids[i - 1]))
                  for i in SOLVUS_SLIDES]
    LAYOUTS = set()
    for sp in src_slides:
        for r in parse_rels(S[rels_of(sp)].decode("utf-8")):
            if r["Type"].endswith("/slideLayout"):
                LAYOUTS.add(resolve(sp, r["Target"]))
    SLIDE_DST = {}
    for sp in src_slides:
        SLIDE_DST[sp] = free(set(T) | listed, "ppt/slides/slide", ".xml")
        T[SLIDE_DST[sp]] = b""
    for sp in src_slides:
        mapping[sp] = SLIDE_DST[sp]
        data = S[sp]
        overrides.append((SLIDE_DST[sp], CT["slide"]))
        rels = parse_rels(S[rels_of(sp)].decode("utf-8"))
        keep = []
        for r in rels:
            tgt = resolve(sp, r["Target"])
            typ = r["Type"].rsplit("/", 1)[-1]
            sub = copy_part(tgt, typ if typ in CT else None)
            keep.append({**r, "Target": relpath(SLIDE_DST[sp], sub)})
        T[rels_of(SLIDE_DST[sp])] = write_rels(keep).encode("utf-8")
        T[SLIDE_DST[sp]] = data

    for n, sp in zip(SOLVUS_SLIDES, src_slides):
        for r in parse_rels(S[rels_of(sp)].decode("utf-8")):
            if r["Type"].endswith("/notesSlide"):
                d = mapping[resolve(sp, r["Target"])]
                if SOLVUS_NOTES.get(n):
                    T[d] = put_notes(T[d].decode("utf-8"), SOLVUS_NOTES[n]).encode("utf-8")

    # table styles: the Solvus tables take their header fill from styles in the Drive deck's tableStyles.xml;
    # without them the white header text sits on white
    used = set()
    for sp in src_slides:
        used |= set(re.findall(r"<a:tableStyleId>([^<]+)</a:tableStyleId>", S[sp].decode("utf-8")))
    src_ts = S["ppt/tableStyles.xml"].decode("utf-8")
    ts = T["ppt/tableStyles.xml"].decode("utf-8")
    have = set(re.findall(r'<a:tblStyle\b[^>]*styleId="([^"]+)"', ts))
    blocks = [m.group(0) for m in re.finditer(r'<a:tblStyle\b[^>]*styleId="([^"]+)"[^>]*>.*?</a:tblStyle>', src_ts, re.S)
              if m.group(1) in used and m.group(1) not in have]
    if blocks:
        if re.search(r"<a:tblStyleLst\b[^>]*/>", ts):
            ts = re.sub(r"(<a:tblStyleLst\b[^>]*)/>", r"\1></a:tblStyleLst>", ts)
        ts = ts.replace("</a:tblStyleLst>", "".join(blocks) + "</a:tblStyleLst>")
        T["ppt/tableStyles.xml"] = ts.encode("utf-8")
    print("table styles copied:", len(blocks), "of", len(used), "used")

    # masters and layouts need ids unique across the presentation
    ids = [int(x) for x in re.findall(r'<p:sldMasterId\b[^>]*\bid="(\d+)"', pres)]
    for n in T:
        if re.match(r"ppt/slideMasters/[^/]+\.xml$", n) and T[n]:
            ids += [int(x) for x in re.findall(r'<p:sldLayoutId\b[^>]*\bid="(\d+)"', T[n].decode("utf-8"))]
    nxt = max(ids) + 1
    new_masters = [d for s, d in mapping.items() if s.startswith("ppt/slideMasters/")]
    prels = parse_rels(T["ppt/_rels/presentation.xml.rels"].decode("utf-8"))
    rid = max(int(r["Id"][3:]) for r in prels if r["Id"].startswith("rId")) + 1
    for m in new_masters:
        master_id = nxt
        prels.append({"Id": f"rId{rid}", "Type": REL + "slideMaster", "Target": relpath("ppt/presentation.xml", m)})
        pres = pres.replace("</p:sldMasterIdLst>",
                            f'<p:sldMasterId id="{master_id}" r:id="rId{rid}"/></p:sldMasterIdLst>')
        rid += 1

        def renum(mm):
            nonlocal nxt
            nxt += 1
            return re.sub(r'\bid="\d+"', f'id="{nxt}"', mm.group(0))
        T[m] = re.sub(r"<p:sldLayoutId\b[^>]*/>", renum, T[m].decode("utf-8")).encode("utf-8")
        nxt += 1
    sid = max(int(x) for x in re.findall(r'<p:sldId\b[^>]*\bid="(\d+)"', pres)) + 1
    for sp in src_slides:
        prels.append({"Id": f"rId{rid}", "Type": REL + "slide",
                      "Target": relpath("ppt/presentation.xml", SLIDE_DST[sp])})
        pres = pres.replace("</p:sldIdLst>", f'<p:sldId id="{sid}" r:id="rId{rid}"/></p:sldIdLst>')
        rid += 1
        sid += 1
    T["ppt/_rels/presentation.xml.rels"] = write_rels(prels).encode("utf-8")
    T["ppt/presentation.xml"] = pres.encode("utf-8")

    exts = set(re.findall(r'<Default Extension="([^"]+)"', ct))
    add = ""
    for d in mapping.values():
        e = posixpath.splitext(d)[1][1:].lower()
        if d.startswith("ppt/media/") and e not in exts:
            mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "gif": "image/gif",
                    "svg": "image/svg+xml", "emf": "image/x-emf"}.get(e, "application/octet-stream")
            add += f'<Default Extension="{e}" ContentType="{mime}"/>'
            exts.add(e)
    for d, c in overrides:
        assert d not in listed, d
        add += f'<Override PartName="/{d}" ContentType="{c}"/>'
    T["[Content_Types].xml"] = ct.replace("</Types>", add + "</Types>").encode("utf-8")
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", T.pop("[Content_Types].xml"))
        for n, b in T.items():
            z.writestr(n, b)
    print("wrote", OUT, "with", len(re.findall(r"<p:sldId\b", pres)), "slides;", "copied parts:",
          sorted(set(mapping.values())))


if __name__ == "__main__":
    main()
