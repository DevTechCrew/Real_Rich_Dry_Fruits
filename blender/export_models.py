# Real-time 3D models for the site (three.js, src/lib/stage3d.ts), written to public/models/:
#   pouch.glb     the 250 g pouch, low-poly; its front is plain white because each pack's art is loaded as a texture
#   art-*.webp    the four front artworks, untouched, 1024 px tall
#   nuts.glb      one almond, cashew, pistachio and raisin, decimated, with the procedural skin baked into textures
#   blender -b --factory-startup -P blender/export_models.py
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rr
import bpy

MODELS = os.path.join(rr.PROJECT, 'public', 'models')
BAKE = os.path.join(rr.WORK, 'bake')
os.makedirs(MODELS, exist_ok=True); os.makedirs(BAKE, exist_ok=True)
ROUGH = {'almond': 0.5, 'cashew': 0.5, 'pistachio': 0.6, 'raisin': 0.38}


def select_only(objs, active):
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = active


def apply_modifiers(o):
    bpy.context.view_layer.update()
    me = bpy.data.meshes.new_from_object(o.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    old = o.data; o.modifiers.clear(); o.data = me; bpy.data.meshes.remove(old)
    return o


def to_emission(mat, input_name):
    """Send one Principled input to an emission shader so an EMIT bake records it exactly; returns an undo function."""
    nt = mat.node_tree
    bsdf = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED'); out = next(n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL')
    em = nt.nodes.new('ShaderNodeEmission'); src = bsdf.inputs[input_name]
    if src.links:
        nt.links.new(src.links[0].from_socket, em.inputs['Color'])
    else:
        v = src.default_value
        em.inputs['Color'].default_value = (v, v, v, 1) if isinstance(v, float) else tuple(v)
    old = out.inputs['Surface'].links[0].from_socket
    nt.links.new(em.outputs['Emission'], out.inputs['Surface'])

    def undo():
        nt.links.new(old, out.inputs['Surface']); nt.nodes.remove(em)
    return undo


def baked_nut(kind, seed=7, tris=1500, size=256):
    hi = apply_modifiers(rr.NUT_BUILDERS[kind](seed=seed, name=f'{kind}_hi'))
    lo = bpy.data.objects.new(kind, hi.data.copy()); bpy.context.scene.collection.objects.link(lo)
    dec = lo.modifiers.new('dec', 'DECIMATE'); dec.ratio = min(1.0, tris / max(1, sum(len(p.vertices) - 2 for p in lo.data.polygons)))
    apply_modifiers(lo)
    for p in lo.data.polygons:
        p.use_smooth = True
    select_only([lo], lo)
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.02)
    bpy.ops.object.mode_set(mode='OBJECT')

    col = bpy.data.images.new(f'{kind}_color', size, size); nrm = bpy.data.images.new(f'{kind}_normal', size, size)
    nrm.colorspace_settings.name = 'Non-Color'
    m = bpy.data.materials.new(f'{kind}'); m.use_nodes = True; nt = m.node_tree
    bsdf = nt.nodes['Principled BSDF']; tex = nt.nodes.new('ShaderNodeTexImage'); nt.nodes.active = tex
    lo.data.materials.clear(); lo.data.materials.append(m)
    select_only([hi, lo], lo)
    sc = bpy.context.scene; sc.cycles.samples = 16
    kw = dict(use_selected_to_active=True, cage_extrusion=0.05, max_ray_distance=0.25, margin=6, use_clear=True)
    tex.image = nrm
    bpy.ops.object.bake(type='NORMAL', normal_space='TANGENT', **kw)
    undos = [to_emission(mt, 'Base Color') for mt in hi.data.materials]
    tex.image = col
    bpy.ops.object.bake(type='EMIT', **kw)
    for u in undos:
        u()
    for img in (col, nrm):
        img.filepath_raw = os.path.join(BAKE, f'{img.name}.png'); img.file_format = 'PNG'; img.save()
    # final real-time material: baked colour + tangent normal map, one roughness value
    tex.image = col; nt.links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
    nm_tex = nt.nodes.new('ShaderNodeTexImage'); nm_tex.image = nrm
    nmap = nt.nodes.new('ShaderNodeNormalMap'); nt.links.new(nm_tex.outputs['Color'], nmap.inputs['Color'])
    nt.links.new(nmap.outputs['Normal'], bsdf.inputs['Normal'])
    bsdf.inputs['Roughness'].default_value = ROUGH[kind]
    bpy.data.objects.remove(hi)
    print('BAKED', kind, len(lo.data.polygons), 'faces')
    return lo


def export(objs, name):
    select_only(objs, objs[0])
    path = os.path.join(MODELS, name)
    bpy.ops.export_scene.gltf(filepath=path, export_format='GLB', use_selection=True, export_apply=True, export_yup=True,
                              export_image_format='WEBP', export_image_quality=82, export_materials='EXPORT',
                              export_texcoords=True, export_normals=True, export_animations=False)
    print('EXPORTED', path, os.path.getsize(path) // 1024, 'KB')


rr.reset(); rr.render_settings(64, 64, samples=16)

# nuts: one of each, centred on the origin
nuts = []
for kind in ('almond', 'cashew', 'pistachio', 'raisin'):
    o = baked_nut(kind)
    mn, mx = rr.bounds(o); c = (mn + mx) / 2
    o.data.transform(__import__('mathutils').Matrix.Translation(-c))
    nuts.append(o)
export(nuts, 'nuts.glb')
for o in nuts:
    o.hide_set(True)

# pouch: low-poly, the same shape as the pack renders (seed 3), white front for the art texture
p = rr.pouch(os.path.join(rr.WORK, 'art', 'almonds.png'), name='pouch', seed=3, res=(28, 40))
front = bpy.data.materials.new('front'); front.use_nodes = True
fb = front.node_tree.nodes['Principled BSDF']; fb.inputs['Base Color'].default_value = (1, 1, 1, 1); fb.inputs['Roughness'].default_value = 0.55
back = p.data.materials[1]; p.data.materials[0] = front
print('POUCH', len(p.data.polygons), 'faces')
export([p], 'pouch.glb')
