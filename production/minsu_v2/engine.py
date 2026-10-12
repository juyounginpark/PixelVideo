"""Native timeline, camera, soft pixel render configuration."""
import bpy, math
from mathutils import Vector

def ease(v):v=max(0,min(1,v));return v*v*(3-2*v)

class CameraDirector:
    def __init__(self):
        bpy.ops.object.camera_add();self.camera=bpy.context.object;self.camera.name='MINSU_V2_CAMERA'
        self.camera.data.clip_start=.01;self.camera.data.clip_end=120;self.camera.data.dof.use_dof=False
        bpy.context.scene.camera=self.camera
    def apply(self,plan,progress):
        cam=self.camera;cam.location=Vector(plan['startPosition']).lerp(Vector(plan['endPosition']),ease(progress))
        cam.rotation_euler=(Vector(plan['target'])-cam.location).to_track_quat('-Z','Y').to_euler()
        cam.data.lens=plan['lens'];cam.data.shift_y=-.04

class LightingPresetManager:
    def daylight(self):
        s=bpy.context.scene
        bpy.ops.object.light_add(type='SUN',location=(-3,-4,6));o=bpy.context.object;o.name='soft_key';o.data.energy=1.8;o.data.angle=.28;o.rotation_euler=(.40,-.30,-.45)
        bpy.ops.object.light_add(type='AREA',location=(-3,-4,5));o=bpy.context.object;o.name='large_fill';o.data.energy=230;o.data.shape='DISK';o.data.size=5
        w=bpy.data.worlds.new('warm_sky');w.use_nodes=True;s.world=w
        bg=next(n for n in w.node_tree.nodes if n.type=='BACKGROUND');bg.inputs[0].default_value=(.46,.64,.73,1);bg.inputs[1].default_value=.7

class OutlinePass:
    """Native-resolution 1px depth silhouette + high-threshold normal creases."""
    def configure(self,scene):
        scene.view_layers[0].use_pass_z=True;scene.view_layers[0].use_pass_normal=True
        g=bpy.data.node_groups.new('MINSU_DEPTH_NORMAL_OUTLINE','CompositorNodeTree')
        g.interface.new_socket(name='Image',in_out='OUTPUT',socket_type='NodeSocketColor')
        scene.compositing_node_group=g;n=g.nodes;l=g.links
        source=n.new('CompositorNodeRLayers');output=n.new('NodeGroupOutput')
        def mathnode(op,a=None,b=None):
            node=n.new('ShaderNodeMath');node.operation=op
            for j,v in enumerate((a,b)):
                if hasattr(v,'bl_idname'):l.new(v,node.inputs[j])
                elif v is not None:node.inputs[j].default_value=v
            return node.outputs[0]
        # Log-depth makes the same relative discontinuity independent of camera distance.
        log=mathnode('LOGARITHM',source.outputs['Depth'],math.e)
        f=n.new('CompositorNodeFilter');f.inputs['Type'].default_value='Sobel';l.new(log,f.inputs['Image'])
        bw=n.new('CompositorNodeRGBToBW');l.new(f.outputs['Image'],bw.inputs[0])
        edge=mathnode('GREATER_THAN',bw.outputs[0],.05)
        nf=n.new('CompositorNodeFilter');nf.inputs['Type'].default_value='Sobel';l.new(source.outputs['Normal'],nf.inputs['Image'])
        nb=n.new('CompositorNodeRGBToBW');l.new(nf.outputs[0],nb.inputs[0])
        normal=mathnode('GREATER_THAN',nb.outputs[0],1.4)
        edge=mathnode('MAXIMUM',edge,normal);edge=mathnode('MULTIPLY',edge,.25)
        mix=n.new('ShaderNodeMix');mix.data_type='RGBA';mix.blend_type='MIX';mix.inputs[7].default_value=(.035,.03,.025,1)
        l.new(edge,mix.inputs[0]);l.new(source.outputs['Image'],mix.inputs[6]);l.new(mix.outputs[2],output.inputs['Image'])

class PixelRenderPipeline:
    def configure(self):
        s=bpy.context.scene;s.render.engine='BLENDER_EEVEE';s.eevee.taa_render_samples=16
        s.render.resolution_x=540;s.render.resolution_y=960;s.render.resolution_percentage=100
        s.render.fps=30;s.frame_start=1;s.frame_end=1080;s.render.image_settings.file_format='PNG'
        s.render.film_transparent=False;s.view_settings.view_transform='Standard';s.view_settings.look='None'
        OutlinePass().configure(s)

class CharacterStateManager:
    def __init__(self,rig):self.rig=rig
    def reset(self,t):
        r=self.rig;r.root.location=(-.72,.44,0);r.root.rotation_euler=(0,0,.3)
        r.body.location=(0,0,.43);r.body.rotation_euler=(.025*math.sin(t*2),0,0)
        r.head.rotation_euler=(.05,0,-.09)
        for a in r.arms:a.rotation_euler=(.06*math.sin(t*2),0,0)
        for l in r.legs:l.rotation_euler=(0,0,0)
        blink=(t%3.73)>.0 and 3.56<t%3.73<3.70
        r.face.set('Curious',blink)

class CharacterAnimationController:
    # Implemented procedural recipes. Hand-object contact needs supplied target/rig setup.
    PRESETS=('Idle','Walk','Run','Turn','LookAt','LookAround','Point','Explain','Surprise','Confused','Think','Happy','Laugh','Scared','Jump','StepBack','LeanForward','Touch','Inspect','PickUp','React','Celebrate')
    def __init__(self,rig):self.r=rig
    def apply(self,name,t,strength=1):
        if name not in self.PRESETS:raise ValueError(name)
        r=self.r;v=strength
        if name in ('Walk','Run'):
            q=math.sin(t*(9 if name=='Run' else 5));r.legs[0].rotation_euler.x=q*.35*v;r.legs[1].rotation_euler.x=-q*.35*v
            r.arms[0].rotation_euler.x=-q*.3*v;r.arms[1].rotation_euler.x=q*.3*v
        elif name in ('Surprise','Scared','React'):
            r.face.set('Scared' if name=='Scared' else 'Surprise');r.body.rotation_euler.x=-.13*v
            r.arms[0].rotation_euler.y=-.35*v;r.arms[1].rotation_euler.y=.35*v;r.head.rotation_euler.x=-.1*v
        elif name in ('Point','Explain','Touch','PickUp'):
            r.arms[1].rotation_euler.x=-1.0*v;r.arms[1].rotation_euler.y=.20*v
            r.head.rotation_euler.z=-.28*v
        elif name in ('LeanForward','Inspect'):
            r.body.rotation_euler.x=.20*v;r.head.rotation_euler.x=.22*v
        elif name in ('Happy','Laugh','Celebrate'):
            r.face.set('Laughing' if name=='Laugh' else 'Happy');r.head.rotation_euler.x=.09*math.sin(t*6)*v
            r.arms[0].rotation_euler.y=-.45*v;r.arms[1].rotation_euler.y=.45*v
        elif name in ('Confused','Think'):
            r.face.set('Thinking' if name=='Think' else 'Confused');r.head.rotation_euler.y=.16*v;r.arms[0].rotation_euler.x=-1.1*v
        elif name in ('LookAt','LookAround','Turn'):
            r.head.rotation_euler.z=.30*math.sin(t*2)*v
            if name=='Turn':r.root.rotation_euler.z+=.3*v
        elif name=='Jump':r.root.location.z=max(0,math.sin(t*math.pi))*.12*v
        elif name=='StepBack':r.root.location.y+=.12*ease(t)*v;r.legs[0].rotation_euler.x=-.18*v
        # Idle already applied by state manager. Presets are reusable, not all exercised in EP04.
