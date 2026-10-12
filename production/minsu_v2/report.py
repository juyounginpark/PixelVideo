from pathlib import Path
import json
R=Path(__file__).resolve().parent;ROOT=R.parents[1]
qa=json.loads((R/'FINAL_QA.json').read_text('utf-8'))
audio=json.loads((R/'audio_mix_v2/audio_qa.json').read_text('utf-8'))
motion=json.loads((R/'MOTION_QA.json').read_text('utf-8'))
text=f'''# MINSU V2 / EP04 결과

2026-10-12. 실제 코드·.blend·36초 영상·BGM/SFX와 검수 자료를 생성했다. 범용 완성 시스템으로 승인하지 않은 작동 프로토타입이다.

## 바로 확인

- [V2 리메이크 + BGM/SFX](exports/MINSU_EP04_V2_BGM_SFX.mp4)
- [기존 V1 화면 유지 + BGM/SFX](exports/MINSU_EP04_THORNY_DEVIL_BGM_SFX_v1.mp4)
- [V2 무음 마스터](exports/MINSU_EP04_V2_SILENT.mp4)
- [V1/V2 주요 프레임 비교](exports/MINSU_EP04_V1_V2_COMPARE.jpg)
- [V2 시안 모음](production/minsu_v2/preview/contact.jpg)
- [동작 전후 프레임](production/minsu_v2/review/HOOK.jpg)
- [편집 가능한 Blender 원본](production/minsu_v2/MINSU_EP04_V2.blend)

## 구현한 코드

| 기능 | 파일 |
|---|---|
| 캐릭터·리그·10표정·32px 재질·사막/비늘 월드 | [art.py](production/minsu_v2/art.py) |
| 상태·동작·카메라·조명·depth/normal 외곽선 | [engine.py](production/minsu_v2/engine.py) |
| 사실 검토 게이트·소재 점수·콘티·타임라인 검사 | [content.py](production/minsu_v2/content.py) |
| 컷/행동/자막/UI/SFX 데이터 | [episode.json](production/minsu_v2/episode.json) |
| 네이티브 씬 생성·키프레임 | [build.py](production/minsu_v2/build.py) |
| 부분/재개 렌더와 캐시 | [render.py](production/minsu_v2/render.py) |
| 별도 자막·라벨·발견창·색 단계화·인코딩 | [compose.py](production/minsu_v2/compose.py) |
| 툴팁/강조/배속/대사창/퀴즈 | [ui_components.py](production/minsu_v2/ui_components.py) |
| 원곡·효과음 생성/스템/덕킹/LUFS/AAC | [audio.py](production/minsu_v2/audio.py) |
| 출력 검사·회귀 테스트 | [qa.py](production/minsu_v2/qa.py), [test_system.py](production/minsu_v2/test_system.py) |

## 실제 검사 결과

- 최종 영상: {qa['frameCount']}프레임 / {qa['metadata']['fps']}fps / {qa['metadata']['size']} / 전체 디코드 통과.
- 네이티브 프레임: 540×960, 1080개. 2배 nearest 확대 후 UI 합성.
- 자막/UI: {qa['uiFramesValidated']}프레임 좌표 검사, 얼굴 중심 겹침 경고 {len(qa['faceAnchorOverlapWarnings'])}건.
- 캐릭터: 두 개의 고정 model ID, 같은 메시 참조 유지. 표정은 고정된 메시 세트의 표시 상태로 변경.
- 동작 검사: {sum(motion['checks'].values())}/{len(motion['checks'])} 통과. 카메라를 제외한 물방울/물길/시선/턱 변화를 확인.
- BGM: 100BPM 오리지널 19.2초 루프. 편집 스템 {audio['bgmMeasurement']['input_i']} LUFS.
- 최종 AAC: {qa['loudness']['input_i']} LUFS, {qa['loudness']['input_tp']} dBTP. 목표 피크 -1dBTP 이하 통과.
- 4dB 덕킹, 0.4초 시작/0.8초 종료 페이드, 루프 경계와 BGM 전 구간 커버리지 검사.
- 기존 V1 오디오 추가본은 비디오 스트림 SHA-256 일치. 화면/자막 타이밍 그대로 유지.
- TTS/음성 없음. BGM/SFX 원본과 각각의 스템 저장, 외부 샘플 없음.

검사 원본: [FINAL_QA.json](production/minsu_v2/FINAL_QA.json), [MOTION_QA.json](production/minsu_v2/MOTION_QA.json), [오디오 QA](production/minsu_v2/audio_mix_v2/audio_qa.json), [기존 영상 무변경 검사](production/minsu_v2/AUDIO_V1_QA.json).

## 비평 반영

실제 시안을 보고 민수 좌측 잘림, 거친 체크 재질, 허공에 뜬 물길, 잘못된 라벨 끝점, 가려진 턱, 첫 컷 자막의 접촉점 가림을 수정했다. 물길을 실제 메시 표면에 맞추고 머리의 물길은 머리 관절에 연결했다. 후킹 컷만 추가로 재렌더하며 나머지 프레임의 재사용 근거를 render_manifest.json에 기록했다.

## 남은 제한

- 물길은 설명용 강조선, 미세구조는 확대 모식도다. 자연스러운 유체 렌더나 수치 유체 해석은 아니다.
- 22개 동작은 절차적 시작 프리셋이며 EP04에서 실제 사용한 인간 동작은 6개다. 범용 손·발 IK와 정교한 연기는 미완성이다.
- 추가 UI 5종은 독립 시안을 생성했다. EP04에 전부 삽입하지 않았으며 실제 인터랙티브 게임 UI가 아니다.
- 사실 검증 게이트는 출처/검토 상태 누락을 차단한다. 논문 판독·외부 리서치·임의 소재의 완전 자동 대본 생성을 구현한 것은 아니다.
- 얼굴 중심 검사는 얼굴 전체 실루엣 가림 검사가 아니다. 수치·프레임 검사와 실제 사람이 듣고 보는 평가를 구분한다.
- 인간 청취 승인, 인스타그램 앱에서의 실기기 확인, 시청 유지율/조회수 성과 측정은 미실행이다.

## 재사용 문서

- [공통 제작 지침](MINSU_V2_PRODUCTION_GUIDE.md)
- [실행/구조/제한](production/minsu_v2/README.md)
- [프롬프트 기록](PROMPT_LOG.md)
- [V2 사용자 원문](MINSU_V2_USER_SPEC.md), [오디오 사용자 원문](MINSU_BGM_SFX_USER_SPEC.md)
- [음원 메타데이터](production/minsu_v2/audio/catalog.json), [출처/크레딧](production/minsu_v2/audio/CREDITS.md)
'''
(ROOT/'MINSU_V2_RESULT.md').write_text(text,'utf-8')
print('RESULT_REPORT_WRITTEN')
