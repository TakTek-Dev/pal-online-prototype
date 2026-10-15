"""Builds the self-hosted web fonts.

python -I tools/fonts.py   (from the project root)

Hepta Slab carries the display voice (the block serif) and Mona Sans carries text,
labels and figures. Hepta Slab ships without a shekel sign, so this script draws one
for each weight we use, built like the face's own '$': no serifs, square joints,
verticals a little lighter than the H stem. Mona Sans keeps its variable axes
(width 75-125, weight 200-900); Hepta Slab ships as two static weights.
Sources: research/fontlab/src (Google Fonts repository, OFL).
"""
import io
import os
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.recordingPen import RecordingPen
from fontTools import subset

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'research', 'fontlab', 'src')
OUT = os.path.join(ROOT, 'assets', 'fonts')
os.makedirs(OUT, exist_ok=True)

# Latin, Latin-1, Latin Extended-A, typographic punctuation, currency, arrows, a few math signs
UNICODES = (list(range(0x20, 0x7F)) + list(range(0xA0, 0x180)) +
            [0x2BE, 0x2BF, 0x2010, 0x2011, 0x2012, 0x2013, 0x2014, 0x2018, 0x2019, 0x201A, 0x201C, 0x201D,
             0x201E, 0x2020, 0x2021, 0x2022, 0x2026, 0x2030, 0x2032, 0x2033, 0x2039, 0x203A, 0x2044,
             0x20AC, 0x20AA, 0x2116, 0x2122, 0x2190, 0x2191, 0x2192, 0x2193, 0x2212, 0x2248, 0x2260,
             0x2264, 0x2265, 0x00D7, 0x00F7])
FEATURES = ['kern', 'liga', 'calt', 'tnum', 'lnum', 'pnum', 'onum', 'case', 'frac', 'sups', 'ordn',
            'ss01', 'ss02', 'ss03', 'ss04', 'ss05', 'ss06', 'ccmp', 'locl', 'mark', 'mkmk']


def h_metrics(font):
    """H stem width, crossbar thickness and cap top, read from the instance's own H."""
    gs, cmap = font.getGlyphSet(), font.getBestCmap()
    rp = RecordingPen()
    gs[cmap[ord('H')]].draw(rp)
    pts = [p for _, args in rp.value for p in args]
    xs = sorted(set(round(p[0]) for p in pts))
    ys = sorted(set(round(p[1]) for p in pts))
    # xs: serif-left, stem-left, ..., stem-right, serif-right of the left leg
    stem = xs[3] - xs[1]
    cross = ys[3] - ys[2]
    return stem, cross, ys[-1]


def draw_shekel(font):
    stem, cross, top = h_metrics(font)
    v = round(stem * 0.78)                 # verticals: the weight of the figures beside it
    t = round(cross * 1.0)                 # horizontals: the crossbar
    g = max(92, round(v * 0.3))            # counters: tight, like the figures
    sb = 80
    x0 = sb
    x1 = x0 + v + g                        # inner leg of the U
    x2 = x1 + v + g                        # inner leg of the arch
    x3 = x2 + v + g                        # outer stem of the U
    adv = x3 + v + sb
    y_arch_leg = round(top * 0.34)         # the arch's inner leg stops a third above the baseline
    y_u_leg = round(top * 0.66)            # the U's inner leg stops a third below the cap
    pen = TTGlyphPen(None)
    # arch: outer stem, top bar, inner leg (clockwise)
    for pt in [(x0, 0), (x0, top), (x2 + v, top), (x2 + v, y_arch_leg), (x2, y_arch_leg),
               (x2, top - t), (x0 + v, top - t), (x0 + v, 0)]:
        (pen.moveTo if pt == (x0, 0) else pen.lineTo)(pt)
    pen.closePath()
    # U: inner leg, bottom bar, outer stem (clockwise)
    first = (x1, y_u_leg)
    for pt in [first, (x1 + v, y_u_leg), (x1 + v, t), (x3, t), (x3, top), (x3 + v, top),
               (x3 + v, 0), (x1, 0)]:
        (pen.moveTo if pt == first else pen.lineTo)(pt)
    pen.closePath()
    glyph = pen.glyph()
    name = 'uni20AA'
    font['glyf'][name] = glyph
    font['hmtx'][name] = (adv, x0)
    order = font.getGlyphOrder()
    if name not in order:
        font.setGlyphOrder(order + [name])
    for table in font['cmap'].tables:
        if table.isUnicode():
            table.cmap[0x20AA] = name
    font['maxp'].numGlyphs = len(font.getGlyphOrder())
    return adv


def reload(font):
    """Round-trip through bytes so every table agrees on the new glyph order."""
    buf = io.BytesIO()
    font.save(buf)
    buf.seek(0)
    return TTFont(buf)


def subset_save(font, path):
    opts = subset.Options()
    opts.layout_features = FEATURES
    opts.flavor = 'woff2'
    opts.name_IDs = ['*']
    opts.name_languages = ['*']
    opts.notdef_outline = True
    opts.glyph_names = False
    opts.hinting = False
    sub = subset.Subsetter(options=opts)
    sub.populate(unicodes=UNICODES)
    sub.subset(font)
    font.flavor = 'woff2'
    font.save(path)
    print(os.path.relpath(path, ROOT), os.path.getsize(path), 'bytes')


for w in (700, 800):
    inst = instancer.instantiateVariableFont(TTFont(os.path.join(SRC, 'HeptaSlab.ttf')), {'wght': w},
                                             updateFontNames=True)
    adv = draw_shekel(inst)
    print('Hepta Slab', w, 'shekel advance', adv)
    inst = reload(inst)
    subset_save(inst, os.path.join(OUT, f'hepta-slab-{w}.woff2'))

# Text never needs the expanded widths or the hairline weights: trim the design space to what ships.
mona = instancer.instantiateVariableFont(TTFont(os.path.join(SRC, 'MonaSans.ttf')),
                                         {'wdth': (75, 100), 'wght': (400, 900)})
subset_save(mona, os.path.join(OUT, 'mona-sans.woff2'))
mona_i = instancer.instantiateVariableFont(TTFont(os.path.join(SRC, 'MonaSans-Italic.ttf')),
                                           {'wdth': 100, 'wght': (400, 600)})
subset_save(mona_i, os.path.join(OUT, 'mona-sans-italic.woff2'))

with open(os.path.join(OUT, 'OFL.txt'), 'w', encoding='utf-8') as fh:
    for lic in ('OFL-HeptaSlab.txt', 'OFL-MonaSans.txt'):
        fh.write(open(os.path.join(SRC, lic), encoding='utf-8').read().strip() + '\n\n' + '-' * 72 + '\n\n')
print('assets/fonts/OFL.txt written')
