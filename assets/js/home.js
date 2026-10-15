/* Pal-Online homepage: the count wall and the gap-in-the-wall form. */
(() => {
  /* the count: one wall of a hundred, emptied to whichever source the reader picks */
  const btns = [...document.querySelectorAll('.fig-btn')];
  const cells = [...document.querySelectorAll('.hundred span:not(.bat)')];
  const cap = document.querySelector('.count-cap');
  const still = matchMedia('(prefers-reduced-motion: reduce)').matches;
  function show(btn) {
    const out = +btn.dataset.out;
    btns.forEach((b) => b.setAttribute('aria-pressed', String(b === btn)));
    cells.forEach((c, i) => {
      // blocks leave from the top course down, the way a wall is taken apart
      c.style.transitionDelay = still ? '0ms' : `${Math.abs(i - out) < 30 ? Math.abs(i - out) * 9 : 0}ms`;
      c.classList.toggle('is-out', i < out);
    });
    if (cap) cap.textContent = btn.dataset.cap;
  }
  btns.forEach((b) => b.addEventListener('click', () => show(b)));

  /* the form: say what is missing in plain words, then confirm without pretending to send */
  const form = document.querySelector('.tell form');
  if (form) {
    form.addEventListener('submit', (ev) => {
      ev.preventDefault();
      let first = null;
      form.querySelectorAll('.field').forEach((f) => {
        const input = f.querySelector('input,textarea');
        const bad = input.required && !input.value.trim();
        f.dataset.state = bad ? 'error' : '';
        input.setAttribute('aria-invalid', String(bad));
        const err = f.querySelector('.err');
        if (err) { err.id = err.id || `${input.id}-err`; input.setAttribute('aria-describedby', err.id); }
        if (bad && !first) first = input;
      });
      if (first) { first.focus(); return; }
      form.classList.add('is-sent');
      form.querySelector('.sent').focus?.();
    });
    form.addEventListener('input', (ev) => {
      const f = ev.target.closest('.field');
      if (f && f.dataset.state === 'error' && ev.target.value.trim()) { f.dataset.state = ''; ev.target.setAttribute('aria-invalid', 'false'); }
    });
  }
})();
