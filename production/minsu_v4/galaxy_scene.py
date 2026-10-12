"""Explicit EP07 adapter. Analytic explanatory trajectories, not observed data."""
import math,random
from types import SimpleNamespace
import bpy
from mathutils import Vector
from art_v4 import Materials,setup,character,visibility,star,dots,cubes
from art import box,empty,line,mesh,cone
from common import config

def ease(t):t=max(0,min(1,t));return t*t*(3-2*t)
def ring(name,r,z,mat,parent):return line(name,[(r*math.cos(j*math.tau/64),r*math.sin(j*math.tau/64),z) for j in range(65)],mat,.009,parent)

class Scene:
    def __init__(self,size):
        self.m=Materials();m=self.m;self.s=setup(size);self.world=empty('OBSERVATORY');self.space=empty('GALAXY_STAGE');self.force=empty('GRAVITY_STAGE');self.dual=empty('TWO_ORBITS')
        self.rig=character(m);self.rig.root.parent=self.world
        # Finished observation room: wide window, warm instruments and contact shadows.
        box('room_floor',(0,0,-.12),(12,12,.20),m['floor'],self.world)
        box('back_wall',(0,2.5,1.8),(8,.22,3.8),m['wall'],self.world)
        box('window_night',(0,2.35,2.0),(4.4,.07,2.25),m['midnight'],self.world)
        for x in (-2.27,2.27):box('window_side',(x,2.25,2.0),(.14,.20,2.42),m['brass'],self.world)
        for z in (.8,3.22):box('window_edge',(0,2.25,z),(4.68,.20,.13),m['brass'],self.world)
        for x in (-.8,.8):box('window_mullion',(x,2.27,2),(.045,.13,2.3),m['dim'],self.world)
        rng=random.Random(407)
        cubes('window_stars',[(rng.uniform(-2.1,2.1),2.29,rng.uniform(.98,3.05)) for _ in range(55)],.035,m['star_cold'],self.world)
        for x in (-1.8,1.8):
            box('wall_sconce',(x,2.0,1.8),(.19,.28,.42),m['brass'],self.world,.02)
            box('sconce_light',(x,1.83,1.82),(.12,.05,.24),m['light'],self.world)
        for x in (-1.5,0,1.5):line('floor_inlay',[(x,-4,.002),(x,2,.002)],m['dim'],.013,self.world)
        self.table=empty('OBSERVATION_TABLE',(.45,.35,0),self.world)
        box('table_top',(0,0,.65),(1.60,1.2,.13),m['navy'],self.table,.04)
        box('table_rim',(0,0,.718),(1.50,1.1,.035),m['brass'],self.table,.02)
        box('projection_screen',(0,0,.746),(1.41,1.00,.035),m['midnight'],self.table)
        for x in (-.62,.62):
            for y in (-.40,.40):box('table_leg',(x,y,.29),(.10,.10,.65),m['navy'],self.table)
        self.switch=box('model_switch',(-.72,-.50,.79),(.13,.16,.07),m['star_gold'],self.table)
        self.telescope=empty('TELESCOPE',(-1.3,.85,.64),self.world)
        for ang in (0,2.094,4.188):line('tripod',[(0,0,0),(.3*math.cos(ang),.3*math.sin(ang),-.63)],m['navy'],.035,self.telescope)
        tube=box('telescope_tube',(0,0,.40),(.28,.80,.28),m['brass'],self.telescope,.025);tube.rotation_euler.x=-.24
        box('telescope_lens',(0,-.425,.50),(.25,.05,.25),m['ice_dark'],self.telescope)
        box('eyepiece',(0,.46,.29),(.12,.15,.12),m['navy'],self.telescope)
        self.world_gal=self.make_galaxy('TABLE_GALAXY',self.world);self.world_gal['root'].location=(.45,.35,.82);self.world_gal['root'].scale=(.52,.52,.52)
        self.gal=self.make_galaxy('MACRO_GALAXY',self.space)
        self.gravity=self.make_force('FORCE',self.force)
        self.compares=[]
        for i,y in enumerate((1.50,-.65)):
            g=self.make_force('PAIR_'+str(i),self.dual);g['root'].location.y=y;g['root'].scale=(.65,)*3;self.compares.append(g)
        bpy.ops.object.camera_add();self.camera=bpy.context.object;self.camera.name='V4_CAMERA';self.camera.data.type='ORTHO';self.s.camera=self.camera
        self.targets={};self.lastmode=None

    def make_galaxy(self,name,parent):
        m=self.m;r=empty(name,parent=parent);field=empty(name+'_STARS',parent=r);positions=[]
        rng=random.Random(41)
        for arm in range(3):
            for j in range(65):
                radius=.08+j*.013;theta=arm*math.tau/3+j*.075
                positions.append((radius*math.cos(theta)+rng.uniform(-.055,.055),radius*math.sin(theta)+rng.uniform(-.055,.055),rng.uniform(-.045,.045)))
        cubes(name+'_starfield',positions,.038,m['star_cold'],field)
        core=star(name+'_CORE',(0,0,0),m['star_gold'],r,.16)
        track=dots(name+'_TRACK',1.13,.02,m['track'],r,64,.025)
        outer=star(name+'_OBSERVED',(1.13,0,.04),m['star_gold'],r,.13)
        expected=empty(name+'_EXPECTED',parent=r)
        points=[((.13 if i%2==0 else .060)*math.cos(math.pi/2+i*math.pi/5),(.13 if i%2==0 else .060)*math.sin(math.pi/2+i*math.pi/5),.029) for i in range(10)]
        line(name+'_ghost_star',points+[points[0]],m['cream'],.012,expected)
        halo=empty(name+'_INFERRED_HALO',parent=r)
        for k in range(2):
            a=k*math.pi/2
            line(name+'_halo_longitude',[(1.45*math.cos(t)*math.cos(a),1.45*math.cos(t)*math.sin(a),.8*math.sin(t)) for t in [j*math.tau/64 for j in range(65)]],m['halo'],.007,halo)
        for z in (-.40,0,.40):dots(name+'_halo_latitude',1.45*math.sqrt(1-(z/.8)**2),z,m['halo'],halo,70,.021)
        trail=empty(name+'_TRAIL',parent=r);beads=[]
        for j in range(8):beads.append(box(name+'_trail_pixel',(0,0,0),(.034,.034,.034),m['star_gold'],trail))
        return dict(root=r,field=field,core=core,track=track,outer=outer,expected=expected,halo=halo,trail=trail,beads=beads)

    def make_force(self,name,parent):
        m=self.m;r=empty(name,parent=parent);core=star(name+'_center',(0,0,0),m['star_cold'],r,.14)
        dots(name+'_orbit',1.05,.015,m['track'],r,64,.020)
        outer=star(name+'_star',(1.05,0,.04),m['star_gold'],r,.14)
        inward=empty(name+'_gravity',parent=r);shaft=box(name+'_gravity_shaft',(-.25,0,0),(.5,.06,.055),m['halo'],inward)
        tip=cone(name+'_gravity_tip',(-.56,0,0),.115,.24,m['halo'],inward);tip.rotation_euler.y=-math.pi/2
        tangent=empty(name+'_velocity',parent=r);box(name+'_velocity_shaft',(0,.24,0),(.035,.48,.04),m['cream'],tangent)
        tip=cone(name+'_velocity_tip',(0,.53,0),.07,.16,m['cream'],tangent);tip.rotation_euler.x=-math.pi/2
        return dict(root=r,core=core,outer=outer,inward=inward,tangent=tangent)

    def actor(self,phase,p,local):
        from character_director import CharacterDirector
        CharacterDirector(self.rig).apply(phase,p,local,self.current_event,self.switch)

    def animate_galaxy(self,g,phase,p,local,event):
        t=local/30;angle=-.55+t*(.30 if phase=='expected' else .75);g['outer'].location=(1.13*math.cos(angle),1.13*math.sin(angle),.07)
        predicted=-.55+t*.30
        if phase=='fit':predicted=predicted+(angle-predicted)*ease((local-event)/12)
        elif phase=='conclusion':predicted=angle
        g['expected'].location=(1.13*math.cos(predicted),1.13*math.sin(predicted),.07)
        visibility(g['expected'],phase in ('expected','hook','actual','fit','conclusion'))
        visibility(g['outer'],phase!='expected');visibility(g['trail'],phase!='expected')
        halo_on=phase in ('halo','fit','conclusion','identity')
        visibility(g['halo'],halo_on and (phase!='identity' or local<38))
        h=ease((local-event+24)/24) if phase=='halo' else 1
        g['halo'].scale=(max(.001,h),)*3
        for j,b in enumerate(g['beads']):
            aa=angle-(j+1)*(.035 if phase=='expected' else .085);b.location=(1.13*math.cos(aa),1.13*math.sin(aa),.065)
        g['outer'].rotation_euler.z=-angle*.3
        return angle

    def animate_force(self,g,t,speed,mag):
        angle=-.5+t*speed;x,y=1.05*math.cos(angle),1.05*math.sin(angle);g['outer'].location=(x,y,.05)
        for name in ('inward','tangent'):g[name].location=(x,y,.06);g[name].rotation_euler.z=angle
        g['inward'].scale=(mag,1,1);g['tangent'].scale=(1,speed/.7,1)

    def pose(self,shot,local):
        phase=shot['phase'];n=shot['endFrame']-shot['startFrame'];p=local/max(1,n-1);event=shot['emphasisEvent'];world=phase in ('observe','fit','conclusion');motion_local=local*shot['scene']['speed']/.75
        mode='world' if world else 'force' if phase=='gravity' else 'dual' if phase=='shortage' else 'space'
        if mode!=self.lastmode:
            for key,root in [('world',self.world),('space',self.space),('force',self.force),('dual',self.dual)]:visibility(root,key==mode)
            self.lastmode=mode
        if world:
            self.current_event=event['frame'];self.actor(phase,p,local);self.animate_galaxy(self.world_gal,phase,p,motion_local,event['frame'])
            self.targets={'head':self.rig.head,'character':self.rig.root,'outer':self.world_gal['outer'],'galaxy':self.world_gal['root']}
        elif mode=='space':
            self.animate_galaxy(self.gal,phase,p,motion_local,event['frame']);self.targets={'outer':self.gal['expected'] if phase=='expected' else self.gal['outer'],'galaxy':self.gal['root']}
        elif mode=='force':
            self.animate_force(self.gravity,motion_local/30,.60,.85);visibility(self.gravity['inward'],local>=event['frame']);visibility(self.gravity['tangent'],True)
            self.targets={'outer':self.gravity['outer'],'gravity':self.gravity['inward']}
        else:
            for i,g in enumerate(self.compares):
                self.animate_force(g,motion_local/30,.42 if i==0 else .85,.4 if i==0 else 1.05)
                visibility(g['tangent'],False);visibility(g['inward'],i==0 or local>=event['frame'])
            self.targets={'outer':self.compares[1]['outer']}
        cam=shot['cameraPlan'];aim=Vector(cam['aim']);direction=Vector(config('CAMERA_PRESETS')[cam['preset']]['direction'])
        self.camera.location=aim+direction;self.camera.rotation_euler=(aim-self.camera.location).to_track_quat('-Z','Y').to_euler()
        pulse=0;age=local-event['frame'];strength=config('EFFECT_PRESETS')['presets'][event['preset']]['cameraPunch']
        if 0<=age<16:pulse=strength*math.sin(math.pi*age/16)
        self.camera.data.ortho_scale=cam['scale']*(1-cam['push']*ease(p))/(1+pulse)
        self.diagnostics=dict(mode=mode,localFrame=local,cameraScale=self.camera.data.ortho_scale,analyticDiagram=True,event=event['type'] if age==0 else None)

    def handles(self):
        # A named-object map makes the packed scene reusable without rebuilding models.
        def encode(x):
            if isinstance(x,bpy.types.Object):return {'__object__':x.name}
            if isinstance(x,dict):return {k:encode(v) for k,v in x.items()}
            if isinstance(x,(list,tuple)):return [encode(v) for v in x]
            return x
        rig=self.rig
        return dict(objects=encode({k:getattr(self,k) for k in ('world','space','force','dual','table','switch','telescope','world_gal','gal','gravity','compares','camera')}),rig=encode(dict(root=rig.root,body=rig.body,head=rig.head,arms=rig.arms,legs=rig.legs,elbows=rig.elbows,moving=rig.moving,faces=rig.face.groups,eyes=rig.face.eyes)),rest={o.name:[list(a) for a in rig.rest[o.name]] for o in rig.moving})
    @classmethod
    def restore(cls,handles,size):
        from design_system import FaceController
        self=cls.__new__(cls)
        def decode(x):
            if isinstance(x,dict):
                if '__object__' in x:return bpy.data.objects[x['__object__']]
                return {k:decode(v) for k,v in x.items()}
            if isinstance(x,list):return [decode(v) for v in x]
            return x
        for k,v in decode(handles['objects']).items():setattr(self,k,v)
        r=decode(handles['rig']);face=FaceController.__new__(FaceController);face.groups=r.pop('faces');face.eyes=r.pop('eyes');r['face']=face;r['rest']=handles['rest'];self.rig=SimpleNamespace(**r)
        self.s=bpy.context.scene;self.s.render.resolution_x,self.s.render.resolution_y=size;self.targets={};self.lastmode=None
        return self
