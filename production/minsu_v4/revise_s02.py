"""P-041: final QA found a relevant observation-table object outside the portrait."""
from datetime import datetime,timezone,timedelta
from common import R,ROOT,read,write,native_key,config

ep=R/'ep07/episode.json';spec=read(ep);size=config('STYLE_SPEC')['nativeSize']
before={s['id']:native_key(s,size) for s in spec['shots']}
stamp=datetime.now(timezone(timedelta(hours=9),'Asia/Seoul')).isoformat(timespec='seconds')
log=ROOT/'PROMPT_LOG.md'
entry=f'''\n\n## P-041 — 최종 MP4 관찰 컷의 관측판 구도 수정\n{stamp}. 실행 전 기록. 최종 기술 QA에서 S02의 관측판 바깥 별이 79프레임 동안 화면 밖에 있음을 확인했다. 민수의 관찰 행동과 별빛 질량 추정을 연결하는 판 전체가 보이도록 S02 카메라 중심 x를 -0.38에서 -0.08로, 직교 스케일을 4.3에서 4.6으로 조정한다. 자막·동작·과학 주장은 유지하며 이 컷만 재렌더링한다. 검사 기준을 완화하지 않는다. 추가 외부 LLM API 호출 없음.\n'''
if '## P-041 ' not in log.read_text('utf-8'):
    with log.open('a',encoding='utf-8') as f:f.write(entry)
shot=next(s for s in spec['shots'] if s['id']=='S02')
shot['cameraPlan']['aim'][0]=-.08;shot['cameraPlan']['scale']=4.6
write(ep,spec)
after={s['id']:native_key(s,size) for s in spec['shots']}
changed=[k for k in before if before[k]!=after[k]]
write(R/'review/final_s02_revision.json',dict(prompt='P-041',changedNativeKeys=changed,before=before,after=after))
assert changed==['S02'],changed
print('Only S02 native cache invalidated')
