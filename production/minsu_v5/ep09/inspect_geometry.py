"""Measure the actual episode meshes without rendering or inventing research data."""
from pathlib import Path
import sys,math
J=Path(__file__).resolve().parent;sys.path.insert(0,str(J.parent));sys.path.insert(0,str(J));sys.path.insert(0,str(J.parent/'experiment'))
import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
from common import read,write,sha,digest
from scene import Scene
from operations import geometry_record
from state import validate_object,ExperimentState,signature

def main():
 spec=read(J/'episode.json');bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);scene=Scene([540,960]);states=[];checks=[];errors=[]
 codes={'plain':0,'white':1,'stripe':2,'check':3,'faint':4}
 for shot in spec['shots']:
  scene.pose(shot,0)
  for i,side in enumerate(['left','right']):
   # Code is an internal categorical identifier, never presented as a measured number.
   pattern=shot['scene'][side];changed=shot['phase']=='coat' and i==1
   obj={'objectId':shot['id']+'_'+side+'_coat','objectType':'HORSE_COAT' if shot['phase'] not in ['macro','patch'] else 'ENLARGED_COAT_PANEL','geometryVersion':sha(J/'scene.py'),'operation':{'type':'Compare','startFrame':0,'completeFrame':77 if changed else 102,'updateFrame':106,'parameters':{'pattern':pattern}},'observedProperties':['coatConditionCode'],'previousValue':codes['plain'] if changed else codes[pattern],'currentValue':codes[pattern],'displayUnits':'internal condition ID, not a physical measurement','definition':'plain0/white1/stripe2/check3/faint4; no model code is shown as experimental data','claimStatus':'MODEL_STATE','evidenceStatus':'SCENE_GEOMETRY'}
   # Patch demonstration deliberately remains a plain panel plus individual white dividers.
   if shot['phase']=='patch' and i==1:obj['previousValue']=obj['currentValue']=0
   validate_object(obj);state=ExperimentState(obj);scene.pose(shot,106)
   target=scene.panels[i] if shot['phase'] in ['macro','patch'] else scene.horses[i]['body'];name=target.data.materials[0].name.split('COAT_')[-1].split('.')[0]
   actual=codes[name];record=geometry_record(target);receipt={**record,'objectId':obj['objectId'],'stateSignature':signature(obj),'frame':106,'completed':True,'properties':{'coatConditionCode':actual}};state.at(106,receipt);states.append({'state':obj,'geometryReceipt':receipt,'displayedAsNumber':False})
  for f in range(120):
   targets=scene.pose(shot,f);targets['character']=scene.rig.root;row={'shot':shot['id'],'frame':f,'targets':{}}
   for name,target in targets.items():
    if target.hide_render:continue
    points=[]
    for part in [target,*target.children_recursive]:
     if part.type=='MESH' and not part.hide_render:points.extend(world_to_camera_view(scene.s,scene.camera,part.matrix_world@Vector(v)) for v in part.bound_box)
    if not points:continue
    rect=[min(v.x for v in points)*1080,(1-max(v.y for v in points))*1920-140,max(v.x for v in points)*1080,(1-min(v.y for v in points))*1920-140]
    row['targets'][name]=rect
    if rect[0]<72 or rect[1]<370 or rect[2]>1008 or rect[3]>1242:errors.append({'shot':shot['id'],'frame':f,'target':name,'rect':rect})
   # Fly model positions are scene coordinates, not empirical flight measurements.
   row['flyPositions']=[list(fly['root'].location) for fly in scene.fly];checks.append(row)
 write(J/'research/object_states.json',{'objects':states,'flyUnits':'scene coordinates; size/time simplified; not observed research tracks','animationSource':'scene.py','geometryVersion':sha(J/'scene.py')})
 write(J/'research/geometry_qa.json',{'checkedFrames':len(checks),'errors':errors,'checks':checks,'scope':'protected experiment targets, actual evaluated material and scene-coordinate paths; not a full self-intersection solver'})
 print('Geometry checks:',len(checks),'errors:',len(errors))
if __name__=='__main__':main()
