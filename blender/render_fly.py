# Floating nut cut-outs: each dry fruit alone, three poses each, transparent background, lit from the top left, no
# ground or shadow (the site adds a soft drop shadow). Renders 1000 x 1000 into blend-src/out/fly; export_web.py crops.
#   blender -b --factory-startup -P blender/render_fly.py -- [almond cashew ...] [--draft]
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rr

# (seed, rotation) per pose; the file names are {kind}.png, {kind}-2.png, {kind}-3.png
POSES = {   # keep the long axis across the view (|ry| small, rz near 0 or pi) so each nut shows its real outline
    'almond':    [(7, (0.25, -0.15, 0.4)), (11, (-0.6, 0.12, 2.75)), (3, (1.2, -0.1, -0.45))],
    'cashew':    [(7, (0.25, -0.15, 0.4)), (5, (-0.4, 0.4, 2.7)), (9, (0.95, 0.15, -0.55))],
    'pistachio': [(7, (0.25, -0.15, 0.4)), (4, (0.45, -0.1, 2.9)), (12, (0.6, 0.1, -0.3))],
    'raisin':    [(7, (0.25, -0.15, 0.4)), (2, (-0.5, 0.1, 2.9)), (8, (1.0, -0.1, -0.35))],
}
EXPOSURE = 0.7

args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
kinds = [a for a in args if not a.startswith('-')] or list(POSES)
draft = '--draft' in args

for kind in kinds:
    for i, (seed, rot) in enumerate(POSES[kind][:1] if draft else POSES[kind]):
        rr.reset()
        rr.render_settings(1000, 1000, samples=48 if draft else 160, transparent=True, exposure=EXPOSURE)
        o = rr.NUT_BUILDERS[kind](seed=seed)
        rr.place(o, (0, 0, 0), rot)
        mn, mx = rr.bounds(o); c = (mn + mx) / 2
        size = max(mx.x - mn.x, mx.y - mn.y, mx.z - mn.z) * 1.2
        rr.studio(target=tuple(c), dist=0.35)
        rr.camera((c.x, c.y - 30, c.z + 30), tuple(c), lens=85, ortho=size)
        rr.render(os.path.join(rr.OUT, 'fly', f'{kind}{"" if i == 0 else f"-{i + 1}"}.png'))
