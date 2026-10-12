"""Reviewed coat experiment adapter. Flight paths are explanatory animations."""
from pathlib import Path
import sys,math,bpy
from mathutils import Vector
J=Path(__file__).resolve().parent;sys.path.insert(0,str(J.parent))
from art_v5 import Materials,setup,character,box,empty,visibility
from design_system import linear
from character_director import CharacterDirector,ease

class Scene:
 def __init__(self,size):
  self.s=setup(size);self.m=Materials();m=self.m;self.patterns={}
  for name in ['plain','white','stripe','check','faint']:
   material=m['cream'].copy();material.name='COAT_'+name
   for node in material.node_tree.nodes:
    if node.type=='TEX_IMAGE':
     im=bpy.data.images.new('coat_'+name,width=32,height=32);pixels=[]
     for y in range(32):
      for x in range(32):
       dark=(x//3)%2==0 if name in ['stripe','faint'] else (x//3+y//3)%2==0
       if name=='plain':col=(.25,.27,.30)
       elif name=='white':col=(.94,.92,.86)
       elif name=='faint':col=(.57,.58,.56) if dark else (.70,.71,.69)
       else:col=(.08,.10,.13) if dark else (.95,.94,.90)
       pixels.extend([linear(c) for c in col]+[1])
     im.colorspace_settings.name='Non-Color';im.pixels=pixels;im.pack();node.image=im;node.interpolation='Closest';node.projection_blend=0
   self.patterns[name]=material
  self.world=empty('PASTEL_PADDOCK');box('ground',(0,0,-.1),(20,20,.2),m['floor'],self.world)
  for x in [-3.3,3.3]:box('fence_post',(x,2.0,.58),(.12,.12,1.16),m['wood'],self.world)
  for z in [.35,.8]:box('fence_rail',(0,2.0,z),(7,.08,.10),m['cream'],self.world)
  for x,y in [(-2.7,1.1),(2.7,1.2)]:
   box('plant_pot',(x,y,.2),(.45,.45,.4),m['roof'],self.world)
   for off in [-.13,0,.13]:box('block_leaf',(x+off,y,.65+abs(off)),(.16,.16,.6),m['leaf'],self.world)
  self.horses=[self.horse('left',(-1.1,.2,0)),self.horse('right',(1.1,.2,0))]
  self.rig=character(m);self.director=CharacterDirector(self.rig);self.rig.root.location=(-2.7,-.55,0);self.rig.root.scale=(.70,)*3
  self.cloth=box('changeable_coat',(.2,-.1,2.4),(.84,1.48,.04),self.patterns['stripe'])
  self.step=box('experiment_step',(-.85,-.5,.175),(1.05,.70,.35),m['wood'],self.world)
  self.fly=[self.make_fly('FLY_LEFT'),self.make_fly('FLY_RIGHT'),self.make_fly('FLY_EXCEPTION')]
  self.macro=empty('MACRO_WORLD');self.panels=[]
  for x in [-1.1,1.1]:self.panels.append(box('coat_surface',(x,0,1),(.95,.10,1.25),self.patterns['plain'],self.macro))
  box('macro_backdrop',(0,1,1.2),(10,.1,8),m['micro_bg'],self.macro)
  self.divisions=[box('patch_divider',(.70+i*.10,-.061,1),(.045,.012,1.25),self.patterns['white'],self.macro) for i in range(8)]
  bpy.ops.object.camera_add();self.camera=bpy.context.object;self.camera.name='EP09_CAMERA';self.camera.data.type='ORTHO';self.s.camera=self.camera

 def horse(self,name,loc):
  m=self.m;root=empty('HORSE_'+name,loc);body=box(name+'_coat',(0,.1,1.02),(.72,1.32,.68),self.patterns['plain'],root,.015)
  neck=box(name+'_neck',(0,-.53,1.35),(.40,.37,.85),m['wood'],root,.01);neck.rotation_euler.x=-.18
  head=empty(name+'_head',(0,-.84,1.72),root);box(name+'_skull',(0,0,0),(.48,.45,.40),m['wood'],head,.015)
  box(name+'_muzzle',(0,-.28,-.11),(.48,.34,.25),m['roof'],head,.012)
  for x in [-.22,.22]:
   box(name+'_eye_white',(x,-.15,.06),(.032,.12,.12),m['cream'],head)
   box(name+'_eye',(x*1.015,-.19,.06),(.033,.055,.073),m['navy'],head)
   box(name+'_ear',(x*.75,.07,.29),(.10,.13,.28),m['wood'],head)
  for x in [-.23,.23]:
   for y in [-.37,.57]:
    box(name+'_leg',(x,y,.39),(.13,.16,.76),m['wood'],root)
    box(name+'_hoof',(x,y,.08),(.18,.23,.16),m['navy'],root)
  for z in [1.25,1.4,1.55]:box(name+'_mane',(0,-.30,z),(.11,.22,.18),m['hair'],root)
  tail=box(name+'_tail',(0,.84,.93),(.08,.09,.62),m['hair'],root);tail.rotation_euler.x=.3
  return {'root':root,'body':body,'head':head,'tail':tail,'restHead':list(head.rotation_euler)}

 def make_fly(self,name):
  m=self.m;r=empty(name);r.scale=(.95,)*3
  box(name+'_abdomen',(0,.08,0),(.19,.28,.14),m['navy'],r,.005);box(name+'_thorax',(0,-.1,0),(.18,.17,.17),m['metal'],r)
  box(name+'_head',(0,-.22,0),(.19,.12,.14),m['navy'],r)
  for x in [-.11,.11]:box(name+'_eye',(x,-.24,.02),(.07,.08,.10),m['red'],r)
  wings=[]
  for side in [-1,1]:
   wing=box(name+'_wing',(side*.18,.02,.08),(.30,.20,.015),m['water'],r);wing.rotation_euler.z=side*.35;wings.append(wing)
   for y in [-.1,.03,.13]:
    leg=box(name+'_leg',(side*.115,y,-.1),(.025,.025,.18),m['navy'],r);leg.rotation_euler.y=side*.55
  return {'root':r,'wings':wings}

 def pose(self,shot,f):
  phase=shot['phase'];p=f/119;macro=phase in ['macro','patch'];visibility(self.world,not macro);visibility(self.macro,macro)
  visibility(self.rig.root,not macro);self.director.pose(shot['scene']['action'],p,f);self.rig.root.scale=(.75,)*3;self.rig.root.location.x=-2.25;self.rig.root.location.y=-.3;self.rig.root.rotation_euler.z=-.1
  for i,h in enumerate(self.horses):
   visibility(h['root'],not macro);h['root'].location=((-1.1 if i==0 else 1.1),.2,0);h['root'].rotation_euler=(0,0,-.55)
   h['body'].data.materials[0]=self.patterns[shot['scene']['left' if i==0 else 'right']]
   h['tail'].rotation_euler.x=.3+.20*math.sin(p*math.tau*2+i);h['head'].rotation_euler.x=.03*math.sin(p*math.tau)
  visibility(self.cloth,phase=='coat');visibility(self.step,phase=='coat')
  if phase=='coat':
   visibility(self.horses[0]['root'],False);h=self.horses[1];h['root'].location=(.3,.15,0)
   t=ease((f-22)/55);self.cloth.location=(.3,.25,1.39);self.cloth.scale=(1,1,1);self.cloth.rotation_euler.x=.5*(1-t)
   h['body'].data.materials[0]=self.patterns['stripe' if t>=1 else 'plain']
   self.rig.root.scale=(1.2,)*3;self.rig.root.location=(-.85,-.5,.35);bpy.context.view_layer.update();grip=self.cloth.matrix_world@Vector((-.42,-.74,0));self.director.aim_hand(1,grip)
   visibility(self.cloth,t<1)
  for i,panel in enumerate(self.panels):panel.data.materials[0]=self.patterns[shot['scene']['left' if i==0 else 'right']]
  for i,d in enumerate(self.divisions):d.hide_render=phase!='patch' or f<20+i*7
  if phase=='patch':self.panels[1].data.materials[0]=self.patterns['plain']
  for i,fly in enumerate(self.fly):
   r=fly['root'];visibility(r,i<2 or phase=='ending');u=ease((f-2-i*3)/26) if phase=='hook' else ease((f-12-i*5)/52);land=(i==0 and phase!='ending') or phase=='ending' and i==2
   if phase=='contrast':land=i==0
   if phase=='coat' or phase=='patch':visibility(r,False);continue
   x=(-1.1 if i==0 else 1.1);z=(1.45 if not macro else 1.4);y=(-.05 if not macro else -.27)
   start=Vector((x+.75,-1.2,z+.68));end=Vector((x,y,z));r.location=start.lerp(end,u)
   if not land and u>=.80:
    bounce=ease((f-28-i*3)/20) if phase=='hook' else ease((f-62-i*5)/35);r.location=end+Vector((.85*bounce,-.65*bounce,.65*bounce))
   if land and u>=1:r.location=end
   for j,w in enumerate(fly['wings']):w.rotation_euler.y=0 if land and u>=1 else (-1 if j==0 else 1)*.35*math.sin(f*2)
  if phase=='ending':
   self.fly[2]['root'].location=(1.1,-.03,1.45) if f>70 else Vector((1.8,-1.3,2.0)).lerp(Vector((1.1,-.03,1.45)),ease((f-15)/55))
  aim=Vector((0,0,1.25 if not macro else 1.05));direction=Vector((0,-8,5.2))
  if phase=='coat':aim=Vector((-.15,0,1.25));scale=6.6
  elif macro:direction=Vector((0,-8,1.8));scale=8.6
  else:scale=11.4
  strength=.08 if shot['emphasisEvent']['preset']=='DISCOVERY' else .025 if shot['emphasisEvent']['preset'] in ['HOOK','PAYOFF'] else 0
  pulse=max(0,1-abs(f-shot['emphasisEvent']['frame'])/12)*strength
  self.camera.location=aim+direction;self.camera.rotation_euler=(aim-self.camera.location).to_track_quat('-Z','Y').to_euler();self.camera.data.ortho_scale=scale*(1-pulse)
  bpy.context.view_layer.update()
  return {'left':self.panels[0] if macro else self.horses[0]['root'],'right':self.panels[1] if macro else self.horses[1]['root']}
