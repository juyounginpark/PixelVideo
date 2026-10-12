"""Retain wet state and keep schematic moving water behind the advancing front."""
import bpy,math,sys
from pathlib import Path
R=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(R/'MINSU_THORNY_DEVIL.blend'))
s=bpy.context.scene
channels=sorted([o for o in bpy.data.objects if o.name.startswith('capillary fill segment')],key=lambda o:o.name)
beads=[o for o in bpy.data.objects if o.name.startswith('capillary moving water')]
drop=bpy.data.objects['micro water drop']
def ease(x):x=max(0,min(1,x));return x*x*(3-2*x)
comparison='--comparison' in sys.argv
frames=range(631,721) if comparison else range(361,541)
for frame in frames:
    s.frame_set(frame);t=(frame-1)/30;cut=int(t//3);u=t-cut*3
    amount=.08+ease(u/2.6)*2.3 if comparison else ((0 if u<.6 else .15+.42*ease((u-.6)/2.4)) if cut==4 else .57+ease(u/2.6)*1.8)
    for i,o in enumerate(channels):
        distance=math.hypot(o.location.x+.32,o.location.y+.32)
        dims=(.14,.075,.025) if i<88 else (.075,.14,.025)
        o.scale=dims if distance<amount else (.00001,)*3;o.keyframe_insert('scale',frame=frame)
    for o in beads:
        distance=math.hypot(o.location.x+.32,o.location.y+.32)
        o.scale=(.13,.08,.035) if (cut==5 or comparison) and distance<amount else (.00001,)*3;o.keyframe_insert('scale',frame=frame)
    drop.scale=(.2,.2,.30) if (cut==4 or comparison) and u<.8 else (.00001,)*3;drop.keyframe_insert('scale',frame=frame)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'MINSU_THORNY_DEVIL.blend'))
for frame in frames:
    s.frame_set(frame);s.render.filepath=str(R/'frames'/f'{frame:04}.png');bpy.ops.render.render(write_still=True)
print('COMPARISON_PATCH_COMPLETE' if comparison else 'CAPILLARY_PATCH_COMPLETE',flush=True)
