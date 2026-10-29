# Studio renders for the sections that had no pictures, in the shared studio (rr.py):
#   icons    enamel-and-gold medallions for the icon cards (Why Real Rich, About values, Quality steps)
#   crate    a wooden crate of pouches (bulk orders)
#   lineup   the four packs in a gentle arc with their dry fruits (final call to action)
#   flatlay  the packs and dry fruits from above on linen (Instagram)
#   seal     the RR monogram in gold on a walnut plinth (About)
#   pin      a gold map pin over a few dry fruits (Contact)
#   footer   dry fruits resting on the footer's top edge
# Renders into blend-src/out/sections; blender/export_web.py (sections) writes public/images/studio/.
#   blender -b --factory-startup -P blender/render_sections.py -- [icons crate ...] [--draft]
import os, sys, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rr
import bpy
from mathutils import Vector, Matrix

args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
draft = '--draft' in args
OUTD = os.path.join(rr.OUT, 'sections')
SVG = os.path.join(rr.WORK, 'svg'); os.makedirs(SVG, exist_ok=True)
ART = lambda slug: os.path.join(rr.WORK, 'art', f'{slug}.png')
SLUGS = ('almonds', 'cashew', 'pistachio', 'raisins')
KIND = {'almonds': 'almond', 'cashew': 'cashew', 'pistachio': 'pistachio', 'raisins': 'raisin'}
EXPOSURE = 0.7

# line icons on a 24 grid (the first four are the site's own "Why Real Rich" icons)
ICONS = {
    'hand-picked': '<path d="M12 3c4 3 6 7 6 11a6 6 0 0 1-12 0c0-4 2-8 6-11Z"/><path d="m9 14 2 2 4-4"/>',
    'origin': '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c-3.5 4-3.5 14 0 18M12 3c3.5 4 3.5 14 0 18"/>',
    'premium': '<circle cx="12" cy="9" r="5.5"/><path d="m8.5 13.5-1.5 7.5 5-3 5 3-1.5-7.5"/>',
    'fresh': '<path d="M7 4h10l2 3v12a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V7l2-3Z"/><path d="M5 7h14M9 12.5c1.5-1.5 4.5-1.5 6 0"/>',
    'star': '<path d="M12 3.5l2.6 5.4 5.9.8-4.3 4.1 1 5.8L12 16.8l-5.2 2.8 1-5.8-4.3-4.1 5.9-.8Z"/>',
    'leaf': '<path d="M5 19C5 10.5 10.5 5 19 5c0 8.5-5.5 14-14 14Z"/><path d="M5 19 14.5 9.5"/>',
    'shield': '<path d="M12 3l7 3v5.5c0 4.6-3 8-7 9.5-4-1.5-7-4.9-7-9.5V6Z"/><path d="m9 12 2 2 4-4"/>',
    'pin': '<path d="M12 21s-6.5-6-6.5-11a6.5 6.5 0 0 1 13 0c0 5-6.5 11-6.5 11Z"/><circle cx="12" cy="10" r="2.4"/>',
    'inspect': '<circle cx="10.5" cy="10.5" r="6"/><path d="m15 15 5.5 5.5"/><path d="M8 12c.8-2.6 2.8-3.8 4.6-3.3.5 1.8-.7 3.8-3.3 4.6Z"/>',
    'graded': '<circle cx="5" cy="16" r="2"/><circle cx="11" cy="15" r="3"/><circle cx="18.2" cy="13.5" r="4.3"/><path d="M2 20h20"/>',
    'packed': '<path d="M7 4h10l2 3v12a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V7l2-3Z"/><path d="M5 7h14"/><path d="m9.5 13.5 2 2 3.5-3.5"/>',
}


def setup(w, h, samples=160, transparent=True):
    rr.reset()
    return rr.render_settings(w // 2 if draft else w, h // 2 if draft else h, samples=48 if draft else samples,
                              transparent=transparent, exposure=EXPOSURE)


def save(name):
    rr.render(os.path.join(OUTD, f'{name}{"_draft" if draft else ""}.png'))


def gold(rough=0.2, hexcol='#E6BC68'):
    m = rr.M(f'gold_{rough}'); m.set(Base_Color=rr.rgb(hexcol), Metallic=1.0, Roughness=rough, Specular_IOR_Level=0.5)
    return m.mat


def enamel(hexcol='#1E140E'):
    m = rr.M('enamel'); m.set(Base_Color=rr.rgb(hexcol), Roughness=0.35, Coat_Weight=0.5, Coat_Roughness=0.08, Specular_IOR_Level=0.4)
    return m.mat


def mat_pine():
    m = rr.M('pine'); v = m.coords(scale=(1, 1, 0.12))
    grain = m.noise(v, 6, detail=6, rough=0.6, distortion=0.6)
    col = m.ramp(grain, [(0.3, '#B98D5C'), (0.55, '#CFA673'), (0.8, '#DDB988')])
    m.link(col, m.bsdf.inputs['Base Color']); m.link(m.bump(grain, strength=0.15, distance=0.02), m.bsdf.inputs['Normal'])
    m.set(Roughness=0.62, Specular_IOR_Level=0.35)
    return m.mat


def svg_objects(inner, name, view='0 0 24 24'):
    path = os.path.join(SVG, f'{name}.svg')
    open(path, 'w').write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{view}"><g fill="none" stroke="#000" stroke-width="1">{inner}</g></svg>')
    return svg_file(path)


def svg_file(path):
    before = set(bpy.data.objects)
    bpy.ops.import_curve.svg(filepath=path)
    return [o for o in bpy.data.objects if o not in before and o.type == 'CURVE']


def fit(objs, size, center=(0, 0, 0)):
    """Scale and move curves so their combined outline spans `size` (largest side), centred on `center`. Returns the scale."""
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
    mn = Vector((min(p.x for p in pts), min(p.y for p in pts), 0)); mx = Vector((max(p.x for p in pts), max(p.y for p in pts), 0))
    s = size / max(mx.x - mn.x, mx.y - mn.y); c = (mn + mx) / 2
    for o in objs:
        o.matrix_world = Matrix.Translation(Vector(center)) @ Matrix.Scale(s, 4) @ Matrix.Translation(-c) @ o.matrix_world
    bpy.context.view_layer.update()
    return objs[0].matrix_world.to_scale().x


def smooth(o):
    for p in o.data.polygons:
        p.use_smooth = True
    return o


# ---------------------------------------------------------------- icon medallions
def icons():
    for name, inner in ICONS.items():
        setup(360, 360, samples=128)
        bpy.ops.mesh.primitive_cylinder_add(vertices=160, radius=2.12, depth=0.42, location=(0, 0, 0))
        disc = smooth(bpy.context.object); disc.data.materials.append(enamel())
        bev = disc.modifiers.new('round', 'BEVEL'); bev.width = 0.05; bev.segments = 3; bev.limit_method = 'ANGLE'
        bpy.ops.mesh.primitive_torus_add(major_radius=2.24, minor_radius=0.17, major_segments=160, minor_segments=24, location=(0, 0, 0.06))
        rim = smooth(bpy.context.object); rim.data.materials.append(gold(0.28))
        objs = svg_objects(inner, name)
        s = fit(objs, 2.75, center=(0, 0, 0.23))
        g = gold(0.16)
        for o in objs:
            cu = o.data; cu.dimensions = '3D'; cu.bevel_mode = 'ROUND'; cu.bevel_depth = 0.085 / s; cu.bevel_resolution = 5
            cu.use_fill_caps = True; cu.materials.clear(); cu.materials.append(g)
        tilt = math.radians(24)
        rr.camera((0, -math.sin(tilt) * 40, math.cos(tilt) * 40), (0, 0, 0), ortho=5.3)
        rr.studio(target=(0, 0, 0), dist=0.45, hdri_strength=0.45)
        save(f'icon-{name}')


# ---------------------------------------------------------------- crate of pouches (bulk)
def plank(name, size, loc, mat, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.object; o.name = name; o.scale = size; o.data.materials.append(mat)
    b = o.modifiers.new('round', 'BEVEL'); b.width = 0.12; b.segments = 2
    return o


def crate():
    setup(1600, 1200)
    pine = mat_pine(); W, D, H = 50.0, 28.0, 15.0; t = 1.4
    for z in (2.4, 7.4, 12.4):                            # three boards per side with small gaps
        plank('front', (W, t, 4.6), (0, -D / 2, z), pine); plank('back', (W, t, 4.6), (0, D / 2, z), pine)
        plank('left', (t, D, 4.6), (-W / 2, 0, z), pine); plank('right', (t, D, 4.6), (W / 2, 0, z), pine)
    for x in (-W / 2, W / 2):
        for y in (-D / 2, D / 2):
            plank('post', (3.0, 3.0, H), (x, y, H / 2), pine)
    plank('floor', (W, D, 1.2), (0, 0, 0.6), pine)
    order = ['almonds', 'cashew', 'pistachio', 'raisins', 'almonds', 'cashew']
    for i, (x, y, z, yaw, lean) in enumerate([(-14.5, 5, 1.8, 8, -10), (0, 6, 1.8, -3, -9), (14.5, 5, 1.8, -9, -11),
                                               (-14, -4, 1.2, 6, -6), (0.5, -3.5, 1.2, -2, -5), (14.5, -4, 1.2, -7, -7)]):
        p = rr.pouch(ART(order[i]), name=f'pouch{i}', seed=10 + i)
        p.rotation_euler = (math.radians(lean), 0, math.radians(yaw)); p.location = (x, y, z)
    sc = rr.shadow_catcher(); rr.collider(sc, shape='BOX')
    pts = [(-20, -22), (-13, -26), (-4, -23), (6, -27), (15, -22), (22, -25), (0, -30)]
    for i, kind in enumerate(('almond', 'cashew', 'pistachio', 'raisin')):
        rr.scatter(rr.variants(kind, n=2, seed=30 + i), pts[i::4], seed=40 + i)
    rr.settle(50)
    rr.camera((24, -78, 46), (0, 0, 12), lens=50)
    rr.studio(target=(0, 0, 12), dist=3.2, key_shadow_only=True, hdri=None, hdri_strength=0.9)
    save('crate')


# ---------------------------------------------------------------- the range in a gentle arc (final CTA)
def lineup():
    setup(2400, 960)
    for i, slug in enumerate(SLUGS):
        x = (i - 1.5) * 19.0
        p = rr.pouch(ART(slug), name=f'pouch{i}', seed=20 + i)
        p.location = (x, abs(x) * 0.12, 0); p.rotation_euler = (0, 0, math.radians(-x * 0.55))
    sc = rr.shadow_catcher(); rr.collider(sc, shape='BOX')
    for i, slug in enumerate(SLUGS):
        x = (i - 1.5) * 19.0; rnd = random.Random(i)
        pts = [(x + rnd.uniform(-6, 6), -7 - rnd.uniform(0, 6)) for _ in range(5)]
        rr.scatter(rr.variants(KIND[slug], n=3, seed=50 + i), pts, seed=60 + i)
    rr.settle(50)
    rr.camera((0, -150, 34), (0, 0, 10.5), lens=55)
    rr.studio(target=(0, 0, 11), dist=3.6, key_shadow_only=True, hdri=None, hdri_strength=0.9)
    save('lineup')


# ---------------------------------------------------------------- from above, on linen (Instagram)
def flatlay():
    setup(2400, 1200, transparent=False)
    rr.collider(rr.cloth(seed=11, size=(170, 120), res=(340, 240), lift=0.5))
    for i, (x, y, yaw) in enumerate([(-24, 1.5, 14), (0, -2.5, -8), (24, 2, 10)]):      # three packs lying face up
        p = rr.pouch(ART(SLUGS[i]), name=f'flat{i}', seed=30 + i, depth=1.5)
        r = math.radians(yaw)                                                           # a lying pouch grows from its base edge,
        p.rotation_euler = (math.radians(-90), 0, r); p.location = (x + 11.5 * math.sin(r), y - 11.5 * math.cos(r), 1.7)   # so re-centre it
        rr.collider(p, shape='CONVEX_HULL')
    b = rr.bowl(radius=6.5, height=3.8, loc=(37, 12, 0)); rr.collider(b)
    rr.heap(rr.variants('raisin', n=3, seed=90), center=(37, 12, 1.2), radius=5.0, height=1.8, rounds=4, seed=91)
    rnd = random.Random(7)
    for i, (kind, cx, cy) in enumerate([('almond', -11, -15), ('cashew', 12, 14), ('pistachio', -37, 13), ('almond', 36, -13), ('cashew', -36, -14)]):
        pts = [(cx + rnd.uniform(-4.5, 4.5), cy + rnd.uniform(-3, 3)) for _ in range(7)]
        rr.scatter(rr.variants(kind, n=3, seed=70 + i), pts, seed=80 + i)
    rr.settle(60)
    rr.camera((0, -4, 118), (0, 0, 0), lens=50)
    rr.studio(target=(0, 0, 0), dist=3.0, hdri_strength=0.3, key=1.1, key_from=(-30, 22, 40))
    save('flatlay')


# ---------------------------------------------------------------- RR monogram in gold (About)
def seal():
    setup(1200, 1200)
    objs = svg_file(os.path.join(rr.PROJECT, 'public', 'logo-mark.svg'))
    s = fit(objs, 12.0, center=(0, 0, 0))
    g = gold(0.18)
    for o in objs:
        cu = o.data; cu.dimensions = '2D'; cu.fill_mode = 'BOTH'; cu.extrude = 0.55 / s; cu.bevel_depth = 0.08 / s; cu.bevel_resolution = 4
        cu.materials.clear(); cu.materials.append(g)
        o.matrix_world = Matrix.Translation((0, 0, 8.4)) @ Matrix.Rotation(math.radians(90), 4, 'X') @ o.matrix_world
    bpy.ops.mesh.primitive_cylinder_add(vertices=160, radius=7.2, depth=2.2, location=(0, 0, 1.1))
    base = smooth(bpy.context.object); base.data.materials.append(rr.material('walnut'))
    bv = base.modifiers.new('round', 'BEVEL'); bv.width = 0.25; bv.segments = 4; bv.limit_method = 'ANGLE'
    rr.shadow_catcher()
    rr.camera((-16, -62, 16), (0, 0, 8), lens=85)
    rr.studio(target=(0, 0, 8), dist=1.6, key_shadow_only=True, hdri_strength=0.6)
    save('seal')


# ---------------------------------------------------------------- gold map pin (Contact)
def pin():
    setup(1000, 1000)
    path = os.path.join(SVG, 'pin-solid.svg')
    open(path, 'w').write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="#000" fill-rule="evenodd" '
                          'd="M12 2C8.1 2 5 5.1 5 9c0 5.2 7 13 7 13s7-7.8 7-13c0-3.9-3.1-7-7-7Zm0 4.2a2.8 2.8 0 1 1 0 5.6 2.8 2.8 0 0 1 0-5.6Z"/></svg>')
    objs = svg_file(path); s = fit(objs, 9.0)
    g = gold(0.16)
    for o in objs:
        cu = o.data; cu.dimensions = '2D'; cu.fill_mode = 'BOTH'; cu.extrude = 0.9 / s; cu.bevel_depth = 0.32 / s; cu.bevel_resolution = 5
        cu.materials.clear(); cu.materials.append(g)
        o.matrix_world = Matrix.Translation((0, 0, 7.6)) @ Matrix.Rotation(math.radians(-22), 4, 'Z') @ Matrix.Rotation(math.radians(90), 4, 'X') @ o.matrix_world
    sc = rr.shadow_catcher(); rr.collider(sc, shape='BOX')
    pts = [(-5.5, -3), (4.8, -4.5), (-1.5, -6.8), (6.5, 1.5), (-6.8, 2)]
    for i, kind in enumerate(('almond', 'cashew', 'pistachio', 'raisin', 'almond')):
        rr.scatter(rr.variants(kind, n=1, seed=100 + i), [pts[i]], seed=110 + i)
    rr.settle(40)
    rr.camera((0, -48, 15), (0, 0, 5.5), lens=85)
    rr.studio(target=(0, 0, 5), dist=1.2, key_shadow_only=True, hdri_strength=0.6)
    save('pin')


# ---------------------------------------------------------------- dry fruits resting on the footer's top edge
def footer():
    setup(1600, 380)
    sc = rr.shadow_catcher(); rr.collider(sc, shape='BOX')
    kinds = ['almond', 'raisin', 'cashew', 'pistachio', 'almond', 'raisin', 'pistachio', 'cashew']
    pts = [(-9.5 + i * 2.75 + random.Random(i).uniform(-0.4, 0.4), random.Random(i + 9).uniform(-1.0, 1.0)) for i in range(len(kinds))]
    for i, kind in enumerate(kinds):
        rr.scatter(rr.variants(kind, n=1, seed=120 + i), [pts[i]], seed=130 + i)
    rr.settle(40)
    rr.camera((0, -60, 22), (0, 0, 0.9), lens=85, ortho=24)
    rr.studio(target=(0, 0, 0), dist=0.9, key_shadow_only=True, hdri_strength=0.6)
    save('footer')


JOBS = {'icons': icons, 'crate': crate, 'lineup': lineup, 'flatlay': flatlay, 'seal': seal, 'pin': pin, 'footer': footer}
for job in [a for a in args if not a.startswith('-')] or list(JOBS):
    JOBS[job]()
