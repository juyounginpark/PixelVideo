# MINSU 제작 시스템 정지 검수 — U-080/081

2026-10-12. 이 단계에서는 영상을 생성하지 않았다. 이후 U-083이 샘플 및 신규 영상 제작을 다시 요청했으므로 V3 실행 결과는 별도 문서로 구분한다.

## 주제 공급 보존

현재 공급원은 사용자 확인대로 **나무위키 미스터리 관련 정보**다. 기존 `research/namuwiki/main.html`, `listing.html`, `history.html`, `TOPIC_LIST_DRAFT.md`와 `prompts/MYSTERY_100_v1.md`의 선별 기준을 보존했다. 아카라이브·디시 자료는 과거 조사 이력이다.

로컬에는 수집한 나무위키 목록과 15개 검토 초안이 있다. 목록 전체를 자동으로 순회하고 제작 이력과 대조해 다음 소재를 반환하는 실행 모듈·DB·스케줄러는 이번 조사에서 확인되지 않았다. 기존 `content.py`는 EP04를 직접 생성하는 역사적 콘티 템플릿이었다. 이를 자동 주제 공급기라고 보고하지 않는다. 새 추천기를 만들거나 목록을 교체하지 않았다.

기존 공급 파일 **261개**와 기존 MP4 **9개**의 SHA-256이 수정 전후 일치했다. [보존/테스트 검사](production/minsu_v2/design_revision/validation.json).

## 실제 수정

- **흰 삼각형:** EEVEE 5.0.1에서 박스 텍스처 투영의 `projection_blend=0`이 모서리 결함을 만들었다. 동일 카메라에서 외곽선 제거·가중 법선 제거로는 사라지지 않았고, blend 0.08로 해결됐다. 텍스처는 유지했다. 통제 이미지의 RGB 각 채널 235 이상 픽셀은 670개에서 0개로 줄었다. 일반적인 품질 점수는 아니다.
- **캐릭터:** V2.1 선택형 팩토리에 넓은 얼굴·짧은 팔다리·연속 앞머리·팔꿈치 관절·10개 표정을 추가했다. 중립과 호기심을 구분하고 피부/옷 텍스처 대비를 줄였다.
- **픽셀 렌더:** 540×960 실제 3D 렌더, nearest 텍스처, 3단계 카툰 조명, depth/normal 외곽선, 색비를 유지한 밝기 단계화 후 정확한 2배 확대. RGB 채널을 별도로 반올림할 때 생긴 뒤통수 올리브색 변질을 수정했다.
- **연기/카메라:** 대상 좌표를 향하는 시선, 준비→동작→반응, 팔꿈치 회전, 호출 순서와 무관한 포즈 평가, 투영된 피사체 바운드 기반 구도 계산을 구현했다. 이 단계에서는 시간적 자연스러움을 승인하지 않았다.
- **UI:** 얼굴·사건 영역을 피하는 라벨 위치 탐색, 자리가 없으면 실패 보고, 자막 1~2줄 제한. EP04 전용 '물길 강조'가 다른 에피소드에 자동 표시되지 않게 분리했다.
- **오디오:** 특정 곡의 묵시적 기본값을 제거했다. 분위기를 명시하고 instrumental/BPM/권리/파일/루프 가능 여부를 검사한다. 효과음은 실제 사건 설명·유효한 시간·게인·권리를 확인하고, 끝에서 잘리는 효과음에는 짧은 페이드를 적용한다. 기존 음원 파일은 재생성하지 않았다.
- **역사적 EP04:** `content.py`를 인자 없이 실행하면 EP04를 자동 생성하지 않는다. 이력 재생성에만 `--legacy-ep04`를 명시한다.

코드: [design_system.py](production/minsu_v2/design_system.py), [art.py](production/minsu_v2/art.py), [layout.py](production/minsu_v2/layout.py), [compose.py](production/minsu_v2/compose.py), [audio.py](production/minsu_v2/audio.py).

## 확인 자료

- [정면·표정·측면·뒷면 정지 시트](production/minsu_v2/design_revision/character_sheet.png)
- [레퍼런스 3·4 / 기존 V2 / V2.1 비교](production/minsu_v2/design_revision/reference_comparison.jpg)
- [텍스처 수정 전](production/minsu_v2/design_revision/legacy_raw.png) / [텍스처 유지 수정 후](production/minsu_v2/design_revision/box_blend_safe.png)
- [포즈·재질·프레이밍 검사](production/minsu_v2/design_revision/design_qa.json)

회귀 테스트 17개 통과. 기존 자막 1,080프레임 좌표 검사에서 얼굴 중심 겹침 경고 0건. 독립 비평에서 흰 모서리·뒤통수 색 변질 해결, 표정 구분·질감 정돈을 확인했다. 목·어깨 잔 노이즈와 턱 아래 강한 명암 띠는 남았다. 검사는 지정된 정지 프레임 범위이며 모든 조명·구도·동작의 최종 승인을 뜻하지 않는다.

새 모델/카메라/카툰 파스는 `design_system.py`의 선택형 컴포넌트다. 과거 EP04 `.blend`와 영상 파일에 소급 적용하지 않았다. 주제별 환경/과학 사건은 기존 공급원에서 선택된 소재에 맞춰 별도 구성해야 하며, 미등록 월드를 사막으로 자동 대체하지 않는다.
