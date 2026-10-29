# Generates src/components/introArt.ts (vector parts of the logo for the preloader) from the logo PDF,
# and small WebP nut cut-outs for the orbit.
# Usage (needs PyMuPDF and Pillow): python3 scripts/gen_intro_art.py "../Available Info/REAL RICH LOGO.pdf" .
import sys, os, re, json
import fitz
from PIL import Image

PDF, ROOT = sys.argv[1], sys.argv[2]
page = fitz.open(PDF)[0]
svg = page.get_svg_image(text_as_path=True)

def path_d(d):
    out, cur = [], None
    def mv(p):
        if cur is None or abs(cur.x - p.x) > 1e-3 or abs(cur.y - p.y) > 1e-3: out.append(f'M{p.x:.2f} {p.y:.2f}')
    for it in d['items']:
        op = it[0]
        if op == 'l':
            mv(it[1]); out.append(f'L{it[2].x:.2f} {it[2].y:.2f}'); cur = it[2]
        elif op == 'c':
            mv(it[1]); c1, c2, p2 = it[2], it[3], it[4]
            out.append(f'C{c1.x:.2f} {c1.y:.2f} {c2.x:.2f} {c2.y:.2f} {p2.x:.2f} {p2.y:.2f}'); cur = p2
        elif op == 're':
            r = it[1]; out.append(f'M{r.x0:.2f} {r.y0:.2f}H{r.x1:.2f}V{r.y1:.2f}H{r.x0:.2f}Z'); cur = None
        elif op == 'qu':
            q = it[1]; out.append(f'M{q.ul.x:.2f} {q.ul.y:.2f}L{q.ur.x:.2f} {q.ur.y:.2f}L{q.lr.x:.2f} {q.lr.y:.2f}L{q.ll.x:.2f} {q.ll.y:.2f}Z'); cur = None
    return ''.join(out)

draws = page.get_drawings()
def fill_hex(d):
    f = d.get('fill'); return '#%02x%02x%02x' % tuple(round(c * 255) for c in f) if f else None
mark = [path_d(d) for d in draws if fill_hex(d) == '#e09e27']
tm = [path_d(d) for d in draws if fill_hex(d) == '#073320']
rules = [path_d(d) for d in draws if fill_hex(d) == '#231f20']
assert (len(mark), len(tm), len(rules)) == (5, 3, 2), (len(mark), len(tm), len(rules))

glyphs = dict(re.findall(r'<path id="(font_[0-9_]+)"[^>]*d="([^"]*)"', svg))
uses = re.findall(r'<use data-text="([^"]*)" xlink:href="#(font_[0-9_]+)" transform="matrix\(([^)]*)\)" fill="(#[0-9a-f]+)"/>', svg)
def tidy(m): return 'matrix(' + ','.join(f'{float(v):.4g}' for v in m.split(',')) + ')'
name = [(g, tidy(m)) for ch, g, m, f in uses if f == '#0e2319' and ch.strip()]
tag = [(g, tidy(m)) for ch, g, m, f in uses if f == '#073320' and ch.strip()]
assert len(name) == 8 and len(tag) > 15, (len(name), len(tag))
used = {g for g, _ in name + tag}
glyphs = {k: v for k, v in glyphs.items() if k in used}

# viewBoxes match the exported PNGs (1 pt padding around the ink), so the docking lines up with the header images
MARK_VB = '83.1 44.9 117.1 102.9'
NAME_VB = '20.8 152 249.7 33.7'
TAG_VB = '20.8 199.6 249.7 12.7'

ts = ['// Generated from "Available Info/REAL RICH LOGO.pdf" by scripts/gen_intro_art.py for the preloader. Do not edit by hand.',
      f'export const MARK_VB = {json.dumps(MARK_VB)};',
      f'export const MARK: string[] = {json.dumps(mark)};',
      f'export const NAME_VB = {json.dumps(NAME_VB)};',
      f'export const TAG_VB = {json.dumps(TAG_VB)};',
      f'export const GLYPHS: Record<string, string> = {json.dumps(glyphs)};',
      f'export const NAME: [string, string][] = {json.dumps(name)};',
      f'export const TM: string[] = {json.dumps(tm)};',
      f'export const TAG: [string, string][] = {json.dumps(tag)};',
      f'export const RULES: string[] = {json.dumps(rules)};', '']
out = os.path.join(ROOT, 'src', 'components', 'introArt.ts')
open(out, 'w').write('\n'.join(ts))
print('introArt.ts', os.path.getsize(out), 'bytes;', len(glyphs), 'glyphs;', len(name), 'name letters;', len(tag), 'tagline letters')

# small nut cut-outs for the orbit, from the Blender cut-outs (blender/render_fly.py)
os.makedirs(os.path.join(ROOT, 'public', 'images', 'intro'), exist_ok=True)
for n in ('almond', 'cashew', 'pistachio', 'raisin'):
    im = Image.open(os.path.join(ROOT, 'public', 'images', 'photos', 'fly', f'{n}.webp')).convert('RGBa')
    im = im.resize((150, round(150 * im.height / im.width)), Image.LANCZOS).convert('RGBA')
    dst = os.path.join(ROOT, 'public', 'images', 'intro', f'{n}.webp')
    im.save(dst, 'WEBP', quality=80, method=6)
    print(dst.split('public/')[1], im.size, os.path.getsize(dst) // 1024, 'KB')
