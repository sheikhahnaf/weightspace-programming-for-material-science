"""Read the built deck back with python-pptx and report its structure.

For each slide: the title text (the text frame whose first run is the largest
white or maroon bold text at the top, or the largest text on divider slides),
the word count of the notes, the number of pictures and tables, and any
text box that is empty. Exits non-zero if a slide lacks a title or notes or
has an empty text box.
"""
import sys
import json
from pathlib import Path

from pptx import Presentation
from pptx.util import Emu

HERE = Path(__file__).resolve().parent
DECK = HERE / json.loads((HERE / "deck.json").read_text())["output"]


def main():
    prs = Presentation(str(DECK))
    w, h = prs.slide_width, prs.slide_height
    print(f"{DECK.name}: {len(prs.slides)} slides, {Emu(w).inches:.2f} x {Emu(h).inches:.2f} in")
    problems = []
    for i, slide in enumerate(prs.slides, 1):
        texts = []
        pictures = 0
        tables = 0
        empty_boxes = []
        for shp in slide.shapes:
            if shp.shape_type == 13:  # picture
                pictures += 1
            if shp.has_table:
                tables += 1
                continue
            if shp.has_text_frame:
                t = shp.text_frame.text.strip()
                is_textbox = shp._element.find('.//{http://schemas.openxmlformats.org/presentationml/2006/main}cNvSpPr') is not None and \
                    shp._element.find('.//{http://schemas.openxmlformats.org/presentationml/2006/main}cNvSpPr').get('txBox') == '1'
                if t:
                    size = 0
                    for p in shp.text_frame.paragraphs:
                        for r in p.runs:
                            if r.font.size:
                                size = max(size, r.font.size.pt)
                    texts.append((shp.top, size, t))
                elif is_textbox:
                    empty_boxes.append(shp.shape_id)
        # title: the text nearest the top with the largest font among the top 1.2 in
        title = None
        if texts:
            top_band = [t for t in texts if t[0] is not None and Emu(t[0]).inches < 1.4]
            cand = top_band or texts
            title = max(cand, key=lambda t: t[1])[2]
        notes = slide.notes_slide.notes_text_frame.text.strip() if slide.has_notes_slide else ""
        nwords = len(notes.split())
        flag = []
        if not title:
            flag.append("NO TITLE")
            problems.append(f"slide {i}: no title text")
        if not notes:
            flag.append("NO NOTES")
            problems.append(f"slide {i}: no notes")
        if empty_boxes:
            flag.append(f"EMPTY TEXT BOXES {empty_boxes}")
            problems.append(f"slide {i}: empty text boxes {empty_boxes}")
        short = (title or "")[:60]
        print(f"{i:2d}  {short:<60} pics {pictures} tables {tables} notes {nwords:3d} words {' '.join(flag)}")
    if problems:
        print("\nPROBLEMS:")
        for p in problems:
            print("  " + p)
        sys.exit(1)
    print("\nevery slide has a title and notes; no empty text boxes")


if __name__ == "__main__":
    main()
