# Scene renders for the site, all in the shared studio (rr.py): the four range scenes (one camera angle for the set),
# the hero and the four origin bowls. Renders at 2x into blend-src/out/scenes; blender/export_web.py makes the site files.
#   blender -b --factory-startup -P blender/scenes.py -- range almonds [cashew ...] [--draft]
#   blender -b --factory-startup -P blender/scenes.py -- hero [--draft]
#   blender -b --factory-startup -P blender/scenes.py -- origins [almonds ...] [--draft]
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rr
from mathutils import Vector

NUT = {'almonds': 'almond', 'cashew': 'cashew', 'pistachio': 'pistachio', 'raisins': 'raisin'}
HEAP = {'almond': (9.0, 4.2), 'cashew': (9.0, 4.0), 'pistachio': (9.0, 4.4), 'raisin': (8.5, 3.8)}   # radius, core height
EXPOSURE = 0.7


def look(target, dist, elev=30, lens=70, fstop=4.5, focus_back=3.0, shift=(0, 0)):
    """The house camera: 30 degrees above the cloth, a 70 mm lens, focused a little in front of the target."""
    target = Vector(target); e = math.radians(elev)
    return rr.camera(target + Vector((0, -math.cos(e), math.sin(e))) * dist, tuple(target), lens=lens, fstop=fstop,
                     focus=dist - focus_back, shift=shift)


def setup(w, h, draft):
    rr.reset()
    return rr.render_settings(w // 2 if draft else w, h // 2 if draft else h, samples=48 if draft else 160, exposure=EXPOSURE)


def range_scene(slug, draft=False):
    """One product per scene: a heap on ivory linen, a few loose pieces in front. The right side stays calm because
    the site lays the pack over it."""
    kind = NUT[slug]
    setup(1920, 1280, draft)
    rr.collider(rr.cloth(seed=4, size=(150, 110), res=(330, 240)))
    src = rr.variants(kind, n=8, seed=2)
    radius, height = HEAP[kind]
    rr.heap(src, center=(-6, 3, 0), radius=radius, height=height, rounds=8, seed=3, tilt=8 if kind == 'cashew' else 16)
    rr.scatter(src, [(1.5, -8.5), (-13.5, -7), (6, -4.5), (-5, -10.5), (9, -8), (11, 1), (-16, 1)], seed=20)
    if kind == 'pistachio':                               # a pinch of empty shells
        husks = rr.variants('pistachio', n=3, seed=9, kernel=False, halves=(1,))
        rr.scatter(husks, [(1, -10), (-11, -9), (6.5, -5.5), (-14, -1)], seed=31)
    rr.settle(60)
    look((-4.1, 2.0, 2.8), dist=47, lens=70, fstop=7.1, focus_back=4.5)
    rr.studio(target=(-5, 3, 2), dist=2.0, key=1.25, fill=1.6, hdri_strength=0.3, key_from=(-30, 22, 40))   # food light: from behind, top left
    rr.render(os.path.join(rr.OUT, 'scenes', f'range_{slug}{"_draft" if draft else ""}.png'))


def hero(draft=False):
    """The almonds pouch on ivory linen with the four dry fruits around it, a walnut bowl and a gold spoon behind,
    shallow focus on the pack. The bottom-left stays quiet: the site's rotating badge sits there."""
    setup(2400, 1600, draft)
    rr.collider(rr.cloth(seed=7, size=(220, 250), res=(440, 500), wrinkles=90, offset=(0, 40)))
    pack = rr.pouch(os.path.join(rr.WORK, 'art', 'almonds.png'), seed=5)
    pack.location = (5, 8, 0); pack.rotation_euler = (0, 0, math.radians(14))
    rr.collider(pack, shape='CONVEX_HULL')
    b = rr.bowl(radius=6.5, height=4.0, loc=(-21, 24, 0)); rr.collider(b)
    sp = rr.spoon(loc=(-10, 16, 0.6), rot_z=math.radians(-24))
    for c_ in sp.children:
        rr.collider(c_)
    piles = [('almond', (-3, -2, 0), 6.6, 3.2, 9, 16), ('cashew', (-15.5, 6, 0), 6.2, 1.2, 5, 4),   # cashews read best lying flat
             ('pistachio', (16.5, 1, 0), 5.8, 3.2, 9, 16), ('raisin', (8, -9.5, 0), 4.8, 2.2, 9, 16)]
    for i, (kind, c, r, h, rounds, tilt) in enumerate(piles):
        rr.heap(rr.variants(kind, n=6, seed=40 + i), center=c, radius=r, height=h, rounds=rounds, seed=50 + i, tilt=tilt)
    rr.heap(rr.variants('raisin', n=4, seed=61), center=(-21, 24, 1.2), radius=5.0, height=2.0, rounds=4, seed=62)   # in the bowl
    rr.scatter(rr.variants('raisin', n=3, seed=63), [(-10.6, 16.2), (-9.4, 15.8), (-10, 16.9)], seed=64, z=1.0)        # in the spoon
    rr.scatter(rr.variants('almond', n=4, seed=70), [(5, -5), (12.5, -3), (-10, -7), (1, -12.5), (-13, -1.5), (21, -6)], seed=71)
    rr.settle(60)
    cam = look((1, 7, 9), dist=104, elev=27, lens=60, fstop=4.0, focus_back=2)
    rr.studio(target=(0, 5, 6), dist=2.8, key=1.25, fill=1.6, hdri_strength=0.3, key_from=(-30, 22, 40))
    tag = '_draft' if draft else ''
    rr.render(os.path.join(rr.OUT, 'scenes', f'hero{tag}.png'))
    # the share image: same set, wider and pushed right, so the logo can sit on the calm linen in the left third
    sc = rr.bpy.context.scene
    sc.render.resolution_x, sc.render.resolution_y = (1200, 630) if draft else (2400, 1260)
    cam.data.lens = 50; cam.data.shift_x = -0.2
    rr.render(os.path.join(rr.OUT, 'scenes', f'og{tag}.png'))


if __name__ == '__main__':
    args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    draft = '--draft' in args
    words = [a for a in args if not a.startswith('-')]
    what, names = (words[0], words[1:]) if words else ('range', [])
    if what == 'range':
        for slug in names or list(NUT):
            range_scene(slug, draft)
    elif what == 'hero':
        hero(draft)
