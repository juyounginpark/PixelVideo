"""Make contact and collection precede the drinking action in the first shot."""
import bpy,math
from pathlib import Path
R=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(R/'MINSU_THORNY_DEVIL.blend'))
s=bpy.context.scene;jaw=bpy.data.objects['drinking jaw']
route=sorted([o for o in bpy.data.objects if o.name.startswith('external water highlight')],key=lambda o:o.name)
def ease(x):x=max(0,min(1,x));return x*x*(3-2*x)
for frame in range(1,91):
    s.frame_set(frame);u=(frame-1)/30
    jaw.rotation_euler.x=.03 if u<1.4 else .07+.13*max(0,math.sin((u-1.4)*math.tau*1.7))
    jaw.keyframe_insert('rotation_euler',frame=frame)
    amount=9*ease((u-.35)/1.05)
    for i,o in enumerate(route):
        o.scale=(.026,.032,.017) if i<amount else (.00001,)*3;o.keyframe_insert('scale',frame=frame)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'MINSU_THORNY_DEVIL.blend'))
for frame in range(1,91):
    s.frame_set(frame);s.render.filepath=str(R/'frames'/f'{frame:04}.png');bpy.ops.render.render(write_still=True)
print('HOOK_SEQUENCE_PATCH_COMPLETE',flush=True)
