from pathlib import Path

previous=Path('prompts/MYSTERY_POST_SELECTION_v3.md').read_text(encoding='utf-8')
prompt=previous.split('```text\n',1)[1].rsplit('```',1)[0].rstrip()
prompt=prompt.replace('https://gall.dcinside.com/mgallery/board/lists/?id=lostmedia&sort_type=N&exception_mode=recommend&search_head=80&page=1',
 'https://arca.live/b/spooky?category=%ED%95%9C%EA%B5%AD%20%EA%B4%B4%EB%8B%B4&cut=50')
prompt=prompt.replace('설문·광고·공지를 제외한 목록 순서의 첫 20건.', '기존에 수집한 한국 괴담 목록의 공지 제외 20건.')
prompt=prompt.replace('이전 아카라이브 표본은 이 결과에 섞지 않는다.', '디시인사이드 표본은 이 결과에 섞지 않는다.')
prompt=prompt.replace('디시 게시 시각은 서비스 표시를 Asia/Seoul로 해석했다는 가정을 명시한다. 시간대를 검증하지 못하면 해당 가정도 함께 남긴다.',
 '아카라이브 time[datetime]의 ISO 시각과 시간대 표기를 보존한다. 시간대가 없으면 임의로 확정하지 않는다.')
prompt=prompt.replace('로스트 미디어', '괴담')
prompt=prompt.replace('무엇이 사라졌는지, 무엇이 발견됐는지 특정되는가?', '어떤 행동·규칙·상황이 이상한지 특정되는가?')
prompt=prompt.replace('게임·방송·작품 자료의 유실과 발굴이라는 사실 정보는 소재 검토 가능하다.', '창작 괴담·민담·설화·방송 형식의 기괴함에 관한 설명은 소재 검토 가능하다.')
prompt+='\n\n[재선정 보완]\n- 이미지 속 괴담·반전을 실제로 읽고 판단한다. 제목이 괴담처럼 보여도 본문이 현실의 법적 분쟁·사생활·민감 사건이면 제외한다.\n- 모음글은 개별 이야기를 검토하되, 높은 수위 내용이 섞인 글 전체를 그대로 후보로 올리지 않는다.\n- 게시글의 장면이 제공되지 않은 짧은 문구만으로 완결된 영상이 되지 않으면 조건부로 낮추고 필요한 자료를 명시한다.\n- 조회 지표는 기존 게시 시각·조회수가 확인되는 경우에만 계산한다. 새로운 목록 요청에 실패하면 과거 측정값의 날짜를 명시한다.\n'
path=Path('prompts/MYSTERY_POST_SELECTION_v4.md')
path.write_text('# 아카라이브 괴담 2단계 선별 프롬프트 v4\n\n- ID: P-004 / 이전 버전: P-003\n- 작성일: 2026-10-12 (Asia/Seoul)\n- 상태: 작성완료·적용 진행\n- 변경: U-027에 따라 아카라이브 원 표본으로 복귀, 이미지 기반 괴담 검토 보완\n\n```text\n'+prompt+'```\n',encoding='utf-8')
logpath=Path('PROMPT_LOG.md')
log=logpath.read_text(encoding='utf-8')
entry='''## P-004 — 아카라이브 괴담 게시글 2단계 재선정 / v4

- 날짜: 2026-10-12 (Asia/Seoul)
- 작성자: 어시스턴트
- 유형: 분석
- 상태: 작성완료·적용 진행
- 관련 사용자 요청: U-022, U-023, U-024, U-027
- 이전 버전: P-003
- 변경 이유: 아카라이브로 대상 복귀, 기존 필터·후킹·조회 지표 유지
- 도구·모델: 로컬 HTML 수집·이미지 확인 / 모델명 미확인
- 입력 파일: research/arca/collected/articles.json 및 stage2/ 자료
- 결과 파일: prompts/MYSTERY_POST_SELECTION_v4.md 및 재선정 보고서

### 프롬프트 원문

```text
'''+prompt+'''```

### 실행 결과 및 피드백

기존 20건에 적용 진행. 디시 결과는 보존하고 별도 보고서 작성.

'''
if '## P-004 —' not in log:
 logpath.write_text(log.replace('## 새 기록 작성 양식',entry+'## 새 기록 작성 양식',1),encoding='utf-8')
