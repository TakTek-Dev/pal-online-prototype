// Mechanical QA over every page and viewport: the visual-qa probe plus a spacing probe
// (dead space inside blocks and between sections, text touching edges or neighbours).
// node --experimental-websocket tools/qa.mjs [base-url]  -> .impeccable/review/qa.json
import { spawn } from 'node:child_process';
import { mkdtempSync, writeFileSync, readFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const base = process.argv[2] || 'http://127.0.0.1:8153/';
const PAGES = ['home', 'index', 'article', 'wall', 'money', 'moving', 'count', 'harvest', 'khan-younis', 'tell', 'about', 'search', 'privacy', '404'];
const VPS = [[1440, 900], [768, 1024], [375, 812]];
const PROBE = readFileSync('C:/Users/Msi/.claude/skills/visual-qa/scripts/qa-checks.js', 'utf8');
const SPACING = `(() => {
  const vis = (el) => { const cs = getComputedStyle(el); if (cs.display === 'none' || cs.visibility === 'hidden') return false; const r = el.getBoundingClientRect(); return r.width > 0 && r.height > 0; };
  const path = (el) => { const p = []; for (let n = el; n && n.nodeType === 1 && p.length < 3; n = n.parentElement) { let s = n.tagName.toLowerCase(); if (n.id) { p.unshift(s + '#' + n.id); break; } const c = [...n.classList].slice(0, 2).join('.'); if (c) s += '.' + c; p.unshift(s); } return p.join(' > '); };
  const out = { innerGaps: [], edgeTouch: [], stuck: [], sectionGaps: [], tagClear: [] };
  // 1. blocks stretched beyond their content: the largest empty run between children
  document.querySelectorAll('.blk, .slab').forEach((b) => {
    if (!vis(b) || b.classList.contains('bat')) return;
    const kids = [...b.children].filter(vis).map((k) => k.getBoundingClientRect()).sort((a, c) => a.top - c.top);
    if (kids.length < 2) return;
    let max = 0;
    for (let i = 1; i < kids.length; i++) max = Math.max(max, kids[i].top - Math.max(...kids.slice(0, i).map((k) => k.bottom)));
    if (max > 56) out.innerGaps.push({ el: path(b), gap: Math.round(max), h: Math.round(b.getBoundingClientRect().height) });
  });
  // 2. text touching the inner edge of a filled or ruled container
  document.querySelectorAll('.blk, .slab, .strip .wrap, .chain, .foot, .howknow, .tellform, form, .mourn, .post').forEach((c) => {
    if (!vis(c)) return;
    const r = c.getBoundingClientRect();
    c.querySelectorAll('h1,h2,h3,p,li,small,span.chalk,label,a.btn').forEach((t) => {
      if (!vis(t) || !t.textContent.trim()) return;
      const q = t.getBoundingClientRect();
      const d = Math.min(q.left - r.left, r.right - q.right, q.top - r.top, r.bottom - q.bottom);
      if (d < 6 && d > -2 && !c.classList.contains('foot')) out.edgeTouch.push({ el: path(t), box: path(c), d: Math.round(d) });
    });
  });
  // 3. consecutive text blocks with no air between them
  document.querySelectorAll('main *, footer *, header *').forEach((p) => {
    const kids = [...p.children].filter((k) => vis(k) && k.textContent.trim() && getComputedStyle(k).display !== 'inline');
    for (let i = 1; i < kids.length; i++) {
      const a = kids[i - 1].getBoundingClientRect(), b = kids[i].getBoundingClientRect();
      const overlapX = Math.min(a.right, b.right) - Math.max(a.left, b.left);
      const gap = b.top - a.bottom;
      if (overlapX > 20 && gap < 2 && gap > -40) out.stuck.push({ a: path(kids[i - 1]), b: path(kids[i]), gap: Math.round(gap) });
    }
  });
  // 4. vertical air between the main's sections
  const secs = [...document.querySelectorAll('main > *, body > footer')].filter(vis);
  for (let i = 1; i < secs.length; i++) {
    const a = secs[i - 1], b = secs[i];
    const last = [...a.querySelectorAll('*')].filter(vis).reduce((m, n) => Math.max(m, n.getBoundingClientRect().bottom), a.getBoundingClientRect().top);
    const first = [...b.querySelectorAll('h1,h2,h3,p,img,.blk,.slab,.wall')].filter(vis).reduce((m, n) => Math.min(m, n.getBoundingClientRect().top), Infinity);
    out.sectionGaps.push({ from: path(a), to: path(b), gap: Math.round(first - last) });
  }
  // 5. the line's tag must clear the string
  document.querySelectorAll('.mline').forEach((l) => {
    const t = l.querySelector('.tag'), s = l.querySelector('svg');
    if (!t || !s || !vis(t)) return;
    out.tagClear.push({ id: l.id, clear: Math.round(s.getBoundingClientRect().top + s.getBoundingClientRect().height / 2 - t.getBoundingClientRect().bottom), lines: Math.round(t.getBoundingClientRect().height / 15) });
  });
  for (const k of Object.keys(out)) if (Array.isArray(out[k]) && k !== 'sectionGaps' && k !== 'tagClear') out[k] = out[k].slice(0, 25);
  return out;
})()`;

const CHROME = 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const port = 9300 + Math.floor(Math.random() * 400);
const prof = mkdtempSync(join(tmpdir(), 'po-qa-'));
const proc = spawn(CHROME, ['--headless=new', `--remote-debugging-port=${port}`, `--user-data-dir=${prof}`, '--hide-scrollbars', '--no-first-run', 'about:blank'], { stdio: 'ignore' });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let ws, id = 0; const pending = new Map();
const send = (method, params = {}) => new Promise((res, rej) => { const i = ++id; pending.set(i, { res, rej }); ws.send(JSON.stringify({ id: i, method, params })); });
const run = async (expression) => {
  const r = await send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true, replMode: true });
  if (r.exceptionDetails) return { error: r.exceptionDetails.exception?.description || r.exceptionDetails.text };
  return r.result.value;
};
const results = {};
try {
  let target;
  for (let k = 0; k < 50; k++) {
    try { target = (await (await fetch(`http://127.0.0.1:${port}/json`)).json()).find((t) => t.type === 'page'); if (target) break; } catch {}
    await sleep(150);
  }
  ws = new WebSocket(target.webSocketDebuggerUrl);
  await new Promise((r) => ws.addEventListener('open', r));
  ws.addEventListener('message', (ev) => { const m = JSON.parse(ev.data); if (m.id && pending.has(m.id)) { const p = pending.get(m.id); pending.delete(m.id); m.error ? p.rej(new Error(m.error.message)) : p.res(m.result); } });
  await send('Page.enable');
  await send('Page.addScriptToEvaluateOnNewDocument', { source: "try{sessionStorage.setItem('po-laid','1')}catch(e){}" });
  await send('Emulation.setEmulatedMedia', { features: [{ name: 'prefers-color-scheme', value: 'light' }] });
  for (const p of PAGES) {
    for (const [w, h] of VPS) {
      await send('Emulation.setDeviceMetricsOverride', { width: w, height: h, deviceScaleFactor: 1, mobile: w < 768 });
      await send('Page.navigate', { url: `${base}${p}.html` });
      await sleep(1500);
      await run("document.querySelectorAll('.lay').forEach(w=>w.classList.add('is-laid'));document.querySelectorAll('[data-spray]').forEach(w=>w.classList.add('is-sprayed'));1");
      await sleep(700);
      results[`${p}@${w}`] = { probe: await run(PROBE), spacing: await run(SPACING) };
      process.stdout.write('.');
    }
  }
  writeFileSync('.impeccable/review/qa.json', JSON.stringify(results, null, 1));
  console.log('\nwritten .impeccable/review/qa.json');
} finally {
  try { ws && ws.close(); } catch {}
  proc.kill();
}
