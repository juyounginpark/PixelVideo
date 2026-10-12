"""V4 keeps the existing authored character/material vocabulary, with one palette."""
import sys,math
from pathlib import Path
R=Path(__file__).resolve().parent
sys.path.append(str(R.parent/'minsu_v31'));sys.path.append(str(R.parent/'minsu_v2'))
import bpy
from mathutils import Vector
from style import Materials as PreviousMaterials,setup as previous_setup
from design_system import CuteCharacterFactory,linear
from art import box,empty,line,mesh

class Materials(PreviousMaterials):
    COLORS={**PreviousMaterials.COLORS,'wall':(.12,.17,.30),'floor':(.41,.53,.61),'brass':(.94,.66,.28),'mint':(.26,.72,.63),'skin':(1,.83,.64),'hair':(.19,.12,.13),'navy':(.055,.095,.18),'cream':(1,.95,.82),'shoe':(.16,.21,.29),'star_gold':(1,.83,.38),'star_cold':(.47,.81,.91),'halo':(.38,.91,.72),'dim':(.18,.31,.44),'track':(.31,.47,.60)}
    def __init__(self):
        super().__init__()
        for key in ('star_gold','star_cold','halo','track','dim'):
            m=self.materials[key];n=m.node_tree.nodes;n.clear();em=n.new('ShaderNodeEmission');em.inputs[0].default_value=(*[linear(c) for c in self.COLORS[key]],1)
            out=n.new('ShaderNodeOutputMaterial');m.node_tree.links.new(em.outputs[0],out.inputs[0])
        for m in self.materials.values():m.name=m.name.replace('V31','V4');m['style']='V4'
def setup(size):
    s=bpy.context.scene;previous_setup(s);s.render.resolution_x,s.render.resolution_y=size
    s.render.threads_mode='FIXED';s.render.threads=4;s.render.image_settings.compression=15
    s.eevee.taa_render_samples=8
    for o in bpy.data.objects:
        if o.type=='LIGHT':
            if 'cool_fill' in o.name:o.data.energy=460;o.data.color=(.78,.89,1)
            if 'warm_key' in o.name:o.data.energy=800
    return s
def character(m):
    r=CuteCharacterFactory(m).minsu();r.root['model_id']='MINSU_CUTE_V21_REUSED'
    return r
def visibility(root,on):
    for o in [root,*root.children_recursive]:o.hide_render=not on
def star(name,loc,mat,parent,size=.14):
    r=empty(name,loc,parent)
    pts=[((size if i%2==0 else size*.46)*math.cos(math.pi/2+i*math.pi/5),(size if i%2==0 else size*.46)*math.sin(math.pi/2+i*math.pi/5)) for i in range(10)]
    verts=[(x,y,z) for z in (-size*.22,size*.22) for x,y in pts]
    faces=[tuple(range(9,-1,-1)),tuple(range(10,20))]+[(i,(i+1)%10,(i+1)%10+10,i+10) for i in range(10)]
    mesh(name+'_star_silhouette',verts,faces,mat,r)
    return r
def dots(name,radius,z,mat,parent,count=52,width=.022):
    # One mesh instead of one Blender object per pixel.
    positions=[(radius*math.cos(i*math.tau/count),radius*math.sin(i*math.tau/count),z) for i in range(count)]
    return cubes(name,positions,width,mat,parent)
def cubes(name,positions,width,mat,parent):
    verts=[];faces=[]
    corners=[(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]
    template=[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)]
    for p in positions:
        n=len(verts);verts.extend([(p[0]+x*width/2,p[1]+y*width/2,p[2]+z*width/2) for x,y,z in corners]);faces.extend([tuple(n+j for j in f) for f in template])
    return mesh(name,verts,faces,mat,parent)
