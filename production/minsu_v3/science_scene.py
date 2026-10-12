"""Explicit granular-orientation visualization selected by the upstream episode.

Authored geometric paths explain a reviewed experiment. No topic default, no
claim of DEM/fluid physics, no reuse of thorny-devil assets or desert staging.
"""
import bpy,math,sys,random
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R.parent/'minsu_v2'))
from art import box,empty,mesh,line
from design_system import ToonMaterialLibrary,CuteCharacterFactory,PixelStylePipeline,StudioLighting,TargetedActing
from effects import smooth

def nut_mesh(name,radii,material,parent,peanut=False):
    verts=[];rings=9;around=8
    for i in range(rings):
        u=-1+2*i/(rings-1);r=math.sqrt(max(.025,1-u*u))
        if peanut:r*=.74+.26*abs(math.sin(u*math.pi))
        for j in range(around):
            a=j*math.tau/around
            verts.append((u*radii[0],math.cos(a)*r*radii[1],math.sin(a)*r*radii[2]*(1+.08*u)))
    faces=[tuple(range(around-1,-1,-1))]
    for i in range(rings-1):
        for j in range(around):faces.append((i*around+j,i*around+(j+1)%around,(i+1)*around+(j+1)%around,(i+1)*around+j))
    faces.append(tuple(range((rings-1)*around,rings*around)))
    return mesh(name,verts,faces,material,parent)

class Scene:
    def __init__(self,spec):
        if spec.get('visualization',{}).get('kind')!='granular_orientation_diagram':raise ValueError('No registered visualizer for supplied episode')
        if not spec.get('sourceReceipt') or not all(f['status']=='reviewed' for f in spec.get('facts',[])):raise ValueError('Reviewed source and facts required')
        self.spec=spec;self.m=ToonMaterialLibrary();m=self.m
        for key,color in [('wood',(.79,.63,.45)),('wall',(.83,.85,.78)),('nut_shell',(.70,.39,.16)),('peanut',(.86,.65,.37)),('frame',(.31,.53,.59)),('floor',(.65,.73,.70))]:
            m.materials[key]=m.make(key,color,True)
        self.rig=CuteCharacterFactory(m).minsu();self.acting=TargetedActing(self.rig)
        self.boxroot=empty('experiment_box',(.58,0,.58))
        box('box_base',(0,0,.012),(1.34,.64,.04),m['frame'],self.boxroot,.012)
        for x in (-.65,.65):
            for y in (-.30,.30):box('box_corner',(x,y,.59),(.024,.024,1.16),m['frame'],self.boxroot)
        for z in (.035,1.17):
            line('box_rim',[(-.65,-.30,z),(.65,-.30,z),(.65,.30,z),(-.65,.30,z),(-.65,-.30,z)],m['frame'],.011,self.boxroot)
        # Open-front explanatory box, not physically transparent glass/PBR.
        box('box_back',(0,.316,.59),(1.28,.02,1.13),m['cream'],self.boxroot)
        self.big=nut_mesh('brazil_nut',(.30,.123,.113),m['nut_shell'],self.boxroot)
        self.stuck=nut_mesh('nonrising_nut',(.23,.104,.08),m['nut_shell'],self.boxroot)
        self.grains=[];self.initial=[];self.grain_rotations=[];rng=random.Random(51005)
        for row in range(9):
            for col in range(7):
                for depth in range(3):
                    g=nut_mesh('peanut',(.085,.052,.050),m['peanut'],self.boxroot,True)
                    pos=Vector(((col-3)*.174+(row%2)*.022+rng.uniform(-.013,.013),-.20+depth*.20+rng.uniform(-.016,.016),.10+row*.106+rng.uniform(-.017,.017)))
                    self.grains.append(g);self.initial.append(pos)
                    self.grain_rotations.append((rng.uniform(-.3,.3),rng.uniform(-.35,.35),rng.uniform(-.55,.55)))
        self.focus_peanut=self.grains[6*21+3]
        # Topic-specific room: worktop, cupboards, window and measuring cup silhouette.
        box('floor',(0,0,-.07),(50,50,.12),m['floor'])
        box('room_back',(0,3,2.3),(14,.12,4.6),m['wall'])
        box('worktop',(.62,0,.50),(1.65,1.05,.12),m['wood'],bevel=.025)
        for x in (-.04,1.28):
            for y in (-.38,.38):box('table_leg',(x,y,.24),(.08,.08,.5),m['wood'])
        for x in (-2.2,-1.1,0,1.1,2.2):
            box('cabinet',(x,2.5,.60),(1.02,.54,1.16),m['cream'],bevel=.025)
            box('cabinet_handle',(x,2.205,.86),(.22,.03,.025),m['frame'])
        box('rear_counter',(0,2.48,1.21),(5.55,.70,.10),m['wood'])
        box('window',(1.3,2.91,2.37),(1.6,.08,1.20),m['frame'])
        for x in (.89,1.71):
            for z in (2.08,2.68):box('window_pane',(x,2.859,z),(.74,.028,.53),m['cyan'])
        box('shelf',(-1.65,2.70,2.02),(1.7,.48,.07),m['wood'])
        for j in range(4):box('book',(-2.15+j*.21,2.65,2.23),(.13,.25,.38),m['mint'] if j%2 else m['cream'],bevel=.005)
        StudioLighting().configure();PixelStylePipeline().configure(bpy.context.scene);bpy.context.scene.eevee.taa_render_samples=24
        bpy.ops.object.camera_add();self.cam=bpy.context.object;bpy.context.scene.camera=self.cam;self.cam.data.type='ORTHO';self.cam.data.dof.use_dof=False
        self.targets={'minsu':self.rig.head,'nut':self.big,'peanut':self.focus_peanut,'stuck':self.stuck}
        self.diagnostics={}

    def granular_pose(self,stage,t):
        # The same large nut: horizontal at bottom -> upright -> rise -> flat top.
        angle=math.radians(75)*smooth(stage/1.0) if stage<=1 else math.radians(75)
        height=.385+.63*smooth((stage-1)/1.0)
        if stage>2:angle=math.radians(75)*(1-smooth(stage-2))
        self.big.location=(.02,-.105,height);self.big.rotation_euler=(0,-angle,.025*math.sin(t*4))
        self.stuck.location=(-.35,.11,.165);self.stuck.rotation_euler=(0,-.10*math.sin(t*1.4),.15)
        flow=smooth((stage-.65)/1.5);inv=Matrix.Rotation(angle,3,'Y')
        for i,(g,base) in enumerate(zip(self.grains,self.initial)):
            pos=base.copy();col=(i//3)%7;row=i//21
            # Channels at the sides bring small nuts down; no teleport/wraparound.
            if col in (0,1,5,6):pos.z-=.18*flow*(row/8)
            else:pos.x+=(1 if col>=3 else -1)*.025*flow
            pos.x+=.008*math.sin(t*11+i)*min(1,stage+.1);pos.z+=.006*math.sin(t*13+i*.7)
            # Keep small pieces outside the moving large ellipsoid, avoiding an
            # obvious through-body path in this deliberately simplified diagram.
            for center,radii,rot in [(Vector(self.big.location),(.385,.194,.185),inv),(Vector(self.stuck.location),(.31,.17,.145),Matrix.Identity(3))]:
                local=rot@(pos-center)
                front=base.y<-.09 or (center.z<.2 and base.y<.16);keep_y=pos.y
                if front:local.y=0  # Front explanatory slice: keep the large nut legible.
                q=sum((local[j]/radii[j])**2 for j in range(3))
                if q<1:
                    if local.length<.0001:local=Vector((1,0,0))
                    local*=1/math.sqrt(max(q,.00001));pos=center+rot.transposed()@local
                    if front:pos.y=keep_y
                    if pos.z>.98:
                        # At the surface, small nuts fall beside the large nut,
                        # rather than being pinned through it by a top clamp.
                        pos.x=(.44 if base.x>=.02 else -.42);pos.z=min(base.z,.95)-.08*flow
            pos.x=max(-.55,min(.55,pos.x));pos.y=max(-.21,min(.21,pos.y));pos.z=max(.085,min(.99,pos.z))
            rot=self.grain_rotations[i]
            g.location=pos;g.rotation_euler=(rot[0],rot[1]+.07*math.sin(t*3+i),rot[2]+.07*math.sin(t*4+i))
        self.diagnostics={'stage':stage,'largeHeight':height,'largeAngleDegrees':math.degrees(angle),
                          'smallFocusZ':self.focus_peanut.location.z,'nonrisingHeight':self.stuck.location.z,'mode':'authored diagram'}

    def pose(self,frame):
        shot=next(s for s in self.spec['shots'] if s['startFrame']<=frame<s['endFrame']);phase=shot['phase']
        p=(frame-shot['startFrame'])/(shot['endFrame']-shot['startFrame']);t=frame/30
        stage={'hook':1.45+.8*smooth(p),'reaction':3,'reset':.0,'rotate':smooth(p),
               'percolate':1+.20*smooth(p),'rise':1.2+.80*smooth(p),'settle':2+smooth(p),'condition':3,'payoff':3}[phase]
        self.boxroot.location=(.58,0,.58)
        shaking=phase in ('hook','reset','rotate','percolate','rise','settle')
        if shaking:self.boxroot.location.x+=.022*math.sin(t*12)
        self.granular_pose(stage,t)
        action='Inspect';progress=.55
        if phase=='reaction':action='Surprise';progress=min(1,p*2.5)
        if phase=='payoff':action='Understand';progress=.3+.7*p
        self.acting.apply(action,progress,(.58,0,1.2));self.rig.root.location=(-.65,-.03,0)
        for obj in self.rig.root.children_recursive:obj.hide_render=phase not in ('reaction','reset','payoff')
        if phase=='reset':
            self.rig.arms[1].rotation_euler.y=-.92;self.rig.elbows[1].rotation_euler.y=-.32
            self.rig.body.rotation_euler.z=-.08;self.rig.arms[1].rotation_euler.x=-.20
        # Explicit per-shot camera language; no inherited EP04 coordinates.
        if phase=='reaction':aim=(-.55,0,1.02);pos=(-.1,-4,1.3);scale=2.30
        elif phase in ('reset','payoff'):aim=(.03,0,1.0);pos=(.3,-5,2.05);scale=4.25
        elif phase=='rotate':aim=(.60,0,1.00);pos=(1.5,-4,1.8);scale=2.65
        elif phase=='percolate':aim=(.44,0,1.00);pos=(.65,-4,1.3);scale=2.65
        elif phase=='condition':aim=(.48,0,.98);pos=(.25,-4,1.35);scale=2.68
        elif phase=='settle':aim=(.61,0,1.04);pos=(.85,-4,2.2);scale=2.65
        else:aim=(.58,0,1.00);pos=(.58,-4,1.45);scale=2.65
        self.cam.location=pos;self.cam.rotation_euler=(Vector(aim)-self.cam.location).to_track_quat('-Z','Y').to_euler();self.cam.data.ortho_scale=scale*(1-.018*smooth(p));self.cam.data.shift_y=0
        # Only visible/needed anchors, and no offscreen face blocking macro labels.
        self.targets={'nut':self.big,'peanut':self.focus_peanut,'stuck':self.stuck}
        if phase in ('reaction','reset','payoff'):self.targets['minsu']=self.rig.head
