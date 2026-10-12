from pathlib import Path
from datetime import datetime,timezone,timedelta
ROOT=Path(__file__).resolve().parents[3]
with (ROOT/'PROMPT_LOG.md').open('a',encoding='utf-8') as f:
    f.write('\n\n## P-048 — 실험창의 회전 여백 수정\n'+datetime.now(timezone(timedelta(hours=9))).isoformat()+'\n실행 전 기록. 첫 기술 프리뷰 실제 MP4의 frame106에서 좌측 막대와 우측 꺾인 모형이 실험창 가장자리에 잘렸다. 동일 비교 카메라의 정사영 범위를 넓힌다. 모든 프레임의 평가된 메시 투영을 실험창과 대조하고 잘림을 실패 처리한다. 정보 계층과 실험 수치 갱신 시점은 유지한다.\n')
