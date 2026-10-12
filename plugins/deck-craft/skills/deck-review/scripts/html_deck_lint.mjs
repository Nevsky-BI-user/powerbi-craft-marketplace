// Render an HTML deck slide by slide and measure it in the page. Measures only: deck_lint.py judges.
//
// Usage: node html_deck_lint.mjs deck.html out_dir [--fonts native|metric|both] [--slide-selector .slide]
//          [--active-class on] [--next-key ArrowRight] [--viewports default|WxH,...] [--theme light|dark]
//          [--no-print] [--no-presenter] [--thresholds path]
// Env:   CHROME_PATH, PLAYWRIGHT_MODULE (see pdf_pages.mjs). Headless only; never opens a window.
// Writes: out_dir/metrics.json (deck-metrics/1), out_dir/png/slide-NN.png, out_dir/png-metric/ (metric
//         font pass), out_dir/print.pdf (print emulation).
// Exit:  0 measured (findings are the judge's job); 1 deck failed to load, no slides found or navigation
//        stuck; 2 usage, Playwright or thresholds.json missing.
//
// Navigation: a deck exposing window.deck (html-deck engine contract) is driven with deck.go(i) after
// deck.ready, then two animation frames. Any other deck: --slide-selector (default .slide) and
// --active-class (default on); the script presses Home, then --next-key per slide, and waits until the
// active slide changes. Units: design px on the slide canvas (client rects divided by the track scale k),
// so a 1280x720 deck measures the same in any viewport. Screenshots are taken at device scale 1/k, which
// gives one PNG pixel per design px. Font modes: native (whatever this machine resolves) and metric
// (every declared family mapped to Liberation Sans or Mono, Arial and Courier metrics): text that
// reflows between the two is what moves on the presenter's machine (check H3).
import { createRequire } from 'node:module';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const USAGE = 'usage: node html_deck_lint.mjs deck.html out_dir [--fonts native|metric|both] [--slide-selector .slide]\n' +
  '         [--active-class on] [--next-key ArrowRight] [--viewports default|WxH,...] [--theme light|dark]\n' +
  '         [--no-print] [--no-presenter] [--thresholds path]';
const die = (msg, code) => { console.error(msg); process.exit(code); };

// ---------- arguments
const argv = process.argv.slice(2);
if (argv.includes('-h') || argv.includes('--help')) { console.log(USAGE); process.exit(0); }
const opt = { fonts: 'both', sel: '.slide', active: 'on', next: 'ArrowRight', viewports: 'default', theme: 'light', print: true, presenter: true, thresholds: null };
const pos = [];
for (let i = 0; i < argv.length; i++) {
  const a = argv[i];
  const val = () => { const v = argv[++i]; if (v === undefined || (v.startsWith('--') && v.length > 2)) die(`${a} needs a value\n${USAGE}`, 2); return v; };
  if (a === '--fonts') opt.fonts = val();
  else if (a === '--slide-selector') opt.sel = val();
  else if (a === '--active-class') opt.active = val();
  else if (a === '--next-key') opt.next = val();
  else if (a === '--viewports') opt.viewports = val();
  else if (a === '--theme') opt.theme = val();
  else if (a === '--thresholds') opt.thresholds = val();
  else if (a === '--no-print') opt.print = false;
  else if (a === '--no-presenter') opt.presenter = false;
  else if (a.startsWith('--')) die(`unknown option ${a}\n${USAGE}`, 2);
  else pos.push(a);
}
if (pos.length !== 2) die(USAGE, 2);
if (!['native', 'metric', 'both'].includes(opt.fonts)) die(`--fonts must be native, metric or both\n${USAGE}`, 2);
if (!['light', 'dark'].includes(opt.theme)) die(`--theme must be light or dark\n${USAGE}`, 2);
const deckPath = path.resolve(pos[0]), outDir = path.resolve(pos[1]);
if (!fs.existsSync(deckPath) || !fs.statSync(deckPath).isFile()) die(`not a file: ${pos[0]}\n${USAGE}`, 2);

const thrPath = opt.thresholds ? path.resolve(opt.thresholds) : fileURLToPath(new URL('./thresholds.json', import.meta.url));
let THR;
try { THR = JSON.parse(fs.readFileSync(thrPath, 'utf8')); } catch { die(`thresholds.json missing or unreadable: ${thrPath}`, 2); }
let viewports;
if (opt.viewports === 'default') viewports = (THR.checks && THR.checks.H1 && THR.checks.H1.talk && THR.checks.H1.talk.viewports) || [];
else {
  viewports = opt.viewports.split(',').map(s => /^(\d{3,5})x(\d{3,5})$/.exec(s.trim()));
  if (viewports.some(m => !m)) die(`bad --viewports (WxH,WxH)\n${USAGE}`, 2);
  viewports = viewports.map(m => [+m[1], +m[2]]);
}
const VIEW = { width: 1600, height: 900 };

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

// =====================================================================================================
// In-page code. Everything below up to the Node section runs inside the deck page via page.evaluate.
// =====================================================================================================
function MEASURE({ sel, index, total, contract }) {
  const slides = [...document.querySelectorAll(sel)];
  const S = slides[index];
  const sr = S.getBoundingClientRect();
  const W = S.offsetWidth || 1280, H = S.offsetHeight || 720;
  const k = sr.width / W || 1;
  const r1 = v => Math.round(v * 10) / 10;
  const R = r => [r1((r.left - sr.left) / k), r1((r.top - sr.top) / k), r1(r.width / k), r1(r.height / k)];
  const scs = getComputedStyle(S);
  const pad = { t: parseFloat(scs.paddingTop) || 0, r: parseFloat(scs.paddingRight) || 0, b: parseFloat(scs.paddingBottom) || 0, l: parseFloat(scs.paddingLeft) || 0 };

  // ---- colour helpers
  const c2d = document.createElement('canvas').getContext('2d');
  const parseColor = str => {
    if (!str || str === 'none' || str === 'transparent') return [0, 0, 0, 0];
    let m = /^rgba?\(([^)]+)\)/.exec(str);
    if (m) {
      const p = m[1].split(/[\s,/]+/).filter(Boolean).map(v => (v.endsWith('%') ? parseFloat(v) / 100 : parseFloat(v)));
      return [p[0], p[1], p[2], p.length > 3 ? p[3] : 1];
    }
    m = /^color\(srgb\s+([-\d.e]+)\s+([-\d.e]+)\s+([-\d.e]+)(?:\s*\/\s*([-\d.e]+%?))?\)/.exec(str);
    if (m) return [m[1] * 255, m[2] * 255, m[3] * 255, m[4] === undefined ? 1 : parseFloat(m[4]) / (m[4].endsWith('%') ? 100 : 1)];
    c2d.fillStyle = '#000'; c2d.fillStyle = str;
    const f = c2d.fillStyle;
    if (f.startsWith('#')) return [parseInt(f.slice(1, 3), 16), parseInt(f.slice(3, 5), 16), parseInt(f.slice(5, 7), 16), 1];
    m = /^rgba?\(([^)]+)\)/.exec(f);
    if (m) { const p = m[1].split(/[\s,/]+/).map(parseFloat); return [p[0], p[1], p[2], p.length > 3 ? p[3] : 1]; }
    return [0, 0, 0, 0];
  };
  const hex = c => (c ? '#' + c.slice(0, 3).map(v => Math.max(0, Math.min(255, Math.round(v))).toString(16).padStart(2, '0')).join('').toUpperCase() : null);
  const lin = v => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
  const lum = c => 0.2126 * lin(c[0]) + 0.7152 * lin(c[1]) + 0.0722 * lin(c[2]);
  const ratio = (a, b) => { const x = lum(a), y = lum(b); return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05); };
  const mix = (fg, bg, a) => [0, 1, 2].map(i => fg[i] * a + bg[i] * (1 - a));
  const stopsOf = s => (String(s).match(/rgba?\([^)]+\)|#[0-9a-f]{3,8}\b|color\(srgb[^)]+\)/gi) || []).map(parseColor).filter(c => c[3] > 0).map(hex);
  const svgStops = f => {
    const id = /url\(["']?#([^"')]+)/.exec(f);
    const g = id && document.getElementById(id[1]);
    return g ? [...g.querySelectorAll('stop')].map(st => hex(parseColor(getComputedStyle(st).stopColor))) : [];
  };

  // ---- visibility and selectors
  const visCache = new Map();
  const isVis = el => {
    if (!el || !(el instanceof Element)) return false;
    if (visCache.has(el)) return visCache.get(el);
    let ok = true;
    for (let e = el; e && e !== S.parentElement; e = e.parentElement) {
      const c = getComputedStyle(e);
      if (c.display === 'none' || c.visibility === 'hidden' || c.visibility === 'collapse' || parseFloat(c.opacity) === 0) { ok = false; break; }
    }
    if (ok && !el.getClientRects().length) ok = false;
    visCache.set(el, ok);
    return ok;
  };
  const selOf = el => {
    const parts = [];
    for (let e = el, d = 0; e && e !== S && d < 3; e = e.parentElement, d++) {
      const cls = (e.getAttribute('class') || '').trim().split(/\s+/).filter(Boolean)[0];
      let s = e.tagName.toLowerCase() + (cls ? '.' + cls : '');
      const sib = e.parentElement ? [...e.parentElement.children].filter(x => x.tagName === e.tagName) : [];
      if (sib.length > 1) s += `:nth-of-type(${sib.indexOf(e) + 1})`;
      parts.unshift(s);
    }
    return parts.join(' > ');
  };
  const opacityChain = el => { let o = 1; for (let e = el; e && e !== S.parentElement; e = e.parentElement) o *= parseFloat(getComputedStyle(e).opacity) || 1; return o; };
  const clipText = el => { const c = getComputedStyle(el); return (c.webkitBackgroundClip || c.backgroundClip) === 'text'; };

  // ---- backgrounds
  const ownBg = e => {
    if (!(e instanceof Element)) return null;
    const t = e.tagName.toLowerCase();
    if (['img', 'video', 'canvas', 'image', 'iframe', 'object', 'embed'].includes(t)) return { kind: 'image' };
    const c = getComputedStyle(e);
    if (e instanceof SVGElement && t !== 'svg') {
      if (!['rect', 'circle', 'ellipse', 'path', 'polygon', 'polyline'].includes(t)) return null;
      const f = c.fill;
      if (!f || f === 'none') return null;
      if (f.startsWith('url(')) return { kind: 'gradient', stops: svgStops(f) };
      const col = parseColor(f), a = col[3] * (parseFloat(c.fillOpacity) || 1) * (parseFloat(c.opacity) || 1);
      return a > 0.01 ? { kind: 'solid', rgba: [col[0], col[1], col[2], a] } : null;
    }
    if (clipText(e)) return null; // its background is the text fill
    const bi = c.backgroundImage;
    if (bi && bi !== 'none') {
      if (/gradient\(/.test(bi)) return { kind: 'gradient', stops: stopsOf(bi) };
      if (/url\(/.test(bi)) return { kind: 'image' };
    }
    const col = parseColor(c.backgroundColor);
    return col[3] > 0.01 ? { kind: 'solid', rgba: col } : null;
  };
  const chainBg = el => {
    const layers = [];
    for (let e = el; e; e = e.parentElement) {
      const b = ownBg(e);
      if (!b) continue;
      if (b.kind !== 'solid') return { kind: b.kind, color: null, stops: b.stops || null };
      layers.push(b.rgba);
      if (b.rgba[3] >= 0.99) break;
    }
    let base = [255, 255, 255];
    for (let j = layers.length - 1; j >= 0; j--) base = mix(layers[j], base, layers[j][3]);
    return { kind: 'solid', color: base };
  };
  const resolveBg = (el, x, y) => {
    let stack = [];
    if (x !== undefined && x >= 0 && y >= 0 && x <= innerWidth && y <= innerHeight) stack = document.elementsFromPoint(x, y);
    const i = stack.findIndex(e => e === el || e.contains(el));
    if (i < 0) return chainBg(el);
    const layers = [];
    for (const e of stack.slice(i)) {
      const b = ownBg(e);
      if (!b) continue;
      if (b.kind !== 'solid') return { kind: b.kind, color: null, stops: b.stops || null };
      layers.push(b.rgba);
      if (b.rgba[3] >= 0.99) break;
    }
    let base = [255, 255, 255];
    for (let j = layers.length - 1; j >= 0; j--) base = mix(layers[j], base, layers[j][3]);
    return { kind: 'solid', color: base };
  };

  // ---- sizes
  const effSize = el => {
    const fs = parseFloat(getComputedStyle(el).fontSize) || 0;
    if (el instanceof SVGElement && el.getScreenCTM) {
      const m = el.getScreenCTM();
      return m ? fs * Math.sqrt(m.a * m.a + m.b * m.b) / k : fs;
    }
    for (let e = el; e && e !== S; e = e.parentElement) {
      if (getComputedStyle(e).transform !== 'none') {
        let blk = el;
        while (blk && !blk.offsetWidth) blk = blk.parentElement;
        return blk && blk.offsetWidth ? fs * (blk.getBoundingClientRect().width / k) / blk.offsetWidth : fs;
      }
    }
    return fs;
  };
  const MONO = /mono|code|courier|consolas|cascadia|menlo/i;
  const familyOf = el => { const f = getComputedStyle(el).fontFamily || ''; return f.split(',')[0].replace(/["']/g, '').trim(); };
  const isMono = el => { const f = getComputedStyle(el).fontFamily || ''; return /\bmonospace\b/.test(f) || MONO.test(f.split(',')[0]); };
  const tokens = t => t.split(/\s+/).filter(w => /[\p{L}\p{N}]/u.test(w)); // \s includes NBSP: words split there, text keeps it (T9)
  const rng = document.createRange();
  const nodeRects = nodes => { const out = []; for (const n of nodes) { rng.selectNodeContents(n); out.push(...rng.getClientRects()); } return out.filter(r => r.width > 0 && r.height > 0); };
  const union = rects => {
    if (!rects.length) return null;
    const l = Math.min(...rects.map(r => r.left)), t = Math.min(...rects.map(r => r.top));
    const rr = Math.max(...rects.map(r => r.right)), b = Math.max(...rects.map(r => r.bottom));
    return { left: l, top: t, right: rr, bottom: b, width: rr - l, height: b - t };
  };
  const lineCount = (rects, size) => {
    const tops = rects.map(r => (r.top + r.bottom) / 2 / k).sort((a, b) => a - b);
    let n = 0, last = -1e9;
    for (const t of tops) if (t - last > Math.max(2, size * 0.5)) { n++; last = t; }
    return n;
  };

  // ---- roles (contract §5; first match wins)
  const titleEl = (() => { const t = S.querySelector('.t'); if (t && isVis(t)) return t; return [...S.querySelectorAll('h1, h2')].find(isVis) || null; })();
  const pnRe = /^\s*0*(\d{1,3})(?:\s*(?:\/|з|of|·)\s*\d{1,3})?\s*$/;
  const pnEl = (() => {
    for (const e of S.querySelectorAll('.pn, [data-role="pn"], .num, .page-num, .page-number, .slide-num, .slide-number'))
      if (isVis(e) && pnRe.test(e.textContent || '')) return e;
    for (const e of S.querySelectorAll('*')) {
      if (e.children.length || !isVis(e)) continue;
      const m = pnRe.exec(e.textContent || '');
      if (!m || +m[1] !== index + 1) continue;
      const b = R(e.getBoundingClientRect());
      if (b[0] < 120 || b[1] < 80 || b[0] + b[2] > W - 120 || b[1] + b[3] > H - 80) return e;
    }
    return null;
  })();
  const ROLES = [['footer', '.pn, .foot, footer, [data-role="footer"]'], ['eyebrow', '.eyebrow'], ['title', '.t'],
    ['hero', '.stat .v, [data-role="hero"]'], ['code', 'pre, code, kbd, .term'],
    ['label', 'svg text, th, td, figcaption, .label, .cap, .tag, .pill, .legend, .callout, [data-role="label"]']];
  const roleOf = el => {
    if (pnEl && (el === pnEl || pnEl.contains(el))) return 'footer';
    for (const [role, s] of ROLES) { const c = el.closest(s); if (c && S.contains(c)) return role; }
    if (titleEl && titleEl.contains(el)) return 'title';
    return 'body';
  };
  const EXCL = 'aside.notes, .notes, .copy, #bar, [data-chrome], [aria-hidden="true"], script, style, template, noscript, title, desc';
  const excluded = el => !!el.closest(EXCL) || (pnEl && (el === pnEl || pnEl.contains(el)));

  // ---- text owners
  const texts = [], textEls = [];
  const words_by_role = { body: 0, label: 0, title: 0, eyebrow: 0, code: 0, hero: 0, footer: 0 };
  let words = 0;
  const contentRects = [], contentEls = [];
  const cx0 = pad.l, cx1 = W - pad.r;
  const inColumns = b => !(b[0] + b[2] < cx0 || b[0] > cx1);
  const all = [S, ...S.querySelectorAll('*')];
  for (const el of all) {
    const nodes = [...el.childNodes].filter(n => n.nodeType === 3 && n.nodeValue.trim());
    if (!nodes.length) continue;
    if (el.closest('script, style, template, noscript, title, desc')) continue;
    if (!isVis(el)) continue;
    const rects = nodeRects(nodes);
    if (!rects.length) continue;
    const text = nodes.map(n => n.nodeValue).join(' ').replace(/[ \t\n\r\f\v]+/g, ' ').trim();
    const w = tokens(text).length;
    const role = roleOf(el);
    const ex = excluded(el);
    if (!ex) { words += w; words_by_role[role] = (words_by_role[role] || 0) + w; }
    const u = union(rects), box = R(u), size = effSize(el);
    const c = getComputedStyle(el);
    const svg = el instanceof SVGElement;
    const cxy = [u.left + u.width / 2, u.top + Math.min(u.height, size * k) / 2];
    const bg = resolveBg(el, cxy[0], cxy[1]);
    let gradient = null, color = null;
    const ct = clipText(el) ? el : null;
    if (ct) gradient = stopsOf(c.backgroundImage);
    else if (svg && (c.fill || '').startsWith('url(')) gradient = svgStops(c.fill);
    else {
      const fc = parseColor(svg ? c.fill : (c.webkitTextFillColor && c.webkitTextFillColor !== c.color ? c.webkitTextFillColor : c.color));
      const a = fc[3] * (svg ? parseFloat(c.fillOpacity) || 1 : 1) * opacityChain(el);
      if (bg.color) color = hex(mix(fc, bg.color, a));
      else color = hex(fc);
    }
    // block lines and measure
    let lines = lineCount(rects, size), cpl = null;
    if (!svg && /^(block|list-item|table-cell|flow-root|flex|grid)$/.test(c.display)) {
      rng.selectNodeContents(el);
      const all2 = [...rng.getClientRects()].filter(r => r.width > 0 && r.height > 0);
      lines = Math.max(lines, lineCount(all2, size));
      const chars = (el.textContent || '').replace(/[ \t\n\r\f\v]+/g, ' ').trim().length;
      cpl = lines ? Math.round(chars / lines) : null;
    }
    const entry = {
      role, sel: selOf(el), text: text.slice(0, 120), words: w, box, size_px: r1(size), weight: +c.fontWeight || 400,
      italic: c.fontStyle !== 'normal', underline: /underline/.test(c.textDecorationLine || ''), color, bg: hex(bg.color),
      bg_kind: bg.kind, lines, chars_per_line: cpl, align: c.textAlign === 'start' ? 'left' : c.textAlign === 'end' ? 'right' : c.textAlign,
      transform: c.textTransform, family: familyOf(el), mono: isMono(el), gradient, clip_text: !!ct, in_shape: !!el.closest('[data-shape]'),
    };
    if (ex) entry.excluded = true;
    texts.push(entry);
    textEls.push(el);
    if (!ex && role !== 'footer' && inColumns(box)) { contentRects.push(box); contentEls.push(el); }
  }

  // ---- media and content bottom
  const images = [];
  for (const e of S.querySelectorAll('img, video')) {
    if (!isVis(e) || excluded(e)) continue;
    const b = R(e.getBoundingClientRect());
    const nw = e.naturalWidth || e.videoWidth || 0, nh = e.naturalHeight || e.videoHeight || 0;
    const native = +e.dataset.nativeWidth || nw || null;
    const ui = e.dataset.uiPx ? +e.dataset.uiPx : null;
    const fit = getComputedStyle(e).objectFit;
    let dw = b[2], dh = b[3];
    if (fit === 'contain' && nw && nh) { const s = Math.min(b[2] / nw, b[3] / nh); dw = nw * s; dh = nh * s; }
    const p = e.parentElement, pc = p ? getComputedStyle(p) : null;
    let fills = null;
    if (p) {
      const iw = p.clientWidth - parseFloat(pc.paddingLeft) - parseFloat(pc.paddingRight);
      const ih = p.clientHeight - parseFloat(pc.paddingTop) - parseFloat(pc.paddingBottom);
      fills = Math.abs(b[2] - iw) <= 2.67 || Math.abs(b[3] - ih) <= 2.67;
    }
    const fig = e.closest('figure') || p;
    const callouts = fig ? [...fig.querySelectorAll('.callout')].filter(isVis).map(cn => ({ size_px: r1(effSize(cn)), words: tokens(cn.textContent || '').length, box: R(cn.getBoundingClientRect()) })) : [];
    const highlights = fig ? [...fig.querySelectorAll('.hl')].filter(isVis).map(h => {
      const hc = getComputedStyle(h), hb = R(h.getBoundingClientRect());
      let sw, col;
      if (h instanceof SVGElement) { // SVG overlay: stroke, scaled unless vector-effect keeps it in screen px
        const m = h.getScreenCTM(), w0 = parseFloat(hc.strokeWidth) || 0;
        sw = hc.vectorEffect === 'non-scaling-stroke' || !m ? w0 : w0 * Math.sqrt(m.a * m.a + m.b * m.b) / k;
        col = hex(parseColor(hc.stroke));
      } else {
        sw = Math.max(parseFloat(hc.borderTopWidth) || 0, parseFloat(hc.outlineWidth) || 0);
        col = hex(parseColor(parseFloat(hc.borderTopWidth) ? hc.borderTopColor : hc.outlineColor));
      }
      return { stroke_px: r1(sw), area_ratio: b[2] * b[3] ? Math.round(hb[2] * hb[3] / (b[2] * b[3]) * 1000) / 1000 : null, color: col };
    }) : [];
    // an <img> that finished loading with no pixels failed (broken source): P1, the slide is not rendered as built
    const broken = e.tagName === 'IMG' ? (e.complete ? !e.naturalWidth : null) : false;
    images.push({ sel: selOf(e), box: b, natural_w: nw || null, broken, native_width: native, ui_px: ui, eff_px: ui && native ? r1(ui * b[2] / native) : null,
      object_fit: fit, letterbox_px: r1(Math.max(b[2] - dw, b[3] - dh)), fills_zone: fills, shot: !!(ui || e.closest('figure.shot, .shot')), callouts, highlights });
    const db = [b[0] + (b[2] - dw) / 2, b[1] + (b[3] - dh) / 2, dw, dh];
    if (inColumns(db)) { contentRects.push(db); contentEls.push(e); }
  }
  const svgs = [];
  for (const sv of S.querySelectorAll('svg')) {
    if (sv.ownerSVGElement || !isVis(sv) || excluded(sv)) continue;
    const b = R(sv.getBoundingClientRect());
    const vb = sv.viewBox && sv.viewBox.baseVal && sv.viewBox.baseVal.width ? sv.viewBox.baseVal : null;
    let content = b, lb = 0, lbr = 0;
    if (vb && sv.preserveAspectRatio.baseVal.align !== 1) {
      const s = Math.min(b[2] / vb.width, b[3] / vb.height), cw = vb.width * s, ch = vb.height * s;
      const al = sv.preserveAspectRatio.baseVal.align; // 6 = xMidYMid
      const fx = [2, 5, 8].includes(al) ? 0 : [4, 7, 10].includes(al) ? 1 : 0.5;
      const fy = [2, 3, 4].includes(al) ? 0 : [8, 9, 10].includes(al) ? 1 : 0.5;
      content = [b[0] + (b[2] - cw) * fx, b[1] + (b[3] - ch) * fy, cw, ch];
      const lw = b[2] - cw, lh = b[3] - ch;
      lb = Math.max(lw, lh); lbr = lw > lh ? lw / b[2] : lh / b[3];
    }
    let outside = 0, minText = null;
    const glyphs = []; // one box per text, or per repositioned tspan (x, y, dx, dy); trimmed to the glyph core band
    for (const t of sv.querySelectorAll('text')) {
      if (!isVis(t) || !(t.textContent || '').trim()) continue;
      const tb = R(t.getBoundingClientRect());
      if (tb[0] < content[0] - 1 || tb[1] < content[1] - 1 || tb[0] + tb[2] > content[0] + content[2] + 1 || tb[1] + tb[3] > content[1] + content[3] + 1) outside++;
      const s = effSize(t);
      minText = minText === null ? s : Math.min(minText, s);
      const moved = [...t.querySelectorAll('tspan')].some(x => ['x', 'y', 'dx', 'dy'].some(at => x.hasAttribute(at)));
      const spans = moved ? [...t.querySelectorAll('tspan')].filter(x => isVis(x) && (x.textContent || '').trim()) : [];
      for (const g of spans.length ? spans : [t]) {
        const gb = R(g.getBoundingClientRect()), cy = gb[1] + gb[3] / 2, gs = effSize(g);
        if (gb[2] > 0) glyphs.push({ text: t, box: [gb[0], cy - 0.3 * gs, gb[2], 0.6 * gs] });
      }
    }
    // H5 text_overlap: two glyph boxes intersecting by more than 1 px on both axes, or a glyph box that
    // crosses the edge of a visible sibling rect (partly inside, partly outside)
    const cross = (a, b) => Math.min(a[0] + a[2], b[0] + b[2]) - Math.max(a[0], b[0]) > 1 && Math.min(a[1] + a[3], b[1] + b[3]) - Math.max(a[1], b[1]) > 1;
    const inside = (a, b) => a[0] >= b[0] - 1 && a[1] >= b[1] - 1 && a[0] + a[2] <= b[0] + b[2] + 1 && a[1] + a[3] <= b[1] + b[3] + 1;
    const rects = [...sv.querySelectorAll('rect')].filter(r => isVis(r) && !r.closest('defs, clipPath, mask, pattern')).map(r => R(r.getBoundingClientRect())).filter(r => r[2] > 2 && r[3] > 2);
    let overlap = 0;
    for (let i = 0; i < glyphs.length; i++) {
      for (let j = i + 1; j < glyphs.length; j++) if (cross(glyphs[i].box, glyphs[j].box)) overlap++;
      if (rects.some(r => cross(glyphs[i].box, r) && !inside(glyphs[i].box, r))) overlap++;
    }
    svgs.push({ sel: selOf(sv), box: b, letterbox_ratio: Math.round(lbr * 1000) / 1000, letterbox_px: r1(lb), text_outside: outside, text_overlap: overlap, min_text_px: minText === null ? null : r1(minText) });
    if (inColumns(content)) { contentRects.push(content); contentEls.push(sv); }
  }
  let lowest = contentRects.length ? Math.max(...contentRects.map(b => b[1] + b[3])) : 0;
  // H3: free main-axis space above the lowest content in column flexboxes: auto margins and justify-content
  // gaps, and the growth of a flex-grow sibling above it (its height minus its height without growth, read
  // with the inline style set and restored at once). Text that reflows taller fills this space before it
  // reaches the bottom padding.
  const autoTop = x => { try { const v = x.computedStyleMap().get('margin-top'); return !!v && String(v) === 'auto'; } catch { return false; } };
  const grownBy = x => {
    const keep = x.getAttribute('style'), h = x.getBoundingClientRect().height;
    x.style.setProperty('flex-grow', '0', 'important');
    x.style.setProperty('flex-basis', 'auto', 'important');
    const h0 = x.getBoundingClientRect().height;
    if (keep === null) x.removeAttribute('style'); else x.setAttribute('style', keep);
    return Math.max(0, h - h0);
  };
  const flexFree = el => { // rects are screen px; CSS lengths are design px, so they scale by k
    let free = 0;
    const px = v => (parseFloat(v) || 0) * k;
    for (let a = el; a && a !== S && a.parentElement; a = a.parentElement) {
      const p = a.parentElement, pc = getComputedStyle(p);
      if (!/flex/.test(pc.display) || pc.flexDirection !== 'column') continue;
      const kids = [...p.children].filter(x => isVis(x) && !['absolute', 'fixed'].includes(getComputedStyle(x).position));
      const idx = kids.indexOf(a);
      if (idx < 0) continue;
      let prev = p.getBoundingClientRect().top + px(pc.borderTopWidth) + px(pc.paddingTop);
      const rowGap = px(pc.rowGap);
      for (let i = 0; i <= idx; i++) {
        const x = kids[i], xc = getComputedStyle(x), xr = x.getBoundingClientRect();
        const extra = xr.top - prev - (i ? rowGap : 0) - (autoTop(x) ? 0 : px(xc.marginTop));
        if (extra > 0.5 * k) free += extra;
        if (i < idx && parseFloat(xc.flexGrow) > 0) free += grownBy(x);
        prev = xr.bottom + px(xc.marginBottom);
      }
    }
    return free / k;
  };
  const lowEls = contentEls.filter((e, i) => contentRects[i][1] + contentRects[i][3] >= lowest - 2);
  const flexFreePx = lowEls.length ? Math.min(...lowEls.map(flexFree)) : 0;

  // ---- framed boxes (cards) and strokes
  const SKIP_CARD = '.pill, .tag, .badge, .chip, .demo-pill, button, kbd, td, th, tr, thead, tbody, table, code, .copy, aside.notes, .notes, #bar';
  const framed = new Map();
  for (const e of S.querySelectorAll('*')) {
    if (e instanceof SVGElement || !isVis(e) || e.closest(SKIP_CARD)) continue;
    const c = getComputedStyle(e);
    if (c.display === 'inline' || c.display === 'contents') continue;
    const b = R(e.getBoundingClientRect());
    if (b[2] * b[3] < 2000 || (b[2] >= W * 0.95 && b[3] >= H * 0.95)) continue;
    const own = ownBg(e), parent = chainBg(e.parentElement || S);
    const sides = ['Top', 'Right', 'Bottom', 'Left'].map(sd => (c[`border${sd}Style`] !== 'none' && parseColor(c[`border${sd}Color`])[3] > 0.05 ? parseFloat(c[`border${sd}Width`]) || 0 : 0));
    const border = Math.max(...sides);
    const side = ['Top', 'Right', 'Bottom', 'Left'][sides.indexOf(border)];
    const shadow = c.boxShadow && c.boxShadow !== 'none';
    let fill = null;
    if (own && own.kind === 'solid' && parent.color) fill = mix(own.rgba, parent.color, own.rgba[3]);
    const differs = fill && parent.color && hex(fill) !== hex(parent.color);
    if (!(differs || border >= 0.5 || shadow || (own && own.kind !== 'solid'))) continue;
    framed.set(e, { e, b, c, fill, parent, border, shadow, borderColor: hex(parseColor(c[`border${side}Color`])) });
  }
  const cards = [], strokes = [];
  let depthMax = 0;
  for (const f of framed.values()) { // a frame that crosses the content-box bottom is overflow (H3)
    const bottom = f.b[1] + f.b[3];
    if (inColumns(f.b) && bottom > H - pad.b + 0.5 && f.b[1] < H - pad.b) lowest = Math.max(lowest, bottom);
  }
  for (const f of framed.values()) {
    let depth = 1;
    for (let a = f.e.parentElement; a && a !== S; a = a.parentElement) if (framed.has(a)) depth++;
    depthMax = Math.max(depthMax, depth);
    const inner = [...contentRects].filter(cb => cb[0] >= f.b[0] - 1 && cb[1] >= f.b[1] - 1 && cb[0] + cb[2] <= f.b[0] + f.b[2] + 1 && cb[1] + cb[3] <= f.b[1] + f.b[3] + 1);
    const innerBottom = f.b[1] + f.b[3] - (parseFloat(f.c.borderBottomWidth) || 0);
    // G5: the largest vertical gap between consecutive in-flow children (a note pinned by margin-top:auto
    // in an equal-height card leaves its dead space here, above the lowest content); content cards only,
    // so a full-height rail or side band in the padding is not a card
    const kids = [...f.e.childNodes].map(x => {
      if (x.nodeType === 3) { if (!x.nodeValue.trim()) return null; rng.selectNodeContents(x); return R(rng.getBoundingClientRect()); }
      if (x.nodeType !== 1 || !isVis(x) || excluded(x) || ['absolute', 'fixed'].includes(getComputedStyle(x).position)) return null;
      return R(x.getBoundingClientRect());
    }).filter(x => x && x[3] > 0).sort((p, q) => p[1] - q[1]); // element and text children: inline runs fill the flow too
    let innerGap = 0;
    for (let i = 1; i < kids.length; i++) innerGap = Math.max(innerGap, kids[i][1] - Math.max(...kids.slice(0, i).map(x => x[1] + x[3])));
    cards.push({ sel: selOf(f.e), box: f.b, bg: hex(f.fill), parent_bg: hex(f.parent.color), border_px: r1(f.border), border_color: f.border ? f.borderColor : null,
      shadow: !!f.shadow, pad_top_px: r1(parseFloat(f.c.paddingTop) || 0),
      gap_bottom_px: inner.length ? r1(innerBottom - Math.max(...inner.map(cb => cb[1] + cb[3]))) : null, max_inner_gap_px: kids.length > 1 && inColumns(f.b) && f.b[3] <= H - pad.t - pad.b + 1 ? r1(innerGap) : null, depth });
    if (f.border >= 0.5) strokes.push({ sel: selOf(f.e), width_px: r1(f.border), color: f.borderColor, bg: hex(f.parent.color) });
  }
  const seenStroke = new Set();
  for (const sh of S.querySelectorAll('svg line, svg path, svg polyline, svg rect, svg circle, svg ellipse, svg polygon')) {
    if (strokes.length > 60 || !isVis(sh)) continue;
    const c = getComputedStyle(sh);
    if (!c.stroke || c.stroke === 'none' || c.stroke.startsWith('url(')) continue;
    const m = sh.getScreenCTM();
    const wpx = (parseFloat(c.strokeWidth) || 0) * (m ? Math.sqrt(m.a * m.a + m.b * m.b) : 1) / k;
    if (wpx <= 0) continue;
    const col = parseColor(c.stroke);
    const a = col[3] * (parseFloat(c.strokeOpacity) || 1) * opacityChain(sh);
    const rb = sh.getBoundingClientRect();
    let bg = chainBg(sh.ownerSVGElement || S);
    const host = sh.ownerSVGElement;
    if (host) { const hb = host.getBoundingClientRect(); const pt = [hb.left + 2, hb.top + 2]; bg = resolveBg(host, pt[0], pt[1]); }
    const color = bg.color ? hex(mix(col, bg.color, a)) : hex(col);
    const key = [r1(wpx), color, hex(bg.color)].join();
    if (seenStroke.has(key)) continue;
    seenStroke.add(key);
    strokes.push({ sel: selOf(sh), width_px: r1(wpx), color, bg: hex(bg.color), svg: true, box: R(rb) });
  }

  // ---- overflow of clipping elements
  const overflow = [];
  for (const e of all) {
    if (e instanceof SVGElement || !isVis(e)) continue;
    const c = getComputedStyle(e);
    const clips = v => ['hidden', 'auto', 'scroll', 'clip'].includes(v);
    const ox = clips(c.overflowX) ? e.scrollWidth - e.clientWidth : 0, oy = clips(c.overflowY) ? e.scrollHeight - e.clientHeight : 0;
    if (ox <= 1 && oy <= 1) continue;
    const kind = e.matches('pre, code, .term') || e.closest('.term') ? 'pre' : e.matches('.card, [class*="card"]') ? 'card' : (e === S || e.matches('.body')) ? 'body' : 'other';
    overflow.push({ sel: e === S ? 'section' : selOf(e), kind, ox_px: Math.max(0, ox), oy_px: Math.max(0, oy), ellipsis: c.textOverflow === 'ellipsis' });
  }

  // ---- components
  const visTexts = texts.filter(t => !t.excluded);
  const elOf = t => textEls[texts.indexOf(t)];
  const sizeOfSel = el => { const t = [el, ...el.querySelectorAll('*')].find(x => [...x.childNodes].some(n => n.nodeType === 3 && n.nodeValue.trim())); return t ? r1(effSize(t)) : null; };
  const bodySizes = visTexts.filter(t => t.role === 'body').map(t => t.size_px);
  const modal = arr => { const m = new Map(); for (const v of arr) m.set(v, (m.get(v) || 0) + 1); let best = null, bc = 0; for (const [v, c] of m) if (c > bc) { best = v; bc = c; } return best; };
  const bodyPx = modal(bodySizes);
  const tables = [...S.querySelectorAll('table')].filter(isVis).map(tb => {
    const rows = [...tb.rows];
    const head = rows.filter(r => r.parentElement.tagName === 'THEAD' || [...r.cells].every(c => c.tagName === 'TH'));
    const bodyRows = rows.filter(r => !head.includes(r));
    const cols = Math.max(0, ...rows.map(r => [...r.cells].reduce((s, c) => s + (c.colSpan || 1), 0)));
    let minSize = null;
    for (const cell of tb.querySelectorAll('td, th')) {
      for (const x of [cell, ...cell.querySelectorAll('*')]) {
        if (![...x.childNodes].some(n => n.nodeType === 3 && n.nodeValue.trim()) || !isVis(x)) continue;
        const s = effSize(x); minSize = minSize === null ? s : Math.min(minSize, s);
      }
    }
    const ths = head.length ? [...head[0].cells] : [];
    const fills = new Set(), colors = [];
    let hbg = null, hcol = null;
    for (const th of ths) {
      const rb = th.getBoundingClientRect();
      const bg = resolveBg(th, rb.left + 2, rb.top + 2);
      fills.add(bg.color ? hex(bg.color) : bg.kind);
      const fc = parseColor(getComputedStyle(th).color);
      const col = bg.color ? hex(mix(fc, bg.color, fc[3] * opacityChain(th))) : hex(fc);
      colors.push(col);
      if (!hbg) { hbg = bg.color ? hex(bg.color) : null; hcol = col; }
    }
    return { sel: selOf(tb), rows: bodyRows.length, cols, min_size_px: minSize === null ? null : r1(minSize), header_bg: hbg, header_color: hcol,
      header_fills: fills.size, is_ref: S.matches('.a-ref-table, [data-archetype="ref-table"]') || tb.matches('.ref, [data-ref-table]') };
  });
  const code = [];
  for (const e of S.querySelectorAll('pre, .term, code')) {
    if (!isVis(e) || (e.matches('code') && e.closest('pre')) || (e.matches('.term') && e.querySelector('pre')) || excluded(e)) continue;
    const t = e.textContent || '';
    let ox = e.scrollWidth - e.clientWidth;
    for (let a = e.parentElement, d = 0; a && d < 2; a = a.parentElement, d++) ox = Math.max(ox, a.scrollWidth - a.clientWidth > 1 && ['hidden', 'auto', 'scroll', 'clip'].includes(getComputedStyle(a).overflowX) ? a.scrollWidth - a.clientWidth : 0);
    const size = sizeOfSel(e);
    code.push({ sel: selOf(e), family: familyOf(e), size_px: size, curly: (t.match(/[‘’“”]/g) || []).length, overflow_px: Math.max(0, ox),
      lines: t.split('\n').filter(x => x.trim()).length, hero: !!e.closest('.code-hero, [data-role="hero"]'), inline: e.matches('code') });
  }
  const pills = [...S.querySelectorAll('.pill, .tag, .badge, .chip, .demo-pill, [data-role="pill"]')].filter(e => isVis(e) && !excluded(e)).map(e => {
    rng.selectNodeContents(e);
    const rs = [...rng.getClientRects()].filter(r => r.width > 0 && r.height > 0);
    const c = getComputedStyle(e), rb = e.getBoundingClientRect(), bg = resolveBg(e, rb.left + 1, rb.top + 1);
    const fc = parseColor(c.color);
    return { sel: selOf(e), text: (e.textContent || '').replace(/[ \t\n\r\f\v]+/g, ' ').trim().slice(0, 40), cls: (e.getAttribute('class') || '').trim(), size_px: sizeOfSel(e),
      lines: lineCount(rs, parseFloat(c.fontSize) || 10), bg: hex(bg.color), color: bg.color ? hex(mix(fc, bg.color, fc[3])) : hex(fc), transform: c.textTransform, box: R(rb) };
  });

  // ---- slide-level objects
  // rendered lines of a text block, character by character (T3: title lines and the last-line orphan)
  const lineSplit = el => {
    const tnodes = [];
    const walk = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
    let n;
    while ((n = walk.nextNode())) if (n.nodeValue.trim()) tnodes.push(n);
    const chars = [];
    for (const tn of tnodes) for (let i = 0; i < tn.nodeValue.length; i++) {
      rng.setStart(tn, i); rng.setEnd(tn, i + 1);
      const rr = rng.getClientRects()[0];
      if (rr && rr.width >= 0) chars.push({ ch: tn.nodeValue[i], mid: (rr.top + rr.bottom) / 2 / k });
    }
    const size = effSize(el);
    const lines = [];
    for (const c of chars) { const l = lines.find(x => Math.abs(x.mid - c.mid) < size * 0.5); if (l) l.s += c.ch; else lines.push({ mid: c.mid, s: c.ch }); }
    lines.sort((a, b) => a.mid - b.mid);
    return { lines: lines.length, last_line_words: lines.length ? tokens(lines[lines.length - 1].s).length : 0 };
  };
  let title = null;
  if (titleEl) {
    const tc = getComputedStyle(titleEl), tr = titleEl.getBoundingClientRect();
    const size = effSize(titleEl);
    const ls = lineSplit(titleEl);
    const ttext = (titleEl.textContent || '').replace(/[ \t\n\r\f\v]+/g, ' ').trim();
    const cx = tr.left + tr.width / 2, cy = tr.top + tr.height / 2;
    const hit = cx >= 0 && cy >= 0 && cx <= innerWidth && cy <= innerHeight ? document.elementFromPoint(cx, cy) : null;
    const bg = resolveBg(titleEl, cx, cy);
    const fc = parseColor(tc.color);
    const box = R(tr);
    title = { text: ttext, chars: ttext.length, lines: ls.lines, last_line_words: ls.last_line_words, box,
      size_px: r1(size), weight: +tc.fontWeight || 400, color: clipText(titleEl) ? null : bg.color ? hex(mix(fc, bg.color, fc[3] * opacityChain(titleEl))) : hex(fc),
      bg: hex(bg.color), align: tc.textAlign === 'start' ? 'left' : tc.textAlign, visible: box[0] < W && box[1] < H && box[0] + box[2] > 0 && box[1] + box[3] > 0,
      covered: !hit || !(hit === titleEl || titleEl.contains(hit) || hit.contains(titleEl)), tag: titleEl.tagName.toLowerCase() };
  }
  const ebEl = [...S.querySelectorAll('.eyebrow')].find(isVis);
  const eyebrow = ebEl ? { text: (ebEl.textContent || '').replace(/[ \t\n\r\f\v]+/g, ' ').trim(), size_px: sizeOfSel(ebEl), transform: getComputedStyle(ebEl).textTransform, mono: isMono(ebEl) } : null;
  const dekEl = [...S.querySelectorAll('.dek, [data-role="dek"]')].find(e => isVis(e) && !excluded(e) && (e.textContent || '').trim());
  const dek = dekEl ? { sel: selOf(dekEl), ...lineSplit(dekEl) } : null;
  const largest = visTexts.reduce((a, t) => (!a || t.size_px > a.size_px ? t : a), null);
  const bodyEl = S.querySelector('.body');
  let zones;
  if (bodyEl && isVis(bodyEl)) zones = [...bodyEl.children].filter(isVis).length;
  else zones = [...S.children].filter(e => isVis(e) && !e.matches('.eyebrow, .t, h1, h2, .dek, .pn, aside.notes, .notes, [data-chrome], .rail') && e !== pnEl && !(pnEl && e.contains(pnEl) && !e.textContent.replace(pnEl.textContent, '').trim())).length;
  const sbg = chainBg(S);
  const archetype = S.getAttribute('data-archetype') || ([...S.classList].find(c => c.startsWith('a-')) || '').slice(2) || null;
  const statsEls = [...S.querySelectorAll('.stat')].filter(isVis);
  const stats = statsEls.map(st => {
    const v = st.querySelector('.v'), l = st.querySelector('.l');
    return { value_px: v ? sizeOfSel(v) : null, label_words: l ? tokens(l.textContent || '').length : null, has_method: !!st.querySelector('.m'), body_px: bodyPx,
      slide_method: !!S.querySelector('.m, .note, [data-role="method"]') };
  });
  let map = null, zoom = null, fromto = null;
  if (archetype === 'map' || S.classList.contains('a-map')) map = { boxes: S.querySelectorAll('[data-box], .box').length, highlights: S.querySelectorAll('.hl').length };
  if (archetype === 'zoom' || S.classList.contains('a-zoom')) {
    const dimT = visTexts.filter(t => elOf(t).closest('.dim'));
    const ratioOf = t => (t.color && t.bg ? ratio(parseColor(t.color), parseColor(t.bg)) : null);
    const act = visTexts.filter(t => !dimT.includes(t)).map(ratioOf).filter(v => v !== null);
    const revealT = visTexts.filter(t => elOf(t).closest('.reveal'));
    zoom = { dim: dimT.map(t => ({ sel: t.sel, ratio: ratioOf(t) === null ? null : Math.round(ratioOf(t) * 100) / 100 })),
      active_min_ratio: act.length ? Math.round(Math.min(...act) * 100) / 100 : null,
      reveal_px: revealT.length ? Math.min(...revealT.map(t => t.size_px)) : null, context_px: dimT.length ? Math.max(...dimT.map(t => t.size_px)) : null };
  }
  if (archetype === 'from-to' || S.classList.contains('a-from-to')) {
    const rows = s => { const e = S.querySelector(s); return e ? (e.querySelectorAll('li').length || [...e.children].filter(isVis).length) : 0; };
    fromto = { from_rows: rows('.from'), to_rows: rows('.to') };
  }
  const notesEl = S.querySelector('aside.notes, .notes');
  const emph = new Set();
  for (const e of S.querySelectorAll('b, strong, em, mark, .accent')) {
    if (!isVis(e) || e.closest('.eyebrow') || (titleEl && titleEl.contains(e)) || excluded(e)) continue;
    const p = e.parentElement; if (!p) continue;
    const a = getComputedStyle(e), b = getComputedStyle(p), d = [];
    if (a.fontWeight !== b.fontWeight) d.push('w' + a.fontWeight);
    if (a.color !== b.color) d.push('c' + hex(parseColor(a.color)));
    if (a.fontStyle !== b.fontStyle) d.push('i');
    if (/underline/.test(a.textDecorationLine) !== /underline/.test(b.textDecorationLine)) d.push('u');
    if (ownBg(e)) d.push('bg');
    if (d.length) emph.add(d.join('|'));
  }
  const data = {};
  for (const a of S.attributes) if (a.name.startsWith('data-')) data[a.name.slice(5)] = a.value;
  const pnBox = pnEl ? R(pnEl.getBoundingClientRect()) : null;
  const pm = pnEl ? pnRe.exec(pnEl.textContent || '') : null;

  return {
    n: index + 1, id: S.id || null, archetype, part: S.getAttribute('data-part'), mode: S.getAttribute('data-mode') || null,
    appendix: S.hasAttribute('data-appendix') || S.classList.contains('appendix'),
    canvas_px: [W, H], scale: Math.round(k * 10000) / 10000, padding_px: [pad.t, pad.r, pad.b, pad.l],
    bg: { color: hex(sbg.color), lum: sbg.color ? Math.round(lum(sbg.color) * 1000) / 1000 : null, kind: sbg.kind },
    words, words_by_role, zones, title, eyebrow, dek,
    largest: largest ? { role: largest.role, size_px: largest.size_px, sel: largest.sel } : null,
    texts, overflow, bottom_slack_px: r1(H - pad.b - lowest), flex_free_px: r1(flexFreePx), empty_ratio: Math.round((H - lowest) / H * 1000) / 1000,
    cards, framed_depth_max: depthMax + 1, strokes, tables, code, pills, images, svgs, map, zoom, stats, fromto,
    page_number: pnEl ? { text: (pnEl.textContent || '').trim(), value: pm ? +pm[1] : null, box: pnBox, size_px: sizeOfSel(pnEl) } : null,
    deco: [...S.querySelectorAll('[data-deco], .brand')].filter(isVis).map(e => ({ sel: selOf(e), box: R(e.getBoundingClientRect()), kind: e.matches('.brand') ? 'brand' : 'deco' })),
    notes: { present: !!notesEl, words: notesEl ? tokens(notesEl.textContent || '').length : 0 },
    todo: S.querySelectorAll('[data-todo]').length + (S.hasAttribute('data-todo') ? 1 : 0),
    lists: [...S.querySelectorAll('[data-list]')].map(e => ({ name: e.getAttribute('data-list'), render: e.getAttribute('data-render'),
      labels: [...e.children].map(c => ((c.querySelector(':scope > .nm') || c).textContent || '').replace(/[ \t\n\r\f\v]+/g, ' ').trim()).filter(Boolean) })), // .nm holds the label of a card or step with a detail line
    links_underlined: [...S.querySelectorAll('a')].filter(a => isVis(a) && /underline/.test(getComputedStyle(a).textDecorationLine)).length,
    emphasis_styles: emph.size, demo_marker: !!S.querySelector('.demo-pill'), data, contract, total,
  };
}

// Deck-level facts read from the live page and from the source markup (DOMParser: no scripts run).
function DECK_INFO({ sel, source }) {
  const roles = ['divider', 'title', 'hero', 'card-heading', 'body', 'label', 'eyebrow', 'code', 'code-hero', 'footer', 'dek', 'small'];
  const read = el => { const cs = getComputedStyle(el); const v = roles.map(r => parseFloat(cs.getPropertyValue('--fs-' + r))).filter(Number.isFinite); return v.length ? v : null; };
  const talk = read(document.documentElement);
  const probe = document.createElement('div');
  probe.setAttribute('data-mode', 'reading');
  (document.querySelector('#track') || document.body).appendChild(probe);
  const reading = read(probe);
  probe.remove();
  const faces = [...new Set([...document.fonts].filter(f => f.status === 'loaded').map(f => f.family.replace(/["']/g, '')))];
  let embedded = false;
  for (const sh of document.styleSheets) {
    let rules = [];
    try { rules = [...sh.cssRules]; } catch { continue; }
    for (const r of rules) if (r instanceof CSSFontFaceRule && /url\(/.test(r.style.getPropertyValue('src'))) embedded = true;
  }
  const doc = new DOMParser().parseFromString(source, 'text/html');
  const srcSlides = [...doc.querySelectorAll(sel)];
  const pnRe = /^\s*0*(\d{1,3})(?:\s*(?:\/|з|of|·)\s*\d{1,3})?\s*$/;
  let pn = 0, toc = 0, prose = 0, countText = 0, inline = 0;
  const perSlideInline = [];
  srcSlides.forEach((s, i) => {
    const st = s.querySelectorAll('[style]').length + (s.hasAttribute('style') ? 1 : 0);
    perSlideInline.push(st); inline += st;
    for (const e of s.querySelectorAll('.pn, [data-role="pn"], .num, .page-num, .page-number, .slide-num, .slide-number')) if (pnRe.test(e.textContent || '')) { pn++; break; }
    for (const e of s.querySelectorAll('nav[data-toc] *, .toc *')) {
      if (e.children.length) continue;
      if (/^\s*\d{1,3}(\s*[-\u2013\u2014]\s*\d{1,3})?\s*$/.test(e.textContent || '')) toc++;
    }
    const walk = doc.createTreeWalker(s, NodeFilter.SHOW_TEXT);
    let n;
    while ((n = walk.nextNode())) {
      if (n.parentElement && n.parentElement.closest('script, style, aside.notes, .notes')) continue;
      for (const m of n.nodeValue.matchAll(/(?:слайд\p{L}*|slides?)\s*(?:№\s*)?(\d{1,4})/giu)) if (+m[1] >= 1 && +m[1] <= srcSlides.length) prose++;
      for (const m of n.nodeValue.matchAll(/(\d{1,4})\s*(?:слайд\p{L}*|slides)/giu)) if (+m[1] === srcSlides.length) countText++;
    }
  });
  // part labels (H2, N13): a dedicated carrier ([data-role=part], .rail .vert) typed in the source is a literal
  // label; the carrier, or else the first eyebrow segment before " · ", must equal the slide's section
  // (data-sect, else the data-part title from script#deck-data). Source text, so text-transform plays no part.
  const norm = t => String(t || '').replace(/[\s ]+/g, ' ').trim().toLocaleLowerCase();
  let partTitles = {};
  try { (JSON.parse((doc.getElementById('deck-data') || {}).textContent || '{}').parts || []).forEach(p => { if (p && p.id) partTitles[p.id] = p.title; }); } catch { partTitles = {}; }
  let partLabels = 0;
  const partMismatch = [];
  srcSlides.forEach((s, i) => {
    const own = [...s.querySelectorAll('[data-role="part"], .rail .vert')].find(e => (e.textContent || '').trim());
    if (own) partLabels++;
    let label = own ? own.textContent : null;
    if (!label) {
      const eb = s.querySelector('.eyebrow');
      const t = eb ? (eb.textContent || '').replace(/[\s ]+/g, ' ').trim() : '';
      if (t.includes(' · ')) label = t.split(' · ')[0];
    }
    const sect = s.getAttribute('data-sect') || partTitles[s.getAttribute('data-part')] || null;
    if (label && sect && norm(label) !== norm(sect)) partMismatch.push({ n: i + 1, label: norm(label).slice(0, 40), section: norm(sect).slice(0, 40) });
  });
  // descendant-selector leaks (H7): a rule whose last compound is a bare type selector after a descendant
  // combinator and that sets a border, padding or margin, matching elements nested inside another match
  const BOX = /^(border(-(top|right|bottom|left))?(-(width|style|color))?|padding(-\w+)?|margin(-\w+)?)$/;
  const slideEls = [...document.querySelectorAll(sel)];
  const leaks = [];
  const walkRules = rules => {
    for (const r of rules) {
      if (r.cssRules && !(r instanceof CSSStyleRule)) { if (!r.media || matchMedia(r.media.mediaText || 'all').matches) walkRules([...r.cssRules]); continue; }
      // a reset to zero or none (.slide ul{margin:0}) draws nothing; only a real border, padding or margin leaks
      if (!(r instanceof CSSStyleRule) || ![...r.style].some(p => BOX.test(p) && !/^(0(px)?|none|initial|unset|inherit|auto|hidden)$/.test(r.style.getPropertyValue(p).trim()))) continue;
      for (const one of r.selectorText.split(',').map(x => x.trim())) {
        if (!/(^|[^>+~\s])\s+[a-z][a-z0-9-]*$/i.test(one)) continue;
        let hits;
        try { hits = new Set(document.querySelectorAll(one)); } catch { continue; }
        const per = new Map();
        for (const e of hits) {
          const at = slideEls.findIndex(s => s.contains(e));
          if (at < 0) continue;
          let up = e.parentElement;
          while (up && !hits.has(up)) up = up.parentElement;
          if (up && slideEls[at].contains(up)) per.set(at + 1, (per.get(at + 1) || 0) + 1);
        }
        if (per.size) leaks.push({ selector: one, slides: [...per.keys()], nested: [...per.values()].reduce((a, b) => a + b, 0) });
      }
    }
  };
  for (const sh of document.styleSheets) { try { walkRules([...sh.cssRules]); } catch { /* cross-origin sheet */ } }
  const headScripts = [...doc.head.querySelectorAll('script')].map(s => s.textContent || '').join('\n');
  const theme_in_head = /theme/i.test(headScripts) && /(localStorage|matchMedia|dataset|setAttribute)/.test(headScripts);
  return {
    lang: document.documentElement.lang || null, type_scale_px: talk || reading ? { talk, reading } : null,
    fonts: { faces, embedded }, theme_in_head, literal_numbers: { pn, toc_ranges: toc, prose_refs: prose, count_text: countText, part_labels: partLabels },
    part_label_mismatch: partMismatch, css_descendant_leaks: leaks,
    inline_styles: inline, inline_styles_per_slide: perSlideInline, source_slides: srcSlides.length,
    meta: window.deck && window.deck.meta ? window.deck.meta : null,
  };
}

function PRINT_INFO({ sel }) {
  const slides = [...document.querySelectorAll(sel)];
  const shown = e => { for (let x = e; x; x = x.parentElement) { const c = getComputedStyle(x); if (c.display === 'none' || c.visibility === 'hidden') return false; } return true; };
  const chromeSel = ['#bar', '#prog', '.copy', 'aside.notes', '.notes', '[data-chrome]', 'button'];
  const visible_chrome = chromeSel.filter(s => [...document.querySelectorAll(s)].some(shown));
  const leaks = [];
  for (const e of document.querySelectorAll('aside.notes, .notes, .copy, #bar')) if (shown(e) && (e.textContent || '').trim()) leaks.push(e.matches('.copy') ? 'copy' : e.matches('#bar') ? 'bar' : 'notes');
  const code_overflow = [];
  slides.forEach((s, i) => {
    let px = 0;
    for (const e of s.querySelectorAll('pre, .term, code')) px = Math.max(px, e.scrollWidth - e.clientWidth);
    code_overflow.push({ n: i + 1, px: Math.max(0, px) });
  });
  return { visible_chrome, pdf_text_leaks: [...new Set(leaks)], code_overflow };
}

function SLIDE_LUMS({ sel }) {
  const lin = v => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
  return [...document.querySelectorAll(sel)].map(s => {
    for (let e = s; e; e = e.parentElement) {
      const m = /rgba?\(([^)]+)\)/.exec(getComputedStyle(e).backgroundColor);
      if (m) { const p = m[1].split(/[\s,/]+/).map(parseFloat); if ((p[3] === undefined ? 1 : p[3]) > 0.5) return 0.2126 * lin(p[0]) + 0.7152 * lin(p[1]) + 0.0722 * lin(p[2]); }
    }
    return 1;
  });
}

function FONT_FAMILIES({ sel }) {
  const GENERIC = /^(serif|sans-serif|monospace|cursive|fantasy|system-ui|ui-\w+|emoji|math|fangsong|-apple-system|BlinkMacSystemFont|inherit|initial)$/i;
  const sans = new Set(), mono = new Set();
  for (const s of document.querySelectorAll(sel)) for (const e of [s, ...s.querySelectorAll('*')]) {
    const f = getComputedStyle(e).fontFamily || '';
    const names = f.split(',').map(x => x.replace(/["']/g, '').trim()).filter(x => x && !GENERIC.test(x));
    const isMono = /\bmonospace\b/.test(f) || /mono|code|courier|consolas|cascadia|menlo/i.test(names[0] || '');
    for (const n of names) (isMono ? mono : sans).add(n);
  }
  return { sans: [...sans], mono: [...mono] };
}

// =====================================================================================================
// Node side
// =====================================================================================================
const { chromium } = await loadPlaywright();
const exe = process.env.CHROME_PATH || '';
let browser;
try {
  browser = await chromium.launch({ ...(exe ? { executablePath: exe } : { channel: 'chromium' }), headless: true, args: ['--force-color-profile=srgb', '--hide-scrollbars'] });
} catch (e) {
  die(`browser launch failed: ${String(e.message || e).split('\n')[0]}\nSet CHROME_PATH or run: npx playwright install chromium`, 2);
}
const deckUrl = pathToFileURL(deckPath).href;
const source = fs.readFileSync(deckPath, 'utf8');
const fail = async msg => { console.error(msg); try { await browser.close(); } catch { /* closing */ } process.exit(1); };

async function openDeck(ctx, metricCss) {
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(String(e.message || e).slice(0, 200)));
  page.on('console', m => { if (m.type() === 'error') errors.push(m.text().slice(0, 200)); });
  if (metricCss) await page.addInitScript(css => {
    const add = () => { const st = document.createElement('style'); st.setAttribute('data-lint', 'metric-fonts'); st.textContent = css; (document.head || document.documentElement).appendChild(st); };
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', add); else add();
  }, metricCss);
  try { await page.goto(deckUrl, { waitUntil: 'load', timeout: 30000 }); } catch (e) { await fail(`deck failed to load: ${String(e.message || e).split('\n')[0]}`); }
  if (opt.theme === 'dark') await page.evaluate(() => document.documentElement.setAttribute('data-theme', 'dark'));
  const contract = await page.evaluate(async () => {
    if (window.deck && window.deck.version && typeof window.deck.go === 'function') {
      await Promise.race([Promise.resolve(window.deck.ready), new Promise(r => setTimeout(r, 15000))]);
      return true;
    }
    await document.fonts.ready;
    return false;
  });
  if (!contract) await page.waitForTimeout(300);
  return { page, errors, contract };
}

const activeIndex = page => page.evaluate(({ sel, cls }) => {
  const s = [...document.querySelectorAll(sel)];
  let i = s.findIndex(e => e.classList.contains(cls));
  if (i < 0) i = s.findIndex(e => getComputedStyle(e).display !== 'none' && e.getClientRects().length);
  return i;
}, { sel: opt.sel, cls: opt.active });

async function goSlide(page, contract, i) {
  if (contract) {
    await page.evaluate(i => new Promise(res => { window.deck.go(i); requestAnimationFrame(() => requestAnimationFrame(res)); }), i);
    return true;
  }
  if (i === 0) {
    if ((await activeIndex(page)) !== 0) await page.keyboard.press('Home');
    for (let t = 0; t < 400 && (await activeIndex(page)) > 0; t++) await page.keyboard.press('ArrowLeft');
  } else await page.keyboard.press(opt.next);
  const ok = await page.waitForFunction(({ sel, cls, i }) => {
    const s = [...document.querySelectorAll(sel)];
    let a = s.findIndex(e => e.classList.contains(cls));
    if (a < 0) a = s.findIndex(e => getComputedStyle(e).display !== 'none' && e.getClientRects().length);
    return a === i;
  }, { sel: opt.sel, cls: opt.active, i }, { timeout: 3000 }).then(() => true, () => false);
  if (ok) await page.waitForTimeout(250);
  return ok;
}

async function slideRect(page, i) {
  return page.evaluate(({ sel, i }) => { const r = document.querySelectorAll(sel)[i].getBoundingClientRect(); return { x: r.left, y: r.top, width: r.width, height: r.height }; }, { sel: opt.sel, i });
}

async function pass(ctx, label, pngDir, metricCss) {
  const { page, errors, contract } = await openDeck(ctx, metricCss);
  const count = await page.evaluate(sel => document.querySelectorAll(sel).length, opt.sel);
  if (!count) await fail(`no slides found with selector ${opt.sel}`);
  fs.mkdirSync(path.join(outDir, pngDir), { recursive: true });
  const digits = Math.max(2, String(count).length);
  const slides = [];
  for (let i = 0; i < count; i++) {
    if (!(await goSlide(page, contract, i))) await fail(`navigation stuck at slide ${i + 1} of ${count} (selector ${opt.sel}, active class ${opt.active}, key ${opt.next})`);
    const m = await page.evaluate(MEASURE, { sel: opt.sel, index: i, total: count, contract });
    const file = `slide-${String(i + 1).padStart(digits, '0')}.png`;
    const rect = await slideRect(page, i);
    await page.screenshot({ path: path.join(outDir, pngDir, file), clip: { ...rect, width: rect.width + 0.6, height: rect.height + 0.6 }, animations: 'disabled' });
    m.png = `${pngDir}/${file}`;
    slides.push(m);
    process.stdout.write(`${label} ${i + 1}/${count}\r`);
  }
  process.stdout.write('\n');
  return { page, errors, contract, count, slides };
}

// probe the track scale to screenshot at one PNG pixel per design px
const probeCtx = await browser.newContext({ viewport: VIEW, deviceScaleFactor: 1, colorScheme: opt.theme, reducedMotion: 'reduce' });
const probe = await openDeck(probeCtx);
const probeInfo = await probe.page.evaluate(sel => {
  const s = document.querySelectorAll(sel);
  const vis = [...s].find(e => e.getClientRects().length && getComputedStyle(e).display !== 'none') || s[0];
  if (!vis) return null;
  return { count: s.length, k: vis.getBoundingClientRect().width / (vis.offsetWidth || 1) };
}, opt.sel);
await probeCtx.close();
if (!probeInfo || !probeInfo.count) await fail(`no slides found with selector ${opt.sel}`);
const dsf = probeInfo.k > 0.05 ? 1 / probeInfo.k : 1;
const ctx = await browser.newContext({ viewport: VIEW, deviceScaleFactor: dsf, colorScheme: opt.theme, reducedMotion: 'reduce' });
fs.mkdirSync(outDir, { recursive: true });

const passes = [];
let main = null;
if (opt.fonts !== 'metric') { main = await pass(ctx, 'native', 'png'); passes.push({ font_mode: 'native', png_dir: 'png', slides: main.slides }); }

// deck-level facts, engine passes (native page; or a fresh page in metric-only runs)
const host = main || { ...(await openDeck(ctx)), slides: [], count: probeInfo.count };
const page = host.page;
const info = await page.evaluate(DECK_INFO, { sel: opt.sel, source });
const fam = await page.evaluate(FONT_FAMILIES, { sel: opt.sel });
info.fonts.families_declared = [...fam.sans, ...fam.mono];

// viewports (H1)
const vpOut = [];
for (const [w, h] of viewports) {
  await page.setViewportSize({ width: w, height: h });
  await page.waitForTimeout(200);
  vpOut.push(await page.evaluate(({ sel, w, h }) => {
    const s = [...document.querySelectorAll(sel)];
    const a = s.find(e => getComputedStyle(e).display !== 'none' && e.getClientRects().length) || s[0];
    const r = a.getBoundingClientRect();
    const bar = document.getElementById('bar');
    const br = bar && getComputedStyle(bar).display !== 'none' ? bar.getBoundingClientRect() : null;
    // the cut per axis is capped at the slide box: a box wholly outside the viewport is cut by its own size
    const cut = Math.max(Math.min(r.width, Math.max(0, -r.left, r.right - w)), Math.min(r.height, Math.max(0, -r.top, r.bottom - h)));
    const ix = Math.min(r.right, w) - Math.max(r.left, 0), iy = Math.min(r.bottom, h) - Math.max(r.top, 0);
    return { w, h, slide_box: [r.left, r.top, r.width, r.height].map(v => Math.round(v * 10) / 10), cut_px: Math.round(cut * 10) / 10,
      bar_overlap_px: br && br.height ? Math.max(0, Math.round((r.bottom - br.top) * 10) / 10) : 0,
      scale: Math.round(r.width / (a.offsetWidth || 1) * 1000) / 1000, visible: ix > 0 && iy > 0 };
  }, { sel: opt.sel, w, h }));
}
await page.setViewportSize(VIEW);
await page.waitForTimeout(150);

// features (H6): swipe listeners, overview, history push, presenter view
const features = { swipe: false, overview: false, history_push: false };
await goSlide(page, host.contract, 0);
await page.evaluate(() => { // a synthetic left swipe in the middle of the stage, as pointer and as touch events
  const el = document.elementFromPoint(innerWidth / 2, innerHeight / 2) || document.body;
  const y = innerHeight / 2, x0 = innerWidth * 0.7, x1 = innerWidth * 0.3, xm = (x0 + x1) / 2;
  const pe = (type, x) => { try { el.dispatchEvent(new PointerEvent(type, { bubbles: true, cancelable: true, pointerType: 'touch', isPrimary: true, pointerId: 7, clientX: x, clientY: y })); } catch { /* no PointerEvent */ } };
  pe('pointerdown', x0); pe('pointermove', xm); pe('pointerup', x1);
  try {
    const t = x => new Touch({ identifier: 7, target: el, clientX: x, clientY: y });
    el.dispatchEvent(new TouchEvent('touchstart', { bubbles: true, cancelable: true, touches: [t(x0)], changedTouches: [t(x0)] }));
    el.dispatchEvent(new TouchEvent('touchmove', { bubbles: true, cancelable: true, touches: [t(xm)], changedTouches: [t(xm)] }));
    el.dispatchEvent(new TouchEvent('touchend', { bubbles: true, cancelable: true, touches: [], changedTouches: [t(x1)] }));
  } catch { /* no TouchEvent */ }
});
await page.waitForTimeout(300);
features.swipe = (await activeIndex(page)) > 0 || (host.contract && (await page.evaluate(() => window.deck.index)) > 0);
const visibleCount = () => page.evaluate(sel => [...document.querySelectorAll(sel)].filter(e => getComputedStyle(e).display !== 'none' && e.getClientRects().length).length, opt.sel);
await goSlide(page, host.contract, 0);
await page.keyboard.press('o');
await page.waitForTimeout(300);
features.overview = (await visibleCount()) > 1 || (await page.evaluate(() => { const o = document.querySelector('#overview, [data-view="overview"]'); return !!o && getComputedStyle(o).display !== 'none' && o.getClientRects().length > 0; }));
await page.keyboard.press('Escape');
await page.waitForTimeout(200);
if ((await visibleCount()) > 1) { await page.keyboard.press('o'); await page.waitForTimeout(200); }
const histBefore = await page.evaluate(() => history.length);
if (host.contract) await page.evaluate(() => window.deck.go(Math.min(2, window.deck.count - 1), { push: true }));
else await page.evaluate(() => { const a = document.querySelector('nav[data-toc] a, .toc a, .toc button, [data-go], a[data-ref]'); if (a) a.click(); });
await page.waitForTimeout(200);
features.history_push = (await page.evaluate(() => history.length)) > histBefore;

let presenter = { available: false, transport: null, follow_ms: null };
if (opt.presenter) {
  await goSlide(page, host.contract, 0);
  const popupP = ctx.waitForEvent('page', { timeout: 2500 }).catch(() => null);
  await page.keyboard.press('s');
  const pop = await popupP;
  if (pop) {
    try {
      await pop.waitForLoadState('load', { timeout: 10000 });
      await pop.waitForTimeout(500);
      presenter.available = true;
      presenter.transport = await pop.evaluate(() => document.documentElement.getAttribute('data-presenter-transport') || (window.opener ? 'postMessage' : 'other'));
      const target = Math.min(3, host.count - 1);
      const t0 = Date.now();
      if (host.contract) await page.evaluate(i => window.deck.go(i), target); else for (let i = 0; i < target; i++) await page.keyboard.press(opt.next);
      let ms = null;
      while (Date.now() - t0 < 3000) {
        const idx = await pop.evaluate(() => (window.deck && typeof window.deck.index === 'number' ? window.deck.index : document.documentElement.dataset.index !== undefined ? +document.documentElement.dataset.index : null));
        if (idx === target) { ms = Date.now() - t0; break; }
        await pop.waitForTimeout(10);
      }
      presenter.follow_ms = ms;
      await pop.close();
    } catch { /* presenter page failed */ }
  }
}

// print (H4)
let print = null;
if (opt.print) {
  await page.emulateMedia({ media: 'print' });
  const pr = await page.evaluate(PRINT_INFO, { sel: opt.sel });
  // light tokens forced in print: printing from the dark theme must give the same slide backgrounds
  // as printing from the light theme (dark dividers stay dark in both, which is not a failure)
  const prevTheme = await page.evaluate(() => document.documentElement.getAttribute('data-theme'));
  await page.evaluate(() => document.documentElement.setAttribute('data-theme', 'light'));
  const lightLums = await page.evaluate(SLIDE_LUMS, { sel: opt.sel });
  await page.evaluate(() => document.documentElement.setAttribute('data-theme', 'dark'));
  const darkLums = await page.evaluate(SLIDE_LUMS, { sel: opt.sel });
  await page.evaluate(t => { if (t === null) document.documentElement.removeAttribute('data-theme'); else document.documentElement.setAttribute('data-theme', t); }, prevTheme);
  const themeDiff = darkLums.map((l, i) => ({ n: i + 1, light: Math.round(lightLums[i] * 1000) / 1000, dark: Math.round(l * 1000) / 1000 })).filter(x => Math.abs(x.light - x.dark) > 0.05);
  const pdfPath = path.join(outDir, 'print.pdf');
  let pages = null, pagePt = null;
  try {
    await page.pdf({ path: pdfPath, preferCSSPageSize: true, printBackground: true });
    const pdf = fs.readFileSync(pdfPath).toString('latin1');
    const counts = [];
    for (const m of pdf.matchAll(/\/Type\s*\/Pages\b/g)) {
      const a = pdf.lastIndexOf('<<', m.index), b = pdf.indexOf('>>', m.index);
      const c = /\/Count\s+(\d+)/.exec(pdf.slice(a, b));
      if (c) counts.push(+c[1]);
    }
    pages = counts.length ? Math.max(...counts) : (pdf.match(/\/Type\s*\/Page(?![s\w])/g) || []).length;
    const mb = /\/MediaBox\s*\[\s*([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\s*\]/.exec(pdf);
    if (mb) pagePt = [Math.round((+mb[3] - +mb[1]) * 100) / 100, Math.round((+mb[4] - +mb[2]) * 100) / 100];
  } catch (e) { console.error(`print to PDF failed: ${String(e.message || e).split('\n')[0]}`); }
  print = { pages, page_pt: pagePt, visible_chrome: pr.visible_chrome, pdf_text_leaks: pr.pdf_text_leaks,
    light_tokens: themeDiff.length === 0, theme_differs: themeDiff.slice(0, 40), code_overflow: pr.code_overflow, file: 'print.pdf' };
  await page.emulateMedia({ media: 'screen' });
}
const consoleErrors = host.errors.slice(0, 50);

// metric font pass (H3)
if (opt.fonts !== 'native') {
  const rules = [];
  const q = n => n.replace(/"/g, '');
  for (const n of fam.sans) rules.push(`@font-face{font-family:"${q(n)}";src:local("Liberation Sans"),local("Arimo");font-weight:100 550}`,
    `@font-face{font-family:"${q(n)}";src:local("Liberation Sans Bold"),local("Arimo Bold"),local("LiberationSans-Bold");font-weight:551 1000}`);
  for (const n of fam.mono) rules.push(`@font-face{font-family:"${q(n)}";src:local("Liberation Mono"),local("Cousine");font-weight:100 550}`,
    `@font-face{font-family:"${q(n)}";src:local("Liberation Mono Bold"),local("Cousine Bold"),local("LiberationMono-Bold");font-weight:551 1000}`);
  const met = await pass(ctx, 'metric', 'png-metric', rules.join('\n'));
  passes.push({ font_mode: 'metric', png_dir: 'png-metric', slides: met.slides, families_mapped: { sans: fam.sans, mono: fam.mono } });
  await met.page.close();
}
await browser.close();

const first = passes[0].slides;
const metrics = {
  schema: 'deck-metrics/1', tool: 'html_deck_lint.mjs', source: path.basename(deckPath),
  canvas_px: first.length ? first[0].canvas_px : [1280, 720], px_per_pt: 1.3333333333,
  deck: {
    count: first.length, contract: host.contract, nav: host.contract ? 'window.deck' : `keys:${opt.next}`, selector: opt.sel, active_class: opt.active,
    lang: info.lang, mode: (info.meta && info.meta.mode) || null, type_scale_px: info.type_scale_px,
    fonts: info.fonts, theme_in_head: info.theme_in_head, literal_numbers: info.literal_numbers, inline_styles: info.inline_styles,
    part_label_mismatch: info.part_label_mismatch, css_descendant_leaks: info.css_descendant_leaks,
    source_slides: info.source_slides, viewports: vpOut, print, presenter, features, console_errors: consoleErrors,
    screenshot_scale: Math.round(dsf * 10000) / 10000, viewport: [VIEW.width, VIEW.height], theme: opt.theme,
  },
  passes,
};
for (const p of passes) p.slides.forEach((s, i) => { s.inline_styles = info.inline_styles_per_slide[i] ?? null; });
fs.writeFileSync(path.join(outDir, 'metrics.json'), JSON.stringify(metrics, null, 1) + '\n');
const ws = first.map(s => s.words).sort((a, b) => a - b);
console.log(`${first.length} slides, ${passes.length} font pass(es), median ${ws[Math.floor(ws.length / 2)] ?? 0} words; ` +
  `print ${print ? print.pages + ' pages' : 'skipped'}; presenter ${presenter.available ? 'yes' : 'no'} -> ${outDir}`);
process.exit(0);
