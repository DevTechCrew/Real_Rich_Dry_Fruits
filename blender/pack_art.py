# Rasterises the client's pack PDFs (front page only, untouched) into high-resolution textures for the 3D pouch.
# Run with the system Python (needs PyMuPDF):  python3 blender/pack_art.py
import os
import fitz

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # the folder that holds real-rich/
SRC = os.path.join(ROOT, 'Available Info')
OUT = os.path.join(ROOT, 'blend-src', 'art')
PACKS = {'almonds': 'Almonds.pdf', 'cashew': 'Casheww.pdf', 'pistachio': 'pistachio.pdf', 'raisins': 'Raisins.pdf'}

os.makedirs(OUT, exist_ok=True)
for slug, pdf in PACKS.items():
    page = fitz.open(os.path.join(SRC, pdf))[0]
    pix = page.get_pixmap(dpi=400, alpha=False)  # 16 x 23 cm front -> about 2520 x 3620 px
    path = os.path.join(OUT, f'{slug}.png')
    pix.save(path)
    print(slug, pix.width, 'x', pix.height, '->', path)
