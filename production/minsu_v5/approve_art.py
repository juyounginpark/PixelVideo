from common import *
p=R/'ep08/gates.json';g=read(p)
paths=[ROOT/'exports/MINSU_EP08_V5_ART_SAMPLE.mp4',R/'review/sample/sequence.jpg',R/'review/crt/pixel_crops.png',R/'review/model/angles.jpg',R/'review/ui_stills/grid.jpg']
g['ART_PREVIEW']=dict(decision='PROCEED_WITH_STATED_LIMITS',reviewer='assistant actual decoded-frame inspection',evidence=[dict(path=str(p.relative_to(ROOT)),sha256=sha(p)) for p in paths],observations=['0초부터 붉은 비와 흰 우산의 색 대비가 보임. 0.3~1.5초 팔·몸통·입 변화와 얼룩 증가 확인.','우산·현미경 테두리 잘림 수정. 머리카락의 검은 모서리 삼각형을 실제 프레임에서 확인 후 수정.','정면·측면·3/4 네 동작 표본에서 실루엣·팔 연결·접지를 확인. 12동작 전체 36뷰 파일 및 60포즈 진단 저장.','CRT 미적용/6%/10%/14%를 실제 인코딩 후 밝은 영역·어두운 영역·자막에서 비교. 6% 모바일 프리셋 선택.','한국어 제목·본문·정보 라벨의 계층이 구분됨. 영어판은 별도 출력.'],limits=['표본 프레임 검수이며 실시간 재생 감상이나 실제 모바일 기기 사용자 테스트가 아니다.','배양과 침강은 설명용 시간 압축이며 유체/생물학 시뮬레이션이 아니다.','표정과 몸짓은 개선했으나 상업 애니메이션 수준의 복잡한 손 연기는 아직 제한적.'])
g['ART_PREVIEW']['approvedSceneSpecHash']=sha(R/'ep08/episode.json')
write(p,g)
