"""Draws the Pal-Online marks from Hepta Slab Black outlines.

python -I tools/brand.py   (from the project root)

The wordmark is the name set as one course: «Pal», a hollow concrete block where the
hyphen goes, «Online». The block keeps the proportions of the block Gaza and the West Bank
are built with (40 x 20 cm face, three cores; two cores read as a face at small sizes).
The mason's line is drawn by the pages, not baked in.
Writes assets/brand/*.svg and tools/out/brand.json (path data for inline use).
"""
import json, os
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'research', 'fontlab', 'src', 'HeptaSlab.ttf')
OUT_BRAND = os.path.join(ROOT, 'assets', 'brand')
OUT_DATA = os.path.join(ROOT, 'tools', 'out')
os.makedirs(OUT_BRAND, exist_ok=True)
os.makedirs(OUT_DATA, exist_ok=True)

FONT = instancer.instantiateVariableFont(TTFont(SRC), {'wght': 900})
GS, CMAP, HMTX = FONT.getGlyphSet(), FONT.getBestCmap(), FONT['hmtx']

INK, MORTAR, LINE = '#141618', '#F3F4F1', '#FF4F12'

# --- the block, in font units (UPM 2000). 40 x 20 cm face -> 1200 x 600 ---
BLOCK_W, BLOCK_H = 1200, 600
BLOCK_Y = 236                      # bottom edge: the block rides the x-height's middle, like a hyphen
CORES = 3
SHELL_X, SHELL_Y, WEB = 176, 160, 150   # face shells and webs, heavier than a real block so it holds at 16 px
CORE_W = (BLOCK_W - 2 * SHELL_X - WEB * (CORES - 1)) / CORES
CORE_H = BLOCK_H - 2 * SHELL_Y
GAP_L, GAP_R = 150, 128            # optical: the round O sits closer than the l's flat stem


def kern_table():
    """Pair kerning from the GPOS 'kern' feature (pair positioning, formats 1 and 2)."""
    gpos = FONT['GPOS'].table
    idx = set()
    for fr in gpos.FeatureList.FeatureRecord:
        if fr.FeatureTag == 'kern':
            idx.update(fr.Feature.LookupListIndex)
    pairs = {}
    for i in sorted(idx):
        lk = gpos.LookupList.Lookup[i]
        for st in lk.SubTable:
            if lk.LookupType == 9:
                st = st.ExtSubTable
            if getattr(st, 'Format', None) == 1 and hasattr(st, 'PairSet'):
                for g1, ps in zip(st.Coverage.glyphs, st.PairSet):
                    for pvr in ps.PairValueRecord:
                        v = getattr(pvr.Value1, 'XAdvance', 0) if pvr.Value1 else 0
                        pairs.setdefault((g1, pvr.SecondGlyph), v)
            elif getattr(st, 'Format', None) == 2 and hasattr(st, 'Class1Record'):
                c1 = st.ClassDef1.classDefs
                c2 = st.ClassDef2.classDefs
                for g1 in st.Coverage.glyphs:
                    k1 = c1.get(g1, 0)
                    rec = st.Class1Record[k1]
                    for g2, k2 in list(c2.items()) + []:
                        v = rec.Class2Record[k2].Value1
                        x = getattr(v, 'XAdvance', 0) if v else 0
                        if x:
                            pairs.setdefault((g1, g2), x)
    return pairs


KERN = kern_table()


def bounds(name):
    bp = BoundsPen(GS)
    GS[name].draw(bp)
    return bp.bounds


def glyph_path(name, dx, dy):
    pen = SVGPathPen(GS)
    GS[name].draw(TransformPen(pen, (1, 0, 0, -1, dx, dy)))
    return pen.getCommands()


def set_word(text, x, base):
    names = [CMAP[ord(c)] for c in text]
    out = []
    for i, n in enumerate(names):
        out.append(glyph_path(n, x, base))
        x += HMTX[n][0]
        if i < len(names) - 1:
            x += KERN.get((n, names[i + 1]), 0)
    return ''.join(out), x


CAP = 1544                          # H top at weight 900
BASE = CAP                          # SVG y of the baseline when the cap top sits at y = 0
DESC = 0                            # no descenders in the name

pal, x_after_pal = set_word('Pal', 0, BASE)
l_right = x_after_pal - (HMTX['l'][0] - bounds('l')[2])
block_x = l_right + GAP_L
o_left_bearing = bounds('O')[0]
online_x = block_x + BLOCK_W + GAP_R - o_left_bearing
online, x_end = set_word('Online', online_x, BASE)
e_right = x_end - (HMTX['e'][0] - bounds('e')[2])
P_left = bounds('P')[0]

# block as a path with two cores (even-odd)
by_top = BASE - BLOCK_Y - BLOCK_H
cy = by_top + SHELL_Y
core_xs = [block_x + SHELL_X + i * (CORE_W + WEB) for i in range(CORES)]


def rect(x, y, w, h):
    return f'M{x:.0f} {y:.0f}h{w:.0f}v{h:.0f}h{-w:.0f}z'


block = rect(block_x, by_top, BLOCK_W, BLOCK_H) + ''.join(rect(x, cy, CORE_W, CORE_H) for x in core_xs)

VB_X, VB_W = P_left, e_right - P_left
VB_Y, VB_H = 0, CAP
pad = 0


def svg(fill_word, fill_block, title='Pal-Online', vb=None):
    vx, vy, vw, vh = vb or (VB_X, VB_Y, VB_W, VB_H)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vx:.0f} {vy:.0f} {vw:.0f} {vh:.0f}" role="img" '
            f'aria-label="{title}"><title>{title}</title>'
            f'<path fill="{fill_word}" d="{pal}"/><path fill="{fill_block}" fill-rule="evenodd" d="{block}"/>'
            f'<path fill="{fill_word}" d="{online}"/></svg>\n')


def write(name, text):
    with open(os.path.join(OUT_BRAND, name), 'w', encoding='utf-8') as fh:
        fh.write(text)


write('logo.svg', svg(INK, INK))
write('logo-line.svg', svg(INK, LINE))
write('logo-night.svg', svg(MORTAR, MORTAR))
write('logo-night-line.svg', svg(MORTAR, LINE))
write('logo-mono-black.svg', svg('#000', '#000'))
write('logo-mono-white.svg', svg('#fff', '#fff'))

# --- the mark: the block under a taut line, on a square ---
def mark_svg(ground, block_fill, line, size=1000, ground_on=True):
    s = size
    bw = s * 0.62
    bh = bw / 2
    bx = (s - bw) / 2
    by = s * 0.47
    k = bw / BLOCK_W
    shx, shy, web = SHELL_X * k, SHELL_Y * k, WEB * k
    cw = (bw - 2 * shx - web * (CORES - 1)) / CORES
    ch = bh - 2 * shy
    path = rect(bx, by, bw, bh) + ''.join(rect(bx + shx + i * (cw + web), by + shy, cw, ch) for i in range(CORES))
    ly = by - s * 0.085          # the line rides a finger's width above the block: the next course
    lw = s * 0.022
    pin = s * 0.05
    g = f'<rect width="{s}" height="{s}" fill="{ground}"/>' if ground_on else ''
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {s} {s}" role="img" aria-label="Pal-Online">'
            f'<title>Pal-Online</title>{g}'
            f'<rect x="0" y="{ly - lw / 2:.1f}" width="{s}" height="{lw:.1f}" fill="{line}"/>'
            f'<path fill="{block_fill}" fill-rule="evenodd" d="{path}"/></svg>\n')


write('mark.svg', mark_svg(MORTAR, INK, LINE))
write('mark-night.svg', mark_svg(INK, MORTAR, LINE))
write('mark-line.svg', mark_svg(LINE, INK, INK))
write('mark-transparent.svg', mark_svg('none', INK, LINE, ground_on=False))
write('favicon.svg', mark_svg(INK, MORTAR, LINE, size=64))

data = {
    'viewBox': [round(VB_X), VB_Y, round(VB_W), VB_H],
    'pal': pal, 'online': online, 'block': block,
    'blockBox': [round(block_x), round(by_top), BLOCK_W, BLOCK_H],
    'cores': [[round(x), round(cy), round(CORE_W), round(CORE_H)] for x in core_xs],
    'cap': CAP, 'xHeightTop': BASE - 1052,
}
with open(os.path.join(OUT_DATA, 'brand.json'), 'w', encoding='utf-8') as fh:
    json.dump(data, fh)
print('wordmark', round(VB_W), 'x', VB_H, 'units; block at', round(block_x), '; kern pairs', len(KERN))
