from pathlib import Path
from datetime import datetime,timezone,timedelta
import sys,shutil
J=Path(__file__).resolve().parent;sys.path.insert(0,str(J.parent))
from common import read,write,sha,ROOT
now=datetime.now(timezone(timedelta(hours=9))).isoformat()
log=ROOT/'PROMPT_LOG.md'
if '## U-094 — EP09 작업 계속' not in log.read_text('utf-8'):
 with log.open('a',encoding='utf-8') as f:f.write('\n\n## U-094 — EP09 작업 계속\n'+now+'\n사용자 원문: continue\n\n## U-095 — EP09 작업 계속 재확인\n'+now+'\n사용자 원문: continue\n진행 중이던 후킹/발견 장면과 신규 영상 제작을 이어간다.\n')
# The partial review composition was never a completed final episode.
source=ROOT/'exports/MINSU_EP09_STRIPES_KO.mp4';sample=ROOT/'exports/MINSU_EP09_ART_SAMPLE.mp4'
if source.exists() and read(J/'final/compose_ko.json')['frames']==240:shutil.copy2(source,sample)
gate=read(J/'gates.json');gate['ART_PREVIEW']={'decision':'PROCEED_WITH_STATED_LIMITS','reviewedAt':now,'approvedSceneSpecHash':sha(J/'episode.json'),'evidence':[{'path':str(sample.relative_to(ROOT)),'sha256':sha(sample)}],'observations':['실제 MP4의 첫2초 표본에서 민무늬 쪽 파리 정착과 줄무늬 쪽 파리 이탈이 구분된다.','말을3/4 방향으로 바꿔 몸통과 다리를 읽을 수 있다. 민수는 화면 왼쪽으로 이동했다.','확대 파리, 2개 픽셀 폰트, 독립 고해상도 UI, 고정 프레임과 색 역할을 확인했다.','체크무늬 발견 캡션은 이벤트 이전 질문에서 이벤트 이후 민트 결과로 바뀌도록 수정했다.'],'limits':['모델은 간결한 블록 스타일이다. 원본의 세밀한 오브젝트 미술과 동일 수준으로 선언하지 않는다.','표본 프레임을 검수했고 실제 실시간 재생이나 오디오 청취는 수행하지 않았다.','전체 콘티의 연속성과 남은 장면의 가림은 전체 프리뷰에서 검수한다.']};write(J/'gates.json',gate)
print('ART review recorded; full preview authorized')
