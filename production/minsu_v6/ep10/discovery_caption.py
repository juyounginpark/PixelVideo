from pathlib import Path
from datetime import datetime,timezone,timedelta
import json
J=Path(__file__).resolve().parent;root=J.parents[2];stamp=datetime.now(timezone(timedelta(hours=9))).isoformat()
with (root/'PROMPT_LOG.md').open('a',encoding='utf8') as f:f.write('\n\n## P-056 — EP10 발견 순간 강조 보완\n'+stamp+'\n실행 전 기록. 21.5초의 반사/투과 경로 발견에 큰 노란 IMPACT_CAPTION "빛의 길이 다르다!"를 배치한다. 21.533초의 카메라·픽셀 강조·로컬 발견 SFX와 연결한다. 앞선 나노입자 산란/흡수 설명의 읽기 시간을 확보하고, 3D 프레임은 재렌더하지 않는다. 영문판 의미를 동일하게 유지한다. 픽셀 글리프 확대는 정수 배율의 짧은 등장만 사용한다.\n')
p=J/'episode.json';d=json.loads(p.read_text('utf8'))
for locale in ['ko','en']:
 for c in d['captions'][locale]:
  if c['start']==18.9:c['end']=21.5
  if c['start']==21.8:
   c.update(start=21.5,lines=['빛의 길이 다르다!' if locale=='ko' else 'Different light paths!'],role='PIXEL_IMPACT',color='yellow');c.pop('newText',None)
p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
