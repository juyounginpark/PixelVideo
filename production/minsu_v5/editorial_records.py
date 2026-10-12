from common import *
write(R/'review/ep07_cut_review.json',dict(method='Actual MP4 decoded timestamp frames and sequence contact sheets; not realtime playback or audio listening',cuts=[
 dict(time='0-3',problem='첫 화면이 예측/관측 은하 도식. 범례를 읽어야 이상함을 이해',change='흰 우산에 붉은 빗방울이 떨어지는 사건으로 시작'),
 dict(time='3-6',problem='민수가 관찰자 위치에 머물고 실험 행동이 작음',change='빗물을 직접 모으고 시료 관찰에 참여'),
 dict(time='6-13',problem='거의 같은 은하 구도가 두 컷 연속',change='채집→침강→현미경으로 관찰 크기와 정보 변화'),
 dict(time='13-20',problem='화살표·동심원 도식이 화면 대부분을 차지',change='배양 결과와 실물 시료 비교로 연결'),
 dict(time='20-24',problem='발견 자막은 커지지만 시각적 사건은 계속 도식',change='배양체 성장과 카메라·임팩트 자막·SFX 동기화'),
 dict(time='24-28',problem='작은 버튼 동작이 시청자에게 약하게 읽힘',change='몸통·고개·팔·얼굴을 함께 변화'),
 dict(time='28-35',problem='은하 반복과 언어 중복으로 정보 밀도 증가',change='처음 우산으로 돌아가 색 원인과 미확인 범위를 한국어만으로 정리')],abstractSeconds=24,durationSeconds=35,referenceComparison={
 'ref4':{'observed':[{'time':'0-2','grammar':'접근하는 손과 몸 반응이 질문보다 먼저 나타남'},{'time':'3-5','grammar':'개념이 바뀌는 순간 뇌 오브젝트로 전환'},{'time':'6-11','grammar':'실제 행동과 설명이 연결'},{'time':'13','grammar':'레이더 도식은 짧게 사용'},{'time':'15-18','grammar':'생활 장면 복귀 후 중요한 감정 순간에 방사 효과'},{'time':'24','grammar':'어두운 집중 화면으로 강약 조절'}],'art':'따뜻한 파스텔·단순한 얼굴·블록 실루엣·수평 스캔라인'},
 'ref3':{'observed':[{'time':'11.5-12.5','grammar':'개념 전환에 맞춰 작은 라벨 교체'},{'time':'37-48','grammar':'고정 무대 안 정보 오브젝트가 달라짐'}],'limit':'고정 무대의 장시간 반복은 복제하지 않음'}},reviewImages=['media/ep07_sequence.jpg','media/ref3_sequence.jpg','media/ref4_sequence.jpg']))
write(R/'research/claim_ledger.json',dict(topic='2001 Kerala red rain',claims=[
 dict(claim='조사된 붉은 빗물에 가라앉는 입자가 있었다',source='https://www.iangoddard.com/sampath2001.pdf',location='Abstract; observations',status='supported'),
 dict(claim='시험한 시료를 배양해 Trentepohlia 속 조류를 확인했다',source='https://www.iangoddard.com/sampath2001.pdf',location='Microbiological studies; Conclusions',status='supported'),
 dict(claim='주변 나무의 시료에서도 같은 종류를 확인했다',source='https://www.iangoddard.com/sampath2001.pdf',location='Further microbiological investigations; Conclusions',status='supported; genus-level comparison'),
 dict(claim='동시에 많은 포자가 공중으로 들어간 정확한 과정',source='https://www.iangoddard.com/sampath2001.pdf',location='Further studies',status='unresolved; no invented transport path'),
 dict(claim='붉은 비 세포의 DNA 분석은 별도 연구에서도 다뤄졌다',source='https://www.microbiologyresearch.org/content/journal/micro/10.1099/mic.0.062711-0',location='2013 primary paper abstract',status='independent research; not a replication of every 2001 claim; not needed onscreen')],limits=['위키는 후보 출처이며 사실 판정 근거가 아니다.','정부 보고서는 공개 보관본으로 읽었으며 현재 정부 서버 원본이 아니다.','2002 Eos 논문은 같은 조사팀으로 독립 재현이 아니다.','2015 나무껍질 DNA 연구를 2001 빗물의 직접 DNA 분석으로 사용하지 않았다.','세계 모든 붉은 비의 원인이나 정확한 종을 단정하지 않는다.']))
