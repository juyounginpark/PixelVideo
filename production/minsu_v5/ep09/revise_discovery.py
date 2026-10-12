from pathlib import Path
from datetime import datetime,timezone,timedelta
import json
J=Path(__file__).resolve().parent;ROOT=J.parents[2];now=datetime.now(timezone(timedelta(hours=9))).isoformat()
with (ROOT/'PROMPT_LOG.md').open('a',encoding='utf-8') as f:f.write('\n\n## P-052 — EP09 발견 컷의 보호 여백·결과 가독성 수정\n'+now+'\n실행 전 기록. 전체 MP4프리뷰에서S05 카메라 확대가61~63프레임 민수의 왼쪽 보호 여백을 침범했다. S05만 네이티브 카메라 이벤트 강도를0.025로 낮춘다. UI와 오디오 이벤트는DISCOVERY를 유지하며, 발견 시 짧은 큰 픽셀디스플레이 자막(체크무늬도!/착륙이 줄었다!)과 민트 반짝임·발견SFX를 동기화한다. 결과 HUD는 착륙 시도의 판정 이후80프레임부터 유지해 읽을 시간을 확보한다. 원 연구2020체크무늬/2023대비가설 근거를 따로 보존하고 접근확인페이지를 증거로 처리하지 않는다. 3D는 해당 컷만 재작업하고 다른 컷은 캐시를 재사용한다.\n')
path=J/'episode.json';spec=json.loads(path.read_text('utf-8'));event=spec['shots'][4]['emphasisEvent'];event.update(preset='PAYOFF',uiPreset='DISCOVERY',audioPreset='DISCOVERY');ledger=json.loads((J/'research/claim_ledger.json').read_text('utf-8'));spec['science']=ledger['claims'];path.write_text(json.dumps(spec,ensure_ascii=False,indent=2),'utf-8')
gpath=J/'gates.json';gates=json.loads(gpath.read_text('utf-8'));gates['ART_PREVIEW']['observations'].append('S05保护여백 수정은 카메라 강도만 낮추고 발견 UI/SFX는 유지한다. 미술 조건은 동일하며 전체/해당 컷 재검수 예정.');gpath.write_text(json.dumps(gates,ensure_ascii=False,indent=2),'utf-8')
