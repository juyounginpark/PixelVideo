# MINSU V4 작업 파이프라인

활성 규칙은 `config/`의 8개 공통 설정 및 루트 U-088/089. 이전 마스터 프롬프트는 읽기 가능한 이력으로 보존하고 현재 실행에 섞지 않는다. TTS 없음. 한글 주 자막+영어 보조 자막, 기존 로컬 BGM/SFX.

`episode.json`이 리뷰된 구조화 입력이다. 공통 지침 전문/전체 로그를 에피소드마다 생성하지 않는다. `plan.py`는 최초 P-033 초안 기록이며 기존 episode.json을 덮어쓰지 않는다. `common.validation`은 Story Map/11개 컷 필드/과학 범위/원문 해시를 검사한다. 자동 점수로 편집 합격을 내리지 않는다. EP07은 기존 공급 목록의 명시적 어댑터이며 임의 소재나 공급 실패 시 대체 주제가 없다.

`TypographyTheme`는 Galmuri11 Bold DISPLAY / Galmuri11 Regular BODY만 사용한다. 모든 UI 문자열은 같은 경로를 거치며 cmap에 글리프가 없으면 실패한다. 12px 글리프를 이진 마스크로 만든 뒤 정수 배율/Nearest로 최종 1080 UI에 합성한다. 한글은 60px 본문, 영어는 36px 보조가 기본이다. 작은 정보는 36px. 같은 역할의 폰트/색상 규칙이 유지되며 선택 단어만 색을 바꾼다. 폰트 라이선스는 기존 OFL을 보존한다.

`galaxy_scene.py`는 실제 Blender 장면, `art_v4.py`는 재질·조명·오브젝트, `character_director.py`는 전신 관찰/장치 접근, `render.py`는 네이티브 프레임과 카메라 증거, `compose.py`는 UI·인코드·오디오의 분리 캐시다. 과학 궤적은 해석적 설명 모형이며 관측 데이터나 중력 N-body 계산이 아니다.

## 실행

프로젝트 루트에서 실행한다. 각 명령의 전체 로그는 파일로, 대화에는 단계 요약만 반환한다. 무거운 Blender 프로세스는 파일 락으로 하나만 허용한다. 배치 명령은 NarrativeDirector 컴파일→전 프레임 투영/글리프/레이아웃 사전 검사→렌더→합성 순서로 실행한다. 캐시 재검증 모드에서는 이미 동일 키로 검증된 입력의 사전 계산을 반복하지 않는다.

```powershell
python production/minsu_v4/run.py sample
python production/minsu_v4/audit_video.py --video exports/MINSU_V4_GRAVITY_SAMPLE.mp4 --out production/minsu_v4/ep07/sample_review --shots S05,S06
# 실제 샘플·인물 시안 검토 후 GATE.json과 source_receipt.json 기록
python production/minsu_v4/run.py preview
# 실제 프리뷰 검토, 문제 있는 SceneSpec만 수정 후 재실행
python production/minsu_v4/run.py final
python production/minsu_v4/run.py verify-cache
```

샘플/프리뷰 GATE는 사람이 읽을 근거와 한계를 기록하는 단계다. 기술 QA 통과만으로 생성하지 않는다. 역할극·과학·자막은 신규 소재에 맞게 검토해야 하며 현재 임의 소재의 모델링까지 완전 자동으로 생성한다고 주장하지 않는다.

## 캐시와 무효화

캐시는 입력 키뿐 아니라 출력 SHA256도 대조한다. native 캐시는 로컬 컷 시간으로 평가하므로 컷 이동만으로 다른 컷의 동작 위상이 달라지지 않는다. 카메라/행동 변경은 해당 SceneSpec의 native 키만 바꾼다. 모든 컷이 사용하는 재질/셰이더 코드 변경은 해당 모든 컷을 무효화한다. 캐릭터/폰트/음원은 기존 파일을 재사용하며 Blender 장면은 packed `.blend`와 핸들 맵으로 재로딩한다.

자막 변경은 해당 컷의 UI·인코드만, 오디오 입력 변경은 기존 영상에 오디오만 재합성한다. 수동으로 캐시를 합격 처리하지 않는다. 파일 손상 또는 코드/입력 차이는 다시 처리한다. 디스크에 프레임/컷 manifest만 저장하고 사용하지 않는 폴리곤 좌표는 생성하지 않는다. 긴 전체 로그와 1,020개 프레임 경로를 모델에 반복 전달하지 않는다.

검증: `test_system.py`는 글리프 실패, 이진 픽셀, 자막/음향/카메라/행동별 무효화 계약과 공급 실패 시 장면 대체 금지를 검사한다. 실제 캐시 재사용은 native/compose 실행 기록으로 별도 확인한다. `audit_video.py`는 완성 MP4를 전부 디코드하고 360px 모바일 크기에서 0.267초 간격+사건/경계 프레임을 저장한다. `technical_audit.py`는 실제 AAC를 PCM으로 디코드해 원본 믹스와 상관 분석하여 인코딩 후 지연도 검사한다. 실제 사람의 청취·실시간 재생·시청 지속률은 별도이며 수치 검사로 대체하지 않는다.
