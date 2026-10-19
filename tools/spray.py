"""Paints the spray marks: cross, tick, slash and strike, as an aerosol can lays them on concrete.

python -I tools/spray.py   (from the project root)

Each mark is a path; the can deposits paint as a dense core with a soft overspray,
heavier where the hand slows (the start and the turns) and thinner where it moves fast.
Output: assets/img/spray-<name>.webp, RGBA in the line orange, used as CSS masks and backgrounds.
"""
import os
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'assets', 'img')
os.makedirs(OUT, exist_ok=True)
ORANGE = (255, 79, 18)


def lerp_path(points, step):
    """Resamples a polyline at a fixed step; returns positions and the local speed factor (slower near corners)."""
    pts = []
    speed = []
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        n = max(2, int(np.hypot(x1 - x0, y1 - y0) / step))
        for i in range(n):
            t = i / n
            pts.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t))
            speed.append(0.55 + 0.45 * np.sin(np.pi * t))   # the hand slows at both ends of a stroke
    pts.append(points[-1])
    speed.append(0.55)
    return np.array(pts), np.array(speed)


def paint(w, h, strokes, width, seed, mist=1.0):
    rng = np.random.default_rng(seed)
    dens = np.zeros((h, w), np.float32)
    for points in strokes:
        pts, speed = lerp_path(points, step=width * 0.12)
        for (x, y), v in zip(pts, speed):
            n_core = int(70 / v)
            n_mist = int(30 * mist / v)
            jitter = rng.normal(0, width * 0.04, 2)
            cx, cy = x + jitter[0], y + jitter[1]
            core = rng.normal(0, width * 0.26, (n_core, 2))
            spray = rng.normal(0, width * 0.85, (n_mist, 2))
            for arr, wgt in ((core, 1.0), (spray, 0.18)):
                xs = np.clip((cx + arr[:, 0]).astype(int), 0, w - 1)
                ys = np.clip((cy + arr[:, 1]).astype(int), 0, h - 1)
                np.add.at(dens, (ys, xs), wgt)
    # soften the particle grain a little, as paint spreads into the concrete's pores
    k = np.array([1, 4, 6, 4, 1], np.float32)
    k = k / k.sum()
    for axis in (0, 1):
        dens = np.apply_along_axis(lambda m: np.convolve(m, k, mode='same'), axis, dens)
    alpha = 1 - np.exp(-dens * 0.95)
    speck = rng.random((h, w)) < 0.0012     # stray droplets in the overspray
    alpha = np.maximum(alpha, speck * rng.uniform(0.35, 0.8, (h, w)))
    img = np.zeros((h, w, 4), np.uint8)
    img[..., 0], img[..., 1], img[..., 2] = ORANGE
    img[..., 3] = (np.clip(alpha, 0, 1) * 255).astype(np.uint8)
    return Image.fromarray(img, 'RGBA')


def save(im, name):
    path = os.path.join(OUT, f'spray-{name}.webp')
    im.save(path, quality=86, method=6)
    print(os.path.relpath(path, ROOT), im.size, os.path.getsize(path), 'bytes')


S = 200
save(paint(S, S, [[(40, 38), (100, 102), (162, 166)], [(160, 36), (102, 98), (42, 164)]], 22, 11), 'cross')
save(paint(S, S, [[(34, 108), (62, 132), (84, 160), (118, 112), (166, 40)]], 22, 12), 'tick')
save(paint(S, S, [[(52, 160), (100, 100), (150, 40)]], 22, 13), 'slash')
save(paint(1200, 70, [[(10, 38), (300, 33), (620, 37), (900, 31), (1190, 35)]], 14, 14, mist=0.8), 'strike')
