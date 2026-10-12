from pathlib import Path
p=Path(__file__).resolve().parents[2]/'PROMPT_LOG.md'
with p.open('a',encoding='utf-8') as f:
    f.write('\n\n## P-030 — 전후 비교의 출발 위치 정정\n\n2026-10-12 (Asia/Seoul). 전후 비교 컷의 출발 윤곽을 실제 첫 프레임의 민수 위치 (-0.48, 0)에 맞춘다. 장식용으로 치우친 위치를 출발 위치처럼 표시하지 않는다. 이동선은 컷 사이 위치를 이어 설명하는 모식선이며 실측 궤적이 아니다. 나머지 콘티·과학 주장·공급원은 바꾸지 않는다. 도구: Blender/Python. 전체 렌더 해시를 갱신해 본편에 반영한다. 기존 5초 표면 발견 샘플에 나타나지 않는 인물 공간의 전후 비교 오브젝트만 수정한다.\n')
