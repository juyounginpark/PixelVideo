from common import *
from datetime import datetime,timezone,timedelta
log=ROOT/'PROMPT_LOG.md'
if 'P-046' not in log.read_text('utf-8'):
 with log.open('a',encoding='utf-8') as f:f.write('\n\n## P-046 — 시료 라벨의 대상 연결\n'+datetime.now(timezone(timedelta(hours=9))).isoformat()+'\n실행 전 기록. 전체 MP4 프리뷰에서 S07의 두 시료 라벨이 화면 상단에 멀리 떨어져 있어 연결이 약했다. 각 라벨을 실제 시료의 투영 좌표 바로 위에 부착한다. 카메라 이동에도 해당 시료를 따라가며, 3D는 재렌더하지 않는다.\n')
p=R/'ep08/episode.json';s=read(p);shot=s['shots'][6];base=shot['labels'][0]
shot['labels']=[{**base,'lines':['빗물 시료'],'english':['Rain sample'],'anchor':'focus'},{**base,'lines':['나무 시료'],'english':['Tree sample'],'anchor':'bark'}]
write(p,s)
