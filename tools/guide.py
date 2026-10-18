"""Builds index.html, the Pal-Online identity guide.

python -I tools/guide.py   (from the project root)

Every specimen on the page is the live system (po.css, the wordmark outlines, the
edition's real people), so the guide cannot drift from the site.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # -I leaves the script's folder off the path
from common import *  # noqa: E402,F401,F403


def P(u, v):
    """A point on the top face of the drawn block (oblique view)."""
    return 40 + 320 * u + 72 * v, 120 - 52 * v


def poly(pts):
    return ' '.join(f'{x:.1f},{y:.1f}' for x, y in pts)


def plate_block():
    sx, web = 176 / 1200, 150 / 1200
    cw = (1 - 2 * sx - 2 * web) / 3
    cores = ''
    for i in range(3):
        u0 = sx + i * (cw + web)
        u1 = u0 + cw
        cores += f'<polygon points="{poly([P(u0, .24), P(u1, .24), P(u1, .76), P(u0, .76)])}" fill="#141618" fill-opacity=".78"/>'
    top = poly([P(0, 0), P(1, 0), P(1, 1), P(0, 1)])
    side = poly([P(1, 0), P(1, 1), (P(1, 1)[0], P(1, 1)[1] + 160), (360, 280)])
    return (f'<svg viewBox="0 0 470 330" aria-hidden="true"><g stroke="#141618" stroke-width="2" stroke-linejoin="round">'
            f'<polygon points="{side}" fill="#B6BAB4"/><polygon points="{top}" fill="#E4E6E1"/>'
            f'<rect x="40" y="120" width="320" height="160" fill="#CED1CC"/></g>{cores}'
            f'<g class="dim"><path d="M40 300v12M360 300v12M40 306h320"/><path d="M14 120h-8M14 280h-8M10 120v160"/></g>'
            f'<text class="dim-t" x="200" y="326" text-anchor="middle">40 cm</text>'
            f'<text class="dim-t" x="0" y="205" text-anchor="start" transform="rotate(-90 0 205)" dy="-4">20 cm</text></svg>')


def plate_line():
    blocks = ''
    for row, y in enumerate((196, 250)):
        off = 0 if row == 0 else -40
        for i in range(7):
            x = 30 + off + i * 80
            if x + 76 < 30 or x > 470:
                continue
            x0, x1 = max(30, x), min(470, x + 76)
            blocks += f'<rect x="{x0}" y="{y}" width="{x1 - x0}" height="50" fill="#CED1CC" stroke="#141618" stroke-width="1.5"/>'
    return (f'<svg viewBox="0 0 500 320" aria-hidden="true">{blocks}'
            f'<rect x="16" y="120" width="10" height="190" fill="#141618"/><rect x="474" y="120" width="10" height="190" fill="#141618"/>'
            f'<path d="M26 192L474 192" stroke="#FF4F12" stroke-width="3"/>'
            f'<path d="M26 192l-6 -3M474 192l6 -3" stroke="#FF4F12" stroke-width="3"/>'
            f'<text class="dim-t" x="250" y="176" text-anchor="middle">the top of the course being laid</text></svg>')


def plate_bars():
    bars = ''
    xs = [70, 132, 194, 256, 318, 380, 430]
    hs = [96, 120, 84, 128, 100, 116, 90]
    for x, h in zip(xs, hs):
        top = 200 - h
        hook = 18 if x % 2 else -18
        bars += f'<path d="M{x} 200V{top}q0 -8 {hook} -10" fill="none" stroke="#983812" stroke-width="5" stroke-linecap="round"/>'
    return (f'<svg viewBox="0 0 500 320" aria-hidden="true">{bars}'
            f'<rect x="30" y="200" width="440" height="56" fill="#CED1CC" stroke="#141618" stroke-width="2"/>'
            f'<rect x="30" y="256" width="440" height="44" fill="#B6BAB4" stroke="#141618" stroke-width="2"/>'
            f'<text class="dim-t" x="250" y="292" text-anchor="middle" fill="#141618">roof slab, the floor that is finished</text></svg>')


def plate_marks():
    return ('<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px;align-items:center;width:84%">'
            '<img src="assets/img/spray-cross.webp?v=1" alt="" width="200" height="200">'
            '<img src="assets/img/spray-tick.webp?v=1" alt="" width="200" height="200">'
            '<img src="assets/img/spray-slash.webp?v=1" alt="" width="200" height="200">'
            '<p style="font:750 34px/1 var(--text);font-stretch:78%;color:var(--oxide);margin:0">12 h</p>'
            '<p style="font:750 34px/1 var(--text);font-stretch:78%;color:var(--oxide);margin:0">×9</p>'
            '<p style="font:750 34px/1 var(--text);font-stretch:78%;color:var(--oxide);margin:0">500 m</p></div>')


CH = [('idea', 'The idea'), ('wordmark', 'Wordmark'), ('mark', 'Mark'), ('colour', 'Colour'), ('type', 'Type'),
      ('wall', 'The wall'), ('block', 'The block'), ('marks', 'Marks'), ('motion', 'Motion'), ('social', 'Social'),
      ('voice', 'Voice'), ('pages', 'Pages'), ('downloads', 'Downloads')]


def ch_head(i, cid, title, intro):
    return (f'<div class="ch-head"><div><h2 id="{cid}-h">{e(title)}</h2></div>'
            f'<p>{rich(intro)}</p></div>')


def section(i, cid, title, intro, body):
    return (f'<section class="ch wrap" id="{cid}" aria-labelledby="{cid}-h">{ch_head(i, cid, title, intro)}{body}</section>')


L = ED['lead']
C0 = ED['course'][0]

top = (f'<header class="g-top"><div class="wrap"><a class="home" href="index.html" aria-label="Pal-Online identity guide">{wordmark()}</a>'
       f'<nav aria-label="Chapters">{"".join(f"<a href={chr(34)}#{c}{chr(34)}>{t}</a>" for c, t in CH[:9])}</nav>'
       f'<button class="theme" type="button" role="switch" aria-checked="false" aria-label="Night colours"><span class="sw" aria-hidden="true"></span><span class="lab" aria-hidden="true">Night</span></button><a class="go" href="home.html">Homepage</a></div></header>')

toc = ''.join(f'<li><a href="#{c}"><span>{i + 1:02d}</span>{t}</a></li>' for i, (c, t) in enumerate(CH))
cover = (f'<section class="cover wrap" aria-labelledby="cover-h"><h1 class="sr" id="cover-h">Pal-Online identity guide</h1>'
         f'<div class="big">{wordmark("Pal-Online")}</div>'
         f'<div class="mline" id="line-cover"><span class="tag">Identity guide · <b>Midmak</b> · first edition, {e(ED["short_date"])}</span>'
         f'<svg viewBox="0 0 1000 30" preserveAspectRatio="none" aria-hidden="true"><path class="string" d="M0 15L1000 15"/></svg></div>'
         f'<div class="cover-grid"><div><p class="state">Pal-Online reports Palestine by livelihood. Its identity is a wall built by hand: '
         f'<em>one block for every worker, one line for today.</em></p>'
         f'<p class="meta-line">Run your pointer across the orange line: it is a mason\'s line, and it answers.</p></div>'
         f'<ol class="toc">{toc}</ol></div></section>')

idea = section(1, 'idea', 'Midmak: one course of a wall',
               'In Arabic a **midmak** is one course of stone or block in a wall, and laying the first midmak is how a foundation is described. '
               'Gaza is being cleared and rebuilt by hand, and West Bank houses stand with their rebar left out for the next floor. The site is built the same way: one course a day.',
               f'<div class="cols" style="--n:4">'
               f'<div class="plate"><div class="art">{plate_block()}</div><h3>The block</h3><p>The three-core hollow block, 40 by 20 cm, that Gaza and the West Bank are built from. It is the hyphen in the name and the unit of every page: one worker, one block.</p></div>'
               f'<div class="plate"><div class="art">{plate_line()}</div><h3>The line</h3><p>A mason stretches a string between two pins and lays each block to it. On the site the line marks today, and it is the only live colour.</p></div>'
               f'<div class="plate"><div class="art">{plate_bars()}</div><h3>The bars</h3><p>Starter bars left standing on a finished roof wait for the next floor. They mark work that is not over, so they stand where tomorrow\'s course will go.</p></div>'
               f'<div class="plate"><div class="art">{plate_marks()}</div><h3>The marks</h3><p>Crews spray and chalk walls: a cross, a tick, a strike, a number. State on the site is a mark like these, never a coloured badge.</p></div></div>')

draw_vb = BRAND['viewBox']
bx, by, bw, bh = BRAND['blockBox']
cap = BRAND['cap']
xh = BRAND['xHeightTop']
dims = (f'<g class="dim"><path d="M{bx} {by - 260}v120M{bx + bw} {by - 260}v120M{bx} {by - 200}h{bw}"/>'
        f'<path d="M{draw_vb[0] - 300} 0h200M{draw_vb[0] - 300} {xh}h200M{draw_vb[0] - 300} {cap}h200M{draw_vb[0] - 200} 0v{cap}"/></g>'
        f'<text class="dim-t" x="{bx + bw / 2}" y="{by - 300}" text-anchor="middle" font-size="190">40 × 20</text>'
        f'<text class="dim-t" x="{draw_vb[0] - 340}" y="{cap / 2}" text-anchor="end" font-size="170">cap</text>'
        f'<text class="dim-t" x="{draw_vb[0] - 340}" y="{xh + 60}" text-anchor="end" font-size="170">x</text>')
vb_pad = f'{draw_vb[0] - 1100} -520 {draw_vb[2] + 1300} {cap + 760}'
drawing = (f'<div class="drawing"><svg viewBox="{vb_pad}" role="img" aria-label="Construction drawing of the wordmark">'
           f'<rect x="{draw_vb[0] - bh}" y="{-bh}" width="{draw_vb[2] + 2 * bh}" height="{cap + 2 * bh}" fill="none" stroke="#141618" stroke-opacity=".35" stroke-dasharray="40 30" stroke-width="10"/>'
           f'<path fill="#141618" d="{BRAND["pal"]}"/><path fill="#FF4F12" fill-rule="evenodd" d="{BRAND["block"]}"/><path fill="#141618" d="{BRAND["online"]}"/>{dims}</svg></div>')
donts = ''
for cap_txt, style, extra in [
    ('Never stretch or squash it', 'transform:scaleX(1.35)', ''),
    ('Never recolour the block outside the palette', '--block-fill:#2C7BE5', ''),
    ('Never set the name in another face', '', 'font'),
    ('Never draw two cores: it turns into a face', '', 'two'),
    ('Never add rebar or the line to the logo', '', 'bars'),
    ('Never place it on a busy photograph', '', 'photo')]:
    if extra == 'font':
        art = '<p style="font:800 34px/1 Georgia,serif;margin:0">Pal-Online</p>'
    elif extra == 'two':
        two = 'M0 0h1200v600H0zM150 130h330v340H150zM720 130h330v340H720z'
        art = (f'<svg class="w" viewBox="{" ".join(str(v) for v in draw_vb)}"><path fill="currentColor" d="{BRAND["pal"]}"/>'
               f'<path fill="currentColor" fill-rule="evenodd" transform="translate({bx} {by})" d="{two}"/><path fill="currentColor" d="{BRAND["online"]}"/></svg>')
    elif extra == 'bars':
        bars = ''.join(f'<path d="M{bx + 260 + i * 340} {by}v-700" stroke="#983812" stroke-width="70" fill="none"/>' for i in range(3))
        art = (f'<svg class="w" viewBox="{draw_vb[0]} -800 {draw_vb[2]} {cap + 800}">{bars}<path d="M{draw_vb[0]} {by - 400}h{draw_vb[2]}" stroke="#FF4F12" stroke-width="40"/>'
               f'<path fill="currentColor" d="{BRAND["pal"]}"/><path fill="currentColor" fill-rule="evenodd" d="{BRAND["block"]}"/><path fill="currentColor" d="{BRAND["online"]}"/></svg>')
    elif extra == 'photo':
        art = (f'<div style="position:absolute;inset:0;background:repeating-linear-gradient(115deg,#7A6B5A 0 18px,#B9A58C 18px 30px,#4E5A63 30px 52px)"></div>'
               f'<svg class="w" style="position:relative;color:#F3F4F1" viewBox="{" ".join(str(v) for v in draw_vb)}"><path fill="currentColor" d="{BRAND["pal"]}"/><path fill="currentColor" fill-rule="evenodd" d="{BRAND["block"]}"/><path fill="currentColor" d="{BRAND["online"]}"/></svg>')
    else:
        art = f'<div style="{style};width:100%;max-width:240px">{wordmark()}</div>'
    donts += f'<figure>{art}{XMARK}<figcaption>{e(cap_txt)}</figcaption></figure>'

wordmark_s = section(2, 'wordmark', 'Wordmark',
                     'The name is set in Hepta Slab Black, outlined, with a hollow block where the hyphen goes. The block is drawn to the real 2:1 face and rides the middle of the x-height, where a hyphen sits. Keep clear space of one block height on every side.',
                     f'{drawing}<p class="cap"><b>Construction.</b> Block 1200 × 600 units on a 2000-unit em; three cores, face shells heavier than a real block so the hyphen survives at 16 px. Gaps are optical: 150 units after the l, 128 before the round O.</p>'
                     f'<div class="lockups" style="margin-top:30px"><div class="lk-mortar">{wordmark()}</div><div class="lk-night">{wordmark()}</div><div class="lk-line">{wordmark()}</div></div>'
                     f'<p class="cap"><b>Three grounds.</b> Charcoal on mortar is the default. On night, the block may take the line colour; on the line, everything is charcoal. Minimum width 120 px on screen, 30 mm in print.</p>'
                     f'<h3 style="margin-top:40px">Misuse</h3><div class="donts">{donts}</div>')

mark_s = section(3, 'mark', 'Mark',
                 'Where the name will not fit, the block stands alone under the line: the next course about to be laid. It is the avatar, the favicon and the loader\'s last frame.',
                 f'<div class="cols" style="--n:4">'
                 f'<div><img src="assets/brand/mark.svg?v={V}" alt="The mark: a charcoal block under an orange line on mortar" width="400" height="400"><p class="cap"><b>Mortar.</b> Default.</p></div>'
                 f'<div><img src="assets/brand/mark-night.svg?v={V}" alt="The mark on charcoal" width="400" height="400"><p class="cap"><b>Night.</b> Social avatar.</p></div>'
                 f'<div><img src="assets/brand/mark-line.svg?v={V}" alt="The mark on the line colour" width="400" height="400"><p class="cap"><b>Line.</b> Campaigns, the tell-us call.</p></div>'
                 f'<div style="display:flex;gap:18px;align-items:flex-end"><img src="assets/brand/favicon.svg?v={V}" alt="Favicon, 64 px" width="64" height="64"><img src="assets/brand/favicon.svg?v={V}" alt="Favicon, 32 px" width="32" height="32"><img src="assets/brand/favicon.svg?v={V}" alt="Favicon, 16 px" width="16" height="16"></div></div>'
                 f'<p class="cap" style="max-width:70ch"><b>Proportion.</b> The block is 62% of the square, sitting just below the centre; the line runs edge to edge 8.5% above it, so in a round avatar crop the block stays whole and the line reads as a horizon.</p>')

sw = [('s-mortar w', 'Mortar', '#F3F4F1', 'The page. Lime mortar, cool. Never cream.'),
      ('blk s-block w', 'Block', '#D9DBD6', 'Every block face, multiplied with the cast-concrete tile.'),
      ('s-ink w', 'Charcoal', '#141618', 'The one structural ink: type, rules, the foundation.'),
      ('s-line w', 'Line', '#FF4F12', 'The mason\'s line. Today, focus, the live mark. Never body text.'),
      ('s-oxide w', 'Oxide', '#983812', 'Rebar. The text-safe shade of the line: chalk numbers, links on mortar.'),
      ('blk s-night w', 'Night block', '#272B2E', 'Dark courses: the chain, the foundation, night mode.')]
swatches = ''.join(f'<div class="sw {c}"><h3>{n}</h3><div><p class="hex">{h}</p><p>{d}</p></div></div>' for c, n, h, d in sw)
pairs = [('#141618', '#F3F4F1', 'Charcoal on mortar', '17.3:1', 'All text'),
         ('#141618', '#D9DBD6', 'Charcoal on block', '13.4:1', 'All text'),
         ('#464B4F', '#D9DBD6', 'Secondary on block', '5.8:1', 'Trades, places, units'),
         ('#983812', '#F3F4F1', 'Oxide on mortar', '6.6:1', 'Links, chalk numbers'),
         ('#983812', '#D9DBD6', 'Oxide on block', '5.1:1', 'Chalk numbers'),
         ('#141618', '#FF4F12', 'Charcoal on line', '6.0:1', 'Text on line fields'),
         ('#FF4F12', '#F3F4F1', 'Line on mortar', '3.0:1', 'Marks and rules only, never text')]
rows = ''.join(f'<tr><td><span class="chip" style="background:{a}"></span><span class="chip" style="background:{b}"></span>{n}</td><td class="n">{r}</td><td>{u}</td></tr>' for a, b, n, r, u in pairs)
colour_s = section(4, 'colour', 'Colour',
                   'One ink, one line. The wall is printed in charcoal on concrete and mortar; the orange of the mason\'s line is the only live colour, and photographs carry everything else. Nothing on the page is coloured for decoration.',
                   f'<div class="wall swatches">{swatches}</div>'
                   f'<div class="ratio" aria-label="Rough share of each colour on a page"><span style="flex:52;background:#F3F4F1;outline:1px solid #14161826">Mortar 52%</span><span style="flex:24;background:#D9DBD6">Block 24%</span><span style="flex:16;background:#141618;color:#F3F4F1">Charcoal 16%</span><span style="flex:5;background:#983812;color:#F3F4F1">5</span><span style="flex:3;background:#FF4F12"></span></div>'
                   f'<table class="pairs"><thead><tr><th>Pair</th><th>Contrast</th><th>Use</th></tr></thead><tbody>{rows}</tbody></table>'
                   f'<p class="cap">Night mode swaps the grounds (mortar #101213, block #2A2E31) and lifts oxide to #FF8A5C; the line stays the same orange.</p>')

type_s = section(5, 'type', 'Type',
                 'Printers called slab serifs **block serifs**. Hepta Slab carries the display voice: the name, headlines, names of people. Mona Sans carries everything a reader scans: text, places, units and the rates, set narrow and heavy so a day\'s pay fits a block.',
                 f'<div class="spec"><p class="aa" style="font-family:var(--display);font-weight:800">Aa</p><div><h3>Hepta Slab 700 · 800</h3><p class="set" style="font-family:var(--display);font-weight:700">He used to design websites. Now he breaks concrete for $20 a day</p><p class="cap">Mint Type, OFL. Headlines 800, names and small heads 700. No italic: quotes go to Mona Sans italic.</p></div></div>'
                 f'<div class="spec"><p class="aa" style="font-family:var(--text);font-weight:900;font-stretch:75%">₪50</p><div><h3>Mona Sans 400 to 900, width 75 to 100</h3><p class="set" style="font-family:var(--text);font-weight:450">Qassam studied IT and built websites. In the ruins of Khan Younis he swings a sledgehammer to free iron and tiles a middleman can sell on.</p><div class="widths"><span style="font-stretch:75%">$16.50</span><span style="font-stretch:88%;font-weight:700">$16.50</span><span style="font-stretch:100%;font-weight:450">$16.50</span></div><p class="cap">GitHub, OFL. Rates at width 75, weight 900, tabular figures; labels at width 82, weight 650.</p></div></div>'
                 f'<h3 style="margin-top:40px">The shekel we drew</h3><p style="max-width:66ch">Hepta Slab ships without a shekel sign, and on this site the shekel is the most used symbol after the full stop. We drew one for each weight we use, built like the face\'s own dollar: no serifs, square joints, verticals at the weight of the figures beside it.</p>'
                 f'<div class="shekels"><div><p class="g" style="font-family:var(--display);font-weight:800">₪3</p><p class="cap">Hepta Slab 800, drawn</p></div><div><p class="g" style="font-family:var(--display);font-weight:700">₪50</p><p class="cap">Hepta Slab 700, drawn</p></div><div><p class="g" style="font-family:var(--text);font-weight:900;font-stretch:75%">₪50</p><p class="cap">Mona Sans 900, width 75, as shipped</p></div></div>'
                 f'<table class="scale"><tbody>'
                 f'<tr><td>Lead</td><td style="font:800 44px/1.04 var(--display)">Gaza\'s rubble, cleared by hand</td><td>Hepta 800 · 32–54 px · 1.04</td></tr>'
                 f'<tr><td>Section</td><td style="font:800 32px/1.06 var(--display)">Changed trades</td><td>Hepta 800 · 28–40 px</td></tr>'
                 f'<tr><td>Person</td><td style="font:700 20px/1.16 var(--display)">Saleh Musbah, 33</td><td>Hepta 700 · 19–21 px</td></tr>'
                 f'<tr><td>Rate</td><td style="font:900 46px/.9 var(--text);font-stretch:75%">₪50</td><td>Mona 900 · width 75 · 34–58 px</td></tr>'
                 f'<tr><td>Text</td><td style="font:400 17.5px/1.6 var(--text)">Every rate is as the worker told the reporter.</td><td>Mona 400 · 17.5 px · 1.6</td></tr>'
                 f'<tr><td>Label</td><td style="font:650 13px/1.2 var(--text);font-stretch:82%;letter-spacing:.04em">Khan Younis · 26 Sep</td><td>Mona 650 · width 82 · 13 px</td></tr>'
                 f'</tbody></table>')

demo = ''.join(f'<div class="blk {s}">{t}</div>' for s, t in [
    ('w', 'block'), ('w', 'block'), ('w', 'block'), ('w', 'block'),
    ('h', 'half'), ('w', 'block'), ('w', 'block'), ('w', 'block'), ('h', 'half'),
    ('w', 'block'), ('w', 'block'), ('w', 'block'), ('w', 'block')])


def mini(halves, pattern):
    return f'<div class="wall" style="--halves:{halves}">' + ''.join(f'<div class="blk {p}"></div>' for p in pattern) + '</div>'


wall_s = section(6, 'wall', 'The wall',
                 'Layouts are walls in running bond: every course is offset half a block from the one below, so no joint runs through two courses. The grid counts half blocks; a full block spans two, a half block spans one. Joints are 6 px of mortar.',
                 f'<div class="wall demo-wall">{demo}</div>'
                 f'<div class="bp"><div>{mini(8, ["w"] * 4 + ["h", "w", "w", "w", "h"] + ["w"] * 4)}<p class="cap"><b>Desktop.</b> Eight halves: four blocks a course.</p></div>'
                 f'<div>{mini(6, ["w"] * 3 + ["h", "w", "w", "h"] + ["w"] * 3)}<p class="cap"><b>Tablet.</b> Six halves: three a course.</p></div>'
                 f'<div>{mini(2, ["w", "h", "h", "w", "h", "h"])}<p class="cap"><b>Phone.</b> Two halves: a whole block, then two halves.</p></div></div>'
                 f'<p class="cap" style="max-width:72ch">Today\'s course is always laid on top, with the line stretched across it; older courses sit below on a darker face, and the footer is the foundation. Starter bars only ever stand at the top edge.</p>')

anat_person = dict(C0, size='w')
variants = (person(dict(C0, size='w')) + person(dict(ED['course'][1], size='h')) + person(dict(ED['course'][2], old=True)) +
            f'<article class="blk blk--night who w"><h3>{e(ED["chain"]["links"][0]["name"])}</h3><p class="trade">{e(ED["chain"]["links"][0]["role"])}</p><p class="rate num">{e(ED["chain"]["links"][0]["rate"])}<small>{e(ED["chain"]["links"][0]["unit"])}</small></p></article>'
            '<div class="blk--gap w" style="display:grid;place-items:center;font:700 14px var(--text);color:var(--oxide)">Your block</div>')
block_s = section(7, 'block', 'The block',
                  'A person is a block: name first, then the trade in plain words, the place, and what they are paid, as they told the reporter. One number may be chalked in the corner when the source gives it: hours worked, times displaced, metres from shore.',
                  f'<div class="anat"><div class="specimen wall" style="--halves:2">{person(anat_person)}'
                  f'<span class="pin-n" style="left:-12px;top:10px">1</span><span class="pin-n" style="left:-12px;top:44px">2</span><span class="pin-n" style="left:-12px;top:74px">3</span><span class="pin-n" style="left:-12px;bottom:30px">4</span><span class="pin-n" style="right:-12px;top:8px">5</span></div>'
                  f'<ol><li><div><b>Name, age.</b> Hepta Slab 700. The whole block links to the story.</div></li><li><div><b>Trade.</b> What they do now, in plain words: breaks concrete, sells internet cards.</div></li>'
                  f'<li><div><b>Place.</b> Town or camp, in its common English news form.</div></li><li><div><b>Rate.</b> As told, in the currency they were paid in. Mona Sans 900 at width 75, tabular figures; the unit goes underneath.</div></li>'
                  f'<li><div><b>Chalk.</b> One number from the source, in oxide. Never a hue, never a badge.</div></li></ol></div>'
                  f'<div class="wall variants">{variants}</div>'
                  f'<p class="cap"><b>Variants.</b> Full block · half block (name and rate only) · older course · night course · the gap, where a reader\'s story goes.</p>')

marks_s = section(8, 'marks', 'Marks',
                  'Crews mark walls by hand, and the site marks state the same way. A mark is drawn once, in the line colour or oxide, and it carries meaning that colour alone never does, so it also works for readers who do not see colour.',
                  f'<div class="marks">'
                  f'<div><div class="art">{XMARK.replace("x-mark", "x-mark big")}</div><div class="txt"><h3>Cross</h3><p>Closed, sealed, cut off. Crossings and roads.</p></div></div>'
                  f'<div><div class="art">{OPEN.replace("x-mark", "x-mark big")}</div><div class="txt"><h3>Tick</h3><p>Open, paid, back at work.</p></div></div>'
                  f'<div><div class="art"><p class="reg-demo" style="margin:0"><span class="spray">Goldsmith</span></p></div><div class="txt"><h3>Strike</h3><p>A trade someone no longer has. Sprayed when the row arrives.</p></div></div>'
                  f'<div><div class="art"><p style="font:750 46px/1 var(--text);font-stretch:78%;color:var(--oxide);margin:0">12 h</p></div><div class="txt"><h3>Chalk</h3><p>The one number the source gives beside the rate.</p></div></div></div>')

lay_demo = '<div class="wall lay-demo">' + ''.join(f'<div class="blk {s}" style="--i:{i}"></div>' for i, s in enumerate(['w', 'w', 'w', 'h', 'w', 'w', 'h', 'w', 'w', 'w'])) + '</div>'
pluck_demo = '<div class="wall" data-line="line-mo">' + ''.join(f'<div class="blk w" tabindex="0" aria-label="Block {i + 1}"></div>' for i in range(3)) + '</div>'
motion_s = section(9, 'motion', 'Motion',
                   'The site moves the way a wall goes up, and only then. Four motions, each with one job; nothing else animates. Every one of them is skipped when the reader asks for reduced motion, and the page is complete without them.',
                   f'<div class="motion">'
                   f'<div class="mo"><h3>Snap</h3><div class="stage"><div class="mline" id="line-snap" style="height:60px"><svg viewBox="0 0 1000 60" preserveAspectRatio="none" aria-hidden="true"><path class="string" d="M0 30L1000 30"/></svg></div></div><p class="spec-t">The line is stretched once, in the loader: slack, then taut on a damped spring, <code>6.2 Hz</code>, <code>τ 110 ms</code>.</p><button class="btn" type="button" data-demo="snap">Snap the line</button></div>'
                   f'<div class="mo"><h3>Lay</h3><div class="stage">{lay_demo}</div><p class="spec-t">Blocks are set course by course as a wall arrives: down 14 px and tapped level, <code>550 ms</code>, <code>cubic-bezier(.2,.9,.25,1.25)</code>, 55 ms apart.</p><button class="btn" type="button" data-demo="lay">Lay the course</button></div>'
                   f'<div class="mo"><h3>Pluck</h3><div class="stage">{line("line-mo", "Point at a block")}{pluck_demo}</div><p class="spec-t">The signature. Pointing at or tabbing to a person plucks the line above their course: <code>7 Hz</code>, <code>τ 260 ms</code>, 10 px.</p></div>'
                   f'<div class="mo"><h3>Spray</h3><div class="stage"><p class="reg-demo"><span class="spray">Nursing graduate</span> → sells internet cards</p></div><p class="spec-t">A struck trade is sprayed once, left to right, <code>750 ms</code>, when its row comes into view.</p><button class="btn" type="button" data-demo="spray">Spray it</button></div>'
                   f'</div><p class="cap" style="margin-top:18px"><b>Loader.</b> Once per session: the pins land, the line snaps, the block is lowered to it and tapped twice, the name opens out from behind it, and the page is lifted. Any key or click skips it. <button class="btn" type="button" data-demo="loader" style="min-height:40px">Replay the loader</button></p>')

pc = ED['social']
hund = ''.join(f'<i{" class=o" if i < pc["number"]["out"] else ""}></i>' for i in range(100))
closed_svg = '<i class="sp sp-x" aria-hidden="true"></i>'
posts = (f'<figure><div class="frame"><div class="post p-worker"><span class="post-line" style="top:9cqw"></span><div class="blkp"><p class="nm">{e(pc["worker"]["name"])}</p><p class="tr">{e(pc["worker"]["trade"])}</p><p class="rt">{e(pc["worker"]["rate"])}<small>{e(pc["worker"]["unit"])}</small></p><p class="qt">“{e(pc["worker"]["quote"])}”</p></div><p class="sr2">{e(pc["worker"]["src"])}</p><div class="wm">{wordmark()}</div></div></div><figcaption><b>Worker.</b> The default post: one person, one block. <a href="assets/brand/social/post-worker.png">PNG 1080 × 1350</a></figcaption></figure>'
         f'<figure><div class="frame"><div class="post p-number"><p class="fig">{e(pc["number"]["value"])}</p><p class="what">{e(pc["number"]["what"])}</p><div class="hund">{hund}</div><p class="sr2">{e(pc["number"]["src"])}</p><div class="wm" style="color:#ECEEEA;--block-fill:#FF4F12">{wordmark()}</div></div></div><figcaption><b>Number.</b> A count, with who counted. <a href="assets/brand/social/post-number.png">PNG</a></figcaption></figure>'
         f'<figure><div class="frame"><div class="post p-quote"><p class="q">{e(pc["quote"]["text"])}</p><p class="by">{e(pc["quote"]["by"])}</p><div class="wm">{wordmark()}</div></div></div><figcaption><b>Quote.</b> Words as published. <a href="assets/brand/social/post-quote.png">PNG</a></figcaption></figure>'
         f'<figure><div class="frame"><div class="post p-closed"><span class="post-line" style="top:9cqw"></span><p class="pl">{e(pc["closed"]["place"])}{closed_svg}</p><p class="st">{e(pc["closed"]["state"])}</p><p class="dd">{e(pc["closed"]["d"])}</p><p class="sr2">{e(pc["closed"]["src"])}</p><div class="wm">{wordmark()}</div></div></div><figcaption><b>Closed.</b> A crossing or road, marked. <a href="assets/brand/social/post-closed.png">PNG</a></figcaption></figure>')
social_s = section(10, 'social', 'Social',
                   'Most readers meet Pal-Online in a feed, so every story must survive as one card. Four templates cover the edition; each carries its source on the card itself, because a screenshot travels without its link.',
                   f'<div class="social">{posts}</div>'
                   f'<div class="avatars"><img src="assets/brand/social/avatar-night-240.png?v={V}" alt="Round avatar, night" width="120" height="120"><img src="assets/brand/social/avatar-mortar-240.png?v={V}" alt="Round avatar, mortar" width="120" height="120"><img class="sq" src="assets/brand/social/avatar-night-240.png?v={V}" alt="Square avatar, night" width="120" height="120"><p class="cap">Avatars, 1080 px: night for X and Instagram, mortar for Telegram and WhatsApp.</p></div>')

voice_s = section(11, 'voice', 'Voice',
                  'Plain, exact, unhurried. The reader should finish every story knowing a name, a trade and a number, and where the number came from.',
                  f'<div class="voice">'
                  f'<div><h3>A person before a number</h3><p>Open on someone at work, then widen to the figure.</p><p class="do"><b class="tag">Write</b>Saleh Musbah, 33, moves debris in Khan Younis for 50 shekels a day.</p><p class="dont">{XMARK}<b class="tag">Not</b>Daily wages in Gaza\'s debris-clearing sector remain depressed.</p></div>'
                  f'<div><h3>Every figure with its source and date</h3><p>Competing counts sit side by side and are never averaged.</p><p class="do"><b class="tag">Write</b>68%, Gaza labour ministry, 8 Oct. More than 90%, UNCTAD, 24 Sep.</p><p class="dont">{XMARK}<b class="tag">Not</b>Unemployment in Gaza is around 80%.</p></div>'
                  f'<div><h3>Trades in plain words</h3><p>Name the work the way the worker would.</p><p class="do"><b class="tag">Write</b>Breaks concrete. Carries water. Sells prepaid internet cards.</p><p class="dont">{XMARK}<b class="tag">Not</b>Engaged in informal rubble-removal livelihood activities.</p></div></div>')

dls = [('assets/brand/pal-online-identity.zip', 'Identity kit (zip)', 'Logos in SVG, avatars and social templates in PNG, fonts licence'),
       ('assets/brand/logo.svg', 'Wordmark, charcoal (SVG)', 'Default on mortar and light photographs'),
       ('assets/brand/logo-line.svg', 'Wordmark, line block (SVG)', 'Hero use on mortar'),
       ('assets/brand/logo-night-line.svg', 'Wordmark, night (SVG)', 'On charcoal; block in the line colour'),
       ('assets/brand/mark.svg', 'Mark (SVG)', 'The block under the line'),
       ('assets/fonts/OFL.txt', 'Font licences', 'Hepta Slab and Mona Sans, SIL Open Font License 1.1')]
PAGES = [('home.html', 'Today', 'The homepage: today’s course on top, the chain, changed trades, the count, workplaces, money and moving.'),
         ('article.html', 'A story', 'One person’s block beside the text, how we know, the chain inline, share and correct.'),
         ('wall.html', 'The wall', 'Everyone on the site, filtered by place and kind of work; the bond re-lays itself.'),
         ('money.html', 'Money', 'A payslip first, then the changer, salaries as what is paid and what is short, cash and prices on the slab.'),
         ('moving.html', 'Moving', 'The board: each crossing, gate and closed field with its mark, date and source.'),
         ('count.html', 'The count', 'Every unemployment figure on one wall of a hundred people, and other counts on the slab.'),
         ('harvest.html', 'A topic', 'The olive harvest, split Gaza and West Bank, people first, then the figures.'),
         ('khan-younis.html', 'A place', 'Khan Younis: its people, its figures, every report from there; the template for any town, camp or tag.'),
         ('tell.html', 'Tell us your work', 'Four steps to a block, and the form with every state.'),
         ('about.html', 'About', 'What the site is, six reporting rules, corrections, contact.'),
         ('privacy.html', 'Privacy', 'What the form collects, who sees it, what the browser keeps.'),
         ('search.html', 'Search', 'Every checked item, matched word by word, filtered by desk.'),
         ('404.html', 'Not found', 'A wall with one block missing.')]
pages_wall = ''.join(f'<a class="blk w" href="{h}" style="display:flex;flex-direction:column;gap:6px;padding:14px 16px;text-decoration:none;min-height:150px"><h3 style="margin:0">{e(t)}</h3><p style="font-size:14.5px;line-height:1.45;color:var(--ink-2)">{e(d)}</p><p class="src" style="margin-top:auto">{h}</p></a>' for h, t, d in PAGES)
pages_s = section(12, 'pages', 'Pages',
                  'Thirteen templates, all built from the same block, line and marks. Each page lists its own sources at the foot.',
                  f'<div class="wall" style="--halves:8">{pages_wall}</div>')

dl_s = section(13, 'downloads', 'Downloads',
               'Everything the newsroom and its designers need to set the brand in place. The fonts are free under the SIL Open Font License; the drawn shekel ships inside the site\'s Hepta Slab files.',
               '<ul class="dl">' + ''.join(f'<li><a href="{h}?v={V}" download>{t}</a><span>{d}</span></li>' for h, t, d in dls) + '</ul>')

foot = (f'<footer class="g-foot"><div class="wrap"><div><a class="home" href="home.html" aria-label="Pal-Online homepage">{wordmark()}</a>'
        f'<p>Identity guide, first edition, {e(ED["short_date"])}. Direction «Midmak», prepared for the Pal-Online team.</p></div>'
        f'<div><p>{rich(ED["foot"]["proto"])}</p><p style="margin-top:10px">Fonts: Hepta Slab (Mint Type) and Mona Sans (GitHub), SIL Open Font License 1.1. The shekel sign in Hepta Slab was drawn for this identity.</p></div></div></footer>')

CONTRACT = open(os.path.join(ROOT, 'tools', 'contract.txt'), encoding='utf-8').read().strip()
page = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{EARLY}
<meta name="robots" content="noindex, nofollow">
<title>Pal-Online — identity guide</title>
<meta name="description" content="The Pal-Online identity: the Midmak system of block, line, bars and marks.">
<meta name="theme-color" content="#F3F4F1" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#101213" media="(prefers-color-scheme: dark)">
<link rel="icon" href="assets/brand/favicon.svg?v={V}" type="image/svg+xml">
<link rel="preload" href="assets/fonts/hepta-slab-800.woff2?v=1" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="assets/fonts/mona-sans.woff2?v=1" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="assets/css/po.css?v={V}">
<link rel="stylesheet" href="assets/css/home.css?v={V}">
<link rel="stylesheet" href="assets/css/guide.css?v={V}">
</head>
<body>
<!--
{CONTRACT}
-->
<a class="skip" href="#idea">Skip to the guide</a>
{top}
<main>
{cover}
{idea}
{wordmark_s}
{mark_s}
{colour_s}
{type_s}
{wall_s}
{block_s}
{marks_s}
{motion_s}
{social_s}
{voice_s}
{pages_s}
{dl_s}
</main>
{foot}
<script src="assets/js/po.js?v={V}" defer></script>
<script src="assets/js/guide.js?v={V}" defer></script>
</body>
</html>
'''
open(os.path.join(ROOT, 'index.html'), 'w', encoding='utf-8').write(page)
print('index.html', len(page), 'bytes')
