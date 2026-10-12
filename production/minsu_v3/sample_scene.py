"""Six-second character/editor test. No topic selection or scientific claim."""
from pathlib import Path
import sys,math
import bpy
from mathutils import Vector
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R.parent/'minsu_v2'))
from art import box,empty
from design_system import ToonMaterialLibrary,CuteCharacterFactory,PixelStylePipeline,StudioLighting,TargetedActing

def sample_spec():
    shots=[]
    for i,(start,end,lines) in enumerate([(0,60,['어?','움직인다']), (60,120,['가까이서','확인해 보자']), (120,180,['이제','찾았다!'])]):
        target='prop' if i==1 else 'minsu'
        shots.append({'id':f'test_{i}','startFrame':start,'endFrame':end,
                      'actions':[{'id':f'action_{i}','startFrame':start,'endFrame':end,'target':target,
                                  'visibleChange':['head tracks rising prop, then surprise','prop rotates while observer inspects','prop turns green and character smiles'][i]}],
                      'captions':[{'startFrame':start+2,'endFrame':end-2,'lines':lines}],'events':[]})
    shots[0]['events']=[{'id':'question','frame':15,'type':'QUESTION','target':'minsu','actionId':'action_0','intensity':1},
                        {'id':'surprise','frame':42,'type':'SURPRISE','target':'minsu','actionId':'action_0','intensity':2}]
    shots[1]['events']=[{'id':'inspect','frame':67,'type':'EXPERIMENT','target':'prop','actionId':'action_1','intensity':1,'focus':True}]
    shots[2]['events']=[{'id':'found','frame':132,'type':'DISCOVERY','target':'minsu','actionId':'action_2','intensity':2,'text':'발견!'}]
    return {'id':'MINSU_V3_EFFECT_TEST','fps':30,'durationFrames':180,'purpose':'editorial test, not a science episode',
            'rendererProfile':'MINSU_V21','shots':shots,'audioMood':'exploration','audioTrack':'curious_desert_100'}

class Scene:
    def __init__(self,spec):
        self.spec=spec;m=ToonMaterialLibrary();self.rig=CuteCharacterFactory(m).minsu();self.acting=TargetedActing(self.rig)
        self.prop=box('reaction_test_prop',(.8,0,.52),(.28,.28,.28),m['pale'],bevel=.025);self.m=m
        box('review_floor',(0,0,-.065),(200,200,.1),m['studio']);StudioLighting().configure();PixelStylePipeline().configure(bpy.context.scene)
        bpy.context.scene.eevee.taa_render_samples=24
        bpy.ops.object.camera_add();self.cam=bpy.context.object;bpy.context.scene.camera=self.cam;self.cam.data.type='ORTHO';self.cam.data.dof.use_dof=False
        self.targets={'minsu':self.rig.head,'prop':self.prop}
    def pose(self,frame):
        t=frame/30;self.prop.location=(.70,0,.52+.18*min(1,t/1.4));self.prop.rotation_euler=(0,0,max(0,t-2)*.5)
        self.prop.data.materials[0]=self.m['mint'] if frame>=132 else self.m['pale']
        if frame<42:action='Inspect';p=min(.75,t/1.4)
        elif frame<60:action='Surprise';p=(frame-42)/18
        elif frame<120:action='Inspect';p=.4+.4*(frame-60)/60
        else:action='Understand';p=min(1,(frame-120)/25)
        self.acting.apply(action,p,tuple(self.prop.location))
        self.cam.location=(1.0,-5,2.0) if frame>=60 and frame<120 else (.2,-5,1.5)
        aim=(.18,0,.80);self.cam.rotation_euler=(Vector(aim)-self.cam.location).to_track_quat('-Z','Y').to_euler();self.cam.data.ortho_scale=3.45;self.cam.data.shift_y=0
