from common import R,ROOT,read,write
p=ROOT/'PROMPT_LOG.md'
entry='''

## P-034 — V4 사전 가독성 수정
2026-10-12 (Asia/Seoul). 실행 전 기록. S04 큰 자막은 `실제론 / 더 빨라요`로 줄이고 영어는 기존 과학 의미를 유지한다. S07 큰 자막은 `추가 질량`으로 집중시키고 하단 설명 `보이지 않는 질량을 / 더하면 설명돼요`, 영어 `Adding unseen mass / can explain the motion.`을 함께 둔다. S02 인물 클로즈업 스케일을 3.8→4.3으로 넓혀 머리 잘림을 방지한다. 원문 공급·과학 주장·오디오는 변경하지 않는다. 추가 외부 LLM 호출 없음. 수정 이유: 실제 글리프 폭 검사와 프레임별 카메라 경계 검출.
'''
if '## P-034' not in p.read_text('utf-8'):
    with p.open('a',encoding='utf-8') as f:f.write(entry)
s=read(R/'ep07/episode.json');s['shots'][1]['cameraPlan']['scale']=4.3
s['shots'][3]['captionPlan'][0]['lines']=['실제론','더 빨라요']
shot=s['shots'][6];shot['captionPlan'][0].update(lines=['추가 질량'],english=['More mass'],start=36,highlight=['질량'])
shot['captionPlan']=shot['captionPlan'][:1]+[dict(role='BODY_CAPTION',lines=['보이지 않는 질량을','더하면 설명돼요'],english=['Adding unseen mass','can explain the motion.'],start=4,end=116,y=1340,highlight=['질량'])]
write(R/'ep07/episode.json',s)
