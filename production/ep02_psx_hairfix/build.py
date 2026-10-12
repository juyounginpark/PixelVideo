"""Rebuild Minsu as a clean low-poly block avatar, then render a PSX presentation."""
import bpy, math, sys, time, json, hashlib, shutil
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'frames';OUT.mkdir(parents=True,exist_ok=True)
BASE=ROOT.parent/'ep02_cinema'
bpy.ops.wm.open_mainfile(filepath=str(BASE/'MINSU_CINEMA_CUTE.blend'))
scene=bpy.context.scene;cam=scene.camera
actor=bpy.data.objects['MINSU'];oldhead=bpy.data.objects['head'];oldarms=[bpy.data.objects['arm'],bpy.data.objects['arm.001']];oldlegs=[bpy.data.objects['leg'],bpy.data.objects['leg.001']];can=bpy.data.objects['CAN'];hand=bpy.data.objects['CLOSEUP_HAND']
FPS=12;COUNT=384
motion=[]
for f in range(1,COUNT+1):
    scene.frame_set(f)
    motion.append(dict(actor=tuple(actor.location),rot=tuple(actor.rotation_euler),head=tuple(oldhead.rotation_euler),arms=[tuple(o.rotation_euler) for o in oldarms],legs=[tuple(o.rotation_euler) for o in oldlegs],can_scale=tuple(can.scale),can_world=[list(r) for r in can.matrix_world]))
can.parent=None
keep={can,*can.children_recursive}
for o in list(actor.children_recursive):
    if o not in keep:bpy.data.objects.remove(o,do_unlink=True)
actor.animation_data_clear();can.animation_data_clear()
def rgba(h):
    a=[int(h[i:i+2],16)/255 for i in (0,2,4)]
    return tuple(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in a)+(1,)
def mat(name,h,rough=.88):
    m=bpy.data.materials.new(name);m.use_nodes=True;m.node_tree.nodes.clear()
    p=m.node_tree.nodes.new('ShaderNodeBsdfPrincipled');p.inputs['Base Color'].default_value=rgba(h);p.inputs['Roughness'].default_value=rough
    p.inputs['Specular IOR Level'].default_value=.18
    out=m.node_tree.nodes.new('ShaderNodeOutputMaterial');m.node_tree.links.new(p.outputs['BSDF'],out.inputs['Surface']);m.diffuse_color=rgba(h);return m
M={k:mat('LP_'+k,c) for k,c in dict(skin='E3B68F',skinshade='C99673',hair='302D31',hairlight='49404A',eye='24232B',jacket='4D8587',jacketlight='689D9B',rib='365E68',shirt='E7DED0',pants='343D50',pantslight='465267',sole='D9D3C4',shoe='4C5E71',lace='C8C6BC',metal='A6ACA5').items()}
def emp(name,loc,parent=actor):
    o=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(o);o.parent=parent;o.location=loc;return o
def box(name,loc,dims,material,parent=actor,bevel=.012,segments=1):
    bpy.ops.mesh.primitive_cube_add(size=1);o=bpy.context.object;o.name=name;o.parent=parent;o.location=loc;o.dimensions=dims;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(M[material])
    if bevel:
        b=o.modifiers.new('edge bevel','BEVEL');b.width=bevel;b.segments=segments
        o.modifiers.new('weighted normals','WEIGHTED_NORMAL')
    return o
def mesh(name,verts,faces,material,parent=actor):
    data=bpy.data.meshes.new(name);data.from_pydata(verts,[],faces);data.update();o=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(o);o.parent=parent;o.data.materials.append(M[material]);return o
def line(name,points,material,parent,radius=.009):
    c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.bevel_depth=radius;c.bevel_resolution=0;c.resolution_u=4
    sp=c.splines.new('POLY');sp.points.add(len(points)-1)
    for p,co in zip(sp.points,points):p.co=(*co,1)
    o=bpy.data.objects.new(name,c);bpy.context.collection.objects.link(o);o.parent=parent;o.data.materials.append(M[material]);return o

# Four-head proportions; a coherent jacket silhouette, separate neck and articulated block limbs.
box('pelvis',(0,0,.87),(.64,.39,.20),'pants')
verts=[(-.32,-.21,.93),(.32,-.21,.93),(.32,.21,.93),(-.32,.21,.93),(-.42,-.24,1.57),(.42,-.24,1.57),(.42,.24,1.57),(-.42,.24,1.57)]
torso=mesh('tailored_jacket',verts,[(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7),(3,2,1,0)],'jacket')
b=torso.modifiers.new('clean edge','BEVEL');b.width=.018;b.segments=1;torso.modifiers.new('weighted normals','WEIGHTED_NORMAL')
box('waist_rib',(0,-.002,.96),(.67,.435,.085),'rib')
box('undershirt',(0,-.253,1.49),(.18,.023,.15),'shirt',bevel=.004)
box('neck',(0,0,1.60),(.25,.25,.18),'skin',bevel=.022,segments=2)
# Hood and slanted collar panels.
box('hood_back',(0,.22,1.52),(.57,.22,.26),'rib',bevel=.065,segments=2)
for side in [-1,1]:
    o=box('collar',(.15*side,-.26,1.52),(.12,.05,.17),'jacketlight',bevel=.008);o.rotation_euler.y=-.32*side
    o=box('welt_pocket',(.20*side,-.238,1.14),(.17,.022,.026),'rib',bevel=.002);o.rotation_euler.y=.2*side
    box('pocket_seam',(.20*side,-.243,1.10),(.17,.012,.015),'jacketlight',bevel=.001)
box('zipper',(0,-.254,1.19),(.018,.018,.37),'metal',bevel=.002)
box('zip_pull',(0,-.276,1.36),(.038,.027,.058),'metal',bevel=.004)
box('chest_patch',(.22,-.26,1.40),(.105,.018,.071),'shirt',bevel=.005)
box('patch_stripe',(.22,-.271,1.40),(.056,.009,.016),'rib',bevel=0)

head=emp('LP_head',(0,0,1.89))
box('head_mesh',(0,0,0),(.63,.56,.56),'skin',head,.075,3)
for x in [-.12,.12]:
    # Discrete flat black eyes, not spherical glossy buttons.
    n=10;verts=[(x+math.cos(i*math.tau/n)*.031,-.286,math.sin(i*math.tau/n)*.047+.025) for i in range(n)]
    mesh('eye_decal',verts,[tuple(range(n))],'eye',head)
    line('brow',[(x-.042,-.286,.115),(x+.036,-.286,.122)],'hair',head,.008)
line('mouth',[(-.068,-.286,-.112),(-.035,-.289,-.13),(0,-.29,-.136),(.035,-.289,-.13),(.068,-.286,-.112)],'eye',head,.008)
# Small ears, no protruding nose or blush.
for side in [-1,1]:box('ear',(.325*side,0,-.015),(.07,.15,.16),'skin',head,.025,2)

# Continuous low-poly hair cap with diagonal swept locks; no separate marshmallow blocks.
n=32;verts=[]
# Rounded square cross-section follows the beveled rectangular skull.
for ring in range(4):
    for i in range(n):
        a=i*math.tau/n
        x=math.copysign(abs(math.cos(a))**.4,math.cos(a))
        y=math.copysign(abs(math.sin(a))**.4,math.sin(a))
        if ring==0:
            z=.145 if y<-.85 else (-.19 if y>.4 else -.08)
            rx,ry=.339,.308
        elif ring==1:z=.25;rx,ry=.350,.321
        elif ring==2:z=.335+.025*x;rx,ry=.285,.263
        else:z=.382+.018*x;rx,ry=.125,.12
        verts.append((x*rx,y*ry,z))
faces=[]
for r in range(3):
    for i in range(n):faces.append((r*n+i,r*n+(i+1)%n,(r+1)*n+(i+1)%n,(r+1)*n+i))
faces.append(tuple(range(3*n,4*n)))
hair=mesh('fitted_hair_shell',verts,faces,'hair',head)
hair.data.materials.append(M['hairlight'])
# Swept fringe roots overlap the shell; tips remain above the eyebrows.
for j,(x0,x1,z0,z1) in enumerate([(-.32,-.12,.15,.12),(-.14,.09,.12,.16),(.07,.29,.16,.22)]):
    v=[(x0,-.27,.30),(x1,-.27,.32),(x1,-.326,z1),(x0,-.326,z0),(x0,-.235,.31),(x1,-.235,.33),(x1,-.295,z1+.025),(x0,-.295,z0+.025)]
    mesh('integrated_fringe',v,[(0,1,2,3),(0,4,5,1),(3,2,6,7),(1,5,6,2),(0,3,7,4)],'hair',head)

arms=[];legs=[]
for side in [-1,1]:
    a=emp('LP_arm',(.53*side,0,1.49));arms.append(a)
    box('upper_sleeve',(0,0,-.20),(.27,.36,.43),'jacket',a,.018)
    box('elbow_band',(0,0,-.414),(.26,.345,.055),'jacketlight',a,.008)
    box('fore_sleeve',(0,-.008,-.535),(.25,.325,.23),'jacket',a,.014)
    box('cuff',(0,-.008,-.665),(.26,.33,.08),'rib',a,.009)
    box('hand',(0,-.015,-.787),(.25,.29,.18),'skin',a,.036,2)
    box('thumb',(-side*.14,-.08,-.77),(.085,.13,.12),'skin',a,.018)
    leg=emp('LP_leg',(.185*side,0,.88));legs.append(leg)
    box('trouser',(0,0,-.335),(.30,.34,.65),'pants',leg,.012)
    box('outer_seam',(.15*side,.005,-.335),(.013,.25,.55),'pantslight',leg,.001)
    box('trouser_hem',(0,0,-.648),(.31,.35,.07),'pantslight',leg,.009)
    box('sneaker',(0,-.08,-.745),(.34,.52,.17),'shoe',leg,.035,2)
    box('sole',(0,-.08,-.84),(.35,.54,.055),'sole',leg,.012)
    box('toe_cap',(0,-.335,-.745),(.31,.09,.11),'sole',leg,.025,2)
    for zz,yy in [(-.65,-.16),(-.65,-.09),(-.65,-.02)]:box('lace',(0,yy,zz),(.17,.017,.014),'lace',leg,.002)
    box('heel_tab',(0,.175,-.69),(.115,.028,.075),'rib',leg,.004)

# Match the first-person insert to the new skin and sleeve design.
for o in list(hand.children):bpy.data.objects.remove(o,do_unlink=True)
box('insert_palm',(0,0,0),(.23,.16,.24),'skin',hand,.025,2)
box('insert_index',(-.06,.08,.18),(.08,.14,.27),'skin',hand,.018,2)
box('insert_thumb',(.14,-.01,.01),(.10,.13,.16),'skin',hand,.025,2)
box('insert_cuff',(0,-.01,-.17),(.27,.22,.105),'rib',hand,.008)
box('insert_sleeve',(0,-.01,-.30),(.28,.24,.18),'jacket',hand,.012)

# Add sparse, point-filtered fabric texels. Geometry and silhouette carry the design.
for key in ['jacket','pants','hair']:
    material=M[key];p=next(n for n in material.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    base=list(p.inputs['Base Color'].default_value);pixels=[]
    for yy in range(16):
        for xx in range(16):
            factor=.91 if (xx*7+yy*11)%29==0 else 1
            pixels.extend([base[0]*factor,base[1]*factor,base[2]*factor,1])
    img=bpy.data.images.new('PSX_'+key,width=16,height=16);img.pixels=pixels;img.pack();img.colorspace_settings.name='Non-Color'
    texture=material.node_tree.nodes.new('ShaderNodeTexImage');texture.image=img;texture.interpolation='Closest';texture.projection='BOX';texture.projection_blend=0
    coord=material.node_tree.nodes.new('ShaderNodeTexCoord');material.node_tree.links.new(coord.outputs['Generated'],texture.inputs['Vector']);material.node_tree.links.new(texture.outputs['Color'],p.inputs['Base Color'])

# Preserve story blocking, adapt the character proportions and hand-held prop position.
for f,state in enumerate(motion,1):
    scene.frame_set(f);t=(f-1)/FPS
    actor.location=state['actor'];actor.rotation_euler=state['rot'];head.rotation_euler=state['head']
    def ease(x):x=max(0,min(1,x));return x*x*(3-2*x)
    if 12<=t<14:head.rotation_euler.z=.16-.33*ease((t-12)/.5)
    elif 24<=t<27:head.rotation_euler.z=.28*ease((t-24)/.35)-.40*ease((t-25)/.4)
    if 14<=t<16:
        hand.location.y=-.91+.20*ease((t-14.55)/.28)
        hand.keyframe_insert(data_path='location',frame=f)
    depth=.024*ease((t-14.65)/.14) if 14<=t<16 else 0
    for name,y in [('button.003',-.548),('button_label.003',-.574)]:
        b=bpy.data.objects.get(name)
        if b:b.location.y=y+depth;b.keyframe_insert(data_path='location',frame=f)
    for o,r in zip(arms,state['arms']):o.rotation_euler=r
    for o,r in zip(legs,state['legs']):o.rotation_euler=r
    for o in [actor,head,*arms,*legs]:
        for prop in ['location','rotation_euler','scale']:o.keyframe_insert(data_path=prop,frame=f)
    can.parent=None
    if 17.5<=t<21:
        bpy.context.view_layer.update()
        # Keep the can at the new hand, not the obsolete chibi arm length.
        can.matrix_world=arms[0].matrix_world @ Matrix.Translation((0,-.04,-.29));can.scale=(1,1,1)
    else:
        can.matrix_world=Matrix(state['can_world']);can.scale=state['can_scale']
    for prop in ['location','rotation_euler','scale']:can.keyframe_insert(data_path=prop,frame=f)
    if 12<=t<14 or 24<=t<27:
        target=Vector((1.22,-1.2,1.65));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
    elif 17.5<=t<21:
        target=Vector((.99,-1.12,1.40));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=55;cam.data.keyframe_insert(data_path='lens',frame=f)
    cam.keyframe_insert(data_path='rotation_euler',frame=f)

scene.frame_set(1);scene.render.engine='BLENDER_EEVEE';scene.eevee.taa_render_samples=24
scene.render.resolution_x=360;scene.render.resolution_y=640;scene.render.resolution_percentage=100
cam.data.dof.use_dof=False;scene.view_settings.exposure=.05
scene.render.fps=FPS;scene.frame_start=1;scene.frame_end=COUNT
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'MINSU_LOWPOLY_PSX.blend'))
dg=bpy.context.evaluated_depsgraph_get();triangles=0
for obj in actor.children_recursive:
    if obj.type in ['MESH','CURVE']:
        evaluated=obj.evaluated_get(dg);geometry=evaluated.to_mesh();geometry.calc_loop_triangles();triangles+=len(geometry.loop_triangles);evaluated.to_mesh_clear()
(ROOT/'model_stats.json').write_text(json.dumps({'character_triangles_after_modifiers':triangles,'source_animation_fps':FPS,'render_size':[360,640],'output_size':[720,1280]},indent=2),encoding='utf-8')
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []

if '--studio' in args:
    for o in bpy.data.objects:
        if o.type not in ['LIGHT','CAMERA'] and o not in {actor,*actor.children_recursive} and o.name!='sidewalk':o.hide_render=True
    actor.animation_data_clear();actor.location=(0,0,0);actor.rotation_euler=(0,0,0)
    for o in [head,*arms,*legs]:o.animation_data_clear();o.rotation_euler=(0,0,0)
    cam.animation_data_clear();cam.data.animation_data_clear();can.hide_render=True
    scene.render.resolution_x=720;scene.render.resolution_y=960;scene.eevee.taa_render_samples=64
    scene.view_settings.exposure=.3
    for name,loc,target,lens in [('threequarter',(3.6,-6,2.8),(0,0,1.12),85),('front',(0,-6.5,2.1),(0,0,1.12),85),('back',(3.6,6,2.8),(0,0,1.12),85),('face',(1.2,-3,2.1),(0,0,1.86),90)]:
        cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens
        scene.render.filepath=str(ROOT/f'model_{name}.png');bpy.ops.render.render(write_still=True)
    print('STUDIO_COMPLETE',flush=True);sys.exit()

frames=[1,79,154,181,229,301,383] if '--preview' in args else range(1,COUNT+1)
cache={};start=time.time()
for f in frames:
    target=OUT/f'{f:05d}.png'
    if '--resume' in args and target.exists():continue
    scene.frame_set(f)
    # Exact transform duplicates can reuse a rendered frame without changing motion.
    signature=[]
    for o in sorted(bpy.data.objects,key=lambda x:x.name):
        if o.type!='LIGHT':signature.extend(round(v,6) for row in o.matrix_world for v in row)
    signature.extend([cam.data.lens])
    key=hashlib.sha1(str(signature).encode()).hexdigest()
    if key in cache:shutil.copyfile(cache[key],target)
    else:
        scene.render.filepath=str(target);bpy.ops.render.render(write_still=True);cache[key]=target
    print(f'FRAME {f}/{COUNT} elapsed={time.time()-start:.1f}',flush=True)
print('RENDER_COMPLETE',flush=True)
