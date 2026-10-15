// Exports the social templates and avatars from the identity guide as PNG, through Chrome DevTools.
// node --experimental-websocket tools/social.mjs [base-url]   (the preview server must be running)
// Each post in index.html is sized in container units, so widening its frame to 1080 px renders it at 1080 x 1350.
import { spawn } from 'node:child_process';
import { mkdtempSync, writeFileSync, mkdirSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const base = process.argv[2] || 'http://127.0.0.1:8153/';
const OUT = 'assets/brand/social';
mkdirSync(OUT, { recursive: true });
const CHROME = 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const port = 9300 + Math.floor(Math.random() * 400);
const prof = mkdtempSync(join(tmpdir(), 'po-social-'));
const proc = spawn(CHROME, ['--headless=new', `--remote-debugging-port=${port}`, `--user-data-dir=${prof}`, '--hide-scrollbars', '--no-first-run', 'about:blank'], { stdio: 'ignore' });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let ws, id = 0; const pending = new Map();
const send = (method, params = {}) => new Promise((res, rej) => { const i = ++id; pending.set(i, { res, rej }); ws.send(JSON.stringify({ id: i, method, params })); });
const evalv = async (expression) => (await send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true })).result.value;

async function open(url, w, h) {
  await send('Emulation.setDeviceMetricsOverride', { width: w, height: h, deviceScaleFactor: 1, mobile: false });
  await send('Emulation.setEmulatedMedia', { features: [{ name: 'prefers-color-scheme', value: 'light' }, { name: 'prefers-reduced-motion', value: 'reduce' }] });
  await send('Page.navigate', { url });
  await sleep(1800);
  await evalv('document.fonts.ready.then(()=>1)');
}
async function shoot(clip, file, beyond = true) {
  const r = await send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: beyond, clip: { ...clip, scale: 1 } });
  writeFileSync(join(OUT, file), Buffer.from(r.data, 'base64'));
  console.log(join(OUT, file));
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

  await open(base + 'index.html', 1200, 1600);   // taller than a post plus the scroll padding, so the clip stays inside the viewport
  await evalv(`(()=>{const s=document.createElement('style');s.textContent='.g-top{display:none!important}.social{grid-template-columns:1080px!important;gap:40px!important}.social .frame{outline:0!important}';document.head.appendChild(s);return 1})()`);
  await sleep(500);
  const names = ['post-worker.png', 'post-number.png', 'post-quote.png', 'post-closed.png'];
  // scroll each frame to the top of a 1400 px viewport and capture it there: no layout shift from a stretched viewport
  for (let i = 0; i < names.length; i++) {
    await evalv(`(()=>{document.querySelectorAll('.social .frame')[${i}].scrollIntoView({block:'start'});return 1})()`);
    await sleep(500);
    const r = JSON.parse(await evalv(`(()=>{const r=document.querySelectorAll('.social .frame')[${i}].getBoundingClientRect();return JSON.stringify({x:r.left+scrollX,y:r.top+scrollY,width:r.width,height:r.height})})()`));
    await shoot(r, names[i], false);
  }

  for (const [svg, file] of [['mark-night.svg', 'avatar-night.png'], ['mark.svg', 'avatar-mortar.png'], ['mark-line.svg', 'avatar-line.png']]) {
    await open(`${base}assets/brand/${svg}`, 1080, 1080);
    await evalv(`(()=>{const s=document.querySelector('svg');s.setAttribute('width','1080');s.setAttribute('height','1080');document.documentElement.style.margin='0';return 1})()`);
    await shoot({ x: 0, y: 0, width: 1080, height: 1080 }, file);
  }
} finally {
  try { ws && ws.close(); } catch {}
  proc.kill();
}
