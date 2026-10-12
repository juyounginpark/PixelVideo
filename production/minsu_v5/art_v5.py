import sys,math
from pathlib import Path
R=Path(__file__).resolve().parent
sys.path.append(str(R.parent/'minsu_v31'));sys.path.append(str(R.parent/'minsu_v2'))
import bpy
from mathutils import Vector
from style import Materials as PreviousMaterials,setup as previous_setup
from design_system import CuteCharacterFactory,linear
from art import empty,box,mesh,line

class Materials(PreviousMaterials):
 COLORS={**PreviousMaterials.COLORS,'skin':(1,.84,.67),'hair':(.31,.20,.22),'mint':(.36,.72,.63),'cream':(1,.96,.84),'navy':(.14,.13,.24),'shoe':(.32,.30,.40),'cheek':(.96,.51,.48),'floor':(.84,.81,.67),'wall':(.70,.84,.77),'wood':(.68,.48,.35),'roof':(.87,.56,.50),'leaf':(.40,.65,.47),'red':(.80,.20,.16),'water':(.74,.88,.88),'glass':(.55,.72,.74),'agar':(.96,.86,.56),'alga':(.59,.72,.29),'micro_bg':(.12,.15,.23),'metal':(.76,.76,.80),'amber':(1,.75,.30)}
 def __init__(self):
  super().__init__()
  for key,m in self.materials.items():
   m.name=m.name.replace('V31','V5');m['style']='V5'
   for n in m.node_tree.nodes:
    if n.type=='VALTORGB':
     for e,val in zip(n.color_ramp.elements,[.62,.83,1.]):e.color=(val,val,val,1)
    if n.type=='TEX_IMAGE':
     # Small triplanar tie-break blend prevents black corner triangles on bevels.
     # Texel sampling remains Closest; this does not blur the output or glyphs.
     n.projection_blend=.12;px=list(n.image.pixels);base=[linear(v) for v in self.COLORS[key]]
     for i in range(0,len(px),4):
      for c in range(3):px[i+c]=base[c]+(px[i+c]-base[c])*.35
     n.image.pixels=px;n.image.pack()
def setup(size):
 s=bpy.context.scene;previous_setup(s);s.render.resolution_x,s.render.resolution_y=size;s.render.threads_mode='FIXED';s.render.threads=4;s.render.image_settings.compression=15;s.eevee.taa_render_samples=8
 bg=next(n for n in s.world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs[0].default_value=(*[linear(c) for c in (.72,.82,.77)],1);bg.inputs[1].default_value=.8
 for o in bpy.data.objects:
  if o.type=='LIGHT':
   if 'warm_key' in o.name:o.data.energy=750;o.data.color=(1,.93,.81)
   if 'cool_fill' in o.name:o.data.energy=430;o.data.color=(.87,.94,1)
 return s
def character(m):
 rig=CuteCharacterFactory(m).minsu()
 for o in rig.root.children_recursive:
  if o.type=='MESH':
   for p in o.data.polygons:p.use_smooth=False
   for mod in o.modifiers:
    if mod.type=='BEVEL':mod.segments=1
 rig.root['model_id']='MINSU_CUTE_V21_V5_PALETTE';return rig
def visibility(o,on):
 for x in [o,*o.children_recursive]:x.hide_render=not on
def cylinder(name,loc,radius,depth,mat,parent=None,vertices=16):
 bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth,location=(0,0,0));o=bpy.context.object;o.name=name;o.parent=parent;o.location=loc;o.data.materials.append(mat);return o
def ring(name,loc,radius,mat,parent=None,width=.018):
 pts=[(loc[0]+radius*math.cos(i*math.tau/32),loc[1]+radius*math.sin(i*math.tau/32),loc[2]) for i in range(33)]
 return line(name,pts,mat,width,parent)
