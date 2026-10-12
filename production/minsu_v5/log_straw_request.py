from datetime import datetime, timezone, timedelta
from pathlib import Path
import json, hashlib

ROOT = Path(__file__).resolve().parents[2]
now = datetime.now(timezone(timedelta(hours=9))).isoformat()
log = ROOT / 'PROMPT_LOG.md'
text = log.read_text('utf-8')
if '## U-091 — 빨대 레퍼런스 실험 게임쇼 가이드' not in text:
    with log.open('a', encoding='utf-8') as f:
        f.write('\n\n## U-091 — 빨대 레퍼런스 실험 게임쇼 가이드\n' + now + '\n사용자 원문. 기존 V5의 충돌하는 시각 규칙보다 우선.\n\n' + (ROOT/'MINSU_STRAW_STYLE_USER_SPEC.md').read_text('utf-8'))
        f.write('\n\n## P-047 — 실험 상태와 게임쇼 UI 검증 시안\n' + now + '\n실행 전 기록. Blender/Pillow/FFmpeg. 추가 외부 LLM API 없음. 기존 주제 공급원·제작 이력·EP08 출력은 보존한다. 제공된 사용자 가이드로 별도 실험 프로필을 구현한다. 빨대 원본은 현재 파일명·조사 메타데이터에서 식별하지 못했으므로 원본 관찰을 주장하지 않는다. 공통 프레임, 고정 색 의미, 7개 텍스트 계층, 5종 숫자 UI와 오브젝트 상태를 연결한다. 실제 변형 완료 영수증과 속성 값이 일치한 뒤 수치를 갱신한다. 회전각을 사용하는 두 가지 모형으로 짧은 기술 프리뷰를 만들며 회전각은 렌더 장면의 변환값이고 현실 관측값이 아니다. 3D에 디더링·약한 고정 배경 노이즈→정수 Nearest 확대→독립 한글 UI→선택적 약한 CRT. 원본과의 일치 및 과학 에피소드의 재미를 이 기술 시안으로 승인하지 않는다. 구조 변화 연산은 실제 메시 검증 없이는 과학 검수 통과로 처리하지 않는다.\n')
folder = ROOT/'production/minsu_v5/experiment/review'
folder.mkdir(parents=True, exist_ok=True)
paths = [* (ROOT/'research/namuwiki').rglob('*'), * (ROOT/'exports').glob('MINSU_EP08*'), ROOT/'prompts/MYSTERY_100_v1.md', ROOT/'production/minsu_v5/ep08/episode.json']
snapshot = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths if p.is_file()}
out = folder/'preservation_before.json'
if not out.exists(): out.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), 'utf-8')
print(json.dumps({'logged': ['U-091','P-047'], 'preservedFiles': len(snapshot), 'time': now}, ensure_ascii=False))
