"""Opt-in V2.1 assets/render/acting; independent of topic discovery or selection.

The existing EP04 build remains a historical recipe. This module never selects a
topic, writes an episode, renders a movie, or falls back to an animal/world.
"""
import math
import bpy
from mathutils import Vector
from art import MaterialLibrary, CharacterRig, empty, box, line
from engine import OutlinePass, ease


def linear(c):
    return c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4


class ToonMaterialLibrary(MaterialLibrary):
    COLORS={**MaterialLibrary.COLORS,
            'skin':(.97,.84,.64),'hair':(.22,.16,.14),'mint':(.26,.65,.53),
            'cream':(.94,.88,.72),'navy':(.16,.20,.27),'shoe':(.29,.25,.24),
            'cheek':(.92,.53,.47),'studio':(.67,.74,.74)}

    def make(self,name,color,textured):
        m=super().make(name,tuple(linear(c) for c in color),textured)
        m.name='MINSU_V21_'+name
        nodes=m.node_tree.nodes;links=m.node_tree.links
        bs=next(n for n in nodes if n.type=='BSDF_DIFFUSE')
        output=next(n for n in nodes if n.type=='OUTPUT_MATERIAL')
        base=bs.inputs['Color'].links[0].from_socket if bs.inputs['Color'].links else None
        for link in list(bs.inputs['Color'].links):links.remove(link)
        bs.inputs['Color'].default_value=(1,1,1,1)
        lighting=nodes.new('ShaderNodeShaderToRGB');links.new(bs.outputs[0],lighting.inputs[0])
        ramp=nodes.new('ShaderNodeValToRGB');ramp.name='Three light bands';ramp.color_ramp.interpolation='CONSTANT'
        for e,pos,val in [(ramp.color_ramp.elements[0],0,.55),(ramp.color_ramp.elements[1],.72,1)]:
            e.position=pos;e.color=(val,val,val,1)
        e=ramp.color_ramp.elements.new(.38);e.color=(.78,.78,.78,1)
        links.new(lighting.outputs['Color'],ramp.inputs['Fac'])
        multiply=nodes.new('ShaderNodeMixRGB');multiply.blend_type='MULTIPLY';multiply.inputs[0].default_value=1
        if base:links.new(base,multiply.inputs[1])
        else:multiply.inputs[1].default_value=(*[linear(c) for c in color],1)
        links.new(ramp.outputs[0],multiply.inputs[2])
        emission=nodes.new('ShaderNodeEmission');links.new(multiply.outputs[0],emission.inputs[0]);links.new(emission.outputs[0],output.inputs[0])
        # Texture images contain linear palette values; do not apply a second sRGB conversion.
        for n in nodes:
            if n.type=='TEX_IMAGE':
                n.image.colorspace_settings.name='Non-Color'
                if name in ('skin','mint','cream','hair','shoe'):
                    px=list(n.image.pixels);basecolor=[linear(c) for c in color]
                    for i in range(0,len(px),4):
                        for j in range(3):px[i+j]=basecolor[j]+(px[i+j]-basecolor[j])*.20
                    n.image.pixels=px;n.image.pack()
        m['style_profile']='MINSU_V21';m['light_bands']=3
        return m


class FaceController:
    STATES=('Neutral','Curious','Surprise','Confused','Happy','Worried','Thinking','Determined','Laughing','Scared')
    def __init__(self,head,m):
        self.groups={};self.eyes=[]
        for state in self.STATES:
            g=empty('v21_face_'+state,parent=head);self.groups[state]=g
            for sign in (-1,1):
                x=sign*.16;z=-.055;y=-.315
                if state in ('Happy','Laughing'):
                    eye=line(state+'_eye',[(x-.040,y,z-.012),(x,y,z+.025),(x+.040,y,z-.012)],m['navy'],.014,g)
                else:
                    h=.082 if state in ('Surprise','Scared') else .058
                    eye=box(state+'_eye',(x,y,z),(.055,.014,h),m['navy'],g,.003)
                    box(state+'_eye_glint',(x-.012,y-.009,z+.013),(.011,.007,.012),m['cream'],g)
                self.eyes.append(eye)
                if state in ('Worried','Confused','Thinking','Determined','Scared','Curious'):
                    brow=box(state+'_brow',(x,y,.018),(.064,.012,.017),m['hair'],g)
                    brow.rotation_euler.y=sign*(-.24 if state=='Determined' else .20)
                    if state=='Curious':
                        brow.rotation_euler.y=-.18 if sign==1 else 0;brow.location.z=.041 if sign==1 else .019
            if state in ('Surprise','Scared','Laughing'):
                box(state+'_mouth',(0,-.315,-.176),(.065,.012,.060),m['navy'],g,.008)
            elif state=='Happy':
                line(state+'_smile',[(-.045,-.316,-.156),(0,-.316,-.179),(.045,-.316,-.156)],m['navy'],.009,g)
            else:box(state+'_mouth',(0,-.316,-.172),(.045,.012,.013),m['navy'],g)
        self.set('Neutral')

    def set(self,state,blink=False):
        if state not in self.groups:raise ValueError('Unknown expression '+state)
        for k,g in self.groups.items():g.scale=(1,1,1) if k==state else (0,0,0)
        for eye in self.eyes:eye.scale.z=.12 if blink else 1


class CuteCharacterFactory:
    def __init__(self,materials):self.m=materials
    def minsu(self):
        m=self.m;root=empty('MINSU_CUTE_V21');body=empty('v21_torso',(0,0,.32),root)
        box('short_mint_jacket',(0,0,.23),(.49,.35,.44),m['mint'],body,.045)
        box('zip',(0,-.183,.225),(.020,.013,.31),m['cream'],body)
        box('collar',(0,-.10,.46),(.21,.19,.05),m['cream'],body,.015)
        head=empty('v21_head',(0,0,.78),body)
        box('wide_cheek_head',(0,0,0),(.81,.61,.70),m['skin'],head,.09)
        box('fitted_hair_shell',(0,.029,.277),(.844,.65,.205),m['hair'],head,.06)
        box('hair_back',(0,.27,.046),(.79,.095,.49),m['hair'],head,.03)
        box('connected_hairline',(0,-.285,.257),(.75,.068,.074),m['hair'],head,.013)
        for sign in (-1,1):
            box('side_hair',(sign*.385,.045,.12),(.08,.48,.35),m['hair'],head,.025)
            box('ear',(sign*.411,-.016,-.089),(.084,.12,.14),m['skin'],head,.025)
            box('soft_cheek',(sign*.26,-.312,-.123),(.071,.007,.026),m['cheek'],head)
        for x,z,w in [(-.285,.185,.17),(-.093,.211,.20),(.14,.234,.27)]:
            box('connected_fringe',(x,-.284,z),(w,.076,.146),m['hair'],head,.012)
        face=FaceController(head,m);arms=[];elbows=[];legs=[]
        for sign in (-1,1):
            shoulder=empty('v21_shoulder',(sign*.291,0,.376),body);arms.append(shoulder)
            box('short_sleeve',(sign*.007,0,-.102),(.165,.215,.224),m['mint'],shoulder,.026)
            elbow=empty('v21_elbow',(sign*.009,0,-.198),shoulder);elbows.append(elbow)
            box('cuff',(0,0,-.049),(.15,.20,.10),m['mint'],elbow,.017)
            box('mitten',(0,-.009,-.139),(.175,.19,.16),m['skin'],elbow,.033)
            leg=empty('v21_hip',(sign*.129,0,.315),root);legs.append(leg)
            box('short_trousers',(0,0,-.119),(.205,.28,.25),m['navy'],leg,.022)
            box('wide_boot',(0,-.042,-.252),(.256,.346,.12),m['shoe'],leg,.024)
        rig=CharacterRig(root,body,head,arms,legs,face);rig.elbows=elbows;rig.moving+=elbows
        rig.rest={o.name:(o.location.copy(),o.rotation_euler.copy(),o.scale.copy()) for o in rig.moving}
        root['model_id']='MINSU_CUTE_V21';root['style_profile']='MINSU_V21';root['head_ratio']=.70/1.48
        return rig


class PixelStylePipeline:
    """Native 540x960 geometry, edges and color bands, then exact 2x still upscale."""
    def configure(self,scene):
        scene.render.engine='BLENDER_EEVEE';scene.eevee.taa_render_samples=64
        scene.render.resolution_x=540;scene.render.resolution_y=960;scene.render.resolution_percentage=100
        scene.render.image_settings.file_format='PNG';scene.render.fps=30
        scene.render.film_transparent=False;scene.view_settings.view_transform='Standard';scene.view_settings.look='None'
        OutlinePass().configure(scene)
        g=scene.compositing_node_group;nodes=g.nodes;links=g.links
        dest=next(n for n in nodes if n.bl_idname=='NodeGroupOutput')
        original=dest.inputs['Image'].links[0].from_socket
        # Quantize luminance, preserving RGB ratios. Per-channel rounding turned
        # dark brown into olive at low values; do not quantize channels separately.
        bw=nodes.new('CompositorNodeRGBToBW');links.new(original,bw.inputs[0]);v=bw.outputs[0]
        for op,value in [('MULTIPLY',24),('ROUND',0),('DIVIDE',24)]:
            n=nodes.new('ShaderNodeMath');n.operation=op;links.new(v,n.inputs[0]);n.inputs[1].default_value=value;v=n.outputs[0]
        denominator=nodes.new('ShaderNodeMath');denominator.operation='MAXIMUM';links.new(bw.outputs[0],denominator.inputs[0]);denominator.inputs[1].default_value=.00001
        ratio=nodes.new('ShaderNodeMath');ratio.operation='DIVIDE';links.new(v,ratio.inputs[0]);links.new(denominator.outputs[0],ratio.inputs[1]);v=ratio.outputs[0]
        for op,value in [('MAXIMUM',.92),('MINIMUM',1.08)]:
            n=nodes.new('ShaderNodeMath');n.operation=op;links.new(v,n.inputs[0]);n.inputs[1].default_value=value;v=n.outputs[0]
        multiply=nodes.new('ShaderNodeMixRGB');multiply.blend_type='MULTIPLY';multiply.inputs[0].default_value=1
        links.new(original,multiply.inputs[1]);links.new(v,multiply.inputs[2]);links.new(multiply.outputs[0],dest.inputs['Image'])
        scene['pixel_style']='MINSU_V21';scene['upscale_filter']='NEAREST';scene['upscale_factor']=2


class StudioLighting:
    """Neutral asset inspection only, not a fallback production world."""
    def configure(self):
        s=bpy.context.scene
        for name,position,power,size in [('key',(-3,-4,5),500,4),('fill',(3,-2,3),150,5)]:
            bpy.ops.object.light_add(type='AREA',location=position);o=bpy.context.object;o.name='review_'+name;o.data.energy=power;o.data.size=size
            o.rotation_euler=(Vector((0,0,.8))-o.location).to_track_quat('-Z','Y').to_euler()
        w=bpy.data.worlds.new('asset_review_neutral');w.use_nodes=True;s.world=w
        bg=next(n for n in w.node_tree.nodes if n.type=='BACKGROUND');bg.inputs[0].default_value=(.5,.55,.58,1);bg.inputs[1].default_value=.45


class TargetedActing:
    """Deterministic three-stage gestures; explicit gaze target, no random sway."""
    def __init__(self,rig):self.rig=rig
    def reset(self):
        for o in self.rig.moving:
            loc,rot,scale=self.rig.rest[o.name];o.location=loc;o.rotation_euler=rot;o.scale=scale
        self.rig.face.set('Neutral')
    def apply(self,action,progress,target):
        if action not in ('Inspect','Surprise','Point','Understand'):raise ValueError('Unsupported acting action')
        if not 0<=progress<=1:raise ValueError('Action progress must be normalized')
        self.reset();r=self.rig
        strength=ease(progress/.25)*(1-.25*ease((progress-.80)/.20))
        anticipation=math.sin(math.pi*min(1,progress/.22))*.05
        bpy.context.view_layer.update()
        local=r.head.parent.matrix_world.inverted()@Vector(target)-r.head.location
        r.head.rotation_euler.z=max(-.65,min(.65,math.atan2(local.x,-local.y)))*strength
        r.head.rotation_euler.x=max(-.45,min(.5,-math.atan2(local.z,math.hypot(local.x,local.y))))*strength
        r.body.rotation_euler.x=-anticipation
        if action=='Inspect':r.face.set('Curious');r.body.rotation_euler.x+=.14*strength
        elif action=='Surprise':
            r.face.set('Surprise');r.body.rotation_euler.x-=.13*strength
            for sign,a,e in zip((-1,1),r.arms,r.elbows):a.rotation_euler.y=sign*.30*strength;e.rotation_euler.x=-.40*strength
        elif action=='Point':
            r.face.set('Determined');r.arms[1].rotation_euler.x=-.85*strength;r.elbows[1].rotation_euler.x=-.38*strength
        else:r.face.set('Happy');r.head.rotation_euler.x+=.1*math.sin(progress*math.pi*2)*strength
        if progress==0:r.face.set('Neutral')


class FramingCamera:
    """Explicit shot distance and target; bounds supplied by the scene compiler."""
    PRESETS={'WIDE':1.7,'MEDIUM':1.22,'CLOSE_UP':1.12,'MACRO':1.18}
    def frame(self,camera,bounds,shot,direction=(0,-1,.12),aspect=9/16):
        if shot not in self.PRESETS:raise ValueError('Unknown framing preset')
        lo,hi=map(Vector,bounds)
        if any(hi[i]<=lo[i] for i in range(3)):raise ValueError('Invalid subject bounds')
        target=(lo+hi)/2;camera.location=target+Vector(direction).normalized()*5
        camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
        rotation=camera.rotation_euler.to_matrix().transposed()
        corners=[rotation@(Vector((x,y,z))-target) for x in (lo.x,hi.x) for y in (lo.y,hi.y) for z in (lo.z,hi.z)]
        width=max(p.x for p in corners)-min(p.x for p in corners);height=max(p.y for p in corners)-min(p.y for p in corners)
        camera.data.type='ORTHO';camera.data.ortho_scale=max(height,width/aspect)*self.PRESETS[shot]
        camera.data.shift_y=0;camera.data.dof.use_dof=False


class WorldRegistry:
    """Resolve only an explicit upstream world choice; never pick a topic/world."""
    def __init__(self):self.factories={}
    def register(self,key,factory):
        if key in self.factories:raise ValueError('World already registered')
        self.factories[key]=factory
    def build(self,key):
        if key not in self.factories:raise ValueError('Missing world asset preset: '+str(key))
        return self.factories[key]()
