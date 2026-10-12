from pathlib import Path
from datetime import datetime,timezone,timedelta
import json
J=Path(__file__).resolve().parent;root=J.parents[2];log=root/'PROMPT_LOG.md';stamp=datetime.now(timezone(timedelta(hours=9))).isoformat()
with log.open('a',encoding='utf8') as f:f.write('\n\n## P-055 — EP10 원인 설명 자막 보완\n'+stamp+'\n실행 전 기록. 3D와 컷 시간을 유지하고, 막연한 "상호작용"을 금·은 나노입자가 빛을 흩뜨리고 흡수하며 색마다 반사·투과가 다르다는 설명으로 구체화한다. 2020 원문 Introduction, scattering discussion, absorption discussion, Conclusion의 범위. 광학 계산·입자 구조·비율을 정확히 재현했다고 주장하지 않는다. KO/EN 의미를 맞추고 고정 역할 크기를 유지한다.\n')
p=J/'episode.json';d=json.loads(p.read_text('utf8'))
for c in d['captions']['ko']:
 if c['start']==18.9:c['lines']=['유리 속 금·은 나노입자가','빛을 흩뜨리고 흡수한다.'];c['newText']='빛을 흩뜨리고 흡수한다.'
 if c['start']==21.8:c['lines']=['색마다 반사·투과가 다르다.']
for c in d['captions']['en']:
 if c['start']==18.9:c['lines']=['Gold and silver particles','scatter / absorb light.'];c['newText']='scatter / absorb light.'
 if c['start']==21.8:c['lines']=['Different colors,','different light paths.'];c['newText']=''.join(c['lines'])
p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
q=J/'research/claim_ledger.json';ledger=json.loads(q.read_text('utf8'));ledger['claims'].append({'claim':'나노입자의 산란·흡수로 색마다 반사/투과 특성이 달라짐','evidence':'2020 primary article, scattering discussion and absorption in mixed composites, plasmonic color conclusion','limits':'도식은 분광 계산이나 고대 입자 합금 구조의 정확한 재현이 아님'});q.write_text(json.dumps(ledger,ensure_ascii=False,indent=2),encoding='utf8')
