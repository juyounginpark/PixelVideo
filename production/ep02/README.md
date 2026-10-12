# 민수 EP02 — 무음 제작본

3D 카툰 복셀 장면을 Blender 5.0.1로 제작하고, 별도 2D UI를 합성한 로컬 검토용 릴스다. 기존 자판기 편 기획을 바탕으로 사운드는 넣지 않는다.

## 산출물

- `../../exports/MINSU_EP02_SILENT_v1.mp4`: 720×1280, 24fps, 43초, H.264, 오디오 트랙 없음.
- `../../exports/MINSU_EP02_contact_sheet.jpg`: 장면별 확인용 이미지.
- `MINSU_EP02.blend`: 인물·자판기·거리·카메라 및 프레임별 포즈를 포함한 편집 가능한 장면.
- `build_scene.py`: 3D 장면 생성과 렌더링.
- `compose.py`: 한글 UI·실제 자료와 3D 프레임을 합성해 MP4 생성.

해상도·프레임률은 이번 제작본의 실제 설정이다. 이전 지침의 1080×1920·30fps 제안과 다르며 업스케일 영상으로 표시하지 않는다.

## 무음 편집 변경

- 후반 내레이션을 의미 단위의 자막으로 교체.
- 52초 기획을 43초로 편집. 진행부 23초, 실제 자료와 설명·복귀 20초.
- 첫 장면과 같은 버튼·손·UI로 돌아오는 디졸브 연결. 원본 사진과 복셀 모델의 모든 버튼 위치가 정확히 일치하는 매치컷은 아니다.
- 민수와 구매·재방문은 각색임을 표시. 쪽지는 재현임을 표시.
- 사진과 보도로 확인한 사실을 사용하며 사라진 원인은 확인되지 않았다고 명시.

## 실제 자료

사진: `../../research/namuwiki/assets/vending_sdot.jpg`.

- 게재 크레딧: Courtesy SDOT / Seattle Met.
- https://www.seattlemet.com/news-and-city-life/2023/08/whatever-happened-capitol-hill-mystery-coke-machine
- https://www.capitolhillseattle.com/2018/06/eyewitnesses-capitol-hills-mystery-soda-machine-has-disappeared/
- https://www.atlasobscura.com/articles/seattle-mystery-soda-machine-is-missing

사진은 조사 과정에서 확보한 참고본이며 공개 게시용 이용 조건은 아직 확인되지 않았다. 이번 산출물은 로컬 검토본이다. 실제 쪽지 사진은 포함하지 않는다. 사진의 75센트 표기를 2018년 가격으로 설명하지 않는다.

## 재생성

프로젝트 루트에서 실행한다. Blender 경로는 설치 위치에 맞춘다.

```powershell
& 'C:\Program Files\Blender Foundation\Blender 5.0\blender.exe' -b -t 6 --python production/ep02/build_scene.py
python production/ep02/compose.py --preview
python production/ep02/compose.py
```

Python 의존성: Pillow, imageio-ffmpeg. 새 이미지·영상 생성 모델이나 외부 유료 API는 사용하지 않았다.

## 검증 결과

전체 1,032프레임 디코딩 통과. 720×1280, 24fps, 43.0초, 오디오 스트림 없음. 파일 크기 4,794,262바이트. 주요 12개 시점의 화면과 한글 UI를 확인했다. 인코딩된 첫·마지막 프레임 평균 픽셀 차이는 0.687/255이며 마지막은 첫 구도로 복귀한다. 실제 인스타그램 업로드 미리보기는 수행하지 않았다. 상세 결과: ../../exports/MINSU_EP02_validation.json.
