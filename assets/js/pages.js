/* Pal-Online inner pages: filters that keep the wall bonded, the share link, the tell-us form, search. */
(() => {
  /* ---------- bond: after filtering or resizing, odd courses start and end on a cut half block ---------- */
  const bat = () => { const s = document.createElement('span'); s.className = 'blk h bat'; s.setAttribute('aria-hidden', 'true'); return s; };
  function bond(wall) {
    wall.querySelectorAll(':scope > .bat').forEach((b) => b.remove());
    const per = Math.floor((parseInt(getComputedStyle(wall).getPropertyValue('--halves'), 10) || 8) / 2);
    const blocks = [...wall.children].filter((c) => (c.classList.contains('blk') || c.classList.contains('blk--gap')) && !c.hidden);
    blocks.forEach((b) => b.classList.remove('pair'));
    if (per < 2) {                                        // a phone lays a whole block, then two halves side by side
      if (wall.classList.contains('people')) blocks.forEach((b, i) => { if (i % 3) b.classList.add('pair'); });
      return;
    }
    blocks.forEach((b) => { b.style.gridColumn = ''; });
    for (let i = 0, row = 0; i < blocks.length; row++) {
      if (row % 2 === 0) {
        const take = Math.min(per, blocks.length - i);
        if (take < per) blocks[i + take - 1].style.gridColumn = `span ${2 + 2 * (per - take)}`;   // a short course is closed, not left open
        i += take; continue;
      }
      const take = Math.min(per - 1, blocks.length - i);
      blocks[i].before(bat());
      if (take === per - 1) blocks[i + take - 1].after(bat());
      else blocks[i + take - 1].style.gridColumn = `span ${2 + 2 * (per - 1 - take) + 1}`;
      i += take;
    }
  }
  const bonded = [...document.querySelectorAll('[data-bond]')];
  bonded.forEach(bond);
  let rt = 0;
  addEventListener('resize', () => { clearTimeout(rt); rt = setTimeout(() => bonded.forEach(bond), 120); });

  /* ---------- filters: plain buttons, one choice per group ---------- */
  document.querySelectorAll('.filters').forEach((f) => {
    const target = f.parentElement.querySelector('.wall.people, [data-board]');
    if (!target) return;
    const state = { g: 'all', w: 'all' };
    const apply = () => {
      let n = 0;
      [...target.children].forEach((c) => {
        if (c.classList.contains('bat') || c.classList.contains('empty') || c.classList.contains('gapblk')) return;
        const ok = (state.g === 'all' || c.dataset.g === state.g) && (state.w === 'all' || c.dataset.w === state.w);
        if (ok && c.hidden) { c.classList.remove('is-in'); void c.offsetWidth; c.classList.add('is-in'); }
        c.hidden = !ok;
        if (ok) n++;
      });
      const empty = target.querySelector('.empty');
      if (empty) empty.hidden = n > 0;
      const out = f.querySelector('.tally b');
      if (out) out.textContent = n;
      if (target.hasAttribute('data-bond')) bond(target);
    };
    f.querySelectorAll('button[data-g], button[data-w]').forEach((b) => b.addEventListener('click', () => {
      const key = 'g' in b.dataset ? 'g' : 'w';
      state[key] = b.dataset[key];
      b.parentElement.querySelectorAll('button').forEach((x) => x.setAttribute('aria-pressed', String(x === b)));
      apply();
    }));
  });

  /* ---------- share: copy the link and say so ---------- */
  document.querySelectorAll('[data-copy]').forEach((b) => b.addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText(location.href.split('#')[0]);
      b.textContent = 'Link copied';
      b.classList.add('done');
    } catch (err) {
      b.textContent = 'Copy the address bar instead';
    }
    setTimeout(() => { b.textContent = 'Copy link'; b.classList.remove('done'); }, 2400);
  }));

  /* ---------- tell us your work: name what is missing, then confirm without pretending to send ---------- */
  const form = document.querySelector('.tellform');
  if (form) {
    form.addEventListener('submit', (ev) => {
      ev.preventDefault();
      let first = null;
      form.querySelectorAll('.field').forEach((fl) => {
        const input = fl.querySelector('input,textarea');
        const bad = input.type === 'checkbox' ? input.required && !input.checked : input.required && !input.value.trim();
        fl.dataset.state = bad ? 'error' : '';
        input.setAttribute('aria-invalid', String(bad));
        const err = fl.querySelector('.err');
        if (err) { err.id = err.id || `${input.id}-err`; input.setAttribute('aria-describedby', err.id); }
        if (bad && !first) first = input;
      });
      if (first) { first.focus(); return; }
      form.classList.add('is-sent');
      form.querySelector('.sent').focus();
    });
    const clear = (ev) => {
      const fl = ev.target.closest('.field');
      const filled = ev.target.type === 'checkbox' ? ev.target.checked : ev.target.value.trim();
      if (fl && fl.dataset.state === 'error' && filled) { fl.dataset.state = ''; ev.target.setAttribute('aria-invalid', 'false'); }
    };
    form.addEventListener('input', clear);
    form.addEventListener('change', clear);
  }

  /* ---------- search: every checked item, matched word by word ---------- */
  const idx = document.getElementById('search-index');
  if (idx) {
    const items = JSON.parse(idx.textContent);
    const q = document.getElementById('q');
    const list = document.querySelector('[data-results]');
    const empty = document.querySelector('[data-empty]');
    const n = document.querySelector('[data-n]');
    const sum = document.querySelector('[data-sum]');
    let desk = 'all';
    const esc = (s) => s.replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
    const fold = (s) => s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[’']/g, '');
    const mark = (text, words) => {
      let out = esc(text);
      words.forEach((w) => {
        if (w.length < 2) return;
        const re = new RegExp(`(${w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'ig');
        out = out.replace(re, '<mark>$1</mark>');
      });
      return out;
    };
    const deskName = { work: 'Work', money: 'Money', prices: 'Prices', moving: 'Moving', count: 'The count' };
    function render() {
      const raw = q.value.trim();
      const words = fold(raw).split(/\s+/).filter(Boolean);
      const hits = items.filter((it) => (desk === 'all' || it.desk === desk) &&
        words.every((w) => fold(`${it.t} ${it.s} ${it.p} ${it.n} ${it.o}`).includes(w)));
      list.innerHTML = hits.map((it) => `<li><div><h3><a href="${esc(it.u)}" rel="noopener">${mark(it.t, raw.split(/\s+/))}</a></h3>
        <p>${mark(it.s, raw.split(/\s+/))}</p><p class="meta"><b>${deskName[it.desk] || ''}</b> · ${esc(it.p)} · ${esc(it.o)}, ${esc(it.d)}</p></div></li>`).join('');
      empty.hidden = hits.length > 0;
      n.innerHTML = `<b>${hits.length}</b> ${hits.length === 1 ? 'report' : 'reports'}`;
      sum.textContent = raw ? `“${raw}”` : 'All reports';
      const url = new URL(location.href);
      if (raw) url.searchParams.set('q', raw); else url.searchParams.delete('q');
      history.replaceState(null, '', url);
    }
    let t = 0;
    q.addEventListener('input', () => { clearTimeout(t); t = setTimeout(render, 110); });
    q.form.addEventListener('submit', (ev) => { ev.preventDefault(); render(); });
    document.querySelectorAll('[data-q]').forEach((b) => b.addEventListener('click', () => { q.value = b.dataset.q; render(); q.focus(); }));
    document.querySelectorAll('button[data-desk]').forEach((b) => b.addEventListener('click', () => {
      desk = b.dataset.desk;
      document.querySelectorAll('button[data-desk]').forEach((x) => x.setAttribute('aria-pressed', String(x === b)));
      render();
    }));
    q.value = new URLSearchParams(location.search).get('q') || '';
    render();
  }
})();
