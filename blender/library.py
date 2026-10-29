# Saves the reusable studio as ../blend-src/nut-library.blend: six variants of each dry fruit (one collection per kind),
# a linen swatch, the walnut bowl, the gold spoon and the almonds pouch, with the light rig and a camera.
#   blender -b --factory-startup -P blender/library.py
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rr

rr.reset()
rr.render_settings(1920, 1080, samples=128)
sc = rr.bpy.context.scene
for row, kind in enumerate(('almond', 'cashew', 'pistachio', 'raisin')):
    col = rr.bpy.data.collections.new(kind); sc.collection.children.link(col)
    for i, o in enumerate(rr.variants(kind, n=6, seed=1)):
        col.objects.link(o); o.location = (i * 4.0 - 10, row * 4.5 - 7, 1.0)
linen = rr.cloth(size=(60, 45), res=(200, 150), seed=2); linen.location.z = -0.2
rr.bowl(loc=(20, 6, 0)); rr.spoon(loc=(20, -8, 0.5))
pack = rr.pouch(os.path.join(rr.WORK, 'art', 'almonds.png'), seed=3); pack.location = (-24, 2, 0)
rr.camera((0, -70, 45), (0, 0, 3), lens=50)
rr.studio(target=(0, 0, 2), dist=2.5)
rr.save_blend('nut-library.blend')
print('SAVED', os.path.join(rr.WORK, 'nut-library.blend'))
