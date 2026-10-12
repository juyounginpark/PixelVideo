from pathlib import Path
import sys,json,time,os,importlib.util
J=Path(__file__).resolve().parent;sys.path.insert(0,str(J));sys.path.insert(0,str(J.parent/'minsu_v5'))
import bpy
from common import sha,digest,write
sys.path.insert(0,str(J))
from directors import validate_story
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector
job=Path(sys.argv[sys.argv.index('--')+1]).resolve();spec=json.loads((job/'episode.json').read_text(encoding='utf8'));validate_story(spec['shots'])
module=importlib.util.spec_from_file_location('episode_adapter',job/'scene.py');adapter=importlib.util.module_from_spec(module);module.loader.exec_module(adapter)
selected=sys.argv[sys.argv.index('--shots')+1].split(',') if '--shots' in sys.argv else None
lock=J.parent/'minsu_v5/cache/render.lock';fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY);os.close(fd);begin=time.perf_counter();index=json.loads((job/'native_index.json').read_text('utf8')) if selected and (job/'native_index.json').exists() else {};metrics=[]
try:
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);scene=adapter.Scene([540,960])
 for shot in spec['shots']:
  if selected and shot['id'] not in selected:continue
  key=digest({'scene':shot['scene'],'camera':shot['cameraPlan'],'event':shot.get('emphasisEvent'),'start':shot['startFrame'],'end':shot['endFrame'],'adapter':sha(job/'scene.py'),'art':sha(J.parent/'minsu_v5/art_v5.py'),'rig':sha(J.parent/'minsu_v5/character_director.py'),'renderer':sha(Path(__file__)),'blender':bpy.app.version_string,'native':[540,960]})
  folder=job/'cache/native'/key;folder.mkdir(parents=True,exist_ok=True);manifest=folder/'manifest.json';old=json.loads(manifest.read_text()) if manifest.exists() else {};records=old.get('frames',{});new=hit=0;t=time.perf_counter()
  indices=[shot['startFrame']+v for v in [0,45,90]] if '--stills' in sys.argv else range(shot['startFrame'],shot['endFrame'])
  for f in indices:
   path=folder/f'{f:04}.png';rec=records.get(str(f))
   if rec and path.exists() and sha(path)==rec['sha256']:hit+=1;continue
   targets=scene.pose(shot,f);bpy.context.view_layer.update();anchors={}
   for name,obj in targets.items():
    points=[world_to_camera_view(scene.s,scene.camera,o.matrix_world@Vector(v)) for o in [obj,*obj.children_recursive] if o.type=='MESH' and not o.hide_render for v in o.bound_box]
    if points:anchors[name]=[min(p.x for p in points),1-max(p.y for p in points),max(p.x for p in points),1-min(p.y for p in points)]
   scene.s.render.filepath=str(path);bpy.ops.render.render(write_still=True);records[str(f)]={'sha256':sha(path),'anchors':anchors};new+=1
   if f%30==0:write(manifest,{'key':key,'frames':records})
  write(manifest,{'key':key,'frames':records});index[shot['id']]={'folder':str(folder),'key':key,'frames':records};metrics.append({'shot':shot['id'],'newFrames':new,'cacheHits':hit,'seconds':time.perf_counter()-t});write(job/'native_index.json',index)
 write(job/'render_metrics.json',{'shots':metrics,'wallSeconds':time.perf_counter()-begin,'workers':1,'native':[540,960]})
finally:lock.unlink(missing_ok=True)
