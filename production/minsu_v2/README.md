# MINSU V2 — 실행과 실제 구현 범위

U-081/083 이후 주제 공급은 나무위키 미스터리 목록/기존 선별 기준을 따른다. 아래 EP04 명령은 역사적 영상 재현용이며 신규 주제 공급기가 아니다. V2.1 정지 변경: [MINSU_DESIGN_REVISION.md](../../MINSU_DESIGN_REVISION.md). V3 편집 시스템은 `../minsu_v3/`에서 이 컴포넌트를 재사용한다.

기존 Blender 5.0.1 / Python / Pillow / FFmpeg를 유지한다. 별도 Unity·Three.js·TTS 설치는 없다.

검증 환경: Python 3.13.7, Blender 5.0.1. 외부 Python 패키지는 `requirements.txt`의 실제 설치 버전으로 기록했다. Blender 스크립트는 Blender 내장 Python에서 실행한다.

## 오디오 추가 — 기존 영상 유지

```powershell
python production/minsu_v2/audio.py --video exports/MINSU_EP04_THORNY_DEVIL_SILENT_v1.mp4 --spec production/minsu_v2/audio_ep04_v1.json --output exports/MINSU_EP04_THORNY_DEVIL_BGM_SFX_v1.mp4 --mood exploration --track curious_desert_100
python production/minsu_v2/qa.py --audio-only
```

- `audio.py`: 원곡/효과음 합성, 사용 허용 메타데이터 확인, 음악 선택, 스템, 덕킹, 2단계 loudnorm, AAC 합성.
- `audio/catalog.json`: mood / bpm / duration / loopable / license / source / 허용 여부. 같은 track ID는 동일한 곡을 선택한다.
- `audio/bgm/curious_desert_100.wav`: 100BPM, 8마디, 19.2초 오리지널 루프.
- `audio/sfx/`: 9개 원본 합성 효과음. 에피소드에서 필요한 것만 사용한다.
- `audio/score.json`: 멜로디 음표와 박자. 기존 곡·외부 샘플을 입력으로 사용하지 않았다.
- `audio/CREDITS.md`: 제작 방식/출처 기록. 외부 저작물에 대한 허가를 주장하지 않는다.
- 각 믹스 폴더의 `used_audio.json`/`CREDITS.md`: 실제 사용한 에셋의 해시와 크레딧. 사용자 추가 카탈로그 항목은 원곡 생성 시 덮어쓰지 않는다.
- `audio_mix/`: 기존 V1의 BGM/SFX/mix WAV와 오디오 검수. 최종 MP4에는 스테레오 믹스를 AAC로 넣는다.
- `audio_mix_v2/`: V2 시간축의 별도 스템과 오디오 검수.
- 인코딩은 `-c:v copy`; 기존 자막과 컷 길이를 재조정하지 않는다.
- BGM 0.4초 페이드인·0.8초 페이드아웃. 중요 이벤트 4dB 덕킹. 최종 true peak -1dBTP 이하 검사.
- TTS/음성 없음. 청취 승인을 자동 수치 검사로 대체하지 않는다.

## V2 에피소드

```powershell
python production/minsu_v2/content.py --legacy-ep04
& 'C:\Program Files\Blender Foundation\Blender 5.0\blender.exe' -b --python production/minsu_v2/build.py -- --preview
python production/minsu_v2/compose.py --preview
# 시안/행동 검수 뒤 전체 렌더
& 'C:\Program Files\Blender Foundation\Blender 5.0\blender.exe' -b --python production/minsu_v2/render.py
python production/minsu_v2/compose.py
python production/minsu_v2/deliver.py
python production/minsu_v2/qa.py
python production/minsu_v2/test_system.py
```

`render.py -- --shot SHOT_05 --force` 또는 `-- --frames 365,390,465`로 부분 렌더한다. 캐시는 .blend 해시가 일치할 때만 재사용한다. 씬 전체 파일 해시가 바뀌면 보수적으로 캐시를 무효화하며, 컷 의존성 기반 최소 무효화까지 구현한 것은 아니다.

## 모듈과 제한

| 역할 | 구현 | 확인 범위/제한 |
|---|---|---|
| CharacterFactory / Rig / Faces | art.py | 같은 메시, 10개 표정, 연속 헤어캡, 단순 부모 리그 |
| State / Animation | engine.py | 22개 절차적 동작 시작점. EP04에서 6개 인간 동작 사용. 범용 IK/손 접촉 해결은 미구현 |
| Material / World | art.py | 32px nearest 텍스처, 사막·외부 비늘 확대, 무광 재질 |
| PixelRender / Outline | engine.py + compose.py | 540×960, depth/normal 경계, 약한 색 단계화, 2배 nearest, UI 별도 |
| CameraDirector | engine.py + episode.json | 컷별 거리/시작끝/대상/렌즈/easing. 범용 자동 프레이밍 최적화는 미구현 |
| Subtitle / Label / Achievement | compose.py | EP04에서 사용한 3종 컴포넌트 |
| Tooltip / Impact / TimeLapse / Dialogue / Quiz | ui_components.py | 독립 시안 5종 생성·좌표 검사. 타이핑·정답 노출·팝인·시간배율 검증 지원. EP04 본편 미사용, 실제 상호작용 기능 아님 |
| TopicScorer | content.py | 사람의 항목 평가값 계산. 웹 전체 자동 소재 발굴 아님 |
| FactVerifier | content.py | 검토 상태·출처·시각화 계획 누락 차단. 논문 내용을 자동 판독해 진실을 판정하지 않음 |
| Storyboard / SceneCompiler | content.py | 검토된 EP04 템플릿과 구조 검증. 임의 소재의 완전 자동 대본 생성 아님 |
| AudioSynchronizer | audio.py | 별도 스템, 이벤트 시점, 덕킹/음량/AAC. TTS 보류 |
| QA | qa.py / test_system.py | 데이터 오류, 글리프, 실제 출력, 앵커 가림 경고, 음량, 스트림 무변경 검사 |

캐릭터와 생물의 상대 크기는 장면 판독을 위한 양식화다. 물길은 표면에 맞춘 강조선, 미세구조는 모식도, 속도는 설명을 위한 압축이다. 모세관 유체 역학 수치 해석이나 정확한 해부학 모델로 표시하지 않는다.

민수 정면·측면·3/4·뒷면 검토 이미지는 `character_review/`에 있다. `character_review.py`는 에피소드 파일을 변경하지 않고 별도 시안을 렌더한다.

기본 방향은 사용자 V2를 적용한 **작동하는 프로토타입**이다. 모든 주제/생물/동작을 자동으로 제작하는 최종 시스템으로 승인하지 않는다. 자동 QA의 픽셀 차이·프레임 수로 재미와 자연스러운 연기를 증명할 수 없다.

## 출처와 폰트

- 생물의 외부 물 수집과 음수 조건: https://doi.org/10.1242/jeb.148791
- 방사형 물 이동: https://pubmed.ncbi.nlm.nih.gov/28989762/
- Nanum Gothic ExtraBold: Google Fonts 배포, `fonts/OFL.txt`, SIL OFL 1.1. 실제 대본 한글 글리프 검사.
- Galmuri: 기존 프로젝트의 `production/retro_voxel/fonts/OFL.md` 동봉본.
- 레퍼런스 원본 1~4: `references/`; 직접 추출한 검토 프레임 `research/reels_v2/`. 화면 문법을 참고하고 원본 영상/캐릭터/음악을 최종물에 합성하지 않았다.
