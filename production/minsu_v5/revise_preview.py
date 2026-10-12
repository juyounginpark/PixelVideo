from common import *
from datetime import datetime,timezone,timedelta
log=ROOT/'PROMPT_LOG.md'
if 'P-044' not in log.read_text('utf-8'):
 with log.open('a',encoding='utf-8') as f:f.write('\n\n## P-044 — V5 실제 프레임 수정\n'+datetime.now(timezone(timedelta(hours=9))).isoformat()+'\n도구: Blender/Pillow, 실행 전 기록. 첫 우산의 좌측 잘림을 카메라 중심과 거리로 수정한다. 현미경 접시를 온전히 보여주고 하단 자막과 분리한다. 비교 장면의 보호 대상은 배경 테이블이 아닌 실제 시료 두 개다. 밝은 마당·어두운 현미경·한글 영역에서 CRT 4개 프리셋을 비교한다.\n')
p=R/'ep08/episode.json';s=read(p)
for q in s['shots']:
 if q['id'] in ('S01','S09'):q['cameraPlan']['aim'][0]=-.12;q['cameraPlan']['scale']=4.8
 if q['id'] in ('S04','S05'):q['cameraPlan']['scale']=4.0;q['cameraPlan']['aim'][1]=-.16
 if q['id']=='S05':
  for c in q['captionPlan']:c['y']=1470
 if q['id']=='S07':q['protectedSubjects']=['focus','bark']
write(p,s)
