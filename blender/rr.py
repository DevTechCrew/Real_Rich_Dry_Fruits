# Real Rich "photo studio" for Blender 5.2: one lighting rig, one colour setup, procedural dry fruits and props.
# Every render script imports this, so all assets share the same look. Scene units are centimetres.
# Run a script with:  blender -b --factory-startup -P blender/<script>.py -- [options]
import bpy, bmesh, math, os, random, time
from mathutils import Euler, Vector, Matrix, noise

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))          # real-rich/
WORK = os.path.join(os.path.dirname(PROJECT), 'blend-src')                     # .blend files and raw renders stay outside the repo
OUT = os.path.join(WORK, 'out')
HDRI_DIR = os.path.join(os.path.dirname(bpy.app.binary_path), '..', 'Resources', f'{bpy.app.version[0]}.{bpy.app.version[1]}', 'datafiles', 'studiolights', 'world')

# palette (site): ivory, almond, walnut, espresso, gold
IVORY, ALMOND, WALNUT, ESPRESSO, GOLD = '#F7F2E8', '#E8D9C0', '#7A5A3C', '#2B1E16', '#B8954A'


def rgb(hexstr, a=1.0):
    h = hexstr.lstrip('#'); c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]  # sRGB -> linear
    return (*lin, a)


# ---------------------------------------------------------------- scene, render, colour
def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    _MATS.clear(); _HULLS.clear(); _POUR.clear()           # cached data died with the old scene
    sc = bpy.context.scene
    sc.unit_settings.system = 'METRIC'
    sc.unit_settings.scale_length = 0.01  # 1 unit = 1 cm, so depth of field behaves like a real macro lens
    return sc


def render_settings(w, h, samples=160, transparent=False, exposure=0.0):
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    prefs = bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type = 'METAL'
    prefs.get_devices()
    for d in prefs.devices:
        d.use = d.type == 'METAL'
    sc.cycles.device = 'GPU'
    sc.cycles.samples = samples
    sc.cycles.use_adaptive_sampling = True
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 10
    sc.cycles.diffuse_bounces = 4
    sc.cycles.glossy_bounces = 4
    sc.cycles.transmission_bounces = 8
    sc.cycles.transparent_max_bounces = 8
    sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = w, h, 100
    sc.render.film_transparent = transparent
    im = sc.render.image_settings
    im.file_format = 'PNG'; im.color_mode = 'RGBA' if transparent else 'RGB'; im.color_depth = '16'
    # Khronos PBR Neutral keeps base colours true (the client's pack art and the real colour of each nut) and only rolls
    # off the highlights, which AgX and Filmic would desaturate.
    vs = sc.view_settings
    vs.view_transform = 'Khronos PBR Neutral'
    vs.exposure = exposure
    return sc


def render(path):
    sc = bpy.context.scene
    os.makedirs(os.path.dirname(path), exist_ok=True)
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
    print('RENDERED', path)


def save_blend(name):
    os.makedirs(WORK, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(WORK, name), compress=True)


# ---------------------------------------------------------------- lighting rig and camera
def rgba_sockets(mix_node):
    """A, B inputs and Result output of a Mix node in colour mode."""
    pick = lambda socks, name: next(s for s in socks if s.name == name and s.type == 'RGBA')
    return pick(mix_node.inputs, 'A'), pick(mix_node.inputs, 'B'), pick(mix_node.outputs, 'Result')


def kelvin(k, amount=0.3):
    """Approximate linear RGB of a black body, normalised to max 1, blended toward white by 1 - amount: the studio uses
    only a hint of colour temperature, so brand colours and the real colour of each nut stay true."""
    t = k / 100
    r = 255 if t <= 66 else 329.7 * (t - 60) ** -0.1332
    g = 99.47 * math.log(t) - 161.12 if t <= 66 else 288.12 * (t - 60) ** -0.0755
    b = 255 if t >= 66 else (0 if t <= 19 else 138.52 * math.log(t - 10) - 305.04)
    c = [max(0, min(255, v)) / 255 for v in (r, g, b)]
    lin = [x ** 2.2 for x in c]; m = max(lin)
    return tuple(1 - amount + amount * x / m for x in lin)


def aim(obj, target):
    d = Vector(target) - obj.location
    obj.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()


def area_light(name, loc, target, size, power, color):
    L = bpy.data.lights.new(name, 'AREA'); L.shape = 'DISK'; L.size = size; L.energy = power; L.color = color
    o = bpy.data.objects.new(name, L); bpy.context.scene.collection.objects.link(o); o.location = loc; aim(o, target)
    return o


def studio(target=(0, 0, 0), dist=1.0, key=1.0, hdri='interior.exr', hdri_strength=0.5, hdri_rot=-0.6, key_shadow_only=False,
           key_from=(-34, -26, 42), fill=1.0):
    """The shared rig: big, slightly warm key top-left, weak cool fill right, faint rim, and an HDRI (turned almost grey)
    for soft reflections. dist scales the rig to the subject (1.0 suits a subject about 10 cm across)."""
    sc = bpy.context.scene
    w = bpy.data.worlds.new('studio'); sc.world = w; w.use_nodes = True
    nt = w.node_tree; nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputWorld'); bg = nt.nodes.new('ShaderNodeBackground')
    env = nt.nodes.new('ShaderNodeTexEnvironment')
    if hdri:
        env.image = bpy.data.images.load(os.path.join(HDRI_DIR, hdri))
    else:                                                 # hdri=None: an even grey studio, so a shadow catcher keeps only a soft contact shadow
        env = nt.nodes.new('ShaderNodeRGB'); env.outputs['Color'].default_value = (0.8, 0.8, 0.8, 1)
    mp = nt.nodes.new('ShaderNodeMapping'); tc = nt.nodes.new('ShaderNodeTexCoord')
    mp.inputs['Rotation'].default_value[2] = hdri_rot
    warm = nt.nodes.new('ShaderNodeMix'); warm.data_type = 'RGBA'; warm.blend_type = 'MULTIPLY'; warm.inputs['Factor'].default_value = 1.0
    wa, wb, wr = rgba_sockets(warm)
    wb.default_value = (*kelvin(5800), 1)  # only a hint of warmth in the reflections
    if hdri:
        nt.links.new(tc.outputs['Generated'], mp.inputs['Vector']); nt.links.new(mp.outputs['Vector'], env.inputs['Vector'])
    grey = nt.nodes.new('ShaderNodeHueSaturation'); grey.inputs['Saturation'].default_value = 0.15   # the bundled HDRIs are amber
    nt.links.new(env.outputs['Color'], grey.inputs['Color']); nt.links.new(grey.outputs['Color'], wa); nt.links.new(wr, bg.inputs['Color'])
    bg.inputs['Strength'].default_value = hdri_strength
    nt.links.new(bg.outputs['Background'], out.inputs['Surface'])
    t = Vector(target); s = dist
    area_light('key', t + Vector(key_from) * s, t, 46 * s, 5200 * key * s * s, kelvin(5200))
    lights = [area_light('fill', t + Vector((40, -18, 14)) * s, t, 34 * s, 700 * fill * s * s, kelvin(7600)),
              area_light('rim', t + Vector((10, 36, 26)) * s, t, 18 * s, 900 * key * s * s, kelvin(5600))]
    if key_shadow_only:                                   # a cut-out on a shadow catcher keeps one soft shadow
        for o in lights:
            o.data.use_shadow = False


def camera(loc, target, lens=85, fstop=None, focus=None, ortho=None, shift=(0, 0)):
    sc = bpy.context.scene
    c = bpy.data.cameras.new('cam'); c.lens = lens; c.sensor_width = 36
    c.shift_x, c.shift_y = shift
    if ortho:
        c.type = 'ORTHO'; c.ortho_scale = ortho
    o = bpy.data.objects.new('cam', c); sc.collection.objects.link(o); o.location = loc; aim(o, target); sc.camera = o
    if fstop:
        c.dof.use_dof = True; c.dof.aperture_fstop = fstop
        c.dof.focus_distance = focus if focus else (Vector(target) - Vector(loc)).length
    return o


# ---------------------------------------------------------------- material helpers
class M:
    """Tiny node-building helper around a Principled BSDF material."""
    def __init__(self, name):
        self.mat = bpy.data.materials.new(name); self.mat.use_nodes = True
        self.nt = self.mat.node_tree; self.nt.nodes.clear()
        self.out = self.n('ShaderNodeOutputMaterial'); self.bsdf = self.n('ShaderNodeBsdfPrincipled')
        self.link(self.bsdf.outputs['BSDF'], self.out.inputs['Surface'])

    def n(self, kind, **props):
        node = self.nt.nodes.new(kind)
        for k, v in props.items():
            setattr(node, k, v)
        return node

    def link(self, a, b):
        self.nt.links.new(a, b)

    def set(self, **inputs):
        for k, v in inputs.items():
            self.bsdf.inputs[k.replace('_', ' ')].default_value = v
        return self

    def coords(self, scale=(1, 1, 1), space='Object'):
        tc = self.n('ShaderNodeTexCoord'); mp = self.n('ShaderNodeMapping')
        mp.inputs['Scale'].default_value = scale
        self.link(tc.outputs[space], mp.inputs['Vector'])
        return mp.outputs['Vector']

    def noise(self, vec, scale, detail=4.0, rough=0.55, distortion=0.0, kind='FBM'):
        t = self.n('ShaderNodeTexNoise'); t.noise_type = kind
        t.inputs['Scale'].default_value = scale; t.inputs['Detail'].default_value = detail
        t.inputs['Roughness'].default_value = rough; t.inputs['Distortion'].default_value = distortion
        self.link(vec, t.inputs['Vector'])
        return t.outputs['Fac']

    def voronoi(self, vec, scale, feature='F1', rand=1.0):
        t = self.n('ShaderNodeTexVoronoi'); t.feature = feature
        t.inputs['Scale'].default_value = scale; t.inputs['Randomness'].default_value = rand
        self.link(vec, t.inputs['Vector'])
        return t.outputs['Distance']

    def ramp(self, fac, stops):
        r = self.n('ShaderNodeValToRGB'); el = r.color_ramp.elements
        for i, (pos, col) in enumerate(stops):
            e = el[i] if i < len(el) else el.new(pos)
            e.position = pos; e.color = rgb(col) if isinstance(col, str) else col
        self.link(fac, r.inputs['Fac'])
        return r.outputs['Color']

    def math(self, op, a, b=None, clamp=False):
        m = self.n('ShaderNodeMath', operation=op); m.use_clamp = clamp
        for i, v in enumerate((a, b)):
            if v is None:
                continue
            if isinstance(v, (int, float)):
                m.inputs[i].default_value = v
            else:
                self.link(v, m.inputs[i])
        return m.outputs['Value']

    def mix(self, fac, a, b, blend='MIX'):
        m = self.n('ShaderNodeMix', data_type='RGBA', blend_type=blend)
        sa, sb, res = rgba_sockets(m)
        for target, v in ((m.inputs['Factor'], fac), (sa, a), (sb, b)):
            if isinstance(v, str):
                target.default_value = rgb(v)
            elif isinstance(v, (int, float, tuple)):
                target.default_value = v
            else:
                self.link(v, target)
        return res

    def bump(self, height, strength=0.4, distance=0.02, normal=None):
        b = self.n('ShaderNodeBump'); b.inputs['Strength'].default_value = strength; b.inputs['Distance'].default_value = distance
        self.link(height, b.inputs['Height'])
        if normal is not None:
            self.link(normal, b.inputs['Normal'])
        return b.outputs['Normal']

    def rand(self):
        return self.n('ShaderNodeObjectInfo').outputs['Random']


def per_object_variation(m, col, hue=0.02, val=0.12):
    """Shift hue/value a little per object, so a heap never looks cloned."""
    r = m.rand()
    hue_in = m.math('MULTIPLY', m.math('SUBTRACT', r, 0.5), hue * 2)
    h = m.n('ShaderNodeHueSaturation')
    m.link(m.math('ADD', hue_in, 0.5), h.inputs['Hue'])
    m.link(m.math('ADD', m.math('MULTIPLY', m.math('SUBTRACT', r, 0.5), val * 2), 1.0), h.inputs['Value'])
    m.link(col, h.inputs['Color'])
    return h.outputs['Color']


# ---------------------------------------------------------------- materials
def mat_almond():
    """Warm brown skin with fine wavy grooves running along the length and meeting at the tip, like real almond skin.
    The grooves follow the meridians of the sphere the almond was shaped from (mesh attribute 'sph')."""
    m = M('almond')
    v = m.coords()
    sph = m.n('ShaderNodeAttribute', attribute_name='sph').outputs['Vector']
    xyz = m.n('ShaderNodeSeparateXYZ'); m.link(sph, xyz.inputs['Vector'])
    theta = m.math('ARCTAN2', xyz.outputs['Z'], xyz.outputs['Y'])               # angle round the long axis

    def grooves(count, wobble, scale, seed, power):
        mp = m.n('ShaderNodeMapping'); mp.inputs['Location'].default_value = (seed, seed * 1.7, seed * 0.6)
        mp.inputs['Scale'].default_value = (1.0, 2.6, 2.6); m.link(sph, mp.inputs['Vector'])
        d = m.noise(mp.outputs['Vector'], scale, detail=2, rough=0.5)
        ph = m.math('ADD', m.math('MULTIPLY', theta, count), m.math('MULTIPLY', m.math('SUBTRACT', d, 0.5), wobble))
        g = m.math('MULTIPLY', m.math('ADD', m.math('SINE', ph), 1.0), 0.5)          # 0 in a groove .. 1 on a ridge
        return m.math('POWER', m.math('SUBTRACT', 1.0, g), power)                     # narrow dark grooves
    lines = m.math('MAXIMUM', grooves(19, 15, 1.6, 0.0, 2.2), m.math('MULTIPLY', grooves(31, 20, 2.3, 7.3, 3.2), 0.55))   # coarse enough to read at web size
    fade = m.n('ShaderNodeMapRange'); fade.inputs['From Min'].default_value = 0.8; fade.inputs['From Max'].default_value = 0.97
    fade.inputs['To Min'].default_value = 1.0; fade.inputs['To Max'].default_value = 0.25
    m.link(m.math('ABSOLUTE', xyz.outputs['X']), fade.inputs['Value'])               # ease off where the grooves bunch up at the ends
    strength = m.noise(v, 3.0, detail=2, rough=0.5)                                  # some grooves are deep, some faint
    lines = m.math('MULTIPLY', m.math('MULTIPLY', lines, fade.outputs['Result']), m.math('ADD', m.math('MULTIPLY', strength, 0.9), 0.35), clamp=True)
    patch = m.noise(m.coords(scale=(0.6, 2.2, 2.2)), 2.0, detail=4, rough=0.55)
    pores = m.voronoi(v, 34, feature='F1')
    base = m.ramp(patch, [(0.3, '#A8642F'), (0.55, '#BE7640'), (0.78, '#CF8D55')])
    base = m.mix(m.math('MULTIPLY', lines, 0.9), base, '#6A3414')
    base = m.mix(m.math('MULTIPLY', m.math('LESS_THAN', pores, 0.04), 0.3), base, '#4A2410')    # tiny dark pores
    col = per_object_variation(m, base, hue=0.008, val=0.13)
    m.link(col, m.bsdf.inputs['Base Color'])
    m.link(m.math('ADD', m.math('MULTIPLY', lines, 0.25), 0.38), m.bsdf.inputs['Roughness'])   # ridges catch a soft shine
    h = m.math('ADD', m.math('MULTIPLY', lines, -1.0), m.math('MULTIPLY', patch, 0.2))
    m.link(m.bump(h, strength=0.9, distance=0.03), m.bsdf.inputs['Normal'])
    m.set(Subsurface_Weight=0.1, Subsurface_Radius=(0.3, 0.18, 0.1), Subsurface_Scale=0.05, Specular_IOR_Level=0.4, Sheen_Weight=0.06, Sheen_Roughness=0.55)
    return m.mat


def mat_cashew():
    m = M('cashew')
    v = m.coords()
    blot = m.noise(v, 2.6, detail=3, rough=0.5)
    fine = m.noise(v, 52, detail=2, rough=0.6)
    speck = m.voronoi(v, 22, feature='F1')
    gen = m.n('ShaderNodeSeparateXYZ'); m.link(m.n('ShaderNodeTexCoord').outputs['Generated'], gen.inputs['Vector'])
    ends = m.math('ABSOLUTE', m.math('SUBTRACT', gen.outputs['X'], 0.5))            # 0 middle .. 0.5 tips
    col = m.ramp(m.math('ADD', m.math('MULTIPLY', ends, 1.1), m.math('MULTIPLY', blot, 0.3)),
                 [(0.15, '#F1E4C4'), (0.40, '#E8D3A6'), (0.60, '#DBBC82'), (0.78, '#CBA367')])
    col = m.mix(m.math('MULTIPLY', m.math('LESS_THAN', speck, 0.045), 0.35), col, '#B58A52')
    col = per_object_variation(m, col, hue=0.01, val=0.06)
    m.link(col, m.bsdf.inputs['Base Color'])
    z = m.n('ShaderNodeSeparateXYZ'); m.link(m.n('ShaderNodeTexCoord').outputs['Object'], z.inputs['Vector'])
    groove = m.n('ShaderNodeMapRange'); groove.inputs['From Min'].default_value = 0.0; groove.inputs['From Max'].default_value = 0.1
    m.link(m.math('ABSOLUTE', z.outputs['Z']), groove.inputs['Value'])          # the seam between the two halves
    grain = m.noise(v, 90, detail=2, rough=0.6)
    pits = m.math('MAXIMUM', m.math('SUBTRACT', 0.16, m.voronoi(v, 30, feature='F1')), 0.0)       # small shallow dimples
    lumps = m.noise(v, 1.4, detail=2, rough=0.5)
    h = m.math('ADD', groove.outputs['Result'], m.math('ADD', m.math('MULTIPLY', fine, 0.2), m.math('MULTIPLY', grain, 0.12)))
    h = m.math('ADD', h, m.math('ADD', m.math('MULTIPLY', pits, -2.2), m.math('MULTIPLY', lumps, 0.5)))
    m.link(m.bump(h, strength=0.55, distance=0.035), m.bsdf.inputs['Normal'])
    m.link(m.math('ADD', m.math('MULTIPLY', fine, 0.14), 0.47), m.bsdf.inputs['Roughness'])
    m.set(Subsurface_Weight=0.35, Subsurface_Radius=(0.6, 0.45, 0.22), Subsurface_Scale=0.12, Specular_IOR_Level=0.42, Sheen_Weight=0.12, Sheen_Roughness=0.5,
          Coat_Weight=0.06, Coat_Roughness=0.4)
    return m.mat


def mat_pistachio_shell():
    m = M('pistachio_shell')
    v = m.coords()
    blot = m.noise(v, 2.2, detail=4, rough=0.6)
    speck = m.noise(v, 60, detail=1, rough=0.4)
    col = m.ramp(m.math('ADD', m.math('MULTIPLY', blot, 0.8), m.math('MULTIPLY', speck, 0.25)),
                 [(0.30, '#E6D5B6'), (0.52, '#D6BE98'), (0.70, '#C3A47E'), (0.86, '#A8845F')])
    blush = m.math('MULTIPLY', m.math('MAXIMUM', m.math('SUBTRACT', m.noise(v, 1.6, detail=2, rough=0.5), 0.52), 0.0), 2.2)
    col = m.mix(blush, col, '#C99A84')                                                   # pinkish stain from the hull
    col = per_object_variation(m, col, hue=0.015, val=0.1)
    m.link(col, m.bsdf.inputs['Base Color'])
    ridge = m.noise(m.coords(scale=(1, 4, 4)), 3.5, detail=5, rough=0.6)
    m.link(m.bump(m.math('ADD', ridge, m.math('MULTIPLY', speck, 0.3)), strength=0.35, distance=0.025), m.bsdf.inputs['Normal'])
    m.set(Roughness=0.62, Subsurface_Weight=0.08, Subsurface_Radius=(0.3, 0.25, 0.18), Subsurface_Scale=0.04, Specular_IOR_Level=0.35)
    return m.mat


def mat_pistachio_kernel():
    m = M('pistachio_kernel')
    v = m.coords()
    patches = m.noise(v, 1.8, detail=3, rough=0.55)
    veins = m.noise(m.coords(scale=(0.5, 2.0, 2.0)), 7.0, detail=2, rough=0.5)          # the papery skin is streaky
    col = m.ramp(m.math('ADD', m.math('MULTIPLY', patches, 0.85), m.math('MULTIPLY', veins, 0.2)),
                 [(0.36, '#86A23E'), (0.47, '#728F36'), (0.57, '#7A5A45'), (0.68, '#6E3A44'), (0.82, '#552634')])
    m.link(col, m.bsdf.inputs['Base Color'])
    m.link(m.bump(m.noise(v, 18, detail=3), strength=0.25, distance=0.02), m.bsdf.inputs['Normal'])
    m.set(Roughness=0.5, Subsurface_Weight=0.25, Subsurface_Radius=(0.25, 0.4, 0.15), Subsurface_Scale=0.06, Specular_IOR_Level=0.4)
    return m.mat


def mat_raisin():
    m = M('raisin')
    v = m.coords()
    blot = m.noise(v, 2.4, detail=4, rough=0.6)
    fine = m.noise(m.coords(scale=(0.6, 2.2, 2.2)), 14, detail=4, rough=0.6, kind='RIDGED_MULTIFRACTAL')
    col = m.ramp(m.math('ADD', m.math('MULTIPLY', blot, 0.7), m.math('MULTIPLY', fine, -0.25)),
                 [(0.05, '#9A5814'), (0.3, '#C07A22'), (0.5, '#D9962F'), (0.7, '#E8B04A'), (0.9, '#F0C870')])
    col = per_object_variation(m, col, hue=0.018, val=0.14)
    m.link(col, m.bsdf.inputs['Base Color'])
    m.link(m.bump(fine, strength=0.25, distance=0.015), m.bsdf.inputs['Normal'])
    m.set(Roughness=0.42, Subsurface_Weight=0.75, Subsurface_Radius=(1.0, 0.55, 0.15), Subsurface_Scale=0.25,
          Specular_IOR_Level=0.5, Coat_Weight=0.3, Coat_Roughness=0.24)
    return m.mat


def mat_linen(tint='#F1ECE2'):
    m = M('linen')
    v = m.coords(scale=(1, 1, 1))
    warp = m.n('ShaderNodeTexWave', wave_type='BANDS', bands_direction='X'); warp.inputs['Scale'].default_value = 2.9
    weft = m.n('ShaderNodeTexWave', wave_type='BANDS', bands_direction='Y'); weft.inputs['Scale'].default_value = 2.9   # ~1.1 mm threads
    for w in (warp, weft):
        w.inputs['Distortion'].default_value = 1.4; w.inputs['Detail'].default_value = 2
        m.link(v, w.inputs['Vector'])
    weave = m.math('MULTIPLY', warp.outputs['Fac'], weft.outputs['Fac'])
    slub = m.noise(m.coords(scale=(1, 14, 1)), 0.6, detail=3)          # uneven linen threads, a few cm long
    col = m.ramp(m.math('ADD', m.math('MULTIPLY', slub, 0.45), m.math('MULTIPLY', weave, 0.45)), [(0.2, '#D9D1C3'), (0.5, tint), (0.85, '#FBF9F4')])
    m.link(col, m.bsdf.inputs['Base Color'])
    m.link(m.bump(m.math('ADD', weave, m.math('MULTIPLY', slub, 0.6)), strength=0.6, distance=0.04), m.bsdf.inputs['Normal'])
    m.set(Roughness=0.9, Sheen_Weight=0.35, Sheen_Roughness=0.5, Specular_IOR_Level=0.3)
    return m.mat


def mat_backdrop(hexcol=ALMOND):
    m = M('backdrop')
    m.set(Base_Color=rgb(hexcol), Roughness=0.95, Specular_IOR_Level=0.2)
    return m.mat


def mat_walnut_wood():
    m = M('walnut')
    v = m.coords(scale=(1, 1, 0.25))
    rings = m.n('ShaderNodeTexWave', wave_type='RINGS', rings_direction='Z'); rings.inputs['Scale'].default_value = 1.6
    rings.inputs['Distortion'].default_value = 6; rings.inputs['Detail'].default_value = 3; m.link(v, rings.inputs['Vector'])
    grain = m.noise(m.coords(scale=(1, 1, 18)), 10, detail=6, rough=0.6)
    fac = m.math('ADD', m.math('MULTIPLY', rings.outputs['Fac'], 0.3), m.math('MULTIPLY', grain, 0.7))   # grain first, rings faint
    col = m.ramp(fac, [(0.25, '#4A2E1C'), (0.5, '#5E3C25'), (0.72, '#704A30'), (0.9, '#7E5638')])
    m.link(col, m.bsdf.inputs['Base Color'])
    m.link(m.bump(grain, strength=0.12, distance=0.02), m.bsdf.inputs['Normal'])
    m.set(Roughness=0.36, Coat_Weight=0.25, Coat_Roughness=0.25, Specular_IOR_Level=0.45)
    return m.mat


def mat_brushed_gold():
    m = M('gold')
    brush = m.noise(m.coords(scale=(1, 60, 1)), 8, detail=2)
    m.link(m.math('ADD', m.math('MULTIPLY', brush, 0.12), 0.32), m.bsdf.inputs['Roughness'])         # brushed, not a mirror
    m.set(Base_Color=rgb('#D9B26A'), Metallic=1.0, Anisotropic=0.5, Specular_IOR_Level=0.5)
    return m.mat


_MATS = {}
def material(name):
    if name not in _MATS:
        _MATS[name] = {'almond': mat_almond, 'cashew': mat_cashew, 'pistachio_shell': mat_pistachio_shell,
                       'pistachio_kernel': mat_pistachio_kernel, 'raisin': mat_raisin, 'linen': mat_linen,
                       'walnut': mat_walnut_wood, 'gold': mat_brushed_gold}[name]()
    return _MATS[name]


# ---------------------------------------------------------------- meshes
def _sphere(seg=96, rings=48):
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=rings, radius=1.0)
    return bm


def _to_object(bm, name, mat, smooth=True, subsurf=1, attrs=None):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for key, vecs in (attrs or {}).items():
        a = me.attributes.new(key, 'FLOAT_VECTOR', 'POINT'); a.data.foreach_set('vector', [c for vec in vecs for c in vec])
    if smooth is not None:                                             # None keeps the per-face flags from the bmesh
        for p in me.polygons:
            p.use_smooth = smooth
    for mt in (mat if isinstance(mat, (list, tuple)) else [mat]):
        me.materials.append(mt)
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o)
    if subsurf:
        mod = o.modifiers.new('sub', 'SUBSURF'); mod.levels = subsurf; mod.render_levels = subsurf
    return o


def _profile(u, a, b):
    return (max(0.0, 1 - u)) ** a * (max(0.0, 1 + u)) ** b


def _pmax(a, b):
    return max(_profile(-1 + 2 * i / 400, a, b) for i in range(401))


def almond(seed=0, name='almond'):
    rnd = random.Random(seed)
    L, W, T = 2.35 * rnd.uniform(0.88, 1.12), 1.42 * rnd.uniform(0.9, 1.08), 0.78 * rnd.uniform(0.88, 1.12)
    a, b = 0.7, 0.5; pm = _pmax(a, b); off = Vector((rnd.random() * 9, rnd.random() * 9, rnd.random() * 9))
    bm = _sphere(112, 56)
    sph = [vert.co.copy() for vert in bm.verts]                       # the skin's grooves are drawn in this space
    for vert in bm.verts:
        x, y, z = vert.co; u = x; r = math.sqrt(max(1e-9, 1 - u * u))
        p = _profile(u, a, b) / pm
        ny, nz = y / r * W / 2 * p, z / r * T / 2 * p * (0.92 + 0.08 * (1 - u) / 2)
        co = Vector((u * L / 2, ny + 0.035 * L * (u * u - 0.35), nz + 0.025 * L * (1 - u * u)))
        co += noise.noise_vector(co * 0.9 + off) * 0.035
        vert.co = co
    return _to_object(bm, name, material('almond'), attrs={'sph': sph})


def cashew(seed=0, name='cashew'):
    """Kidney-shaped crescent: a plump rounded head, a body that bends round and tapers to a curled tip."""
    rnd = random.Random(seed)
    L, W, T = 3.0 * rnd.uniform(0.92, 1.08), 1.42 * rnd.uniform(0.92, 1.08), 0.98 * rnd.uniform(0.92, 1.08)
    bend = math.radians(rnd.uniform(188, 206)); R = (L / 2) / (bend / 2)
    off = Vector((rnd.random() * 9, rnd.random() * 9, rnd.random() * 9))
    bm = _sphere(128, 64)
    for vert in bm.verts:
        x, y, z = vert.co; u = x; r = math.sqrt(max(1e-9, 1 - u * u))
        fat = (1 - u * u) ** 0.5 * (1 - 0.22 * u)                     # -u end is the plump head, +u tapers
        ly, lz = y / r * W / 2 * fat, z / r * T / 2 * fat
        th = u * bend / 2
        rad = R + ly * (1.0 if ly > 0 else 0.82)                       # the inner edge is a little flatter
        co = Vector((math.sin(th) * rad, R - math.cos(th) * rad, lz))
        co += noise.noise_vector(co * 0.8 + off) * 0.03
        vert.co = co
    return _to_object(bm, name, material('cashew'))


def raisin(seed=0, name='raisin'):
    """Golden kishmish: an elongated berry with a few deep folds along its length and fine wrinkles between them."""
    rnd = random.Random(seed)
    L, W, T = 1.8 * rnd.uniform(0.86, 1.14), 0.9 * rnd.uniform(0.86, 1.12), 0.68 * rnd.uniform(0.85, 1.12)
    off = Vector((rnd.random() * 20, rnd.random() * 20, rnd.random() * 20))
    folds = rnd.choice((4, 5, 5, 6)); twist = rnd.uniform(-0.6, 0.6)
    bm = _sphere(160, 72)
    for vert in bm.verts:
        n = vert.co.normalized()
        co = Vector((n.x * L / 2, n.y * W / 2, n.z * T / 2))
        phi = math.atan2(n.z, n.y) + twist * n.x + noise.noise(co * 1.4 + off) * 0.9
        fold = abs(math.sin(phi * folds / 2)) ** 0.35                      # 0 in a fold, 1 on a ridge
        tip = max(0.0, 1 - abs(n.x)) ** 0.5                                # folds fade out at the ends
        fine = abs(noise.noise(Vector((co.x * 3, co.y * 9, co.z * 9)) + off))
        d = -0.085 * (1 - fold) * tip - 0.018 * (1 - min(1.0, fine / 0.12)) + noise.noise(co * 1.1 + off) * 0.045
        vert.co = co + n * d
    return _to_object(bm, name, material('raisin'))


def pistachio(seed=0, name='pistachio', open_deg=None, kernel=True, halves=(1, -1)):
    """Two shell halves hinged at the bottom suture, split open on top over a green kernel. One mesh with two
    materials, so heaps can use linked copies. kernel=False and halves=(1,) give a loose half shell (husk)."""
    rnd = random.Random(seed)
    L, W, T = 2.05 * rnd.uniform(0.92, 1.08), 1.3 * rnd.uniform(0.92, 1.06), 1.16 * rnd.uniform(0.92, 1.06)
    a, b = 0.62, 0.5; pm = _pmax(a, b)
    alpha = math.radians(open_deg if open_deg is not None else rnd.uniform(13, 20))
    off = Vector((rnd.random() * 9, rnd.random() * 9, rnd.random() * 9))
    parts = []
    for side in halves:
        bm = _sphere(96, 48)
        for vert in bm.verts:
            x, y, z = vert.co; u = x; r = math.sqrt(max(1e-9, 1 - u * u)); p = _profile(u, a, b) / pm
            co = Vector((u * L / 2, y / r * W / 2 * p, z / r * T / 2 * p))
            co += noise.noise_vector(co * 1.1 + off) * 0.02
            vert.co = co
        geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
        bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-5, plane_co=(0, 0, 0), plane_no=(0, side, 0), clear_inner=True)
        pivot = Vector((0, 0, -T / 2 * 0.96))
        rot = Matrix.Rotation(-side * alpha, 4, 'X')
        for vert in bm.verts:
            vert.co = rot @ (vert.co - pivot) + pivot
        o = _to_object(bm, f'{name}_shell{side}', material('pistachio_shell'), subsurf=0)
        sol = o.modifiers.new('shell', 'SOLIDIFY'); sol.thickness = 0.055; sol.offset = -1
        parts.append((o, 0))
    if kernel:
        kb = _sphere(64, 32)
        for vert in kb.verts:
            n = vert.co.normalized(); co = Vector((n.x * L * 0.40, n.y * W * 0.36, n.z * T * 0.36 + 0.06))
            vert.co = co + n * noise.noise(co * 2 + off) * 0.04
        parts.append((_to_object(kb, f'{name}_kernel', material('pistachio_kernel'), subsurf=0), 1))
    bpy.context.view_layer.update(); deps = bpy.context.evaluated_depsgraph_get()
    bm = bmesh.new()
    for o, mi in parts:                                  # bake the shell thickness, then join the parts
        me = bpy.data.meshes.new_from_object(o.evaluated_get(deps))
        n0 = len(bm.faces); bm.from_mesh(me); bm.faces.ensure_lookup_table()
        for f in bm.faces[n0:]:
            f.material_index = mi
        bpy.data.objects.remove(o); bpy.data.meshes.remove(me)
    return _to_object(bm, name, [material('pistachio_shell'), material('pistachio_kernel')])


NUT_BUILDERS = {'almond': almond, 'cashew': cashew, 'pistachio': pistachio, 'raisin': raisin}


# ---------------------------------------------------------------- props
def plane(name, size_x, size_y, mat, loc=(0, 0, 0), subdiv=0, displace=0.0, disp_scale=6.0, seed=0):
    bpy.ops.mesh.primitive_plane_add(size=1, location=loc)
    o = bpy.context.object; o.name = name; o.scale = (size_x, size_y, 1)
    bpy.ops.object.transform_apply(scale=True)
    o.data.materials.append(mat)
    if subdiv:
        s = o.modifiers.new('sub', 'SUBSURF'); s.subdivision_type = 'SIMPLE'; s.levels = s.render_levels = subdiv
    if displace:
        t = bpy.data.textures.new(f'{name}_folds', 'CLOUDS'); t.noise_scale = disp_scale; t.noise_depth = 2
        d = o.modifiers.new('folds', 'DISPLACE'); d.texture = t; d.strength = displace; d.mid_level = 0.5
        d.texture_coords = 'GLOBAL'
    for p in o.data.polygons:
        p.use_smooth = True
    return o


def sweep(name='sweep', width=200, depth=120, height=90, radius=40, mat=None, y0=-20):
    """A seamless studio backdrop: floor that curves up into a wall."""
    verts, faces = [], []
    prof = []
    for i in range(0, 25):
        prof.append((y0 + depth * i / 24, 0.0))
    for i in range(1, 25):
        a = math.pi / 2 * i / 24
        prof.append((y0 + depth + radius * math.sin(a), radius * (1 - math.cos(a))))
    for i in range(1, 13):
        prof.append((y0 + depth + radius, radius + (height - radius) * i / 12))
    xs = [-width / 2, width / 2]
    for (y, z) in prof:
        for x in xs:
            verts.append((x, y, z))
    for i in range(len(prof) - 1):
        a, b = i * 2, (i + 1) * 2
        faces.append((a, a + 1, b + 1, b))
    me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces); me.update()
    for p in me.polygons:
        p.use_smooth = True
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o)
    o.data.materials.append(mat or mat_backdrop())
    sub = o.modifiers.new('sub', 'SUBSURF'); sub.levels = sub.render_levels = 2
    return o


def bowl(name='bowl', radius=7.0, height=4.2, wall=0.45, loc=(0, 0, 0)):
    """Turned walnut bowl from a profile and a Screw modifier."""
    pts = []
    for i in range(0, 13):
        t = i / 12; pts.append((radius * 0.38 + (radius - radius * 0.38) * (1 - (1 - t) ** 2.2), height * t ** 1.6))
    inner = [(max(0.0, r - wall), max(wall * 0.9, z - wall * 0.2)) for (r, z) in reversed(pts)]
    prof = [(0.0, 0.0)] + pts + [(radius - wall * 0.5, height + 0.05)] + inner + [(0.0, wall * 0.9)]
    verts = [(r, 0.0, z) for (r, z) in prof]; edges = [(i, i + 1) for i in range(len(verts) - 1)]
    me = bpy.data.meshes.new(name); me.from_pydata(verts, edges, []); me.update()
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o); o.location = loc
    scr = o.modifiers.new('lathe', 'SCREW'); scr.axis = 'Z'; scr.steps = 96; scr.render_steps = 96; scr.use_merge_vertices = True
    sub = o.modifiers.new('sub', 'SUBSURF'); sub.levels = sub.render_levels = 2
    o.data.materials.append(material('walnut'))
    for p in me.polygons:
        p.use_smooth = True
    bpy.context.view_layer.objects.active = o
    return o


def spoon(name='spoon', loc=(0, 0, 0), rot_z=0.0):
    bm = _sphere(48, 24)
    for vert in bm.verts:
        x, y, z = vert.co; vert.co = Vector((x * 2.2, y * 1.45, z * 0.55))
    bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-5, plane_co=(0, 0, 0.12), plane_no=(0, 0, 1), clear_outer=True)
    bowl_o = _to_object(bm, f'{name}_bowl', material('gold'))
    s = bowl_o.modifiers.new('t', 'SOLIDIFY'); s.thickness = 0.12; bowl_o.modifiers.move(len(bowl_o.modifiers) - 1, 0)
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.28, depth=10, location=(6.8, 0, 0.35), rotation=(0, math.radians(86), 0))
    h = bpy.context.object; h.name = f'{name}_handle'; h.scale = (1, 1.35, 1); h.data.materials.append(material('gold'))
    bv = h.modifiers.new('round', 'BEVEL'); bv.width = 0.08; bv.segments = 3
    for p in h.data.polygons:
        p.use_smooth = True
    root = bpy.data.objects.new(name, None); bpy.context.scene.collection.objects.link(root)
    bowl_o.parent = root; h.parent = root
    root.location = loc; root.rotation_euler = (0, 0, rot_z)
    return root


# ---------------------------------------------------------------- the 250 g stand-up pouch
def mat_pouch_front(art_path, W=16.0, H=23.0, seal=0.7, top_seal=1.0):
    """The client's front artwork, untouched, on a satin laminate. Only the heat seals get a crimp (bump only)."""
    m = M('pouch_front')
    tex = m.n('ShaderNodeTexImage'); tex.image = bpy.data.images.load(art_path); tex.interpolation = 'Cubic'; tex.extension = 'EXTEND'
    uv = m.n('ShaderNodeTexCoord').outputs['UV']; m.link(uv, tex.inputs['Vector'])
    m.link(tex.outputs['Color'], m.bsdf.inputs['Base Color'])
    sep = m.n('ShaderNodeSeparateXYZ'); m.link(uv, sep.inputs['Vector'])
    u, v = sep.outputs['X'], sep.outputs['Y']
    top = m.math('GREATER_THAN', v, 1 - top_seal / H)
    side = m.math('MAXIMUM', m.math('LESS_THAN', u, seal / W), m.math('GREATER_THAN', u, 1 - seal / W))
    lines_top = m.math('SINE', m.math('MULTIPLY', u, 2 * math.pi * W / 0.09))       # crimp lines 0.9 mm apart
    lines_side = m.math('SINE', m.math('MULTIPLY', v, 2 * math.pi * H / 0.09))
    h = m.math('ADD', m.math('MULTIPLY', top, lines_top), m.math('MULTIPLY', m.math('MULTIPLY', side, m.math('SUBTRACT', 1.0, top)), lines_side))
    m.link(m.bump(h, strength=0.35, distance=0.004), m.bsdf.inputs['Normal'])
    m.set(Roughness=0.55, Specular_IOR_Level=0.32)                                  # soft-touch matte laminate
    return m.mat


def mat_pouch_back(hexcol='#F6E3C4'):
    m = M('pouch_back')
    m.set(Base_Color=rgb(hexcol), Roughness=0.55, Specular_IOR_Level=0.32)
    return m.mat


def pouch(art_path, name='pouch', W=16.0, H=23.0, depth=2.6, seal=0.7, top_seal=1.0, seed=0, back_hex='#F6E3C4', res=(116, 176)):
    """A filled 16 x 23 cm stand-up pouch standing on z = 0, front facing -y.
    The artwork is mapped by film length, so it is never stretched: the film keeps its width, which pulls the side seals
    in where the pouch bulges, as on a real filled pouch. Heat seals, a zip line, tear notches, creases from the top
    corners and the gentle lumps of nuts inside are modelled; the art itself is left exactly as supplied."""
    rnd = random.Random(seed)
    off = Vector((rnd.random() * 50, rnd.random() * 50, rnd.random() * 50))
    Wb = W - 2 * seal                       # film width that bulges, between the side seals
    t_top = 1 - top_seal / H
    film = 0.015                            # half the thickness of the flat seals

    def S(v):                               # bulge (0..1) up the film
        if v >= t_top:
            return 0.0
        k = max(0.0, (v - 0.3) / (t_top - 0.3))
        sv = math.cos(math.pi / 2 * k) ** 1.3
        if v < 0.05:
            sv *= 1 - 0.22 * (1 - v / 0.05) ** 2  # the base rounds back a little
        return sv
    prof = lambda t: max(0.0, 1 - abs(t) ** 2.2) ** 0.62
    NT = 300
    ts = [-1 + 2 * k / NT for k in range(NT + 1)]; fp = [prof(t) for t in ts]

    def solve_row(D):
        """Half width of the bulge and the cumulative film length across it, for bulge depth D."""
        def arc(hw):
            return sum(math.hypot(hw * (ts[k + 1] - ts[k]), D * (fp[k + 1] - fp[k])) for k in range(NT))
        lo, hi = 0.3 * Wb / 2, Wb / 2
        for _ in range(30):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if arc(mid) < Wb else (lo, mid)
        hw = (lo + hi) / 2; cum = [0.0]
        for k in range(NT):
            cum.append(cum[-1] + math.hypot(hw * (ts[k + 1] - ts[k]), D * (fp[k + 1] - fp[k])))
        scale = Wb / cum[-1]
        return hw, [c * scale for c in cum]

    def t_at(cum, target):
        lo, hi = 0, NT
        while hi - lo > 1:
            mid = (lo + hi) // 2
            lo, hi = (mid, hi) if cum[mid] <= target else (lo, mid)
        f = (target - cum[lo]) / max(1e-9, cum[hi] - cum[lo])
        return ts[lo] + (ts[hi] - ts[lo]) * f

    # rows (film height) and columns (film across), with exact rows/columns on the seal boundaries
    nb, nr = res                            # columns across the bulge, rows below the top seal (lower for real-time models)
    ns, nt_ = (6, 8) if nb >= 80 else (2, 2)
    vs = [t_top * j / nr for j in range(nr + 1)] + [t_top + (1 - t_top) * j / nt_ for j in range(1, nt_ + 1)]
    ss = ([-W / 2 + seal * i / ns for i in range(ns)] + [-Wb / 2 + Wb * i / nb for i in range(nb)] +
          [Wb / 2 + seal * i / ns for i in range(ns + 1)])
    zs = [0.0]
    for j in range(1, len(vs)):
        dv = (vs[j] - vs[j - 1]) * H; dD = depth * (S(vs[j]) - S(vs[j - 1]))
        zs.append(zs[-1] + math.sqrt(max(1e-12, dv * dv - dD * dD)))
    z_top = zs[-1]; z_zip = z_top - 3.0; z_notch = z_top - 2.3; fill_z = zs[0] + 0.62 * z_top

    creases = []                            # (origin, direction, length, amplitude, width): from the top corners down and in,
    for sgn in (-1, 1):                     # and two short ones where the gusset pulls at the bottom corners
        for _ in range(4):
            a = math.radians(rnd.uniform(22, 62))
            creases.append((Vector((sgn * (Wb / 2 - rnd.uniform(0.1, 0.9)), z_top - top_seal - rnd.uniform(0.05, 0.6))),
                            Vector((-sgn * math.cos(a), -math.sin(a))), rnd.uniform(2.5, 6.5), rnd.uniform(0.08, 0.16), rnd.uniform(0.24, 0.45)))
        for _ in range(2):
            a = math.radians(rnd.uniform(28, 55))
            creases.append((Vector((sgn * (Wb / 2 - rnd.uniform(0.0, 0.4)), rnd.uniform(0.3, 1.2))),
                            Vector((-sgn * math.cos(a), math.sin(a))), rnd.uniform(1.5, 3.0), rnd.uniform(0.05, 0.1), rnd.uniform(0.2, 0.35)))

    def crease(x, z):
        h = 0.0; p = Vector((x, z))
        for o, d, ln, amp, w in creases:
            q = p - o; along = q.dot(d)
            if 0 < along < ln:
                perp = q.dot(Vector((-d.y, d.x)))
                h += amp * math.exp(-(perp / w) ** 2) * (1 - along / ln) ** 1.5 * (1 - math.exp(-along * 6))
        return h

    bm = bmesh.new(); uvl = bm.loops.layers.uv.new('UVMap')
    front, back = [], []
    for j, v in enumerate(vs):
        D = depth * S(v); hw, cum = solve_row(D); z = zs[j]
        notch = 0.45 * max(0.0, 1 - abs(z - z_notch) / 0.22)       # V-shaped tear notch in both side seals
        rf, rb = [], []
        for s_ in ss:
            if abs(s_) <= Wb / 2 + 1e-9:
                t = t_at(cum, s_ + Wb / 2); x = hw * t; bulge = D * prof(t); sfilm = s_; inside = prof(t)
            else:
                c = (seal - notch) / seal                            # the notch cuts the seal; the art is cut, not squeezed
                sfilm = math.copysign(Wb / 2 + (abs(s_) - Wb / 2) * c, s_)
                x = math.copysign(hw + abs(sfilm) - Wb / 2, s_); bulge = 0.0; inside = 0.0
            p3 = Vector((x, 0.0, z))
            lumps = 0.0
            if inside > 0:
                fade = 1.0 if z < fill_z else max(0.0, 1 - (z - fill_z) / 3.0)
                lumps = inside * fade * (0.1 * noise.noise(p3 * 0.5 + off) + 0.05 * noise.noise(p3 * 1.1 + off)) + 0.012 * noise.noise(p3 * 2.5 + off)
            zip_ = 0.04 * (math.exp(-((z - z_zip) / 0.08) ** 2) + math.exp(-((z - z_zip - 0.28) / 0.08) ** 2))
            wr = crease(x, z) * (0.35 + 0.65 * inside) if (z > z_top - 9 or z < 4) else 0.0
            if inside == 0:                                             # the flat seals are never perfectly flat
                wr += 0.05 * noise.noise(Vector((x * 0.2, z * 0.35, 3.0)) + off)
            yf = -(film + bulge + lumps + zip_ + wr)
            yb = film + bulge * 0.96 + lumps * 0.6
            rf.append((bm.verts.new((x, yf, z)), ((sfilm + W / 2) / W, v)))
            rb.append((bm.verts.new((x, yb, z)), (1 - (sfilm + W / 2) / W, v)))
        front.append(rf); back.append(rb)

    def quad(vs4, uvs, mat, smooth=True):
        f = bm.faces.new(vs4); f.material_index = mat; f.smooth = smooth
        if uvs:
            for loop, uvv in zip(f.loops, uvs):
                loop[uvl].uv = uvv
        return f
    R, C = len(vs), len(ss)
    for j in range(R - 1):
        for i in range(C - 1):
            a, b, c, d = front[j][i], front[j][i + 1], front[j + 1][i + 1], front[j + 1][i]
            quad([a[0], b[0], c[0], d[0]], [a[1], b[1], c[1], d[1]], 0)
            a, b, c, d = back[j][i], back[j][i + 1], back[j + 1][i + 1], back[j + 1][i]
            quad([d[0], c[0], b[0], a[0]], [d[1], c[1], b[1], a[1]], 1)
    strips = []
    for i in range(C - 1):                  # bottom and top edges
        strips.append(quad([back[0][i][0], back[0][i + 1][0], front[0][i + 1][0], front[0][i][0]], None, 1, False))
        strips.append(quad([front[-1][i][0], front[-1][i + 1][0], back[-1][i + 1][0], back[-1][i][0]], None, 1, False))
    for j in range(R - 1):                  # side edges
        strips.append(quad([front[j][0][0], front[j + 1][0][0], back[j + 1][0][0], back[j][0][0]], None, 1, False))
        strips.append(quad([back[j][-1][0], back[j + 1][-1][0], front[j + 1][-1][0], front[j][-1][0]], None, 1, False))
    for f in strips:
        for e in f.edges:
            e.smooth = False
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    o = _to_object(bm, name, [mat_pouch_front(art_path, W, H, seal, top_seal), mat_pouch_back(back_hex)], smooth=None, subsurf=0)
    return o


def shadow_catcher(size=400, z=0.0):
    bpy.ops.mesh.primitive_plane_add(size=size, location=(0, 0, z))
    o = bpy.context.object; o.name = 'shadow_catcher'; o.is_shadow_catcher = True
    return o


# ---------------------------------------------------------------- placement
def bounds(obj):
    """World-space bounding box of an object and its children, after modifiers."""
    bpy.context.view_layer.update()
    deps = bpy.context.evaluated_depsgraph_get(); pts = []
    for o in [obj] + list(obj.children_recursive):
        if o.type != 'MESH' or o.hide_render:
            continue
        e = o.evaluated_get(deps); me = e.to_mesh(); mw = o.matrix_world
        pts += [mw @ v.co for v in me.vertices]; e.to_mesh_clear()
    return (Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts))),
            Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts))))


def rest_on(obj, z=0.0):
    """Lower or raise an object so its lowest point touches height z."""
    mn, _ = bounds(obj); obj.location.z += z - mn.z
    return obj


def place(obj, loc, rot=(0, 0, 0), scale=1.0):
    obj.location = loc; obj.rotation_euler = rot; obj.scale = (scale, scale, scale)
    return obj


def cloth(name='linen', size=(140, 100), res=(280, 200), folds=7, wrinkles=40, seed=0, mat=None, lift=1.0, offset=(0, 0)):
    """A linen cloth lying on the table: a few soft, long folds and many small wrinkles. A displaced grid that heaps
    can land on."""
    rnd = random.Random(seed); sx, sy = size
    F = [(rnd.uniform(-sx / 2, sx / 2), rnd.uniform(-sy / 2, sy / 2), rnd.uniform(0, math.pi), rnd.uniform(18, 50),
          rnd.uniform(1.6, 3.5), rnd.uniform(0.9, 2.0) * lift) for _ in range(folds)]
    F += [(rnd.uniform(-sx / 2, sx / 2), rnd.uniform(-sy / 2, sy / 2), rnd.uniform(0, math.pi), rnd.uniform(4, 16),
           rnd.uniform(0.45, 1.2), rnd.uniform(0.35, 0.9) * lift * rnd.choice((1, 1, -0.6))) for _ in range(wrinkles)]
    off = Vector((rnd.random() * 30, rnd.random() * 30, 0))

    def h(x, y):
        z = 0.0
        for cx, cy, a, ln, w, amp in F:
            dx, dy = x - cx, y - cy
            along = dx * math.cos(a) + dy * math.sin(a); perp = -dx * math.sin(a) + dy * math.cos(a)
            z += amp * math.exp(-(perp / w) ** 2) * math.exp(-(along / ln) ** 2)
        p = Vector((x, y, 0))
        return z + lift * (0.35 * noise.noise(p * 0.05 + off) + 0.08 * noise.noise(p * 0.2 + off))
    nx, ny = res; bm = bmesh.new()
    ox, oy = offset
    grid = [[bm.verts.new((ox - sx / 2 + sx * i / nx, oy - sy / 2 + sy * j / ny, h(-sx / 2 + sx * i / nx, -sy / 2 + sy * j / ny)))
             for i in range(nx + 1)] for j in range(ny + 1)]
    for j in range(ny):
        for i in range(nx):
            bm.faces.new((grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]))
    return _to_object(bm, name, mat or material('linen'), subsurf=1)


# ---------------------------------------------------------------- heaps: rigid-body drops with low-poly stand-ins
def variants(kind, n=6, seed=1, **kw):
    """n differently shaped copies of one dry fruit with their modifiers applied, kept out of the scene, so heaps use
    linked copies of them (Cycles then instances the geometry instead of storing every nut)."""
    out = []
    for i in range(n):
        o = NUT_BUILDERS[kind](seed=seed * 101 + i, name=f'{kind}_tmp', **kw)
        bpy.context.view_layer.update()
        me = bpy.data.meshes.new_from_object(o.evaluated_get(bpy.context.evaluated_depsgraph_get()))
        me.name = f'{kind}_{seed}_{i}'
        bpy.data.objects.remove(o)
        out.append(bpy.data.objects.new(me.name, me))
    return out


def hull_of(src, n=64):
    """Low-poly convex hull of a nut (a farthest-point sample of its own hull), a fast rigid-body stand-in."""
    if src.data.name in _HULLS:
        return _HULLS[src.data.name]
    bm = bmesh.new(); bm.from_mesh(src.data)
    res = bmesh.ops.convex_hull(bm, input=bm.verts[:])
    pts = [g.co.copy() for g in res['geom'] if isinstance(g, bmesh.types.BMVert)]; bm.free()
    c = sum(pts, Vector()) / len(pts)
    pick = [max(pts, key=lambda q: (q - c).length)]
    d = [(q - pick[0]).length for q in pts]
    while len(pick) < min(n, len(pts)):
        i = max(range(len(pts)), key=d.__getitem__); q0 = pts[i]; pick.append(q0)
        d = [min(a, (q - q0).length) for a, q in zip(d, pts)]
    hb = bmesh.new()
    for q in pick:
        hb.verts.new(q)
    bmesh.ops.convex_hull(hb, input=hb.verts[:])
    me = bpy.data.meshes.new(src.data.name + '_hull'); hb.to_mesh(me); hb.free()
    _HULLS[src.data.name] = me
    return me


def _rigid_world(frames=240):
    sc = bpy.context.scene
    if sc.rigidbody_world is None:
        bpy.ops.rigidbody.world_add()
    w = sc.rigidbody_world
    w.substeps_per_frame = 10; w.solver_iterations = 12; w.use_split_impulse = True
    w.point_cache.frame_start = 1; w.point_cache.frame_end = max(w.point_cache.frame_end, frames)
    sc.frame_start = 1; sc.frame_end = max(sc.frame_end, frames)
    return w


def collider(o, shape='MESH', friction=1.0):
    """A fixed surface the nuts land on (the cloth, a bowl, a hidden core under a heap)."""
    _rigid_world()
    with bpy.context.temp_override(object=o, active_object=o, selected_objects=[o], selected_editable_objects=[o]):
        bpy.ops.rigidbody.object_add(type='PASSIVE')
    rb = o.rigid_body; rb.collision_shape = shape; rb.friction = friction; rb.collision_margin = 0.01; rb.mesh_source = 'BASE'
    return o


def _stand_in(src, hm, loc, rot):
    p = bpy.data.objects.new('drop', hm); bpy.context.scene.collection.objects.link(p)
    p.rotation_euler = rot; p.location = loc
    _POUR.append((p, src))
    return p


def _make_active(objs):
    with bpy.context.temp_override(object=objs[0], active_object=objs[0], selected_objects=objs, selected_editable_objects=objs):
        bpy.ops.rigidbody.objects_add(type='ACTIVE')
    for p in objs:
        rb = p.rigid_body; rb.collision_shape = 'CONVEX_HULL'; rb.friction = 1.0; rb.restitution = 0.02
        rb.collision_margin = 0.015; rb.linear_damping = 0.45; rb.angular_damping = 0.85; rb.use_deactivation = True


def _extent(hm):
    """Centre of a stand-in's bounding box, its half-size in plan (any yaw) and its half-thickness."""
    xs, ys, zs = ([v.co[i] for v in hm.vertices] for i in range(3))
    c = Vector(((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, (min(zs) + max(zs)) / 2))
    return c, 0.5 * math.hypot(max(xs) - min(xs), max(ys) - min(ys)), 0.5 * (max(zs) - min(zs))


def _dome(r, radius, height):
    return height * max(0.0, math.cos(math.pi / 2 * min(1.0, r / radius))) ** 1.3


def mound(center, radius, height, color='#3A2416', name='core'):
    """The core of a heap: a low dark dome the nuts settle on, so two layers of nuts make a full pile (gaps between
    them read as deep shadow)."""
    bm = bmesh.new(); rings, segs = 40, 96
    top = bm.verts.new((center[0], center[1], center[2] + height))
    prev = [top] * segs
    for i in range(1, rings + 1):
        r = radius * 1.04 * i / rings
        ring = [bm.verts.new((center[0] + r * math.cos(2 * math.pi * j / segs), center[1] + r * math.sin(2 * math.pi * j / segs),
                              center[2] + _dome(r, radius, height) - 0.15 * (i == rings))) for j in range(segs)]
        for j in range(segs):
            q = [prev[j], ring[j], ring[(j + 1) % segs]] + ([] if i == 1 else [prev[(j + 1) % segs]])
            bm.faces.new(q if i == 1 else [prev[j], ring[j], ring[(j + 1) % segs], prev[(j + 1) % segs]])
        prev = ring
    m = M(name); m.set(Base_Color=rgb(color), Roughness=0.8)
    return _to_object(bm, name, m.mat, subsurf=0)


def _run(frames):
    sc = bpy.context.scene; _rigid_world(frames)
    sc.frame_set(1)
    for f in range(2, frames + 1):
        sc.frame_set(f)


def _freeze(objs):
    """Keep simulated nuts where they came to rest, as fixed colliders for the next round."""
    mws = [p.matrix_world.copy() for p in objs]
    for p, mw in zip(objs, mws):
        p.rigid_body.type = 'PASSIVE'; p.matrix_world = mw


def heap(sources, center, radius, height, rounds=6, seed=1, tilt=26, frames=45):
    """A heap built the way a real one forms: a low dark core over `center`, then `rounds` of nuts (random picks from
    `sources`) dropped just above the surface so far, each round settling and freezing before the next fills its gaps."""
    rnd = random.Random(seed); _rigid_world()
    core_r = radius * 0.8                                 # the outer ring of nuts rests on the cloth, hiding the core's edge
    collider(mound(center, core_r, height), shape='MESH')
    info = [(s_, hull_of(s_)) for s_ in sources]
    ext = [_extent(h) for _, h in info]
    rxy = max(e[1] for e in ext); rz = max(e[2] for e in ext); t = math.radians(tilt)
    cxy, half = 2 * rxy * 1.02, (rz + rxy * math.sin(t)) * 1.02
    tops = {}                                             # spatial hash of settled nuts: cell -> [(x, y, top z)]
    cell = lambda x, y: (int(math.floor(x / cxy)), int(math.floor(y / cxy)))
    all_objs = []
    for k in range(rounds):
        ang = rnd.uniform(0, math.pi); ox, oy = rnd.uniform(0, cxy), rnd.uniform(0, cxy); n = int(radius / cxy) + 2
        objs = []
        for i in range(-n, n + 1):
            for j in range(-n, n + 1):
                gx = (i + (0.5 if j % 2 else 0)) * cxy + ox; gy = j * cxy * 0.866 + oy
                x = gx * math.cos(ang) - gy * math.sin(ang); y = gx * math.sin(ang) + gy * math.cos(ang)
                r = math.hypot(x, y)
                if r > radius * (1.0 - 0.025 * k):
                    continue
                X, Y = center[0] + x, center[1] + y; cx_, cy_ = cell(X, Y)
                ground = center[2] + _dome(r, core_r, height)
                near = [tz for di in (-1, 0, 1) for dj in (-1, 0, 1) for (px, py, tz) in tops.get((cx_ + di, cy_ + dj), ())
                        if math.hypot(px - X, py - Y) < cxy]
                z = max([ground] + near) + half + 0.08
                src_i = rnd.randrange(len(info)); src, hm = info[src_i]; c = ext[src_i][0]
                rot = Euler((rnd.uniform(-t, t), rnd.uniform(-t, t), rnd.uniform(0, 2 * math.pi)))
                objs.append(_stand_in(src, hm, Vector((X, Y, z)) - rot.to_matrix() @ c, rot))
        if not objs:
            break
        _make_active(objs); _run(frames); _freeze(objs)
        for p in objs:
            X, Y, Z = p.matrix_world.translation
            tops.setdefault(cell(X, Y), []).append((X, Y, Z + half))
        all_objs += objs
    print(f'HEAP {len(all_objs)} nuts in {rounds} rounds')
    return all_objs


def scatter(sources, points, seed=1, z=0.0):
    """Loose pieces: one nut lying roughly flat at each (x, y), dropped from just above the cloth."""
    rnd = random.Random(seed); _rigid_world(); objs = []
    for (x, y) in points:
        src = rnd.choice(sources); hm = hull_of(src); c, rxy, rz = _extent(hm)
        rot = Euler((rnd.uniform(-0.3, 0.3), rnd.uniform(-0.3, 0.3), rnd.uniform(0, 2 * math.pi)))
        objs.append(_stand_in(src, hm, Vector((x, y, z + rz + rxy * 0.35 + 1.0)) - rot.to_matrix() @ c, rot))
    _make_active(objs)
    return objs


def settle(frames=240):
    """Run the drop, put each real nut where its stand-in came to rest, then remove the physics."""
    sc = bpy.context.scene; _rigid_world(frames); t = time.time()
    for f in range(1, frames + 1):
        sc.frame_set(f)
    placed = []
    for p, src in _POUR:
        o = src.copy(); sc.collection.objects.link(o); o.matrix_world = p.matrix_world.copy(); placed.append(o)
    for p, _ in _POUR:
        bpy.data.objects.remove(p)
    print(f'SETTLED {len(_POUR)} nuts in {time.time() - t:.0f}s')
    _POUR.clear()
    bpy.ops.rigidbody.world_remove()
    sc.frame_set(1)
    return placed


_HULLS, _POUR = {}, []
