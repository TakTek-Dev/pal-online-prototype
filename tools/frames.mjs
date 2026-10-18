// Captures the motion grammar frame by frame, so it can be checked without watching it.
// node --experimental-websocket tools/frames.mjs [base-url]   (the preview server must be running)
// Writes .impeccable/review/motion/<motion>-<ms>.png: pluck (the line answering a block),
// spray (a struck trade), lay (a course set into place).
import { spawn } from 'node:child_process';
import { mkdtempSync, writeFileSync, mkdirSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const base = process.argv[2] || 'http://127.0.0.1:8153/';
const OUT = '.impeccable/review/motion';
mkdirSync(OUT, { recursive: true });
const CHROME = 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const port = 9300 + Math.floor(Math.random() * 400);
const prof = mkdtempSync(join(tmpdir(), 'po-frames-'));
const proc = spawn(CHROME, ['--headless=new', `--remote-debugging-port=${port}`, `--user-data-dir=${prof}`, '--hide-scrollbars', '--no-first-run', 'about:blank'], { stdio: 'ignore' });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let ws, id = 0; const pending = new Map();
const send = (method, params = {}) => new Promise((res, rej) => { const i = ++id; pending.set(i, { res, rej }); ws.send(JSON.stringify({ id: i, method, params })); });
const evalv = async (expression) => (await send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true })).result.value;
async function open(url) {
  await send('Emulation.setDeviceMetricsOverride', { width: 1440, height: 900, deviceScaleFactor: 1, mobile: false });
  await send('Page.addScriptToEvaluateOnNewDocument', { source: "try{sessionStorage.setItem('po-laid','1')}catch(e){}" });
  await send('Page.navigate', { url });
  await sleep(1800);
  await evalv('document.fonts.ready.then(()=>1)');
}
async function shot(name, clip) {
  const r = await send('Page.captureScreenshot', { format: 'png', clip: { ...clip, scale: 1 } });
  writeFileSync(join(OUT, name), Buffer.from(r.data, 'base64'));
}
async function series(prefix, times, clip) {
  const t0 = Date.now();
  for (const t of times) {
    const wait = t - (Date.now() - t0);
    if (wait > 0) await sleep(wait);
    await shot(`${prefix}-${String(t).padStart(4, '0')}.png`, clip);
  }
}
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

  // pluck: point at a block in today's course; the line above it should swing and settle
  await open(base + 'home.html');
  const b = JSON.parse(await evalv(`JSON.stringify((()=>{const r=document.querySelectorAll('.hero .who')[1].getBoundingClientRect();const l=document.querySelector('#line-today').getBoundingClientRect();return {x:r.left+r.width/2,y:r.top+r.height/2,ly:l.top}})())`));
  await send('Input.dispatchMouseEvent', { type: 'mouseMoved', x: 5, y: 5 });
  await send('Input.dispatchMouseEvent', { type: 'mouseMoved', x: b.x, y: b.y });
  await series('pluck', [20, 60, 110, 170, 260, 420, 900], { x: 60, y: b.ly - 10, width: 1320, height: 60 });

  // spray: bring the register into view; the old trade should be struck left to right
  await evalv(`(()=>{document.querySelector('#trades').scrollIntoView({block:'start'});return 1})()`);
  const s = JSON.parse(await evalv(`JSON.stringify((()=>{const r=document.querySelector('.reg li').getBoundingClientRect();return {x:r.left,y:r.top+scrollY,w:r.width,h:r.height}})())`));
  await series('spray', [80, 300, 520, 760, 1200], { x: s.x, y: s.y, width: s.w, height: s.h });

  // lay: the chain's course, scrolled into view from below
  await evalv(`(()=>{scrollTo(0,0);return 1})()`);
  await sleep(300);
  await evalv(`(()=>{document.querySelector('#chain').scrollIntoView({block:'start'});return 1})()`);
  const c = JSON.parse(await evalv(`JSON.stringify((()=>{const r=document.querySelector('#chain .links').getBoundingClientRect();return {x:r.left,y:r.top+scrollY,w:r.width,h:r.height}})())`));
  await series('lay', [30, 150, 300, 500, 900], { x: c.x, y: c.y, width: c.w, height: c.h });
  console.log('frames written to', OUT);
} finally {
  try { ws && ws.close(); } catch {}
  proc.kill();
}
