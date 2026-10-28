# Exports the site's logo files from the client's logo PDF.
# Usage (needs PyMuPDF, NumPy and Pillow): python3 scripts/export_logo.py "../Available Info/REAL RICH LOGO.pdf" public <preview dir>
import sys, os, re, json
import fitz
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

PDF, PUB, PREV = sys.argv[1], sys.argv[2], sys.argv[3]
GOLD, IVORY, ESPRESSO = '#e09e27', '#f7f2e8', (43, 30, 22)
page = fitz.open(PDF)[0]
W = page.rect.width
report = {}

# ---- find the parts: row clusters of ink (mark / wordmark / tagline)
Z = 12
pix = page.get_pixmap(matrix=fitz.Matrix(Z, Z), alpha=True)
alpha = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)[:, :, 3]
ink = alpha > 8
rows = np.where(ink.any(axis=1))[0]
clusters, start, prev = [], rows[0], rows[0]
for r in rows[1:]:
    if r - prev > Z * 0.8:
        clusters.append((start, prev)); start = r
    prev = r
clusters.append((start, prev))
def box(r0, r1):
    cols = np.where(ink[r0:r1 + 1].any(axis=0))[0]
    return fitz.Rect(cols[0] / Z, r0 / Z, (cols[-1] + 1) / Z, (r1 + 1) / Z)
parts = [box(a, b) for a, b in clusters]
report['clusters_pt'] = [[round(v, 1) for v in p] for p in parts]
assert len(parts) == 3, f'expected mark, wordmark and tagline, found {len(parts)} bands'
mark_r, word_r, tag_r = parts
full_r = fitz.Rect(min(p.x0 for p in parts), mark_r.y0, max(p.x1 for p in parts), tag_r.y1)
pad = lambda r, d: fitz.Rect(r.x0 - d, r.y0 - d, r.x1 + d, r.y1 + d)
full_c, mark_c, word_c = pad(full_r, 2), pad(mark_r, 1), pad(word_r, 1)

def render_pdf(clip, width_px=None, height_px=None):
    z = width_px / clip.width if width_px else height_px / clip.height
    p = page.get_pixmap(matrix=fitz.Matrix(z, z), clip=clip, alpha=True)
    return Image.frombytes('RGBA', (p.width, p.height), p.samples) if p.n == 4 else None

def unpremultiply(im):
    a = np.asarray(im).astype(np.float32)
    al = a[:, :, 3:4] / 255.0
    rgb = np.where(al > 0, np.clip(a[:, :, :3] / np.maximum(al, 1e-6), 0, 255), 0)
    return Image.fromarray(np.concatenate([rgb, a[:, :, 3:4]], axis=2).astype(np.uint8), 'RGBA')

# MuPDF pixmaps are premultiplied; check once and fix if so
probe = render_pdf(mark_c, height_px=200)
px = np.asarray(probe)
semi = px[(px[:, :, 3] > 40) & (px[:, :, 3] < 200)]
premult = bool(len(semi)) and float(np.median(semi[:, 0].astype(int) * 255 / semi[:, 3])) > 235
report['premultiplied'] = premult
fix = unpremultiply if premult else (lambda im: im)

# ---- SVG versions (vector, from the PDF), cropped by viewBox
svg_full = page.get_svg_image(text_as_path=True)
def crop_svg(svg, r):
    svg = re.sub(r'width="[^"]+" height="[^"]+" viewBox="[^"]+"',
                 f'width="{r.width:.2f}" height="{r.height:.2f}" viewBox="{r.x0:.2f} {r.y0:.2f} {r.width:.2f} {r.height:.2f}"', svg, count=1)
    return svg
svg_light = svg_full
for dark in ('#073320', '#0e2319', '#231f20'):
    svg_light = svg_light.replace(f'fill="{dark}"', f'fill="{IVORY}"')
assert svg_light.count(f'fill="{GOLD}"') == svg_full.count(f'fill="{GOLD}"')

# Mark-only SVG built straight from the PDF's gold shapes (no hidden text inside)
def path_d(d):
    out, cur = [], None
    for it in d['items']:
        op = it[0]
        if op == 'l':
            p1, p2 = it[1], it[2]
            if cur is None or abs(cur.x - p1.x) > 1e-3 or abs(cur.y - p1.y) > 1e-3: out.append(f'M{p1.x:.3f} {p1.y:.3f}')
            out.append(f'L{p2.x:.3f} {p2.y:.3f}'); cur = p2
        elif op == 'c':
            p1, c1, c2, p2 = it[1], it[2], it[3], it[4]
            if cur is None or abs(cur.x - p1.x) > 1e-3 or abs(cur.y - p1.y) > 1e-3: out.append(f'M{p1.x:.3f} {p1.y:.3f}')
            out.append(f'C{c1.x:.3f} {c1.y:.3f} {c2.x:.3f} {c2.y:.3f} {p2.x:.3f} {p2.y:.3f}'); cur = p2
        elif op == 're':
            r = it[1]; out.append(f'M{r.x0:.3f} {r.y0:.3f}H{r.x1:.3f}V{r.y1:.3f}H{r.x0:.3f}Z'); cur = None
        elif op == 'qu':
            q = it[1]; out.append(f'M{q.ul.x:.3f} {q.ul.y:.3f}L{q.ur.x:.3f} {q.ur.y:.3f}L{q.lr.x:.3f} {q.lr.y:.3f}L{q.ll.x:.3f} {q.ll.y:.3f}Z'); cur = None
    return ''.join(out)
gold_paths = [d for d in page.get_drawings() if d.get('fill') and abs(d['fill'][0] - 0.878) < 0.01]
assert len(gold_paths) == 5, len(gold_paths)
EO = ' fill-rule="evenodd"'
paths = ''.join('<path fill="%s"%s d="%s"/>' % (GOLD, EO if d.get('even_odd') else '', path_d(d)) for d in gold_paths)
svg_mark = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{mark_c.width:.2f}" height="{mark_c.height:.2f}" '
            f'viewBox="{mark_c.x0:.2f} {mark_c.y0:.2f} {mark_c.width:.2f} {mark_c.height:.2f}">{paths}</svg>\n')

# check the hand-built mark against the PDF render
def render_svg(svg, clip_pt, height_px):
    d = fitz.open(stream=svg.encode(), filetype='svg'); pg = d[0]
    s = pg.rect.width / float(re.search(r'width="([^"]+)"', svg).group(1))
    vb = [float(v) for v in re.search(r'viewBox="([^"]+)"', svg).group(1).split()]
    clip = fitz.Rect((clip_pt.x0 - vb[0]) * s, (clip_pt.y0 - vb[1]) * s, (clip_pt.x1 - vb[0]) * s, (clip_pt.y1 - vb[1]) * s)
    z = height_px / clip.height
    p = pg.get_pixmap(matrix=fitz.Matrix(z, z), clip=clip, alpha=True)
    return Image.frombytes('RGBA', (p.width, p.height), p.samples)
a1 = np.asarray(render_pdf(mark_c, height_px=300))[:, :, 3].astype(int)
a2 = np.asarray(render_svg(svg_mark, mark_c, 300))[:, :, 3].astype(int)
h, w = min(a1.shape[0], a2.shape[0]), min(a1.shape[1], a2.shape[1])
report['mark_svg_vs_pdf_mean_alpha_diff'] = round(float(np.abs(a1[:h, :w] - a2[:h, :w]).mean()), 3)

# ---- write files
def save_png(im, name):
    im.save(os.path.join(PUB, name), optimize=True); report[name] = list(im.size)
open(os.path.join(PUB, 'logo.svg'), 'w').write(crop_svg(svg_full, full_c))
open(os.path.join(PUB, 'logo-light.svg'), 'w').write(crop_svg(svg_light, full_c))
open(os.path.join(PUB, 'logo-mark.svg'), 'w').write(svg_mark)
full_png = fix(render_pdf(full_c, width_px=1200)); save_png(full_png, 'logo.png')
light_png = fix(render_svg(crop_svg(svg_light, full_c), full_c, round(600 * full_c.height / full_c.width))); save_png(light_png, 'logo-light.png')
mark_png = fix(render_pdf(mark_c, height_px=240)); save_png(mark_png, 'logo-mark.png')
word_png = fix(render_pdf(word_c, width_px=600))
word_png = word_png.resize((600, round(600 * word_c.height / word_c.width)), Image.LANCZOS)  # exact aspect, so the preloader docks onto it cleanly
save_png(word_png, 'logo-wordmark.png')

# ---- icons: gold mark on an espresso tile
big_mark = fix(render_pdf(mark_c, height_px=1024))
def tile(size, rounded, mark_share=0.62):
    S = size * 4
    im = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle([0, 0, S - 1, S - 1], radius=int(S * 0.22) if rounded else 0, fill=ESPRESSO + (255,))
    mh = int(S * mark_share); mw = round(mh * big_mark.width / big_mark.height)
    if mw > S * 0.78: mw = int(S * 0.78); mh = round(mw * big_mark.height / big_mark.width)
    m = big_mark.resize((mw, mh), Image.LANCZOS)
    im.alpha_composite(m, ((S - mw) // 2, (S - mh) // 2))
    return im.resize((size, size), Image.LANCZOS)
save_png(tile(512, True), 'icon-512.png'); save_png(tile(192, True), 'icon-192.png')
save_png(tile(180, False).convert('RGB'), 'apple-touch-icon.png')
for s in (16, 32, 48): save_png(tile(s, True, 0.7), f'favicon-{s}.png')
tile(256, True, 0.7).save(os.path.join(PUB, 'favicon.ico'), sizes=[(16, 16), (32, 32), (48, 48)])

# ---- social share image (1200x630): new logo + hero photo, same layout as before
og = Image.new('RGBA', (1200, 630), (247, 242, 232, 255))
ImageDraw.Draw(og).rectangle([0, 0, 1199, 7], fill=(184, 149, 74, 255))
lw = 430; lg = full_png.resize((lw, round(lw * full_png.height / full_png.width)), Image.LANCZOS)
og.alpha_composite(lg, (310 - lw // 2, 315 - lg.height // 2))
hero = Image.open(os.path.join(PUB, 'images', 'photos', 'hero.webp')).convert('RGBA')
hw, hh = 520, round(520 * hero.height / hero.width); hero = hero.resize((hw, hh), Image.LANCZOS)
x, y = 620, (630 - hh) // 2
sh = Image.new('RGBA', og.size, (0, 0, 0, 0))
ImageDraw.Draw(sh).rectangle([x + 6, y + 14, x + hw + 6, y + hh + 14], fill=(43, 30, 22, 70))
og.alpha_composite(sh.filter(ImageFilter.GaussianBlur(18)))
og.alpha_composite(hero, (x, y))
og.convert('RGB').save(os.path.join(PUB, 'og-image.png'), optimize=True); report['og-image.png'] = [1200, 630]

# ---- previews for review
sheet = Image.new('RGBA', (1240, 470), (247, 242, 232, 255))
d = ImageDraw.Draw(sheet); d.rectangle([620, 0, 1239, 469], fill=ESPRESSO + (255,))
f1 = full_png.resize((420, round(420 * full_png.height / full_png.width))); sheet.alpha_composite(f1, (100, 30))
f2 = light_png.resize((420, round(420 * light_png.height / light_png.width))); sheet.alpha_composite(f2, (720, 30))
hdr = Image.new('RGBA', (560, 80), (247, 242, 232, 255))
m2 = mark_png.resize((round(44 * mark_png.width / mark_png.height) * 1, 44)); hdr.alpha_composite(m2, (10, 18))
w2 = word_png.resize((round(17 * word_png.width / word_png.height), 17)); hdr.alpha_composite(w2, (10 + m2.width + 12, 32))
sheet.alpha_composite(hdr.resize((hdr.width, hdr.height)), (40, 380))
for i, s in enumerate((512, 192, 48, 32, 16)):
    t = Image.open(os.path.join(PUB, 'icon-512.png' if s == 512 else 'icon-192.png' if s == 192 else f'favicon-{s}.png')).convert('RGBA')
    t = t.resize((min(s, 96), min(s, 96))) if s > 96 else t
    sheet.alpha_composite(t, (700 + i * 105, 360))
sheet.convert('RGB').save(os.path.join(PREV, 'logo-sheet.jpg'), quality=90)
og.convert('RGB').save(os.path.join(PREV, 'og-preview.jpg'), quality=85)
print(json.dumps(report, indent=1))
