import bpy,sys
from pathlib import Path
R=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(R/'MINSU_EP04_V2.blend'))
s=bpy.context.scene;s.frame_set(68);s.compositing_node_group=None
s.render.filepath=str(R/'raw_compare.png');bpy.ops.render.render(write_still=True)
