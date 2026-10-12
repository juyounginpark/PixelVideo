"""Single-worker, content-addressed native shot cache and reusable packed asset library."""
import argparse,sys,time,os,json
from pathlib import Path
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R));sys.path.append(str(R.parent/'minsu_v2'))
import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector
from common import read,write,sha,digest,config,native_key,validation,RENDERER_VERSION
from rain_scene import Scene
from adapters import validate_adapter

def project(scene,obj):
    points=[]
    for o in [obj,*obj.children_recursive]:
        if o.type not in ('MESH','CURVE') or o.hide_render or min(o.matrix_world.to_scale())<.00001:continue
        # Conservative object bounds; no unused per-polygon masks are serialized.
        points.extend(world_to_camera_view(scene,scene.camera,o.matrix_world@Vector(v)) for v in o.bound_box)
    if not points:raise ValueError('No target geometry '+obj.name)
    rect=[min(p.x for p in points)*1080,(1-max(p.y for p in points))*1920,max(p.x for p in points)*1080,(1-min(p.y for p in points))*1920]
    return dict(rect=[round(v,2) for v in rect],point=[round((rect[0]+rect[2])/2,2),round((rect[1]+rect[3])/2,2)])

def main():
    p=argparse.ArgumentParser();p.add_argument('--job',type=Path,default=R/'ep08');p.add_argument('--quality',choices=['preview','final'],default='final');p.add_argument('--shots');p.add_argument('--stills',action='store_true');p.add_argument('--preflight',action='store_true');a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    if bpy.app.version_string!=RENDERER_VERSION:raise RuntimeError('Blender version changed; validate and update renderer cache version first')
    spec=read(a.job/'episode.json');validation(spec);validate_adapter(spec);size=config('STYLE_SPEC')['previewSize' if a.quality=='preview' else 'nativeSize'];shots=[s for s in spec['shots'] if not a.shots or s['id'] in a.shots.split(',')]
    cache=R/'cache';cache.mkdir(exist_ok=True);lock=cache/'render.lock'
    fd=os.open(str(lock),os.O_CREAT|os.O_EXCL|os.O_WRONLY);os.write(fd,str(os.getpid()).encode());os.close(fd)
    start=time.perf_counter();metrics={'quality':a.quality,'renderedFrames':0,'reusedFrames':0,'projectionSeconds':0,'renderSeconds':0,'shots':{},'errors':[]};index={}
    try:
        names=[R/'rain_scene.py',R/'art_v5.py',R.parent/'minsu_v31/style.py',R.parent/'minsu_v2/design_system.py',R.parent/'minsu_v2/art.py',R.parent/'minsu_v2/engine.py']
        assetkey=digest({**{str(x):sha(x) for x in names},'_blender':bpy.app.version_string});assets=cache/'assets'/assetkey;assets.mkdir(parents=True,exist_ok=True);blend=assets/'assets.blend'
        receipt=assets/'manifest.json'
        if receipt.exists() and blend.exists() and sha(blend)==read(receipt)['sha256']:
            bpy.ops.wm.open_mainfile(filepath=str(blend));scene=Scene.restore(read(assets/'handles.json'),size);metrics['assetCache']='HIT'
        else:
            bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);scene=Scene(size)
            write(assets/'handles.json',scene.handles());bpy.ops.wm.save_as_mainfile(filepath=str(blend));write(receipt,{'sha256':sha(blend),'assetKey':assetkey});metrics['assetCache']='MISS'
        metrics['assetSetupSeconds']=time.perf_counter()-start
        metrics['materials']=[dict(name=m.name,texelsPerUnit=m.get('texels_per_world_unit'),bands=m.get('light_bands')) for m in bpy.data.materials if m.get('style')=='V5']
        for shot in shots:
            begin=time.perf_counter();key=native_key(shot,size);folder=cache/'native'/key;folder.mkdir(parents=True,exist_ok=True);manifest=folder/'manifest.json';old=read(manifest) if manifest.exists() else {};records=old.get('frames',{});n=shot['endFrame']-shot['startFrame']
            indices=sorted(set([0,n//2,n-1,shot['emphasisEvent']['frame'],min(n-1,shot['emphasisEvent']['frame']+8)])) if a.stills else range(n)
            rendered=reused=0;preflight={}
            for f in indices:
                path=folder/f'{f:04}.png';record=records.get(str(f))
                if not a.preflight and record and path.exists() and sha(path)==record['sha256']:
                    for subject in shot['protectedSubjects']:
                        if subject in record['anchors']:
                            x0,y0,x1,y1=record['anchors'][subject]['rect']
                            if x0<20 or y0<60 or x1>1060 or y1>1810:metrics['errors'].append(dict(shot=shot['id'],frame=f,subject=subject,rect=[x0,y0,x1,y1]))
                    reused+=1;continue
                scene.pose(shot,f);bpy.context.view_layer.update();t=time.perf_counter()
                anchors={k:project(scene.s,o) for k,o in scene.targets.items() if not o.hide_render};metrics['projectionSeconds']+=time.perf_counter()-t
                for subject in shot['protectedSubjects']:
                    if subject in anchors:
                        x0,y0,x1,y1=anchors[subject]['rect']
                        if x0<20 or y0<60 or x1>1060 or y1>1810:metrics['errors'].append(dict(shot=shot['id'],frame=f,subject=subject,rect=[x0,y0,x1,y1]))
                record=dict(anchors=anchors,motion=scene.diagnostics)
                if a.preflight:preflight[str(f)]=record;continue
                scene.s.render.filepath=str(path);t=time.perf_counter();bpy.ops.render.render(write_still=True);metrics['renderSeconds']+=time.perf_counter()-t
                record['sha256']=sha(path);records[str(f)]=record;rendered+=1
                if rendered%30==0:write(manifest,dict(key=key,size=size,frames=records));print('V4_PROGRESS',shot['id'],f,n,flush=True)
            if a.preflight:write(a.job/a.quality/'preflight'/f'{shot["id"]}.json',preflight)
            else:write(manifest,dict(key=key,size=size,frames=records))
            metrics['renderedFrames']+=rendered;metrics['reusedFrames']+=reused;metrics['shots'][shot['id']]=dict(rendered=rendered,reused=reused,seconds=time.perf_counter()-begin,key=key)
            index[shot['id']]=dict(key=key,folder=str(folder),frames=n,complete=len(records)==n)
            print('V4_SHOT',shot['id'],rendered,reused,round(time.perf_counter()-begin,2),flush=True)
        target=a.job/a.quality/'native_index.json';previous=read(target) if target.exists() else {};previous.update(index);write(target,previous)
        metrics['totalSeconds']=time.perf_counter()-start;metrics['nativeSize']=size;metrics['blenderVersion']=bpy.app.version_string;metrics['samples']=scene.s.eevee.taa_render_samples
        hist=a.job/a.quality/'runs';hist.mkdir(parents=True,exist_ok=True);write(hist/f'{time.time_ns()}.json',metrics);write(a.job/a.quality/'last_render.json',metrics)
        print('V4_RENDER_RESULT',json.dumps({k:v for k,v in metrics.items() if k not in ('materials','shots','errors')}),flush=True)
        if metrics['errors']:raise RuntimeError('Character clipping: '+str(metrics['errors'][:4]))
    finally:lock.unlink(missing_ok=True)
if __name__=='__main__':main()
