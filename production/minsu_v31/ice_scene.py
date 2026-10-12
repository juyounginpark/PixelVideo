"""Authored ice-friction diagrams and Minsu acting. Not a molecular simulation."""
import math
import bpy
from mathutils import Vector
from art import box,empty,line,mesh,cone
from style import Materials,setup,character
from effects import smooth

def visible(root,on):
    for o in [root,*root.children_recursive]:o.hide_render=not on

def arrow(name,start,end,mat,parent,width=.027):
    a,b=Vector(start),Vector(end);v=b-a
    line(name+'_shaft',[a,b-v.normalized()*.10],mat,width,parent)
    tip=cone(name+'_head',(a+b)/2, .08,.20,mat,parent)
    tip.location=b-v.normalized()*.085;tip.rotation_euler=v.to_track_quat('Z','Y').to_euler()
    return tip

def molecule(name,loc,oxygen,hydrogen,parent,size=.15):
    root=empty(name,loc,parent)
    box(name+'_O',(0,0,0),(size,size,size),oxygen,root,size*.11)
    for sign in (-1,1):
        pos=(sign*size*.70,-size*.05,size*.61)
        line(name+'_OH',[(0,0,0),pos],hydrogen,size*.07,root)
        box(name+'_H',pos,(size*.46,)*3,hydrogen,root,size*.035)
    return root

class Scene:
    def __init__(self,spec):
        self.spec=spec;m=self.m=Materials();setup(bpy.context.scene)
        self.world=empty('ICE_PAVILION');self.macro=empty('MOLECULAR_SECTION');self.pathgroup=empty('SURFACE_PATH');self.comparegroup=empty('CONTROLLED_COMPARISON')
        self.rig=character(m);self.rig.root.parent=self.world
        # Purpose-built rink: dark architecture, cold skating surface, warm fixtures.
        box('ice_floor',(0,0,-.15),(12,14,.25),m['ice'],self.world)
        box('rink_wall',(0,3,1.3),(9,.17,2.6),m['wall'],self.world)
        for x in (-3.6,-1.8,0,1.8,3.6):
            box('window_frame',(x,2.88,1.7),(1.48,.12,1.1),m['midnight'],self.world,.04)
            box('window_glass',(x,2.795,1.7),(1.25,.035,.90),m['ice_dark'],self.world)
            box('window_mullion',(x,2.75,1.7),(.045,.04,.94),m['rail'],self.world)
            box('warm_lamp',(x,2.6,2.57),(.48,.26,.055),m['light'],self.world)
            box('pier',(x+.78,2.7,1.35),(.11,.25,2.8),m['navy'],self.world)
        # Discrete ice scratches with a stable world-space texel rhythm.
        for j in range(12):
            x=-3+(j%6)*1.0;y=-1.8+(j//6)*1.6
            line('ice_score',[(x,y,-.016),(x+.22,y+.17,-.016),(x+.52,y+.20,-.016)],m['ice_top'],.008,self.world)
        for x in (-2.4,2.4):
            for y in (-.7,1.5,2.3):box('barrier_post',(x,y,.40),(.065,.065,.86),m['rail'],self.world)
            box('warm_rail',(x,.8,.81),(.09,3.5,.09),m['amber'],self.world,.01)
        for j in range(5):
            box('rear_bench',(-2.6+j*1.25,2.14,.34),(.92,.30,.08),m['rail'],self.world)
            for x in (-.3,.3):box('bench_leg',(-2.6+j*1.25+x,2.14,.15),(.06,.19,.30),m['navy'],self.world)
        self.trail=empty('travel_evidence',parent=self.world)
        # Initial position is the actual frame-zero pose, not a decorative offset.
        line('actual_start_to_finish',[(-.48,0,.0),(-.1,0,.0),(.4,.24,.0),(.65,.40,.0)],m['amber'],.018,self.trail)
        self.ghost=empty('previous_position',(-.48,0,0),self.trail)
        for z,w,h in [(.53,.48,.45),(1.1,.80,.68)]:
            line('before_outline',[(-w/2,0,z-h/2),(w/2,0,z-h/2),(w/2,0,z+h/2),(-w/2,0,z+h/2),(-w/2,0,z-h/2)],m['ice_top'],.014,self.ghost)
        # An isolated cutaway. Warm mobile surface above cool bonded interior.
        self.base=box('ice_cutaway',(0,.12,-.48),(2.45,1.35,.20),m['ice_dark'],self.macro,.025)
        self.surface=box('surface_reference',(0,.12,.10),(2.45,1.35,.032),m['ice_top'],self.macro)
        self.bulk=[]
        for depth in range(2):
            for row in range(3):
                for col in range(7):
                    pos=(-1.04+col*.347,-.16+depth*.56,-.30+row*.16)
                    root=molecule(f'bulk_{depth}_{row}_{col}',pos,m['ice'],m['ice_top'],self.macro,.12)
                    self.bulk.append((root,Vector(pos)))
                    if col<6:line('bulk_bond',[pos,(pos[0]+.347,pos[1],pos[2])],m['bond'],.014,self.macro)
                    if row<2:line('bulk_vertical',[pos,(pos[0],pos[1],pos[2]+.16)],m['bond'],.012,self.macro)
        self.surface_molecules=[]
        for i in range(10):
            pos=(-.96+(i%5)*.46,-.22+(i//5)*.60,.285)
            root=molecule('mobile_'+str(i),pos,m['oxygen'],m['hydrogen'],self.macro,.16)
            self.surface_molecules.append((root,Vector(pos)))
        self.slider=empty('contact_slider',(-.8,.0,.52),self.macro)
        box('steel_contact',(0,.10,.15),(.72,.64,.22),m['metal'],self.slider,.045)
        box('steel_contact_dark',(0,.10,.285),(.55,.48,.075),m['navy'],self.slider,.02)
        self.boot=empty('boot_closeup',parent=self.macro)
        box('boot_sole',(0,.10,.36),(1.05,.65,.13),m['shoe'],self.boot,.04)
        box('boot_body',(.12,.13,.68),(.85,.59,.55),m['navy'],self.boot,.06)
        box('boot_cuff',(.27,.18,1.00),(.53,.58,.22),m['mint'],self.boot,.03)
        box('boot_blade',(0,.10,.235),(1.18,.052,.07),m['metal'],self.boot)
        for j in range(3):box('boot_lace',(-.2+j*.14,-.18,.81),(.045,.07,.2),m['cream'],self.boot)
        self.contact_glow=box('active_boundary',(0,-.02,.175),(2.20,.045,.024),m['amber'],self.macro)
        # Large, readable trajectory demonstration (three representative molecules).
        box('path_ice',(0,.10,-.19),(2.5,.9,.30),m['ice_dark'],self.pathgroup,.03)
        for i in range(9):box('path_fixed_pixel',(-1.04+i*.26,-.36,-.18),(.16,.03,.12),m['ice'],self.pathgroup)
        self.tracked=molecule('tracked_water',(-.8,-.18,.20),m['oxygen'],m['hydrogen'],self.pathgroup,.25)
        self.neighbor1=molecule('left_neighbor',(-.90,.22,.20),m['ice_top'],m['cream'],self.pathgroup,.21)
        self.neighbor2=molecule('right_neighbor',(.86,.15,.20),m['ice_top'],m['cream'],self.pathgroup,.21)
        self.pathmarks=[]
        for i in range(13):
            self.pathmarks.append(box('motion_path',(-.78+i*.12,-.23,.08),(.065,.045,.024),m['amber'],self.pathgroup))
        # Identical-speed steel contacts; arrows communicate friction qualitatively.
        self.comparison=[]
        for index,x in enumerate((-.78,.78)):
            root=empty('cold' if index==0 else 'less_cold',(x,0,0),self.comparegroup)
            slab=box('condition_ice',(0,0,-.20),(1.30,1.0,.42),m['ice_dark'] if index==0 else m['ice'],root,.04)
            box('condition_top',(0,0,.025),(1.25,.95,.03),m['ice_top'],root)
            ball=empty('steel_sphere',(-.34,0,.23),root)
            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=.19);o=bpy.context.object;o.name='steel_sphere_mesh';o.parent=ball;o.location=(0,0,0);o.data.materials.append(m['metal'])
            resistance=empty('friction_force',parent=root)
            arrow('friction_arrow',(.35,-.55,.10),(-.42 if index==0 else .08,-.55,.10),m['coral'],resistance,.029)
            beads=[]
            for j in range(4):beads.append(molecule('condition_molecule',(-.42+j*.28,-.19,.12),m['ice'] if index==0 else m['oxygen'],m['hydrogen'],root,.09))
            self.comparison.append((root,slab,ball,resistance,beads))
        # Native orthographic camera; changes always relate to a named subject.
        bpy.ops.object.camera_add();self.camera=bpy.context.object;self.camera.name='V31_DIRECTOR_CAMERA';bpy.context.scene.camera=self.camera
        self.camera.data.type='ORTHO';self.camera.data.dof.use_dof=False
        self.targets={};self.diagnostics={};self.lastgroup=None

    def reset_actor(self):
        r=self.rig
        for o in r.moving:
            loc,rot,scale=r.rest[o.name];o.location=loc;o.rotation_euler=rot;o.scale=scale
        r.face.set('Neutral');r.root.location.z=.025

    def acting(self,phase,p,t):
        self.reset_actor();r=self.rig
        if phase in ('hook','loop'):
            q=p if phase=='hook' else .65*p
            slip=smooth((q-.12)/.50);recover=smooth((q-.70)/.30)
            r.root.location.x=-.48+1.0*slip;r.root.rotation_euler.z=-.12+.22*slip
            r.body.rotation_euler.y=-.17*slip+.13*recover;r.body.rotation_euler.z=-.13*math.sin(q*math.pi)
            r.legs[1].rotation_euler.y=-.65*slip*(1-.4*recover);r.legs[0].rotation_euler.y=.32*slip
            r.arms[0].rotation_euler.y=-1.15*slip;r.arms[1].rotation_euler.y=1.1*slip
            r.elbows[0].rotation_euler.x=-.35*slip;r.elbows[1].rotation_euler.x=-.45*slip
            r.head.rotation_euler.y=.14*slip;r.head.rotation_euler.x=.08*math.sin(q*math.pi)
            r.face.set('Happy' if q<.17 else ('Surprise' if q<.68 else 'Worried'))
        elif phase=='inspect':
            crouch=smooth(p/.35);look=smooth((p-.28)/.40)
            r.root.location.x=-.35;r.body.location.z-=.10*crouch;r.body.rotation_euler.x=.27*crouch
            r.head.rotation_euler.x=.32*look;r.head.rotation_euler.z=-.12*look
            r.arms[1].rotation_euler.x=-.9*look;r.arms[1].rotation_euler.y=.25*look;r.elbows[1].rotation_euler.x=-.4*look
            r.legs[0].rotation_euler.x=.22*crouch;r.legs[1].rotation_euler.x=-.18*crouch
            r.face.set('Worried' if p<.22 else ('Curious' if p<.68 else 'Thinking'))
        elif phase=='return':
            q=smooth(p);r.root.location.x=-.45+.7*q;r.root.rotation_euler.z=.15-.30*q
            r.arms[0].rotation_euler.y=-.75*(1-q);r.arms[1].rotation_euler.y=.75*(1-q)
            r.legs[1].rotation_euler.y=-.4*(1-q);r.head.rotation_euler.z=.16*math.sin(p*math.pi)
            r.face.set('Surprise' if p<.25 else ('Happy' if p<.65 else 'Thinking'))
        elif phase=='before_after':
            q=smooth(p);r.root.location=(.40+.25*q,.24+.16*q,.025);r.root.rotation_euler.z=.10
            r.arms[0].rotation_euler.y=-.30;r.arms[1].rotation_euler.y=.45
            r.legs[1].rotation_euler.x=-.15*math.sin(p*math.pi);r.head.rotation_euler.x=-.12
            r.face.set('Curious' if p<.4 else 'Happy')
        elif phase=='result':
            q=smooth(p);r.root.location.x=-.25+.45*q;r.root.rotation_euler.z=-.08+.18*q
            r.arms[1].rotation_euler.x=-.65*math.sin(p*math.pi);r.arms[1].rotation_euler.y=.25
            r.head.rotation_euler.x=.14*math.sin(p*math.pi*3);r.head.rotation_euler.z=.13*math.sin(p*math.pi)
            r.legs[0].rotation_euler.x=.16*math.sin(p*math.pi*2);r.legs[1].rotation_euler.x=-.16*math.sin(p*math.pi*2)
            r.face.set('Thinking' if p<.17 else ('Happy' if p<.66 else 'Determined'))
        if int(t*30)%101 in (0,1,2):r.face.set('Curious' if phase=='inspect' else 'Happy',blink=True)

    def frame_camera(self,pos,aim,scale):
        self.camera.location=pos;self.camera.rotation_euler=(Vector(aim)-self.camera.location).to_track_quat('-Z','Y').to_euler();self.camera.data.ortho_scale=scale

    def pose(self,frame):
        shot=next(s for s in self.spec['shots'] if s['startFrame']<=frame<s['endFrame']);phase=shot['phase'];p=(frame-shot['startFrame'])/(shot['endFrame']-shot['startFrame']);t=frame/30
        mode='world' if phase in ('hook','inspect','return','before_after','result','loop') else ('path' if phase=='path' else ('compare' if phase=='compare' else 'macro'))
        if mode!=self.lastgroup:
            for key,root in [('world',self.world),('macro',self.macro),('path',self.pathgroup),('compare',self.comparegroup)]:visible(root,key==mode)
            self.lastgroup=mode
        self.targets={};self.diagnostics={'phase':phase,'mode':mode,'physicalSimulation':False}
        if mode=='world':
            self.acting(phase,p,t);visible(self.trail,phase=='before_after')
            x=self.rig.root.location.x
            if phase=='before_after':self.frame_camera((2.95,-4.5,6.2),(.35,.10,.55),4.35)
            elif phase=='inspect':self.frame_camera((1.7,-5,2.25),(-.14,0,.72),3.65-.10*smooth(p))
            else:self.frame_camera((1.7+x*.20,-5.4,2.35),(x*.45,0,.78),4.05-.10*smooth(p))
            self.targets={'minsu':self.rig.head,'body':self.rig.root}
            self.diagnostics.update(characterRoot=list(self.rig.root.location),expressionPhase=p)
        elif mode=='path':
            q=smooth(p);self.tracked.location=(-.78+1.45*q,-.18,.21+.05*math.sin(q*math.pi*2));self.tracked.rotation_euler=(0,-q*math.tau*.60,.12*math.sin(q*math.pi))
            self.neighbor1.rotation_euler.y=.05*math.sin(t*3);self.neighbor2.rotation_euler.y=-.08*math.sin(t*3)
            for j,obj in enumerate(self.pathmarks):obj.hide_render=j/13>q
            focus=-.18+.30*q;self.frame_camera((focus+.6,-4.8,2.25),(focus,0,.06),3.45-.08*q)
            self.targets={'molecule':self.tracked,'surface':self.tracked};self.diagnostics['trackedPosition']=list(self.tracked.location)
        elif mode=='compare':
            for i,(root,slab,ball,resistance,beads) in enumerate(self.comparison):
                ball.location.x=-.34+.68*smooth(p)
                for j,g in enumerate(beads):g.location.x=-.42+j*.28+(.006 if i==0 else .045)*math.sin(t*5+j);g.rotation_euler.y=(.03 if i==0 else .25)*math.sin(t*4+j)
                visible(resistance,p>.28)
            self.frame_camera((.25,-5.8,3.3),(0,0,.10),5.85-.10*smooth(p))
            self.targets={'surface':self.comparison[0][1],'cold':self.comparison[0][1],'warm':self.comparison[1][1]}
            self.diagnostics['comparisonControl']='same authored slider speed; friction arrows qualitative; temperatures from study'
        else:
            contact=phase=='contact';visible(self.boot,contact);visible(self.slider,phase in ('discovery','factors'))
            for root,pos in self.bulk:
                root.location=pos+Vector((.004*math.sin(t*4+pos.x),0,.004*math.cos(t*4+pos.x)))
            for i,(root,pos) in enumerate(self.surface_molecules):
                root.location=pos+Vector((.10*math.sin(t*2.2+i*.70),.035*math.cos(t*2+i),.025*math.sin(t*3+i)))
                root.rotation_euler.y=.35*math.sin(t*2.6+i)
                visible(root,not contact)
            self.surface.hide_render=not contact;self.contact_glow.hide_render=phase not in ('contact','discovery','factors')
            self.slider.location=(-.86+1.62*smooth(p),0,.40)
            self.slider.rotation_euler=(0,0,0)
            if contact:
                self.boot.location.x=-.15+.30*smooth(p);self.frame_camera((2.2,-5.2,2.4),(0,.1,.48),3.85-.25*smooth(p))
            elif phase=='structure':self.frame_camera((2.0,-5.8,2.65),(0,.10,.0),4.6-.15*smooth(p))
            elif phase=='discovery':
                follow=self.slider.location.x*.35;self.frame_camera((follow+1.0,-5.4,2.3),(follow,.12,.25),4.35-.28*smooth(p))
            else:
                self.slider.location.z=.40-.035*math.sin(p*math.pi);self.frame_camera((.40,-5.8,1.2),(0,.08,.15),4.6)
            self.targets={'surface':self.surface if contact else self.surface_molecules[3][0], 'molecule':self.surface_molecules[3][0]}
            if phase in ('discovery','factors'):self.targets['slider']=self.slider
            self.diagnostics.update(surfaceMobility=.10,bulkMobility=.004,sliderPosition=list(self.slider.location))
        bpy.context.view_layer.update()
