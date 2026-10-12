# 재사용 제작 기반

MASTER 원문: ../../RETRO_VOXEL_MASTER_SPEC.md. 운영 룰: ../../RETRO_VOXEL_PRODUCTION_GUIDE.md. 감독 템플릿: ../../prompts/RETRO_VOXEL_DIRECTOR_v2.md.

이 구현은 재사용 UI, 소재별 컷 명세, 편집 가능한 3D 타임라인과 합성기를 제공한다. 임의 주제의 생물 메시와 과학 동작을 자동으로 정확하게 생성하는 범용 모델은 아니다. 새 소재의 모델·행동은 참고자료에 맞춰 제작/검수해야 한다.

## 실행

1. 감독 템플릿으로 검증된 사실·한계와 컷 구성을 기록한다. 프롬프트는 실행 전에 PROMPT_LOG.md에 추가한다.
2. episode.json에 시리즈명, 보조문구, 질문, 30fps, 길이, 컷별 카메라/행동/두 줄 대사/태그/출처를 기록한다.
3. Blender에서 같은 생물과 캐릭터 메시를 재사용해 네이티브 30fps 장면을 frames/0001.png부터 렌더링한다. 3D는 360×496이다. 카메라 핵심 대상이 출력 y650~1280에 들어오는지 확인한다.

EP04 전체 재생성 명령은 Blender `-b --python production/ep04_thorny/build.py -- --fresh`다. 기존 프레임을 재개할 때와 연출/모델을 바꿔 전체를 다시 만들 때를 구분한다.
4. 시안: `python production/retro_voxel/render_episode.py production/ep04_thorny/episode.json --preview`
5. 전체 합성: `python production/retro_voxel/render_episode.py production/ep04_thorny/episode.json`

합성기는 프레임 누락, 문장 폭/줄 수, 출력 크기·fps·프레임 수·오디오 없음, 전체 디코드를 확인한다. 미세구조의 과학 정확성이나 행동 전달력을 자동으로 승인하지 않는다.

## 구성

- ui.py: 픽셀 헤더·도감 아이콘·질문 배너·RPG 대사창·검정 세계 태그·도감 팝인.
- render_episode.py: JSON 기반 이미지 확대/합성 및 H.264 출력/검증.
- fonts/: Galmuri 2.40.3, SIL Open Font License. 픽셀 형태를 가진 한국어 글꼴. UI는 최종 해상도로 별도 그린다.
- ../ep04_thorny/build.py: 신규 생물 에셋·환경·12컷 카메라/동작. Blender 5.0에서 실행.
- ../ep04_thorny/MINSU_THORNY_DEVIL.blend: 키프레임으로 편집 가능한 전체 타임라인.
- ../ep04_thorny/episode.json: UI와 컷 명세.

장면 전체에 동일한 고정 UI를 적용한다. 생물 핵심 행동을 UI가 가리지 않도록 카메라를 조절한다. 본편에 작업 이력·렌더링 상태·제작 툴 설명을 표시하지 않는다. ‘재현’/‘물길 강조’는 시청자가 실제 구조와 시각화를 구분하는 데 필요한 콘텐츠 표시다.
