from pathlib import Path
from datetime import datetime,timezone,timedelta
import hashlib,json
R=Path(__file__).resolve().parent;ROOT=R.parents[1];now=datetime.now(timezone(timedelta(hours=9))).isoformat();log=ROOT/'PROMPT_LOG.md'
if '## U-096 — MINSU V6 관객 우선 재설계' not in log.read_text('utf-8'):
 with log.open('a',encoding='utf-8') as f:f.write('\n\n## U-096 — MINSU V6 관객 우선 재설계\n'+now+'\n사용자 원문:\n\n'+(ROOT/'MINSU_V6_USER_SPEC.md').read_text('utf-8')+'\n\n## P-053 — V6 편집 분석·모드·연속 자막 구현\n'+now+'\n실행 전 기록. 기존 EP09 MP4 전체 디코드와 전프레임 자막 교체를 조사하고 실제 대표/경계 프레임을 검수한다. 현재 도구에는 실시간 영상 재생/청취 관찰 도구가 없어 그 수행을 주장하지 않는다. WORLD_ACTION→관찰 대상 확대의 EXPLAIN_SCENE→같은 모델/위치/시간 상태로 WORLD_RETURN을 연결하는 공통 모드와 인과 검증을 구현한다. 고정 제목·챕터·숫자·반복 출처는 삭제한다. 읽기 시간 기반 전역 자막 타임라인,4프레임 알파/정수 위치 변화,기존 구절 유지,사건 중심 임팩트를 구현한다. 기존 민수·폰트·픽셀 셰이딩·로컬 BGM/SFX를 재사용해 EP09의 사건/확대/복귀10초 품질 샘플을 먼저 만든다. 샘플 검수 뒤 기존 캐시 후보의 후킹 콘티와 독립 근거를 검토해 새 소재를 선정한다. 최종 프리뷰·문제컷 수정·렌더/오디오·기술/시청경험 판단을 분리해 제출한다. 높은 점수만으로 시청경험을 승인하지 않는다.\n')
(R/'review').mkdir(parents=True,exist_ok=True)
paths=[*(ROOT/'research/namuwiki').rglob('*'),*(ROOT/'exports').glob('MINSU_EP0*'),ROOT/'prompts/MYSTERY_100_v1.md']
out=R/'review/preservation_before.json'
if not out.exists():out.write_text(json.dumps({str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths if p.is_file()},ensure_ascii=False,indent=2),'utf-8')
print('V6 logged and source/history baseline preserved',now)
