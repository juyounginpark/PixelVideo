"""Source-backed red-rain adapter: courtyard, observation lab and explicit macro models."""
import math,random,bpy
from mathutils import Vector
from art_v5 import Materials,setup,character,box,empty,mesh,line,cylinder,ring,visibility
from character_director import CharacterDirector,ease
from common import config

class Scene:
 def __init__(self,size):
  self.s=setup(size);self.m=Materials();m=self.m
  self.garden=empty('WORLD_COURTYARD');self.lab=empty('WORLD_LAB');self.micro=empty('WORLD_MICRO');self.compare=empty('WORLD_COMPARE')
  self.rig=character(m);self.director=CharacterDirector(self.rig)
  box('courtyard_ground',(0,0,-.08),(8,8,.16),m['floor'],self.garden)
  box('sage_garden_wall',(0,1.6,.60),(6,.16,1.2),m['wall'],self.garden)
  for x in [-2,-1.2,-.4,.4,1.2,2]:box('fence_cap',(x,1.6,1.23),(.70,.24,.09),m['cream'],self.garden)
  box('house_warm_wall',(-2.1,2.0,1.4),(1.6,.9,2.8),m['cream'],self.garden)
  box('house_roof',(-2.1,2.0,2.85),(1.9,1.25,.18),m['roof'],self.garden)
  box('window_frame',(-2.0,1.52,1.7),(.8,.05,.9),m['wood'],self.garden)
  box('window_blue',(-2.0,1.48,1.7),(.65,.02,.75),m['water'],self.garden)
  self.tree=empty('COURTYARD_TREE',(1.35,.80,0),self.garden)
  box('tree_trunk',(0,0,.75),(.23,.22,1.5),m['wood'],self.tree)
  for x,y,z,sz in [(-.25,0,1.6,.65),(.22,0,1.85,.72),(0,.05,2.2,.6)]:box('block_canopy',(x,y,z),(sz,.52,sz*.7),m['leaf'],self.tree,.03)
  for i in range(7):box('tree_algal_patch',((i%3-1)*.055,-.116,.4+i*.055),(.07,.006,.055),m['red'],self.tree)
  for x,y in [(-1.25,.8),(1.0,1.25),(2,0)]:
   box('plant_pot',(x,y,.16),(.35,.35,.3),m['roof'],self.garden)
   for dx in [-.11,0,.11]:box('plant_leaf',(x+dx,y,.4+abs(dx)),(.13,.13,.25),m['leaf'],self.garden)
  self.umbrella=empty('PROP_UMBRELLA',(-.5,.12,1.92),self.garden)
  verts=[(0,0,.2)]+[(.78*math.cos(i*math.tau/8),.78*math.sin(i*math.tau/8),0) for i in range(8)]
  mesh('white_umbrella_canopy',verts,[(0,i+1,(i+1)%8+1) for i in range(8)],m['cream'],self.umbrella)
  for i in range(8):line('umbrella_rib',[(0,0,.201),verts[i+1]],m['glass'],.009,self.umbrella)
  cylinder('umbrella_pole',(0,0,-.67),.016,1.36,m['wood'],self.umbrella,8)
  self.spots=[]
  for i in range(17):
   ang=i*2.399;r=.18+(i%5)*.10;x,y=r*math.cos(ang),r*math.sin(ang);z=.20*(1-r/.78)+.009
   self.spots.append(box('red_rain_stain',(x,y,z),(.07,.065,.012),m['red'],self.umbrella))
  rng=random.Random(508);self.drops=[];self.drop_seeds=[]
  for i in range(42):
   self.drop_seeds.append([rng.uniform(-1.5,1.4),rng.uniform(-.65,1.1),rng.random()])
   self.drops.append(box('red_raindrop',(0,0,1),(.025,.025,.115),m['red'],self.garden,.004))
  self.handjar=self.make_jar('hand_sample',self.garden,.38)
  box('lab_floor',(0,0,-.08),(7,7,.16),m['cream'],self.lab)
  box('lab_wall',(0,1.4,1.2),(6,.12,2.4),m['wall'],self.lab)
  for x in [-1.6,1.45]:
   box('lab_window_border',(x,1.31,1.6),(.78,.04,.9),m['wood'],self.lab)
   box('lab_window',(x,1.28,1.6),(.68,.02,.8),m['water'],self.lab)
  self.table=empty('LAB_TABLE',(0,0,0),self.lab)
  box('table_top',(.40,.23,.78),(1.7,.80,.10),m['wood'],self.table)
  for x in [-.34,1.13]:
   for y in [-.1,.55]:box('table_leg',(x,y,.37),(.09,.09,.74),m['wood'],self.table)
  self.labjar=self.make_jar('lab_sample',self.lab,.50);self.labjar['root'].location=(.12,-.02,1.03)
  self.scope=empty('MICROSCOPE',(.78,.17,.86),self.lab)
  box('scope_base',(0,0,.035),(.46,.32,.07),m['navy'],self.scope)
  box('scope_arm',(0,.07,.29),(.10,.12,.51),m['metal'],self.scope)
  box('scope_stage',(0,-.10,.21),(.31,.30,.05),m['navy'],self.scope)
  arm=box('scope_tube',(0,-.05,.57),(.16,.16,.34),m['cream'],self.scope,.018);arm.rotation_euler.x=-.45
  cylinder('scope_knob',(.11,.07,.29),.065,.08,m['navy'],self.scope,12).rotation_euler.y=math.pi/2
  self.closejar=self.make_jar('settling_sample',None,1.0);self.closejar['root'].location=(0,0,.72)
  self.closeback=empty('JAR_BACKDROP');box('jar_background',(0,1.0,.75),(5,.08,4),m['wall'],self.closeback);box('jar_bench',(0,0,.27),(4,2,.12),m['cream'],self.closeback)
  box('micro_dark_background',(0,0,-.12),(6,6,.08),m['micro_bg'],self.micro)
  self.dish=cylinder('culture_agar',(0,0,0),.88,.05,m['agar'],self.micro,32);self.dish_rim=ring('culture_dish_edge',(0,0,.045),.92,m['glass'],self.micro,.024)
  self.cells=[]
  for i in range(16):
   a=i*2.399;r=.16+.54*(i%5)/5
   self.cells.append(self.cell('MICRO_RED_CELL',(r*math.cos(a),r*math.sin(a),.08),.09,m['red'],self.micro))
  self.colony=[]
  for i,(x,y) in enumerate([(-.42,-.36),(-.30,-.26),(-.17,-.14),(-.04,-.02),(.09,.10),(.20,.24),(.33,.36),(.42,.47),(-.02,.15),(-.15,.27),(-.28,.37),(.19,-.02),(.33,-.12),(.45,-.20)]):
   self.colony.append(self.cell('ALGAL_BRANCH_CELL',(x,y,.09),.095,m['alga'] if i%4 else m['red'],self.micro))
  self.comparejar=self.make_jar('rain_comparison',self.compare,.80);self.comparejar['root'].location=(-.62,0,.63)
  self.bark=empty('BARK_SAMPLE',(.65,0,.73),self.compare);box('bark_strip',(0,0,0),(.54,.25,1.05),m['wood'],self.bark,.02)
  for i in range(12):self.cell('bark_alga_patch',(((i%3)-1)*.125,-.143,(i//3-1.5)*.17),.074,m['red'],self.bark)
  box('comparison_table',(0,.2,.11),(3.4,1.8,.14),m['cream'],self.compare)
  bpy.ops.object.camera_add();self.camera=bpy.context.object;self.camera.name='V5_CAMERA';self.camera.data.type='ORTHO';self.s.camera=self.camera
  self.targets={};self.diagnostics={}

 def cell(self,name,loc,r,mat,parent):
  bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=r);o=bpy.context.object;o.name=name;o.parent=parent;o.location=loc;o.scale.z=.55;o.data.materials.append(mat);return o
 def make_jar(self,name,parent,scale):
  m=self.m;r=empty(name,parent=parent);r.scale=(scale,)*3
  box(name+'_back',(0,.18,0),(.65,.025,.88),m['water'],r)
  for x in [-.34,.34]:box(name+'_glass_edge',(x,0,0),(.035,.4,.96),m['glass'],r)
  box(name+'_base',(0,0,-.46),(.70,.40,.04),m['glass'],r)
  box(name+'_rim',(0,.12,.46),(.71,.045,.045),m['glass'],r)
  box(name+'_rim_front',(0,-.18,.46),(.71,.025,.045),m['glass'],r)
  dots=[];starts=[];rng=random.Random(81)
  for i in range(43):
   xyz=[rng.uniform(-.27,.27),rng.uniform(-.13,.12),rng.uniform(-.35,.35)];starts.append(xyz)
   dots.append(box(name+'_particle',xyz,(.048,.043,.049),m['red'],r))
  return dict(root=r,dots=dots,starts=starts)
 def settle(self,jar,p):
  for i,(o,xyz) in enumerate(zip(jar['dots'],jar['starts'])):
   floor=-.40+(i%3)*.019;o.location=(xyz[0],xyz[1],xyz[2]*(1-p)+floor*p)
 def pose(self,shot,local):
  phase=shot['phase'];n=shot['endFrame']-shot['startFrame'];p=local/max(1,n-1);event=shot['emphasisEvent'];t=local/30
  garden=phase in ('rain','collect','unknown','payoff');lab=phase=='reveal';macro=phase in ('cells','culture')
  for obj,on in [(self.garden,garden),(self.lab,lab),(self.micro,macro),(self.compare,phase=='compare'),(self.closejar['root'],phase=='settle'),(self.closeback,phase=='settle'),(self.rig.root,garden or lab)]:visibility(obj,on)
  self.director.pose(shot['scene']['action'],p,local)
  self.rig.root.location.x=(-.72 if lab else .13);self.rig.root.location.y=.18 if lab else .02
  if phase=='collect':self.rig.root.location.x=-.35;self.rig.head.rotation_euler.z=-.20;self.rig.arms[1].rotation_euler.x=-.75;self.rig.elbows[1].rotation_euler.x=-.35
  if lab:self.rig.head.rotation_euler.z=-.20*(1-ease(p));self.rig.body.rotation_euler.x=.06*(1-ease(p))
  if phase=='unknown':self.rig.head.rotation_euler.x=-.28*ease(p);self.rig.root.rotation_euler.z=-.12
  bpy.context.view_layer.update()
  visibility(self.umbrella,garden and phase!='collect');self.umbrella.rotation_euler=(0,.05*math.sin(p*math.pi),-.04)
  if garden and phase!='collect':
   self.umbrella.location=(-.40,.10,1.94);self.director.aim_hand(0,(-.40,.08,.64))
  visibility(self.handjar['root'],phase=='collect')
  if phase=='collect':
   bpy.context.view_layer.update();self.handjar['root'].location=self.rig.elbows[1].matrix_world@Vector((.13,-.015,-.13));self.settle(self.handjar,0)
  for i,(o,v) in enumerate(zip(self.drops,self.drop_seeds)):
   x,y,seed=v;z=2.8-((seed+t*1.45)%1)*2.8;o.location=(x,y,z)
   under_canopy=(x+.40)**2+(y-.10)**2<.78**2 and z<1.94
   o.hide_render=not garden or under_canopy or phase=='unknown';o.rotation_euler.y=.06
  for i,o in enumerate(self.spots):o.hide_render=not(garden and phase!='collect') or i>4+int(p*17)
  self.settle(self.closejar,ease((p-.10)/.72));self.settle(self.labjar,1);self.settle(self.comparejar,.9)
  if macro:
   visibility(self.dish,phase=='culture');visibility(self.dish_rim,True)
   for i,o in enumerate(self.cells):o.hide_render=phase!='cells';o.scale=(1+.04*math.sin(t*2+i),1,.55)
   grow=ease((p-.08)/.46)
   for i,o in enumerate(self.colony):
    visibility(o,phase=='culture');k=max(.0001,min(1,grow*len(self.colony)-i));o.scale=(k,k,.55*k)
  if garden:self.targets={'head':self.rig.head,'focus':self.handjar['root'] if phase=='collect' else self.umbrella}
  elif lab:self.targets={'head':self.rig.head,'focus':self.labjar['root']}
  elif phase=='settle':self.targets={'focus':self.closejar['root']}
  elif macro:self.targets={'focus':self.dish_rim}
  else:self.targets={'focus':self.comparejar['root'],'bark':self.bark}
  cam=shot['cameraPlan'];aim=Vector(cam['aim']);direction=Vector(config('CAMERA_PRESETS')[cam['preset']]['direction']);self.camera.location=aim+direction;self.camera.rotation_euler=(aim-self.camera.location).to_track_quat('-Z','Y').to_euler()
  age=local-event['frame'];strength=config('EFFECT_LIBRARY')['presets'][event['preset']]['punch'];pulse=strength*max(0,1-abs(age-2)/9) if 0<=age<11 else 0
  self.camera.data.ortho_scale=cam['scale']*(1-cam['push']*ease(p))/(1+pulse)
  self.diagnostics=dict(localFrame=local,action=shot['scene']['action'],cameraScale=self.camera.data.ortho_scale,event=event['preset'] if age==0 else None,analyticDiagram=phase in ('settle','cells','culture'),footContact='boot minimum z corrected')
 def handles(self):
  def encode(v):
   if isinstance(v,bpy.types.Object):return {'object':v.name}
   if isinstance(v,dict):return {k:encode(x) for k,x in v.items()}
   if isinstance(v,(list,tuple)):return [encode(x) for x in v]
   return v
  keys=['garden','lab','micro','compare','tree','umbrella','spots','drops','drop_seeds','handjar','table','labjar','scope','closejar','closeback','dish','dish_rim','cells','colony','comparejar','bark','camera']
  r=self.rig
  return dict(objects=encode({k:getattr(self,k) for k in keys}),rig=encode(dict(root=r.root,body=r.body,head=r.head,arms=r.arms,legs=r.legs,elbows=r.elbows,moving=r.moving,faces=r.face.groups,eyes=r.face.eyes)),rest={o.name:[list(a) for a in r.rest[o.name]] for o in r.moving})
 @classmethod
 def restore(cls,data,size):
  from types import SimpleNamespace
  from design_system import FaceController
  from mathutils import Euler
  def decode(v):
   if isinstance(v,dict) and set(v)=={'object'}:return bpy.data.objects[v['object']]
   if isinstance(v,dict):return {k:decode(x) for k,x in v.items()}
   if isinstance(v,list):return [decode(x) for x in v]
   return v
  self=cls.__new__(cls);self.s=bpy.context.scene;self.s.render.resolution_x,self.s.render.resolution_y=size
  for k,v in decode(data['objects']).items():setattr(self,k,v)
  d=decode(data['rig']);face=FaceController.__new__(FaceController);face.groups=d.pop('faces');face.eyes=d.pop('eyes');self.rig=SimpleNamespace(**d,face=face)
  self.rig.rest={k:(Vector(v[0]),Euler(v[1]),Vector(v[2])) for k,v in data['rest'].items()};self.director=CharacterDirector(self.rig);self.targets={};self.diagnostics={};return self
