"""Write the delivery report only after verified movie and preservation checks."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
JOB=ROOT/'production/minsu_v3/ep05'
qa=json.loads((JOB/'review/DELIVERY_QA.json').read_text('utf-8'))
final=qa['final'];audio=json.loads((JOB/'audio/audio_qa.json').read_text('utf-8'))
temporal=json.loads((JOB/'review/TEMPORAL_QA.json').read_text('utf-8'))
assert final['fullDecodePassed'] and all(not v['changed'] for v in qa['preservation'].values())
effect_rows='\n'.join(f'| {k} | {v} |' for k,v in qa['actualEffectCounts'].items())
text=f'''# MINSU V3 제작 결과

## 완성 파일

- [EP05 — 흔들었더니 더 안 섞인다?](exports/MINSU_EP05_V3_BRAZIL_NUT.mp4)
- [6초 효과 검증 영상](exports/MINSU_V3_EFFECT_SAMPLE.mp4)
- [본편 9컷](production/minsu_v3/ep05/review/cuts.jpg)
- [레퍼런스 3·4 / 기존 V2 / 신규 V3 프레임 비교](production/minsu_v3/ep05/review/reference_comparison.jpg)
- [수정된 캐릭터 표정·측면·후면](production/minsu_v2/design_revision/character_sheet.png)

본편은 30초, 1080×1920, 30fps, H.264 / AAC다. 540×960 3D 렌더를 정수 2배 확대하고 글자/UI를 별도로 합성했다. BGM·SFX만 있으며 TTS·나레이션은 없다.

## 선정 경로와 사실 범위

기존 나무위키 미스터리 목록의 **브라질너트 효과**를 선별했다. 저장 원문의 92행과 기존 후보 문서 1번 항목을 확인하고, 기존 제작 이력과 중복을 대조했다. 새 추천기나 기본 동물 주제를 추가하지 않았다. 현재 확인된 공급 경로는 저장된 목록과 검토 지침이며, 자동 실행되는 선택기·스케줄러가 확인됐다고 주장하지 않는다.

과학 근거는 [Gajjar 외, Scientific Reports (2021)](https://doi.org/10.1038/s41598-021-87280-1)다. 이 실험에서 관찰한 일부 길쭉한 견과의 회전, 주변 작은 입자의 하강, 큰 견과의 상승을 연결했다. 모든 큰 견과가 올라오는 법칙으로 표현하지 않고 바닥에 남은 견과도 보여준다.

[선정·검증 기록](production/minsu_v3/ep05/SELECTION_AND_FACTS.md) / [공급원 영수증](production/minsu_v3/ep05/source_receipt.json)

## 실제 코드 변경

| 영역 | 구현과 변경 |
|---|---|
| 캐릭터 | 큰 머리·짧은 몸 비율, 연결된 머리카락, 10종 얼굴, 팔꿈치와 시선·상체가 함께 반응하는 연기 |
| 재질·렌더 | BOX 텍스처 경계의 흰 삼각형 수정, 카툰 조명, RGB 비율을 보존하는 명도 단계화, 픽셀 외곽선 |
| 편집 | 행동 ID·대상·사건 프레임이 있는 이벤트만 EffectDirector에서 처리; 예산·중복·유효 구간 검사 |
| 카메라 | 실제 3D 카메라의 대상 중심 확대, 범위 이탈 시 제한, 컷별 거리·높이·시점 변경 |
| UI | 최종 해상도 자막, 대상 투영 좌표를 따르는 효과, 얼굴·핵심 대상 보호, 배치 실패 시 오류 |
| 오디오 | 기존 로컬 카탈로그 재사용, 권한·분위기·파일 검사, 프레임 동기 SFX, 분리 스템·덕킹·AAC 검사 |
| 재개·검수 | Spec/렌더 코드 해시, 프레임 완료 기록, 전체 UI 사전 검사, 컷·이벤트 전후 비교 이미지 |

핵심 코드: [design_system.py](production/minsu_v2/design_system.py), [effects.py](production/minsu_v3/effects.py), [native.py](production/minsu_v3/native.py), [graphics.py](production/minsu_v3/graphics.py), [render_job.py](production/minsu_v3/render_job.py), [compose_job.py](production/minsu_v3/compose_job.py).

본편의 새 에셋과 행동은 [science_scene.py](production/minsu_v3/science_scene.py), 컷·자막·사건은 [episode.json](production/minsu_v3/ep05/episode.json)에 있다. 이전 사막·도마뱀 장면을 재사용하지 않고 실내 실험대와 견과 에셋을 만들었다.

## 본편에 사용한 효과

| 효과 | 횟수 |
|---|---:|
{effect_rows}

[효과별 시작·종료 프레임 CSV](production/minsu_v3/ep05/review/effect_frames.csv). 구간 끝은 미포함이다. 본편은 Hard Cut을 기본으로 사용한다. Dark Focus는 가림이 없는 6초 샘플에서 검증했고, 견과가 겹치는 본편에서는 사용하지 않았다. Freeze와 Wipe는 라이브러리에 있지만 이번 전달 영상에서는 사용하지 않았으므로 완성 영상 수준의 시각 검증을 받았다고 표시하지 않는다.

## 검증 결과

- 전체 영상 디코드: 통과, {final['frameCount']}프레임.
- 자막·효과 영역 검사: {final['uiFramesValidated']}프레임, 오류 0.
- 동작 순서 검사: 회전 후 상승 / 작은 땅콩 하강 / 큰 견과 상승 / 수평 복귀 / 아래 견과 잔류, 5개 통과.
- 코드 검사: V2 17개 + V3 10개 통과.
- 전체 오디오: {final['loudness']['input_i']} LUFS, {final['loudness']['input_tp']} dBTP.
- SFX {qa['audioEvents']}개, 기록된 샘플 배치 오차 최대 {qa['maxAudioSyncErrorSeconds']}초.
- BGM 루프 경계·재생 범위·피크 검사 통과. 시작 0.4초, 종료 0.8초 페이드, 중요 효과음 구간 4dB 덕킹.
- 기존 공급 자료 {qa['preservation']['sourceFiles']['checked']}개와 이전 영상 {qa['preservation']['videos']['checked']}개 해시 일치.
- 최종 MP4 연속 프레임 분석: {temporal['decodedFrames']}프레임, 축소 디코드에서 완전 동일 화면의 최장 연속 구간 {temporal['longestExactStillSeconds']}초. 컷 내부 평균 밝기 20/255 초과 급변 {len(temporal['brightnessJumpsOver20Levels'])}건. 미적 품질 합격 점수로 사용하지 않는다.

[통합 QA](production/minsu_v3/ep05/review/DELIVERY_QA.json) / [오디오 QA](production/minsu_v3/ep05/audio/audio_qa.json) / [음원 출처](production/minsu_v3/ep05/audio/CREDITS.md)

[연속 프레임 분석](production/minsu_v3/ep05/review/TEMPORAL_QA.json) / [최종 파일 시각 검수](production/minsu_v3/ep05/review/VISUAL_REVIEW.md). 최종 MP4에서 1/3초 간격과 사건 전후·컷 경계 프레임을 추출해 검토했다. 실시간 전체 재생이나 청취 검수를 수행했다고 주장하지 않는다.

정지 검수에서는 머리카락 경계의 흰 메시, 피부의 과한 색 패치, 하단 견과의 가림, 자막과 라벨의 충돌을 수정했다. 레퍼런스의 캐릭터 반응·짧은 강조·게임 정보 표현을 적용했으며, 원본의 편집 타이밍 전체를 정밀 복제했다고 주장하지 않는다.

## 제한과 후속 작업

- 입자 움직임은 논문 관찰에 근거한 기하학적 설명 애니메이션이다. DEM 물리 해석·실측 X선 데이터·질량 보존 시뮬레이션이 아니다. 영상에 내부 모식도로 표시했다.
- 새 과학 주제의 에셋·행동은 여전히 소재별 씬 구현과 검토가 필요하다. 임의 주제를 넣으면 완성 영상을 만드는 범용 자동 생성기를 완성한 것은 아니다. 미등록 소재는 대체 영상 없이 중단한다.
- 대상 마스크는 메시의 화면 투영이며 다른 오브젝트에 가린 영역까지 해결하는 깊이 마스크가 아니다.
- 얼굴 보호와 UI 경계 검사는 미적 완성도·시청 유지율을 보증하지 않는다. 원본 전체 영상과의 청취 비교, 사람의 최종 청취, 실제 인스타그램 화면 검수는 수행하지 않았다.
- 현재 소스는 프레임별 절차적 포즈를 평가한다. 별도로 베이크한 편집용 애니메이션 타임라인을 납품한 것은 아니다.

재실행 명령과 컴포넌트 설명은 [V3 README](production/minsu_v3/README.md)에 정리했다. 사용자 요청과 기획 변경은 [PROMPT_LOG.md](PROMPT_LOG.md)에 누적했다.
'''
(ROOT/'MINSU_V3_RESULT.md').write_text(text,'utf-8')
print('RESULT_REPORT_WRITTEN')
