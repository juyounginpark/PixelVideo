"""Only still design sheets and pose diagnostics. No episode or video generation."""
import bpy, sys, json
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R))
from art import box
from design_system import ToonMaterialLibrary,CuteCharacterFactory,PixelStylePipeline,StudioLighting,TargetedActing,FramingCamera,WorldRegistry

bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;m=ToonMaterialLibrary();rig=CuteCharacterFactory(m).minsu()
box('asset_review_floor',(0,0,-.065),(200,200,.1),m['studio'])
StudioLighting().configure();PixelStylePipeline().configure(s)
bpy.ops.object.camera_add();cam=bpy.context.object;s.camera=cam
out=R/'design_revision';out.mkdir(exist_ok=True)
acting=TargetedActing(rig);camera=FramingCamera();records=[]
bounds=((- .51,-.39,-.005),(.51,.39,1.51))
poses=[('neutral','Inspect',0,(0,-1,.12)),('curious','Inspect',.55,(.65,-1,.18)),
       ('surprise','Surprise',.6,(-.55,-1,.15)),('happy','Understand',.65,(.15,-1,.10)),
       ('side','Inspect',0,(1,-.12,.12)),('back','Inspect',0,(.2,1,.12))]
for name,action,progress,direction in poses:
    acting.apply(action,progress,(.4,-1.5,.95));camera.frame(cam,bounds,'MEDIUM',direction)
    bpy.context.view_layer.update()
    s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
    head_world=rig.head.matrix_world.translation;face=world_to_camera_view(s,cam,head_world)
    records.append({'name':name,'faceNormalized':[face.x,face.y,face.z],
                    'model':rig.root['model_id'],'camera':list(cam.location)})

# Pose evaluation without animation rendering: determinism and actual joints.
joint_samples=[]
for progress in (0,.12,.35,.70,1):
    acting.apply('Surprise',progress,(.4,-1.5,.95))
    joint_samples.append({'progress':progress,'torso':list(rig.body.rotation_euler),
                          'elbow':list(rig.elbows[0].rotation_euler),'head':list(rig.head.rotation_euler)})
acting.apply('Surprise',.35,(.4,-1.5,.95));a=list(rig.elbows[0].rotation_euler)
acting.apply('Inspect',.9,(-1,-1,0));acting.apply('Surprise',.35,(.4,-1.5,.95))
assert a==list(rig.elbows[0].rotation_euler),'Poses depend on evaluation order'
assert len({tuple(p['elbow']) for p in joint_samples})>1
assert all(0<r['faceNormalized'][0]<1 and 0<r['faceNormalized'][1]<1 for r in records)
missing_rejected=False
try:WorldRegistry().build('missing')
except ValueError:missing_rejected=True
assert missing_rejected
textures=[n for mat in m.materials.values() for n in mat.node_tree.nodes if n.type=='TEX_IMAGE']
assert textures and all(n.interpolation=='Closest' and n.projection_blend>0 for n in textures)
qa={'mode':'STILLS_ONLY','topicSelected':False,'videoCreated':False,'nativeSize':[540,960],
    'renderEngine':s.render.engine,'threeBandMaterials':len(m.materials),'textures':len(textures),
    'nearestTextures':True,'projectionBlendNonzero':True,'deterministicPoses':True,
    'elbowChanges':True,'unknownWorldRejected':missing_rejected,'poses':joint_samples,'stills':records,
    'limits':['No motion playback quality validation','No new episode or source selection','Review studio is not a production environment']}
(out/'design_qa.json').write_text(json.dumps(qa,indent=2),'utf-8')
print('DESIGN_STILLS_AND_POSE_CHECKS_COMPLETE')
