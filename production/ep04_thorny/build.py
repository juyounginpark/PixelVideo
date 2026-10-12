"""Native 30fps voxel observation cutscene. External surface water is schematic."""
import bpy, math, json, sys, time
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent
OUT=R/'frames';OUT.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R.parent/'ep03_brocken_v2/MINSU_BROCKEN_ACTION.blend'))
s=bpy.context.scene;s.frame_set(1)
actor=bpy.data.objects['MINSU'];keep={actor,*actor.children_recursive}
for o in list(bpy.data.objects):
    if o not in keep:bpy.data.objects.remove(o,do_unlink=True)
for o in keep:
    o.animation_data_clear()
    if o.data and hasattr(o.data,'animation_data_clear'):o.data.animation_data_clear()
    o.hide_render=False
head=bpy.data.objects['LP_head']
arms=[bpy.data.objects[n] for n in ['LP_arm','LP_arm.001']]
elbows=[bpy.data.objects[n] for n in ['elbow','elbow.001']]
legs=[bpy.data.objects[n] for n in ['LP_leg','LP_leg.001']]
knees=[bpy.data.objects[n] for n in ['knee','knee.001']]
for a in arms:a.location.x=math.copysign(.415,a.location.x)
eyes=[o for o in head.children if o.name.startswith('eye_decal')]
eye_scales=[o.scale.copy() for o in eyes]

def material(name,color,emission=False):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
    n=m.node_tree.nodes;n.clear();out=n.new('ShaderNodeOutputMaterial')
    if emission:
        bs=n.new('ShaderNodeEmission');bs.inputs[0].default_value=(*color,1);bs.inputs[1].default_value=.85
    else:
        bs=n.new('ShaderNodeBsdfDiffuse');bs.inputs['Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=.75
    m.node_tree.links.new(bs.outputs[0],out.inputs[0]);return m
sand=material('game sand',(.68,.40,.18));rock=material('sandstone',(.47,.29,.16))
ochre=material('thorny scale ochre',(.57,.32,.13));amber=material('thorny scale gold',(.78,.51,.23))
cream=material('thorny scale pale',(.86,.65,.34));brown=material('thorny spine tips',(.24,.12,.065))
black=material('game eye black',(.025,.026,.035));water=material('water game blue',(.14,.53,.66))
cyan=material('water route highlight',(.17,.88,.89),True)
base=material('skin cross section',(.43,.25,.12))
def empty(name,loc=(0,0,0),parent=None):
    o=bpy.data.objects.new(name,None);s.collection.objects.link(o);o.parent=parent;o.location=loc;return o
def mesh(name,verts,faces,mat,parent=None):
    me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update()
    o=bpy.data.objects.new(name,me);s.collection.objects.link(o);o.parent=parent;me.materials.append(mat)
    for p in me.polygons:p.use_smooth=False
    return o
def box(name,loc,dim,mat,parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1);o=bpy.context.object;o.name=name;o.parent=parent;o.location=loc;o.scale=dim;o.data.materials.append(mat);return o
def cone(name,loc,radius,height,mat,parent=None,rotation=(0,0,0)):
    bpy.ops.mesh.primitive_cone_add(vertices=4,radius1=radius,radius2=0,depth=height)
    o=bpy.context.object;o.name=name;o.parent=parent;o.location=loc;o.rotation_euler=rotation;o.data.materials.append(mat);return o
def stone(name,loc,scale,mat):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=1,location=loc);o=bpy.context.object;o.name=name;o.scale=scale;o.data.materials.append(mat);return o
ground=box('desert floor',(0,0,-.06),(80,80,.12),sand)
# Sparse, deliberately subordinate environment, no tropical or cactus motifs.
for i in range(22):
    a=i*2.399;rad=2.8+(i%5)*1.1
    stone('lowpoly sandstone',(math.sin(a)*rad,math.cos(a)*rad,.10),(.15+(i%3)*.08,.19,.12),rock)
for i in range(9):
    x=-3.0+(i%3)*2.6;y=2.5+(i//3)*2.8
    for j in range(3):cone('dry grass',(x+j*.1,y,.20),.035,.4,cream,rotation=(0,.2*(j-1),0))

# One canonical animal asset: squat body, angular horns, false-head hump, spiked tail.
animal=empty('THORNY_DEVIL');animal.scale=(.25,)*3
body=empty('lizard body',(0,0,.16),animal)
verts=[]
for y,w,zmid in [(-.30,.20,.09),(0,.26,.13),(.32,.20,.10)]:
    for a in range(8):
        angle=a*math.tau/8;verts.append((w*math.cos(angle),y,zmid+.13*math.sin(angle)))
faces=[]
for row in range(2):
    for j in range(8):faces.append((row*8+j,row*8+(j+1)%8,(row+1)*8+(j+1)%8,(row+1)*8+j))
faces.extend([tuple(range(7,-1,-1)),tuple(range(16,24))])
torso=mesh('angular spiny torso',verts,faces,ochre,body)
torso.data.materials.append(amber);torso.data.materials.append(cream)
for p in torso.data.polygons:p.material_index=p.index%3
lhead=empty('lizard head',(0,-.41,.20),body)
box('horned head',(0,-.035,0),(.29,.29,.17),amber,lhead)
box('snout',(0,-.18,-.03),(.23,.13,.09),ochre,lhead)
for sign in (-1,1):
    cone('supraocular horn',(sign*.115,.04,.115),.065,.21,brown,lhead,rotation=(0,sign*.22,0))
    box('lizard eye',(sign*.149,-.09,.027),(.018,.06,.035),black,lhead)
    cone('cheek spine',(sign*.15,-.02,-.015),.037,.12,brown,lhead,rotation=(0,sign*1.0,0))
jaw=empty('drinking jaw',(0,-.04,-.095),lhead)
lizard_eyes=[o for o in lhead.children if o.name.startswith('lizard eye')]
lizard_eye_scales=[o.scale.copy() for o in lizard_eyes]
box('lower jaw',(0,-.085,0),(.22,.22,.048),cream,jaw)
cone('false head hump',(0,.25,.20),.105,.18,ochre,lhead)
for row in range(7):
    y=-.24+row*.09
    for col in range(-2,3):
        x=col*.085;h=.085+.05*((row+col)%3)/2
        z=.21-.21*abs(x)+.018*(row%2)
        cone('dorsal scale spine',(x,y,z+h/2),.043,h,brown if (row+col)%4==0 else amber,body,rotation=(col*.10,0,0))
for sign in (-1,1):
    for i in range(6):cone('lateral spine',(sign*.235,-.22+i*.09,.10),.045,.14,ochre,body,rotation=(0,sign*1.18,0))
tail=empty('tail articulation',(0,.29,.04),body)
for i in range(8):
    w=.13*(1-i/9);y=.05+i*.10;z=.012+i*i*.009
    box('tail segment',(0,y,z),(w,.13,w*.6),amber if i%2==0 else ochre,tail)
    cone('tail spine',(0,y,z+w*.65),w*.38,.095,brown,tail)
feet=[];limbs=[]
for sign in (-1,1):
    for row,y in enumerate((-.21,.24)):
        leg=empty('splayed leg',(sign*.20,y,.075),body);limbs.append(leg)
        upper=box('leg segment',(sign*.07,.03 if row==0 else -.03,-.045),(.19,.075,.07),ochre,leg)
        upper.rotation_euler.z=sign*(.35 if row==0 else -.35)
        box('lower leg connecting joint',(sign*.13,-.035 if row==0 else .035,-.13),(.055,.065,.14),ochre,leg)
        foot=empty('lizard foot',(sign*.13,-.035 if row==0 else .035,-.19),leg);feet.append(foot)
        box('ankle',(0,0,.018),(.055,.08,.055),amber,foot)
        for j in range(4):
            toe=box('tiny toe',(sign*(.028+j*.012),-.047+j*.022,-.008),(.085,.018,.018),cream,foot)
            toe.rotation_euler.z=(j-1.5)*.23
# Discrete small skin plates, not smooth plastic. 16px checker texture, nearest sampled.
im=bpy.data.images.new('desert scales 16px',width=16,height=16)
pixels=[]
for yy in range(16):
    for xx in range(16):
        v=[.70,.83,.95][(xx//3+yy//4)%3];pixels.extend((v,v*.70,v*.37,1))
im.pixels=pixels;im.pack()
for ma in (ochre,amber):
    nodes=ma.node_tree.nodes;tex=nodes.new('ShaderNodeTexImage');tex.image=im;tex.interpolation='Closest'
    coord=nodes.new('ShaderNodeTexCoord');ma.node_tree.links.new(coord.outputs['Generated'],tex.inputs[0])
    diff=next(n for n in nodes if n.type=='BSDF_DIFFUSE')
    mix=nodes.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=.45;mix.inputs[1].default_value=ma.diffuse_color
    ma.node_tree.links.new(tex.outputs['Color'],mix.inputs[2]);ma.node_tree.links.new(mix.outputs[0],diff.inputs['Color'])

puddle=box('shallow puddle',(.0,-.13,.008),(.32,.27,.01),water)
# Tiny accent path resides OUTSIDE animal, never through torso to internal organs.
routepoints=[(-.33,-.23,-.04),(-.28,-.22,.06),(-.23,-.22,.16),(-.19,-.20,.23),(-.14,-.24,.30),(-.11,-.31,.31),(-.10,-.39,.25),(-.10,-.47,.21),(-.095,-.53,.19)]
route=[]
for i,p in enumerate(routepoints):route.append(box('external water highlight',p,(.026,.032,.017),cyan,body))
backroute=[]
for i in range(13):
    y=.18-i*.054;x=.045*math.sin(i*.8)
    backroute.append(box('back water highlight',(x,y,.285 if i<7 else .23),(.022,.035,.017),cyan,body))
drop=box('falling water drop',(0,0,0),(.018,.018,.027),cyan)
ripples=[]
for i in range(3):
    bpy.ops.mesh.primitive_circle_add(vertices=12,radius=.04,fill_type='NOTHING')
    o=bpy.context.object;o.name='water ripple';o.location=(0,-.13,0);o.data.materials.append(cyan)
    # thin lowpoly torus instead of non-rendering edges
    bpy.data.objects.remove(o,do_unlink=True)
    bpy.ops.mesh.primitive_torus_add(major_segments=12,minor_segments=3,major_radius=.04,minor_radius=.001)
    o=bpy.context.object;o.name='game water ripple';o.data.materials.append(water);ripples.append(o)

# Educational scale model far from the normal habitat, with a clearly external channel grid.
micro=empty('MICRO_SURFACE',(20,0,0))
box('impermeable skin slab',(0,0,-.23),(3.5,3.5,.45),base,micro)
for row in range(5):
    for col in range(5):
        x=(col-2)*.64;y=(row-2)*.64
        plate=box('overlapping angular scale',(x,y,.07),(.53,.53,.15),amber if (row+col)%2 else ochre,micro)
        cone('micro spine',(x+.06,y+.08,.19),.10,.24,cream,micro)
channels=[]
for axis in range(2):
    for row in range(4):
        c=(row-1.5)*.64
        for col in range(22):
            a=-1.67+col*.155
            p=(a,c,.018) if axis==0 else (c,a,.018)
            o=box('capillary fill segment',p,(.14,.075,.025) if axis==0 else (.075,.14,.025),cyan,micro)
            channels.append((o,math.hypot(p[0]+.32,p[1]+.32)))
beads=[]
for i in range(15):beads.append(box('capillary moving water',(0,0,.025),(.13,.08,.035),cyan,micro))
microdrop=box('micro water drop',(0,0,.3),(.2,.2,.30),cyan,micro)

bpy.ops.object.camera_add();cam=bpy.context.object;cam.name='OBSERVATION_CAMERA';s.camera=cam
cam.data.dof.use_dof=False;cam.data.clip_start=.008;cam.data.clip_end=150
bpy.ops.object.light_add(type='SUN',location=(0,0,6));sun=bpy.context.object;sun.data.energy=2.0;sun.data.angle=.16;sun.rotation_euler=(.45,-.35,-.65)
bpy.ops.object.light_add(type='AREA',location=(-2,-2,5));fill=bpy.context.object;fill.data.energy=160;fill.data.shape='DISK';fill.data.size=5
world=bpy.data.worlds.new('bright game sky');world.use_nodes=True;s.world=world
bg=next(n for n in world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs[0].default_value=(.33,.55,.69,1);bg.inputs[1].default_value=.7
s.render.engine='BLENDER_EEVEE';s.eevee.taa_render_samples=12
s.render.resolution_x=360;s.render.resolution_y=496;s.render.resolution_percentage=100
s.render.fps=30;s.frame_start=1;s.frame_end=1080;s.render.image_settings.file_format='PNG'
s.render.film_transparent=False;s.view_settings.view_transform='Standard'
s.render.use_file_extension=True
s.render.filepath=str(OUT/'0001.png')
def ease(x):x=max(0,min(1,x));return x*x*(3-2*x)
def lerp(a,b,u):return Vector(a).lerp(Vector(b),u)
def point(loc,target,lens):
    cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens
visible_scales={o:o.scale.copy() for o in [*route,*backroute,drop,*[o for o,_ in channels],*beads,microdrop]}
def show(obj,on):obj.scale=visible_scales[obj] if on else (.00001,)*3
def pose(frame):
    s.frame_set(frame)
    t=(frame-1)/30;sequence=min(11,int(t//3));u=t-sequence*3;q=u/3
    cut=[0,1,2,3,4,5,6,9,7,8,10,11][sequence]
    ground.hide_render=(cut==6)
    cam.data.shift_y=-.10 if cut not in (1,11) else -.05
    animal.location=(0,0,0);animal.rotation_euler=(0,0,0)
    body.location.z=.16+.007*math.sin(t*math.tau*.9)
    lhead.rotation_euler=(-.10+.016*math.sin(t*1.9),0,.025*math.sin(t*1.2))
    for i,e in enumerate(lizard_eyes):
        e.scale=lizard_eye_scales[i].copy()
        phase=t%4.3
        if phase>4.14:e.scale.z*=max(.08,abs(phase-4.22)/.08)
    tail.rotation_euler=(0,0,.038*math.sin(t*2))
    jaw.rotation_euler.x=.06+.10*max(0,math.sin(t*math.tau*1.7))
    for i,leg in enumerate(limbs):
        gait=math.sin(t*math.tau*.8+(i%2)*math.pi+(i//2)*math.pi)
        leg.rotation_euler=(.12*gait if cut in (2,11) else .018*gait,0,.05*gait if cut in (2,11) else 0)
    actor.location=(-.52,.22,0) if cut==1 else (-5,5,0)
    actor.rotation_euler=(0,0,.9);actor.scale=(1,1,1)
    for o in [head,*arms,*elbows,*legs,*knees]:o.rotation_euler=(0,0,0)
    head.rotation_euler.x=.22;head.rotation_euler.z=.10*math.sin(t*1.4)
    for i,e in enumerate(eyes):
        e.scale=eye_scales[i].copy()
        phase=t%3.7
        if phase>3.54:e.scale.z*=max(.05,abs(phase-3.62)/.08)
    # Camera-family shots keep action above the dialogue panel.
    if cut==0:
        animal.location.y=.12*(1-ease(u/.8))
        jaw.rotation_euler.x=.03 if u<1.4 else .07+.13*max(0,math.sin((u-1.4)*math.tau*1.7))
        if u<.8:
            for i,leg in enumerate(limbs):
                leg.rotation_euler.x=.34*math.sin(u*math.tau/.8+(i%2+i//2)*math.pi)
        point(lerp((-.54,-.26,.20),(-.49,-.25,.19),ease(q)),(0,-.10,.03),45)
    elif cut==1:
        crouch=ease(u/.55)
        actor.location.z=-.55*crouch
        legs[0].rotation_euler.x=-.9*crouch;knees[0].rotation_euler.x=1.45*crouch
        legs[1].rotation_euler.x=-.85*crouch;knees[1].rotation_euler.x=1.25*crouch
        head.rotation_euler.x=.42+.14*ease((u-.8)/.5)
        head.rotation_euler.z=-.26+.43*ease((u-1.3)/.65)
        arms[0].rotation_euler.x=-.6*crouch;elbows[0].rotation_euler.x=-.8*crouch
        cam.data.shift_y=-.10
        point(lerp((-.43,-.63,.34),(-.40,-.58,.32),q),(0,-.07,.035),42)
    elif cut==2:
        # Forward/back small settling steps return to the same puddle position.
        animal.location.y=-.035*math.sin(q*math.pi)
        actor.location.z=-.55;legs[0].rotation_euler.x=-.9;knees[0].rotation_euler.x=1.45
        legs[1].rotation_euler.x=-.85;knees[1].rotation_euler.x=1.25
        point(lerp((-.50,-.83,.46),(-.55,-.89,.49),q),(0,-.02,.025),37)
    elif cut==3:
        point(lerp((-.43,-.50,.23),(-.40,-.48,.22),q),(0,-.12,.025),45)
        limbs[0].rotation_euler.x=.20*math.sin(u*3)
    elif cut==4:
        point(lerp((18.2,-2.4,3.8),(18.55,-2.0,3.3),ease(q)),(20,0,-.12),48)
    elif cut==5:
        point(lerp((18.6,-1.8,3.4),(18.9,-1.6,3.15),q),(20,0,-.10),46)
    elif cut==6:
        point(lerp((17.2,-3.1,1.75),(17.5,-3.0,1.6),q),(20,0,-.20),43)
    elif cut==7:
        point(lerp((-.48,-.48,.31),(-.42,-.57,.24),q),(0,-.10,.033),46)
    elif cut==8:
        point(lerp((-.21,-.39,.13),(-.19,-.38,.12),q),(0,-.14,.06),51)
        jaw.rotation_euler.x=.07+.13*max(0,math.sin(u*math.tau*1.7))
    elif cut==9:
        point(lerp((18.35,-2.4,3.7),(18.5,-2.1,3.5),q),(20,0,-.12),48)
    elif cut==10:
        point(lerp((-.35,-.48,.40),(-.32,-.45,.36),q),(0,-.04,.035),42)
    else:
        actor.location.z=-.55;legs[0].rotation_euler.x=-.9;knees[0].rotation_euler.x=1.45
        legs[1].rotation_euler.x=-.85;knees[1].rotation_euler.x=1.25
        head.rotation_euler.x=.40+.12*math.sin(u*4)
        arms[0].rotation_euler.x=-.35;elbows[0].rotation_euler.x=-.45
        cam.data.shift_y=-.20
        point(lerp((-.56,-.79,.39),(-.51,-.75,.35),q),(0,-.07,.03),42)
    # Surface pathways fill with a leading front, retaining earlier wet state.
    for i,o in enumerate(route):
        amount=0
        if cut==0:amount=9*ease((u-.35)/1.05)
        elif cut in (1,2,3,8,10,11):amount=9
        elif cut==7:amount=9*ease(u/2.2)
        show(o,i<amount)
    for i,o in enumerate(backroute):show(o,cut==10 and i<13*ease((u-.45)/1.9))
    if cut==10:
        drop.location=(0,.035,.28*(1-ease(u/.6))+.105);show(drop,u<.6)
    else:show(drop,False)
    for i,o in enumerate(ripples):
        phase=(u+i*.32)%1.3;o.location=(-.02,-.13,.0005+i*.0003)
        o.location.z=.014+i*.0003
        o.scale=(.3+phase*.9,.3+phase*.9,1) if cut in (0,3,7,8) else (.0001,)*3
    # Radial external network. Filled water remains above the skin slab, not inside it.
    amount=0
    if cut==4:amount=0 if u<.6 else .15+.42*ease((u-.6)/2.4)
    elif cut==5:amount=.57+ease(u/2.6)*1.8
    elif cut==6:amount=2.3
    elif cut==9:amount=.08+ease(u/2.6)*2.3
    for o,dist in channels:show(o,cut in (4,5,6,9) and dist<amount)
    microdrop.location=(-.32,-.32,.8*(1-ease(u/.65))+.15)
    show(microdrop,cut in (4,9) and u<.8)
    for i,o in enumerate(beads):
        phase=(u*.48+i*.137)%1
        direction=1 if i%2 else -1
        if i%3==0:o.location=(-.32+direction*phase*1.4,-.32,.025)
        elif i%3==1:o.location=(-.32,-.32+direction*phase*1.4,.025)
        else:o.location=(-.32+direction*phase*.9,.32,.025)
        distance=math.hypot(o.location.x+.32,o.location.y+.32)
        show(o,cut in (5,6,9) and distance<amount)
    return cut

# Bake transforms for an editable timeline, not just an offline slideshow.
moving=[cam,actor,head,*arms,*elbows,*legs,*knees,*eyes,*lizard_eyes,animal,body,lhead,jaw,tail,*limbs,*route,*backroute,drop,*ripples,*[o for o,_ in channels],*beads,microdrop]
start=time.time()
for frame in range(1,1081):
    if (frame-1)%3==0 or frame%90==0 or (frame-1)%90==0 or frame==1080:
        pose(frame)
        for o in moving:
            for prop in ('location','rotation_euler','scale'):o.keyframe_insert(prop,frame=frame)
        cam.data.keyframe_insert('lens',frame=frame)
        cam.data.keyframe_insert('shift_y',frame=frame)
        ground.keyframe_insert('hide_render',frame=frame)
for o in moving:
    if o.animation_data and o.animation_data.action:
        for layer in o.animation_data.action.layers:
            for strip in layer.strips:
                for slot in o.animation_data.action.slots:
                    bag=strip.channelbag(slot)
                    if bag:
                        for fc in bag.fcurves:
                            for k in fc.keyframe_points:k.interpolation='LINEAR'
s.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'MINSU_THORNY_DEVIL.blend'))
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
spec=json.loads((R/'episode.json').read_text(encoding='utf-8'))
frames=spec['preview_frames'] if '--preview' in args else range(1,1081)
for frame in frames:
    s.frame_set(frame)
    s.render.filepath=str(OUT/f'{frame:04}.png')
    if '--preview' not in args and '--fresh' not in args and Path(s.render.filepath).exists():continue
    bpy.ops.render.render(write_still=True)
    print(f'NATIVE_FRAME {frame}/1080 elapsed={time.time()-start:.1f}',flush=True)
print('RENDER_COMPLETE',flush=True)
