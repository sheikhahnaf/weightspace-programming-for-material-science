// Build the deck named in deck.json: one HTML file per slide in slides/, converted with
// html2pptx (Playwright + PptxGenJS). Speaker notes come from the NOTES comment
// in each file; tables come from the TABLES map below and are placed on the
// placeholder div of the slide that declares them.
const fs = require('fs');
const path = require('path');
const pptxgen = require('pptxgenjs');
const html2pptx = require('./html2pptx');

const HERE = __dirname;
const SLIDES = path.join(HERE, 'slides');
const CFG = JSON.parse(fs.readFileSync(path.join(HERE, 'deck.json'), 'utf8'));
const OUT = path.join(HERE, CFG.output);
const TMP = process.env.DECK_TMP || path.join(HERE, '.tmp');
fs.mkdirSync(TMP, { recursive: true });

const MAROON = '500000';
const GRAY = 'D6D3D1';
const TEXT = '333333';

function hdr(t) {
  return { text: t, options: { bold: true, color: 'FFFFFF', fill: { color: MAROON }, fontFace: 'Calibri', valign: 'middle' } };
}

// Tables keyed by slide slug (file name without its number prefix), written by
// make_slides.py into tables.json: rows of strings, the first row the header.
const RAW = JSON.parse(fs.readFileSync(path.join(HERE, 'tables.json'), 'utf8'));
function spec(t) {
  return { id: t.id, rows: [t.rows[0].map(hdr), ...t.rows.slice(1)], options: { colW: t.colW, fontSize: t.fontSize } };
}
const TABLES = {};
for (const [slug, t] of Object.entries(RAW)) {
  TABLES[slug] = Array.isArray(t) ? { multi: t.map(spec) } : spec(t);
}

function notesOf(html) {
  const m = html.match(/<!--NOTES([\s\S]*?)-->/);
  return m ? m[1].replace(/\s+/g, ' ').trim() : '';
}

function addTable(slide, ph, spec) {
  slide.addTable(spec.rows, {
    x: ph.x, y: ph.y, w: ph.w, h: ph.h,
    colW: spec.options.colW,
    fontSize: spec.options.fontSize,
    fontFace: 'Calibri',
    color: TEXT,
    border: { type: 'solid', pt: 0.75, color: GRAY },
    valign: 'middle',
    autoPage: false,
    margin: 0.04,
  });
}

(async () => {
  const pptx = new pptxgen();
  pptx.layout = 'LAYOUT_16x9';
  pptx.author = CFG.author;
  pptx.title = CFG.title;
  pptx.subject = CFG.subject;

  const files = fs.readdirSync(SLIDES).filter((f) => f.endsWith('.html')).sort();
  const wordCounts = [];
  const failures = [];
  for (const f of files) {
    const html = fs.readFileSync(path.join(SLIDES, f), 'utf8');
    let slide, placeholders;
    try {
      ({ slide, placeholders } = await html2pptx(path.join(SLIDES, f), pptx, { tmpDir: TMP }));
    } catch (e) {
      failures.push(e.message);
      console.log(`FAIL ${f}`);
      continue;
    }
    const notes = notesOf(html);
    if (notes) slide.addNotes(notes);
    wordCounts.push([f, notes.split(/\s+/).filter(Boolean).length]);
    const spec = TABLES[f.replace(/^\d+-/, '')];
    if (spec) {
      if (spec.multi) {
        for (const t of spec.multi) {
          const ph = placeholders.find((p) => p.id === t.id);
          if (!ph) throw new Error(`${f}: placeholder ${t.id} missing`);
          addTable(slide, ph, t);
        }
      } else {
        if (!placeholders.length) throw new Error(`${f}: no placeholder for table`);
        addTable(slide, placeholders[0], spec);
      }
    }
    console.log(`ok  ${f}  notes ${wordCounts[wordCounts.length - 1][1]} words`);
  }
  if (failures.length) {
    console.log(`\n${failures.length} slide(s) failed validation; deck not written:`);
    for (const m of failures) console.log('  ' + m.replace(/\n/g, '\n    '));
    process.exit(1);
  }
  await pptx.writeFile({ fileName: OUT });
  console.log(`wrote ${OUT} with ${files.length} slides`);
  const [lo, hi] = CFG.notes_words || [60, 120];
  const short = wordCounts.filter(([, n]) => n < lo || n > hi);
  if (short.length) console.log(`notes outside ${lo} to ${hi} words:`, short.map(([f, n]) => `${f} (${n})`).join(', '));
})().catch((e) => { console.error(e); process.exit(1); });
