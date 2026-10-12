"""Twelve full-body actions; all transforms reset and sampled in shot-local time."""
import math
from mathutils import Vector
def ease(x):x=max(0,min(1,x));return x*x*(3-2*x)
class CharacterDirector:
 def __init__(self,rig):self.r=rig
 def reset(self):
  for o in self.r.moving:
   p,rot,scale=self.r.rest[o.name];o.location=p;o.rotation_euler=rot;o.scale=scale
 def aim_hand(self,index,target):
  import bpy
  r=self.r;s=r.arms[index];e=r.elbows[index];bpy.context.view_layer.update()
  # Two link IK in torso coordinates, with a deliberate outward elbow bend.
  goal=r.body.matrix_world.inverted()@Vector(target);start=s.location.copy();delta=goal-start;d=min(.389,max(.06,delta.length));axis=delta.normalized();side=Vector(((-1 if index==0 else 1),-.5,.15));side=(side-axis*side.dot(axis)).normalized();elbow=start+axis*(d*.5)+side*math.sqrt(max(0,.20**2-(d*.5)**2))
  s.rotation_euler=(elbow-start).to_track_quat('-Z','Y').to_euler();bpy.context.view_layer.update();local=s.matrix_world.inverted()@(r.body.matrix_world@goal);e.rotation_euler=(local-e.location).to_track_quat('-Z','Y').to_euler()
 def pose(self,action,p,frame):
  r=self.r;self.reset();wave=math.sin(p*math.pi);beat=math.sin(p*math.tau);r.face.set('Curious',blink=(frame%109 in (57,58)))
  r.body.rotation_euler.x=.025*wave;r.head.rotation_euler.z=.025*beat
  if action=='OBSERVE':r.body.rotation_euler.x=.16*wave;r.head.rotation_euler.x=.12*wave;r.arms[1].rotation_euler.x=-.55*wave;r.elbows[1].rotation_euler.x=-.32*wave
  elif action in ('REACT','SURPRISE'):
   k=ease(p/.25)*(1-.45*ease((p-.45)/.45));r.face.set('Surprise' if p<.65 else 'Curious');r.body.rotation_euler.x=-.14*k;r.head.rotation_euler.x=-.09*k
   r.arms[1].rotation_euler.y=-.65*k;r.elbows[1].rotation_euler.x=-.40*k;r.legs[1].rotation_euler.x=.20*k;r.root.location.y=.12*k
  elif action=='POINT':r.body.rotation_euler.z=-.07*wave;r.head.rotation_euler.z=-.20*wave;r.arms[1].rotation_euler.x=-.95*wave;r.elbows[1].rotation_euler.x=-.30*wave
  elif action=='LOOK_AROUND':r.head.rotation_euler.z=.42*math.sin(p*math.tau);r.head.rotation_euler.x=-.20*ease((p-.35)/.4);r.body.rotation_euler.z=.12*math.sin(p*math.tau)
  elif action=='CONFUSED':r.face.set('Confused');r.head.rotation_euler.y=.15*beat;r.arms[0].rotation_euler.y=.35*wave;r.arms[1].rotation_euler.y=-.35*wave
  elif action=='THINK':r.face.set('Thinking');r.head.rotation_euler.x=.08;r.head.rotation_euler.y=.07*wave;r.arms[1].rotation_euler.x=-.35;r.elbows[1].rotation_euler.x=-.60
  elif action=='WALK':
   gait=math.sin(p*math.tau*2);r.legs[0].rotation_euler.x=.28*gait;r.legs[1].rotation_euler.x=-.28*gait;r.arms[0].rotation_euler.x=-.25*gait;r.arms[1].rotation_euler.x=.25*gait;r.root.location.x+=.5*(p-.5)
  elif action=='TURN':r.root.rotation_euler.z=.6*ease(p);r.head.rotation_euler.z=.16*math.sin(p*math.pi);r.arms[1].rotation_euler.x=-.2*wave
  elif action=='EXPLAIN':r.arms[1].rotation_euler.x=-.6*wave;r.arms[0].rotation_euler.y=.2*wave;r.head.rotation_euler.x=.04*beat
  elif action=='DISCOVER':
   k=ease(p/.35);r.face.set('Surprise' if p<.5 else 'Happy');r.body.rotation_euler.x=-.08*wave;r.head.rotation_euler.x=-.07*wave;r.arms[1].rotation_euler.y=-.65*k;r.elbows[1].rotation_euler.x=-.55*k
  elif action=='CELEBRATE':r.face.set('Happy');r.head.rotation_euler.x=.10*math.sin(p*math.tau*2);r.body.rotation_euler.y=.06*beat;r.arms[1].rotation_euler.y=-.30*wave;r.elbows[1].rotation_euler.x=-.25*wave
  else:raise ValueError('Unsupported action '+action)
  # Keep the lower of the two boots grounded while a step lifts the other.
  import bpy
  bpy.context.view_layer.update();boots=[o for o in r.root.children_recursive if o.type=='MESH' and o.name.startswith('wide_boot')]
  low=min((o.matrix_world@Vector(v)).z for o in boots for v in o.bound_box);r.root.location.z-=low
