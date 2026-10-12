"""Cinematic, soft chibi redesign. Load original native 3D assets; new art, lights and blocking."""
import bpy,math,sys,time,json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'frames_final';OUT.mkdir(parents=True,exist_ok=True)
FPS=12;COUNT=32*FPS
bpy.ops.wm.open_mainfile(filepath=str(ROOT.parent/'ep02'/'MINSU_EP02.blend'))
scene=bpy.context.scene
for o in bpy.data.objects:
    o.animation_data_clear()
    if o.data and hasattr(o.data,'animation_data_clear'):o.data.animation_data_clear()
actor=bpy.data.objects['MINSU'];head=bpy.data.objects['head'];machine=bpy.data.objects['VENDING_MACHINE'];note=bpy.data.objects['NOTE'];hand=bpy.data.objects['CLOSEUP_HAND'];can=bpy.data.objects['CAN'];cam=scene.camera
arms=[bpy.data.objects['arm'],bpy.data.objects['arm.001']];legs=[bpy.data.objects['leg'],bpy.data.objects['leg.001']]
def col(h):
    a=[int(h[i:i+2],16)/255 for i in (0,2,4)]
    return tuple(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in a)+(1,)
palette=dict(ink='514B50',dark='776E72',teal='94CDBE',skin='FFF1DC',hair='947567',sole='F8EAD4',red='DA938C',yellow='F1CF7C',cream='FFF7DC',pave='D1CEC4',wall='D8DACD',trim='FAE8CE',glass='91B6BA',leaf='AAC3A1',leaf2='C2D2A8',pot='D4ADA0',metal='ACA9A1',white='FFF9E7')
for name,h in palette.items():
    m=bpy.data.materials.get(name)
    if not m:continue
    m.use_nodes=True
    m.node_tree.nodes.clear()
    p=m.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
    output=m.node_tree.nodes.new('ShaderNodeOutputMaterial')
    m.node_tree.links.new(p.outputs['BSDF'],output.inputs['Surface'])
    p.inputs['Base Color'].default_value=col(h);p.inputs['Roughness'].default_value=.67
    m.diffuse_color=col(h)
    if name=='metal':p.inputs['Metallic'].default_value=.28
def material(name,h,rough=.65):
    m=bpy.data.materials.new(name);m.use_nodes=True
    p=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None) or m.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
    output=next((n for n in m.node_tree.nodes if n.type=='OUTPUT_MATERIAL'),None) or m.node_tree.nodes.new('ShaderNodeOutputMaterial')
    m.node_tree.links.new(p.outputs['BSDF'],output.inputs['Surface']);p.inputs['Base Color'].default_value=col(h);p.inputs['Roughness'].default_value=rough;return m
pink=material('blush','F2A8A1');black=material('eye_black','332D32',.25)
def cube(name,loc,dims,mat,parent=None,bevel=.02):
    bpy.ops.mesh.primitive_cube_add(size=1);o=bpy.context.object;o.name=name;o.location=loc;o.dimensions=dims;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat);o.parent=parent
    if bevel:
        b=o.modifiers.new('soft edge','BEVEL');b.width=bevel;b.segments=3
        o.modifiers.new('weighted normals','WEIGHTED_NORMAL')
    return o
def ball(name,loc,scale,mat,parent=None):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8);o=bpy.context.object;o.name=name;o.parent=parent;o.location=loc;o.scale=scale;o.data.materials.append(mat)
    for p in o.data.polygons:p.use_smooth=True
    return o

# Keep original person identifiable, soften silhouette and make proportions distinctly chibi.
for o in list(head.children):
    if any(o.name.startswith(n) for n in ['eye','brow','nose','mouth']):bpy.data.objects.remove(o,do_unlink=True)
head.location=(0,0,1.38);head.scale=(1.65,1.65,1.55)
for o in head.children:
    if o.type=='MESH':
        o.modifiers.clear();b=o.modifiers.new('soft voxel corners','BEVEL');b.width=.105 if o.name.startswith('face') else .045;b.segments=4;o.modifiers.new('normals','WEIGHTED_NORMAL')
for x in [-.135,.135]:
    ball('round_eye',(x,-.244,-.015),(.04,.027,.055),black,head)
    ball('eye_spark',(x-.011,-.269,.003),(.012,.009,.014),bpy.data.materials['white'],head)
    ball('blush',(x*1.52,-.246,-.103),(.061,.012,.026),pink,head)
# A tiny, neutral w-shaped mouth.
curve=bpy.data.curves.new('tiny_mouth','CURVE');curve.dimensions='3D';curve.bevel_depth=.006;curve.bevel_resolution=2
sp=curve.splines.new('BEZIER');sp.bezier_points.add(4)
for p,xyz in zip(sp.bezier_points,[(-.043,-.257,-.123),(-.024,-.257,-.14),(0,-.257,-.123),(.024,-.257,-.14),(.043,-.257,-.123)]):p.co=xyz;p.handle_left_type='AUTO';p.handle_right_type='AUTO'
mouth=bpy.data.objects.new('tiny_mouth',curve);bpy.context.collection.objects.link(mouth);mouth.parent=head;curve.materials.append(black)
body=bpy.data.objects['teal_sweater'];body.location=(0,0,.78);body.scale=(1.2,1.2,.76)
bpy.data.objects['collar'].location=(0,-.22,1.0)
for o in [body,bpy.data.objects['collar']]:
    b=o.modifiers.new('soft clothing','BEVEL');b.width=.065;b.segments=3;o.modifiers.new('normals','WEIGHTED_NORMAL')
for i,o in enumerate(arms):o.location=((-.43 if i==0 else .43),0,1.0);o.scale=(1,.95,.70)
for i,o in enumerate(legs):o.location=((-.19 if i==0 else .19),0,.47);o.scale=(1.15,1.1,.60)
for o in list(actor.children_recursive):
    if o.type=='MESH' and not o.modifiers and o.parent!=head:
        b=o.modifiers.new('soft toy','BEVEL');b.width=.025;b.segments=2;o.modifiers.new('normals','WEIGHTED_NORMAL')
# Redesign the can as a squat, faceted cylinder.
for o in list(can.children):bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=.13,depth=.3);o=bpy.context.object;o.name='cherry_can';o.parent=can;o.location=(0,-.075,-.52);o.data.materials.append(bpy.data.materials['red'])
bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=.131,depth=.016);o=bpy.context.object;o.name='can_lid';o.parent=can;o.location=(0,-.075,-.363);o.data.materials.append(bpy.data.materials['metal'])
for x in [-.04,.04]:ball('cherry_mark',(x,-.199,-.53),(.037,.011,.039),bpy.data.materials['cream'],can)
# Paper closer to the viewer, anchored to the front rail.
note.location=(.18,.4,1.22)

# Distant architecture supplies depth behind reverse angles, instead of an empty world background.
cube('distant_shop',(6.0,-2.0,2.8),(.6,10,5.6),bpy.data.materials['wall'],bevel=.04)
for yy in [-5,-3.2,-1.4,.4]:
    for zz in [1.7,3.7]:
        cube('distant_window_frame',(5.65,yy,zz),(.09,1.4,1.4),bpy.data.materials['trim'],bevel=.025)
        cube('distant_window',(5.59,yy,zz),(.04,1.22,1.22),bpy.data.materials['glass'],bevel=.02)

# Physical lighting: soft window-side key, cool fill, subtle warm rim.
def area(name,loc,power,color,size,target):
    data=bpy.data.lights.new(name,'AREA');data.energy=power;data.color=color;data.shape='DISK';data.size=size
    o=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();return o
area('warm_key',(-3.5,-4.5,6),650,(1,.81,.64),4,(0,0,1))
area('sky_fill',(4,-1,4.5),380,(.67,.82,1),5,(0,0,1))
area('rim',(1.8,2.2,4.8),800,(1,.77,.57),3,(1,-1,1.4))
scene.world.use_nodes=True;bg=next(n for n in scene.world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs[0].default_value=(.62,.72,.83,1);bg.inputs[1].default_value=.20
scene.render.engine='BLENDER_EEVEE'
scene.eevee.taa_render_samples=16
scene.render.resolution_x=720;scene.render.resolution_y=1280;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB';scene.render.film_transparent=False
scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.view_settings.exposure=.5
scene.render.fps=FPS;scene.frame_start=1;scene.frame_end=COUNT
cam.data.type='PERSP';cam.data.sensor_fit='HORIZONTAL';cam.data.sensor_width=36;cam.data.dof.use_dof=True;cam.data.dof.aperture_blades=7
def s(x):x=max(0,min(1,x));return x*x*(3-2*x)
def mix(a,b,u):return Vector(a).lerp(Vector(b),s(u))
def camera(loc,target,lens=50,fstop=3.5,focus=None):
    cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens;cam.data.dof.aperture_fstop=fstop
    cam.data.dof.focus_distance=(Vector(focus if focus else target)-cam.location).length
def pose(t):
    past=5.5<=t<21
    machine.location.z=0 if past else -20
    note.location=(.18,.4,1.22 if not past else -20)
    actor.location=(1.22,-1.2,0);actor.rotation_euler=(0,0,-2.3)
    head.rotation_euler=(0,0,0)
    for a in arms+legs:a.rotation_euler=(0,0,0)
    hand.scale=(0,0,0);can.scale=(0,0,0)
    if t<1.25:
        camera(mix((2.12,-3.30,1.9),(1.95,-3.08,1.86),t/1.25),(.03,.32,1.14),45,4.0, (.18,.4,1.22))
        head.rotation_euler.z=.12*s(t/1.2)
    elif t<3.5:
        u=(t-1.25)/2.25;actor.location.x=5
        camera(mix((.45,-1.1,1.35),(.30,-1.04,1.3),u),(.18,.4,1.22),55,4.5)
    elif t<8.5:
        # Identical framing across the past/present cut.
        camera((2.75,-5.2,1.7),(.25,-.1,1.38),43,5.6)
        actor.location=(1.4,-1.02,0);actor.rotation_euler.z=-2.22
        head.rotation_euler.z=.15*s((t-5.5)/2)
    elif t<12:
        actor.location.x=5
        u=(t-8.5)/3.5
        camera(mix((-.44,-1.86,1.70),(.24,-1.86,1.70),u),(0,-.50,1.50),48,7)
    elif t<14:
        # A glance motivates the next detail shot.
        camera((-.5,-.85,1.8),(1.22,-1.2,1.38),43,3.5)
        head.rotation_euler.z=.08-.2*s((t-12)/2)
    elif t<16:
        actor.location.x=5;hand.scale=(1,1,1)
        u=(t-14)/2;hand.location=(.10,-.91+.20*s(u/.7),1.15)
        camera((.58,-2.0,1.81),(0,-.50,1.45),50,5.6)
    elif t<17.5:
        actor.location.x=5;can.parent=None;can.scale=(1,1,1);can.rotation_euler=(0,0,0)
        can.location=(.02,-.57,.89-.12*s((t-16)/.45))
        camera((.55,-1.87,.65),(0,-.5,.37),60,4.0)
    elif t<21:
        can.parent=arms[0];can.location=(0,0,0);can.scale=(1,1,1);can.rotation_euler=(0,0,.5*s((t-17.5)/2))
        actor.rotation_euler.z=-.65
        arms[0].rotation_euler.x=-1.15;head.rotation_euler.x=.14
        camera(mix((2.7,-4.5,1.7),(2.4,-4.1,1.68),(t-17.5)/3.5),(1.07,-1.13,1.20),65,3.2)
    elif t<24:
        can.parent=arms[0];can.location=(0,0,0)
        camera((2.75,-5.2,1.7),(.25,-.1,1.38),43,5.6)
        u=t-21;actor.location=(1.4+.25*(1-s(u)), -1.02-.55*(1-s(u)),0)
        actor.rotation_euler.z=-2.22
        if u<1:
            legs[0].rotation_euler.x=.25*math.sin(u*7);legs[1].rotation_euler.x=-.25*math.sin(u*7)
        head.rotation_euler.z=.12*s(u)
    elif t<27:
        actor.location=(1.22,-1.2,0)
        camera((-.5,-.85,1.8),(1.22,-1.2,1.38),43,3.5)
        head.rotation_euler.z=.16*s((t-24)/2)
    elif t<30:
        actor.location.x=5
        camera(mix((.45,-1.1,1.35),(.30,-1.04,1.3),(t-27)/3),(.18,.4,1.22),55,4.5)
    else:
        # Ending OTS is the same spatial anchor as the opening.
        u=(t-30)/2
        camera(mix((2.3,-3.55,1.95),(2.12,-3.30,1.9),u),(.03,.32,1.14),45,4,(.18,.4,1.22))
    return [machine,note,actor,head,hand,can,cam]+arms+legs

# Parent-switching is not safely keyframeable: retain one parent and use world matrix for hatch insert.
def resolved_pose(t):
    objects=pose(t)
    if can.parent is None:
        bpy.context.view_layer.update();world=can.matrix_world.copy();can.parent=arms[0];bpy.context.view_layer.update();can.matrix_world=world
    return objects

PREVIEW=[0,.9,2,4.5,6.5,10,12.8,15,16.7,19,22,25,28.2,31.9]
for f in range(1,COUNT+1):
    for o in resolved_pose((f-1)/FPS):
        for prop in ['location','rotation_euler','scale']:o.keyframe_insert(data_path=prop,frame=f)
    for prop in ['lens','dof.aperture_fstop','dof.focus_distance']:cam.data.keyframe_insert(data_path=prop,frame=f)
scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'MINSU_CINEMA_CUTE.blend'))
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
frames=[int(t*FPS)+1 for t in PREVIEW] if '--preview' in args else range(1,COUNT+1)
if '--test' in args:frames=[int(12.8*FPS)+1,int(6.5*FPS)+1]
start=time.time()
for f in frames:
    path=OUT/f'{f:05d}.png'
    if '--resume' in args and path.exists():continue
    scene.frame_set(f);scene.render.filepath=str(path);bpy.ops.render.render(write_still=True)
    print(f'FRAME {f}/{COUNT} seconds={time.time()-start:.1f}',flush=True)
print('RENDER_COMPLETE',flush=True)
