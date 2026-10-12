"""Inspect baked scene state separately from codec checks."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(R/'MINSU_THORNY_DEVIL.blend'))
s=bpy.context.scene
jaw=bpy.data.objects['drinking jaw'];head=bpy.data.objects['lizard head'];animal=bpy.data.objects['THORNY_DEVIL']
foot=bpy.data.objects['lizard foot'];water=bpy.data.objects['shallow puddle']
channels=[o for o in bpy.data.objects if o.name.startswith('capillary fill segment')]
routes=[o for o in bpy.data.objects if o.name.startswith('external water highlight')]
def point(o):
    v=world_to_camera_view(s,s.camera,o.matrix_world.translation)
    return [round(v.x*1080,1),round(432+(1-v.y)*1488,1)]
rows=[]
for f in [1,16,30,45,60,89,91,110,140,179,390,420,450,480,510,540,570,600,630,660,690,720,740,760,779,810,825,840,855,869,930,960,990,1010,1050,1080]:
    s.frame_set(f)
    rows.append({'frame':f,'time':round((f-1)/30,3),'animal_y':round(animal.location.y,5),'jaw_rotation_x':round(jaw.rotation_euler.x,5),'mouth_screen':point(jaw),'foot_screen':point(foot),'mouth_world_z':round(jaw.matrix_world.translation.z,5),'surface_z':round(water.location.z+water.dimensions.z/2,5),'visible_channel_segments':sum(o.scale.x>.0001 for o in channels),'visible_route_segments':sum(o.scale.x>.0001 for o in routes)})
assert max(r['jaw_rotation_x'] for r in rows if 27<=r['time']<30)-min(r['jaw_rotation_x'] for r in rows if 27<=r['time']<30)>.07
assert all(r['mouth_world_z']>r['surface_z'] for r in rows if r['time']<3)
assert max(r['visible_channel_segments'] for r in rows)-min(r['visible_channel_segments'] for r in rows)>40
(R/'MOTION_AUDIT.json').write_text(json.dumps({'method':'evaluated baked transforms, not a viewer retention test','samples':rows},indent=2),encoding='utf-8')
print('MOTION_STATE_AUDIT_PASSED',flush=True)
