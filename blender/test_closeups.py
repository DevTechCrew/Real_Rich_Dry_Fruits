# Test: each dry fruit alone, large, on a transparent background (the cut-out setup), stitched into a contact sheet.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rr

for kind in ('almond', 'cashew', 'pistachio', 'raisin'):
    rr.reset()
    rr.render_settings(720, 520, samples=128, transparent=True)
    o = rr.NUT_BUILDERS[kind](seed=7)
    rr.place(o, (0, 0, 0), (0.25, -0.15, 0.4))
    mn, mx = rr.bounds(o); c = (mn + mx) / 2; size = max(mx.x - mn.x, mx.y - mn.y) * 1.25
    rr.studio(target=tuple(c), dist=0.35)
    rr.camera((c.x, c.y - 30, c.z + 30), tuple(c), lens=85, ortho=size)
    rr.render(os.path.join(rr.OUT, 'tests', f'close_{kind}.png'))
