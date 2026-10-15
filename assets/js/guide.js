/* Pal-Online identity guide: the cover line answers the pointer, and the motion demos replay. */
(() => {
  const still = matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* cover: crossing the line plucks it where you crossed */
  const cover = document.getElementById('line-cover');
  if (cover && cover.__line) {
    let lastY = null;
    const zone = cover.parentElement;
    zone.addEventListener('pointermove', (ev) => {
      const r = cover.getBoundingClientRect();
      const mid = r.top + r.height / 2;
      if (lastY !== null && (lastY - mid) * (ev.clientY - mid) < 0 && ev.clientX >= r.left && ev.clientX <= r.right) {
        cover.__line.pluck((ev.clientX - r.left) / r.width, Math.min(14, 5 + Math.abs(ev.movementY || 4)));
      }
      lastY = ev.clientY;
    });
    zone.addEventListener('pointerleave', () => { lastY = null; });
  }

  /* demos */
  const snapLine = document.getElementById('line-snap');
  function snap() {
    if (!snapLine) return;
    const path = snapLine.querySelector('.string');
    if (still) return;
    const t0 = performance.now();
    const step = (t) => {
      const s = (t - t0) / 1000;
      const sag = s < .12 ? 26 : 26 * Math.exp(-(s - .12) / .11) * Math.cos((s - .12) * 2 * Math.PI * 6.2);
      path.setAttribute('d', `M0 30Q500 ${(30 + sag).toFixed(2)} 1000 30`);
      if (s < 1) requestAnimationFrame(step); else path.setAttribute('d', 'M0 30L1000 30');
    };
    requestAnimationFrame(step);
  }
  function lay() {
    const w = document.querySelector('.lay-demo');
    if (!w || still) return;
    w.classList.remove('replaying');
    void w.offsetWidth;
    w.classList.add('replaying');
  }
  function spray() {
    const el = document.querySelector('.mo .reg-demo');
    if (!el) return;
    el.classList.remove('is-sprayed');
    void el.offsetWidth;
    requestAnimationFrame(() => el.classList.add('is-sprayed'));
  }
  function loader() {
    try { sessionStorage.removeItem('po-laid'); } catch (e) { /* ignore */ }
    location.href = 'home.html';
  }
  const demos = { snap, lay, spray, loader };
  document.querySelectorAll('[data-demo]').forEach((b) => b.addEventListener('click', () => demos[b.dataset.demo]()));

  // show each demo once as it arrives
  if ('IntersectionObserver' in window && !still) {
    const io = new IntersectionObserver((entries) => entries.forEach((en) => {
      if (!en.isIntersecting) return;
      const k = en.target.dataset.auto;
      if (demos[k]) demos[k]();
      io.unobserve(en.target);
    }), { threshold: .6 });
    document.querySelectorAll('.mo').forEach((m) => {
      const b = m.querySelector('[data-demo]');
      if (b && b.dataset.demo !== 'loader') { m.dataset.auto = b.dataset.demo; io.observe(m); }
    });
  } else {
    spray();
  }
})();
