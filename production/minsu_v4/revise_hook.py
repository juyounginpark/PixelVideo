from common import R,ROOT,read,write,native_key
p=ROOT/'PROMPT_LOG.md';entry='''

## P-039 — 한·영 후킹 자막과 이동 별 가림 수정
2026-10-12 (Asia/Seoul). 실행 전 기록. 모든 프레임의 이동 별과 자막 사각형을 대조하자 S01/S04 후반 상단 영어가 별을 가리는 구간이 있었다. S01은 `예상보다 빠르다!` / `Faster than expected!`, S04는 `더 빨라요` / `Faster than predicted.` 한 줄씩으로 줄이고 y=180으로 올린다. 3D 장면과 움직임은 변경하지 않는다. 네이티브 캐시 키가 그대로임을 기록하고 UI만 갱신한다. 외부 LLM 추가 호출 없음.
'''
if '## P-039' not in p.read_text('utf-8'):
    with p.open('a',encoding='utf-8') as f:f.write(entry)
s=read(R/'ep07/episode.json');before={x['id']:native_key(x,[270,480]) for x in s['shots']}
s['shots'][0]['captionPlan'][0].update(lines=['예상보다 빠르다!'],english=['Faster than expected!'],y=180,highlight=['빠르다'])
s['shots'][3]['captionPlan'][0].update(lines=['더 빨라요'],english=['Faster than predicted.'],y=180)
after={x['id']:native_key(x,[270,480]) for x in s['shots']};assert before==after
write(R/'ep07/episode.json',s);write(R/'review/caption_only_change.json',dict(shots=['S01','S04'],nativeKeysBefore=before,nativeKeysAfter=after,nativeInvalidations=0,changes='Korean and English layout only'))
