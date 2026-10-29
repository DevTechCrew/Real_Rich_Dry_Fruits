# The hero stage poster: the pouch and the ring of dry fruits from src/data/stage.json at t = 0, rendered in the studio
# on a transparent background with a soft contact shadow, so the live 3D (src/lib/stage3d.ts) takes over without a jump.
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


def three_euler(deg):
    """three.js Euler 'XYZ' (matrix Rx Ry Rz) as a Blender matrix in three.js axes."""
    x, y, z = (math.radians(d) for d in deg)
    return Matrix.Rotation(x, 3, 'X') @ Matrix.Rotation(y, 3, 'Y') @ Matrix.Rotation(z, 3, 'Z')


W, H = (600, 480) if draft else (1200, 960)
rr.reset(); rr.render_settings(W, H, samples=48 if draft else 192, transparent=True, exposure=0.7)
pouch = rr.pouch(os.path.join(rr.WORK, 'art', f"{spec['pouch']['slug']}.png"), seed=3)   # same shape as models/pouch.glb
pouch.location = B(spec['pouch']['position']); pouch.rotation_euler = (0, 0, math.radians(spec['pouch']['rotationY']))
rr.shadow_catcher()
ring = spec['ring']; tilt = math.radians(ring['tilt'])
for n in spec['nuts']:
    o = rr.NUT_BUILDERS[n['kind']](seed=7)                # same shape as models/nuts.glb, centred the same way
    mn, mx = rr.bounds(o); o.data.transform(Matrix.Translation(-(mn + mx) / 2))
    a = math.radians(n['a'])
    p = (n['r'] * math.cos(a), ring['y'] + n['h'] - n['r'] * math.sin(a) * math.sin(tilt), n['r'] * math.sin(a) * math.cos(tilt))
    o.matrix_world = Matrix.Translation(B(p)) @ (Ci @ three_euler(n['rot']) @ C).to_4x4() @ Matrix.Scale(n['scale'], 4)
cam = rr.camera(tuple(B(spec['camera']['position'])), tuple(B(spec['camera']['target'])))
cam.data.sensor_fit = 'VERTICAL'; cam.data.sensor_height = 24; cam.data.lens = 12 / math.tan(math.radians(spec['camera']['fov']) / 2)
rr.studio(target=(0, 0, 11), dist=2.4, key_shadow_only=True, hdri=None, hdri_strength=0.9)
out = os.path.join(rr.OUT, 'stage', f'hero-stage{"_draft" if draft else ""}.png')
rr.render(out)
bpy.context.view_layer.update()
base = world_to_camera_view(bpy.context.scene, cam, B(spec['pouch']['position']))
json.dump({'base': [base.x * W, (1 - base.y) * H], 'size': [W, H]}, open(out[:-4] + '.json', 'w'))
