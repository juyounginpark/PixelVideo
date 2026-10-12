"""Whole-body observation and a two-link reach to an actual scene-space switch."""
import math
import bpy
from mathutils import Vector
def ease(t):t=max(0,min(1,t));return t*t*(3-2*t)
class CharacterDirector:
    def __init__(self,rig):self.r=rig
    def reach(self,target,strength):
        r=self.r;arm=r.arms[1];elbow=r.elbows[1];bpy.context.view_layer.update()
        shoulder=arm.matrix_world.translation;delta=Vector(target)-shoulder;distance=max(.03,min(.198+.139-.002,delta.length));direction=delta.normalized()
        bend=Vector((0,-1,.25));bend=(bend-direction*bend.dot(direction)).normalized()
        cosine=max(-1,min(1,(.198**2+distance**2-.139**2)/(2*.198*distance)))
        joint=shoulder+direction*(.198*cosine)+bend*(.198*math.sqrt(1-cosine*cosine));end=shoulder+direction*distance
        world1=(joint-shoulder).to_track_quat('-Z','Y');local1=arm.parent.matrix_world.to_quaternion().inverted()@world1
        base=arm.rotation_euler.to_quaternion();arm.rotation_euler=base.slerp(local1,strength).to_euler();elbow.location=(0,0,-.198)
        world2=(end-joint).to_track_quat('-Z','Y');local2=world1.inverted()@world2;elbow.rotation_euler=elbow.rotation_euler.to_quaternion().slerp(local2,strength).to_euler()
    def apply(self,phase,p,local,event,switch):
        r=self.r
        for o in r.moving:
            loc,rot,scale=r.rest[o.name];o.location=loc;o.rotation_euler=rot;o.scale=scale
        r.root.location=(-.63,-.30,.02);r.root.rotation_euler.z=.22
        look=ease(p/.22);r.head.rotation_euler.z=.22*look;r.head.rotation_euler.x=.20*look
        r.body.rotation_euler.x=.06*look;r.face.set('Curious')
        switch.location.y=-.77;switch.location.z=.67;switch.scale.y=2.5
        if phase=='observe':
            # Gaze, torso and pointing arm all refer to the observation table.
            r.body.rotation_euler.y=.08*look;r.body.rotation_euler.x=.12*look
            r.arms[1].rotation_euler.y=-.55*look;r.arms[1].rotation_euler.x=.25*look;r.elbows[1].rotation_euler.x=.30*look
            r.legs[0].rotation_euler.x=.10*look;r.legs[1].rotation_euler.x=-.08*look;r.face.set('Thinking' if p>.60 else 'Curious')
            r.arms[0].rotation_euler.y=-.13*look
        elif phase=='conclusion':
            r.arms[1].rotation_euler.y=-.4*look;r.elbows[1].rotation_euler.x=.2*look
            r.body.rotation_euler.y=.05*look;r.head.rotation_euler.x=.17+.07*math.sin(p*math.tau)
            r.legs[1].rotation_euler.x=-.05*look;r.face.set('Happy' if p>.2 else 'Thinking')
        else:
            anticipate=math.sin(math.pi*min(1,p/.20));press=ease((local-event+25)/22)*(1-.35*ease((local-event-8)/22))
            r.body.rotation_euler.y=-.035*anticipate+.06*press;r.body.rotation_euler.x=.05*press
            r.arms[0].rotation_euler.y=-.15*press;r.legs[1].rotation_euler.x=-.09*press
            r.head.rotation_euler.x=.17+.08*math.sin(max(0,local-event)/30*math.pi)*ease((local-event)/8)
            r.face.set('Happy' if local>event+8 else 'Thinking')
            switch.location.z=.67-.025*max(0,1-abs(local-event)/8)
            bpy.context.view_layer.update();self.reach(switch.matrix_world.translation,press)
        if local%113 in (105,106):r.face.set('Happy' if phase=='conclusion' else 'Curious',blink=True)
