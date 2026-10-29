# Pack mockups: each 250 g pouch wearing its untouched front artwork, turned slightly, on a transparent background with
# a soft contact shadow. Renders 960 x 1380 into blend-src/out/packs; blender/export_web.py makes the site files.
#   blender -b --factory-startup -P blender/render_packs.py -- [almonds cashew ...] [--draft]
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rr
from mathutils import Vector

args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
slugs = [a for a in args if not a.startswith('-')] or ['almonds', 'cashew', 'pistachio', 'raisins']
draft = '--draft' in args

for slug in slugs:
    rr.reset()
    rr.render_settings(960, 1380, samples=48 if draft else 192, transparent=True, exposure=0.7)
    o = rr.pouch(os.path.join(rr.WORK, 'art', f'{slug}.png'), seed=3)
    o.rotation_euler = (0, 0, math.radians(-10))
    rr.shadow_catcher()
    _, mx = rr.bounds(o)
    frame = mx.z / 0.82                                   # the pouch fills 82% of the height, room below for its shadow
    target = Vector((0, 0, mx.z + 0.05 * frame - frame / 2))
    lens, elev = 85, math.radians(7)
    dist = frame / 2 / (18 / lens)
    cam = rr.camera(target + Vector((0, -math.cos(elev), math.sin(elev))) * dist, tuple(target), lens=lens)
    cam.data.sensor_fit = 'VERTICAL'; cam.data.sensor_height = 36
    rr.studio(target=(0, 0, mx.z * 0.5), dist=2.2, key_shadow_only=True, hdri=None, hdri_strength=0.9)
    rr.render(os.path.join(rr.OUT, 'packs', f'{slug}.png'))
