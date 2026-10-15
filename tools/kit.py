"""Packs the identity kit for download.

python -I tools/kit.py   (after brand.py and social.mjs)
Writes assets/brand/pal-online-identity.zip: logos and marks (SVG), avatars and social
templates (PNG), the font licences.
"""
import glob, os, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
B = os.path.join(ROOT, 'assets', 'brand')
out = os.path.join(B, 'pal-online-identity.zip')
with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
    for f in sorted(glob.glob(os.path.join(B, '*.svg'))):
        z.write(f, 'logos/' + os.path.basename(f))
    for f in sorted(glob.glob(os.path.join(B, 'social', '*.png'))):
        z.write(f, 'social/' + os.path.basename(f))
    z.write(os.path.join(ROOT, 'assets', 'fonts', 'OFL.txt'), 'fonts/OFL.txt')
    z.writestr('README.txt', 'Pal-Online identity kit, direction Midmak.\n'
               'Fonts: Hepta Slab (Mint Type) and Mona Sans (GitHub), SIL Open Font License 1.1, free from Google Fonts.\n'
               'The shekel sign in Hepta Slab was drawn for this identity and ships in the site font files.\n'
               'Colours: mortar #F3F4F1, block #D9DBD6, charcoal #141618, line #FF4F12, oxide #983812, night block #272B2E.\n')
print(os.path.relpath(out, ROOT), os.path.getsize(out), 'bytes')
