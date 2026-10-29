# Test render: the four dry fruits side by side in the shared studio, to approve the look before any batch.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rr

rr.reset()
rr.render_settings(1400, 640, samples=96)
rr.sweep(mat=rr.mat_backdrop(rr.IVORY), width=120, y0=-30, depth=50, radius=22, height=50)
for kind, x, rz in (('almond', -7.2, 0.35), ('cashew', -2.4, -0.2), ('pistachio', 2.6, 0.5), ('raisin', 7.0, 0.1)):
    o = rr.NUT_BUILDERS[kind](seed=3)
    rr.place(o, (x, 0, 0), (0, 0, rz))
    rr.rest_on(o, 0.0)
rr.studio(target=(0, 0, 0.6), dist=0.55)
rr.camera((0, -22, 21), (0, 0.4, 0.2), lens=58, fstop=9)
rr.save_blend('tests/lineup.blend')
rr.render(os.path.join(rr.OUT, 'tests', 'lineup.png'))
