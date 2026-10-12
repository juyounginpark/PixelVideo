from common import ROOT,R,read,write
p=ROOT/'PROMPT_LOG.md';entry='''

## P-038 — 민수의 조작 가시성과 결말 수정
2026-10-12 (Asia/Seoul). 실행 전 기록. S08의 버튼이 머리 뒤에 가려져 보여 조작부를 테이블 전면으로 옮기고, 팔의 두 관절이 그 버튼을 향하도록 한다. '모형과 관측의 일치'는 실제 겹침이 끝나는 54프레임 이후에만 표시한다. 읽기 시간을 위해 S08을 3→4초로 늘리고 후속 컷을 이동하여 총35초로 만든다. S10은 이미 일치한 궤적을 유지하며 민수는 버튼을 반복 조작하지 않고 납득하는 몸짓으로 닫는다. 과학 샘플의 힘/궤적은 그대로다. 외부 LLM 추가 호출 없음.
'''
if '## P-038' not in p.read_text('utf-8'):
    with p.open('a',encoding='utf-8') as f:f.write(entry)
s=read(R/'ep07/episode.json')
if s['durationFrames']==1020:
    s['shots'][7]['endFrame']+=30
    for x in s['shots'][8:]:x['startFrame']+=30;x['endFrame']+=30
    s['durationFrames']+=30
x=s['shots'][7];x['captionPlan'][0]['end']=116;x['labels'][0].update(start=54,end=116,y=235)
s['shots'][9]['visualAction']='처음의 두 궤적이 일치한 상태를 유지하고 민수가 관측판을 향해 고개를 끄덕인다'
write(R/'ep07/episode.json',s)
