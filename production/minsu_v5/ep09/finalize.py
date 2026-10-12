from pathlib import Path
from datetime import datetime,timezone,timedelta
import sys
J=Path(__file__).resolve().parent;sys.path.insert(0,str(J.parent))
from common import read,write,sha,ROOT
now=datetime.now(timezone(timedelta(hours=9))).isoformat();qa=read(J/'review/final/technical_qa.json');assert qa['technical']=='PASS'
gates=read(J/'gates.json');evidence=read(J/'review/final/evidence.json')
gates['FINAL_QA']={'decision':'PROCEED_WITH_STATED_LIMITS','technical':'PASS','editorial':'REVIEWED_WITH_LIMITS','reviewedAt':now,'evidence':qa['outputs'],'editorialObservations':['한국어 최종36초 MP4의0.5초 간격 및 첫2초 조밀 표본 프레임을 검사했다.','한국어 결론은 시각 원리는 연구 중으로 줄여 기본 글자 크기를 유지한다. 영어 발견 장면과 연구 조건 문장도 실제 완성 프레임에서 확인했다.','발견 장면은 질문→큰민트 임팩트캡션/반짝임/발견SFX로 구분한다. 카메라 확대 여백 문제는 해당 컷 재렌더 후 해결됐다.','끝에는 체크 덮개에 착륙하는 예외 모형을 넣어 완전 차단의 과장을 피한다.','빨대 원본의 동작→결과 UI와 ref4의 캐릭터 리액션 대표 프레임을 나란히 비교했다.','완성 영상의 기술 정상 동작과 시청 재미·레퍼런스 수준의 미술 완성도를 같은 판정으로 처리하지 않는다.'],'limits':gates['EDITING_PREVIEW']['limits']};gates['EDITING_PREVIEW']['observations'][-1]='최종한국어 결론을 기본 글자 크기로 확인했다. 영어 발견/연구조건의 가독성과 충돌 없는 화면도 확인했다.';write(J/'gates.json',gates)
write(J/'review/final/editorial.json',{'reviewedAt':now,'decision':'REVIEWED_WITH_LIMITS','actualFinalMP4':evidence,'observations':gates['FINAL_QA']['editorialObservations'],'remainingLimits':gates['FINAL_QA']['limits'],'technicalQA':'PASS','humanRealtimePlayback':False,'humanAudioListening':False,'audienceTests':False})
print('Final technical/editorial evidence recorded')
