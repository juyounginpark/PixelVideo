"""Native V3.1 frames with resumable, data-and-code verified checkpoints."""
import argparse,hashlib,json,sys,time
from pathlib import Path
import bpy
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R));sys.path.append(str(R.parent/'minsu_v3'));sys.path.append(str(R.parent/'minsu_v2'))
from effects import EffectDirector
from native import projected,NativeCameraEffects
from ice_scene import Scene

p=argparse.ArgumentParser();p.add_argument('--job',default=str(R/'ep06'),type=Path);p.add_argument('--frames');p.add_argument('--preflight',action='store_true');p.add_argument('--resume',action='store_true');a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
job=a.job.resolve();spec=json.loads((job/'episode.json').read_text('utf-8'));timeline=EffectDirector().compile(spec)
(job/'effects.json').write_text(json.dumps(timeline,ensure_ascii=False,indent=2),'utf-8')
dependencies=[R/x for x in ('render.py','ice_scene.py','style.py')]+[R.parent/'minsu_v3'/x for x in ('effects.py','native.py')]+[R.parent/'minsu_v2'/x for x in ('art.py','design_system.py','engine.py')]
# Selection status is external provenance; it does not affect image generation.
render_spec={k:v for k,v in spec.items() if k not in ('source',)}
digest=hashlib.sha256(json.dumps(render_spec,sort_keys=True).encode()+b''.join(x.read_bytes() for x in dependencies)).hexdigest()
manifest=job/'render_manifest.json';old=json.loads(manifest.read_text('utf-8')) if manifest.exists() else {}
valid=a.resume and old.get('sourceHash')==digest
done=set(old.get('completed',[])) if valid else set();records=json.loads((job/'anchors.json').read_text('utf-8')) if valid and (job/'anchors.json').exists() else {};motion=json.loads((job/'motion.json').read_text('utf-8')) if valid and (job/'motion.json').exists() else {}
camrecords={};folder=job/'frames';folder.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=Scene(spec);camera_fx=NativeCameraEffects();s=bpy.context.scene
frames=range(spec['durationFrames'])
if a.frames:
    frames=[]
    for segment in a.frames.split(','):
        if ':' in segment:
            begin,end=map(int,segment.split(':'));frames.extend(range(begin,end))
        else:frames.append(int(segment))
    frames=sorted(set(frames))
started=time.time()
def save(prefix=''):
    (job/(prefix+'anchors.json')).write_text(json.dumps(records),'utf-8')
    (job/(prefix+'motion.json')).write_text(json.dumps(motion),'utf-8')
    (job/(prefix+'camera_qa.json')).write_text(json.dumps(camrecords),'utf-8')
    if not prefix:manifest.write_text(json.dumps({'sourceHash':digest,'completed':sorted(done),'elapsedSeconds':time.time()-started}),'utf-8')
for f in frames:
    if f<0 or f>=spec['durationFrames']:raise ValueError('Invalid frame')
    path=folder/f'{f:04}.png'
    if not a.preflight and f in done and path.is_file():continue
    scene.pose(f);bpy.context.view_layer.update()
    camrecords[str(f)]=camera_fx.apply(s,f,timeline,scene.targets);bpy.context.view_layer.update()
    records[str(f)]={key:projected(s,obj) for key,obj in scene.targets.items() if not obj.hide_render}
    motion[str(f)]={**scene.diagnostics,'cameraLocation':list(s.camera.location),'cameraScale':s.camera.data.ortho_scale}
    if not a.preflight:
        s.render.filepath=str(path);bpy.ops.render.render(write_still=True);done.add(f)
        if f%15==0:save();print('PROGRESS',f,'done',len(done),'seconds',round(time.time()-started,1),flush=True)
save('preflight_' if a.preflight else '')
materials=[{'name':m.name,'texelsPerUnit':m.get('texels_per_world_unit'),'mapping':m.get('texture_coordinates'),'lightBands':m.get('light_bands')} for m in bpy.data.materials if m.get('style')=='V31']
(job/'native_qa.json').write_text(json.dumps({'resolution':[s.render.resolution_x,s.render.resolution_y],'percentage':s.render.resolution_percentage,'taaSamples':s.eevee.taa_render_samples,'filterSize':s.render.filter_size,'materials':materials},indent=2),'utf-8')
if not a.preflight:bpy.ops.wm.save_as_mainfile(filepath=str(job/'scene.blend'))
print('PREFLIGHT_COMPLETE' if a.preflight else 'RENDER_COMPLETE',len(frames),len(done),flush=True)
