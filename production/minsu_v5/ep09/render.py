from pathlib import Path
import sys,os,time,argparse
J=Path(__file__).resolve().parent;sys.path.insert(0,str(J.parent));sys.path.insert(0,str(J))
import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector
from common import read,write,sha,digest
from scene import Scene

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--quality',choices=['preview','final'],default='final');ap.add_argument('--shots');ap.add_argument('--stills',action='store_true');a=ap.parse_args(sys.argv[sys.argv.index('--')+1:]);spec=read(J/'episode.json');size=[270,480] if a.quality=='preview' else [540,960]
 out=J/a.quality;out.mkdir(exist_ok=True);cache=J/'cache';cache.mkdir(exist_ok=True);lock=J.parent/'cache/render.lock';fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY);os.close(fd);begin=time.perf_counter();metrics={'renderedFrames':0,'reusedFrames':0,'nativeSize':size,'shots':{}};index={}
 try:
  bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);scene=Scene(size)
  assets=digest({str(p):sha(p) for p in [J/'scene.py',J.parent/'art_v5.py',J.parent/'character_director.py',J.parent.parent/'minsu_v2/design_system.py']})
  for shot in spec['shots']:
   if a.shots and shot['id'] not in a.shots.split(','):continue
   key=digest({'assets':assets,'scene':shot['scene'],'phase':shot['phase'],'camera':shot['cameraPlan'],'event':shot['emphasisEvent'],'nativeSize':size,'blender':bpy.app.version_string,'renderer':sha(Path(__file__))})
   folder=cache/'native'/key;folder.mkdir(parents=True,exist_ok=True);manifest=folder/'manifest.json';old=read(manifest) if manifest.exists() else {};records=old.get('frames',{});n=shot['endFrame']-shot['startFrame'];indices=sorted({0,30,60,90,119,shot['emphasisEvent']['frame']}) if a.stills else range(n);t=time.perf_counter();new=hit=0
   for f in indices:
    path=folder/f'{f:04}.png';rec=records.get(str(f))
    if rec and path.exists() and sha(path)==rec['sha256']:hit+=1;continue
    targets=scene.pose(shot,f);anchors={}
    for name,obj in targets.items():
     points=[]
     for o in [obj,*obj.children_recursive]:
      if o.type=='MESH' and not o.hide_render:points.extend(world_to_camera_view(scene.s,scene.camera,o.matrix_world@Vector(v)) for v in o.bound_box)
     if points:
      anchors[name]={'rect':[min(p.x for p in points)*1080,(1-max(p.y for p in points))*1920-140,max(p.x for p in points)*1080,(1-min(p.y for p in points))*1920-140]}
    scene.s.render.filepath=str(path);bpy.ops.render.render(write_still=True);records[str(f)]={'sha256':sha(path),'anchors':anchors};new+=1
   write(manifest,{'key':key,'frames':records});index[shot['id']]={'key':key,'folder':str(folder),'frames':records};metrics['shots'][shot['id']]={'rendered':new,'reused':hit,'seconds':time.perf_counter()-t};metrics['renderedFrames']+=new;metrics['reusedFrames']+=hit
  write(out/'native_index.json',index);metrics['wallSeconds']=time.perf_counter()-begin;write(out/'render_metrics.json',metrics)
 finally:lock.unlink(missing_ok=True)
if __name__=='__main__':main()
