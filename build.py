#!/usr/bin/env python3
"""Vygeneruje web z _data/*.json: index, obchod, produkt/<slug>.html, kosik.

  python3 build.py
"""
import hashlib, html, json, os, re
from pathlib import Path

ROOT = Path(__file__).parent
S = json.loads((ROOT / "_data/site.json").read_text())
P = json.loads((ROOT / "_data/products.json").read_text())
C = json.loads((ROOT / "_data/categories.json").read_text())
BY = {p["slug"]: p for p in P}
CAT = {c["slug"]: c for c in C}
e = html.escape


def ver(path):
    return hashlib.md5((ROOT / path).read_bytes()).hexdigest()[:8]


def kc(n):
    return f"{n:,}".replace(",", " ") + " Kč"


def price_html(p, cls="price"):
    if p["range"] and p["range"][0] != p["range"][1]:
        return f'<span class="{cls}"><small>od</small> {kc(p["range"][0])}</span>'
    old = f' <s>{kc(p["regular"])}</s>' if p["regular"] > p["price"] else ""
    return f'<span class="{cls}">{kc(p["price"])}{old}</span>'


def img(src, alt, r, cls="", sizes="", lazy=True, w=None, h=None):
    thumb = src.replace(".webp", "-s.webp")
    a = f' class="{cls}"' if cls else ""
    l = ' loading="lazy" decoding="async"' if lazy else ' fetchpriority="high"'
    wh = f' width="{w}" height="{h}"' if w else ""
    s = f' sizes="{sizes}"' if sizes else ""
    return (f'<img{a} src="{r}{src}" srcset="{r}{thumb} 640w, {r}{src} 1400w"{s} alt="{e(alt)}"{l}{wh}>')


def card(p, r):
    im = p["images"][0]
    cats = " ".join(p["cats"])
    sale = '<span class="tag">Akce</span>' if p["regular"] > p["price"] else ""
    return f'''<article class="pcard" data-cats="{cats}" data-price="{p['price']}">
  <a href="{r}produkt/{p['slug']}.html" class="pcard__media">{sale}{img(im['src'], p['name'], r, sizes='(max-width:700px) 50vw, 320px')}</a>
  <div class="pcard__body">
    <h3><a href="{r}produkt/{p['slug']}.html">{e(p['name'])}</a></h3>
    <div class="pcard__foot">{price_html(p)}
      <button class="pcard__add" data-add="{p['slug']}" aria-label="Přidat do košíku: {e(p['name'])}"><svg viewBox="0 0 24 24"><path d="M12 5v14M5 12h14"/></svg></button>
    </div>
  </div>
</article>'''


ICON = {
    "cart": '<svg viewBox="0 0 24 24" class="ico"><path d="M3 4h2l2.2 10.5a2 2 0 0 0 2 1.5h7.6a2 2 0 0 0 2-1.5L20.5 8H6.2"/><circle cx="10" cy="20" r="1.3"/><circle cx="17" cy="20" r="1.3"/></svg>',
    "arrow": '<svg viewBox="0 0 24 24" class="ico"><path d="M5 12h14M13 6l6 6-6 6"/></svg>',
    "phone": '<svg viewBox="0 0 24 24" class="ico"><path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2"/></svg>',
    "mail": '<svg viewBox="0 0 24 24" class="ico"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/></svg>',
    "pin": '<svg viewBox="0 0 24 24" class="ico"><path d="M12 21s-7-6.2-7-12a7 7 0 0 1 14 0c0 5.8-7 12-7 12z"/><circle cx="12" cy="9" r="2.5"/></svg>',
    "star": '<svg viewBox="0 0 24 24" class="star"><path d="m12 3 2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1L3.2 9.5l6.1-.9z"/></svg>',
}


def head(title, desc, r, extra=""):
    css, js = ver("assets/style.css"), ver("assets/app.js")
    return f'''<!DOCTYPE html>
<html lang="cs">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="icon" href="{r}favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@100..125,400..700&family=Instrument+Serif:ital@0;1&family=Inter+Tight:wght@300..600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{r}assets/style.css?v={css}">
<script src="{r}assets/app.js?v={js}" defer></script>
{extra}</head>
'''


def header(r, page):
    nav = [("obchod.html", "Obchod", "obchod"), ("obchod.html?k=ohniste", "Ohniště", ""), ("obchod.html?k=udirny", "Udírny", ""),
           ("index.html#zakazka", "Na zakázku", ""), ("index.html#o-nas", "O nás", ""), ("index.html#kontakt", "Kontakt", "")]
    links = "".join(f'<a href="{r}{h}"{" aria-current=page" if page == k and k else ""}>{t}</a>' for h, t, k in nav)
    transparent = " hdr--over" if page == "home" else ""
    return f'''<body class="page-{page}" data-root="{r}">
<div class="demo-bar"><span class="demo-bar__dot"></span>{e(S['demo_bar'])}</div>
<header class="hdr{transparent}" id="hdr">
  <div class="hdr__in">
    <a href="{r}index.html" class="hdr__logo" aria-label="Kovovýroba Bučovice – úvod">
      <img src="{r}assets/img/brand/logo-light.png" alt="Kovovýroba Bučovice" class="logo-light" width="201" height="56">
      <img src="{r}assets/img/brand/logo-dark.png" alt="" class="logo-dark" width="201" height="56" aria-hidden="true">
    </a>
    <nav class="hdr__nav" aria-label="Hlavní menu">{links}</nav>
    <div class="hdr__act">
      <a href="{r}kosik.html" class="cart-btn" aria-label="Košík">{ICON['cart']}<span class="cart-count" data-cart-count>0</span></a>
      <button class="burger" aria-label="Menu" aria-expanded="false"><span></span><span></span></button>
    </div>
  </div>
</header>
<div class="mnav" id="mnav"><nav>{links}</nav>
  <div class="mnav__c"><a href="tel:{S['contact']['phone_href']}">{S['contact']['phone']}</a><a href="mailto:{S['contact']['email']}">{S['contact']['email']}</a></div>
</div>
'''


def drawer(r):
    return f'''<div class="drawer" id="drawer" aria-hidden="true">
  <div class="drawer__bg" data-close></div>
  <aside class="drawer__panel" role="dialog" aria-label="Košík">
    <div class="drawer__head"><strong>Přidáno do košíku</strong><button data-close aria-label="Zavřít">×</button></div>
    <div class="drawer__item" data-drawer-item></div>
    <div class="drawer__sum"><span>Celkem v košíku</span><strong data-cart-total>0 Kč</strong></div>
    <a href="{r}kosik.html" class="btn btn--fire btn--block">Přejít do košíku {ICON['arrow']}</a>
    <button class="btn btn--ghost btn--block" data-close>Pokračovat v nákupu</button>
    <p class="drawer__note">Ukázka návrhu – košík funguje jen v tomto prohlížeči.</p>
  </aside>
</div>
<div class="modal" id="modal" aria-hidden="true"><div class="modal__bg" data-close></div>
  <div class="modal__box" role="dialog"><button class="modal__x" data-close aria-label="Zavřít">×</button><div data-modal-body></div></div>
</div>
'''


def footer(r):
    c = S["contact"]
    cats = "".join(f'<a href="{r}obchod.html?k={x["slug"]}">{e(x["name"])}</a>' for x in C)
    return f'''<footer class="ftr" id="kontakt">
  <div class="wrap">
    <div class="ftr__top">
      <div class="ftr__big">
        <p class="eyebrow eyebrow--light">Kontakt</p>
        <h2 class="ftr__title">Poradíme s výběrem.<br><em>Napište nebo zavolejte.</em></h2>
        <div class="ftr__direct">
          <a href="tel:{c['phone_href']}" class="ftr__line">{ICON['phone']}<span>{c['phone']}</span></a>
          <a href="mailto:{c['email']}" class="ftr__line">{ICON['mail']}<span>{c['email']}</span></a>
          <a href="{c['map']}" target="_blank" rel="noopener" class="ftr__line">{ICON['pin']}<span>{c['address']}</span></a>
        </div>
      </div>
      <form class="ftr__form" data-demo-form="Zpráva">
        <p class="ftr__formtitle">Napište nám</p>
        <label><span>Jméno</span><input name="jmeno" required autocomplete="name"></label>
        <label><span>E-mail</span><input name="email" type="email" required autocomplete="email"></label>
        <label><span>Vaše zpráva</span><textarea name="zprava" rows="4" required></textarea></label>
        <button class="btn btn--fire" type="submit">Odeslat zprávu {ICON['arrow']}</button>
      </form>
    </div>
    <div class="ftr__cols">
      <div><img src="{r}assets/img/brand/logo-light.png" alt="Kovovýroba Bučovice" class="ftr__logo" width="201" height="56" loading="lazy">
        <p class="ftr__small">{c['person']}<br>{c['workshop_label']}<br>{c['address']}</p></div>
      <div><h4>Obchod</h4>{cats}</div>
      <div><h4>Informace</h4><a href="{r}index.html#o-nas">O nás</a><a href="{r}index.html#zakazka">Výroba na zakázku a spolupráce</a><a href="{r}index.html#dotazy">Nejčastější dotazy</a><a href="{r}kosik.html">Doprava a platba</a></div>
      <div><h4>Sledujte nás</h4><a href="{c['facebook']}" target="_blank" rel="noopener">Facebook – {e(c['facebook_label'])}</a><a href="{c['instagram']}" target="_blank" rel="noopener">Instagram {c['instagram_label']}</a>
        <p class="ftr__small">Fakturační údaje: {c['billing_name']}, IČO {c['ico']}</p></div>
    </div>
    <div class="ftr__bottom"><span>© 2026 Kovovýroba Bučovice</span><span>Návrh webu: Studentské Weby</span></div>
  </div>
</footer>
'''


def products_js(r):
    slim = {p["slug"]: {"n": p["name"], "p": p["price"], "o": p["regular"], "i": r + p["images"][0]["src"].replace(".webp", "-s.webp"),
                        "vl": p["variant_label"], "v": [[v["label"], v["price"], v["regular"]] for v in p["variants"]]} for p in P}
    return "<script>window.KB_PRODUCTS=" + json.dumps(slim, ensure_ascii=False) + ";window.KB_SHIP=" + json.dumps(S["shipping"], ensure_ascii=False) + ";</script>\n"


def tail(r):
    return drawer(r) + products_js(r) + "</body>\n</html>\n"


# ───────────────────────────── INDEX ─────────────────────────────
def build_index():
    r = ""
    h = S["hero"]
    bp = BY[h["badge_product"]]
    words = lambda t: " ".join(f'<span class="w"><span>{e(x)}</span></span>' for x in t.split())
    facts = "".join(f"<li>{e(f)}</li>" for f in h["facts"])
    mq = "".join(f'<span>{e(m)}</span><img src="assets/img/brand/plamen.svg" alt="" aria-hidden="true">' for m in S["marquee"])

    # kategorie
    cat_cards = []
    for i, c in enumerate(C):
        ps = [p for p in P if c["slug"] in p["cats"]]
        mn = min((p["range"][0] if p["range"] else p["price"]) for p in ps)
        cat_cards.append(f'''<a href="obchod.html?k={c['slug']}" class="cat cat--{i}">
  {img(S['category_images'][c['slug']], c['name'], r, sizes='(max-width:700px) 100vw, 40vw')}
  <span class="cat__shade"></span>
  <span class="cat__txt"><span class="cat__count">{c['count']} výrobků · od {kc(mn)}</span><span class="cat__name">{e(c['name'])}</span></span>
  <span class="cat__go">{ICON['arrow']}</span>
</a>''')

    # velikosti
    sz = S["sizes"]
    sp = [BY[s] for s in sz["products"]]
    sizes_all = ["60 cm", "70 cm", "80 cm", "90 cm", "100 cm"]
    chips = "".join(f'<button class="szchip{" is-on" if s == sz["default"] else ""}" data-size="{s}">Ø {s}</button>' for s in sizes_all)
    rows = "".join(f'''<a class="szrow" href="produkt/{p['slug']}.html" data-size-row='{json.dumps({v["label"]: [v["price"], v["regular"]] for v in p["variants"]}, ensure_ascii=False)}'>
  <span class="szrow__img">{img(p['images'][0]['src'], p['name'], r, sizes='80px')}</span>
  <span class="szrow__name">{e(p['name'])}</span><span class="szrow__price" data-size-price>–</span>{ICON['arrow']}</a>''' for p in sp)

    # akční sety
    sety = [p for p in P if "akcni-sety" in p["cats"]]
    sety_cards = "".join(card(p, r) for p in sety)

    a = S["about"]
    stats = "".join(f'<div class="stat"><span class="stat__n" data-count="{s["n"]}" data-suffix="{s.get("suffix", "")}">0</span><span class="stat__l">{e(s["label"])}</span></div>' for s in a["stats"])
    paras = "".join(f"<p>{e(x)}</p>" for x in a["p"])

    sm = S["smokers"]
    sm_list = "".join(f'<a href="produkt/{BY[s]["slug"]}.html" class="smrow"><span>{e(BY[s]["name"])}</span>{price_html(BY[s])}</a>' for s in sm["products"])

    cu = S["custom"]
    rv = "".join(f'<figure class="rev"><div class="rev__stars">{ICON["star"] * 5}</div><blockquote>„{e(x["text"])}“</blockquote><figcaption>{e(x["name"])}</figcaption></figure>' for x in S["reviews"])
    faq = "".join(f'<details class="faq"><summary>{e(x["q"])}<span class="faq__pm"></span></summary><p>{e(x["a"])}</p></details>' for x in S["faq"])
    guides = "".join(f'<article class="guide"><span class="guide__n">0{i+1}</span><h3>{e(g["title"])}</h3><p>{e(g["text"])}</p></article>' for i, g in enumerate(S["guides"]))

    out = head(S["title"], S["description"], r, f'<link rel="preload" as="image" href="{h["image"]}">\n') + header(r, "home") + f'''
<main>
<section class="hero">
  <div class="hero__left">
    <div class="hero__glow" aria-hidden="true"></div>
    <div class="hero__copy">
      <p class="eyebrow eyebrow--light reveal-up">{e(h['eyebrow'])}</p>
      <h1 class="hero__h1"><span class="line">{words(h['h1_a'])}</span><span class="line">{words(h['h1_b'])}</span><span class="line line--em"><em>{words(h['h1_em'])}</em></span></h1>
      <p class="hero__lead reveal-up" style="--d:.7s">{e(h['lead'])}</p>
      <div class="hero__cta reveal-up" style="--d:.85s">
        <a href="obchod.html?k=ohniste" class="btn btn--fire magnetic">{e(h['cta'])} {ICON['arrow']}</a>
        <a href="#zakazka" class="btn btn--line">{e(h['cta2'])}</a>
      </div>
      <ul class="hero__facts reveal-up" style="--d:1s">{facts}</ul>
    </div>
    <a href="#kategorie" class="scroll-ind" aria-label="Posunout dolů"><span></span>Scroll</a>
  </div>
  <div class="hero__right">
    <div class="hero__img">{img(h['image'], 'Zahradní ohniště s polohovatelným roštem', r, sizes='55vw', lazy=False, w=1254, h=1254)}</div>
    <a href="produkt/{bp['slug']}.html" class="hero__badge">
      <span class="hero__badge-l">{e(h['badge_label'])}</span>
      <span class="hero__badge-p"><small>od</small> {kc(bp['range'][0])}</span>
      <span class="hero__badge-s">Ø 60–120 cm {ICON['arrow']}</span>
    </a>
  </div>
</section>

<div class="marquee" aria-hidden="true"><div class="marquee__track">{mq}{mq}</div></div>

<section class="sec cats" id="kategorie">
  <div class="wrap">
    <div class="sec__head">
      <div><p class="eyebrow">Obchod</p><h2 class="h2">Co vyrábíme <em>a co u nás koupíte</em></h2></div>
      <a href="obchod.html" class="link-u">Všech {len(P)} výrobků {ICON['arrow']}</a>
    </div>
    <div class="cats__grid">{''.join(cat_cards)}</div>
  </div>
</section>

<section class="sec sizes" id="velikost">
  <div class="wrap sizes__in">
    <div class="sizes__copy">
      <p class="eyebrow">{e(sz['eyebrow'])}</p>
      <h2 class="h2">{e(sz['title'])}</h2>
      <p class="sizes__lead">{e(sz['lead'])}</p>
      <div class="szchips" role="group" aria-label="Průměr ohniště">{chips}</div>
      <div class="szrows">{rows}</div>
    </div>
    <div class="sizes__viz" aria-hidden="true">
      <div class="ring-stage">
        <div class="ring ring--ghost" style="--s:1"></div>
        <div class="ring" data-ring style="--s:.8"><span class="ring__label" data-ring-label>Ø 80 cm</span></div>
        <div class="ring__person"><span>100 cm</span></div>
      </div>
      <p class="sizes__note">Kruh v měřítku: plná čára je zvolený průměr, tečkovaná 100 cm.</p>
    </div>
  </div>
</section>

<section class="sec sets">
  <div class="wrap">
    <div class="sec__head">
      <div><p class="eyebrow">Akční sety</p><h2 class="h2">Ohniště rovnou <em>s víkem, roštem a vidlicemi</em></h2></div>
      <div class="rail-nav"><button data-rail="-1" aria-label="Předchozí">‹</button><button data-rail="1" aria-label="Další">›</button></div>
    </div>
  </div>
  <div class="rail" data-rail-track>{sety_cards}</div>
</section>

<section class="about" id="o-nas">
  <div class="wrap about__in">
    <div class="about__media">
      <div class="about__img clip-reveal">{img(a['image'], 'Ohniště z dílny Kovovýroba Bučovice', r, sizes='(max-width:900px) 100vw, 45vw')}</div>
      <div class="about__img2 clip-reveal">{img(a['image2'], 'Elegantní ohniště', r, sizes='30vw')}</div>
    </div>
    <div class="about__copy">
      <p class="eyebrow eyebrow--light">{e(a['eyebrow'])}</p>
      <h2 class="h2 h2--light">{e(a['title_a'])} <em>{e(a['title_em'])}</em></h2>
      {paras}
      <blockquote class="about__quote">„{e(a['quote'])}“</blockquote>
    </div>
  </div>
  <div class="wrap stats">{stats}</div>
  <div class="about__word" aria-hidden="true">opeč špek</div>
</section>

<section class="sec smokers">
  <div class="wrap smokers__in">
    <div class="smokers__media">
      <div class="smokers__tall">{img(sm['image'], 'Uzení v udírně ze sudu', r, sizes='(max-width:900px) 100vw, 40vw')}</div>
      <div class="smokers__sq">{img(sm['image2'], 'Udírna ze sudu', r, sizes='25vw')}</div>
    </div>
    <div class="smokers__copy">
      <p class="eyebrow">{e(sm['eyebrow'])}</p>
      <h2 class="h2">{e(sm['title_a'])} <em>{e(sm['title_em'])}</em></h2>
      <p class="smokers__text">{e(sm['text'])}</p>
      <div class="smlist">{sm_list}</div>
      <a href="obchod.html?k=udirny" class="link-u">Všechny udírny a příslušenství {ICON['arrow']}</a>
    </div>
  </div>
</section>

<section class="custom" id="zakazka">
  <div class="custom__bg">{img(cu['image'], 'Ohniště na zakázku', r, sizes='100vw')}</div>
  <div class="wrap custom__in">
    <div class="custom__card">
      <p class="eyebrow">{e(cu['eyebrow'])}</p>
      <h2 class="h2">{e(cu['title_a'])} <em>{e(cu['title_em'])}</em></h2>
      <p>{e(cu['text'])}</p>
      <div class="custom__b2b"><h3>{e(cu['b2b_title'])}</h3><p>{e(cu['b2b_text'])}</p></div>
      <button class="btn btn--fire" data-inquiry="Výroba na zakázku">Poptat výrobu na míru {ICON['arrow']}</button>
    </div>
  </div>
</section>

<section class="sec reviews">
  <div class="wrap">
    <div class="sec__head"><div><p class="eyebrow">Hodnocení zákazníků</p><h2 class="h2">Co říkají <em>ti, kdo už zapálili</em></h2></div><p class="reviews__note">{e(S['reviews_note'])}</p></div>
    <div class="reviews__grid">{rv}</div>
  </div>
</section>

<section class="sec faqsec" id="dotazy">
  <div class="wrap faqsec__in">
    <div><p class="eyebrow">Nejčastější dotazy</p><h2 class="h2">Než si <em>vyberete</em></h2>
      <div class="guides"><p class="eyebrow eyebrow--small">Rady a tipy</p>{guides}</div></div>
    <div class="faqs">{faq}</div>
  </div>
</section>
</main>
''' + footer(r) + tail(r)
    (ROOT / "index.html").write_text(out)


# ───────────────────────────── OBCHOD ─────────────────────────────
def build_shop():
    r = ""
    chips = '<button class="chip is-on" data-filter="">Vše <span>' + str(len(P)) + "</span></button>" + "".join(
        f'<button class="chip" data-filter="{c["slug"]}">{e(c["short"])} <span>{c["count"]}</span></button>' for c in C)
    cards = "".join(card(p, r) for p in P)
    out = head("Obchod – Kovovýroba Bučovice", "Ohniště, udírny, grily, rošty a doplňky z Kovovýroby Bučovice.", r) + header(r, "obchod") + f'''
<main class="shop">
  <section class="shop__head">
    <div class="wrap">
      <nav class="crumbs"><a href="index.html">Úvod</a><span>/</span><span>Obchod</span></nav>
      <h1 class="shop__h1" data-shop-title>Obchod</h1>
      <p class="shop__lead" data-shop-lead>Ohniště z naší dílny, udírny, exkluzivní grily a všechno, co se k ohni hodí.</p>
    </div>
  </section>
  <div class="shop__bar">
    <div class="wrap shop__bar-in">
      <div class="chips" role="group" aria-label="Kategorie">{chips}</div>
      <label class="sort"><span>Řadit</span><select data-sort><option value="">Doporučené</option><option value="asc">Od nejlevnějšího</option><option value="desc">Od nejdražšího</option></select></label>
    </div>
  </div>
  <div class="wrap"><div class="pgrid" data-grid>{cards}</div>
    <div class="shop__custom"><div><h2 class="h3">Nenašli jste, co jste hledali?</h2><p>Vyrábíme také na zakázku – ohniště ve speciálním rozměru, brány, ploty a další kovové výrobky.</p></div>
      <button class="btn btn--dark" data-inquiry="Výroba na zakázku">Poptat výrobu na míru {ICON['arrow']}</button></div>
  </div>
</main>
<script>window.KB_CATS={json.dumps({c['slug']: c['name'] for c in C}, ensure_ascii=False)};</script>
''' + footer(r) + tail(r)
    (ROOT / "obchod.html").write_text(out)


# ───────────────────────────── PRODUKT ─────────────────────────────
def build_products():
    r = "../"
    (ROOT / "produkt").mkdir(exist_ok=True)
    for p in P:
        cat = CAT.get(p["cats"][0]) if p["cats"] else None
        ims = p["images"]
        main = img(ims[0]["src"], p["name"], r, sizes="(max-width:900px) 100vw, 55vw", lazy=False)
        thumbs = "".join(f'<button class="gal__t{" is-on" if i == 0 else ""}" data-full="{r}{im["src"]}" aria-label="Fotka {i+1}">{img(im["src"], "", r, sizes="90px")}</button>' for i, im in enumerate(ims)) if len(ims) > 1 else ""
        if p["variants"]:
            vs = "".join(f'<button class="vchip{" is-on" if i == 0 else ""}" data-v="{i}">{e(v["label"])}</button>' for i, v in enumerate(p["variants"]))
            v0 = p["variants"][0]
            variants = f'<div class="pd__var"><span class="pd__vl">{e(p["variant_label"] or "Varianta")}</span><div class="vchips">{vs}</div></div>'
            price, old = v0["price"], v0["regular"]
        else:
            variants, price, old = "", p["price"], p["regular"]
        oldh = f'<s data-pd-old>{kc(old)}</s>' if old > price else '<s data-pd-old hidden></s>'
        rel = [x for x in P if x["slug"] != p["slug"] and cat and cat["slug"] in x["cats"]][:4]
        relh = "".join(card(x, r) for x in rel)
        crumb = f'<a href="{r}obchod.html?k={cat["slug"]}">{e(cat["name"])}</a><span>/</span>' if cat else ""
        out = head(f'{p["name"]} – Kovovýroba Bučovice', re.sub(r"<[^>]+>", " ", p["desc"])[:155], r) + header(r, "produkt") + f'''
<main class="pd" data-product="{p['slug']}">
  <div class="wrap">
    <nav class="crumbs"><a href="{r}index.html">Úvod</a><span>/</span><a href="{r}obchod.html">Obchod</a><span>/</span>{crumb}<span>{e(p['name'])}</span></nav>
    <div class="pd__in">
      <div class="gal"><div class="gal__main">{main}</div><div class="gal__ts">{thumbs}</div></div>
      <div class="pd__info">
        {'<span class="tag tag--static">Akce</span>' if old > price else ''}
        <h1 class="pd__h1">{e(p['name'])}</h1>
        <div class="pd__price"><strong data-pd-price>{kc(price)}</strong>{oldh}</div>
        {variants}
        <div class="pd__buy">
          <div class="qty"><button data-q="-1" aria-label="Méně">−</button><input data-qty value="1" inputmode="numeric" aria-label="Počet kusů"><button data-q="1" aria-label="Více">+</button></div>
          <button class="btn btn--fire btn--grow" data-buy>{ICON['cart']} Do košíku</button>
        </div>
        <button class="btn btn--line-dark btn--block" data-inquiry="{e(p['name'])}">Zeptat se na výrobek nebo jiný rozměr</button>
        <ul class="pd__usp">
          <li>{ICON['pin']}<span><strong>Osobní odběr v dílně</strong> Hájecká 1109, Bučovice (Po–Čt, po domluvě)</span></li>
          <li>{ICON['arrow']}<span><strong>Doprava po ČR i na Slovensko</strong> TOPTRANS až na adresu za 399 Kč</span></li>
          <li>{ICON['phone']}<span><strong>Poradíme s výběrem</strong> {S['contact']['phone']}</span></li>
        </ul>
      </div>
    </div>
    <section class="pd__desc"><h2 class="h3">Popis výrobku</h2><div class="rich">{p['desc']}</div></section>
    {f'<section class="pd__rel"><h2 class="h3">Ze stejné kategorie</h2><div class="pgrid pgrid--4">{relh}</div></section>' if relh else ''}
  </div>
</main>
''' + footer(r) + tail(r)
        (ROOT / "produkt" / f"{p['slug']}.html").write_text(out)


# ───────────────────────────── KOŠÍK ─────────────────────────────
def build_cart():
    r = ""
    ship = "".join(f'''<label class="opt"><input type="radio" name="doprava" value="{s['id']}"{' checked' if i == 0 else ''}><span class="opt__b"></span>
  <span class="opt__t"><strong>{e(s['label'])}</strong><small>{e(s['note'])}</small></span><span class="opt__p">{'zdarma' if s['price'] == 0 else (kc(s['price']) if s['price'] else 'dle dohody')}</span></label>''' for i, s in enumerate(S["shipping"]))
    pay = "".join(f'''<label class="opt"><input type="radio" name="platba" value="{s['id']}"{' checked' if i == 0 else ''}><span class="opt__b"></span><span class="opt__t"><strong>{e(s['label'])}</strong></span></label>''' for i, s in enumerate(S["payment"]))
    out = head("Košík – Kovovýroba Bučovice", "Košík a objednávka", r) + header(r, "kosik") + f'''
<main class="cartp">
  <div class="wrap">
    <nav class="crumbs"><a href="index.html">Úvod</a><span>/</span><span>Košík</span></nav>
    <h1 class="shop__h1">Košík</h1>
    <div class="demo-note"><strong>Ukázka návrhu.</strong> Košík i objednávka tu fungují jen na zkoušku a nic se neodešle. Na hotovém webu může být plnohodnotný e-shop s objednávkami, nebo jen katalog s poptávkou – podle toho, co Vám bude vyhovovat víc.</div>
    <div class="cartp__in">
      <div>
        <div class="citems" data-citems></div>
        <div class="cempty" data-cempty hidden><p>Košík je zatím prázdný.</p><a href="obchod.html" class="btn btn--fire">Do obchodu {ICON['arrow']}</a></div>
        <form class="checkout" data-checkout>
          <h2 class="h3">Doprava</h2><div class="opts">{ship}</div>
          <h2 class="h3">Platba</h2><div class="opts">{pay}</div>
          <h2 class="h3">Kontaktní a doručovací údaje</h2>
          <div class="fgrid">
            <label><span>Jméno a příjmení</span><input required autocomplete="name"></label>
            <label><span>Telefon</span><input type="tel" required autocomplete="tel"></label>
            <label class="span2"><span>E-mail</span><input type="email" required autocomplete="email"></label>
            <label class="span2"><span>Ulice a číslo popisné</span><input autocomplete="street-address"></label>
            <label><span>Město</span><input autocomplete="address-level2"></label>
            <label><span>PSČ</span><input autocomplete="postal-code"></label>
            <label class="span2"><span>Poznámka k objednávce</span><textarea rows="3"></textarea></label>
          </div>
        </form>
      </div>
      <aside class="summary">
        <h2 class="h3">Shrnutí</h2>
        <div class="summary__row"><span>Zboží</span><strong data-sum-goods>0 Kč</strong></div>
        <div class="summary__row"><span>Doprava</span><strong data-sum-ship>zdarma</strong></div>
        <div class="summary__row summary__row--total"><span>Celkem</span><strong data-sum-total>0 Kč</strong></div>
        <button class="btn btn--fire btn--block" data-order>Odeslat objednávku {ICON['arrow']}</button>
        <p class="summary__note">Ukázka návrhu – objednávka se nikam neodešle.</p>
      </aside>
    </div>
  </div>
</main>
''' + footer(r) + tail(r)
    (ROOT / "kosik.html").write_text(out)


def build_404():
    r = "/kovovyroba-bucovice/"
    out = head("Stránka nenalezena – Kovovýroba Bučovice", "", r) + header(r, "404") + f'''
<main class="shop"><section class="shop__head"><div class="wrap"><h1 class="shop__h1">Tady nic není</h1><p class="shop__lead">Stránka neexistuje. Zkuste <a href="{r}obchod.html" class="link-u">obchod</a>.</p></div></section></main>
''' + footer(r) + tail(r)
    (ROOT / "404.html").write_text(out)


if __name__ == "__main__":
    build_index(); build_shop(); build_products(); build_cart(); build_404()
    print("OK:", 4 + len(P), "stránek")
