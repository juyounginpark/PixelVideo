# MINSU V3.1 — 사건·편집·미술 검수

기존 Blender/Pillow/FFmpeg, V2 캐릭터·로컬 오디오, V3 EffectDirector·실제 카메라 제어를 확장한다. 다른 제작 도구나 주제 추천기를 도입하지 않았다. 이 폴더의 EP06은 기존 나무위키 목록의 `얼음이 미끄러운 이유`를 명시적으로 제작하는 어댑터다. 다른 소재는 기존 공급 절차로 검토한 뒤 별도 사건 콘티·과학 시각화가 필요하며, 공급 실패 시 이 주제로 대체하지 않는다.

## 변경

| 모듈 | 역할 |
|---|---|
| `editorial.py` | 컷마다 9개 사건 필드, 시간 범위, 자막 역할, 강조 단어, 출처 필수값을 검증. 같은 정보/모드 반복은 검토 경고이며 합격 점수로 환산하지 않음 |
| `typography.py` | 6개 자막 계층의 서체·크기·색·등장 움직임, 문장 의미에 따른 선택 강조, 독립된 1080 UI |
| `style.py` | 3단계 명암, 일정한 재질 texel 밀도, 실제 저해상도 윤곽, 민수의 목도리·스케이트와 미술 팔레트 |
| `ice_scene.py` | 전신 연기와 실제 카메라, 내부/경로/접촉/온도 조건/전후 비교. 분자 계산을 수행한 물리 엔진은 아님 |
| `render.py` | 540×960 실제 Blender 렌더, 프레임별 투영 앵커·카메라 증거, 데이터·코드 해시가 같을 때만 재개 |
| `compose.py` | 540→Nearest 2배→1080 타이포/의미 효과→로컬 BGM/SFX→H.264/AAC. 출처·권한·분리 스템·동기·LUFS·피크 보존 |
| `audit.py` | 최종 MP4 전체 디코드, 컷별·사건 전후 실제 프레임, 픽셀 크롭, 공급 자료/기존 영상 보존 검사 |
| `compare.py` | 원본 Ref3·Ref4·EP05 및 EP06 실제 프레임의 나란한 비교. 같은 편집 역할끼리 비교하며 동일 과학 현상으로 오인하지 않음 |

문서: `EDITORIAL_AUDIT.md`, `STORYBOARD.md`, `SOURCE_AND_SCOPE.md`, `ep06/sample_review/GATE.md`.

## 재현

작업 루트에서 실행한다. 설치된 Blender 5.0 경로는 이 환경 기준이다. `plan.py`는 초기 작성 기록이며 확정된 `episode.json`을 다시 덮어쓰지 않는다.

```powershell
& 'C:/Program Files/Blender Foundation/Blender 5.0/blender.exe' -b --python production/minsu_v31/render.py -- --preflight
python production/minsu_v31/compose.py --preflight
& 'C:/Program Files/Blender Foundation/Blender 5.0/blender.exe' -b --python production/minsu_v31/render.py -- --frames 306:456 --resume
python production/minsu_v31/compose.py --sample --output exports/MINSU_V31_ICE_DISCOVERY_SAMPLE.mp4
python production/minsu_v31/audit.py --sample --video exports/MINSU_V31_ICE_DISCOVERY_SAMPLE.mp4
```

5초 MP4 실제 프레임을 검토하고 핵심 발견·미술·인과 순서가 충분할 때 본편으로 진행한다. 자동 파일 검사만으로 이 단계를 통과시키지 않는다.

```powershell
& 'C:/Program Files/Blender Foundation/Blender 5.0/blender.exe' -b --python production/minsu_v31/render.py -- --resume
python production/minsu_v31/compose.py --output exports/MINSU_EP06_V31_ICE.mp4
python production/minsu_v31/compose.py --preview
python production/minsu_v31/audit.py --video exports/MINSU_EP06_V31_ICE.mp4
python production/minsu_v31/compare.py --final
```

최종 검토는 `ep06/review/SHOT_*.jpg`와 비교판을 직접 확인한다. 실제 재생 속도·사람의 청취·휴대폰 앱 표시는 별도 검수 범위이며 프레임 검사만으로 승인했다고 보고하지 않는다. 기존 주제 데이터·프롬프트·영상의 보존 해시는 `review/preservation_before.json`을 기준으로 확인한다.

## 타이포그래피

HOOK 113px / EXPLANATION 61px / IMPACT 148px / MICRO 33px / FACT 44px / RESULT 110px가 기준이며, 실제 문구 폭과 등장 프레임에 따라 조정한다. 앰버는 발견/이동 대상, 시안은 내부/결론, 코럴은 저항/조건 대비에 사용한다. 두 번째 줄이라는 이유로 색을 바꾸지 않는다. 보조 창은 실험 조건과 출처가 공개되는 때에만 표시한다.

화살표는 설치된 Segoe UI Symbol로 래스터화하며 폰트 파일은 복제하지 않는다. Jua·Nanum·Galmuri는 기존 프로젝트의 파일과 라이선스를 재사용한다.

Jua에 없는 말줄임표도 같은 기호 폴백을 사용한다. 실제 MP4에서 발견한 SHOT_10 인물 크롭은 별도 `ep06_repair_shot10` 작업에 744–845프레임만 재렌더했다. `ep06/repair_receipt.json`은 변경한 카메라 분기·양쪽 소스 해시·그대로 유지한 948프레임의 검증을 기록한다. 최종 manifest의 `sourceHash`는 `null`이며 혼합 이력을 단일 버전으로 꾸미지 않는다. 이 상태에서 일반 `--resume`을 실행하면 안전하게 전체를 다시 렌더한다. 최종 `.blend`는 마지막 포즈의 씬 스냅샷이며 전체 애니메이션의 재현은 Python 프레임 평가로 수행한다.

## 검사의 한계

`EffectTimeline`의 컴파일된 개수는 실제 화면에 그린 효과 개수와 같지 않다. V3.1은 모든 기존 브래킷/패널 효과를 중복 렌더하지 않고 의미에 맞는 경로·접촉선·명시적 타이포로 대체한다. 발견 카메라는 실제 추적이며 줌 효과의 개수로 완성도를 평가하지 않는다. 모식도에는 실측 거리·속도·힘을 발명해 넣지 않는다.
