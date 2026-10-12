// Render each PDF page to a page-exact PNG through Chromium's built-in PDF viewer (no poppler needed).
//
// Usage: node pdf_pages.mjs deck.pdf out_dir [from] [to] [--viewport 1640x940] [--no-crop]
// Env:   CHROME_PATH        full Chromium or Chrome binary (the headless SHELL has no PDF viewer);
//                           unset: Playwright's channel 'chromium' (the full build, new headless mode)
//        PLAYWRIGHT_MODULE  path or name of the playwright package when normal resolution fails
//        PDF_WAIT_MS        paint wait per page in ms (default 2500; the first page waits twice as long)
// Writes: out_dir/slide-NN.png (NN padded to 2 digits, 3 above 99) and out_dir/manifest.json (deck-pages/1).
// Exit:  0 ok; 1 render failed (blank after one retry, or no PDF viewer); 2 usage or Playwright missing.
//
// Practice (rubric lesson L76): navigate to about:blank between pages, open
// file:///deck.pdf#page=N&toolbar=0&navpanes=0&view=Fit, wait for the asynchronous paint, screenshot.
// A 1640x940 viewport gives about 1.7 px per pt. The page rectangle is found on the pixels and the
// capture is clipped to it, so the PNG holds the page and nothing of the viewer. Never opens a window.
import { createRequire } from 'node:module';
import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import zlib from 'node:zlib';

const USAGE = 'usage: node pdf_pages.mjs deck.pdf out_dir [from] [to] [--viewport 1640x940] [--no-crop]';
const die = (msg, code) => { console.error(msg); process.exit(code); };

// ---------- arguments
const argv = process.argv.slice(2);
if (argv.includes('-h') || argv.includes('--help')) { console.log(USAGE); process.exit(0); }
let viewport = { width: 1640, height: 940 };
let crop = true;
const pos = [];
for (let i = 0; i < argv.length; i++) {
  const a = argv[i];
  if (a === '--viewport') {
    const m = /^(\d{3,5})x(\d{3,5})$/.exec(argv[++i] || '');
    if (!m) die(`bad --viewport\n${USAGE}`, 2);
    viewport = { width: +m[1], height: +m[2] };
  } else if (a === '--no-crop') crop = false;
  else if (a.startsWith('--')) die(`unknown option ${a}\n${USAGE}`, 2);
  else pos.push(a);
}
if (pos.length < 2 || pos.length > 4) die(USAGE, 2);
const [pdfArg, outDir, fromArg, toArg] = pos;
for (const v of [fromArg, toArg]) if (v !== undefined && !/^\d+$/.test(v)) die(`page numbers must be integers\n${USAGE}`, 2);
const pdf = path.resolve(pdfArg);
if (!fs.existsSync(pdf) || !fs.statSync(pdf).isFile()) die(`not a file: ${pdfArg}\n${USAGE}`, 2);
const waitMs = Number(process.env.PDF_WAIT_MS || 2500);
if (!Number.isFinite(waitMs) || waitMs < 0) die('PDF_WAIT_MS must be a number of milliseconds', 2);

// ---------- Playwright (the only npm dependency)
async function loadPlaywright() {
  const require = createRequire(import.meta.url);
  const tries = [];
  if (process.env.PLAYWRIGHT_MODULE) tries.push(process.env.PLAYWRIGHT_MODULE);
  tries.push('playwright');
  for (const t of tries) {
    try { return require(t); } catch { /* next */ }
    try { const m = await import(t.includes(path.sep) || t.includes('/') ? pathToFileURL(t).href : t); return m.default || m; } catch { /* next */ }
  }
  die('Playwright not found. Install it next to the scripts or globally: npm i -D playwright\n' +
      'then npx playwright install chromium, or set PLAYWRIGHT_MODULE to the package path.', 2);
}

// ---------- PDF facts from the file itself
const bytes = fs.readFileSync(pdf).toString('latin1');
function pageCount() {
  const counts = [];
  for (const m of bytes.matchAll(/\/Type\s*\/Pages\b/g)) {
    const a = bytes.lastIndexOf('<<', m.index), b = bytes.indexOf('>>', m.index);
    const c = a >= 0 && b > 0 ? /\/Count\s+(\d+)/.exec(bytes.slice(a, b)) : null;
    if (c) counts.push(+c[1]);
  }
  if (counts.length) return Math.max(...counts);
  const leaves = bytes.match(/\/Type\s*\/Page(?![s\w])/g);
  return leaves ? leaves.length : 0;
}
function pageSize() {
  const m = /\/MediaBox\s*\[\s*([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\s*\]/.exec(bytes);
  if (!m) return null;
  const w = Math.abs(+m[3] - +m[1]), h = Math.abs(+m[4] - +m[2]);
  return w > 0 && h > 0 ? [Math.round(w * 100) / 100, Math.round(h * 100) / 100] : null;
}
const found = pageCount();
const from = fromArg ? +fromArg : 1;
const total = toArg ? +toArg : found;
if (!total) die('page count not found (compressed page tree): pass [from] [to]', 2);
if (from < 1 || from > total) die(`bad page range ${from}..${total}`, 2);
const pagePt = pageSize();

// ---------- minimal PNG decoder (8-bit, non-interlaced; what Chromium screenshots produce)
function decodePng(buf) {
  let p = 8, w = 0, h = 0, bd = 0, ct = 0, il = 0;
  const idat = [];
  while (p < buf.length) {
    const len = buf.readUInt32BE(p), type = buf.toString('latin1', p + 4, p + 8);
    const chunk = buf.subarray(p + 8, p + 8 + len);
    p += 12 + len;
    if (type === 'IHDR') { w = chunk.readUInt32BE(0); h = chunk.readUInt32BE(4); bd = chunk[8]; ct = chunk[9]; il = chunk[12]; }
    else if (type === 'IDAT') idat.push(chunk);
    else if (type === 'IEND') break;
  }
  const bpp = { 0: 1, 2: 3, 4: 2, 6: 4 }[ct];
  if (bd !== 8 || il !== 0 || !bpp) throw new Error('unsupported PNG layout');
  const raw = zlib.inflateSync(Buffer.concat(idat));
  const stride = w * bpp, out = Buffer.alloc(h * stride);
  let i = 0;
  for (let y = 0; y < h; y++) {
    const f = raw[i++], row = y * stride, prev = row - stride;
    for (let x = 0; x < stride; x++) {
      const a = x >= bpp ? out[row + x - bpp] : 0;
      const b = y > 0 ? out[prev + x] : 0;
      const c = x >= bpp && y > 0 ? out[prev + x - bpp] : 0;
      let v = raw[i++];
      if (f === 1) v += a;
      else if (f === 2) v += b;
      else if (f === 3) v += (a + b) >> 1;
      else if (f === 4) { const q = a + b - c, pa = Math.abs(q - a), pb = Math.abs(q - b), pc = Math.abs(q - c); v += pa <= pb && pa <= pc ? a : pb <= pc ? b : c; }
      out[row + x] = v & 255;
    }
  }
  const px = (x, y) => { const o = y * stride + x * bpp; return bpp >= 3 ? [out[o], out[o + 1], out[o + 2]] : [out[o], out[o], out[o]]; };
  return { w, h, bpp, ct, data: out, px };
}

// ---------- minimal PNG encoder for the cropped page (filter 0, same colour type)
const CRC = new Int32Array(256).map((_, n) => { let c = n; for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1; return c; });
const crc32 = b => { let c = -1; for (let i = 0; i < b.length; i++) c = CRC[(c ^ b[i]) & 255] ^ (c >>> 8); return (c ^ -1) >>> 0; };
function chunk(type, data) {
  const len = Buffer.alloc(4); len.writeUInt32BE(data.length);
  const td = Buffer.concat([Buffer.from(type, 'latin1'), data]);
  const crc = Buffer.alloc(4); crc.writeUInt32BE(crc32(td));
  return Buffer.concat([len, td, crc]);
}
function encodeCrop(img, box) {
  const { bpp, data } = img, stride = img.w * bpp, rowLen = box.width * bpp;
  const raw = Buffer.alloc(box.height * (rowLen + 1));
  for (let y = 0; y < box.height; y++) {
    const src = (box.y + y) * stride + box.x * bpp;
    data.copy(raw, y * (rowLen + 1) + 1, src, src + rowLen);
  }
  const ihdr = Buffer.alloc(13);
  ihdr.writeUInt32BE(box.width, 0); ihdr.writeUInt32BE(box.height, 4); ihdr[8] = 8; ihdr[9] = img.ct;
  return Buffer.concat([Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]), chunk('IHDR', ihdr),
    chunk('IDAT', zlib.deflateSync(raw, { level: 6 })), chunk('IEND', Buffer.alloc(0))]);
}

// Viewer chrome is a neutral dark grey with a soft shadow gradient; the page edge is the first pixel
// that is not neutral dark grey or that jumps away from the gradient.
const viewerish = ([r, g, b]) => Math.max(r, g, b) - Math.min(r, g, b) <= 8 && Math.max(r, g, b) <= 100;
const jump = (p, q) => Math.max(Math.abs(p[0] - q[0]), Math.abs(p[1] - q[1]), Math.abs(p[2] - q[2])) > 6;
function edge(img, fixed, horizontal, reverse) {
  const n = horizontal ? img.w : img.h;
  const at = k => (horizontal ? img.px(k, fixed) : img.px(fixed, k));
  let prev = at(reverse ? n - 1 : 0);
  if (!viewerish(prev)) return reverse ? n : 0;
  for (let s = 1; s < n / 2; s++) {
    const k = reverse ? n - 1 - s : s, cur = at(k);
    if (!viewerish(cur) || jump(cur, prev)) return reverse ? k + 1 : k;
    prev = cur;
  }
  return null;
}
const median = a => a.slice().sort((x, y) => x - y)[Math.floor(a.length / 2)];
function pageBox(img) {
  const rows = [0.3, 0.5, 0.7].map(f => Math.floor(img.h * f));
  const L = rows.map(y => edge(img, y, true, false)), R = rows.map(y => edge(img, y, true, true));
  const T = edge(img, Math.floor(img.w / 2), false, false);
  if (L.includes(null) || R.includes(null) || T === null) return null;
  const left = median(L), right = median(R), top = T;
  const width = right - left;
  if (width < img.w / 3) return null;
  let height;
  if (pagePt) height = Math.round(width * pagePt[1] / pagePt[0]);
  else {
    const B = edge(img, Math.floor(img.w / 2), false, true);
    height = B === null ? img.h - top : B - top;
  }
  height = Math.min(height, img.h - top);
  return { x: left, y: top, width, height };
}
function isBlank(img) {
  const first = img.px(0, 0);
  for (let y = 0; y < img.h; y += 7) for (let x = 0; x < img.w; x += 7) if (jump(img.px(x, y), first)) return false;
  return true;
}

// ---------- render
const exe = process.env.CHROME_PATH || '';
if (/headless[_-]shell/i.test(exe)) die('CHROME_PATH points to the headless shell, which has no PDF viewer: use full Chromium or Chrome', 1);
const { chromium } = await loadPlaywright();
fs.mkdirSync(outDir, { recursive: true });
const launch = exe ? { executablePath: exe } : { channel: 'chromium' };
let browser;
try {
  browser = await chromium.launch({ ...launch, headless: true, args: ['--force-color-profile=srgb', '--hide-scrollbars'] });
} catch (e) {
  die(`browser launch failed: ${String(e.message || e).split('\n')[0]}\nSet CHROME_PATH to a full Chromium or Chrome, or run: npx playwright install chromium`, 2);
}
const page = await browser.newPage({ viewport, deviceScaleFactor: 1 });
const url = pathToFileURL(pdf).href;
const digits = Math.max(2, String(total).length);
const files = [], failed = [];
let lastBox = null, pxPerPt = null;

async function capture(n, wait) {
  await page.goto('about:blank');
  let navError = '';
  try { await page.goto(`${url}#page=${n}&toolbar=0&navpanes=0&view=Fit`, { timeout: 30000 }); }
  catch (e) { navError = String(e.message || e); }
  if (/download/i.test(navError)) return { noViewer: true };
  await page.waitForTimeout(wait);
  let shot = await page.screenshot();
  for (let k = 0; k < 3; k++) { // wait until two captures agree (progressive tiles)
    await page.waitForTimeout(300);
    const again = await page.screenshot();
    if (again.equals(shot)) break;
    shot = again;
  }
  return { img: decodePng(shot), shot };
}

for (let n = from; n <= total; n++) {
  let r = await capture(n, n === from ? 2 * waitMs : waitMs);
  if (r.noViewer) { await browser.close(); die('the browser downloaded the PDF instead of showing it: no PDF viewer (headless shell?). Use full Chromium or Chrome.', 1); }
  if (isBlank(r.img)) r = await capture(n, 2 * waitMs); // one retry
  if (isBlank(r.img)) { failed.push(n); console.error(`page ${n}: blank capture after one retry`); continue; }
  let box = crop ? pageBox(r.img) : null;
  if (crop && box && pagePt && Math.abs(box.width / box.height - pagePt[0] / pagePt[1]) > 0.02) box = null;
  if (crop && !box) box = lastBox;
  if (crop && !box) console.error(`page ${n}: page rectangle not found, kept the full viewport`);
  if (box) lastBox = box;
  const file = `slide-${String(n).padStart(digits, '0')}.png`;
  fs.writeFileSync(path.join(outDir, file), box ? encodeCrop(r.img, box) : r.shot);
  if (box && pagePt && !pxPerPt) pxPerPt = Math.round((box.width / pagePt[0]) * 1000) / 1000;
  files.push(file);
  console.log(file);
}
await browser.close();

const manifest = {
  schema: 'deck-pages/1', tool: 'pdf_pages.mjs', source: path.basename(pdf), pages: found || total,
  rendered: files.length, from, to: total, page_pt: pagePt, px_per_pt: pxPerPt,
  viewport: [viewport.width, viewport.height], cropped: crop && !!lastBox, files, failed,
};
fs.writeFileSync(path.join(outDir, 'manifest.json'), JSON.stringify(manifest, null, 1) + '\n');
console.log(`${files.length} of ${total - from + 1} pages -> ${outDir}`);
process.exit(failed.length ? 1 : 0);
