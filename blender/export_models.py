# Real-time 3D models for the site (three.js, src/lib/stage3d.ts), written to public/models/:
#   pouch.glb     the 250 g pouch, low-poly; its front is plain white because each pack's art is loaded as a texture
#   art-*.webp    the four front artworks, untouched, 1024 px tall
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


def export(objs, name):
    select_only(objs, objs[0])
    path = os.path.join(MODELS, name)
    bpy.ops.export_scene.gltf(filepath=path, export_format='GLB', use_selection=True, export_apply=True, export_yup=True,
                              export_image_format='WEBP', export_image_quality=82, export_materials='EXPORT',
                              export_texcoords=True, export_normals=True, export_animations=False)
    print('EXPORTED', path, os.path.getsize(path) // 1024, 'KB')


rr.reset(); rr.render_settings(64, 64, samples=16)

# pouch: low-poly, the same shape as the pack renders (seed 3), white front for the art texture
p = rr.pouch(os.path.join(rr.WORK, 'art', 'almonds.png'), name='pouch', seed=3, res=(28, 40))
front = bpy.data.materials.new('front'); front.use_nodes = True
fb = front.node_tree.nodes['Principled BSDF']; fb.inputs['Base Color'].default_value = (1, 1, 1, 1); fb.inputs['Roughness'].default_value = 0.55
back = p.data.materials[1]; p.data.materials[0] = front
print('POUCH', len(p.data.polygons), 'faces')
export([p], 'pouch.glb')
