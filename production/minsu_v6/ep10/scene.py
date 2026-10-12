"""Explanatory cup optics; color depends on scripted lamp geometry, not a spectral solver."""
from pathlib import Path
import sys,math,bpy
from mathutils import Vector
J=Path(__file__).resolve().parent;sys.path.insert(0,str(J.parents[1]/'minsu_v5'))
from art_v5 import Materials,setup,character,box,empty,visibility,mesh
from character_director import CharacterDirector,ease
from design_system import linear
class Scene:
 def __init__(self,size):
  self.s=setup(size);self.m=Materials();m=self.m
  self.world=empty('WARM_GALLERY');box('floor',(0,0,-.12),(16,16,.24),m['floor'],self.world)
  box('gallery_wall',(0,2.3,1.5),(8,.15,3),m['wall'],self.world)
  for x in [-2,2]:
   box('shelf',(x,1.95,.8),(.7,.6,.12),m['wood'],self.world);box('display_block',(x,1.95,1.1),(.35,.35,.5),m['cream'],self.world)
  self.table=empty('TABLE',(.4,0,0),self.world);box('table_top',(0,0,.91),(1.05,.9,.12),m['wood'],self.table)
  for x in [-.4,.4]:
   for y in [-.32,.32]:box('table_leg',(x,y,.43),(.12,.12,.86),m['wood'],self.table)
  self.cup=empty('SAME_CUP',(.4,0,.99),self.world);self.green=m['leaf'].copy();self.red=m['red'].copy()
  self.green.name='CUP_REFLECTION_GREEN';self.red.name='CUP_TRANSMISSION_RED'
  self.parts=[]
  self.parts.append(self.ring('cup_body',[(.24,0),(.28,.15),(.37,.55),(.39,.72)],self.green,self.cup,.055))
  self.parts.append(self.ring('cup_rim',[(.39,.70),(.39,.76)],self.green,self.cup,.05))
  self.ring('metal_foot',[(.26,0),(.26,.06)],m['metal'],self.cup,.15)
  for i in range(8):
   a=i*math.tau/8;vine=box('cage_rib',(.37*math.cos(a),.37*math.sin(a),.43),(.065,.065,.49),self.green,self.cup);vine.rotation_euler.z=a;self.parts.append(vine)
  self.lamp=empty('MOVING_WHITE_LAMP',(-.35,-.65,0),self.world);box('lamp_base',(0,0,.08),(.3,.3,.16),m['metal'],self.lamp);box('lamp_pole',(0,0,.72),(.07,.07,1.3),m['metal'],self.lamp)
  self.lamphead=box('lamp_head',(0,0,1.4),(.22,.20,.25),m['navy'],self.lamp);self.bulb=box('white_light',(0,-.115,1.4),(.15,.025,.15),m['cream'],self.lamp)
  self.knob=box('lamp_handle',(0,-.12,.98),(.12,.14,.13),m['wood'],self.lamp)
  self.beam=box('white_incident_light',(0,0,0),(.035,.035,1),m['cream'],self.world)
  self.outbeam=box('observed_light_path',(0,0,0),(.05,.05,1),m['mint'],self.world)
  self.rig=character(m);self.director=CharacterDirector(self.rig)
  self.macro=empty('SAME_GLASS_MACRO');box('macro_background',(0,1,1.3),(10,.1,8),m['micro_bg'],self.macro)
  self.wall=box('same_glass_wall',(0,0,1.3),(.48,.16,1.65),m['glass'],self.macro)
  self.nano=[]
  for x,z in [(-.12,.72),(.10,.93),(-.08,1.15),(.13,1.38),(-.12,1.6),(.08,1.83)]:self.nano.append(box('metal_particle',(x,-.12,z),(.09,.09,.09),m['amber'] if len(self.nano)%2 else m['metal'],self.macro))
  self.photons=[]
  for i in range(9):self.photons.append(box('light_packet',(0,-.2,1.3),(.10,.10,.10),m['cream'],self.macro))
  self.rays=[]
  for name,col in [('incoming','cream'),('reflected','mint'),('transmitted','red')]:self.rays.append(box(name,(0,-.19,1.3),(1,.025,.035),m[col],self.macro))
  bpy.ops.object.camera_add();self.camera=bpy.context.object;self.camera.data.type='ORTHO';self.s.camera=self.camera
 def ring(self,name,rings,mat,parent,thickness):
  n=12;vertices=[]
  for r,z in rings:
   for radius in [r,max(.02,r-thickness)]:vertices.extend((radius*math.cos(i*math.tau/n),radius*math.sin(i*math.tau/n),z) for i in range(n))
  faces=[]
  for j in range(len(rings)-1):
   for i in range(n):
    k=(i+1)%n;a=j*2*n;b=(j+1)*2*n
    faces.extend([(a+i,a+k,b+k,b+i),(a+n+k,a+n+i,b+n+i,b+n+k)])
  for j in [0,len(rings)-1]:
   a=j*2*n
   for i in range(n):k=(i+1)%n;faces.append((a+i,a+n+i,a+n+k,a+k) if j==0 else (a+i,a+k,a+n+k,a+n+i))
  data=bpy.data.meshes.new(name);data.from_pydata(vertices,[],faces);data.update();o=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(o);o.parent=parent;o.data.materials.append(mat);return o
 def pose(self,shot,f):
  phase=shot['scene']['phase'];local=f-shot['startFrame'];p=local/(shot['endFrame']-shot['startFrame']-1);macro=phase in ('particles','paths')
  visibility(self.world,not macro);visibility(self.rig.root,not macro);visibility(self.macro,macro)
  if phase=='hook':t=ease((f-4)/40)
  elif phase=='inspect':t=1-ease((local-50)/55)
  elif phase=='front':t=0
  elif phase=='back':t=ease(local/65)
  elif phase=='return':t=1
  elif phase=='payoff':t=ease((local-55)/45) if local>55 else 1-ease(local/45)
  else:t=1
  # Identical world snapshot at frame 480 and return frame 720.
  if phase=='return':action='POINT'
  elif phase=='inspect':action='WALK' if 50<local<105 else 'THINK'
  elif phase in ('hook','payoff'):action='SURPRISE' if local>24 else 'WALK'
  elif phase=='back':action='WALK' if local<65 else 'OBSERVE'
  else:action='OBSERVE'
  self.director.pose(action,p,f);self.rig.root.location=(-.8,-1+1.35*t,0);self.rig.root.scale=(1,)*3;self.rig.head.rotation_euler.z=-.18
  self.lamp.location=(-.35,-.65+1.35*t,0);self.lamphead.rotation_euler.z=math.pi*t
  self.bulb.location.y=-.115+ .23*t
  bpy.context.view_layer.update()
  # Manual stage placement follows the action; re-establish foot contact afterwards.
  boots=[o for o in self.rig.root.children_recursive if o.type=='MESH' and o.name.startswith('wide_boot')]
  minimum=min((o.matrix_world@Vector(v)).z for o in boots for v in o.bound_box)
  self.rig.root.location.z-=minimum;bpy.context.view_layer.update()
  self.director.aim_hand(1,self.knob.matrix_world.translation)
  origin=Vector((-.35,-.65+1.35*t,1.4));target=Vector((.4,0,1.4))
  for obj,a,b in [(self.beam,origin,target),(self.outbeam,target,Vector((.4,-.95,1.4)))]:
   obj.location=(a+b)/2;obj.scale.z=(b-a).length;obj.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();visibility(obj,phase in ('front','back','payoff'))
  self.outbeam.data.materials[0]=self.m['red'] if t>=.5 else self.m['mint']
  for o in self.parts:o.data.materials[0]=self.red if t>=.5 else self.green
  self.cup.rotation_euler.z=.12*math.sin(p*math.pi) if phase=='inspect' else 0
  for i,o in enumerate(self.nano):o.scale=(ease((local-i*6)/20) if phase=='particles' else 1,)*3
  for i,o in enumerate(self.photons):
   visibility(o,phase=='paths');u=((local+i*11)%90)/90
   if i<3:o.location=(-1.5+1.5*u,-.2,1.45);o.data.materials[0]=self.m['cream']
   elif i<6:o.location=(-1.35*u,-.2,1.45+.65*u);o.data.materials[0]=self.m['mint']
   else:o.location=(1.35*u,-.2,1.45);o.data.materials[0]=self.m['red']
  for i,o in enumerate(self.rays):
   visibility(o,phase=='paths');o.location=((- .75 if i<2 else .75),-.19,1.45+(.30 if i==1 else 0));o.scale.x=1.5;o.rotation_euler.y=-.42 if i==1 else 0
  if macro:
   aim=Vector((0,0,1.2));direction=Vector((0,-8,.1));scale=5.5
   if phase=='particles':scale=1.6+3.9*ease(local/25)
   if phase=='paths':scale=5.5-3.9*ease((local-95)/24)
  else:
   aim=Vector((-.05,0,.90));direction=Vector((0,-8,3.1));scale=4.9
   if shot['cameraPlan'] in ('close','follow'):aim=Vector((-.1,0,1.1));scale=4.6;direction=Vector((.7,-8,2.5))
   if shot['cameraPlan']=='three_quarter':direction=Vector((1.5,-8,3.1))
   if shot['cameraPlan']=='match':scale=4.6;aim=Vector((-.1,0,1.1));direction=Vector((.7,-8,2.5))
   if phase=='back' and local>90:
    zoom=ease((local-90)/29);scale=4.6-3*zoom;aim=aim.lerp(Vector((.4,0,1.4)),zoom)
   if phase=='return':
    zoom=ease(local/25);scale=1.6+3*zoom;aim=Vector((.4,0,1.4)).lerp(aim,zoom)
  event=shot.get('emphasisEvent',{});pulse=max(0,1-abs(f-event.get('frame',-100))/10)*.045
  self.camera.location=aim+direction;self.camera.rotation_euler=(aim-self.camera.location).to_track_quat('-Z','Y').to_euler();self.camera.data.ortho_scale=scale*(1-pulse)
  return {'glass':self.wall} if macro else {'cup':self.cup,'character':self.rig.root,'lamp':self.lamp}
