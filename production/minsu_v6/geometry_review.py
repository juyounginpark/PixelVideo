from pathlib import Path
import sys,json,importlib.util
J=Path(__file__).resolve().parent;job=J/'ep10';sys.path.insert(0,str(J.parent/'minsu_v5'))
import bpy
from mathutils import Vector
module=importlib.util.spec_from_file_location('cup_review',job/'scene.py');a=importlib.util.module_from_spec(module);module.loader.exec_module(a);bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);s=a.Scene([540,960]);spec=json.loads((job/'episode.json').read_text('utf8'));rows=[]
for f in [0,24,40,119,150,190,210,229,240,360,479,480,600,719,720,745,840,895,918,959]:
 shot=next(x for x in spec['shots'] if x['startFrame']<=f<x['endFrame']);s.pose(shot,f);bpy.context.view_layer.update()
 boot=[o for o in s.rig.root.children_recursive if o.type=='MESH' and o.name.startswith('wide_boot')];low=min((o.matrix_world@Vector(v)).z for o in boot for v in o.bound_box)
 rows.append({'frame':f,'phase':shot['scene']['phase'],'lamp':list(s.lamp.location),'cup':list(s.cup.location),'cupRotation':list(s.cup.rotation_euler),'cupMaterial':s.parts[0].data.materials[0].name,'actorLocation':list(s.rig.root.location),'bootMinimumZ':low,'cameraScale':s.camera.data.ortho_scale})
before=next(r for r in rows if r['frame']==479);after=next(r for r in rows if r['frame']==720);continuity={k:before[k]==after[k] for k in ['lamp','cup','cupRotation','cupMaterial','actorLocation']}
zeroNormals=[o.name for o in bpy.data.objects if o.type=='MESH' and any(p.normal.length<.99 for p in o.data.polygons)];invalid=[o.name for o in bpy.data.objects if o.type=='MESH' and o.data.validate(verbose=False)]
report={'samples':rows,'continuity':continuity,'degenerateNormals':zeroNormals,'invalidMeshes':invalid,'limits':'This is sampled mesh/transform validation, not a general self-intersection, UV or joint collision solver.'};(job/'research/geometry_qa.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps({'continuity':continuity,'minimumBootZ':min(r['bootMinimumZ'] for r in rows),'invalid':invalid}))
