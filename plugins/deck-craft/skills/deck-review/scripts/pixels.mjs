// Pixel analysis of a rendered deck: contact sheets, mean luminance per slide and luminance flips
// between neighbours, near-duplicate slides, empty bottom band, and (for PDFs) the background
// colour under every text run. Works on any PNG set (pdf_pages.mjs or html_deck_lint.mjs output).
//
// Usage: node pixels.mjs png_dir out_dir [--runs pages.json] [--cols 6] [--per-sheet 30] [--near 5] [--thresholds path]
// Env:   CHROME_PATH, PLAYWRIGHT_MODULE (as pdf_pages.mjs). PNGs are decoded in headless Chromium
//        (canvas), so no image library is needed. Never opens a window.
// Writes: out_dir/pixels.json (deck-pixels/1) and out_dir/contact-1.png ... contact-N.png.
// Exit:  0 ok; 1 no PNGs or a decode failure; 2 usage, Playwright or thresholds.json missing.
//
// Measurement parameters come from thresholds.json `measure` (rubric §1): lum_dark_max and
// lum_light_min (C4 classes; mid never counts as a flip), dup_hamming_max (T11 near-duplicates),
// per_sheet, ring_px (C1 background ring). Tile width = V6 thumb_scale x the 1280 px canvas, so the
// contact sheet doubles as the 25% thumbnail test of V6. The empty bottom band (G5) is scanned upward from
// above the footer band, G2 margin_pt high, so a page number or footer line does not end the scan.
// near_pairs lists the --near closest pairs above dup_hamming_max for the contact-sheet check (a display
// count, not a threshold).
import { createRequire } from 'node:module';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const USAGE = 'usage: node pixels.mjs png_dir out_dir [--runs pages.json] [--cols 6] [--per-sheet 30] [--near 5] [--thresholds path]';
const die = (msg, code) => { console.error(msg); process.exit(code); };

const argv = process.argv.slice(2);
if (argv.includes('-h') || argv.includes('--help')) { console.log(USAGE); process.exit(0); }
const opt = { runs: null, cols: 6, perSheet: null, near: 5, thresholds: null };
const pos = [];
for (let i = 0; i < argv.length; i++) {
  const a = argv[i];
  const val = () => { const v = argv[++i]; if (v === undefined || v.startsWith('--')) die(`${a} needs a value\n${USAGE}`, 2); return v; };
  if (a === '--runs') opt.runs = val();
  else if (a === '--cols') opt.cols = +val();
  else if (a === '--per-sheet') opt.perSheet = +val();
  else if (a === '--near') opt.near = +val();
  else if (a === '--thresholds') opt.thresholds = val();
  else if (a.startsWith('--')) die(`unknown option ${a}\n${USAGE}`, 2);
  else pos.push(a);
}
if (pos.length !== 2) die(USAGE, 2);
if (!(opt.cols >= 1 && opt.cols <= 20)) die(`--cols must be 1..20\n${USAGE}`, 2);
if (opt.perSheet !== null && !(opt.perSheet >= 1)) die(`--per-sheet must be a positive integer\n${USAGE}`, 2);
if (!(Number.isInteger(opt.near) && opt.near >= 0 && opt.near <= 50)) die(`--near must be an integer 0..50\n${USAGE}`, 2);
const [pngDir, outDir] = pos.map(p => path.resolve(p));
if (!fs.existsSync(pngDir) || !fs.statSync(pngDir).isDirectory()) die(`not a directory: ${pos[0]}\n${USAGE}`, 2);

const thrPath = opt.thresholds ? path.resolve(opt.thresholds) : fileURLToPath(new URL('./thresholds.json', import.meta.url));
let THR;
try { THR = JSON.parse(fs.readFileSync(thrPath, 'utf8')); } catch { die(`thresholds.json missing or unreadable: ${thrPath}`, 2); }
const M = THR.measure || {};
for (const k of ['lum_dark_max', 'lum_light_min', 'dup_hamming_max', 'per_sheet', 'ring_px'])
  if (typeof M[k] !== 'number') die(`thresholds.json measure.${k} missing: ${thrPath}`, 2);
const perSheet = opt.perSheet || M.per_sheet;
const canvasW = (THR.units && THR.units.canvas_px && THR.units.canvas_px[0]) || 1280;
const canvasHpt = (THR.units && THR.units.canvas_pt && THR.units.canvas_pt[1]) || 540;
const footerPt = THR.checks && THR.checks.G2 && THR.checks.G2.talk && THR.checks.G2.talk.margin_pt;
if (typeof footerPt !== 'number') die(`thresholds.json checks.G2.talk.margin_pt missing: ${thrPath}`, 2);
const thumb = THR.checks && THR.checks.V6 && THR.checks.V6.talk && THR.checks.V6.talk.thumb_scale;
const tileW = Math.round(canvasW * (thumb || 0.25));

let RUNS = null;
if (opt.runs) {
  try { RUNS = JSON.parse(fs.readFileSync(opt.runs, 'utf8')); } catch { die(`cannot read --runs ${opt.runs}`, 2); }
  if (Array.isArray(RUNS)) RUNS = { pages: RUNS.map(p => ({ ...p, n: p.n || p.page })) }; // legacy bare list
}

const files = fs.readdirSync(pngDir)
  .filter(f => /\.png$/i.test(f) && !/^contact-/i.test(f) && /\d+/.test(f))
  .map(f => ({ f, n: +(/(\d+)(?!.*\d)/.exec(f)[1]) }))
  .sort((a, b) => a.n - b.n);
if (!files.length) die(`no slide PNGs in ${pos[0]}`, 1);

async function loadPlaywright() {
  const require = createRequire(import.meta.url);
  const tries = [];
  if (process.env.PLAYWRIGHT_MODULE) tries.push(process.env.PLAYWRIGHT_MODULE);
  tries.push('playwright');
  for (const t of tries) {
    try { return require(t); } catch { /* next */ }
    try { const m = await import(t.includes('/') || t.includes(path.sep) ? pathToFileURL(t).href : t); return m.default || m; } catch { /* next */ }
  }
  die('Playwright not found: npm i -D playwright (then npx playwright install chromium), or set PLAYWRIGHT_MODULE.', 2);
}

// ---------- in-page analysis of one PNG
async function analyse({ dataUrl, runs, pagePt, ring, tileW, bandFrac }) {
  const img = new Image();
  img.src = dataUrl;
  await img.decode();
  const W = img.naturalWidth, H = img.naturalHeight;
  const ctxOf = (w, h) => { const c = document.createElement('canvas'); c.width = w; c.height = h; const x = c.getContext('2d', { willReadFrequently: true }); x.imageSmoothingEnabled = true; x.imageSmoothingQuality = 'high'; return [c, x]; };
  const lin = v => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
  const hex = (r, g, b) => '#' + [r, g, b].map(v => Math.round(v).toString(16).padStart(2, '0')).join('').toUpperCase();

  // luminance and background on a reduced copy
  const sw = 480, sh = Math.max(1, Math.round(H * sw / W));
  const [, sx] = ctxOf(sw, sh);
  sx.drawImage(img, 0, 0, sw, sh);
  const sd = sx.getImageData(0, 0, sw, sh).data;
  let lum = 0;
  const buckets = new Map();
  for (let i = 0; i < sd.length; i += 4) {
    lum += 0.2126 * lin(sd[i]) + 0.7152 * lin(sd[i + 1]) + 0.0722 * lin(sd[i + 2]);
    const k = (sd[i] >> 3) << 10 | (sd[i + 1] >> 3) << 5 | (sd[i + 2] >> 3);
    buckets.set(k, (buckets.get(k) || 0) + 1);
  }
  lum /= sd.length / 4;
  let bk = 0, bc = -1;
  for (const [k, c] of buckets) if (c > bc) { bk = k; bc = c; }
  const bgq = [(bk >> 10) << 3, ((bk >> 5) & 31) << 3, (bk & 31) << 3];
  const near = (i, ref, tol) => Math.abs(sd[i] - ref[0]) <= tol && Math.abs(sd[i + 1] - ref[1]) <= tol && Math.abs(sd[i + 2] - ref[2]) <= tol;
  const band = Math.min(sh - 1, Math.round(sh * bandFrac));
  let freeRows = band; // the footer band counts as empty: a page number or footer line is chrome, not content
  for (let y = sh - 1 - band; y >= 0; y--) {
    let ok = 0;
    for (let x = 0; x < sw; x++) if (near((y * sw + x) * 4, bgq, 14)) ok++;
    if (ok / sw < 0.98) break;
    freeRows++;
  }

  // 9x8 difference hash
  const [, mx] = ctxOf(72, 64);
  mx.drawImage(img, 0, 0, 72, 64);
  const [, hx] = ctxOf(9, 8);
  hx.drawImage(mx.canvas, 0, 0, 9, 8);
  const hd = hx.getImageData(0, 0, 9, 8).data;
  const grey = i => 0.299 * hd[i] + 0.587 * hd[i + 1] + 0.114 * hd[i + 2];
  let bits = '';
  for (let y = 0; y < 8; y++) for (let x = 0; x < 8; x++) bits += grey((y * 9 + x) * 4) > grey((y * 9 + x + 1) * 4) ? '1' : '0';
  let dhash = '';
  for (let i = 0; i < 64; i += 4) dhash += parseInt(bits.slice(i, i + 4), 2).toString(16);

  // tile for the contact sheet
  const th = Math.round(tileW * H / W);
  const [tc, tx] = ctxOf(tileW, th);
  tx.drawImage(img, 0, 0, tileW, th);
  const tile = tc.toDataURL('image/png');

  // background ring around each PDF run (y = baseline from the bottom, flipped here)
  const runBg = [];
  if (runs && runs.length && pagePt) {
    const [, fx] = ctxOf(W, H);
    fx.drawImage(img, 0, 0);
    const fd = fx.getImageData(0, 0, W, H).data;
    const k = W / pagePt[0];
    runs.forEach((r, i) => {
      const yb = (pagePt[1] - r.y) * k;
      const x0 = Math.floor(r.x * k) - 1, x1 = Math.ceil(r.x1 * k) + 1;
      const y0 = Math.floor(yb - r.size * 0.82 * k) - 1, y1 = Math.ceil(yb + r.size * 0.24 * k) + 1;
      if (x1 <= 0 || y1 <= 0 || x0 >= W || y0 >= H) { runBg.push({ i, bg: null, unknown: true, offcanvas: true }); return; }
      const counts = new Map(), sums = new Map();
      const add = (x, y) => {
        if (x < 0 || y < 0 || x >= W || y >= H) return;
        const o = (y * W + x) * 4, q = (fd[o] >> 3) << 10 | (fd[o + 1] >> 3) << 5 | (fd[o + 2] >> 3);
        counts.set(q, (counts.get(q) || 0) + 1);
        const s = sums.get(q) || [0, 0, 0]; s[0] += fd[o]; s[1] += fd[o + 1]; s[2] += fd[o + 2]; sums.set(q, s);
      };
      for (let d = 1; d <= ring; d++) {
        for (let x = x0 - d; x <= x1 + d; x++) { add(x, y0 - d); add(x, y1 + d); }
        for (let y = y0 - d; y <= y1 + d; y++) { add(x0 - d, y); add(x1 + d, y); }
      }
      let total = 0, best = 0, bq = 0;
      for (const [q, c] of counts) { total += c; if (c > best) { best = c; bq = q; } }
      if (!total) { runBg.push({ i, bg: null, unknown: true }); return; }
      const s = sums.get(bq);
      runBg.push({ i, bg: hex(s[0] / best, s[1] / best, s[2] / best), unknown: best / total < 0.6, share: Math.round(best / total * 100) / 100 });
    });
  }
  return { w: W, h: H, lum, bg: hex(...bgq.map(v => v + 4)), bottom_free: freeRows / sh, dhash, tile, tileH: th, runBg };
}

// ---------- in-page contact sheet
async function sheet({ tiles, cols, tileW, tileH }) {
  const gap = 10, band = 24, rows = Math.ceil(tiles.length / cols);
  const c = document.createElement('canvas');
  c.width = cols * tileW + (cols + 1) * gap;
  c.height = rows * (tileH + band) + (rows + 1) * gap;
  const x = c.getContext('2d');
  x.fillStyle = '#3A3A3A';
  x.fillRect(0, 0, c.width, c.height);
  x.textBaseline = 'middle';
  for (let i = 0; i < tiles.length; i++) {
    const t = tiles[i], img = new Image();
    img.src = t.tile;
    await img.decode();
    const px = gap + (i % cols) * (tileW + gap), py = gap + Math.floor(i / cols) * (tileH + band + gap);
    x.drawImage(img, px, py, tileW, tileH);
    if (t.dup) { x.strokeStyle = '#FF7A00'; x.lineWidth = 4; x.strokeRect(px + 2, py + 2, tileW - 4, tileH - 4); }
    x.fillStyle = '#FFFFFF';
    x.font = 'bold 17px sans-serif';
    x.fillText(String(t.n), px + 2, py + tileH + band / 2 + 1);
    x.font = '14px sans-serif';
    const lab = `${t.lum.toFixed(2)} ${t.cls}${t.dup ? '  ~' + t.dup : ''}`;
    x.fillText(lab, px + tileW - x.measureText(lab).width - 2, py + tileH + band / 2 + 1);
  }
  return c.toDataURL('image/png');
}

// ---------- main
const { chromium } = await loadPlaywright();
const exe = process.env.CHROME_PATH || '';
let browser;
try {
  browser = await chromium.launch({ ...(exe ? { executablePath: exe } : { channel: 'chromium' }), headless: true, args: ['--force-color-profile=srgb'] });
} catch (e) {
  die(`browser launch failed: ${String(e.message || e).split('\n')[0]}\nSet CHROME_PATH or run: npx playwright install chromium`, 2);
}
const page = await browser.newPage();
await page.setContent('<!doctype html><title>pixels</title>');
fs.mkdirSync(outDir, { recursive: true });
const rel = f => path.relative(outDir, path.join(pngDir, f)).split(path.sep).join('/');
const slides = [], runBg = [], tiles = [];
let failed = 0;
for (const { f, n } of files) {
  const dataUrl = 'data:image/png;base64,' + fs.readFileSync(path.join(pngDir, f)).toString('base64');
  let pg = null;
  if (RUNS) pg = (RUNS.pages || []).find(p => (p.n || p.page) === n) || null;
  const pagePt = pg ? (pg.size_pt || RUNS.page_pt || null) : null;
  let r;
  try {
    r = await page.evaluate(analyse, { dataUrl, runs: pg ? pg.runs : null, pagePt, ring: M.ring_px, tileW, bandFrac: footerPt / ((pagePt && pagePt[1]) || canvasHpt) });
  } catch (e) {
    console.error(`${f}: decode failed (${String(e.message || e).split('\n')[0]})`);
    failed++;
    continue;
  }
  const lum = Math.round(r.lum * 1000) / 1000;
  const cls = lum <= M.lum_dark_max ? 'dark' : lum >= M.lum_light_min ? 'light' : 'mid';
  slides.push({ n, png: rel(f), w_px: r.w, h_px: r.h, lum, class: cls, bg: r.bg, dhash: r.dhash, bottom_free: Math.round(r.bottom_free * 1000) / 1000 });
  for (const b of r.runBg) runBg.push({ n, ...b });
  tiles.push({ n, tile: r.tile, tileH: r.tileH, lum, cls });
}
if (!slides.length) { await browser.close(); die('no PNG could be decoded', 1); }

const ham = (a, b) => { let d = 0; for (let i = 0; i < 16; i++) { let x = parseInt(a[i], 16) ^ parseInt(b[i], 16); while (x) { d += x & 1; x >>= 1; } } return d; };
const dupPairs = [], above = [];
for (let i = 0; i < slides.length; i++) for (let j = i + 1; j < slides.length; j++) {
  const d = ham(slides[i].dhash, slides[j].dhash);
  if (d <= M.dup_hamming_max) dupPairs.push({ a: slides[i].n, b: slides[j].n, hamming: d });
  else above.push({ a: slides[i].n, b: slides[j].n, hamming: d });
}
const nearPairs = above.sort((p, q) => p.hamming - q.hamming || p.a - q.a || p.b - q.b).slice(0, opt.near);
const flips = [];
for (let i = 1; i < slides.length; i++) {
  const a = slides[i - 1], b = slides[i];
  if (a.class !== 'mid' && b.class !== 'mid' && a.class !== b.class) flips.push({ a: a.n, b: b.n, from: a.class, to: b.class });
}
const dupOf = new Map();
for (const p of dupPairs) { if (!dupOf.has(p.a)) dupOf.set(p.a, p.b); if (!dupOf.has(p.b)) dupOf.set(p.b, p.a); }

const sheets = [];
for (let s = 0; s * perSheet < tiles.length; s++) {
  const part = tiles.slice(s * perSheet, (s + 1) * perSheet).map(t => ({ ...t, dup: dupOf.get(t.n) || null }));
  const url = await page.evaluate(sheet, { tiles: part, cols: opt.cols, tileW, tileH: Math.max(...part.map(t => t.tileH)) });
  const name = `contact-${s + 1}.png`;
  fs.writeFileSync(path.join(outDir, name), Buffer.from(url.split(',')[1], 'base64'));
  sheets.push(name);
}
await browser.close();

const out = {
  schema: 'deck-pixels/1', tool: 'pixels.mjs', png_dir: path.relative(outDir, pngDir).split(path.sep).join('/') || '.',
  params: { lum_dark_max: M.lum_dark_max, lum_light_min: M.lum_light_min, dup_hamming_max: M.dup_hamming_max, ring_px: M.ring_px, tile_px: tileW,
    footer_band_pt: footerPt, near: opt.near },
  slides, flips, dup_pairs: dupPairs, near_pairs: nearPairs, sheets,
};
if (RUNS) out.run_bg = runBg;
fs.writeFileSync(path.join(outDir, 'pixels.json'), JSON.stringify(out, null, 1) + '\n');
const cls = c => slides.filter(s => s.class === c).length;
console.log(`${slides.length} slides: ${cls('light')} light, ${cls('mid')} mid, ${cls('dark')} dark; ${flips.length} flips; ${dupPairs.length} near-duplicate pairs; ${sheets.length} contact sheet(s) -> ${outDir}`);
process.exit(failed ? 1 : 0);
