# Prepares the photographed skins for the nut materials (rr.py, mat_*_photo): evens out any light falloff so each image
# works as surface colour, softens what is too coarse at nut size, and makes every tile seamless.
# Reads blend-src/tex/*.png (macro photographs of almond, cashew, pistachio shell and kernel, golden raisin skin),
# writes blend-src/tex/final/. Run with the system Python (Pillow, NumPy):  python3 blender/skins.py
import os
import numpy as np
from PIL import Image, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, 'blend-src', 'tex'); OUT = os.path.join(SRC, 'final')
SKINS = {  # name: share of a softened copy blended in (the cashew photo is lumpier than a real kernel at nut size)
    'almond_skin': 0.0, 'cashew_surface': 0.6, 'pistachio_shell': 0.15, 'pistachio_kernel': 0.1, 'raisin_skin': 0.0}
TINT = {'raisin_skin': (0.93, 1.08, 1.25)}  # golden raisins (kishmish) are golden amber, not apricot orange


def blur(a, r):
    return np.asarray(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(r))).astype(np.float32)


def even(a, r=90):
    """Divide out slow light falloff, keeping the average colour: an albedo, not a lit photograph."""
    return np.clip(a / np.maximum(blur(a, r), 1) * a.reshape(-1, 3).mean(axis=0), 0, 255)


def seamless(a, band=0.14):
    """Cross-fade with a copy shifted by half a tile, so opposite edges meet without a seam."""
    h, w = a.shape[:2]
    shifted = np.roll(np.roll(a, w // 2, axis=1), h // 2, axis=0)
    t = lambda n: np.abs(np.arange(n) - (n - 1) / 2) / (n / 2)                 # 0 in the middle, 1 at the edges
    f = lambda v: np.clip((v - (1 - 2 * band)) / band, 0, 1)
    wgt = np.maximum(f(t(w))[None, :], f(t(h))[:, None])[..., None]
    wgt = wgt * wgt * (3 - 2 * wgt)
    return a * (1 - wgt) + shifted * wgt


os.makedirs(OUT, exist_ok=True)
for name, soften in SKINS.items():
    a = np.asarray(Image.open(os.path.join(SRC, f'{name}.png')).convert('RGB')).astype(np.float32)
    a = even(a) * np.array(TINT.get(name, (1, 1, 1)), dtype=np.float32)
    if soften:
        a = a * (1 - soften) + blur(a, 3) * soften
    a = seamless(a)
    Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(os.path.join(OUT, f'{name}.png'))
    print(name, 'mean colour', [int(v) for v in a.reshape(-1, 3).mean(axis=0)])
