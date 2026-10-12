"""Resume or partially render an approved native scene, with content-hash cache."""
import bpy, sys, json, hashlib, time
from pathlib import Path
R=Path(__file__).resolve().parent
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
blend=R/'MINSU_EP04_V2.blend';bpy.ops.wm.open_mainfile(filepath=str(blend))
digest=hashlib.sha256(blend.read_bytes()).hexdigest();manifest=R/'render_manifest.json'
cache=json.loads(manifest.read_text('utf-8')) if manifest.exists() else {}
if cache.get('sceneHash')!=digest:cache={'sceneHash':digest,'completed':[]}
done=set(cache['completed']);frames=range(1,1081)
if '--frames' in args:frames=[int(f) for f in args[args.index('--frames')+1].split(',')]
if '--shot' in args:
    spec=json.loads((R/'episode.json').read_text('utf-8'));shot=next(s for s in spec['shots'] if s['shotId']==args[args.index('--shot')+1])
    frames=range(round(shot['startTime']*30)+1,round(shot['endTime']*30)+1)
start=time.time();s=bpy.context.scene
for f in frames:
    path=R/'frames'/f'{f:04}.png'
    if f in done and path.exists() and '--force' not in args:continue
    s.frame_set(f);s.render.filepath=str(path);bpy.ops.render.render(write_still=True)
    done.add(f);cache['completed']=sorted(done);manifest.write_text(json.dumps(cache),'utf-8')
    if f%30==0:print(f'PROGRESS {f}/1080 elapsed={time.time()-start:.1f}',flush=True)
print('RENDER_COMPLETE',len(done),flush=True)
