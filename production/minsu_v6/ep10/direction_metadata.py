from pathlib import Path
import json
J=Path(__file__).resolve().parent;p=J/'episode.json';d=json.loads(p.read_text('utf8'))
questions=['빛만 옮겼는데 왜 색이 바뀌지?','다른 잔으로 교체한 걸까?','앞에서 비춘 빛은 어떻게 보일까?','뒤에서 통과한 빛은 왜 다르게 보일까?','같은 유리 벽 안에 무엇이 있을까?','입자가 빛을 어떤 경로로 보내는가?','처음 색 변화를 이제 어떻게 이해할까?','같은 잔을 어느 조명 조건에서 보는가?']
emotions=['놀람: 걷기→고개·몸통 반응','호기심: 기울여 관찰','관찰: 조명에 손을 뻗음','조사: 조명 이동 후 확인','캐릭터 생략: 구조만 확대','캐릭터 생략: 빛 경로만 관찰','깨달음: 같은 잔을 가리킴','확인: 조명 왕복·결과 반응']
for i,s in enumerate(d['shots']):
 s['viewerQuestion']=questions[i];s['characterEmotion']=emotions[i];s['captionPlan']={locale:[j for j,c in enumerate(d['captions'][locale]) if c['start']*30<s['endFrame'] and c['end']*30>s['startFrame']] for locale in ['ko','en']}
p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
(J/'research/object_states.json').write_text(json.dumps({'objectId':'same_cup','objectType':'explanatory_cage_cup','geometryVersion':'EP10-V6-1','operation':'MoveLight','observedProperties':['reflected appearance','transmitted appearance'],'previousValue':'green reflection','currentValue':'red transmission','displayUnits':'Qualitative color; no invented numerical measurement','claimStatus':'VERIFIED_EXPLAINED','evidenceStatus':'Primary publication verified','lampCoordinates':'Front y=-0.65; back y=0.70, scene coordinates, not physical measured units','simplification':'Scripted appearance tied to light position, not full spectral rendering; not exact historical replica'},ensure_ascii=False,indent=2),encoding='utf8')
