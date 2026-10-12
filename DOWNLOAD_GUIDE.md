# 계정별 조회수 상위 릴스 다운로드

지정한 7개 계정에서 수집 가능한 릴스 목록 전체의 카운트를 조회한 뒤, 계정별 상위 3개만 MP4로 저장한다. 최신 3개를 고르는 프로그램이 아니다. 대상은 `accounts.json`에서 수정할 수 있다.

## 실행

### 브라우저에서 로그인

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\login_browser.ps1
```

별도 Edge 창에서 인스타그램에 직접 로그인한다. 추가 인증도 브라우저에서 완료한다. 로그인 후 뜨는 작은 창에 방금 로그인한 계정의 사용자명을 입력한다. 비밀번호는 인스타그램 페이지에만 입력한다. Chrome을 사용하려면 `-Browser chrome`을 추가한다.

이 기능은 [Playwright의 설치된 Edge/Chrome 실행 기능](https://playwright.dev/python/docs/browsers#google-chrome--microsoft-edge)과 [브라우저 컨텍스트 쿠키 API](https://playwright.dev/python/docs/api/class-browsercontext#browser-context-cookies)를 사용한다. 일반 브라우저의 기존 프로필을 읽지 않고, `%LOCALAPPDATA%\PIXELvideo\instagram\browser-profile-브라우저명\`에 별도 프로필을 만든다. 그 창의 Instagram 쿠키만 로컬 Instaloader 세션으로 전달한다.

세션 저장 후 `run_download.ps1`은 저장된 사용자명으로 실행한다. 브라우저 로그인 성공은 API 접근 성공이나 429 해제를 보장하지 않는다. 세션·브라우저 프로필은 로컬 계정 인증 정보이므로 다른 사람에게 전달하지 않는다.

### 다운로드 실행

이 폴더에서 PowerShell을 열고 실행한다.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run_download.ps1
```

인스타그램이 로그인을 요구하면 본인 인스타그램 사용자명을 넣어 실행한다. 비밀번호와 2단계 인증 코드는 터미널에서 직접 입력한다.

다운로드 없이 로그인만 먼저 하려면 아래를 실행한다. 성공하면 이후 `run_download.ps1`이 저장된 사용자명과 세션을 사용한다.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\login_instagram.ps1
```

별도 로그인 창에서 사용자명(이메일이 아닌 계정 아이디)을 입력한다. 비밀번호는 숨겨진 입력으로 받는다. 추가 인증이 필요하면 안내에 따른다. 세션 만료로 로그인에 실패한 경우 이 명령에 `-FreshLogin`을 추가한다.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run_download.ps1 -Login 내인스타아이디
```

비밀번호는 파일에 저장하지 않는다. 재사용할 로그인 세션은 작업 폴더 밖 `%LOCALAPPDATA%\PIXELvideo\instagram\`에 저장한다. 세션이 만료되면 `-FreshLogin`을 추가한다. 기존 세션은 백업으로 보존한다. 인스타그램이 추가 인증을 요구하면 인스타그램 앱/웹에서 해당 인증을 완료해야 할 수 있다.

순위만 조사하고 영상은 받지 않으려면 `-RankOnly`를 추가한다.

## 저장 결과

```text
references/
  download_summary.json
  pixel.sciences2/
    ranking.json
    릴스코드.mp4
    릴스코드.json
    릴스코드.txt
  zenith.whatif/
    ...
```

- `ranking.json`: 수집한 릴스 목록, 두 카운트 값, 수집 시각, 선택한 지표와 상위 순위, 오류.
- `.mp4`: 음성을 포함한 인스타그램 제공 영상 파일. 별도 음원 연결이 영상 파일에 포함되지 않는 경우 앱 재생 사운드와 다를 수 있다.
- `.json` / `.txt`: 원본 링크, 게시일, 카운트, 순위, 캡션.
- `download_summary.json`: 계정별 완료/실패 및 아직 시도하지 않은 계정.

수집된 계정이 3개 미만의 릴스만 제공하면 존재하는 개수만 저장한다. 동률이면 게시일이 최신인 순서, 다음으로 릴스 코드 순서로 선택한다. 재실행 시 같은 코드의 정상 MP4는 다시 받지 않는다. `.part`는 미완성 파일이며 완료 영상으로 취급하지 않는다.

## 조회수의 기준과 정확성

Instaloader 공식 API는 `video_play_count`와 `video_view_count`를 구분한다. 기본값 `auto`는 계정의 모든 수집 릴스에 play count가 있으면 해당 값으로 정렬한다. 그렇지 않으면 모든 릴스에 view count가 있을 때만 그 값으로 정렬한다. **서로 다른 카운트를 영상별로 섞지 않는다.** API 카운트와 앱의 표시 조회수가 항상 같다고 보장하지 않는다. 사용한 필드는 결과에 기록된다. [공식 카운트 문서](https://instaloader.github.io/module/structures.html)

view count만을 엄격히 기준으로 삼으려면 다음 명령을 사용한다.

```powershell
.\.venv\Scripts\python.exe .\download_reels.py --login 내인스타아이디 --metric video_view_count
```

전체 목록을 끝까지 수집하지 못했거나, 어느 한 지표로 모든 릴스를 비교할 수 없으면 순위를 확정하지 않고 영상 다운로드도 하지 않는다. 수집 가능한 범위는 해당 세션에 인스타그램이 반환하는 릴스 탭 목록이다. 삭제·비공개·지역 제한 등으로 반환되지 않는 영상은 비교할 수 없다. 순위는 수집 기간의 스냅샷이며 실시간 고정 순위가 아니다.

인스타그램 접근 제한·로그인 요구·429가 발생하면 실패를 기록하고 멈춘다. 반복 접속으로 제한을 우회하지 않는다. 로그인해도 서비스 측 제한으로 다운로드가 실패할 수 있다.

## 개별 계정 실행

계정 전체 조회 없이 제공한 릴스 링크만 받으려면 다음과 같이 실행한다. 계정별 상위 순위는 조사하지 않는다.

```powershell
.\.venv\Scripts\python.exe .\download_reels.py --login 내인스타아이디 --urls 'https://www.instagram.com/reel/릴스코드/'
```

링크는 여러 개를 이어서 지정할 수 있다. 추적용 쿼리 문자열은 영상 식별에서 제외한다. 영상은 확인한 작성자 계정 폴더에 저장하고, 개별 링크 실행 결과는 `references/direct_download_summary.json`과 `references/direct_links/릴스코드.json`에 저장한다. 계정 전체 수집 결과를 덮어쓰지 않는다. 로그인·429 등 접근 제한 시 즉시 중단한다.

```powershell
.\.venv\Scripts\python.exe .\download_reels.py --accounts pixelithm hypothesis.kr --count 3 --login 내인스타아이디
```

전체 순위를 구하려면 계정의 전체 릴스 메타데이터를 읽어야 하므로 게시물이 많은 계정은 시간이 걸린다. `--scan-limit`은 진단용 제한이다. 제한으로 중단되면 상위 3개라고 판단하거나 다운로드하지 않는다.

구현은 [Instaloader 릴스 목록 API](https://instaloader.github.io/module/structures.html#instaloader.Profile.get_reels)와 [로그인·세션 API](https://instaloader.github.io/module/instaloader.html)를 사용한다. 설치 버전은 `requirements.txt`에 고정했다.

## 검증 결과 (2026-10-11)

후속 개별 링크 다운로드는 성공했다. 사용자가 제공한 DeTSMDtqIs2를 `references/pixel_sciences2/DeTSMDtqIs2.mp4`에 저장했고, 작성자·게시일·캡션·API play count를 함께 보존했다. 작성자 아이디는 기존 점 표기가 아니라 `pixel_sciences2`로 확인되어 기본 계정 목록을 보정했다. 개별 링크 관련 테스트를 포함해 총 11개 테스트가 통과했다. 아래 계정 전체 조회 실패 이력과 구분한다.

조회수 상위 정렬, 지표를 섞지 않는 처리, 누락 수치, 불완전 목록, 0 조회수, 경로 검증, 미완성 다운로드 및 기존 파일 재사용을 다루는 7개 테스트가 통과했다. 실제 pixelithm 접속 테스트는 인스타그램의 HTTP 429로 중단되었다. 영상 다운로드 성공은 아직 검증하지 못했다. 해당 실패는 `references/pixelithm/ranking.json`과 `references/download_summary.json`에 기록되어 있다.

사용자가 브라우저 로그인을 완료한 뒤 저장된 세션으로 계정 일치 검증에 성공했다. 이후 전체 대상 수집을 실행했으나 첫 대상 pixel.sciences2의 프로필 API에서 다시 HTTP 429가 반환되어 즉시 중단했다. 이번 실행의 다운로드는 0개이며, 아직 시도하지 않은 다른 6개 계정도 요약에 기록했다. 로그인 문제와 프로필 조회 제한을 구분해야 한다.
