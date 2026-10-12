import bpy, math, random, sys, json, time
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'frames'; OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
random.seed(17)
def mat(name,hex):
    h=hex.lstrip('#'); c=tuple(int(h[i:i+2],16)/255 for i in (0,2,4))
    m=bpy.data.materials.new(name); m.diffuse_color=(*c,1); return m
M={k:mat(k,v) for k,v in dict(ink='202B39',dark='34404C',teal='329C9C',skin='EAC297',hair='252C36',sole='E6E5D9',red='BB5149',yellow='EEC45B',cream='F6EBD1',pave='AFB5B3',wall='7D959A',trim='D0D6C8',glass='426673',leaf='5C8668',leaf2='7EA077',pot='A1745D',metal='77858B',white='F2F0E7').items()}
def box(name,loc,scale,material,parent=None,bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object;o.name=name;o.dimensions=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(M[material]);
    if parent:o.parent=parent
    if bevel:
        m=o.modifiers.new('edge','BEVEL');m.width=bevel;m.segments=1
        o.modifiers.new('normals','WEIGHTED_NORMAL')
    return o
def empty(name,loc=(0,0,0),parent=None):
    o=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(o);o.location=loc;o.parent=parent;return o
def text3(name,body,loc,size,material,parent=None):
    c=bpy.data.curves.new(name,'FONT');c.body=body;c.align_x='CENTER';c.align_y='CENTER';c.size=size;c.extrude=.0005
    o=bpy.data.objects.new(name,c);bpy.context.collection.objects.link(o);o.location=loc;o.rotation_euler=(math.pi/2,0,0);o.data.materials.append(M[material]);o.parent=parent;return o

# A small, deliberately composed street set.
box('sidewalk',(0,0,-.16),(16,13,.3),'pave')
box('building',(0,1.48,2.9),(14,.45,6),'wall')
for z in [.25,.62,1,1.38,1.76,2.14,2.52,2.9,3.28,3.66,4.04,4.42,4.8]:
    box('siding',(0,1.23,z),(14,.035,.035),'dark')
for x in [-3.7,-1.3,1.4,3.8]:
    box('window_frame',(x,1.16,3.35),(1.95,.15,1.95),'trim')
    box('window',(x,1.05,3.35),(1.73,.07,1.74),'glass')
    box('mullion',(x,.99,3.35),(.08,.09,1.78),'trim')
    box('mullion',(x,.99,3.35),(1.8,.09,.08),'trim')
for x in range(-5,6):
    box('pavement_seam',(x,-1.6,.003),(.015,5,.009),'metal')
for y in [-3.5,-2.3,-1.1,.1]:box('pavement_seam',(0,y,.004),(12,.012,.009),'metal')
for x in [-2.1,-1.05,0,1.05,2.1]:box('railing_post',(x,.55,.75),(.065,.065,1.5),'dark')
for z in [.5,1.35]:box('rail',(0,.55,z),(4.5,.08,.08),'dark')
for x in [-2.65,3.1]:
    box('planter',(x,.05,.27),(.72,.72,.55),'pot',bevel=.03)
    for i in range(15):box('plant',(x+random.uniform(-.3,.3),random.uniform(-.2,.3),random.uniform(.58,1.03)),(.26,.26,.3),random.choice(['leaf','leaf2']))
box('lamp_pole',(-3.3,-.75,1.85),(.12,.12,3.7),'dark')
box('lamp',(-3.3,-.75,3.7),(.5,.5,.35),'cream')
box('lamp_cap',(-3.3,-.75,3.92),(.64,.64,.1),'dark')

machine=empty('VENDING_MACHINE')
box('cabinet',(0,0,1.36),(1.72,.85,2.72),'dark',machine,.025)
box('face',(0,-.444,1.36),(1.57,.045,2.55),'ink',machine)
box('red_header',(0,-.48,2.13),(1.48,.065,.82),'red',machine)
text3('SODA','S O D A',(0,-.524,2.2),.28,'cream',machine)
text3('cold','ICE COLD',(0,-.525,1.95),.085,'cream',machine)
for col in range(3):
    for row in range(2):
        x=(col-1)*.45;z=1.59-row*.19
        box('button_frame',(x,-.49,z),(.425,.09,.155),'metal',machine)
        box('button',(x,-.548,z),(.39,.045,.12),'yellow',machine,.008)
        text3('button_label','MYSTERY',(x,-.574,z),.058,'ink',machine)
box('coin_slot',(.61,-.49,1.15),(.1,.045,.25),'metal',machine)
box('slot',(.61,-.517,1.18),(.025,.012,.13),'ink',machine)
box('hatch_frame',(0,-.49,.38),(1.05,.08,.39),'metal',machine)
box('hatch',(0,-.54,.38),(.93,.06,.27),'ink',machine)
for i in range(24):
    x=random.uniform(-.68,.68);z=random.uniform(.65,1.2)
    box('paint_wear',(x,-.472,z),(.03+random.random()*.055,.01,.018),'dark',machine)

# Articulated voxel actor; simple animation remains editable in the blend file.
actor=empty('MINSU',(1.5,-.6,0))
body=box('teal_sweater',(0,0,1.06),(.57,.35,.65),'teal',actor)
box('collar',(0,-.19,1.32),(.24,.04,.1),'cream',actor)
head=empty('head',(0,0,1.65),actor)
box('face',(0,0,0),(.58,.48,.58),'skin',head)
box('hair_top',(0,.01,.32),(.64,.54,.16),'hair',head)
box('hair_back',(0,.24,.09),(.63,.12,.48),'hair',head)
for x,z in [(-.25,.19),(-.12,.26),(.04,.22),(.2,.28)]:box('fringe',(x,-.245,z),(.16,.08,.16),'hair',head)
for x in [-.13,.13]:
    box('eye',(x,-.251,.035),(.068,.025,.082),'ink',head)
    box('eye_glint',(x-.012,-.268,.056),(.018,.009,.019),'white',head)
    box('brow',(x,-.258,.14),(.105,.025,.025),'hair',head)
box('nose',(0,-.28,-.045),(.09,.09,.09),'skin',head)
box('mouth',(0,-.254,-.16),(.12,.025,.025),'dark',head)
arms=[];legs=[]
for side in [-1,1]:
    arm=empty('arm',(.39*side,0,1.28),actor);arms.append(arm)
    box('sleeve',(0,0,-.18),(.23,.3,.42),'teal',arm)
    box('hand',(0,0,-.46),(.21,.27,.18),'skin',arm)
    leg=empty('leg',(.16*side,0,.77),actor);legs.append(leg)
    box('trouser',(0,0,-.31),(.235,.3,.62),'ink',leg)
    box('shoe',(0,-.055,-.69),(.27,.43,.17),'sole',leg)
can=empty('CAN',(0,0,0),arms[0])
box('can_body',(0,-.02,-.55),(.2,.2,.32),'red',can,.025)
box('can_top',(0,-.02,-.38),(.2,.2,.025),'metal',can)
text3('can_label','CHERRY',(0,-.13,-.54),.035,'cream',can)

# Foreground hand is independently rigged for the opening button shot.
hand=empty('CLOSEUP_HAND',(.4,-.92,1.44))
box('palm',(0,0,0),(.25,.15,.24),'skin',hand)
box('finger',(-.07,.1,.19),(.085,.14,.3),'skin',hand)
box('cuff',(.025,-.02,-.2),(.29,.22,.19),'teal',hand)
note=empty('NOTE',(.32,.40,1.16))
box('paper',(0,0,0),(.67,.028,.43),'cream',note)
box('tape',(0,-.019,.23),(.17,.018,.1),'yellow',note)
text3('note_words','Went for\na walk.',(0,-.026,0),.105,'ink',note)

scene=bpy.context.scene
scene.render.engine='BLENDER_WORKBENCH'
scene.display.shading.light='STUDIO';scene.display.shading.studiolight_rotate_z=.35
scene.display.shading.color_type='MATERIAL';scene.display.shading.show_shadows=True
scene.display.shading.show_cavity=True;scene.display.shading.cavity_type='BOTH'
scene.display.shading.curvature_ridge_factor=1.2;scene.display.shading.curvature_valley_factor=1.05
scene.display.shading.show_specular_highlight=True
scene.display.shading.background_type='WORLD';scene.world.color=(.13,.19,.24)
scene.view_settings.view_transform='Standard'
scene.render.resolution_x=720;scene.render.resolution_y=1280;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB'
scene.render.fps=24;scene.frame_start=1;scene.frame_end=552
bpy.ops.object.camera_add();cam=bpy.context.object;cam.name='CAMERA';scene.camera=cam
cam.data.type='ORTHO';cam.data.lens=45;cam.data.clip_end=100
def camera(loc,target,scale):
    cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale
def smooth(x):return max(0,min(1,x))**2*(3-2*max(0,min(1,x)))
def pose(t):
    machine.location.z=0 if t<12 else -20
    note.location.z=1.16 if t>=12 else -20
    actor.location=(1.45,-.7,0);actor.rotation_euler.z=-.2
    head.rotation_euler=(0,0,0)
    for o in arms+legs:o.rotation_euler=(0,0,0)
    hand.location=(.35,-.95,1.15);hand.scale=(1,1,1)
    can.scale=(0,0,0)
    if t<5:
        camera((.08,-5,1.98),(0,-.42,1.55),2.85)
        actor.location.x=5
        hand.location.x=.28*math.sin(t*1.6) if t<3 else .02
        hand.location.z=1.12+.12*smooth(t/2)
        hand.location.y=-.85+.12*smooth((t-3)/.7)
    elif t<9:
        hand.scale=(0,0,0);can.scale=(1,1,1)
        camera((3.6,-6,3.4),(.75,-.3,1.33),3.65)
        actor.rotation_euler.z=.22
        arms[0].rotation_euler.x=-1.15-.2*math.sin((t-5)*2)
        head.rotation_euler.x=.13
        head.rotation_euler.z=-.16
    elif t<12:
        hand.scale=(0,0,0);can.scale=(1,1,1)
        u=t-9;actor.location.x=1.45+u*.42;actor.rotation_euler.z=-.7
        arms[0].rotation_euler.x=-.65
        legs[0].rotation_euler.x=.28*math.sin(u*7);legs[1].rotation_euler.x=-.28*math.sin(u*7)
        head.rotation_euler.z=.45*smooth((u-1)/.6)
        camera((4.3,-7,3.7),(.45,0,1.25),5.5)
    elif t<16:
        hand.scale=(0,0,0)
        u=t-12;actor.location.x=2.5-1.1*smooth(u/1.4);actor.rotation_euler.z=.5
        if u<1.4:
            legs[0].rotation_euler.x=.25*math.sin(u*7);legs[1].rotation_euler.x=-.25*math.sin(u*7)
        head.rotation_euler.z=.3*smooth((u-1.3)/.6)
        camera((4.3,-7,3.7),(.45,0,1.25),5.5-.3*smooth(u/4))
    elif t<20:
        hand.scale=(0,0,0);actor.location.x=5
        camera((.55,-4,1.72),(.32,.40,1.2),1.65-.10*smooth((t-16)/4))
    else:
        hand.scale=(0,0,0)
        camera((3,-5.5,2.7),(.75,0,1.05),3.7)
        actor.rotation_euler.z=.6;head.rotation_euler.z=.25*math.sin((t-20)*1.5)
    return [machine,note,actor,head,hand,can,cam]+arms+legs

# Bake deterministic poses to retain an editable, scrub-able scene.
for f in range(1,553):
    for o in pose((f-1)/24):
        o.keyframe_insert(data_path='location',frame=f);o.keyframe_insert(data_path='rotation_euler',frame=f);o.keyframe_insert(data_path='scale',frame=f)
    cam.data.keyframe_insert(data_path='ortho_scale',frame=f)
scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'MINSU_EP02.blend'))
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
frames=[1,145,250,330,420,510] if '--preview' in args else range(1,553)
start=time.time()
for f in frames:
    target=OUT/f'{f:05d}.png'
    scene.frame_set(f);scene.render.filepath=str(target);bpy.ops.render.render(write_still=True)
    if f%24==0:print(f'PROGRESS {f}/552 elapsed={time.time()-start:.1f}',flush=True)
print('RENDER_COMPLETE',flush=True)
