from pathlib import Path
from datetime import datetime,timezone,timedelta
import hashlib,json
ROOT=Path(__file__).resolve().parents[2];R=ROOT/'production/minsu_v5';job=R/'ep09';job.mkdir(exist_ok=True)
now=datetime.now(timezone(timedelta(hours=9))).isoformat()
log=ROOT/'PROMPT_LOG.md'
if '## U-093 — 신규 소재 한 편 제작' not in log.read_text('utf-8'):
    with log.open('a',encoding='utf-8') as f:
        f.write('\n\n## U-093 — 신규 소재 한 편 제작\n'+now+'\n사용자 원문: 새로운거로 하나 만들어줄래\n\n## P-049 — EP09 소재 선정과 실험 게임쇼 제작\n'+now+'\n실행 전 기록. 기존 나무위키 미스터리 분류 캐시의 후보 배치를 갱신하고 이전 에피소드와 중복을 제외한다. 독립 1차 연구로 사실을 확인하고, 80점 이상이며 첫 화면의 행동을 만들 수 있는 소재 한 개를 선정한다. 최신 빨대 가이드의 공통 프레임·챕터·숫자 정의·변형 후 결과 갱신·다른 대상 적용·처음 질문 회귀를 사용한다. 민수는 관찰·실험·발견을 전신으로 연기한다. 실제 연구의 조건과 결론, 미확인 기제는 구분한다. 설명용 파리/동물 움직임은 모식도로 표시하고 제작된 애니메이션 횟수를 실제 착륙률로 세지 않는다. 한글 기본/영어 별도 출력, TTS 없음, 기존 로컬 BGM/SFX. 품질 샘플과 전체 프리뷰 검수 후 최종 렌더·오디오·분리 QA를 수행한다. 추가 외부 LLM API 없이 구조화된 콘티·에셋·씬별 캐시를 사용한다.\n')
paths=[*(ROOT/'research/namuwiki').rglob('*'),*(ROOT/'exports').glob('MINSU_EP0*'),ROOT/'prompts/MYSTERY_100_v1.md']
out=job/'preservation_before.json'
if not out.exists():out.write_text(json.dumps({str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths if p.is_file()},ensure_ascii=False,indent=2),'utf-8')
print(now)
