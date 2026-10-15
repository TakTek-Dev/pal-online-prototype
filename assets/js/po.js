/* Pal-Online — motion grammar: snap (the line), lay (the blocks), pluck (the signature),
   spray (a struck trade). Everything here is progressive: without JS the page is complete. */
(() => {
  const root = document.documentElement;
  const still = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const store = {
    get(k) { try { return sessionStorage.getItem(k); } catch (e) { return null; } },
    set(k, v) { try { sessionStorage.setItem(k, v); } catch (e) { /* private mode: fine */ } }
  };

  /* ---------- the line: a taut string drawn as one path, plucked by hand ---------- */
  const lines = [];
  function makeLine(el) {
    const svg = el.querySelector('svg');
    const path = el.querySelector('.string');
    const line = { el, svg, path, w: 1000, y: 15, raf: 0, start: 0, xp: .5, amp: 0 };
    const rest = () => path.setAttribute('d', `M0 ${line.y}L${line.w} ${line.y}`);
    line.rest = rest;
    line.pluck = (xFrac, amp = 7) => {
      if (still) return;
      const now = performance.now();
      if (line.raf && now - line.start < 140) return;      // one finger at a time
      line.xp = Math.min(.96, Math.max(.04, xFrac));
      line.amp = amp;
      line.start = now;
      cancelAnimationFrame(line.raf);
      const tick = (t) => {
        const k = (t - line.start) / 1000;
        const d = line.amp * Math.exp(-k / .17) * Math.cos(k * 2 * Math.PI * 8.5);
        const x = line.xp * line.w;
        path.setAttribute('d', `M0 ${line.y}L${x.toFixed(1)} ${(line.y + d).toFixed(2)}L${line.w} ${line.y}`);
        if (k < .9) line.raf = requestAnimationFrame(tick); else { line.raf = 0; rest(); }
      };
      line.raf = requestAnimationFrame(tick);
    };
    rest();
    lines.push(line);
    el.__line = line;
    return line;
  }
  document.querySelectorAll('.mline').forEach(makeLine);

  // blocks pluck the line laid above their wall
  document.querySelectorAll('[data-line]').forEach((wall) => {
    const lineEl = document.getElementById(wall.dataset.line);
    if (!lineEl || !lineEl.__line) return;
    const pluckFrom = (target) => {
      const blk = target.closest('.blk');
      if (!blk) return;
      const r = blk.getBoundingClientRect();
      const lr = lineEl.getBoundingClientRect();
      lineEl.__line.pluck((r.left + r.width / 2 - lr.left) / lr.width);
    };
    wall.addEventListener('pointerenter', (e) => { if (e.pointerType !== 'touch') pluckFrom(e.target); }, true);
    wall.addEventListener('focusin', (e) => pluckFrom(e.target));
    wall.addEventListener('pointerdown', (e) => { if (e.pointerType === 'touch') pluckFrom(e.target); });
  });

  /* ---------- lay: blocks are set course by course as a wall comes into view ---------- */
  if (!still && 'IntersectionObserver' in window) {
    root.classList.add('js-lay');
    const io = new IntersectionObserver((entries) => {
      entries.forEach((en) => {
        if (!en.isIntersecting) return;
        en.target.classList.add('is-laid');
        io.unobserve(en.target);
      });
    }, { rootMargin: '0px 0px -12% 0px', threshold: .08 });
    document.querySelectorAll('.lay').forEach((wall) => {
      [...wall.children].forEach((c, i) => c.style.setProperty('--i', Math.min(i, 14)));
      io.observe(wall);
    });
    // anything already on screen at load lays at once, after the loader if there is one
    requestAnimationFrame(() => document.querySelectorAll('.lay').forEach((w) => {
      const r = w.getBoundingClientRect();
      if (r.top < innerHeight && !root.classList.contains('is-loading')) { w.classList.add('is-laid'); io.unobserve(w); }
    }));
  }

  /* ---------- spray: a struck-through trade is sprayed when its row arrives ---------- */
  if ('IntersectionObserver' in window) {
    const so = new IntersectionObserver((entries) => entries.forEach((en) => {
      if (en.isIntersecting) { en.target.classList.add('is-sprayed'); so.unobserve(en.target); }
    }), { rootMargin: '0px 0px -18% 0px' });
    document.querySelectorAll('[data-spray]').forEach((el) => so.observe(el));
  } else {
    document.querySelectorAll('[data-spray]').forEach((el) => el.classList.add('is-sprayed'));
  }

  /* ---------- loader: once per session, the line snaps and the first block is laid ---------- */
  const loader = document.getElementById('loader');
  if (loader) {
    const seen = store.get('po-laid');
    if (still || seen) {
      loader.remove();
    } else {
      root.classList.add('is-loading');
      const string = loader.querySelector('.ld-string');
      const finish = () => {
        if (!loader.isConnected || loader.dataset.done) return;
        loader.dataset.done = '1';
        store.set('po-laid', '1');
        loader.classList.add('is-up');
        root.classList.remove('is-loading');
        document.querySelectorAll('.lay').forEach((w) => {
          if (w.getBoundingClientRect().top < innerHeight) w.classList.add('is-laid');
        });
        const first = document.querySelector('.mline');
        setTimeout(() => first && first.__line && first.__line.pluck(.5, 9), 260);
        setTimeout(() => loader.remove(), 900);
      };
      // the string snaps from slack to taut: a damped spring on the sag
      const t0 = performance.now();
      const snap = (t) => {
        const k = (t - t0) / 1000;
        if (k < .18) { string.setAttribute('d', 'M0 60Q500 60 1000 60'); requestAnimationFrame(snap); return; }
        const s = k - .18;
        const sag = 46 * Math.exp(-s / .11) * Math.cos(s * 2 * Math.PI * 6.2);
        string.setAttribute('d', `M0 60Q500 ${(60 + sag).toFixed(2)} 1000 60`);
        if (s < .8) requestAnimationFrame(snap);
      };
      requestAnimationFrame(snap);
      const timer = setTimeout(finish, 2050);
      const skip = () => { clearTimeout(timer); finish(); };
      loader.addEventListener('click', skip);
      addEventListener('keydown', skip, { once: true });
    }
  }

  /* ---------- the compact bar: a small block rides the line to show where you are ---------- */
  const bar = document.querySelector('.bar');
  const mast = document.querySelector('.mast');
  if (bar && mast && 'IntersectionObserver' in window) {
    new IntersectionObserver(([en]) => bar.classList.toggle('is-on', !en.isIntersecting), { threshold: 0 }).observe(mast);
    const rider = bar.querySelector('.bar-rider');
    let ticking = false;
    const place = () => {
      ticking = false;
      const max = document.documentElement.scrollHeight - innerHeight;
      const p = max > 0 ? Math.min(1, scrollY / max) : 0;
      rider && rider.style.setProperty('--p', p.toFixed(4));
    };
    addEventListener('scroll', () => { if (!ticking) { ticking = true; requestAnimationFrame(place); } }, { passive: true });
    place();
  }
})();
