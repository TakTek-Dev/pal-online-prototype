"""Shared pieces for the page builders: the edition, the photographs, the wordmark,
the block, the line and the drawn marks."""
import html, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V = 25
SITE = 'https://taktek-dev.github.io/pal-online-prototype/'

ED = json.load(open(os.path.join(ROOT, 'research', 'edition.json'), encoding='utf-8'))
PH = {p['id']: p for p in json.load(open(os.path.join(ROOT, 'research', 'photos.json'), encoding='utf-8'))['photos']}
BRAND = json.load(open(os.path.join(ROOT, 'tools', 'out', 'brand.json'), encoding='utf-8'))


def e(s):
    return html.escape(str(s), quote=True)


def rich(s):
    """Escapes text, then allows **bold** for figures inside running copy."""
    return re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', e(s))


def wordmark(title='Pal-Online', cls='', ids=False):
    vb = ' '.join(str(v) for v in BRAND['viewBox'])
    a = (lambda n: f' class="{n}"') if ids else (lambda n: '')
    return (f'<svg{(" class=" + chr(34) + cls + chr(34)) if cls else ""} viewBox="{vb}" role="img" aria-label="{e(title)}">'
            f'<path{a("ld-pal")} fill="currentColor" d="{BRAND["pal"]}"/>'
            f'<path{a("ld-block")} fill="var(--block-fill,currentColor)" fill-rule="evenodd" d="{BRAND["block"]}"/>'
            f'<path{a("ld-online")} fill="currentColor" d="{BRAND["online"]}"/></svg>')


def photo_credit(pid, note=''):
    p = PH[pid]
    lic = p['licence']
    return f'{e(note) + " " if note else ""}Photo: {e(p["author"])}, {e(lic)}, Wikimedia Commons.'


def img(pid, alt, cls='', sizes='100vw', eager=False):
    """A Commons photo with every width photos.py made; width and height come from the file."""
    loc = json.load(open(os.path.join(ROOT, 'tools', 'out', 'photos-local.json'), encoding='utf-8'))[pid]
    srcset = ', '.join(f'{s}?v={V} {w}w' for w, s in loc['set'])
    mid = next((s for w, s in loc['set'] if w >= 1200), loc['set'][-1][1])
    load = 'fetchpriority="high"' if eager else 'loading="lazy" decoding="async"'
    return (f'<img{" class=" + chr(34) + cls + chr(34) if cls else ""} src="{mid}?v={V}" srcset="{srcset}" sizes="{sizes}" '
            f'width="{loc["w"]}" height="{loc["h"]}" alt="{e(alt)}" {load}>')


def line(lid, tag_html, extra=''):
    return (f'<div class="mline" id="{lid}"><span class="tag">{tag_html}</span>{extra}'
            f'<svg viewBox="0 0 1000 30" preserveAspectRatio="none" aria-hidden="true">'
            f'<path class="string" d="M0 15L1000 15"/></svg></div>')


def person(p, i=0):
    size = p.get('size', 'w')
    chalk = f'<span class="chalk" title="{e(p["chalk_note"])}">{e(p["chalk"])}</span>' if p.get('chalk') else ''
    unit = f'<small>{e(p["unit"])}</small>' if p.get('unit') else ''
    place = f'<p class="place">{e(p["place"])}</p>' if p.get('place') else ''
    trade = f'<p class="trade">{e(p["trade"])}</p>' if p.get('trade') and size == 'w' else ''
    age = f', {e(p["age"])}' if p.get('age') else ''
    href = p.get('href', '#' + p.get('anchor', 'sources'))
    old = ' blk--old' if p.get('old') else ''
    when = f'<p class="when">{e(p["src"])}</p>' if p.get('src') else ''
    return (f'<article class="blk who {size}{old}">{chalk}<h3><a href="{e(href)}">{e(p["name"])}{age}</a></h3>'
            f'{trade}{place}<p class="rate num">{e(p["rate"])}{unit}</p>{when}</article>')


ARROW = ('<svg class="to" viewBox="0 0 40 20" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="2.2" '
         'd="M2 10h33M27 3l8 7-8 7"/></svg>')

XMARK = '<i class="x-mark sp sp-x" aria-hidden="true"></i>'
OPEN = '<i class="x-mark sp sp-t" aria-hidden="true"></i>'


CONTRACT = open(os.path.join(ROOT, 'tools', 'contract.txt'), encoding='utf-8').read().strip()

# ---------- the chrome every page shares ----------

NAV = [('home.html', 'Today', 'home'), ('wall.html', 'The wall', 'wall'), ('money.html', 'Money', 'money'),
       ('moving.html', 'Moving', 'moving'), ('count.html', 'The count', 'count'), ('harvest.html', 'Olive harvest', 'harvest'),
       ('tell.html', 'Tell us your work', 'tell')]

LOUPE = ('<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.2" fill="none" stroke="currentColor" '
         'stroke-width="2.2"/><path d="M15.2 15.2 21 21" stroke="currentColor" stroke-width="2.4" stroke-linecap="square"/></svg>')


EARLY = "<script>try{var t=localStorage.getItem('po-theme');if(t==='light'||t==='dark')document.documentElement.setAttribute('data-theme',t)}catch(e){}</script>"


def head(title, desc, css, path, og='assets/og.png', ld=(), printable=False):
    """ld: schema.org objects, written as JSON-LD so a CMS theme can keep them as they are."""
    lds = ''.join('<script type="application/ld+json">' + json.dumps(o, ensure_ascii=False).replace('</', '<\\/') + '</script>\n' for o in ld)
    links = ''.join(f'<link rel="stylesheet" href="assets/css/{c}.css?v={V}">\n' for c in ['po'] + list(css))
    return (
        '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f'{EARLY}\n'
        '<meta name="robots" content="noindex, nofollow">\n'
        f'<title>{e(title)}</title>\n<meta name="description" content="{e(desc)}">\n'
        '<meta property="og:type" content="website">\n<meta property="og:site_name" content="Pal-Online">\n'
        f'<meta property="og:title" content="{e(title)}">\n<meta property="og:description" content="{e(desc)}">\n'
        f'<meta property="og:url" content="{SITE}{path}">\n<meta property="og:image" content="{SITE}{og}">\n'
        '<meta property="og:image:width" content="1200">\n<meta property="og:image:height" content="630">\n'
        '<meta name="twitter:card" content="summary_large_image">\n'
        '<meta name="theme-color" content="#F3F4F1" media="(prefers-color-scheme: light)">\n'
        '<meta name="theme-color" content="#101213" media="(prefers-color-scheme: dark)">\n'
        f'<link rel="icon" href="assets/brand/favicon.svg?v={V}" type="image/svg+xml">\n'
        f'<link rel="apple-touch-icon" href="assets/brand/apple-touch-icon.png?v={V}">\n'
        f'<link rel="manifest" href="manifest.webmanifest?v={V}">\n'
        '<link rel="preload" href="assets/fonts/hepta-slab-800.woff2?v=1" as="font" type="font/woff2" crossorigin>\n'
        '<link rel="preload" href="assets/fonts/mona-sans.woff2?v=1" as="font" type="font/woff2" crossorigin>\n'
        f'{links}' + (f'<link rel="stylesheet" href="assets/css/print.css?v={V}" media="print">' + chr(10) if printable else '') + f'{lds}</head>')


def strip():
    r = ED['rates']
    items = ''.join(f'<li>{e(k)} <b>{e(v)}</b></li>' for k, v in r['items'])
    return (f'<div class="strip"><div class="wrap"><time datetime="{ED["date"]}">{e(ED["dateline"])}</time>'
            f'<ul class="rates" aria-label="Exchange rates and fuel">{items}<li class="by">{e(r["by"])}</li></ul>'
            f'<a class="tell-link" href="tell.html">Tell us your work</a><button class="theme" type="button" role="switch" aria-checked="false" aria-label="Night colours"><span class="sw" aria-hidden="true"></span><span class="lab" aria-hidden="true">Night</span></button></div></div>')


def mast(active, inner=False):
    def a(h, t, k, extra=''):
        cur = ' aria-current="page"' if k == active else ''
        return f'<a href="{h}"{cur}{extra}>{t}</a>'
    links = ''.join(a(h, t, k) for h, t, k in NAV)
    cur = ' aria-current="page"' if active == 'search' else ''
    find = f'<a class="find" href="search.html"{cur}>{LOUPE}<span class="sr">Search</span></a>'
    bar_links = ''.join(a(h, t, k, ' tabindex="-1"') for h, t, k in NAV)
    return (f'<header class="mast{" mast--inner" if inner else ""}"><div class="wrap">'
            f'<a class="home" href="home.html" aria-label="Pal-Online, home">{wordmark("Pal-Online")}</a>'
            f'<p class="motto">{rich(ED["motto"])}</p>'
            f'<nav class="nav" aria-label="Sections">{links}{find}</nav>'
            f'</div></header>'
            f'<div class="bar" aria-hidden="true"><div class="wrap"><a class="home" href="home.html" tabindex="-1">{wordmark("Pal-Online")}</a>'
            f'<nav>{bar_links}</nav></div><span class="bar-rider"></span></div>')


def foot(sources, credits, note=None):
    F = ED['foot']
    srcs = ''.join(f'<li><a href="{e(u)}" rel="noopener">{e(t)}</a></li>' for t, u in sources)
    creds = ''.join(f'<li>{e(c)}</li>' for c in credits)
    tops = ''.join('<span class="w"></span>' for _ in range(8))
    photos = (f'<h2 style="margin-top:22px">Photographs</h2><ul>{creds}</ul><p style="margin-top:12px">{rich(note or F["photo_note"])}</p>'
              if credits else '')
    sources_html = f'<h2>Sources on this page</h2><ul>{srcs}</ul>' if sources else ''
    return (f'<footer class="foot"><div class="wrap"><div class="wall course-top" aria-hidden="true">{tops}</div>'
            f'<div class="foot-grid"><div><a class="home" href="home.html" aria-label="Pal-Online, home">{wordmark("Pal-Online")}</a>'
            f'<p>{rich(F["about"])}</p><nav aria-label="Footer"><ul><li><a href="about.html">About</a></li>'
            f'<li><a href="about.html#how">How we report</a></li><li><a href="about.html#corrections">Corrections</a></li>'
            f'<li><a href="search.html">Search</a></li><li><a href="privacy.html">Privacy</a></li><li><a href="index.html">Identity guide</a></li></ul></nav></div>'
            f'<div id="sources">{sources_html}{photos}</div></div>'
            f'<p class="proto">{rich(F["proto"])}</p></div></footer>')


def loader():
    return (f'<div id="loader" aria-hidden="true"><div class="ld">'
            f'<div class="ld-line"><svg viewBox="0 0 1000 120" preserveAspectRatio="none">'
            f'<rect class="ld-pin" x="-6" y="40" width="12" height="40"/><rect class="ld-pin" x="994" y="40" width="12" height="40"/>'
            f'<path class="ld-string" d="M0 60Q500 106 1000 60"/></svg></div>'
            f'{wordmark("Pal-Online", "ld-word", ids=True)}'
            f'<p class="ld-note">Who is working in Palestine today</p></div></div>')


def chain():
    C = ED['chain']
    lis = ''
    for i, k in enumerate(C['links']):
        q = f'<q>{e(k["quote"])}</q>' if k.get('quote') else ''
        age = f', {e(k["age"])}' if k.get('age') else ''
        lis += (f'<li class="blk blk--night {k.get("size", "w")}">'
                f'<h3>{e(k["name"])}{age}</h3><p class="role">{e(k["role"])}</p><p class="who-is">{e(k["who"])}</p>'
                f'<p class="rate num">{e(k["rate"])}<small>{e(k["unit"])}</small></p>{q}</li>')
    return (f'<section class="chain" id="chain" aria-labelledby="chain-h"><div class="wrap">'
            f'<div class="sec-head"><h2 id="chain-h">{e(C["title"])}</h2><p>{rich(C["sub"])}</p></div>'
            f'{line("line-chain", e(C["tag"]))}'
            f'<ol class="wall links lay" data-line="line-chain">{lis}</ol>'
            f'<p class="src">{rich(C["source"])}</p></div></section>')


LIMIT = '<i class="x-mark sp sp-s" aria-hidden="true"></i>'


def mark(state):
    return {'closed': XMARK, 'open': OPEN, 'limited': LIMIT}[state]


ORG = {'@type': 'NewsMediaOrganization', 'name': 'Pal-Online', 'url': SITE + 'home.html',
       'logo': {'@type': 'ImageObject', 'url': SITE + 'assets/brand/social/avatar-night.png', 'width': 1080, 'height': 1080}}


def crumbs(*pairs):
    """BreadcrumbList from (name, path) pairs; the homepage is always first."""
    items = [('Today', 'home.html')] + list(pairs)
    return {'@context': 'https://schema.org', '@type': 'BreadcrumbList',
            'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': SITE + p} for i, (n, p) in enumerate(items)]}
