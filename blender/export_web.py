# Turns the raw Blender renders (blend-src/out, rendered at 2x) into the site's files in public/.
# Run with the system Python (needs Pillow):  python3 blender/export_web.py [packs] [fly] [scenes]
import os, sys
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
