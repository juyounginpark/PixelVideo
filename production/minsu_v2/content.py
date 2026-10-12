"""Validated, evidence-gated storyboard data. Does not fabricate external research."""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parent
class TopicScorer:
    WEIGHTS={'visual':30,'hook':20,'causality':20,'acting':15,'verification':15}
    def score(self, values):
        if set(values)!=set(self.WEIGHTS):raise ValueError('All five assessed dimensions required')
        if any(not 0<=v<=1 for v in values.values()):raise ValueError('Scores must be normalized 0..1')
        score=sum(values[k]*w for k,w in self.WEIGHTS.items())
        return {'score':round(score,1),'thresholdPassed':score>=75,'humanAssessment':True}

class FactVerifier:
    def validate(self, claims):
        if not claims:raise ValueError('Missing factual evidence')
        for c in claims:
            if not c.get('evidence') or c.get('status')!='reviewed':raise ValueError('Unreviewed science: '+c.get('claim',''))
            if not c.get('visualRepresentation'):raise ValueError('No visual evidence plan')
        return True

class SceneCompiler:
    def validate(self, spec):
        FactVerifier().validate(spec['factCheck'])
        end=0;ids=set();characters={c['characterId'] for c in spec['characters']}
        for s in spec['shots']:
            if s['shotId'] in ids:raise ValueError('Duplicate shot id')
            ids.add(s['shotId'])
            if abs(s['startTime']-end)>1e-8 or s['endTime']<=s['startTime']:raise ValueError('Gap/overlap')
            if not set(s['characterIds'])<=characters:raise ValueError('Unresolved character')
            if not s['expectedVisibleChange'] or not s['actionTimeline']:raise ValueError('Static-only shot')
            for caption in s['captionTimeline']:
                if not s['startTime']<=caption['start']<caption['end']<=s['endTime']:raise ValueError('Caption outside shot')
            for e in s['audioEvents']:
                if not s['startTime']<=e['time']<s['endTime']:raise ValueError('Audio outside shot')
            end=s['endTime']
        if end!=spec['duration']:raise ValueError('Incorrect duration')
        return True

class ScriptPlanner:
    """Compile reviewed event-first scripts. No unverified automatic science writer."""
    def captions(self,start,end,lines):
        return [{'start':start+.08,'end':end-.12,'lines':lines,'highlightLine':len(lines)-1}]

class StoryboardDirector:
    # Historical, explicitly requested EP04 fixture, not a topic supplier.
    def ep04(self):
        durations=[0,1.8,4.5,8,12,17,22,27,32,36]
        lines=[['물이 왜','올라가?!'],['입은','물 밖에 있는데?'],['사막에 사는','가시도마뱀'],
               ['비늘 사이를','확대해 보면…'],['좁은 틈을 따라','물이 퍼진다'],['피부 속이 아니라','표면의 물길로'],
               ['모인 물이','입까지 도착!'],['피부가 마시는 게 아니라','입으로 보내는 거야'],['사막에서 살아남는','작은 물길']]
        purposes=['hook','reaction','observation','anatomy','mechanism','connection','payoff','discovery','ending']
        actions=['drop contact, wet front starts','Minsu gaze, lean and surprise; animal turns','four-leg walk toward free water',
                 'scale surface expands to channel model','capillary front spreads radially between external scales',
                 'external wet routes progress on whole animal','water reaches mouth, then jaw cycles',
                 'Minsu points to route then nods','animal head turns, observer settles']
        kinds=['EXTREME_CLOSE_UP','TWO_SHOT','WIDE','MACRO','MACRO','MEDIUM','CLOSE_UP','TWO_SHOT','CLOSE_UP']
        # Z-up Blender coordinates. Locations are persisted as a reviewable CameraPlan.
        cams=[((-.70,-.91,.50),(-.64,-.84,.47),(-.31,-.22,.09),48),
              ((-1.6,-4.8,2.35),(-1.55,-4.7,2.32),(-.36,.08,.74),48),
              ((-3.5,-5.4,2.9),(-3.65,-5.5,3),(-.15,0,.58),46),
              ((17.1,-4.3,4.2),(18.05,-3.1,3.2),(20,0,.1),48),
              ((18.2,-3.1,3.3),(18.35,-3.0,3.25),(20,0,.1),48),
              ((-1.30,-1.7,1.65),(-1.45,-2.0,1.85),(0,-.04,.20),48),
              ((-.71,-1.58,.68),(-.66,-1.5,.65),(0,-.50,.26),55),
              ((-1.6,-4.8,2.35),(-1.55,-4.7,2.32),(-.36,.08,.74),48),
              ((-.92,-1.8,.77),(-.88,-1.74,.75),(0,-.42,.27),50)]
        sfx=[[(.55,'water_drop',False)],[(2.18,'question_blip',True)],[],[(9.0,'soft_whoosh',False)],
             [(12.65,'water_drop',False)],[],[(23.5,'water_drop',False)],[(28.6,'discovery',True)],[]]
        shots=[]
        for i in range(9):
            a,b=durations[i:i+2];p0,p1,target,lens=cams[i]
            events=[{'time':t,'sound':name,'duck':duck,'gainDb':-4,'event':actions[i]} for t,name,duck in sfx[i]]
            shots.append({'shotId':f'SHOT_{i+1:02}','startTime':a,'endTime':b,'narrativePurpose':purposes[i],
                          'worldId':'micro' if i in (3,4) else 'desert','characterIds':['thorny'] if i not in (1,2,7) else ['minsu','thorny'],
                          'sceneObjects':['water','scales'],'cameraPlan':{'shotType':kinds[i],'startPosition':p0,'endPosition':p1,'target':target,
                          'lens':lens,'movementDuration':b-a,'easing':'smoothstep','subjectFraming':'action above subtitles','focusTarget':'scales' if i in (3,4) else 'thorny'},
                          'actionTimeline':[{'start':a,'end':b,'action':actions[i]}],'animationTimeline':[{'start':a,'end':b,'preset':purposes[i]}],
                          'captionTimeline':ScriptPlanner().captions(a,b,lines[i]),'uiEvents':[],'vfxEvents':[],
                          'audioEvents':events,'expectedVisibleChange':actions[i]})
        shots[0]['captionTimeline'][0].update({'centerX':735,'y':280,'fontSize':62,'placementPreset':'upper_right_contact_safe'})
        shots[3]['uiEvents']=[{'kind':'ObjectLabel','start':9,'end':11.8,'text':'비늘 사이 통로','anchor':'micro_anchor'}]
        shots[4]['uiEvents']=[{'kind':'ObjectLabel','start':12.2,'end':16.8,'text':'모세관 작용','anchor':'micro_anchor'}]
        shots[5]['uiEvents']=[{'kind':'ObjectLabel','start':18,'end':21.8,'text':'물의 이동','anchor':'route_anchor'}]
        shots[7]['uiEvents']=[{'kind':'AchievementPopup','start':28.6,'end':30.5,'text':'사막의 물길 발견'}]
        facts=[{'claim':'비늘 사이 외부 통로의 모세관 작용으로 물을 모은다','evidence':['https://doi.org/10.1242/jeb.148791'],
                'status':'reviewed','confidence':'high','visualRepresentation':'Water stays between scales, above skin slab','limitations':'Diagram and time compression; not a numerical fluid solver.'},
               {'claim':'수분은 피부를 통해 직접 흡수되지 않고 입으로 섭취된다','evidence':['https://doi.org/10.1242/jeb.148791'],
                'status':'reviewed','confidence':'high','visualRepresentation':'External route reaches mouth before jaw motion','limitations':'Moist sand alone did not produce drinking in the cited experiment; depict free water supply. Oral transfer details uncertain.'},
               {'claim':'물은 통로에서 여러 방향으로 퍼질 수 있다','evidence':['https://pubmed.ncbi.nlm.nih.gov/28989762/'],
                'status':'reviewed','confidence':'high','visualRepresentation':'Radial capillary front in macro and branches on back','limitations':'Not a unidirectional pump.'}]
        spec={'episodeId':'MINSU_EP04_V2','title':'사막의 물길','topic':'Thorny devil cutaneous water collection','hook':lines[0],
              'duration':36,'fps':30,'aspectRatio':'9:16','visualStyle':'cute voxel / soft pixel','narrativeMode':'BGM_SFX_NO_VOICE',
              'targetAudience':'general Korean science viewers','internalResolution':[540,960],'outputResolution':[1080,1920],
              'characters':[{'characterId':'minsu','species':'stylized human','modelAssetId':'MINSU_CUTE_V2','materialPreset':'cream_mint','facePresetSet':'ten_states','animationLibrary':'minsu_motion','defaultScale':1},
                            {'characterId':'thorny','species':'Moloch horridus','modelAssetId':'THORNY_V2','materialPreset':'desert_scales','facePresetSet':'animal','animationLibrary':'quadruped','defaultScale':1}],
              'worlds':[{'worldId':'desert','environmentPreset':'warm_desert','backgroundAssets':['rocks','dry_grass','dunes'],'lightingPreset':'soft_daylight','groundMaterial':'sand32','atmosphere':'clear'},
                        {'worldId':'micro','environmentPreset':'external_scale_section','backgroundAssets':[],'lightingPreset':'soft_daylight','groundMaterial':'skin64','atmosphere':'none'}],
              'shots':shots,'factCheck':facts,'audioEvents':[e for s in shots for e in s['audioEvents']],
              'topicAssessment':TopicScorer().score({'visual':.9,'hook':.85,'causality':.9,'acting':.85,'verification':1})}
        SceneCompiler().validate(spec)
        return spec

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description='Historical EP04 fixture only. Topic supply remains the existing NamuWiki workflow.')
    p.add_argument('--legacy-ep04',action='store_true',help='Explicitly regenerate the historical EP04 fixture')
    if not p.parse_args().legacy_ep04:
        p.error('No implicit topic. Use the existing source/selection workflow; --legacy-ep04 is historical replay only.')
    spec=StoryboardDirector().ep04();(ROOT/'episode.json').write_text(json.dumps(spec,ensure_ascii=False,indent=2),'utf-8')
    print('EPISODE_SPEC_VALID',len(spec['shots']))
