"""Expose the skin slab in the cross-section shot; desert floor must not occlude it."""
import bpy
from pathlib import Path
R=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(R/'MINSU_THORNY_DEVIL.blend'))
s=bpy.context.scene;floor=bpy.data.objects['desert floor']
for f,value in [(1,False),(540,False),(541,True),(630,True),(631,False),(1080,False)]:
    floor.hide_render=value;floor.keyframe_insert('hide_render',frame=f)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'MINSU_THORNY_DEVIL.blend'))
for f in range(541,631):
    s.frame_set(f);s.render.filepath=str(R/'frames'/f'{f:04}.png');bpy.ops.render.render(write_still=True)
print('CROSS_SECTION_PATCH_COMPLETE',flush=True)
