"""V3.1 native materials with object-space texel density; preserves old looks."""
import math,random
import bpy
from mathutils import Vector
from art import MaterialLibrary
from design_system import CuteCharacterFactory,linear
from engine import OutlinePass

class Materials(MaterialLibrary):
    COLORS={**MaterialLibrary.COLORS,
      'skin':(.99,.80,.56),'hair':(.16,.105,.12),'mint':(.18,.67,.61),'cream':(.99,.94,.80),
      'navy':(.06,.12,.23),'shoe':(.15,.22,.35),'cheek':(.98,.39,.34),
      'ice':(.30,.72,.82),'ice_top':(.53,.89,.94),'ice_dark':(.085,.34,.49),
      'amber':(1,.62,.18),'coral':(1,.29,.25),'metal':(.70,.82,.86),'midnight':(.035,.075,.15),
      'wall':(.08,.19,.30),'rail':(.23,.40,.50),'snow':(.81,.91,.93),'light':(1,.79,.36),
      'bond':(.15,.43,.59),'oxygen':(1,.64,.19),'hydrogen':(1,.91,.68)}
    def __init__(self):
        self.materials={}
        for name,col in self.COLORS.items():self.materials[name]=self.make(name,col,name not in ('navy','cheek','light','bond','oxygen','hydrogen','midnight'))
    def make(self,name,color,textured):
        m=bpy.data.materials.new('MINSU_V31_'+name);m.diffuse_color=(*color,1);m.use_nodes=True
        n=m.node_tree.nodes;n.clear();l=m.node_tree.links
        out=n.new('ShaderNodeOutputMaterial');diff=n.new('ShaderNodeBsdfDiffuse');diff.inputs['Color'].default_value=(1,1,1,1);diff.inputs['Roughness'].default_value=1
        rgb=n.new('ShaderNodeShaderToRGB');l.new(diff.outputs[0],rgb.inputs[0])
        ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.interpolation='CONSTANT'
        ramp.color_ramp.elements[0].position=.12;ramp.color_ramp.elements[0].color=(.40,.40,.40,1)
        ramp.color_ramp.elements[1].position=.72;ramp.color_ramp.elements[1].color=(1,1,1,1)
        e=ramp.color_ramp.elements.new(.36);e.color=(.72,.72,.72,1);l.new(rgb.outputs[0],ramp.inputs[0])
        mul=n.new('ShaderNodeMixRGB');mul.blend_type='MULTIPLY';mul.inputs[0].default_value=1
        mul.inputs[1].default_value=(*[linear(x) for x in color],1);l.new(ramp.outputs[0],mul.inputs[2])
        if textured:
            im=bpy.data.images.new(name+'_32px_V31',width=32,height=32);pixels=[];rng=random.Random('V31'+name)
            variation=.016 if name in ('skin','cream','hair') else .055
            for y in range(32):
                for x in range(32):
                    value=rng.choice([1,1,1,1-variation,1+variation])
                    pixels += [linear(min(1,c*value)) for c in color]+[1]
            im.colorspace_settings.name='Non-Color';im.pixels=pixels;im.pack()
            tex=n.new('ShaderNodeTexImage');tex.image=im;tex.interpolation='Closest';tex.projection='BOX';tex.projection_blend=.08
            coord=n.new('ShaderNodeTexCoord');scale=n.new('ShaderNodeVectorMath');scale.operation='SCALE';scale.inputs[3].default_value=.5
            l.new(coord.outputs['Object'],scale.inputs[0]);l.new(scale.outputs[0],tex.inputs[0]);l.new(tex.outputs['Color'],mul.inputs[1])
            m['texels_per_world_unit']=16;m['texture_coordinates']='local Object; baked mesh dimensions; no Generated mapping'
        em=n.new('ShaderNodeEmission');l.new(mul.outputs[0],em.inputs[0]);l.new(em.outputs[0],out.inputs[0])
        if name=='light':
            for link in list(em.inputs[0].links):l.remove(link)
            em.inputs[0].default_value=(*[linear(x) for x in color],1)
        m['style']='V31';m['light_bands']=3
        return m

def setup(scene):
    scene.render.engine='BLENDER_EEVEE';scene.eevee.taa_render_samples=8
    scene.render.resolution_x=540;scene.render.resolution_y=960;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.render.fps=30
    scene.render.film_transparent=False;scene.render.filter_size=.01
    scene.view_settings.view_transform='Standard';scene.view_settings.look='None'
    scene.view_settings.exposure=0;scene.view_settings.gamma=1
    OutlinePass().configure(scene)
    # Strengthen the native binary contour, without blurring or upscaling UI.
    for node in scene.compositing_node_group.nodes:
        if node.bl_idname=='ShaderNodeMath' and node.operation=='MULTIPLY' and abs(node.inputs[1].default_value-.25)<.001:node.inputs[1].default_value=.68
    world=bpy.data.worlds.new('MIDNIGHT_ICE_PAVILION');world.use_nodes=True;scene.world=world
    bg=next(n for n in world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs[0].default_value=(*[linear(c) for c in (.035,.075,.15)],1);bg.inputs[1].default_value=.80
    for name,pos,power,size,col in [('warm_key',(-3,-4,6),650,4,(1,.87,.69)),('cool_fill',(3,-1,4),350,3,(.58,.85,1)),('rim',(0,4,4),450,2,(.50,.81,1))]:
        bpy.ops.object.light_add(type='AREA',location=pos);o=bpy.context.object;o.name=name;o.data.energy=power;o.data.size=size;o.data.color=col
        o.rotation_euler=(Vector((0,0,.5))-o.location).to_track_quat('-Z','Y').to_euler()
    scene['native_resolution']='540x960';scene['upscale']='NEAREST x2 before final-resolution typography'

def character(m):
    from art import box
    r=CuteCharacterFactory(m).minsu()
    box('warm_scarf',(0,-.13,.49),(.34,.22,.10),m['amber'],r.body,.014)
    box('scarf_tail',(.16,-.205,.35),(.10,.035,.27),m['amber'],r.body,.01)
    for leg in r.legs:
        box('skate_blade',(0,-.055,-.34),(.038,.40,.042),m['metal'],leg)
        for y in (-.15,.08):box('blade_mount',(0,y,-.30),(.052,.045,.068),m['metal'],leg)
    r.root['model_id']='MINSU_CUTE_V31';return r
