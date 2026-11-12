// Render every slide HTML to a 1920 x 1080 PNG in thumbs/ with Playwright.
// The HTML is what positions the PPTX, so these renders are the visual check.
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const HERE = __dirname;
const SLIDES = path.join(HERE, 'slides');
const THUMBS = path.join(HERE, 'thumbs');
fs.mkdirSync(THUMBS, { recursive: true });

(async () => {
  const only = process.argv.slice(2);
  let files = fs.readdirSync(SLIDES).filter((f) => f.endsWith('.html')).sort();
  if (only.length) files = files.filter((f) => only.some((o) => f.startsWith(o)));
  const browser = await chromium.launch({ channel: 'chrome' });
  const page = await browser.newPage({ viewport: { width: 960, height: 540 }, deviceScaleFactor: 2 });
  for (const f of files) {
    await page.goto('file://' + path.join(SLIDES, f));
    await page.waitForLoadState('load');
    const dims = await page.evaluate(() => ({ sw: document.body.scrollWidth, sh: document.body.scrollHeight }));
    const out = path.join(THUMBS, f.replace(/\.html$/, '.png'));
    await page.screenshot({ path: out, clip: { x: 0, y: 0, width: 960, height: 540 } });
    const flag = dims.sw > 961 || dims.sh > 541 ? `  OVERFLOW ${dims.sw}x${dims.sh}` : '';
    console.log(`${f}${flag}`);
  }
  await browser.close();
})().catch((e) => { console.error(e); process.exit(1); });
