from pathlib import Path
import sys,json,time,math
J=Path(__file__).resolve().parent;V=J.parent/'minsu_v5';sys.path.insert(0,str(V/'ep09'));sys.path.insert(0,str(V))
import bpy
from mathutils import Vector
from scene import Scene
from art_v5 import visibility
from common import sha,digest,write
out=J/'sample/native';out.mkdir(parents=True,exist_ok=True)
spec=json.loads((V/'ep09/episode.json').read_text(encoding='utf8'));key=digest([sha(Path(__file__)),sha(V/'ep09/scene.py'),'540x960'])
manifest=out/'manifest.json';old=json.loads(manifest.read_text()) if manifest.exists() else {};records=old.get('frames',{}) if old.get('key')==key else {};start=time.perf_counter();new=hit=0
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);s=Scene([540,960])
for f in range(300):
 file=out/f'{f:04}.png'
 if str(f) in records and file.exists() and sha(file)==records[str(f)]:hit+=1;continue
 macro=90<=f<210
 if macro:shot=spec['shots'][3];local=min(119,f-90)
 else:shot=spec['shots'][0];local=f if f<90 else 90+f-210
 s.pose(shot,local)
 if not macro:
  visibility(s.horses[0]['root'],False);visibility(s.fly[0]['root'],False);visibility(s.fly[2]['root'],False)
  s.horses[1]['root'].location=(.45,.15,0);s.fly[1]['root'].location.x-=.65
  s.fly[1]['root'].location.x=min(.9,s.fly[1]['root'].location.x)
  s.rig.root.location=(-.6,-.6,0);s.rig.root.scale=(.9,)*3
  aim=Vector((.15,0,1.15));direction=Vector((0,-8,4.5));scale=4.8
 else:
  for i,panel in enumerate(s.panels):panel.location.x=(-.65 if i==0 else .65)
  for i,fly in enumerate(s.fly[:2]):fly['root'].location.x+=(.45 if i==0 else -.45)
  aim=Vector((0,0,1.2));direction=Vector((0,-8,1.8));scale=5.8
 s.camera.location=aim+direction;s.camera.rotation_euler=(aim-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=scale
 bpy.context.view_layer.update();s.s.render.filepath=str(file);bpy.ops.render.render(write_still=True);records[str(f)]=sha(file);new+=1
 if f%30==0:write(manifest,{'key':key,'frames':records})
write(manifest,{'key':key,'frames':records});write(out.parent/'render_metrics.json',{'newFrames':new,'cacheHits':hit,'seconds':time.perf_counter()-start,'native':[540,960],'workers':1})
