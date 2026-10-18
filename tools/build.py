"""Builds home.html from the edition file.

python -I tools/build.py   (from the project root)

Inputs:  research/edition.json   the frozen edition (every item carries its source and date)
         research/photos.json    Commons photographs (licence, author, file page)
         tools/out/brand.json    wordmark outlines (tools/brand.py)
Output:  home.html. Never hand-edit it; change the edition or this file and rebuild.
Bump V on every asset change so browsers drop their cached copies.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # -I leaves the script's folder off the path
from common import *  # noqa: E402,F401,F403 (the shared vocabulary of the builders)


def today():
    L = ED['lead']
    people = ''.join(person(p, i) for i, p in enumerate(ED['course']))
    ph = L['photo']
    lead = (f'<article class="blk lead" id="lead">'
            f'<figure class="opening">{img(ph, L["alt"], sizes="(max-width:1100px) 100vw, 680px", eager=True)}'
            f'<figcaption>{e(L["caption"])}</figcaption></figure>'
            f'<div class="txt"><h2 class="lead-h"><a href="article.html">{e(L["headline"])}</a></h2>'
            f'<p class="dek">{rich(L["dek"])}</p>'
            f'<div class="meta"><p class="src">{rich(L["source"])}</p>'
            f'<p class="rate num">{e(L["rate"])}<small>{e(L["unit"])}</small></p></div></div></article>')
    n = len(ED['course']) + 1
    tag = f'At work today, {e(ED["short_date"])} <b>· {n} people and their pay</b>'
    rebar = '<div class="rebar" aria-hidden="true">' + '<i></i>' * 7 + '</div>'
    return (f'<section class="today wrap" id="today" aria-labelledby="today-h">'
            f'<h1 class="sr" id="today-h">Pal-Online: who is working in Palestine today, {e(ED["short_date"])}</h1>'
            f'{line("line-today", tag, rebar)}'
            f'<div class="wall hero lay" data-line="line-today">{lead}{people}</div>'
            f'</section>')


def earlier():
    E = ED['earlier']
    if not E['people']:
        return ''
    people = ''.join(person(dict(p, old=True)) for p in E['people'])
    return (f'<section class="wrap" aria-labelledby="earlier-h"><h2 class="sr" id="earlier-h">{e(E["title"])}</h2>'
            f'<div class="wall earlier lay" data-line="line-today">{people}</div></section>')


def trades():
    R = ED['register']
    rows = ''
    for r in R['rows']:
        age = f', {e(r["age"])}' if r.get('age') else ''
        rows += (f'<li data-spray><div><h3>{e(r["name"])}{age}</h3><p class="meta">{e(r["place"])} · {e(r["source"])}</p></div>'
                 f'<p class="was"><span class="sr">Was: </span><span class="spray">{e(r["was"])}</span></p>{ARROW}'
                 f'<p class="now"><span class="sr">Now: </span>{e(r["now"])}</p>'
                 f'<p class="words">{rich(r["words"])} <a href="{e(r["url"])}" rel="noopener">Source</a></p></li>')
    return (f'<section class="sec wrap" id="trades" aria-labelledby="trades-h">'
            f'<div class="sec-head"><h2 id="trades-h">{e(R["title"])}</h2><p>{rich(R["sub"])} <a href="wall.html">The whole wall</a></p></div>'
            f'<ul class="reg">{rows}</ul></section>')


def count():
    C = ED['count']
    btns = ''
    for i, f in enumerate(C['figures']):
        btns += (f'<button class="fig-btn" type="button" aria-pressed="{"true" if i == 0 else "false"}" '
                 f'data-out="{f["out"]}" data-cap="{e(f["cap"])}">'
                 f'<span class="big num">{e(f["value"])}</span><span class="what">{e(f["what"])}</span>'
                 f'<span class="who-said">{e(f["by"])}</span></button>')
    first = C['figures'][0]
    cells = ''
    for r in range(10):          # ten courses of ten, in running bond; odd courses end on a cut block
        row = ''.join(f'<span{" class=" + chr(34) + "is-out" + chr(34) if r * 10 + c < first["out"] else ""}></span>' for c in range(10))
        cells += f'<div class="crs">{row}{"<span class=bat></span>" if r % 2 else ""}</div>'
    return (f'<section class="sec wrap" id="count" aria-labelledby="count-h">'
            f'<div class="sec-head"><h2 id="count-h">{e(C["title"])}</h2><p>{rich(C["sub"])} <a href="count.html">Every count, side by side</a></p></div>'
            f'<div class="count"><div><div class="figs" role="group" aria-label="Choose whose figure the wall shows">{btns}</div>'
            f'<p class="src count-note">{rich(C["note"])}</p></div>'
            f'<div><div class="hundred" aria-hidden="true">{cells}</div>'
            f'<p class="count-cap" aria-live="polite">{e(first["cap"])}</p></div></div></section>')


def workplace():
    W = ED['workplace']
    out = ''
    for i, d in enumerate(W['desks']):
        paras = ''.join(f'<p>{rich(p)}</p>' for p in d['body'])
        out += (f'<article class="desk{" flip" if i % 2 else ""}" id="{e(d["id"])}">'
                f'<figure class="opening">{img(d["photo"], d["alt"], sizes="(max-width:860px) 100vw, 56vw")}'
                f'<figcaption>{e(d["caption"])}</figcaption></figure>'
                f'<div><h3>{e(d["headline"])}</h3><p class="place">{e(d["place"])}</p>{paras}'
                f'<blockquote><p>{e(d["quote"])}</p><footer>{e(d["quote_by"])}</footer></blockquote></div></article>')
    return (f'<section class="sec wrap" id="workplace" aria-labelledby="wp-h">'
            f'<div class="sec-head"><h2 id="wp-h">{e(W["title"])}</h2><p>{rich(W["sub"])}</p></div>{out}</section>')




def money():
    M = ED['money']
    pay = ''.join(f'<li><span class="k">{e(i["k"])}</span><span class="v num">{e(i["v"])}</span>'
                  f'<p class="d">{rich(i["d"])}<span class="src">{rich(i["src"])}</span></p></li>' for i in M['money'])
    roads = ''.join(f'<li class="road">{XMARK if r["state"] != "open" else OPEN}<div><p class="k">{e(r["place"])}</p><p class="state">{e(r["label"])}</p>'
                    f'<p class="d">{rich(r["d"])}<span class="src">{rich(r["src"])}</span></p></div></li>'
                    for r in M['moving'])
    return (f'<section class="sec wrap" id="money" aria-labelledby="money-h">'
            f'<div class="sec-head"><h2 id="money-h">{e(M["title"])}</h2><p>{rich(M["sub"])} <a href="money.html">Money</a> · <a href="moving.html">Moving</a></p></div>'
            f'<div class="ledger"><div><h3>{e(M["money_title"])}</h3><ul class="items">{pay}</ul></div>'
            f'<div><h3>{e(M["moving_title"])}</h3><ul class="items">{roads}</ul></div></div></section>')


def tell():
    T = ED['tell']
    gaps = ''.join(f'<span class="{c}">{t}</span>' for c, t in [
        ('blk w', ''), ('blk w', ''), ('blk w', ''),
        ('blk h', ''), ('blk w', ''), ('blk--gap w', 'Your block'), ('blk h', '')])
    els = ''.join(f'<li><a href="{h}"><b>{e(k)}</b>{e(t)}</a></li>' for k, t, h in T['elsewhere'])
    return (f'<section class="sec wrap" id="tell" aria-labelledby="tell-h"><div class="tell">'
            f'<div><h2 id="tell-h">{e(T["title"])}</h2><p class="dek" style="margin-top:12px">{rich(T["intro"])}</p>'
            f'<div class="wall gap-wall" aria-hidden="true">{gaps}</div>'
            f'<ul class="else" aria-label="Elsewhere on Pal-Online">{els}</ul></div>'
            f'<form action="#" method="post" novalidate>'
            f'<div class="field"><label for="f-trade">Your trade</label><input id="f-trade" name="trade" required autocomplete="organization-title"><p class="err">Tell us what you do for work.</p></div>'
            f'<div class="field"><label for="f-town">Town or camp</label><input id="f-town" name="town" required autocomplete="address-level2"><p class="err">Tell us where you work.</p></div>'
            f'<div class="field full"><label for="f-changed">What changed <span>(before the war, and now)</span></label><textarea id="f-changed" name="changed" required></textarea><p class="err">A sentence is enough.</p></div>'
            f'<div class="field full"><label for="f-contact">Phone or email <span>(only for our reporter)</span></label><input id="f-contact" name="contact" required autocomplete="email"><p class="err">We need a way to call you back.</p></div>'
            f'<button class="btn" type="submit">Send to the newsroom</button><p class="note">We never publish your contact details. <a href="tell.html">More ways to tell us</a></p>'
            f'<p class="sent" role="status">Received. This is a prototype, so nothing was sent; on the live site a reporter would call you.</p>'
            f'</form></div></section>')


SITE_LD = [{'@context': 'https://schema.org', '@type': 'WebSite', 'name': 'Pal-Online', 'url': SITE + 'home.html',
            'publisher': ORG, 'potentialAction': {'@type': 'SearchAction', 'target': SITE + 'search.html?q={search_term_string}',
                                                  'query-input': 'required name=search_term_string'}}]

page = f'''{head('Pal-Online — who is working in Palestine today', ED['description'], ['home'], 'home.html', ld=SITE_LD)}
<body>
<!--
{CONTRACT}
-->
{loader()}
<a class="skip" href="#today">Skip to today's course</a>
{strip()}
{mast('home')}
<main>
{today()}
{earlier()}
{chain()}
{trades()}
{count()}
{workplace()}
{money()}
{tell()}
</main>
{foot(ED['foot']['sources'], ED['foot']['credits'])}
<script src="assets/js/po.js?v={V}" defer></script>
<script src="assets/js/home.js?v={V}" defer></script>
</body>
</html>
'''
open(os.path.join(ROOT, 'home.html'), 'w', encoding='utf-8').write(page)
print('home.html', len(page), 'bytes')
