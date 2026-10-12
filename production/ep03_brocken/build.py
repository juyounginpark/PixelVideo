import bpy, math, sys, hashlib, shutil, time
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent;O=R/'frames';O.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R.parent/'ep02_pet/MINSU_PET_TOON.blend'))
s=bpy.context.scene;actor=bpy.data.objects['MINSU'];cam=s.camera
keep={actor,*actor.children_recursive,cam}
for o in list(bpy.data.objects):
    if o not in keep:bpy.data.objects.remove(o,do_unlink=True)
for o in keep:
    o.animation_data_clear()
    if o.data and hasattr(o.data,'animation_data_clear'):o.data.animation_data_clear()
actor.location=(0,0,0);actor.rotation_euler=(0,0,math.pi)
head=bpy.data.objects['LP_head'];arms=[bpy.data.objects['LP_arm'],bpy.data.objects['LP_arm.001']]
legs=[bpy.data.objects['LP_leg'],bpy.data.objects['LP_leg.001']]
for o in [head,*arms,*legs]:o.rotation_euler=(0,0,0)
# Neutral, slightly tense mouth instead of the previous episode's fixed smile.
mouth=bpy.data.objects.get('mouth')
if mouth and mouth.type=='CURVE':
    for spline in mouth.data.splines:
        for p in spline.points:p.co.z=-.12
for o in list(actor.children_recursive):
    if o.name.startswith('CAN'):bpy.data.objects.remove(o,do_unlink=True)
def mat(name,color,emit=False):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;n=m.node_tree.nodes;n.clear();out=n.new('ShaderNodeOutputMaterial')
    if emit:
        sh=n.new('ShaderNodeEmission');sh.inputs[0].default_value=(*color,1)
    else:
        sh=n.new('ShaderNodeBsdfDiffuse');sh.inputs[0].default_value=(*color,1)
    m.node_tree.links.new(sh.outputs[0],out.inputs[0]);return m
rock=mat('slate',(.13,.23,.25));top=mat('moss',(.24,.35,.31));mist=mat('mist',(.32,.47,.50),True);dark=mat('shadow in mist',(.095,.19,.23),True)
def ico(name,loc,scale,m):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=1,location=loc);o=bpy.context.object;o.name=name;o.scale=scale;o.data.materials.append(m);return o
ico('ridge',(0,-1,-.75),(3.5,4,.85),top)
for i,(x,y,z) in enumerate([(-3,1,-1),(3,2,-1),(-2,-3,-1),(1,-3,-1)]):ico('rock',(x,y,z),(2,2,1.8),rock)
for i in range(8):ico('distant ridge',(-20+i*6,24+(i%2)*5,-2),(7,5,5+(i%3)),mat('far'+str(i),(.22+i*.008,.35+i*.006,.40+i*.004),True))
# Backdrop plane is atmospheric scenery, not a physical wall in the story.
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,35,12),rotation=(math.pi/2,0,0));bpy.context.object.data.materials.append(mist)
sunmat=mat('warm sun',(1,.77,.37),True);ico('sun',(-7,-7,9),(.65,.65,.65),sunmat)
world=s.world;world.use_nodes=True
bg=next(n for n in world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs[0].default_value=(.40,.52,.58,1);bg.inputs[1].default_value=.65
bpy.ops.object.light_add(type='SUN',location=(-4,-6,8));light=bpy.context.object;light.rotation_euler=(.5,-.5,-.5);light.data.energy=2.5;light.data.angle=.12
bpy.ops.object.light_add(type='AREA',location=(1,-5,5));light=bpy.context.object;light.data.energy=350;light.data.shape='DISK';light.data.size=5;light.rotation_euler=(Vector((0,0,1))-light.location).to_track_quat('-Z','Y').to_euler()
# A flat, atmospheric silhouette is driven by the SAME poses as Minsu.
shadowroot=bpy.data.objects.new('projected_silhouette',None);bpy.context.collection.objects.link(shadowroot)
mapping={actor:shadowroot}
children=list(actor.children_recursive)
for o in children:
    c=o.copy()
    if o.data:c.data=o.data.copy()
    bpy.context.collection.objects.link(c);mapping[o]=c;c.animation_data_clear()
for o,c in list(mapping.items())[1:]:
    c.parent=mapping[o.parent];c.matrix_parent_inverse=o.matrix_parent_inverse.copy()
    if c.type in ['MESH','CURVE']:c.data.materials.clear();c.data.materials.append(dark)
shadowroot.scale=(2.4,.035,2.4);shadowroot.location=(0,7,.2);shadowroot.rotation_euler=(0,0,math.pi)
# A restrained glory centered behind the head, seen from near the observer axis.
# Omit the glory from the stylized off-axis shots. The real photograph shows it;
# an off-axis decorative ring would misrepresent its observer-centered geometry.
cam.data.type='PERSP';cam.data.lens=43;cam.data.dof.use_dof=False
s.render.engine='BLENDER_EEVEE';s.eevee.taa_render_samples=24;s.render.resolution_x=360;s.render.resolution_y=640;s.render.resolution_percentage=100;s.render.fps=12
s.view_settings.view_transform='Standard';s.view_settings.look='None';s.view_settings.exposure=0
def ease(t):t=max(0,min(1,t));return t*t*(3-2*t)
def pose(t):
    actor.location=(0,0,0);actor.rotation_euler=(0,0,math.pi)
    for o in [head,*arms,*legs]:o.rotation_euler=(0,0,0)
    arm=1.9*ease(t/.6) if t<4 else 0
    if 4<=t<6:arm=1.9
    if 6<=t<10:head.rotation_euler.z=.65*ease((t-6)/.4);actor.rotation_euler.z=2.55
    if 10<=t<15:
        actor.location.x=.7*math.sin((t-10)*1.5);arms[0].rotation_euler.x=.2*math.sin(t*6);legs[0].rotation_euler.x=.25*math.sin(t*6);legs[1].rotation_euler.x=-legs[0].rotation_euler.x
    if 15<=t<19:
        crouch=math.sin(min(1,(t-15)/2)*math.pi)*.45;actor.location.z=-crouch;actor.rotation_euler.x=.28*crouch/.45
    arms[1].rotation_euler.y=-arm
    shadowroot.location.x=actor.location.x*2.4;shadowroot.location.z=.2+actor.location.z*2.4;shadowroot.rotation_euler=actor.rotation_euler
    for o,c in list(mapping.items())[1:]:c.location=o.location;c.rotation_euler=o.rotation_euler;c.scale=o.scale
    if 6<=t<10:
        cam.location=(3,4,2.7);target=(0,0,1.55);cam.data.lens=56
    elif 19<=t<23:
        q=ease((t-19)/3);cam.location=(8-3*q,-7-4*q,5+2*q);target=(0,3,2.1);cam.data.lens=36
    else:
        cam.location=(2.8,-9.5,4.5);target=(0,3.5,2.65);cam.data.lens=53
    cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
    bpy.context.view_layer.update()

for f in range(1,277):
    pose((f-1)/12)
    for o in [actor,head,*arms,*legs,shadowroot,*mapping.values(),cam]:
        for p in ['location','rotation_euler','scale']:o.keyframe_insert(data_path=p,frame=f)
    cam.data.keyframe_insert(data_path='lens',frame=f)
s.frame_start=1;s.frame_end=276;s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(R/'MINSU_BROCKEN.blend'))
frames=[1,20,80,135,195,253] if '--preview' in sys.argv else range(1,277)
cache={};start=time.time()
for f in frames:
    s.frame_set(f);target=O/f'{f:05d}.png'
    sig=[round(v,5) for o in sorted(bpy.data.objects,key=lambda x:x.name) for row in o.matrix_world for v in row]+[cam.data.lens]
    key=hashlib.sha1(str(sig).encode()).hexdigest()
    if key in cache:shutil.copyfile(cache[key],target)
    else:s.render.filepath=str(target);bpy.ops.render.render(write_still=True);cache[key]=target
    print(f'FRAME {f}/276 {time.time()-start:.1f}s',flush=True)
print('RENDER_COMPLETE',flush=True)
