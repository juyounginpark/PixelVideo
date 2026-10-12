"""Save an episode-local initial frame and export the final camera plan."""
import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(R/'MINSU_THORNY_DEVIL.blend'))
s=bpy.context.scene;manifest=json.loads((R/'episode.json').read_text(encoding='utf-8'));rows=[]
for i,cut in enumerate(manifest['cuts']):
    row={'cut':i+1,'camera_family':cut['camera'],'action':cut['action'],'start':i*3,'end':i*3+3,'states':[]}
    for f in [i*90+1,(i+1)*90]:
        s.frame_set(f);cam=s.camera
        row['states'].append({'frame':f,'position':list(cam.location),'view_direction':list(cam.rotation_euler.to_quaternion()@Vector((0,0,-1))),'lens_mm':cam.data.lens,'shift_y':cam.data.shift_y})
    rows.append(row)
(R/'CAMERA_PLAN.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
s.frame_set(1);s.render.filepath=str(R/'frames'/'0001.png')
bpy.ops.wm.save_as_mainfile(filepath=str(R/'MINSU_THORNY_DEVIL.blend'))
print('EDITABLE_SCENE_HANDOFF_READY')
