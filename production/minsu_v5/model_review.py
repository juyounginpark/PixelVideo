"""Actual three-angle/action renders plus conservative mesh/rig diagnostics."""
import sys,math
from pathlib import Path
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R))
import bpy
from mathutils import Vector
from rain_scene import Scene
from common import config,write
from art_v5 import visibility
out=R/'review/model';out.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=Scene((270,480))
for obj in [s.garden,s.lab,s.micro,s.compare,s.closejar['root'],s.closeback]:visibility(obj,False)
from art_v5 import box
box('review_ground',(0,0,-.06),(8,8,.12),s.m['cream'])
issues=[];meshes=[o for o in s.rig.root.children_recursive if o.type=='MESH'];poseqa=[]
for o in meshes:
 if any(p.area<1e-10 or not math.isfinite(p.normal.length) for p in o.data.polygons):issues.append([o.name,'degenerate face/normal'])
 if not o.data.materials:issues.append([o.name,'missing material'])
 if o.matrix_world.determinant()<0:issues.append([o.name,'negative determinant'])
for action in config('CHARACTER_LIBRARY')['actions']:
 for p in [0,.25,.5,.75,1]:
  s.director.pose(action,p,round(p*119));bpy.context.view_layer.update()
  boots=[o for o in meshes if o.name.startswith('wide_boot')]
  low=min((o.matrix_world@Vector(v)).z for o in boots for v in o.bound_box)
  if abs(low)>.015:issues.append([action,p,'foot contact',low])
  poseqa.append(dict(action=action,progress=p,minimumBootZ=low))
 s.director.pose(action,.40,48);bpy.context.view_layer.update()
 for view,direction in [('front',(0,-6,2.3)),('side',(6,0,2.3)),('threequarter',(3,-6,2.8))]:
  aim=Vector((0,0,.84));s.camera.location=aim+Vector(direction);s.camera.rotation_euler=(aim-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=2.75
  s.s.render.filepath=str(out/f'{action}_{view}.png');bpy.ops.render.render(write_still=True)
materialqa=[]
for m in bpy.data.materials:
 if m.get('style')=='V5':
  materialqa.append(dict(name=m.name,texelsPerUnit=m.get('texels_per_world_unit'),textures=[dict(image=n.image.name,packed=bool(n.image.packed_file),interpolation=n.interpolation,projection=n.projection,blend=n.projection_blend) for n in m.node_tree.nodes if n.type=='TEX_IMAGE']))
write(out/'technical.json',dict(meshCount=len(meshes),issues=issues,poses=poseqa,materials=materialqa,limitations=['No exhaustive mesh-mesh penetration solver; intentional joint/hair overlaps require image review.','BOX world projection is used rather than authored UV islands.','Static angles do not certify every camera or motion.']))
