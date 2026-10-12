import sys
from pathlib import Path
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R))
import bpy
from common import read,write,sha,digest
names=[R/'rain_scene.py',R/'art_v5.py',R.parent/'minsu_v31/style.py',R.parent/'minsu_v2/design_system.py',R.parent/'minsu_v2/art.py',R.parent/'minsu_v2/engine.py']
key=digest({**{str(x):sha(x) for x in names},'_blender':bpy.app.version_string});folder=R/'cache/assets'/key
bpy.ops.wm.open_mainfile(filepath=str(folder/'assets.blend'));bpy.context.view_layer.update();scaled=[];missing=[]
for o in bpy.data.objects:
 if o.type!='MESH':continue
 scale=o.matrix_world.to_scale();textured=[m for m in o.data.materials if m and m.get('texels_per_world_unit')]
 if textured and max(abs(abs(v)-1) for v in scale)>.01:scaled.append(dict(object=o.name,worldScale=list(scale),nominalObjectTexels=16,effectiveAxisTexels=[16/max(abs(v),.0001) for v in scale]))
 for m in o.data.materials:
  if m and m.node_tree:
   for n in m.node_tree.nodes:
    if n.type=='TEX_IMAGE' and (not n.image or not n.image.packed_file):missing.append([o.name,m.name])
write(R/'review/asset_audit.json',dict(assetKey=key,meshCount=sum(o.type=='MESH' for o in bpy.data.objects),missingPackedTextures=missing,scaledTexturedMeshes=scaled,textureDensityScope='16 texels per local object unit. Parent-scaled props are denser in world units; do not claim perfect global texel equality.',interpretation='Actual texture sampling is Closest, but small jars/cells have residual world-scale density differences. This is an editorial limitation, not a missing-file error.'))
