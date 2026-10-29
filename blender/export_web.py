# Turns the raw Blender renders (blend-src/out, rendered at 2x) into the site's files in public/.
# Run with the system Python (needs Pillow):  python3 blender/export_web.py [packs] [fly] [scenes]
import json, os, sys
import numpy as np
from PIL import Image, ImageChops, ImageDraw

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(os.path.dirname(PROJECT), 'blend-src', 'out')
PUB = os.path.join(PROJECT, 'public', 'images')
SLUGS = ('almonds', 'cashew', 'pistachio', 'raisins')


def resize(im, size):
    """Resize RGBA through premultiplied alpha, so edges never pick up a dark fringe from transparent pixels."""
    return im.convert('RGBa').resize(size, Image.LANCZOS).convert('RGBA')


def save_webp(im, path, quality, budget_kb):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    q = quality
    while True:
        im.save(path, 'WEBP', quality=q, method=6, alpha_quality=90)
        kb = os.path.getsize(path) / 1024
        if kb <= budget_kb or q <= 60:
            break
        q -= 4
    print(f'{os.path.relpath(path, PROJECT):44s} {im.size[0]}x{im.size[1]}  q{q}  {kb:.0f} KB')


def fade_shadow(im):
    """The render's shadow catcher darkens the whole floor a little; keep the contact shadow under the pouch and fade
    the rest out well before the image edge, so no faint rectangle shows over the photo. Pouch pixels are untouched."""
    W, H = im.size
    px = im.load()
    rows = [y for y in range(H) if any(px[x, y][3] == 255 and max(px[x, y][:3]) > 40 for x in range(0, W, 3))]
    base = rows[-1]
    cols = [x for x in range(W) if px[x, base - 40][3] == 255]
    cx, half = (cols[0] + cols[-1]) / 2, (cols[-1] - cols[0]) / 2
    mask = Image.new('L', (W, H), 0); mp = mask.load()
    for y in range(base - 60, H):
        for x in range(W):
            r, g, b, a = px[x, y]
            if a == 0 or a == 255 or max(r, g, b) > 6:
                continue                                    # only the black, half-transparent shadow pixels
            dx = max(0.0, abs(x - cx) - half * 0.8) / (half * 0.42)
            dy = max(0.0, y - base) / ((H - base) * 0.9)
            f = max(0.0, 1 - (dx * dx + dy * dy)) ** 1.6
            mp[x, y] = int(min(255, a * 1.25) * f)
    alpha = im.getchannel('A')
    shadow_px = Image.eval(im.convert('L'), lambda v: 255 if v <= 6 else 0)
    keep = ImageChops.multiply(alpha, Image.eval(shadow_px, lambda v: 255 - v))   # pouch pixels as they are
    out = im.copy(); out.putalpha(ImageChops.lighter(keep, ImageChops.multiply(mask, shadow_px)))
    return out


def packs():
    for slug in SLUGS:
        im = Image.open(os.path.join(OUT, 'packs', f'{slug}.png')).convert('RGBA')
        save_webp(resize(fade_shadow(im), (480, 690)), os.path.join(PUB, 'packs', f'{slug}.webp'), 88, 70)


def fly():
    """Cut-outs: crop to the nut with a little air, 400 px wide (sharp at 3x for the largest 120 px slot)."""
    for name in sorted(f[:-4] for f in os.listdir(os.path.join(OUT, 'fly')) if f.endswith('.png')):
        im = Image.open(os.path.join(OUT, 'fly', f'{name}.png')).convert('RGBA')
        x0, y0, x1, y1 = im.getchannel('A').point(lambda a: 255 if a > 8 else 0).getbbox()
        pad = int(0.04 * max(x1 - x0, y1 - y0))
        im = im.crop((max(0, x0 - pad), max(0, y0 - pad), min(im.width, x1 + pad), min(im.height, y1 + pad)))
        save_webp(resize(im, (400, round(400 * im.height / im.width))), os.path.join(PUB, 'photos', 'fly', f'{name}.webp'), 86, 60)


def art():
    """The four front artworks for the real-time pouch (three.js), untouched, 1024 px tall."""
    for slug in SLUGS:
        im = Image.open(os.path.join(os.path.dirname(PROJECT), 'blend-src', 'art', f'{slug}.png')).convert('RGB')
        save_webp(im.resize((round(1024 * im.width / im.height), 1024), Image.LANCZOS), os.path.join(PROJECT, 'public', 'models', f'art-{slug}.webp'), 90, 110)


def stage():
    """Hero stage poster (blender/render_stage.py): keep the soft shadow under the floating pack, fade the rest of the
    shadow catcher's floor shading out, so the transparent image sits cleanly on the hero background."""
    src = os.path.join(OUT, 'stage', 'hero-stage.png')
    bx, by = json.load(open(src[:-4] + '.json'))['base']
    a = np.asarray(Image.open(src).convert('RGBA')).astype(np.float32)
    H, W = a.shape[:2]
    yy, xx = np.mgrid[0:H, 0:W]
    shadow = (a[..., 3] > 0) & (a[..., 3] < 255) & (a[..., :3].max(axis=2) <= 6)
    f = np.clip(1 - (((xx - bx) / (W * 0.26)) ** 2 + ((yy - by) / (H * 0.1)) ** 2), 0, 1) ** 1.5
    a[..., 3] = np.where(shadow, np.minimum(255, a[..., 3] * 1.2) * f, a[..., 3])
    save_webp(Image.fromarray(a.astype(np.uint8)), os.path.join(PUB, 'photos', 'hero-stage.webp'), 86, 150)


def _crop_object(im, pad=0.04, keep_shadow=0.35):
    """Fade the shadow catcher's floor shading out around the object (a soft margin of `keep_shadow` x its size),
    then crop to what is left with a little air."""
    a = np.asarray(im.convert('RGBA')).astype(np.float32)
    H, W = a.shape[:2]
    obj = (a[..., 3] > 200) & (a[..., :3].max(axis=2) > 12)
    ys, xs = np.nonzero(obj)
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    mx, my = (x1 - x0) * keep_shadow, (y1 - y0) * keep_shadow
    yy, xx = np.mgrid[0:H, 0:W]
    dx = np.maximum(0, np.maximum(x0 - xx, xx - x1)) / max(1, mx); dy = np.maximum(0, np.maximum(y0 - yy, yy - y1)) / max(1, my)
    f = np.clip(1 - np.sqrt(dx * dx + dy * dy), 0, 1) ** 1.5
    shadow = (a[..., 3] < 255) & (a[..., :3].max(axis=2) <= 12)
    a[..., 3] = np.where(shadow, a[..., 3] * f, a[..., 3])
    out = Image.fromarray(a.astype(np.uint8))
    bx = out.getchannel('A').point(lambda v: 255 if v > 6 else 0).getbbox()
    px, py = int((bx[2] - bx[0]) * pad), int((bx[3] - bx[1]) * pad)
    c = np.asarray(out.crop((max(0, bx[0] - px), max(0, bx[1] - py), min(W, bx[2] + px), min(H, bx[3] + py)))).astype(np.float32)
    h, w = c.shape[:2]; yy, xx = np.mgrid[0:h, 0:w]                     # and any shadow left reaches zero before the border
    edge = np.clip(np.minimum(np.minimum(xx, w - 1 - xx), np.minimum(yy, h - 1 - yy)) / (0.1 * min(w, h)), 0, 1) ** 1.5
    sh = (c[..., 3] < 255) & (c[..., :3].max(axis=2) <= 12)
    c[..., 3] = np.where(sh, c[..., 3] * edge, c[..., 3])
    return Image.fromarray(c.astype(np.uint8))


def sections():
    """The section renders (blender/render_sections.py) for public/images/studio/."""
    src = lambda n: Image.open(os.path.join(OUT, 'sections', f'{n}.png'))
    dst = lambda n: os.path.join(PUB, 'studio', n)
    sizes = {}
    for f in sorted(os.listdir(os.path.join(OUT, 'sections'))):
        if f.startswith('icon-') and f.endswith('.png') and '_draft' not in f:
            im = _crop_object(src(f[:-4]), pad=0.02, keep_shadow=0)
            save_webp(resize(im, (160, round(160 * im.height / im.width))), dst(f'icons/{f[5:-4]}.webp'), 88, 20)
    for name, width, budget in (('crate', 900, 120), ('lineup', 1400, 160), ('seal', 640, 70), ('pin', 480, 50), ('footer', 760, 50)):
        im = _crop_object(src(name))
        out = resize(im, (width, round(width * im.height / im.width))); sizes[name] = out.size
        save_webp(out, dst(f'{name}.webp'), 86, budget)
    flat = src('flatlay').convert('RGB')
    save_webp(flat.resize((1400, 700), Image.LANCZOS), dst('flatlay.webp'), 82, 150); sizes['flatlay'] = (1400, 700)
    # the levitating dry fruits: four slices, one nut each, so each can float on its own beat
    pr = _crop_object(src('promise'), pad=0.03, keep_shadow=0)
    pr = resize(pr, (1400, round(1400 * pr.height / pr.width)))
    al = np.asarray(pr.getchannel('A')) > 8; cols = al.any(axis=0)
    runs, inside = [], False
    for x, c in enumerate(cols):
        if c and not inside:
            start, inside = x, True
        elif not c and inside:
            runs.append((start, x)); inside = False
    if inside:
        runs.append((start, len(cols)))
    runs = sorted(sorted(runs, key=lambda r: r[1] - r[0], reverse=True)[:4])   # the four nuts
    cuts = [0] + [(runs[i][1] + runs[i + 1][0]) // 2 for i in range(3)] + [pr.width]
    for i in range(4):
        piece = pr.crop((cuts[i], 0, cuts[i + 1], pr.height))
        save_webp(piece, dst(f'promise-{i + 1}.webp'), 86, 40); sizes[f'promise-{i + 1}'] = piece.size
    for f in sorted(os.listdir(dst('icons'))):
        sizes[f'icon-{f[:-5]}'] = Image.open(dst(f'icons/{f}')).size
    json.dump(sizes, open(os.path.join(OUT, 'sections', 'sizes.json'), 'w'), indent=1)   # for the img width/height attributes
    print('SIZES', json.dumps(sizes))


def hero():
    im = Image.open(os.path.join(OUT, 'scenes', 'hero.png')).convert('RGB')
    save_webp(im.resize((1200, 800), Image.LANCZOS), os.path.join(PUB, 'photos', 'hero.webp'), 86, 180)


def og():
    """Share image: the wide frame of the hero set, the logo on the calm linen in the left third, the gold top rule."""
    im = Image.open(os.path.join(OUT, 'scenes', 'og.png')).convert('RGBA').resize((1200, 630), Image.LANCZOS)
    ImageDraw.Draw(im).rectangle([0, 0, 1199, 7], fill=(184, 149, 74, 255))
    logo = Image.open(os.path.join(PROJECT, 'public', 'logo.png')).convert('RGBA')
    lw = 360; lg = resize(logo, (lw, round(lw * logo.height / logo.width)))
    im.alpha_composite(lg, (215 - lw // 2, 318 - lg.height // 2))
    path = os.path.join(PROJECT, 'public', 'og-image.png')
    rgb = im.convert('RGB'); rgb.save(path, optimize=True)
    if os.path.getsize(path) > 400 * 1024:              # photographic PNGs run large: 256 colours, dithered, still clean
        rgb.quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.FLOYDSTEINBERG).save(path, optimize=True)
    print(f'{os.path.relpath(path, PROJECT):44s} 1200x630  {os.path.getsize(path) / 1024:.0f} KB')


if __name__ == '__main__':
    jobs = sys.argv[1:] or ['packs']
    for j in jobs:
        globals()[j]()
