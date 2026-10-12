from common import *
from datetime import datetime,timezone,timedelta
p=R/'delivery.py';text=p.read_text('utf-8').replace('편집 수정은 구도·재질·자막의 3차례입니다.','편집 수정은 구도·재질·자막·대상 연결 라벨의 4차례입니다.')
text=text.replace("'손가락·시선·물체 접촉 연기는 레퍼런스 대비 단순하다.',","'손가락·시선·물체 접촉 연기는 레퍼런스 대비 단순하다.','작은 소품과 납작한 세포의 축척 때문에 월드 기준 텍셀 밀도는 완전히 같지 않다.',")
p.write_text(text,'utf-8')
q=read(R/'review/optimization_design.json');q['measuredFinalPreflight']={'projectedShotsReused':9,'uiCheckSeconds':11.915087699999276,'earlierUiCheckSeconds':48.13487990000067,'reason':'Skip CRT in layout-only preflight; use verified normalized preview projection for final resolution'};q['creativeRevisionRounds']=4;write(R/'review/optimization_design.json',q)
p=R/'review/IMPLEMENTATION.json';q=read(p);q['creativePrompts'].append('P-046');q['notImplemented'].append('perfect world-space texel density on all parent-scaled props');write(p,q)
log=ROOT/'PROMPT_LOG.md';marker='V5 실행 기록 보정 — P-044'
if marker not in log.read_text('utf-8'):
 with log.open('a',encoding='utf-8') as f:f.write('\n\n### '+marker+'\n'+datetime.now(timezone(timedelta(hours=9))).isoformat()+'\nP-044 최초 로그 작성은 Windows Python tzdata 누락으로 실패했다. 일부 보호 대상 코드 수정 뒤 렌더가 시작되어 이 부분은 사전 기록 조건을 완전히 충족하지 못했다. 이후 고정 UTC+9 시간대로 고쳐 원문을 기록하고 카메라 수정 렌더를 수행했다. 이후 P-045·P-046은 실행 전에 기록했다. 실패를 성공 기록으로 덮어쓰지 않는다.\n')
