"""Change observer framing, preserving native animal and human animation."""
import bpy,sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(R/'MINSU_THORNY_DEVIL.blend'))
s=bpy.context.scene;cam=s.camera
for frame in range(91,181):
    s.frame_set(frame);u=(frame-91)/90
    cam.location=Vector((-.43,-.63,.34)).lerp(Vector((-.40,-.58,.32)),u)
    cam.rotation_euler=(Vector((0,-.07,.035))-cam.location).to_track_quat('-Z','Y').to_euler()
    cam.data.lens=42;cam.data.shift_y=-.10
    cam.keyframe_insert('location',frame=frame);cam.keyframe_insert('rotation_euler',frame=frame)
    cam.data.keyframe_insert('lens',frame=frame);cam.data.keyframe_insert('shift_y',frame=frame)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'MINSU_THORNY_DEVIL.blend'))
preview='--preview' in sys.argv
frames=[140] if preview else range(91,181)
dest=R/'observation_preview' if preview else R/'frames';dest.mkdir(exist_ok=True)
for frame in frames:
    s.frame_set(frame);s.render.filepath=str(dest/f'{frame:04}.png');bpy.ops.render.render(write_still=True)
print('OBSERVATION_PATCH_COMPLETE',flush=True)
