from common import ROOT,R,read,write
p=ROOT/'PROMPT_LOG.md';entry='''

## P-040 — 전체 프리뷰 후 예상/관측 기호 일관성
2026-10-12 (Asia/Seoul). 실제 35초 프리뷰와 레퍼런스 비교 후, S03의 예상 모형도 노란 별을 써서 S01/04의 색 범례와 혼동할 수 있음을 확인했다. S03은 흰 외곽선 예상 별만 보여주고 노란 관측 별/궤적은 숨긴다. S04 범례의 '점선'은 실제 흰 외곽선 기호에 맞춰 `흰색 예상 / 노랑 관측`, `White: predicted / Yellow: observed`로 통일한다. S03 3.5초 부분 프리뷰를 먼저 다시 검수한다. 다른 장면 동작은 그대로다. 별도로 실제 Blender 5.0.1 버전을 네이티브/에셋 캐시 키와 실행 검사에 명시한다. 코드 의존성 변경은 안전을 위해 최종 네이티브 캐시를 보수적으로 무효화하며, 이전 샘플 프레임을 억지로 재사용했다고 보고하지 않는다. 추가 외부 LLM 호출 없음.
'''
if '## P-040' not in p.read_text('utf-8'):
    with p.open('a',encoding='utf-8') as f:f.write(entry)
s=read(R/'ep07/episode.json');s['shots'][3]['labels'][0].update(lines=['흰색 예상 / 노랑 관측'],english=['White: predicted / Yellow: observed'])
write(R/'ep07/episode.json',s)
