"""Apply the reviewed hook-only mesh change after the running full render finishes."""
import bpy,sys,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R))
from art import droplet
blend=R/'MINSU_EP04_V2.blend';oldhash=hashlib.sha256(blend.read_bytes()).hexdigest()
manifest=json.loads((R/'render_manifest.json').read_text('utf-8'))
assert manifest['sceneHash']==oldhash and len(manifest['completed'])==1080,'Finish baseline render before selective patch'
bpy.ops.wm.open_mainfile(filepath=str(blend));o=bpy.data.objects['free_water_drop']
tmp=droplet('replacement_drop',o.location,o.data.materials[0]);o.data=tmp.data
for mod in list(o.modifiers):o.modifiers.remove(mod)
bpy.data.objects.remove(tmp,do_unlink=True)
bpy.context.scene.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(blend))
manifest['previousSceneHash']=oldhash;manifest['sceneHash']=hashlib.sha256(blend.read_bytes()).hexdigest()
manifest['selectivePatch']={'objects':['free_water_drop'],'shots':['SHOT_01'],'reason':'Mesh is visible only in frames 1..18. Only shot 1 invalidated; no transforms, camera or other objects changed.'}
manifest['completed']=[f for f in manifest['completed'] if f>54]
(R/'render_manifest.json').write_text(json.dumps(manifest),'utf-8')
print('HOOK_PATCH_READY')
