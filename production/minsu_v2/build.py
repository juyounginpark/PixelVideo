import bpy, sys, json, math, time, hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R))
from art import *
from engine import *
from content import SceneCompiler

spec=json.loads((R/'episode.json').read_text('utf-8'));SceneCompiler().validate(spec)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;m=MaterialLibrary();factory=CharacterFactory(m)
minsu=factory.minsu();animal=factory.thorny();world=WorldFactory(m);water_anchor=world.desert()
micro,channels,micro_anchor=world.micro();camera=CameraDirector();LightingPresetManager().daylight();PixelRenderPipeline().configure()
state=CharacterStateManager(minsu);motion=CharacterAnimationController(minsu)

# Droplets have visible volume; paths are exterior schematic highlights, not internal organs.
drop=droplet('free_water_drop',(-.33,-.22,.6),m['cyan'])
microdrop=box('macro_drop',(19.74,-.26,1),(.16,.16,.22),m['cyan'],bevel=.025)
routepoints=[(-.37,-.35,.036),(-.37,-.30,.045),(-.35,-.255,.10),(-.29,-.20,.18),(-.25,-.20,.255),(-.20,-.23,.296),(-.13,-.28,.337),(-.115,-.35,.318),(-.105,-.42,.30),(-.095,-.49,.283),(-.080,-.565,.268)]
# Project onto the actual evaluated animal surface, rather than trusting guessed Z values.
bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();verts=[];polys=[]
for obj in animal['root'].children_recursive:
    if obj.type!='MESH' or any(word in obj.name for word in ('horn','spine','spike','eye')):continue
    ev=obj.evaluated_get(deps);me=ev.to_mesh();offset=len(verts)
    verts.extend(ev.matrix_world@v.co for v in me.vertices)
    polys.extend(tuple(offset+i for i in p.vertices) for p in me.polygons);ev.to_mesh_clear()
surface=BVHTree.FromPolygons(verts,polys)
def on_surface(p):
    hit=surface.ray_cast(Vector((p[0],p[1],2)),Vector((0,0,-1)),3)[0]
    return (p[0],p[1],hit.z+.004) if hit else p
dense=[]
for a,b in zip(routepoints,routepoints[1:]):
    for k in range(4):dense.append(on_surface(Vector(a).lerp(Vector(b),k/4)))
dense.append(on_surface(routepoints[-1]))
# Continue around the snout edge to the visible mouth corner, not merely the forehead.
dense.extend([(-.079,-.59,.262),(-.075,-.596,.235),(-.066,-.599,.203)])
routepoints=dense
route=[]
for j in range(len(routepoints)-1):
    parent=animal['head'] if j>=24 else animal['root']
    inv=parent.matrix_world.inverted()
    points=[tuple(inv@Vector(p)) for p in (routepoints[j],routepoints[j+1])]
    route.append(line('external_wet_route',points,m['cyan'],.004,parent))
branches=[]
for j in range(12):
    p=on_surface((-.18+j*.026,-.20+j*.035,.32-.035*abs(j-5)/6))
    branches.append(box('radial_branch',p,(.025,.038,.008),m['cyan'],animal['root'],.002))
route_anchor=empty('route_anchor',(-.18,-.22,.34),animal['root'])
mouthwater=box('mouth_water',(-.064,-.24,-.054),(.027,.013,.009),m['cyan'],animal['head'],.003)
anchors={'micro_anchor':micro_anchor,'route_anchor':route_anchor,'minsu_face':minsu.head,'thorny_head':animal['head'],'water':water_anchor}
moving=[camera.camera,minsu.root,*minsu.moving,animal['root'],animal['body'],animal['head'],animal['jaw'],animal['tail'],*animal['limbs'],drop,microdrop,mouthwater,*route,*branches,*[o for o,d in channels]]
moving=list(dict.fromkeys(moving))

def visible(o,on):o.scale=(1,1,1) if on else (0,0,0)

def pose(frame):
    t=(frame-1)/30;s.frame_set(frame)
    index=next((i for i,x in enumerate(spec['shots']) if x['startTime']<=t<x['endTime']),8)
    shot=spec['shots'][index];u=t-shot['startTime'];q=u/(shot['endTime']-shot['startTime'])
    camera.apply(shot['cameraPlan'],q);state.reset(t)
    animal['root'].location=(0,-.08 if index>=3 else 0,0);animal['root'].rotation_euler=(0,0,0)
    animal['body'].location.z=.21+.003*math.sin(t*2.4)
    animal['head'].rotation_euler=(.015*math.sin(t*2),0,.04*math.sin(t*1.3))
    animal['jaw'].rotation_euler.x=0;animal['tail'].rotation_euler.z=.032*math.sin(t*2)
    for leg in animal['limbs']:leg.rotation_euler=(0,0,0)
    minsu.root.scale=(1,1,1)
    if index in (0,3,4,5,6,8):minsu.root.location=(-4,4,0)
    if index==1:
        motion.apply('LeanForward',t,ease(u/.5))
        if u>.35:motion.apply('Surprise',t,ease((u-.35)/.20)*(1-.4*ease((u-1.0)/1.0)))
        minsu.head.rotation_euler.x=.48-.16*ease((u-1.0)/.7)
        minsu.head.rotation_euler.z=.37+.12*ease((u-1.0)/.7)
        animal['head'].rotation_euler.z=-.16*ease((u-.6)/.7)
    if index==2:
        animal['root'].location.y=-.08*ease(u/2.6)
        for j,leg in enumerate(animal['limbs']):
            phase=u*5+(j%2+j//2)*math.pi
            leg.rotation_euler.x=.17*math.sin(phase)*(1-ease((u-2.2)/.7))
        motion.apply('Inspect',t,.7)
    if index==5:
        animal['head'].rotation_euler.z=-.08+.13*ease(u/4)
    if index==6:
        if u>1.5:animal['jaw'].rotation_euler.x=.12*max(0,math.sin((u-1.5)*math.tau*1.35))
    if index==7:
        if u<1.5:motion.apply('Point',t,ease(u/.4))
        else:motion.apply('Happy',t,ease((u-1.5)/.3))
        minsu.head.rotation_euler.z=.42-.2*ease((u-2.2)/.7)
        minsu.head.rotation_euler.x=.38-.32*ease((u-2.2)/.7)
    if index==8:animal['head'].rotation_euler.z=.16*math.sin(u*.75);animal['jaw'].rotation_euler.x=.035*max(0,math.sin(u*5))
    drop.location=(-.36,-.29,on_surface((-.36,-.29,.058))[2]+.027+.22*(1-ease(u/.55)))
    visible(drop,index==0 and u<.58)
    # First hook shows only local wetting; entire route is explained/revealed later.
    amount=12*ease((u-.55)/1.0) if index==0 else (len(route)*ease(u/4.0) if index==5 else len(route) if index>=6 else 12)
    for j,o in enumerate(route):visible(o,index not in (3,4) and j<amount)
    for j,o in enumerate(branches):visible(o,index>=5 and j<12*ease((u-.5)/3) if index==5 else index>=6)
    visible(mouthwater,index>=6 and (index!=6 or u>=1.5))
    amount=0 if index==3 else 2.4*ease((u-.65)/3.8)
    for o,dist in channels:visible(o,index==4 and dist<amount)
    microdrop.location=(19.74,-.26,.145+.9*(1-ease(u/.65)))
    visible(microdrop,index==4 and u<.69)
    return index

def bake():
    anchor_records={};start=time.time()
    # Every other frame plus cut boundaries: transform curves; no cut interpolations.
    boundaries={round(x['startTime']*30)+1 for x in spec['shots']}
    frames=set(range(1,1081,2))|boundaries|{f-1 for f in boundaries if f>1}|{1080}
    for f in sorted(frames):
        pose(f)
        for o in moving:
            for p in ('location','rotation_euler','scale'):o.keyframe_insert(p,frame=f)
        camera.camera.data.keyframe_insert('lens',frame=f)
    for o in moving:
        if not o.animation_data:continue
        action=o.animation_data.action
        for layer in action.layers:
            for strip in layer.strips:
                for slot in action.slots:
                    bag=strip.channelbag(slot)
                    if bag:
                        for fc in bag.fcurves:
                            for key in fc.keyframe_points:key.interpolation='LINEAR'
    for f in range(1,1081):
        s.frame_set(f);bpy.context.view_layer.update();row={}
        for name,o in anchors.items():
            p=world_to_camera_view(s,camera.camera,o.matrix_world.translation)
            row[name]=[round(p.x*1080,1),round((1-p.y)*1920,1),round(p.z,3)]
        anchor_records[str(f)]=row
    (R/'anchors.json').write_text(json.dumps(anchor_records),'utf-8')
    (R/'asset_manifest.json').write_text(json.dumps({'models':['MINSU_CUTE_V2','THORNY_V2'],
        'meshCount':sum(o.type=='MESH' for o in bpy.data.objects),'faceStates':minsu.face.STATES,'animationPresets':motion.PRESETS,
        'exercisedPresets':['Idle','LeanForward','Surprise','Inspect','Point','Happy'],'frameCount':1080,'nativeResolution':[540,960],
        'textures':[im.name for im in bpy.data.images if im.name.endswith('_32px')],'bakeSeconds':time.time()-start},indent=2),'utf-8')
    s.frame_set(1);s.render.filepath=str(R/'frames/0001.png')
    bpy.ops.wm.save_as_mainfile(filepath=str(R/'MINSU_EP04_V2.blend'))

if __name__=='__main__':
    bake();out=R/'frames';out.mkdir(exist_ok=True)
    args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
    if '--build-only' not in args:
        frames=[1,15,24,50,68,112,163,235,280,352,390,470,530,605,680,728,820,865,920,985,1060] if '--preview' in args else range(1,1081)
        for f in frames:
            s.frame_set(f);s.render.filepath=str(out/f'{f:04}.png');bpy.ops.render.render(write_still=True)
            print('FRAME',f,flush=True)
