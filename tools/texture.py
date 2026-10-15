"""Generates the block-face texture: cast concrete, not a grunge overlay.

python -I tools/texture.py   (from the project root)

One seamless 512 px tile, near-white, meant to be multiplied over the block colour
(background-blend-mode: multiply), so the same tile serves every block tone.
Layers: a soft cloud of cement (periodic blur, so the tile wraps), fine sand grain,
aggregate specks, and the small pores a vibrated block face shows.
"""
import os
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'assets', 'img')
os.makedirs(OUT, exist_ok=True)
N = 512
rng = np.random.default_rng(1510)          # fixed seed: the texture is part of the identity


def periodic_blur(a, sigma):
    """Gaussian blur through the FFT, so the result tiles without seams."""
    f = np.fft.fftfreq(N)
    gx, gy = np.meshgrid(f, f)
    kernel = np.exp(-2 * (np.pi * sigma) ** 2 * (gx ** 2 + gy ** 2))
    return np.real(np.fft.ifft2(np.fft.fft2(a) * kernel))


def norm(a):
    a = a - a.mean()
    return a / (np.abs(a).max() + 1e-9)


cloud = norm(periodic_blur(rng.standard_normal((N, N)), 38)) * 0.55 + norm(periodic_blur(rng.standard_normal((N, N)), 12)) * 0.45
sand = norm(periodic_blur(rng.standard_normal((N, N)), 0.9))
tone = 1.0 - 0.075 * (cloud * 0.5 + 0.5) - 0.055 * (sand * 0.5 + 0.5)

yy, xx = np.mgrid[0:N, 0:N]


def stamp(cx, cy, r, depth, soft=0.9):
    """Adds a round mark with a soft edge, wrapping across tile borders."""
    dx = (xx - cx + N / 2) % N - N / 2
    dy = (yy - cy + N / 2) % N - N / 2
    d = np.sqrt(dx ** 2 + (dy * 1.15) ** 2)
    return depth * np.clip((r - d) / soft, 0, 1)


marks = np.zeros((N, N))
for _ in range(2200):         # aggregate: crushed stone, slightly darker or lighter than the paste
    marks -= stamp(rng.uniform(0, N), rng.uniform(0, N), rng.uniform(0.6, 1.6), rng.choice([0.05, 0.035, -0.03]))
for _ in range(190):          # pores: small, dark, sharp
    marks -= stamp(rng.uniform(0, N), rng.uniform(0, N), rng.uniform(1.0, 2.8), rng.uniform(0.10, 0.20), soft=0.6)

img = np.clip(tone + marks, 0, 1)
Image.fromarray((img * 255).astype(np.uint8), 'L').save(os.path.join(OUT, 'concrete.webp'), quality=82, method=6)
print('assets/img/concrete.webp', os.path.getsize(os.path.join(OUT, 'concrete.webp')), 'bytes; range', round(img.min(), 3), round(img.max(), 3))
