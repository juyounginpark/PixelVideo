# MINSU — REFERENCE STRAW VIDEO STYLE GUIDE

[VIDEO IDENTITY]

레트로 픽셀 게임쇼 + 과학 실험 시뮬레이션.

레퍼런스의 핵심은 다음과 같다.

1. 지속되는 공통 UI 프레임
2. 챕터에 따라 바뀌는 실험 대상
3. 실제 행동에 따라 갱신되는 수치
4. 하나의 개념을 여러 물체에 적용하는 서사
5. 결과에 대한 게임형 성공·실패 피드백
6. 마지막에 처음 질문으로 돌아오는 구조

[VISUAL STYLE]

- 화면 비율 9:16
- 프로젝트 최종 출력 1080x1920
- 30fps
- 픽셀 외곽선
- 제한된 팔레트
- Flat / Cel Shading
- Ordered Dithering
- 오브젝트별 통일된 픽셀 텍스처
- 약한 배경 노이즈
- CRT Scanline은 선택적으로 약하게 사용

원본 영상의 정확한 셰이더 코드는 알 수 없으므로
화면 비교를 통해 파라미터를 조정한다.

[COLOR SEMANTICS]

색상에 역할을 부여한다.

YELLOW:
질문, 가설, 선택지, 중요 숫자

MINT:
확인된 실험 결과, 성공, 핵심 원리

PURPLE:
대안적 가설이나 비교할 정의

RED:
기각된 가설 또는 실험상의 실패

WHITE:
일반 설명

한 장면에서 임의로 색상의 의미를 바꾸지 않는다.

[OBJECT STATE]

모든 실험 오브젝트는 구조화된 상태를 가진다.

objectId
objectType
geometryVersion
operation
observedProperties
previousValue
currentValue
displayUnits
claimStatus
evidenceStatus

단위와 수치의 의미를 반드시 명시한다.

[EXPERIMENT TIMELINE]

1. 초기 물체를 보여준다.
2. 현재 수치를 표시한다.
3. 시청자에게 결과를 예상하게 만든다.
4. 실제 변형 또는 실험을 실행한다.
5. 변형이 끝난 후 수치를 갱신한다.
6. 예상과 결과를 비교한다.
7. 다음 실험의 질문으로 연결한다.

[NUMERIC UI]

- 챕터 진행률
- 실험 전후 상태
- 비교 결과
- 성공·실패 여부
- 필요 시 실제 관측값

이 다섯 종류를 구분한다.

실제 데이터와 연출용 숫자를 섞지 않는다.
근거 없는 숫자를 임의 생성하지 않는다.

정의에 따라 답이 달라지는 문제는
그 정의를 함께 표시한다.

[TYPOGRAPHY]

- 공통 한글 픽셀 폰트 계열
- 고정 타이틀
- 챕터 제목
- 일반 본문
- 작은 오브젝트 라벨
- 결과 수치
- 선택형 엔딩

각 계층의 크기·색상·두께·좌표를 전역 정의한다.

설명 본문과 실험 HUD의 내용을 중복하지 않는다.

[ANIMATION]

새로운 월드를 계속 생성하는 대신
기존 오브젝트의 변형과 상태 변화를 활용한다.

지원 애니메이션:
- Rotate
- Squash
- Stretch
- Bend
- Flatten
- Cut
- Pierce
- Join
- Open / Close
- Morph
- Compare
- ValueUpdate

과학적 정확성이 필요한 변형은
실제 구조 변화와 수치 변화가 일치해야 한다.

[STORY PROGRESSION]

질문
→ 경쟁하는 가설
→ 관찰
→ 실험
→ 반전 또는 원리 발견
→ 다른 물체·상황에 적용
→ 결론
→ 참여

중요한 것은 컷 수가 아니라
이해의 진전이다.

[ASSET OPTIMIZATION]

반복 오브젝트는 고정 에셋으로 관리한다.

- geometry preset
- material preset
- operation animations
- UI label position
- comparison camera preset

동일 오브젝트를 매번 새로 생성하지 않는다.
변형 애니메이션은 데이터로 재사용한다.

최종 목표:
과학적 내용을 설명하는 장면들의 모음이 아니라,
시청자가 하나의 개념을 발견하고
다음 실험으로 검증해가는
레트로 픽셀 게임형 과학 애니메이션.
