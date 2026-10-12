"""Explicit scene/spec/job paths, cache verification, still preview or movie frames."""
import bpy,sys,json,hashlib,time,importlib,argparse
from pathlib import Path
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R));sys.path.insert(0,str(R.parent/'minsu_v2'))
from effects import EffectDirector,held_frame
from native import NativeCameraEffects,projected
p=argparse.ArgumentParser();p.add_argument('--scene',required=True);p.add_argument('--job',required=True,type=Path);p.add_argument('--spec',type=Path);p.add_argument('--frames');p.add_argument('--resume',action='store_true');p.add_argument('--preflight',action='store_true')
a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
workspace=R.parents[1]
a.job=(workspace/a.job).resolve() if not a.job.is_absolute() else a.job.resolve()
if not a.job.is_relative_to(workspace):raise ValueError('Render job must stay in project workspace')
if a.spec and not a.spec.is_absolute():a.spec=workspace/a.spec
if a.scene not in ('sample_scene','science_scene'):raise ValueError('Unknown scene adapter')
module=importlib.import_module(a.scene)
spec=json.loads(a.spec.read_text('utf-8')) if a.spec else module.sample_spec()
timeline=EffectDirector().compile(spec)
a.job.mkdir(parents=True,exist_ok=True);folder=a.job/'frames';folder.mkdir(exist_ok=True)
(a.job/'spec.json').write_text(json.dumps(spec,ensure_ascii=False,indent=2),'utf-8');(a.job/'effects.json').write_text(json.dumps(timeline,ensure_ascii=False,indent=2),'utf-8')
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=module.Scene(spec);s=bpy.context.scene;camera=NativeCameraEffects();records={};camrecords=[];motion=[]
# Invalidate resumable frames if either data or rendering source changes.
deps=[R/'effects.py',R/'native.py',R/f'{a.scene}.py',R/'render_job.py',R.parent/'minsu_v2/design_system.py',R.parent/'minsu_v2/art.py',R.parent/'minsu_v2/engine.py']
digest=hashlib.sha256(json.dumps(spec,sort_keys=True).encode()+b''.join(x.read_bytes() for x in deps)).hexdigest()
manifest=a.job/'render_manifest.json';old=json.loads(manifest.read_text('utf-8')) if manifest.exists() else {}
done=set(old.get('completed',[])) if a.resume and old.get('sourceHash')==digest else set()
if done:
    records=json.loads((a.job/'anchors.json').read_text('utf-8'));camrecords=json.loads((a.job/'camera_qa.json').read_text('utf-8'))
frames=[int(f) for f in a.frames.split(',')] if a.frames else range(spec['durationFrames'])
started=time.time()
for frame in frames:
    path=folder/f'{frame:04}.png'
    if frame in done and path.exists():continue
    if not 0<=frame<spec['durationFrames']:raise ValueError('Frame outside timeline')
    sample=held_frame(frame,timeline);scene.pose(sample);bpy.context.view_layer.update()
    camrecords.extend(camera.apply(s,sample,timeline,scene.targets));bpy.context.view_layer.update()
    records[str(frame)]={k:projected(s,v) for k,v in scene.targets.items() if not v.hide_render}
    if hasattr(scene,'diagnostics'):motion.append({'frame':frame,**scene.diagnostics})
    if not a.preflight:
        s.render.filepath=str(path);bpy.ops.render.render(write_still=True);done.add(frame)
    if frame%30==0:print('RENDER',frame,'elapsed',round(time.time()-started,1),flush=True)
    # Save inexpensive checkpoint every 30 frames and at the end below.
    if frame%30==0 and not a.preflight:
        (a.job/'anchors.json').write_text(json.dumps(records),'utf-8');(a.job/'camera_qa.json').write_text(json.dumps(camrecords),'utf-8')
        manifest.write_text(json.dumps({'sourceHash':digest,'completed':sorted(done)}),'utf-8')
prefix='preflight_' if a.preflight else ''
(a.job/(prefix+'anchors.json')).write_text(json.dumps(records),'utf-8');(a.job/(prefix+'camera_qa.json')).write_text(json.dumps(camrecords),'utf-8')
(a.job/(prefix+'motion.json')).write_text(json.dumps(motion),'utf-8')
if not a.preflight:manifest.write_text(json.dumps({'sourceHash':digest,'completed':sorted(done),'elapsedSeconds':time.time()-started}),'utf-8')
print('RENDER_JOB_COMPLETE',len(done))
