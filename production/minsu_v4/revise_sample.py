from common import R,ROOT,read,write
p=ROOT/'PROMPT_LOG.md';entry='''

## P-037 — 7초 실제 MP4 검수 후 수정
2026-10-12 (Asia/Seoul). 첫 샘플 실제 MP4의 0.267초 간격 연속 프레임에서 후반 S05의 진행 화살표가 범례에 닿는 것을 확인했다. S05 범례를 y=1130으로 옮기고 중력 화살표 등장·범례·SFX를 로컬 30프레임에 맞춘다. S06은 속도 차이를 별의 실제 이동으로 전달하므로 진행 화살표를 제거하고, 더 큰 중력 화살표가 32프레임에 SFX와 함께 드러나게 한다. 연기 시안에서도 민수 시선을 관측판으로 돌리고 두 관절 팔이 실제 버튼에 닿도록 수정했다. 과학 주장은 유지하며 샘플을 다시 만든다. 외부 LLM 추가 호출 없음.
'''
if '## P-037' not in p.read_text('utf-8'):
    with p.open('a',encoding='utf-8') as f:f.write(entry)
s=read(R/'ep07/episode.json');s['shots'][4]['labels'][1].update(y=1130,start=30)
s['shots'][1]['visualAction']='관측판 가까이 몸을 기울이고 밝은 별 부분을 손으로 가리킨다'
write(R/'ep07/episode.json',s)
