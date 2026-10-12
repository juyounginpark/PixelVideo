from pathlib import Path
from datetime import datetime,timezone,timedelta
import json
J=Path(__file__).resolve().parent;ROOT=J.parents[2]
with (ROOT/'PROMPT_LOG.md').open('a',encoding='utf-8') as f:f.write('\n\n## P-051 — EP09 후킹·동물 구도 검수 수정\n'+datetime.now(timezone(timedelta(hours=9))).isoformat()+'\n실행 전 기록. 실제 첫 정지 프레임에서 파리가 너무 작고 민수 위치가 리셋되어 중앙을 가렸다. 민수의 XY 위치를 전신 포즈 리셋 뒤 적용한다. 말의 3/4 방향으로 몸통과 다리를 드러내고, 파리를 모식도 확대 크기로 보이게 한다. 첫 컷은 2초 안에 착륙/실패가 완료되도록 시간을 조정한다. 모든 결과 표시는 변형/비행이 끝난 뒤 나타낸다. 뒤 울타리 기둥이 말 머리와 겹쳐 뿔처럼 보이는 구도도 피한다. 영어 결론은 작은 글씨로 줄이지 않도록 짧게 다듬는다.\n')
p=J/'episode.json';spec=json.loads(p.read_text('utf-8'));spec['shots'][-1]['captionPlan']['en']=['Why it works is still studied.','Not a perfect shield.'];p.write_text(json.dumps(spec,ensure_ascii=False,indent=2),'utf-8')
