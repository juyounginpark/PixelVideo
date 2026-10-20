# 공개 복셀 조립 코드의 로컬 실행

2026-10-20 요청 U-100. 대상: https://voxel.hanbean.dev/

**공개 클라이언트 조립 코드는 원문 그대로 확보했다. 자연어 → 모델 명령 생성 서버는 확보하지 못했으므로 전체 알고리즘의 100% 복제는 미완료다.**

U-101/102 추가: 로컬 UI와 새 `/api/generate`를 구현했다. 현재 Codex의 ChatGPT 로그인을 사용해 자연어 요청과 수정 요청을 처리한다. 원본 사이트의 서버를 복제한 것은 아니다.

## 더블클릭 실행 / ChatGPT 로그인

프로젝트 루트의 `run_voxel.cmd`를 더블클릭하면 서버를 숨김 창으로 시작하고 http://127.0.0.1:8766 을 연다. 다시 실행하면 기존 서버를 재사용한다. 종료는 `stop_voxel.cmd`다. 생성 중에는 먼저 화면에서 취소한다.

첫 실행에는 Node.js와 Codex CLI가 필요하다. 현재 PC에서는 설치와 ChatGPT 로그인 상태를 확인했다. 로그인 만료 시 터미널에서 `codex login`으로 다시 로그인한다. 외부에 공개하지 않고 127.0.0.1에만 바인딩한다.

한국어로 원하는 캐릭터를 입력하면 생성된다. 수정할 때는 **현재 캐릭터를 수정하기**를 체크한다. 기본 10종 보기·명령 편집·렌더링·저장은 로컬에서 동작하고, AI 생성은 인터넷과 Codex 사용 가능 계정이 필요하다.

로그인 토큰을 읽어 복사하거나 브라우저에 전달하지 않는다. U-105부터 공식 `codex app-server`의 stdio 프로토콜을 사용한다. 별도 임시 폴더에서 read-only/ephemeral 스레드를 만든다. U-111부터 기본 모델은 **gpt-6-astra / medium**이며 UI에서 변경할 수 있다. thread/start 응답의 모델·추론 강도를 확인하고 turn/start에도 같은 값을 전달한다. 전역 Codex 설정과 별도로 적용한다. 요청당 최대 180초, 동시 생성은 1개다.

`item/agentMessage/delta`로 받은 실제 텍스트를 줄 단위로 보내고, 브라우저가 도착 순서대로 상자를 조립한다. `use` 템플릿은 내부 부품으로 펼쳐서 48ms, 일반 명령은 90ms 간격으로 조립한다. 원본 Builder의 320ms 등장·overshoot·대칭 40ms 지연을 사용하고, 작은 픽셀 입자와 부드러운 카메라 추적을 추가했다. 추론 중에는 아직 모델 명령이 없으므로 대기 블록만 표시한다. 완료본을 먼저 만든 뒤 재생하는 방식이 아니다. 수정 중 이전 모델은 반투명하게 보이고, 실패/취소하면 이전 모델을 복원한다.

진행 상태와 경과 시간은 생성 버튼 아래에 보인다. 마지막 성공 결과는 `output/latest.json`에 저장되어 새로고침 시 복원된다. 로컬 서버의 `/api/generate`는 `Accept: application/x-ndjson`에서 status/line/done/error 이벤트를 보내며, 이 헤더가 없으면 종전의 최종 JSON 응답을 유지한다.

실제 호출 전에 기본 지침·카탈로그·요청·이전 모델을 합친 전체 입력을 프로젝트 `PROMPT_LOG.md`의 새 P 번호로 기록한다. 생성된 명령은 `output/P-번호.boxes`에 저장된다. 현재 지침은 `generation-instructions-v3.txt`이며 원본 비공개 프롬프트가 아니다. 이전 v1과 JSON 스키마는 이력으로 보존한다.

공식 근거: [Codex 인증](https://learn.chatgpt.com/docs/auth), [비대화형 실행](https://learn.chatgpt.com/docs/non-interactive-mode). 설치된 CLI 0.163.0의 도움말에서 실행 옵션도 확인했다.

실시간 프로토콜 근거: [Codex App Server](https://learn.chatgpt.com/docs/app-server). 설치된 CLI에서 JSON 스키마를 생성하여 thread/start, turn/start, agentMessage delta 필드도 대조했다. U-105 브라우저 측정 1회: 첫 명령 8.421초, 생성 완료 36.860초, 36개 명령. 요청/모델/서버 상황에 따라 달라지며 보장 시간이 아니다.

`vendor/boxes.js`, `templates.js`, `look.js`는 해당 사이트가 브라우저에 제공하는 파일의 바이트 그대로다. 버전은 취득 시점의 스냅샷이며, 사이트의 향후 변경과 연동되지 않는다. 원문·출처·SHA-256은 `../../research/hanbean_voxel/`에 보존한다. 공개 제공 사실과 오픈소스 라이선스는 별개이며, 라이선스는 확인하지 못했다.

## 실행

Node.js 22에서 검증했다. 이 폴더에서:

```powershell
npm.cmd ci --ignore-scripts --no-audit --no-fund
node generate.mjs --list
node generate.mjs --template person output/person
node generate.mjs --template cat output/cat "color=#ffcc88"
node generate.mjs --file character.boxes output/character
npm.cmd test
```

출력: `.obj`, `.mtl`, `.boxes`, `.three.json`, `.json`.
OBJ와 MTL은 같은 폴더에 둔다. 좌표는 원본과 같은 Y-up, 정면 +Z.
Three.js JSON은 `ObjectLoader`로 읽으며 원본 계층과 재질을 보존한다.
OBJ는 세계 좌표로 변환한 정적 메시다. 등장 애니메이션, 원본 후처리, 조명은 포함하지 않는다.
OBJ/MTL은 색·투명도를 전달하지만 가져오는 프로그램의 조명/색 관리에 따라 표시가 달라진다.

## 실제 확인된 방식

1. `app.js:243`에서 `POST /api/generate`에 `{prompt, prev}`를 보낸다.
2. 응답을 텍스트 스트림으로 읽어 줄별 명령으로 처리한다. 이전 결과는 `prev`로 전달된다.
3. `use`는 기본 틀을 `box` 명령으로 펼친다. 기본 틀은 poop/person/cat/dog/bear/bunny/frog/penguin/chick/hamster 10종이다.
4. `box 이름 부모 가로 세로 깊이 x y z #색 [rot rx ry rz] [mirror] [soft] [glass]`를 Three.js 계층으로 조립한다.
5. `mirror`는 x 좌표와 y/z 회전 부호를 반전한다. `soft`는 모서리 반경을 계산하는 대신 크기가 다른 상자 셋을 겹친다. 최소 두께 0.13 이하의 면은 평면색 재질로 처리한다.
6. 같은 이름을 다시 쓰면 기존 부품을 교체한다. `hide`는 해당 이름과 대칭 짝을 제거한다. 원본의 이름 처리와 동작도 수정 없이 보존한다.
7. 조립 큐는 90ms 간격이며 부품 등장 시간은 320ms다. 대칭 짝은 40ms 늦게 등장한다. `look.js`는 깊이 기반 외곽선과 번짐, 선택적 CRT 효과를 구현한다.

이것은 서로 다른 크기의 상자 조립 방식이다. 공개 코드에는 입력 이미지를 3D 볼륨으로 복원하거나 균일 격자를 채우는 모델 생성 과정이 없다.

`templates.js`와 `app.js` 주석은 Claude를 언급하지만, 실제 서버 모델 ID·시스템 프롬프트·샘플링 설정·호출 코드·필터는 미확인이다. 공개 웹 검색에서는 연결된 소스 저장소를 찾지 못했다. 서버 호출을 대리 연결하거나 추측한 프롬프트를 원본이라고 대체하지 않았다.

## 검증 범위

- 원본 스냅샷과 실행용 vendor 파일의 바이트 일치.
- 기본 틀 10종의 유한 좌표, OBJ 면 인덱스 범위, Three.js JSON 재로딩 후 경계 상자 일치(오차 1e-10 이내).
- 대칭, soft 구성, hide, 애니메이션 종료 검사.
- 잘못된 명령은 로컬 어댑터에서 명시적으로 오류 처리한다. 원본 UI는 잘못된 줄을 건너뛰므로 이 입력 오류 정책은 원본과 다르다.
- person(22개 메시), cat(29개 메시) 실제 파일 생성.

미검증: 원본 사이트와의 화면 픽셀 일치, 실제 자연어 생성 결과 동일성, 외부 프로그램에서의 재질 시각 일치. 기술 검사 통과를 미적 품질 승인으로 해석하지 않는다.

원본 서버까지 동일하게 만들려면 `/api/generate` 구현과 실제 사용한 시스템 프롬프트·모델/설정이 추가로 필요하다.


## OAuth 모델 선택 및 관절 애니메이션 (2026-10-20)

화면 상단 OAuth 모델 목록은 Codex `model/list`에서 읽는다. 모델별 지원 추론 강도만 표시하고 선택값은 이 브라우저에 저장한다. 기본값은 `gpt-6-astra / medium`이다. 전역 Codex 설정을 변경하지 않는다. 서버에서도 허용 모델·강도를 검사한 뒤 thread/start 및 turn/start에 전달하고 실제 시작 설정을 검증한다. 목록은 서버에서 5분 캐시한다.

생성은 모델 조립 → 관절 연결 확인 → 동작 준비 → 자동 재생 순서다. v3 지시문이 의미 있는 부품 이름과 마지막 `motion PRESET`을 생성한다. 기본 동작은 숨쉬기·걷기·달리기·손 흔들기·대화·춤·점프·놀람·작업·먹기·졸기다. 필요한 부품이 없는 동작은 제외한다. 화면에서 동작 전환·일시정지·기본 자세·속도·관절 표시를 조절한다.

관절은 실제 Three.js Bone 부모 계층이며 상자는 관절에 고정 연결된다. 긴 팔·다리 한 덩어리는 중간을 분할해 팔꿈치·무릎을 만든다. 기존 짧은 발 템플릿은 다리 메시가 없으므로 발목만 움직인다. 가중치 피부 변형·IK·물리 시뮬레이션이나 임의 행동의 완전 자동 합성이 아닌 기본 동작 클립이다. 원본 vendor 코드는 그대로 보존한다.

GLB + 동작 및 Three.js 저장에는 기본 자세의 관절과 동작 클립을 넣는다. OBJ는 현재 자세의 정적 메시다.

검증: npm test 24개 통과. Chrome에서 모델 목록 7개, 추론 옵션·새로고침 후 선택 유지·일시정지·390px 모바일 가로 넘침 없음 확인. Sol/low 실제 생성 P-087은 고양이/wave, 관절 10개 및 동작 11개로 완료했다. GLBExporter→GLTFLoader 왕복 11클립 확인, 브라우저 예외 없음. QA 스크린샷과 GLB는 output/rig-* 및 output/generated-wave.png. 기술 검증 및 정지 화면 검수이며 모든 동작의 미적 품질 승인은 아니다.


## V6 영상 생성 연결 및 대칭 오류 수정 (U-111/112)

`production/minsu_v6/render.py`는 기본 캐릭터 팩토리를 `video_bridge.character`로 연결한다. `assets/minsu.boxes`를 사이트의 실제 parseLine → expand → Builder로 조립하고, 동일한 로컬 관절 구성 후 메시·부모 계층·재질을 Blender로 가져온다. Y-up/+Z front를 Z-up/-Y front로 변환하고 높이 1.9로 정규화한다. 기존 CharacterDirector의 행동과 사건·카메라·자막·소재 공급 경로를 유지한다. 기본 민수는 명시적인 수작업 상자 에셋이며 AI가 생성한 결과로 표시하지 않는다.

AI로 영상 캐릭터를 새로 만들려면 공방 서버를 실행한 뒤 다음을 실행한다. 사용자 프롬프트는 실제 호출 전에 PROMPT_LOG에 기록된다. 파일 생성과 성공한 휴머노이드 관절 검사 후에만 해당 episode.json을 갱신한다.

```powershell
.venv/Scripts/python.exe production/voxel_model/prepare_video_character.py PATH/episode.json --prompt "요청할 캐릭터: 팔·아래팔·손과 다리·종아리·발을 별도 부품으로 구성"
```

이 명령 역시 공방과 같은 OAuth API와 Astra/medium 기본값을 사용한다. 결과는 episode.json의 `characterBoxes`로 고정되어 렌더 때마다 AI를 재호출하지 않는다. 직접 만든 .boxes도 이 필드에 에피소드 폴더 기준 상대 경로로 지정할 수 있다. 코드·에셋 해시는 V6 프레임 캐시 키에 포함된다. 원본 서버의 비공개 자연어 생성 알고리즘은 여전히 확보되지 않았다.

원본 Builder는 자동 대칭 자식을 twins 맵에 등록하지 않아서 손자 이후 단계의 손·발이 한쪽만 생성됐다. vendor 원문은 유지하고 `builder.mjs`에서 이 등록만 보완한다. 이 어댑터를 실시간 조립·최종 모델·Blender 내보내기가 함께 사용한다. 기존 생성 명령도 다시 적용/불러오면 고쳐진다. 본래 명령 자체에 없는 부품을 추측해 추가하는 수리는 아니다.

검증: Node 25개 테스트(다단계 대칭·교체·삭제 포함), Blender 실제 임포트와 기존 11가지 행동, V6 EP10 모든 컷의 시작 포즈 및 프레임45 렌더 통과. 브라우저 Astra/medium 기본값 및 좌우 손·발 확인. 전체 영상 재렌더 및 실제 재생·청취 평가는 이번 검사에 포함하지 않았다.

```powershell
& 'C:/Program Files/Blender Foundation/Blender 5.0/blender.exe' -b --python-exit-code 1 --python production/voxel_model/test_video_bridge.py
```
