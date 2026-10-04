/* Kovovýroba Bučovice – návrh webu. Košík je jen ukázka (localStorage). */
(() => {
  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => [...el.querySelectorAll(s)];
  const PR = window.KB_PRODUCTS || {};
  const ROOT = document.body.dataset.root || '';
  const KEY = 'kb_kosik_demo';
  const kc = n => n.toLocaleString('cs-CZ').replace(/\s/g, ' ') + ' Kč';
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

  /* ── košík ── */
  const load = () => { try { return JSON.parse(localStorage.getItem(KEY)) || []; } catch (e) { return []; } };
  const save = c => { localStorage.setItem(KEY, JSON.stringify(c)); paintCount(); };
  const lineInfo = l => {
    const p = PR[l.s]; if (!p) return null;
    const v = l.v != null && p.v[l.v] ? p.v[l.v] : null;
    return { name: p.n, img: p.i, variant: v ? (p.vl ? p.vl + ': ' : '') + v[0] : '', price: v ? v[1] : p.p };
  };
  const total = c => c.reduce((a, l) => { const i = lineInfo(l); return a + (i ? i.price * l.q : 0); }, 0);
  function paintCount(bump) {
    const c = load(), n = c.reduce((a, l) => a + l.q, 0);
    $$('[data-cart-count]').forEach(el => {
      el.textContent = n; el.classList.toggle('has', n > 0);
      if (bump) { el.classList.remove('bump'); void el.offsetWidth; el.classList.add('bump'); }
    });
    $$('[data-cart-total]').forEach(el => el.textContent = kc(total(c)));
  }
  function add(slug, v = null, q = 1) {
    const c = load();
    const ex = c.find(l => l.s === slug && l.v === v);
    ex ? ex.q += q : c.push({ s: slug, v, q });
    save(c); paintCount(true);
    const i = lineInfo({ s: slug, v });
    const box = $('[data-drawer-item]');
    if (box && i) box.innerHTML = `<img src="${i.img}" alt=""><div><strong>${esc(i.name)}</strong><small>${esc(i.variant)}${i.variant ? ' · ' : ''}${q}× ${kc(i.price)}</small></div>`;
    open('#drawer');
  }
  const open = sel => { const el = $(sel); if (el) { el.classList.add('is-open'); el.setAttribute('aria-hidden', 'false'); } };
  const close = el => { el.classList.remove('is-open'); el.setAttribute('aria-hidden', 'true'); };
  document.addEventListener('click', e => {
    const c = e.target.closest('[data-close]');
    if (c) close(c.closest('.drawer,.modal'));
    const a = e.target.closest('[data-add]');
    if (a) { e.preventDefault(); const p = PR[a.dataset.add]; add(a.dataset.add, p && p.v.length ? 0 : null); }
    const inq = e.target.closest('[data-inquiry]');
    if (inq) { e.preventDefault(); inquiry(inq.dataset.inquiry); }
  });
  document.addEventListener('keydown', e => { if (e.key === 'Escape') $$('.drawer.is-open,.modal.is-open').forEach(close); });

  /* ── modal: ukázkové odeslání ── */
  function modal(html) { $('[data-modal-body]').innerHTML = html; open('#modal'); }
  const demoDone = what => modal(`<img class="modal__flame" src="${ROOT}assets/img/brand/plamen.svg" alt=""><h3>${what} by teď odešla</h3><p>Tohle je ukázka návrhu, takže se nic neodeslalo. Na hotovém webu by přišlo potvrzení e-mailem a Vám by zpráva dorazila do schránky nebo do administrace.</p><button class="btn btn--dark" data-close>Rozumím</button>`);
  function inquiry(topic) {
    modal(`<h3>Poptávka: ${esc(topic)}</h3><p>Napište, co potřebujete – rozměr, provedení, počet kusů. Ozveme se s nabídkou.</p>
      <form data-demo-form="Poptávka"><div class="fgrid"><label><span>Jméno</span><input required></label><label><span>E-mail</span><input type="email" required></label>
      <label class="span2"><span>Co byste potřebovali?</span><textarea rows="4" required></textarea></label></div>
      <button class="btn btn--fire" type="submit">Odeslat poptávku</button></form>`);
  }
  document.addEventListener('submit', e => {
    const f = e.target.closest('[data-demo-form]');
    if (f) { e.preventDefault(); demoDone(f.dataset.demoForm); f.reset && f.reset(); }
  });

  /* ── hlavička ── */
  const hdr = $('#hdr');
  const demoH = $('.demo-bar') ? $('.demo-bar').offsetHeight : 0;
  document.documentElement.style.setProperty('--demo-h', demoH + 'px');
  const onScroll = () => hdr && hdr.classList.toggle('is-solid', scrollY > (document.body.classList.contains('page-home') ? 40 : 0));
  addEventListener('scroll', onScroll, { passive: true }); onScroll();
  const burger = $('.burger');
  if (burger) burger.addEventListener('click', () => {
    const o = document.body.classList.toggle('menu-open'); burger.setAttribute('aria-expanded', o);
  });
  $$('#mnav a').forEach(a => a.addEventListener('click', () => document.body.classList.remove('menu-open')));

  /* ── reveal + countery ── */
  const targets = $$('.sec__head, .cat, .rev, .faq, .guide, .smrow, .szrow, .stat, .custom__card, .about__copy > *, .smokers__copy > *, .pd__desc, .shop__custom');
  targets.forEach(el => el.classList.add('rv'));
  const io = new IntersectionObserver(es => es.forEach(en => {
    if (!en.isIntersecting) return;
    const el = en.target;
    const sib = el.parentElement ? [...el.parentElement.children].indexOf(el) : 0;
    el.style.transitionDelay = (Math.min(sib, 6) * 70) + 'ms';
    el.classList.add('in'); io.unobserve(el);
    $$('.clip-reveal', el).forEach((c, i) => setTimeout(() => c.classList.add('in'), i * 250));
    $$('[data-count]', el).concat(el.matches('[data-count]') ? [el] : []).forEach(countUp);
  }), { rootMargin: '0px 0px -8% 0px', threshold: .08 });
  // clip-path: inset(100%) má nulovou plochu, proto se sleduje rodič
  const clipParents = [...new Set($$('.clip-reveal').map(c => c.parentElement))];
  targets.concat(clipParents).forEach(el => io.observe(el));
  function countUp(el) {
    const to = +el.dataset.count, suf = el.dataset.suffix || '', t0 = performance.now(), dur = 1600;
    const step = t => { const k = Math.min(1, (t - t0) / dur), e = 1 - Math.pow(1 - k, 4);
      el.textContent = Math.round(to * e).toLocaleString('cs-CZ') + suf; if (k < 1) requestAnimationFrame(step); };
    requestAnimationFrame(step);
  }

  /* ── magnetic tlačítko ── */
  if (matchMedia('(hover:hover)').matches) $$('.magnetic').forEach(b => {
    b.addEventListener('mousemove', e => { const r = b.getBoundingClientRect();
      b.style.transform = `translate(${(e.clientX - r.left - r.width / 2) * .18}px,${(e.clientY - r.top - r.height / 2) * .3}px)`; });
    b.addEventListener('mouseleave', () => b.style.transform = '');
  });

  /* ── výběr průměru ── */
  const ring = $('[data-ring]');
  if (ring) {
    const pick = size => {
      $$('.szchip').forEach(c => c.classList.toggle('is-on', c.dataset.size === size));
      const cm = parseInt(size, 10);
      ring.style.setProperty('--s', (cm / 100).toFixed(2));
      $('[data-ring-label]').textContent = 'Ø ' + size;
      $$('[data-size-row]').forEach(r => {
        const m = JSON.parse(r.dataset.sizeRow), v = m[size], out = $('[data-size-price]', r);
        r.classList.toggle('is-na', !v);
        out.innerHTML = v ? kc(v[0]) + (v[1] > v[0] ? `<s>${kc(v[1])}</s>` : '') : 'v tomto průměru není';
      });
    };
    $$('.szchip').forEach(c => c.addEventListener('click', () => pick(c.dataset.size)));
    pick(($('.szchip.is-on') || $('.szchip')).dataset.size);
  }

  /* ── rail ── */
  const rail = $('[data-rail-track]');
  $$('[data-rail]').forEach(b => b.addEventListener('click', () => rail.scrollBy({ left: +b.dataset.rail * rail.clientWidth * .8, behavior: 'smooth' })));

  /* ── obchod: filtr + řazení ── */
  const grid = $('[data-grid]');
  if (grid && $('[data-sort]')) {
    const cards = $$('.pcard', grid), orig = cards.slice();
    const cats = window.KB_CATS || {};
    const apply = (k, push) => {
      $$('.chip').forEach(c => c.classList.toggle('is-on', c.dataset.filter === k));
      cards.forEach(c => { const show = !k || c.dataset.cats.split(' ').includes(k);
        c.classList.toggle('is-hidden', !show); if (show) { c.classList.remove('is-in'); void c.offsetWidth; c.classList.add('is-in'); } });
      $('[data-shop-title]').textContent = k ? cats[k] : 'Obchod';
      if (push) history.replaceState(null, '', k ? '?k=' + k : location.pathname);
    };
    $$('.chip').forEach(c => c.addEventListener('click', () => apply(c.dataset.filter, true)));
    $('[data-sort]').addEventListener('change', e => {
      const v = e.target.value;
      const list = v ? cards.slice().sort((a, b) => (v === 'asc' ? 1 : -1) * (a.dataset.price - b.dataset.price)) : orig;
      list.forEach(c => grid.appendChild(c));
    });
    const k = new URLSearchParams(location.search).get('k') || '';
    apply(cats[k] ? k : '', false);
  }

  /* ── detail výrobku ── */
  const pd = $('[data-product]');
  if (pd) {
    const slug = pd.dataset.product, p = PR[slug];
    let vi = p.v.length ? 0 : null;
    const qty = $('[data-qty]');
    $$('.vchip').forEach(b => b.addEventListener('click', () => {
      vi = +b.dataset.v; $$('.vchip').forEach(x => x.classList.toggle('is-on', x === b));
      const v = p.v[vi]; $('[data-pd-price]').textContent = kc(v[1]);
      const o = $('[data-pd-old]'); o.hidden = !(v[2] > v[1]); o.textContent = kc(v[2]);
    }));
    $$('[data-q]').forEach(b => b.addEventListener('click', () => { qty.value = Math.max(1, (+qty.value || 1) + +b.dataset.q); }));
    $('[data-buy]').addEventListener('click', () => add(slug, vi, Math.max(1, +qty.value || 1)));
    const main = $('.gal__main img');
    $$('.gal__t').forEach(t => t.addEventListener('click', () => {
      $$('.gal__t').forEach(x => x.classList.toggle('is-on', x === t));
      main.style.opacity = 0;
      setTimeout(() => { main.removeAttribute('srcset'); main.src = t.dataset.full; main.onload = () => main.style.opacity = 1; }, 180);
    }));
  }

  /* ── stránka košíku ── */
  const citems = $('[data-citems]');
  if (citems) {
    const ship = () => { const id = ($('input[name=doprava]:checked') || {}).value; return (window.KB_SHIP || []).find(s => s.id === id); };
    const render = () => {
      const c = load();
      $('[data-cempty]').hidden = c.length > 0;
      citems.innerHTML = c.map((l, i) => { const x = lineInfo(l); if (!x) return '';
        return `<div class="citem"><img src="${x.img}" alt=""><div><div class="citem__n">${esc(x.name)}</div><div class="citem__v">${esc(x.variant)}</div><button class="citem__x" data-rm="${i}">Odebrat</button></div>
          <div class="qty"><button data-cq="${i}" data-d="-1" aria-label="Méně">−</button><input value="${l.q}" readonly aria-label="Počet"><button data-cq="${i}" data-d="1" aria-label="Více">+</button></div>
          <div class="citem__p">${kc(x.price * l.q)}</div></div>`; }).join('');
      const g = total(c), s = ship();
      $('[data-sum-goods]').textContent = kc(g);
      $('[data-sum-ship]').textContent = !s || s.price === 0 ? 'zdarma' : s.price == null ? 'dle dohody' : kc(s.price);
      $('[data-sum-total]').textContent = kc(g + (s && s.price ? s.price : 0));
    };
    citems.addEventListener('click', e => {
      const c = load(), rm = e.target.closest('[data-rm]'), q = e.target.closest('[data-cq]');
      if (rm) c.splice(+rm.dataset.rm, 1);
      if (q) { const l = c[+q.dataset.cq]; l.q = Math.max(1, l.q + +q.dataset.d); }
      if (rm || q) { save(c); render(); }
    });
    $$('input[name=doprava]').forEach(r => r.addEventListener('change', render));
    $('[data-order]').addEventListener('click', () => {
      if (!load().length) { modal('<h3>Košík je prázdný</h3><p>Přidejte si nejdřív něco z obchodu.</p><a class="btn btn--fire" href="obchod.html">Do obchodu</a>'); return; }
      demoDone('Objednávka');
    });
    render();
  }

  paintCount();
})();
