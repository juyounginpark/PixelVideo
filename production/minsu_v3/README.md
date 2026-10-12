# MINSU V3 — 의미 이벤트 기반 편집

기존 Blender 5.0.1 / Pillow / FFmpeg와 V2 로컬 오디오를 사용한다. Remotion·CapCut·TTS를 추가하지 않았다. 주제 선정 코드는 새로 만들지 않으며 기존 나무위키 자료/선별 지침을 따른다.

## 데이터와 코드

- `effects.py`: `EffectDirector`. 장면→행동 ID→대상→사건 프레임을 검증한 뒤 Effect/Camera/Caption/Particle/SoundEffectTimeline을 생성한다. 예산은 상한이며 부족분을 자동으로 채우지 않는다.
- `native.py`: 실제 Blender 카메라 렌즈/orthographic scale과 대상 방향을 제어한다. 대상이 잘리면 줌을 제한하고 이유를 남긴다. 오브젝트 메시를 현재 카메라 좌표로 투영해 UI 앵커·보호 범위·대상 마스크를 전달한다.
- `graphics.py`: 540×960 격자의 십자 파티클·방사형 반응·질문·하이라이트, 최종 해상도 임팩트 글자·상태창·자막. 피사체를 보호하고 자리가 없으면 오류를 보고한다.
- `render_job.py`: 명시한 씬 어댑터와 Spec만 실행한다. 샘플 외 제작은 `--spec`이 필요하다. 데이터/렌더 코드 해시로 재개 여부를 판단한다.
- `compose_job.py`: 픽셀 2배 확대→효과/UI→BGM/SFX→AAC/H.264→실제 디코드·프레임 수·규격·음량 검사.

프레임은 **0부터 시작**, 구간 끝은 미포함이다. `held_frame`은 0.13초 홀드 구간에 3D 동작·카메라·앵커를 같은 원본 프레임에서 평가한다. 전체 길이는 유지하므로 재개 지점에서 생기는 작은 점프는 장면별로 검토해야 한다.

## 효과

| 효과 | 실행 위치 / 조건 |
|---|---|
| Punch Zoom | 실제 3D 카메라, 사건 대상 기준, 0.10초 peak 후 안정화 |
| Impact Caption | 0.75→1.12→1.00 팝, 기본 자막 중복 차단 |
| Dark Focus | 투영한 메시 마스크 외부만 최대 28% 어둡게, 마스크 없으면 실패 |
| Pixel Spark | 대상 주변 결정적인 7개 십자, 두세 색, 무작위 전역 배치 없음 |
| Question Pop | 머리 위 짧은 이동/퇴장 |
| Reaction Burst | 대상 주변 방사선, 전체 백색 플래시 없음 |
| Object Highlight | 매 프레임의 투영된 대상 경계에 코너 브래킷 |
| Data Reveal | provenance가 있는 상태값 또는 실제 프레임 샘플만 표시 |
| Impact Freeze | 명시된 허용 사건에 한해 4프레임 내외 홀드 |
| Transition Director | 기본 하드컷, 명시된 매치컷/이전 컷 기반 짧은 wipe |

매치컷은 자동 모션 추정이 아니라, 씬 어댑터의 동일 동작/위치 이어짐을 계획하고 검수하는 방식이다. 상태창은 가짜 숫자를 카운트하지 않는다.

## 한계

- Dark Focus 마스크는 실제 메시 면의 화면 투영이다. 앞의 다른 오브젝트에 가린 부분까지 분리하는 깊이/cryptomatte 마스크는 아니다. 가림이 있는 장면에서는 해당 효과를 사용하지 않는다.
- 모션과 과학 시각화는 선택된 소재의 어댑터에서 구현해야 한다. EffectDirector가 임의의 과학 시뮬레이션을 발명하지 않는다.
- 샘플에서 사용하지 않은 선택형 효과는 코드/단위 검사만으로 영상 품질 승인을 받지 않는다. 최종 결과 문서에서 실제 사용한 효과와 미사용 효과를 구분한다.
- 사람의 청취/실기기 앱 재생/시청 지속률 측정을 자동 QA로 대체하지 않는다.

## 6초 효과 샘플

```powershell
& 'C:/Program Files/Blender Foundation/Blender 5.0/blender.exe' -b --python production/minsu_v3/render_job.py -- --scene sample_scene --job production/minsu_v3/sample
python production/minsu_v3/compose_job.py --job production/minsu_v3/sample --output exports/MINSU_V3_EFFECT_SAMPLE.mp4
python production/minsu_v3/compose_job.py --job production/minsu_v3/sample --preview
python -m unittest discover -s production/minsu_v3 -p 'test*.py'
```

`sample_scene.py`는 얼굴/카메라/효과 검증용이며 새 과학 소재나 릴스 후보로 등록하지 않는다. 수정 전 공급 파일과 과거 영상은 보존한다.

## EP05 재현과 검수

아래 명령은 이미 검토된 EP05 산출물을 재현한다. 다음 주제를 추천하거나 큐에서 자동 소비하는 명령이 아니다. `ep05/plan.py`도 이 에피소드의 대본 기록이며 공급기를 대체하지 않는다.

```powershell
& 'C:/Program Files/Blender Foundation/Blender 5.0/blender.exe' -b --python production/minsu_v3/render_job.py -- --scene science_scene --job production/minsu_v3/ep05 --spec production/minsu_v3/ep05/episode.json --preflight
python production/minsu_v3/preflight.py --job production/minsu_v3/ep05
& 'C:/Program Files/Blender Foundation/Blender 5.0/blender.exe' -b --python production/minsu_v3/render_job.py -- --scene science_scene --job production/minsu_v3/ep05 --spec production/minsu_v3/ep05/episode.json --resume
python production/minsu_v3/compose_job.py --job production/minsu_v3/ep05 --output exports/MINSU_EP05_V3_BRAZIL_NUT.mp4
python production/minsu_v3/audit_delivery.py --job production/minsu_v3/ep05
python production/minsu_v3/write_result.py
```

`--preflight`는 실제 메시·카메라 포즈와 UI 좌표를 평가하지만 영상 프레임을 렌더하지 않는다. `--resume`는 같은 Spec/렌더 코드 해시의 완료 프레임만 재사용한다. 인코딩은 전체 프레임과 완료 기록이 모두 있을 때만 허용된다. `audit_delivery.py`는 완성 파일 QA 이후 기존 공급 자료·이전 영상 보존을 재확인하고, 컷 및 사건 전후 이미지와 효과 프레임 CSV를 만든다.
