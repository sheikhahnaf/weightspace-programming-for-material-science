"""Slide library for the maroon-slide-deck skill.

A deck is declared in make_slides.py as a sequence of calls in deck order:
title(), outline(k), content(), build steps (content(..., kind="build")),
recap(), dark() and table_slide(). This module supplies the page chrome
(title, maroon rule, wordmark, footer bar with the slide number), the layout
helpers (img, p, sbox, node, line, panel) and write(), which renders one HTML
file per slide into slides/ and the tables into tables.json for build.js.

Coordinates are points on the 720 x 405 pt page (16:9). The content area runs
from y = 58 to y = 382; x from 24 to 696.
"""
import json
import math
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
SLIDES = HERE / "slides"
FIG = HERE / "figures"
CFG = json.loads((HERE / "deck.json").read_text(encoding="utf-8"))
SECTIONS = CFG["sections"]

slides = []   # dicts: slug, kind, section, body, notes, meta
tables = {}
DECK_MAP = {}


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ------------------------------------------------------------------ figures

def norm(rel):
    """Copy a figure into figures/deck/ as an 8-bit RGB PNG, alpha flattened on white.

    PowerPoint shows "The picture can't be displayed" for some PNG variants
    (palette, alpha) and for files whose extension does not match their
    content, so nothing is placed from its original file.
    """
    out = "deck/" + rel.replace("/", "__").rsplit(".", 1)[0] + ".png"
    dst = FIG / out
    if out not in DECK_MAP:
        im = Image.open(FIG / rel)
        if im.mode in ("RGBA", "LA", "P"):
            im = im.convert("RGBA")
            bg = Image.new("RGB", im.size, "white")
            bg.paste(im, mask=im.split()[-1])
            im = bg
        else:
            im = im.convert("RGB")
        dst.parent.mkdir(parents=True, exist_ok=True)
        im.save(dst, "PNG")
        DECK_MAP[out] = rel
    return out


def fit(rel, x, y, w, h, halign="center", valign="top"):
    """An <img> of figures/<rel> scaled to fit inside the box, keeping its aspect."""
    rel = norm(rel)
    im = Image.open(FIG / rel)
    a = im.width / im.height
    if w / h > a:
        ih, iw = h, h * a
    else:
        iw, ih = w, w / a
    ix = x + {"left": 0, "center": (w - iw) / 2, "right": w - iw}[halign]
    iy = y + {"top": 0, "middle": (h - ih) / 2, "bottom": h - ih}[valign]
    return (f'<img src="../figures/{rel}" style="left:{ix:.1f}pt;top:{iy:.1f}pt;'
            f'width:{iw:.1f}pt;height:{ih:.1f}pt;">'), (ix, iy, iw, ih)


def img(rel, x, y, w, h, **k):
    return fit(rel, x, y, w, h, **k)[0]


# ------------------------------------------------------------------ elements

def p(cls, x, y, w, text, style=""):
    """A positioned paragraph. Classes: lab (bold maroon label), cap (caption),
    small (11 pt grey), nodet (centred node text), cite (10 pt citation, bottom right)."""
    return f'<p class="{cls}" style="left:{x}pt;top:{y}pt;width:{w}pt;{style}">{text}</p>'


def sbox(x, y, w, lines, size=14, lh=18, pad=7):
    """The red-bordered summary box of a case-study slide: one line per entry, never wrapped.
    Keep each line short enough for the width; two to six lines."""
    h = len(lines) * lh + 2 * pad
    out = [f'<div class="sbox" style="left:{x}pt;top:{y}pt;width:{w}pt;height:{h}pt;"></div>']
    for i, t in enumerate(lines):
        out.append(f'<p class="sboxt" style="left:{x + pad + 2}pt;top:{y + pad + i * lh}pt;width:{w - 2 * pad - 4}pt;'
                   f'font-size:{size}pt;line-height:{lh}pt;">{t}</p>')
    return "\n".join(out)


def node(x, y, w, h, color="#1F3A5F", bw=1.5, bg="#FFFFFF", radius=0):
    """A boxed node of a tree or pipeline; text goes on top with p('nodet', ...)."""
    r = f"border-radius:{radius}pt;" if radius else ""
    return (f'<div class="node" style="left:{x}pt;top:{y}pt;width:{w}pt;height:{h}pt;'
            f'border:{bw}pt solid {color};background:{bg};{r}"></div>')


def line(x, y, w, h, color="#8A8F98"):
    """A connector: a thin horizontal (h small) or vertical (w small) bar."""
    return f'<div style="position:absolute;left:{x}pt;top:{y}pt;width:{w}pt;height:{h}pt;background:{color};"></div>'


def panel(x, y, w, h):
    """The orange-bordered panel of the conclusion slide."""
    return f'<div class="panel" style="left:{x}pt;top:{y}pt;width:{w}pt;height:{h}pt;"></div>'


def labelled_node(x, y, w, h, head, body, color="#1F3A5F", kicker=None):
    """A node with an optional grey kicker (e.g. 'Part 2'), a bold coloured head and a body line."""
    out = [node(x, y, w, h, color, 2)]
    top = y + 6
    if kicker:
        out.append(p("small", x + 6, top, w - 12, kicker, "text-align:center;color:#8A8F98;"))
        top += 16
    out.append(p("nodet", x + 6, top, w - 12, f"<b>{head}</b>", f"font-size:13pt;line-height:16pt;color:{color};"))
    out.append(p("nodet", x + 6, top + 36, w - 12, body, "font-size:10.5pt;line-height:13pt;"))
    return "\n".join(out)


# ------------------------------------------------------------------ slides

def add(slug, kind, section, body, notes, **meta):
    slides.append(dict(slug=slug, kind=kind, section=section, body=body, notes=notes.strip(), meta=meta))


def content(slug, title, section, body, notes, kind="content", **meta):
    """A white content slide. kind: content, build (one step of a progressive build) or backup.
    title: the source document's own section or subsection heading, shortened; never a claim."""
    add(slug, kind, section, dict(title=title, html=body), notes, **meta)


def recap(slug, section, text, notes, **meta):
    """The blurred previous slide with one centred red-bordered box of one or two sentences.
    The slug must contain 'recap'; make_recaps.py blurs the preceding slide's thumbnail."""
    if "recap" not in slug:
        slug = "recap-" + slug
    add(slug, "recap", section, dict(text=text), notes, **meta)


def outline(k, notes):
    """The outline on the maroon backdrop with section k highlighted in yellow."""
    add(f"outline-{k}", "outline", k, dict(k=k), notes)


def title(deck_title, event, name, date, name_lines, notes):
    """The title slide: maroon low-polygon backdrop, white slanted banner with the wordmark,
    the title right-aligned in white, then event, name, date and an optional line of names (collaborators, committee)."""
    wm1, wm2 = CFG["wordmark"]
    top, rest = (wm1.split(" & ", 1) + [""])[:2]
    html = f"""<p style="position:absolute;left:330pt;top:86pt;width:360pt;font-size:28pt;line-height:30pt;font-weight:bold;color:#500000;">{esc(top)}</p>
<p style="position:absolute;left:330pt;top:116pt;width:360pt;font-size:28pt;line-height:30pt;font-weight:bold;color:#500000;">{('&amp; ' + esc(rest)) if rest else ''}</p>
<p style="position:absolute;left:330pt;top:146pt;width:360pt;font-size:13pt;line-height:14pt;letter-spacing:3pt;color:#500000;">{esc(wm2)}</p>
<div style="position:absolute;left:316pt;top:90pt;width:1.5pt;height:68pt;background:#500000;"></div>
<p style="position:absolute;left:96pt;top:180pt;width:600pt;font-size:24pt;line-height:29pt;font-weight:bold;color:#FFFFFF;text-align:right;">{esc(deck_title)}</p>
<p style="position:absolute;left:296pt;top:250pt;width:400pt;font-size:18pt;line-height:22pt;color:#FFFFFF;text-align:right;">{esc(event)}</p>
<p style="position:absolute;left:296pt;top:276pt;width:400pt;font-size:16pt;line-height:20pt;font-weight:bold;color:#FFFFFF;text-align:right;">{esc(name)}</p>
<p style="position:absolute;left:296pt;top:299pt;width:400pt;font-size:14pt;line-height:18pt;color:#FFFFFF;text-align:right;">{esc(date)}</p>"""
    for i, ln in enumerate(name_lines):
        html += (f'\n<p style="position:absolute;left:196pt;top:{340 + 15 * i}pt;width:500pt;font-size:12pt;'
                 f'line-height:15pt;color:#F2E6E6;text-align:right;">{esc(ln)}</p>')
    add("title", "title", 0, dict(html=html), notes)


def dark(slug, heading, lines, notes):
    """A maroon divider (e.g. the backup divider): a yellow bar, a white heading, a few white lines."""
    html = (f'<div style="position:absolute;left:0pt;top:150pt;width:8pt;height:100pt;background:#FFD400;"></div>\n'
            f'<p style="position:absolute;left:40pt;top:170pt;width:640pt;font-size:34pt;line-height:40pt;font-weight:bold;color:#FFFFFF;">{esc(heading)}</p>')
    for i, t in enumerate(lines):
        html += f'\n<p style="position:absolute;left:40pt;top:{222 + 22 * i}pt;width:640pt;font-size:16pt;line-height:20pt;color:#F2E6E6;">{esc(t)}</p>'
    add(slug, "dark", 99, dict(html=html), notes)


def html_table(rows, widths_pt, size):
    ws = "".join(f'<col style="width:{w}pt">' for w in widths_pt)
    head = "".join(f"<th>{esc(c)}</th>" for c in rows[0])
    body = "".join("<tr>" + "".join(f"<td>{esc(c)}</td>" for c in r) + "</tr>" for r in rows[1:])
    return (f'<table style="border-collapse:collapse;font-size:{size}pt;line-height:{size + 2}pt;width:100%;table-layout:fixed;">'
            f'<colgroup>{ws}</colgroup><tr style="background:#500000;color:#fff;font-weight:bold;">{head}</tr>{body}</table>'
            '<style>td,th{border:0.75pt solid #D6D3D1;padding:2pt 3pt;vertical-align:middle;text-align:left;}</style>')


def table_slide(slug, title_, section, rows, colW_in, size, x, y, w, h, notes, cap=None, kind="content", cap_gap=6, **meta):
    """A native PowerPoint table (drawn by build.js on the placeholder), header row maroon.
    colW_in: column widths in inches, summing to about w/72.
    cap_gap: points between the placeholder bottom and the caption; PowerPoint may draw the table taller than h."""
    widths = [c * 72 for c in colW_in]
    tables[slug + ".html"] = dict(rows=rows, colW=colW_in, fontSize=size)
    body = (f'<div id="t1" class="placeholder" style="position:absolute;left:{x}pt;top:{y}pt;width:{w}pt;height:{h}pt;">'
            f'{html_table(rows, widths, size)}</div>')
    if cap:
        body += "\n" + p("small", x, y + h + cap_gap, w, cap)
    content(slug, title_, section, body, notes, kind=kind, **meta)


def conclusions(slug, title_, section, columns, notes, **meta):
    """Three orange-bordered panels side by side, the qualifying-exam conclusion layout.
    columns: [(heading, [fig1, fig2], [line, line, line]), ...] with figures relative to figures/."""
    out = []
    for j, (hd, figs, lines_) in enumerate(columns):
        x = 24 + j * 228
        out.append(p("lab", x, 58, 216, hd, "font-size:18pt;line-height:22pt;text-align:center;text-decoration:underline;color:#1F1F1F;"))
        out.append(panel(x, 84, 216, 288))
        if len(figs) == 1:   # one larger figure per panel
            out.append(img(figs[0], x + 6, 92, 204, 194, valign="middle"))
        for k, f in enumerate(figs[:2] if len(figs) > 1 else []):
            out.append(img(f, x + 10, 94 + 98 * k, 196, 92, valign="middle"))
        for k, t in enumerate(lines_):
            out.append(p("nodet", x + 8, 294 + k * 18, 200, t))
    content(slug, title_, section, "\n".join(out), notes, **meta)


# ------------------------------------------------------------------ rendering

def _wordmark():
    a, b = (esc(s) for s in CFG["wordmark"])
    return f'<div class="wm"><p class="b">{a}</p><p>{b}</p></div>'


def _partner():
    """Optional co-branding (deck.json "partner": {"logo": "<file in figures/>", "accent": "#RRGGBB"}): the partner's
    logo beside the wordmark, an accent line under the title rule and an accent stripe on the footer."""
    return CFG.get("partner") or {}


def _footer(num):
    pt = _partner()
    stripe = (f'<div style="position:absolute;left:0;top:386.5pt;width:720pt;height:1.5pt;'
              f'background:{pt["accent"]};"></div>\n') if pt.get("accent") else ""
    return stripe + f"""<div class="foot"></div>
<p class="foottxt">{esc(CFG["footer"])}</p>
<div class="numblk"></div>
<p class="num">{num}</p>"""


def _chrome(num):
    pt = _partner()
    extra = ""
    if pt.get("accent"):
        extra += (f'<div style="position:absolute;left:24pt;top:53pt;width:672pt;height:0.75pt;'
                  f'background:{pt["accent"]};"></div>\n')
    if pt.get("logo"):
        from PIL import Image as _I
        rel = norm(pt["logo"])
        im = _I.open(FIG / rel)
        h = 24.0
        w = h * im.width / im.height
        extra += f'<img src="../figures/{rel}" style="left:{517 - w:.1f}pt;top:14pt;width:{w:.1f}pt;height:{h}pt;">\n'
    return f'<div class="rule"></div>\n{extra}<div class="wmline"></div>\n{_wordmark()}\n{_footer(num)}'


FITSCRIPT = ("<script>(function(){var t=document.querySelector('h1.t');var z=28;"
             "while(t.scrollWidth>t.clientWidth&&z>20){z-=1;t.style.fontSize=z+'pt';}})();</script>")


def _page(body_attr, inner, notes):
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<link rel="stylesheet" href="deck.css">
</head>
<body{body_attr}>
{inner}
<!--NOTES
{notes}
-->
</body>
</html>
"""


def _render(num, s, fname):
    k = s["kind"]
    if k in ("content", "build", "backup"):
        tw = ' style="width:462pt;"' if _partner().get("logo") else ""
        inner = f'<h1 class="t"{tw}>{s["body"]["title"]}</h1>\n{FITSCRIPT}\n{_chrome(num)}\n{s["body"]["html"]}'
        return _page("", inner, s["notes"])
    if k == "recap":
        text = s["body"]["text"]
        nl = math.ceil(len(text) / 63)
        h = nl * 25 + 22
        top = round((405 - h) / 2 - 8)
        inner = (f'{_wordmark()}\n<div class="wmline"></div>\n{_footer(num)}\n'
                 f'<div class="rbox" style="top:{top}pt;height:{h}pt;"></div>\n'
                 f'<p class="rtxt" style="top:{top + 14}pt;">{text}</p>')
        bg = f' style="background-image:url(\'../figures/recaps/{fname.replace(".html", ".png")}\');"'
        return _page(bg, inner, s["notes"])
    if k == "outline":
        cur = s["body"]["k"]
        step = min(40, 300 // max(1, len(SECTIONS)))
        items = []
        for j, name in enumerate(SECTIONS, 1):
            cls = "oi on" if j == cur else "oi"
            items.append(f'<p class="{cls}" style="top:{78 + (j - 1) * step}pt;">{j}&#160;&#160;&#160;{esc(name)}</p>')
        inner = '<p class="oh">Outline</p>\n' + "\n".join(items) + "\n" + _footer(num)
        return _page(' style="background-image:url(\'../figures/outline_bg.png\');"', inner, s["notes"])
    if k == "title":
        return _page(' style="background-image:url(\'../figures/title_bg.png\');"', s["body"]["html"], s["notes"])
    if k == "dark":
        return _page(' style="background-image:url(\'../figures/dark_bg.png\');"', s["body"]["html"] + "\n" + _footer(num), s["notes"])
    raise ValueError(k)


def write():
    """Render every declared slide to slides/NNN-slug.html; write tables.json and slide_index.json."""
    SLIDES.mkdir(exist_ok=True)
    for old in SLIDES.glob("*.html"):
        old.unlink()
    rows = []
    for i, s in enumerate(slides, 1):
        fname = f"{i:03d}-{s['slug']}.html"
        (SLIDES / fname).write_text(_render(i, s, fname), encoding="utf-8")
        t = s["body"].get("title") if isinstance(s["body"], dict) else None
        if s["kind"] == "outline":
            t = f"Outline: {SECTIONS[s['body']['k'] - 1]}"
        elif s["kind"] in ("recap", "title", "dark"):
            t = s["kind"].capitalize()
        rows.append(dict(file=fname, title=t, kind=s["kind"], section=s["section"],
                         source=s["meta"].get("source", ""), replaces=s["meta"].get("replaces", "")))
    (HERE / "tables.json").write_text(json.dumps(tables, ensure_ascii=False, indent=1), encoding="utf-8")
    (HERE / "deck_images.json").write_text(json.dumps(DECK_MAP, indent=1), encoding="utf-8")
    (HERE / "slide_index.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    kinds = {}
    for r in rows:
        kinds[r["kind"]] = kinds.get(r["kind"], 0) + 1
    print(len(rows), "slides", kinds)
