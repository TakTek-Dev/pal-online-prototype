"""Downloads the Commons photographs the edition uses and makes WebP widths of each.

python -I tools/photos.py   (from the project root; needs ffmpeg with libwebp)

Reads the photo ids used in research/edition.json, fetches each from Wikimedia Commons
(a 2000 px thumbnail when the original is larger), and writes
assets/img/photo/<id>-<w>.webp plus tools/out/photos-local.json for the builders.
"""
import json, os, re, subprocess, time, urllib.parse, urllib.request, urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'research', 'photo-src')
OUT = os.path.join(ROOT, 'assets', 'img', 'photo')
os.makedirs(SRC, exist_ok=True)
os.makedirs(OUT, exist_ok=True)
os.makedirs(os.path.join(ROOT, 'tools', 'out'), exist_ok=True)

photos = {p['id']: p for p in json.load(open(os.path.join(ROOT, 'research', 'photos.json'), encoding='utf-8'))['photos']}
edition = open(os.path.join(ROOT, 'research', 'edition.json'), encoding='utf-8').read()
used = sorted(set(re.findall(r'"photo"\s*:\s*"([^"]+)"', edition)))
WIDTHS = (1800, 1200, 700)
UA = {'User-Agent': 'TakTek-prototype/1.0 (Pal-Online archive photos, credited)'}


def thumb_url(p):
    """Commons serves resized copies at /thumb/<path>/<w>px-<name>, only at its standard steps; take 1920."""
    url = p['url']
    if p.get('width', 0) <= 1920 or '/commons/' not in url:
        return url
    head, name = url.rsplit('/', 1)
    base = head.replace('/wikipedia/commons/', '/wikipedia/commons/thumb/')
    suffix = '.jpg' if name.lower().endswith(('.tif', '.tiff')) else ''
    return f'{base}/{name}/1920px-{name}{suffix}'


def fetch(url, dst):
    for attempt in range(6):        # Commons rate-limits bursts: back off and retry
        try:
            body = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120).read()
            open(dst, 'wb').write(body)
            return
        except urllib.error.HTTPError as ex:
            if ex.code not in (429, 503) or attempt == 5:
                raise
            time.sleep(8 * (attempt + 1))


local = {}
for pid in used:
    p = photos[pid]
    url = thumb_url(p)
    ext = os.path.splitext(urllib.parse.urlparse(url).path)[1].lower() or '.jpg'
    raw = os.path.join(SRC, pid + ext)
    if not os.path.exists(raw):
        fetch(url, raw)
        time.sleep(2)
    probe = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height',
                            '-of', 'csv=p=0', raw], capture_output=True, text=True).stdout.strip().split(',')
    sw, sh = int(probe[0]), int(probe[1])
    made = []
    for w in WIDTHS:
        tw = min(w, sw)
        if any(m[0] == tw for m in made):
            continue
        th = round(sh * tw / sw / 2) * 2
        dst = os.path.join(OUT, f'{pid}-{tw}.webp')
        if not os.path.exists(dst):
            subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', raw, '-vf', f'scale={tw}:{th}:flags=lanczos',
                            '-c:v', 'libwebp', '-quality', '78', '-compression_level', '6', dst], check=True)
        made.append((tw, th, f'assets/img/photo/{pid}-{tw}.webp'))
    made.sort()
    local[pid] = {'w': made[-1][0], 'h': made[-1][1], 'set': [[w, s] for w, h, s in made]}
    print(pid, sw, 'x', sh, '->', [m[0] for m in made])
json.dump(local, open(os.path.join(ROOT, 'tools', 'out', 'photos-local.json'), 'w', encoding='utf-8'), indent=1)
