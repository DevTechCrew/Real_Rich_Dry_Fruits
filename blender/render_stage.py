# The hero stage poster: the pouch from src/data/stage.json, rendered in the studio on a transparent background with a
# soft contact shadow, so the live 3D (src/lib/stage3d.ts) takes over without a jump. The ring of photographed dry fruits
# is added by export_web.py (stage), which places each card exactly where three.js draws it at t = 0.
# Writes blend-src/out/stage/hero-stage.png (+ .json with the pouch base in pixels); export_web.py makes the WebP.
#   blender -b --factory-startup -P blender/render_stage.py [-- --draft]
import os, sys, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rr
import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Matrix, Vector

draft = '--draft' in sys.argv
spec = json.load(open(os.path.join(rr.PROJECT, 'src', 'data', 'stage.json')))
C = Matrix(((1, 0, 0), (0, 0, 1), (0, -1, 0)))           # Blender (x, y, z) -> three.js (x, z, -y)
Ci = C.transposed()
B = lambda v: Ci @ Vector(v)                              # three.js point -> Blender point


W, H = (600, 480) if draft else (1200, 960)
rr.reset(); rr.render_settings(W, H, samples=48 if draft else 192, transparent=True, exposure=0.7)
pouch = rr.pouch(os.path.join(rr.WORK, 'art', f"{spec['pouch']['slug']}.png"), seed=3)   # same shape as models/pouch.glb
pouch.location = B(spec['pouch']['position']); pouch.rotation_euler = (0, 0, math.radians(spec['pouch']['rotationY']))
rr.shadow_catcher()
cam = rr.camera(tuple(B(spec['camera']['position'])), tuple(B(spec['camera']['target'])))
cam.data.sensor_fit = 'VERTICAL'; cam.data.sensor_height = 24; cam.data.lens = 12 / math.tan(math.radians(spec['camera']['fov']) / 2)
rr.studio(target=(0, 0, 11), dist=2.4, key_shadow_only=True, hdri=None, hdri_strength=0.9)
out = os.path.join(rr.OUT, 'stage', f'hero-stage{"_draft" if draft else ""}.png')
rr.render(out)
bpy.context.view_layer.update()
base = world_to_camera_view(bpy.context.scene, cam, B(spec['pouch']['position']))
json.dump({'base': [base.x * W, (1 - base.y) * H], 'size': [W, H]}, open(out[:-4] + '.json', 'w'))
