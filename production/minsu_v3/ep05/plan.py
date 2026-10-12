"""Authored episode artifact for the already selected source item, not a selector."""
import json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parent;ROOT=R.parents[2]
source=ROOT/'research/namuwiki/listing.txt';lines=source.read_text('utf-8').splitlines()
assert lines[91].strip()=='브라질너트 효과','Existing source entry changed; stop without substitution'
receipt=json.loads((R/'source_receipt.json').read_text('utf-8'))
receipt.update({'indexUrl':'https://namu.wiki/w/미스터리%20관련%20정보','selectedItem':'브라질너트 효과','duplicateCheck':'No previous produced episode for this concept found'})
assert receipt['sourceSha256']==hashlib.sha256(source.read_bytes()).hexdigest()
assert json.loads((R.parent/'sample/FINAL_QA.json').read_text('utf-8'))['fullDecodePassed']
cuts=[(0,60,'hook','nut',['밑에 있던 게','왜 위로 올라와?'],'Large nut visibly emerges through the small nuts'),
 (60,150,'reaction','minsu',['큰 것부터','가라앉을 줄 알았는데?'],'Minsu follows the top nut then leans back'),
 (150,240,'reset','nut',['처음엔 밑에 놓고','상자를 흔들었다'],'Explicit return to initial state, Minsu pushes the box'),
 (240,360,'rotate','nut',['이 실험에선 견과가','먼저 몸을 세웠다'],'Elongated nut rotates with little centroid height change'),
 (360,480,'percolate','peanut',['그 옆 틈으로','작은 땅콩이 내려가자'],'Small peanuts move down beside the upright Brazil nut'),
 (480,600,'rise','nut',['큰 견과가','위로 올라왔다'],'Small nuts descend as the large upright nut rises'),
 (600,720,'settle','nut',['올라온 견과는','다시 옆으로 누웠다'],'Large nut reorients horizontally at the surface'),
 (720,810,'condition','stuck',['다 올라오진 않아','모양·주변 틈도 중요해'],'A lower large nut remains while others have risen'),
 (810,900,'payoff','minsu',['잘 섞으려고 흔들었는데','오히려 갈라져 버렸다'],'Minsu points between top and bottom and reacts with understanding')]
shots=[]
for i,(a,b,phase,target,text,action) in enumerate(cuts):
    shots.append({'id':f'SHOT_{i+1:02}','startFrame':a,'endFrame':b,'phase':phase,
      'cameraType':['CLOSE_UP','CLOSE_UP','TWO_SHOT','MACRO','MACRO','MEDIUM','CLOSE_UP','MEDIUM','TWO_SHOT'][i],
      'actions':[{'id':phase,'startFrame':a,'endFrame':b,'target':target,'visibleChange':action}],
      'captions':[{'startFrame':a+2,'endFrame':b-2,'lines':text}],'events':[],
      'representationLabel':'내부 모식도' if i in (3,4,5,6,7) else ('처음 상태' if i==2 else None)})
events=[(0,28,'SURPRISE',2,None),(1,69,'QUESTION',1,None),(2,161,'COMPARISON',1,None),
        (3,265,'EXPERIMENT',1,None),(4,398,'EXPERIMENT',1,None),(5,519,'SURPRISE',2,None),
        (6,659,'DISCOVERY',2,'올라왔다!'),(7,724,'EXPERIMENT',1,None),(8,837,'REALIZATION',1,None)]
for i,frame,kind,intensity,text in events:
    s=shots[i];ev={'id':f'event_{i}','frame':frame,'type':kind,'actionId':s['phase'],'target':s['actions'][0]['target'],'intensity':intensity}
    if text:ev['text']=text
    if i==2:ev['data']={'label':'브라질너트','value':'효과','provenance':'Existing NamuWiki entry and Gajjar et al. 2021 DOI 10.1038/s41598-021-87280-1'}
    if i==7:ev['effectDurationFrames']=82
    s['events'].append(ev)
spec={'id':'MINSU_EP05_V3_BRAZIL_NUT','title':'흔들었더니 더 안 섞인다?','topic':'브라질너트 효과','fps':30,'durationFrames':900,
      'rendererProfile':'MINSU_V21','audioMood':'observation','audioTrack':'curious_desert_100','sourceReceipt':receipt,
      'visualization':{'kind':'granular_orientation_diagram','world':'warm_tabletop','style':'MINSU_V21','mode':'authored scientific reconstruction, not numerical particle simulation'},
      'facts':[{'claim':'일부 큰 견과의 회전→상승→표면에서 수평 회전','evidence':'https://doi.org/10.1038/s41598-021-87280-1','section':'Results, pages 2–3','status':'reviewed'},
               {'claim':'작은 땅콩의 하강과 주변 조건이 중요; 큰 견과 모두 상승하지 않음','evidence':'https://doi.org/10.1038/s41598-021-87280-1','section':'Discussion, pages 3–4','status':'reviewed'}],
      'shots':shots,'credits':'Gajjar 외 · Scientific Reports (2021)'}
(R/'episode.json').write_text(json.dumps(spec,ensure_ascii=False,indent=2),'utf-8')
(R/'source_receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),'utf-8')
print('EP05_REVIEWED_PLAN_WRITTEN')
