from common import ROOT,R,read,write
p=ROOT/'PROMPT_LOG.md';entry='''

## P-036 — V4 모식도 식별성과 범례 수정
2026-10-12 (Asia/Seoul). 실제 시안에서 겹친 큐브 별이 원반처럼 보이고 비교 별 위로 영문 범례가 지나갔다. 별은 단일 오각별 실루엣으로 교체, 예상 표시도 같은 외곽선으로 맞춘다. 추론 헤일로의 과도한 자오선은 두 개로 줄인다. S01 범례는 `흰색 예상 / 노랑 관측` / `White: predicted / Yellow: observed`로 구분하고 y=1400에 배치한다. S06 범례는 위 180, 아래 780으로 옮겨 움직이는 별을 가리지 않는다. S07 발견 프레임에 헤일로가 완전히 드러나도록 맞춘다. 이는 실측 모양/색이 아니라 설명 기호다. 실행 전 기록, 외부 LLM 호출 없음.
'''
if '## P-036' not in p.read_text('utf-8'):
    with p.open('a',encoding='utf-8') as f:f.write(entry)
s=read(R/'ep07/episode.json');s['shots'][0]['labels'][0].update(lines=['흰색 예상 / 노랑 관측'],english=['White: predicted / Yellow: observed'],y=1400)
s['shots'][5]['labels'][0]['y']=180;s['shots'][5]['labels'][1]['y']=780
write(R/'ep07/episode.json',s)
