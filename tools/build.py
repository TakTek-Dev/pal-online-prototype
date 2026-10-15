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


def strip():
    r = ED['rates']
    items = ''.join(f'<li>{e(k)} <b>{e(v)}</b></li>' for k, v in r['items'])
    return (f'<div class="strip"><div class="wrap"><time datetime="{ED["date"]}">{e(ED["dateline"])}</time>'
            f'<ul class="rates" aria-label="Exchange rates and fuel">{items}<li class="by">{e(r["by"])}</li></ul>'
            f'<a class="tell-link" href="#tell">Tell us your work</a></div></div>')


NAV = [('#today', 'Work today'), ('#chain', 'The chain'), ('#trades', 'Changed trades'), ('#count', 'The count'),
       ('#workplace', 'Workplaces'), ('#money', 'Money &amp; moving'), ('#tell', 'Tell us your work')]


def mast():
    links = ''.join(f'<a href="{h}">{t}</a>' for h, t in NAV)
    return (f'<header class="mast"><div class="wrap">'
            f'<a class="home" href="home.html" aria-label="Pal-Online, home">{wordmark("Pal-Online")}</a>'
            f'<p class="motto">{rich(ED["motto"])}</p>'
            f'<nav class="nav" aria-label="Sections">{links}<span class="ed">Edition of {e(ED["short_date"])}</span></nav>'
            f'</div></header>'
            f'<div class="bar" aria-hidden="true"><div class="wrap"><a class="home" href="home.html" tabindex="-1">{wordmark("Pal-Online")}</a>'
            f'<nav>{"".join(f"<a href={chr(34)}{h}{chr(34)} tabindex={chr(34)}-1{chr(34)}>{t}</a>" for h, t in NAV)}</nav></div>'
            f'<span class="bar-rider"></span></div>')


def today():
    L = ED['lead']
    people = ''.join(person(p, i) for i, p in enumerate(ED['course']))
    ph = L['photo']
    lead = (f'<article class="blk lead" id="lead">'
            f'<figure class="opening">{img(ph, L["alt"], sizes="(max-width:1100px) 100vw, 680px", eager=True)}'
            f'<figcaption>{e(L["caption"])}</figcaption></figure>'
            f'<div class="txt"><h1><a href="#lead-story">{e(L["headline"])}</a></h1>'
            f'<p class="dek">{rich(L["dek"])}</p>'
            f'<div class="meta"><p class="src">{rich(L["source"])}</p>'
            f'<p class="rate num">{e(L["rate"])}<small>{e(L["unit"])}</small></p></div></div></article>')
    n = len(ED['course']) + 1
    tag = f'At work today, {e(ED["short_date"])} <b>· {n} people and their pay</b>'
    rebar = '<div class="rebar" aria-hidden="true">' + '<i></i>' * 7 + '</div>'
    return (f'<section class="today wrap" id="today" aria-labelledby="today-h">'
            f'<h2 class="sr" id="today-h">At work today</h2>'
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


def chain():
    C = ED['chain']
    lis = ''
    for i, k in enumerate(C['links']):
        q = f'<q>{e(k["quote"])}</q>' if k.get('quote') else ''
        age = f', {e(k["age"])}' if k.get('age') else ''
        lis += (f'<li class="blk blk--night {k.get("size", "w")}"><span class="step">{i + 1:02d}</span>'
                f'<p class="role">{e(k["role"])}</p><h3>{e(k["name"])}{age}</h3><p class="who-is">{e(k["who"])}</p>'
                f'<p class="rate num">{e(k["rate"])}<small>{e(k["unit"])}</small></p>{q}</li>')
    return (f'<section class="chain" id="chain" aria-labelledby="chain-h"><div class="wrap">'
            f'<div class="sec-head"><h2 id="chain-h">{e(C["title"])}</h2><p>{rich(C["sub"])}</p></div>'
            f'{line("line-chain", e(C["tag"]))}'
            f'<ol class="wall links lay" data-line="line-chain">{lis}</ol>'
            f'<p class="src">{rich(C["source"])}</p></div></section>')




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
            f'<div class="sec-head"><h2 id="trades-h">{e(R["title"])}</h2><p>{rich(R["sub"])}</p></div>'
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
            f'<div class="sec-head"><h2 id="count-h">{e(C["title"])}</h2><p>{rich(C["sub"])}</p></div>'
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
                f'<div><p class="place">{e(d["place"])}</p><h3>{e(d["headline"])}</h3>{paras}'
                f'<blockquote><p>{e(d["quote"])}</p><footer>{e(d["quote_by"])}</footer></blockquote></div></article>')
    return (f'<section class="sec wrap" id="workplace" aria-labelledby="wp-h">'
            f'<div class="sec-head"><h2 id="wp-h">{e(W["title"])}</h2><p>{rich(W["sub"])}</p></div>{out}</section>')




def money():
    M = ED['money']
    pay = ''.join(f'<li><span class="k">{e(i["k"])}</span><span class="v num">{e(i["v"])}</span>'
                  f'<p class="d">{rich(i["d"])}<span class="src">{rich(i["src"])}</span></p></li>' for i in M['money'])
    roads = ''.join(f'<li class="road">{XMARK if r["state"] != "open" else OPEN}<div><p class="state">{e(r["label"])}</p>'
                    f'<p class="k">{e(r["place"])}</p><p class="d">{rich(r["d"])}<span class="src">{rich(r["src"])}</span></p></div></li>'
                    for r in M['moving'])
    return (f'<section class="sec wrap" id="money" aria-labelledby="money-h">'
            f'<div class="sec-head"><h2 id="money-h">{e(M["title"])}</h2><p>{rich(M["sub"])}</p></div>'
            f'<div class="ledger"><div><h3>{e(M["money_title"])}</h3><ul class="items">{pay}</ul></div>'
            f'<div><h3>{e(M["moving_title"])}</h3><ul class="items">{roads}</ul></div></div></section>')


def tell():
    T = ED['tell']
    gaps = ''.join(f'<span class="{c}">{t}</span>' for c, t in [
        ('blk w', ''), ('blk w', ''), ('blk w', ''),
        ('blk h', ''), ('blk w', ''), ('blk--gap w', 'Your block'), ('blk h', '')])
    els = ''.join(f'<li><a href="#"><b>{e(k)}</b>{e(t)}</a></li>' for k, t in T['elsewhere'])
    return (f'<section class="sec wrap" id="tell" aria-labelledby="tell-h"><div class="tell">'
            f'<div><h2 id="tell-h">{e(T["title"])}</h2><p class="dek" style="margin-top:12px">{rich(T["intro"])}</p>'
            f'<div class="wall gap-wall" aria-hidden="true">{gaps}</div>'
            f'<ul class="else" aria-label="Elsewhere on Pal-Online">{els}</ul></div>'
            f'<form action="#" method="post" novalidate>'
            f'<div class="field"><label for="f-trade">Your trade</label><input id="f-trade" name="trade" required autocomplete="organization-title"><p class="err">Tell us what you do for work.</p></div>'
            f'<div class="field"><label for="f-town">Town or camp</label><input id="f-town" name="town" required autocomplete="address-level2"><p class="err">Tell us where you work.</p></div>'
            f'<div class="field full"><label for="f-changed">What changed <span>(before the war, and now)</span></label><textarea id="f-changed" name="changed" required></textarea><p class="err">A sentence is enough.</p></div>'
            f'<div class="field full"><label for="f-contact">Phone or email <span>(only for our reporter)</span></label><input id="f-contact" name="contact" required autocomplete="email"><p class="err">We need a way to call you back.</p></div>'
            f'<button class="btn" type="submit">Send to the newsroom</button><p class="note">We never publish your contact details. A reporter calls before anything is published.</p>'
            f'<p class="sent" role="status">Received. This is a prototype, so nothing was sent; on the live site a reporter would call you.</p>'
            f'</form></div></section>')


def foot():
    F = ED['foot']
    credits = ''.join(f'<li>{e(c)}</li>' for c in F['credits'])
    srcs = ''.join(f'<li><a href="{e(u)}" rel="noopener">{e(t)}</a></li>' for t, u in F['sources'])
    course = ''.join(f'<span class="{"w" if (i // 8) % 2 == 0 and i % 8 != 7 or (i // 8) % 2 == 1 and i % 8 not in (0,) else "h"}"></span>' for i in range(0))
    tops = ''.join('<span class="w"></span>' for _ in range(8))
    return (f'<footer class="foot"><div class="wrap"><div class="wall course-top" aria-hidden="true">{tops}</div>'
            f'<div class="foot-grid"><div><a class="home" href="home.html" aria-label="Pal-Online, home">{wordmark("Pal-Online")}</a>'
            f'<p>{rich(F["about"])}</p><nav aria-label="Footer"><ul><li><a href="index.html">Identity guide</a></li><li><a href="#">About</a></li>'
            f'<li><a href="#">Corrections</a></li><li><a href="#tell">Contact</a></li></ul></nav></div>'
            f'<div id="sources"><h2>Sources for this edition</h2><ul>{srcs}</ul>'
            f'<h2 style="margin-top:22px">Photographs</h2><ul>{credits}</ul><p style="margin-top:12px">{rich(F["photo_note"])}</p></div></div>'
            f'<p class="proto">{rich(F["proto"])}</p></div></footer>')


def loader():
    return (f'<div id="loader" aria-hidden="true"><div class="ld">'
            f'<div class="ld-line"><svg viewBox="0 0 1000 120" preserveAspectRatio="none">'
            f'<rect class="ld-pin" x="-6" y="40" width="12" height="40"/><rect class="ld-pin" x="994" y="40" width="12" height="40"/>'
            f'<path class="ld-string" d="M0 60Q500 106 1000 60"/></svg></div>'
            f'{wordmark("Pal-Online", "ld-word", ids=True)}'
            f'<p class="ld-note">Who is working in Palestine today</p></div></div>')


CONTRACT = open(os.path.join(ROOT, 'tools', 'contract.txt'), encoding='utf-8').read().strip()

page = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>Pal-Online — who is working in Palestine today</title>
<meta name="description" content="{e(ED["description"])}">
<meta name="theme-color" content="#F3F4F1" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#101213" media="(prefers-color-scheme: dark)">
<link rel="icon" href="assets/brand/favicon.svg?v={V}" type="image/svg+xml">
<link rel="preload" href="assets/fonts/hepta-slab-800.woff2?v=1" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="assets/fonts/mona-sans.woff2?v=1" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="assets/css/po.css?v={V}">
<link rel="stylesheet" href="assets/css/home.css?v={V}">
</head>
<body>
<!--
{CONTRACT}
-->
{loader()}
<a class="skip" href="#today">Skip to today's course</a>
{strip()}
{mast()}
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
{foot()}
<script src="assets/js/po.js?v={V}" defer></script>
<script src="assets/js/home.js?v={V}" defer></script>
</body>
</html>
'''
open(os.path.join(ROOT, 'home.html'), 'w', encoding='utf-8').write(page)
print('home.html', len(page), 'bytes')
