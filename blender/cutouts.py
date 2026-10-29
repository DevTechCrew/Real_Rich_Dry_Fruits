# Photographed floating dry fruits. Codex photographs (blend-src/photo/gen-*/photo.png: four of one nut on a plain
# backdrop, and gen-dark: all four rim-lit on black) are cut out with Apple's Vision subject lifting (blender/lift.swift),
# the backdrop colour is taken out of the soft edges, and the site files are written:
#   photos/fly/{nut}, {nut}-2, {nut}-3   floating, parallax and marquee nuts, and the hero's ring (src/lib/stage3d.ts)
#   intro/{nut}                          the preloader's orbit
#   studio/promise-1..4                  the dark promise band (src/components/Levitas.tsx)
# plus full-size PNG masters in blend-src/photo/cut for the Blender hero poster (blender/render_stage.py).
#   python3 blender/cutouts.py
import glob, os, subprocess, sys, tempfile
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from export_web import PUB, resize, save_webp

HERE = os.path.dirname(os.path.abspath(__file__))
PHOTO = os.path.join(os.path.dirname(os.path.dirname(HERE)), 'blend-src', 'photo')
CUT = os.path.join(PHOTO, 'cut')
NUTS = ['almond', 'cashew', 'pistachio', 'raisin']
# which of the four photographed pieces (reading order) becomes each file: fly {nut}, -2, -3, then the intro's
PICK = {'almond': [0, 1, 3, 2], 'cashew': [0, 3, 1, 0], 'pistachio': [0, 1, 3, 2], 'raisin': [0, 1, 3, 2]}


def lift(path):
    """Soft masks of every subject in the photo, largest first."""
    exe = os.path.join(PHOTO, 'bin', 'lift'); src = os.path.join(HERE, 'lift.swift')
    if not os.path.exists(exe) or os.path.getmtime(exe) < os.path.getmtime(src):
        os.makedirs(os.path.dirname(exe), exist_ok=True); subprocess.run(['swiftc', '-O', src, '-o', exe], check=True)
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run([exe, path, tmp], check=True, capture_output=True)
        masks = []
        for f in glob.glob(os.path.join(tmp, 'mask-*.f32')):
            w, h = map(int, f[:-4].rsplit('-', 1)[1].split('x'))
            masks.append(np.fromfile(f, np.float32).reshape(h, w))
    return sorted(masks, key=lambda m: -m.sum())


def bbox(a, t=0.02):
    ys, xs = np.nonzero(a > t)
    return xs.min(), ys.min(), xs.max() + 1, ys.max() + 1


def _box(x, r):
    """Box blur of radius r over both image axes (edges repeated), with cumulative sums."""
    for ax in (0, 1):
        x = np.moveaxis(x, ax, 0); n = x.shape[0]
        c = np.cumsum(np.concatenate([np.repeat(x[:1], r + 1, 0), x, np.repeat(x[-1:], r, 0)]), 0)
        x = np.moveaxis((c[2 * r + 1:2 * r + 1 + n] - c[:n]) / (2 * r + 1), 0, ax)
    return x


def bleed(im):
    """Spread the edge colours out under the transparent pixels, so resizing and WebGL mipmaps never pull in black."""
    x = np.asarray(im, np.float32) / 255; f, a = x[..., :3], x[..., 3]
    num, den = np.zeros_like(f), np.zeros_like(a)
    for r in (2, 6, 18):
        num += _box(f * a[..., None], r) / r; den += _box(a, r) / r
    f = np.where((a > 0)[..., None], f, num / np.maximum(den, 1e-6)[..., None])
    return Image.fromarray((np.dstack([f, a]) * 255 + 0.5).astype(np.uint8))


def cut(photo, masks, pad=0.05):
    """Each subject as straight-alpha RGBA, cropped with a margin; the backdrop is unmixed from its soft edge."""
    img = np.asarray(Image.open(photo).convert('RGB'), np.float32) / 255
    union = np.max(masks, axis=0)
    out = []
    for m in masks:
        x0, y0, x1, y1 = bbox(m)
        p = int(max(x1 - x0, y1 - y0) * pad)
        x0, y0, x1, y1 = max(0, x0 - p), max(0, y0 - p), min(img.shape[1], x1 + p), min(img.shape[0], y1 + p)
        c, u = img[y0:y1, x0:x1], union[y0:y1, x0:x1]
        bg = np.median(c[u < 0.01], axis=0)                       # the backdrop right round this piece
        a = np.clip((m[y0:y1, x0:x1] - 0.06) / 0.88, 0, 1)        # drop the faint halo, make the core solid
        f = np.clip((c - (1 - a)[..., None] * bg) / np.maximum(a, 1e-3)[..., None], 0, 1)
        rgba = np.dstack([f, a]); rgba[a <= 0] = 0
        out.append(((x0 + x1) / 2, (y0 + y1) / 2, Image.fromarray((rgba * 255 + 0.5).astype(np.uint8))))
    return out


def fit(im, w):
    return bleed(im if im.width <= w else resize(im, (w, round(im.height * w / im.width))))


def main():
    os.makedirs(CUT, exist_ok=True)
    for nut in NUTS:
        pieces = cut(os.path.join(PHOTO, f'gen-{nut}', 'photo.png'), lift(os.path.join(PHOTO, f'gen-{nut}', 'photo.png'))[:4])
        pieces.sort(key=lambda p: (p[1] > 512, p[0]))               # reading order: top row, then bottom row
        for i, j in enumerate(PICK[nut]):
            im = pieces[j][2]
            if i < 3:
                name = nut if i == 0 else f'{nut}-{i + 1}'
                bleed(im).save(os.path.join(CUT, f'{name}.png'))
                save_webp(fit(im, 480), os.path.join(PUB, 'photos', 'fly', f'{name}.webp'), 88, 60, exact=True)
            else:
                save_webp(fit(im, 300), os.path.join(PUB, 'intro', f'{nut}.webp'), 88, 30)

    # the promise band: one strip across the four rim-lit pieces, split in the gaps so they all share one height
    photo = os.path.join(PHOTO, 'gen-dark', 'photo.png')
    masks = sorted(lift(photo)[:4], key=lambda m: bbox(m)[0])
    img = np.asarray(Image.open(photo).convert('RGB'), np.float32) / 255
    union = np.max(masks, axis=0); boxes = [bbox(m) for m in masks]
    a = np.clip((union - 0.06) / 0.88, 0, 1)
    bg = np.median(img[union < 0.01], axis=0)
    f = np.clip((img - (1 - a)[..., None] * bg) / np.maximum(a, 1e-3)[..., None], 0, 1)
    rgba = np.dstack([f, a]); rgba[a <= 0] = 0
    strip = Image.fromarray((rgba * 255 + 0.5).astype(np.uint8))
    p = int(max(b[3] - b[1] for b in boxes) * 0.06)
    top, bottom = min(b[1] for b in boxes) - p, max(b[3] for b in boxes) + p
    cuts = [boxes[0][0] - p] + [(boxes[i][2] + boxes[i + 1][0]) // 2 for i in range(3)] + [boxes[3][2] + p]
    sizes = []
    for i in range(4):
        piece = strip.crop((cuts[i], top, cuts[i + 1], bottom))
        save_webp(piece, os.path.join(PUB, 'studio', f'promise-{i + 1}.webp'), 86, 40); sizes.append(list(piece.size))
    print('promise sizes (src/components/Levitas.tsx):', sizes)


if __name__ == '__main__':
    main()
