from common import *
from datetime import datetime,timezone,timedelta
log=ROOT/'PROMPT_LOG.md'
if 'P-045' not in log.read_text('utf-8'):
 with log.open('a',encoding='utf-8') as f:f.write('\n\n## P-045 — 관찰을 보완하는 자막\n'+datetime.now(timezone(timedelta(hours=9))).isoformat()+'\n실행 전 기록. S02는 채집 행동을 반복 설명하지 않고 물 자체의 색인지 입자인지 구분하는 목적을 제시한다. S03은 가라앉는 움직임과 용해/부유의 차이를 연결한다. S04는 확대 관찰에서 다음 배양 실험으로 연결한다. S06 정보창에 보고서의 속명 Trentepohlia를 정확히 제시한다. 한국어 기본, 영어 별도. 기존 3D 캐시 재사용.\n')
p=R/'ep08/episode.json';spec=read(p)
for s in spec['shots']:
 c=s['captionPlan'][0]
 if s['id']=='S02':c.update(lines=['물의 색일까, 입자일까?'],english=['Colored water,','or tiny particles?'],highlight=['입자'])
 if s['id']=='S03':c.update(lines=['물에 녹은 색이 아닌','떠 있던 입자!'],english=['Suspended particles,','not dissolved color.'],highlight=['입자'])
 if s['id']=='S04':c.update(lines=['이 입자를 키워 봤더니…'],english=['Then researchers','cultured these particles...'],highlight=[])
 if s['id']=='S06':
  s['labels'][0].update(lines=['트렌테폴리아 속 조류'],english=['Trentepohlia algae'])
  s['visualAction']='실험대 옆의 민수가 고개와 몸통을 들고 팔을 벌리며 놀람에서 납득으로 반응한다'
write(p,spec)
