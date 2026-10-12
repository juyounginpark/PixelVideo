from common import R,ROOT,read,write
entry='''

## P-035 — V4 실제 정지 프레임 미술·구도 수정
2026-10-12 (Asia/Seoul), 실행 전 기록. 첫 시안에서 작은 관측판, 화면 끝 별 잘림, 얼굴 위 라벨, 비교 궤도 위 문자 겹침을 직접 확인했다. S01은 관측 별이 예상 표시를 앞서는 확대 모형으로 시작하고 S02에서 민수의 관측 역할을 연결한다. S02는 얼굴 중심으로 카메라를 옮긴다. S03/04/09의 외곽 별을 전부 담고 S05의 중력 화살표를 넓게 보이게 한다. S06 두 궤도는 위로 이동하고 느림/빠름 라벨을 궤도 위에 배치한다. S07 헤일로는 화면 안에 들어오도록 확대 강도를 제한한다. S08의 팔을 실제 스위치 방향으로 뻗는다. 흰 화살표는 진행, 민트 화살표는 중력이라는 범례를 추가한다. 하단 영어도 함께 옮긴다. 외부 LLM 추가 호출 없음.
'''
p=ROOT/'PROMPT_LOG.md'
if '## P-035' not in p.read_text('utf-8'):
    with p.open('a',encoding='utf-8') as f:f.write(entry)
s=read(R/'ep07/episode.json')
for x in s['shots']:
    ph=x['phase']
    if ph=='hook':
        x['cameraPlan'].update(preset='MACRO',aim=[0,-.25,0],scale=4.9)
        x['visualAction']='같은 바깥 궤도 위 노란 관측 별이 점선 예상 별을 앞선다';x['characterEmotion']='다음 컷 민수의 관측으로 연결'
        x['labels'][0]['y']=1240
    if ph=='observe':x['cameraPlan'].update(aim=[-.38,0,.82],scale=4.3)
    if ph in ('expected','actual','identity'):x['cameraPlan'].update(aim=[0,-.25,0],scale=4.9)
    if ph=='gravity':
        x['cameraPlan'].update(aim=[0,-.30,0],scale=4.7)
        x['labels'].append(dict(role='MICRO_LABEL',lines=['흰색: 진행  민트: 중력'],english=['White: motion / Mint: gravity'],start=24,end=105,y=350,highlight=['중력']))
    if ph=='shortage':x['labels'][0]['y']=320;x['labels'][1]['y']=880
    if ph=='halo':x['cameraPlan']['scale']=5.9;x['labels'][0]['y']=1160
    if ph=='fit':x['labels'][0]['y']=1150
write(R/'ep07/episode.json',s)
