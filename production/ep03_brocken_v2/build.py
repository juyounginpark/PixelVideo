"""EP03 revision: performed action, articulated limbs, facial beats and reveal shots."""
import bpy,math,sys,time,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent;O=R/'frames';O.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R.parent/'ep03_brocken/MINSU_BROCKEN.blend'))
s=bpy.context.scene;actor=bpy.data.objects['MINSU'];head=bpy.data.objects['LP_head'];cam=s.camera
old=bpy.data.objects['projected_silhouette']
for o in [*old.children_recursive,old]:bpy.data.objects.remove(o,do_unlink=True)
for o in bpy.data.objects:
    o.animation_data_clear()
    if o.data and hasattr(o.data,'animation_data_clear'):o.data.animation_data_clear()
actor.location=(0,0,0);actor.rotation_euler=(0,0,math.pi)
arms=[bpy.data.objects['LP_arm'],bpy.data.objects['LP_arm.001']]
legs=[bpy.data.objects['LP_leg'],bpy.data.objects['LP_leg.001']]
for o in [head,*arms,*legs]:o.rotation_euler=(0,0,0)
bpy.context.view_layer.update()
def empty(name,parent,loc):
    o=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(o);o.parent=parent;o.location=loc;return o
def reparent(o,parent):
    mw=o.matrix_world.copy();o.parent=parent;o.matrix_world=mw
elbows=[];knees=[]
for a in arms:
    e=empty('elbow',a,(0,0,-.415));elbows.append(e);bpy.context.view_layer.update()
    for child in list(a.children):
        if child!=e and any(child.name.startswith(n) for n in ['fore_sleeve','cuff','hand','thumb']):reparent(child,e)
for l in legs:
    k=empty('knee',l,(0,0,-.35));knees.append(k);bpy.context.view_layer.update()
    for child in list(l.children):
        if child==k:continue
        if child.name.startswith('trouser') and not child.name.startswith('trouser_hem'):
            # Separate thigh from shin; preserve the existing material and bevels.
            child.dimensions.z=.34;child.location.z=-.175
            shin=child.copy();shin.data=child.data.copy();bpy.context.collection.objects.link(shin);shin.name='shin';shin.parent=k;shin.location=(0,0,-.17);shin.dimensions.z=.34
        elif any(child.name.startswith(n) for n in ['trouser_hem','sneaker','sole','toe_cap','lace','heel_tab']):reparent(child,k)
        elif child.name.startswith('outer_seam'):child.hide_render=True
eyes=[o for o in head.children if o.name.startswith('eye_decal')]
brows=[o for o in head.children if o.name.startswith('brow')]
mouth=bpy.data.objects.get('mouth');mouthpoints=list(mouth.data.splines[0].points)
baseeye=[o.scale.copy() for o in eyes]

# Darker silhouette, warmer key light, cooler background: avoid flat monochrome.
dark=bpy.data.materials.get('shadow in mist')
shadowshader=next(n for n in dark.node_tree.nodes if n.type=='EMISSION')
for o in bpy.data.objects:
    if o.type=='LIGHT' and o.data.type=='SUN':o.data.energy=2.0;o.data.color=(1,.86,.67)
sun=bpy.data.objects.get('sun');sun.location=(-1.5,-14,6.5);sun.scale=(.9,.9,.9)
worldbg=next(n for n in s.world.node_tree.nodes if n.type=='BACKGROUND');worldbg.inputs[0].default_value=(.21,.32,.37,1);worldbg.inputs[1].default_value=.65
for material in bpy.data.materials:
    if material.name.startswith('LP_jacket'):
        ramp=next((n for n in material.node_tree.nodes if n.type=='VALTORGB'),None)
        if ramp:
            for e in ramp.color_ramp.elements:
                c=e.color;e.color=(c[0]*.8,min(1,c[1]*1.12),min(1,c[2]*1.1),1)

# Duplicate the complete articulated rig. Both figures use the same poses.
root=empty('SILHOUETTE',None,(0,7,.2));root.scale=(2.65,.028,2.65)
mapping={actor:root}
for o in actor.children_recursive:
    c=o.copy();c.name='SHADOW_'+o.name
    if o.data:c.data=o.data.copy()
    bpy.context.collection.objects.link(c);c.animation_data_clear();mapping[o]=c
for o,c in list(mapping.items())[1:]:
    c.parent=mapping[o.parent];c.matrix_parent_inverse=o.matrix_parent_inverse.copy()
    if c.type in ['MESH','CURVE']:c.data.materials.clear();c.data.materials.append(dark)

# Moving wisps, using 4D procedural noise, sit in front of the distant silhouette.
fog=bpy.data.materials.new('moving mist');fog.use_nodes=True;n=fog.node_tree.nodes;n.clear();links=fog.node_tree.links
out=n.new('ShaderNodeOutputMaterial');mix=n.new('ShaderNodeMixShader');tr=n.new('ShaderNodeBsdfTransparent');em=n.new('ShaderNodeEmission');em.inputs[0].default_value=(.30,.45,.48,1)
noise=n.new('ShaderNodeTexNoise');noise.noise_dimensions='4D';noise.inputs['Scale'].default_value=2.7;noise.inputs['Detail'].default_value=1
coord=n.new('ShaderNodeTexCoord');links.new(coord.outputs['Generated'],noise.inputs['Vector'])
mul=n.new('ShaderNodeMath');mul.operation='MULTIPLY';mul.inputs[1].default_value=.32;links.new(noise.outputs['Fac'],mul.inputs[0]);links.new(mul.outputs[0],mix.inputs[0]);links.new(tr.outputs[0],mix.inputs[1]);links.new(em.outputs[0],mix.inputs[2]);links.new(mix.outputs[0],out.inputs[0])
bpy.ops.mesh.primitive_plane_add(size=1,location=(0,6.8,3),rotation=(math.pi/2,0,0));veil=bpy.context.object;veil.name='fog wisps';veil.scale=(18,12,1);veil.data.materials.append(fog)
try:fog.surface_render_method='DITHERED'
except:pass

FPS=24;COUNT=408
s.render.engine='BLENDER_EEVEE';s.eevee.taa_render_samples=24;s.render.resolution_x=432;s.render.resolution_y=768;s.render.resolution_percentage=100;s.render.fps=FPS
cam.data.dof.use_dof=False;s.frame_start=1;s.frame_end=COUNT
def ease(x):x=max(0,min(1,x));return x*x*(3-2*x)
def pulse(t,start,duration):return math.sin(math.pi*max(0,min(1,(t-start)/duration))) if start<=t<=start+duration else 0
def pointcam(loc,target,lens):
    cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens
def pose(t):
    ending=t>=14.5
    # The ending continues a fresh confirmation gesture; no reversed playback.
    u=t-14.5 if ending else t
    actor.location=(-.30,0,0);actor.rotation_euler=(0,0,math.pi)
    for o in [head,*arms,*legs,*elbows,*knees]:o.rotation_euler=(0,0,0)
    actor.location.z=.012*math.sin(t*math.tau*.75)
    fear=.0
    if ending:
        raisehand=1.45*ease(u/.45)*(1-ease((u-1.25)/.45));arms[0].rotation_euler.y=raisehand;elbows[0].rotation_euler.x=-.12
        head.rotation_euler.z=.05*math.sin(u*2)
    else:
        # Arrive, freeze, then lift a hand deliberately to verify the silhouette.
        actor.location.y=-.18+.18*ease(t/.6)
        freeze=pulse(t,.48,.45);actor.location.z+=.05*freeze;head.rotation_euler.x=-.18*ease((t-.55)/.35)
        raisehand=1.60*ease((t-1.05)/.65)*(1-ease((t-2.3)/.4))
        arms[0].rotation_euler.y=raisehand;elbows[0].rotation_euler.x=-.12*ease((t-1.1)/.4)
        if 2.75<=t<3.8:
            fear=ease((t-2.75)/.18);head.rotation_euler.z=.45*ease((t-2.8)/.3)
            elbows[0].rotation_euler.x=-.75*fear;elbows[1].rotation_euler.x=-.45*fear
            actor.location.y=-.16*ease((t-2.8)/.25)
        if 3.8<=t<8.5:
            q=t-3.8
            raisehand=1.45*ease(q/.65)*(1-ease((q-1.25)/.32))+1.80*ease((q-1.95)/.45)*(1-ease((q-3.1)/.38))
            arms[0].rotation_euler.y=raisehand
            elbows[0].rotation_euler.x=-.18
            step=.48*ease((q-3.45)/.65)
            actor.location.x=-.30+step
            gait=math.sin(max(0,min(1,(q-3.45)/.65))*math.tau)
            legs[0].rotation_euler.x=.26*gait;legs[1].rotation_euler.x=-.26*gait;knees[0].rotation_euler.x=.25*max(0,-gait);knees[1].rotation_euler.x=.25*max(0,gait)
            head.rotation_euler.z=.10*math.sin(q*2)
        if 8.5<=t<10.6:
            q=t-8.5;fear=.9*ease(q/.2)
            actor.location.y=-.3*ease(q/.4);actor.location.z=-.1*pulse(q,0,.65)
            actor.rotation_euler.x=-.12*ease(q/.3)
            elbows[0].rotation_euler.x=-1.0;elbows[1].rotation_euler.x=-.8;arms[0].rotation_euler.y=.23;arms[1].rotation_euler.y=-.23
            head.rotation_euler.z=.52*ease((q-.65)/.4)
        if 10.6<=t<14.5:
            q=t-10.6;actor.rotation_euler.z=math.pi-.95*ease(q/.65)
            head.rotation_euler.z=-.5*ease(q/.5);head.rotation_euler.x=-.22*ease(q/.7)
            arms[0].rotation_euler.y=.85*ease((q-.8)/.5);elbows[0].rotation_euler.x=-.4
    # Facial reaction and blinks are animated, not a fixed neutral decal.
    blink=max(pulse(t,2.72,.16),pulse(t,9.75,.16),pulse(t,12.4,.16))
    for o,base in zip(eyes,baseeye):o.scale=base.copy();o.scale.z=(1+.18*fear)*(1-.92*blink)
    for i,o in enumerate(brows):o.location.z=.035*fear;o.rotation_euler.y=(1 if i else -1)*.18*fear
    for j,p in enumerate(mouthpoints):
        x=(j-3)*.019;y=-.291;z=-.123
        if fear>.1:
            a=math.tau*j/(len(mouthpoints)-1);x=math.cos(a)*.027*fear;z=-.12+math.sin(a)*.037*fear
        p.co=(x,y,z,1)
    # Exactly synchronous, including footfalls, elbows and the body turn.
    root.location=(actor.location.x*2.65,7,.2+actor.location.z*2.65);root.rotation_euler=actor.rotation_euler
    for o,c in list(mapping.items())[1:]:c.location=o.location;c.rotation_euler=o.rotation_euler;c.scale=o.scale
    reveal=ease((t-.08)/.62)
    shadowshader.inputs[0].default_value=(.30*(1-reveal)+.055*reveal,.45*(1-reveal)+.12*reveal,.48*(1-reveal)+.16*reveal,1)
    noise.inputs['W'].default_value=t*.11
    mul.inputs[1].default_value=.32*(1-ease((t-11.7)/.3)) if t<14.5 else .32
    if ending:
        pointcam((1.6,-7.5,3.4),(0,3.6,2.8),42)
    elif 2.75<=t<3.8:
        q=(t-2.75)/1.05;pointcam((1.8-q*.18,2.5,2.6),(-.30,-.1,1.65),62)
    elif 8.5<=t<10.6:
        q=ease((t-8.5)/2.1);pointcam((1.7-q*.3,2.8,2.5),(-.30,-.15,1.58),57)
    elif 12<=t<14.5:
        q=ease((t-12)/2.5);pointcam((4.1-q,7.3,3.9),(-1.1,-5.5,3.6),38)
    else:
        q=ease(min(t,2.7)/2.7);pointcam((1.8-.2*q,-7.9+.4*q,3.5-.1*q),(0,3.6,2.8),40+2*q)
    bpy.context.view_layer.update()

rig=[actor,head,*arms,*legs,*elbows,*knees,*eyes,*brows,root,*mapping.values(),cam]
motion=[]
for f in range(1,COUNT+1):
    t=(f-1)/FPS;pose(t)
    for o in set(rig):
        for p in ['location','rotation_euler','scale']:o.keyframe_insert(data_path=p,frame=f)
    for p in mouthpoints:p.keyframe_insert(data_path='co',frame=f)
    cam.data.keyframe_insert(data_path='lens',frame=f);noise.inputs['W'].keyframe_insert(data_path='default_value',frame=f);mul.inputs[1].keyframe_insert(data_path='default_value',frame=f);shadowshader.inputs[0].keyframe_insert(data_path='default_value',frame=f)
    motion.append({'f':f,'arm':round(arms[0].rotation_euler.y,4),'elbow':round(elbows[0].rotation_euler.x,4),'x':round(actor.location.x,4),'camera':list(cam.location)})
s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(R/'MINSU_BROCKEN_ACTION.blend'))
(R/'motion.json').write_text(json.dumps(motion),encoding='utf-8')
frames=[1,18,42,76,114,166,228,288,315,348,390] if '--preview' in sys.argv else range(1,COUNT+1)
start=time.time()
for f in frames:
    s.frame_set(f);s.render.filepath=str(O/f'{f:05d}.png');bpy.ops.render.render(write_still=True)
    print(f'FRAME {f}/{COUNT} {time.time()-start:.1f}s',flush=True)
print('RENDER_COMPLETE',flush=True)
