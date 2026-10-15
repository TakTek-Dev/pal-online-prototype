"""Shared pieces for the page builders: the edition, the photographs, the wordmark,
the block, the line and the drawn marks."""
import html, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V = 7

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
    return (f'<article class="blk who {size}{old}">{chalk}<h3><a href="{e(href)}">{e(p["name"])}{age}</a></h3>'
            f'{trade}{place}<p class="rate num">{e(p["rate"])}{unit}</p></article>')


ARROW = ('<svg class="to" viewBox="0 0 40 20" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="2.2" '
         'd="M2 10h33M27 3l8 7-8 7"/></svg>')

XMARK = ('<svg class="x-mark" viewBox="0 0 26 26" aria-hidden="true"><path d="M4.5 5.2C10 11 15.5 16.6 21.6 21.2M21 4.6C15.8 9.6 '
         '10.6 15.4 4.9 21.7"/></svg>')

OPEN = ('<svg class="x-mark" viewBox="0 0 26 26" aria-hidden="true"><path d="M4.6 14.2c2.6 2.3 4.5 4.6 6.3 7.1C14.6 14 18 9 '
        '22.2 4.6"/></svg>')
