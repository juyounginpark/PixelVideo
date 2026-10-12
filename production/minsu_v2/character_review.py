"""Canonical character turnarounds; does not modify the episode .blend."""
import bpy,sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent;out=R/'character_review';out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'MINSU_EP04_V2.blend'))
s=bpy.context.scene;s.frame_set(1);root=bpy.data.objects['MINSU_CUTE_V2'];cam=s.camera
for obj in bpy.data.objects:
    obj.animation_data_clear()
    if obj.data and hasattr(obj.data,'animation_data_clear'):obj.data.animation_data_clear()
keep={root,*root.children_recursive,cam,bpy.data.objects['sand_ground']}
for o in bpy.data.objects:
    o.hide_render=o not in keep and o.type!='LIGHT'
root.location=(0,0,0);root.rotation_euler=(0,0,0)
for name in ('minsu_torso_pivot','minsu_head'):bpy.data.objects[name].rotation_euler=(0,0,0)
for o in root.children_recursive:
    if o.name.startswith('face_'):o.scale=(1,1,1) if o.name=='face_Neutral' else (0,0,0)
s.render.resolution_x=540;s.render.resolution_y=540;cam.data.type='ORTHO';cam.data.ortho_scale=1.94;cam.data.shift_y=0
for name,pos in [('front',(0,-4,.9)),('side',(4,0,.9)),('threequarter',(3,-4,1.6)),('back',(0,4,.9))]:
    cam.location=pos;cam.rotation_euler=(Vector((0,0,.8))-cam.location).to_track_quat('-Z','Y').to_euler()
    s.render.filepath=str(out/f'{name}.png');bpy.ops.render.render(write_still=True)
print('CHARACTER_REVIEW_RENDERED')
