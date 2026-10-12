"""Measure native object changes separately from camera movement."""
import bpy,json,math
from pathlib import Path
R=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(R/'MINSU_EP04_V2.blend'))
s=bpy.context.scene
def sample(frame,name,prop='rotation_euler'):
    s.frame_set(frame);return list(getattr(bpy.data.objects[name],prop))
def active(frame,prefix):
    s.frame_set(frame);return sum(min(o.scale)>.5 for o in bpy.data.objects if o.name.startswith(prefix))
drop1=sample(1,'free_water_drop','location')[2];drop17=sample(17,'free_water_drop','location')[2]
head60=sample(60,'minsu_head');head100=sample(100,'minsu_head')
jaw0=sample(706,'thorny_jaw')[0];jaw1=sample(712,'thorny_jaw')[0]
checks={'dropFalls':drop1>drop17+.1,'hookWetFrontGrows':active(18,'external_wet_route')<active(50,'external_wet_route'),
        'characterGazeChanges':max(abs(a-b) for a,b in zip(head60,head100))>.05,
        'capillaryFrontGrows':active(390,'wet_channel_segment')<active(470,'wet_channel_segment'),
        'bodyRouteGrows':active(520,'external_wet_route')<active(625,'external_wet_route'),
        'jawMovesAfterArrival':abs(jaw1-jaw0)>.07}
meshes={o.name:o.data.as_pointer() for o in bpy.data.objects if o.type=='MESH'}
for f in (1,68,280,470,680,820,1060):
    s.frame_set(f)
    assert all(bpy.data.objects[n].data.as_pointer()==ptr for n,ptr in meshes.items())
report={'checks':checks,'dropZ':[drop1,drop17],'gazeEuler':[head60,head100],
        'jawEulerX':[jaw0,jaw1],'singleCanonicalModelIds':[o.get('model_id') for o in bpy.data.objects if o.get('model_id')],
        'geometryIdentityStable':True,'notes':'Object transforms and visibility are tested, not inferred from camera/image changes. Natural acting and comprehension still require visual review.'}
(R/'MOTION_QA.json').write_text(json.dumps(report,indent=2),'utf-8')
if not all(checks.values()):raise RuntimeError(report)
print('MOTION_QA_PASSED')
