import csv
import json
from collections import Counter
from datetime import datetime,timezone,timedelta
from pathlib import Path

root=Path('research/dcinside')
rows=json.loads((root/'sample20.json').read_text(encoding='utf-8'))
assessments=json.loads((root/'assessments.json').read_text(encoding='utf-8'))
by_no={r['no']:r for r in rows}
by_assessment={r['no']:r for r in assessments}
assert len(rows)==20 and len(by_no)==20 and set(by_no)==set(by_assessment)
combined=[dict(r,assessment=by_assessment[r['no']]) for r in rows]
(root/'selection_results.json').write_text(json.dumps(combined,ensure_ascii=False,indent=2),encoding='utf-8')
candidate_rows=sorted([r for r in combined if r['assessment']['final'] in ['우선 후보','조건부 후보']],key=lambda r:r['assessment'].get('priority',999))
(root/'final_candidates.json').write_text(json.dumps(candidate_rows,ensure_ascii=False,indent=2),encoding='utf-8')
first=datetime.fromisoformat(rows[0]['collected_at_utc']).astimezone(timezone(timedelta(hours=9)))
second=datetime.fromisoformat(rows[0]['second_collected_at_utc']).astimezone(timezone(timedelta(hours=9)))
counts=Counter(r['final'] for r in assessments)
stage1=Counter(r['stage1'] for r in assessments)
lines=['# 로스트 미디어 20개 게시글 소재 선정 보고서','',
f'- 첫 측정: {first.isoformat(timespec="seconds")} (Asia/Seoul)',
f'- 두 번째 측정: {second.isoformat(timespec="seconds")} (Asia/Seoul)',
f'- 간격: {rows[0]["interval_hours"]*60:.2f}분',
'- 표본: 사용자가 지정한 소개·추천 목록 첫 페이지의 광고·설문·공지 제외 첫 20건. 목록 순서 표본이며 조회수 상위 표본이 아니다.',
'- 아카라이브의 이전 20건 선정은 수집 대상 변경으로 중단했다. 기존 자료는 보존했다.',
'- 본문: 제목 단계 제외 3건을 빼고 17건 확보. 최종 후보 2건은 첨부 이미지도 검토했다. 제외 사유가 본문에서 확인된 글은 모든 이미지를 추가 열람하지 않았다.',
'- 게시자 주장과 검토자의 판단을 구분했다. 외부 원출처와 사실관계를 독립적으로 확정한 보고서는 아니다.',
'',
'## 결과','',
f'제목 1차: 통과 {stage1["통과"]}개, 보류 {stage1["보류"]}개, 제외 {stage1["제외"]}개. 통과·보류 17건을 2차 검토했다.',
f'최종: 조건부 후보 {counts["조건부 후보"]}개, 보류 {counts["보류"]}개, 제외 {counts["제외"]}개. 우선 후보는 0개다.',
'',
'이번 표본에서 남은 후보는 공포보다 유실 게임 추적·복원에 관한 미스터리에 가깝다. 괴담이나 공포물로 바꾸려면 원문에 없는 내용을 창작해야 하므로 그런 변형은 하지 않았다. 실제 범죄·사고·피해 사건을 공포 소재로 쓰는 글은 제외하되, 작품·게임 자료의 유실과 발굴 정보는 검토했다.',
'',
'## 시간당 조회 지표 해석','',
'게시 후 평균 조회/시간 = 첫 목록 표시 조회수 ÷ (첫 수집 시각 − 게시 시각)의 시간 값. 서비스의 게시 시각은 Asia/Seoul로 해석했다. 표에는 소수 둘째 자리까지 표시했고 원 계산값은 JSON에 보존했다.',
'',
'구간 조회/시간 = (두 번째 표시 조회수 − 첫 표시 조회수) ÷ 관측 간격. 한 시점 평균과 구간 증가를 혼합하지 않았다. 약 6분은 추세 판단에 짧으며, 본문을 수집한 17건 대부분이 1회씩 늘었다. 수집기의 본문 방문이 조회수에 영향을 주었을 수 있으나 정확한 집계 규칙을 확인하지 못해 임의로 차감하지 않았다. 이 구간 지표로 인기를 정렬하지 않았다.',
'',
'전체 표본에서 게시 후 평균이 가장 높은 글은 일부혐주의를 표시한 82239번(26.44회/시간)이지만 제목 필터에서 제외했다. 추천 필터와 게시 후 나이, 시리즈 노출을 통제하지 않은 보조 지표이며 릴스의 예상 조회수를 뜻하지 않는다.',
'',
'## 1차 제목 심사 및 조회 지표 — 전체 20건','',
'| 번호 | 제목 | 게시 시각(KST) | 첫 조회 | 평균 조회/시간 | 두 번째 조회·증가 | 구간 조회/시간 | 제목 판정 | 제목 근거 |',
'|---|---|---|---:|---:|---|---:|---|---|']
for r in combined:
 a=r['assessment']
 lines.append(f"| {r['no']} | [{r['title']}]({r['url']}) | {r['published_at_kst'][:19].replace('T',' ')} | {r['views']} | {r['lifetime_avg_views_per_hour']:.2f} | {r['second_views']} (+{r['view_delta']}) | {r['interval_views_per_hour']:.2f} | {a['stage1']} | {a['stage1_reason']} |")
lines.extend(['','## 2차 본문 심사','',
'내용 평가 순서는 A 핵심 미스터리, B 사건 변화, C 시각화, D 압축, E 보상이다. 제외 사유가 확정된 글은 내용 점수로 구제하지 않았다. 보류 글은 최종 후보 목록에서 제외했다.',
'',
'| 번호 | 최종 판정 | A / B / C / D / E | 후킹 가능성 | 판정 이유 | 근거 위치 |',
'|---|---|---|---|---|---|'])
for r in combined:
 a=r['assessment']
 if a['stage1']=='제외':continue
 criteria=' / '.join(a['criteria']) if 'criteria' in a else '제외 조건 확인 후 평가 중단'
 lines.append(f"| {r['no']} | {a['final']} | {criteria} | {a['hook']} | {a['reason']} | [{a['evidence']}](bodies/{r['no']}.md) |")
lines.extend(['','## 최종 후보 목록','',
'두 글 모두 소재 후보로 선정한 것이며 제작·게시 확정은 아니다. 출처, 첨부자료의 재사용 허락, 사실관계는 제작 전에 별도로 확인해야 한다. 후킹 가능성은 검토자의 평가이며 실제 시청 지속률이나 클릭률 측정값이 아니다.'])
for r in candidate_rows:
 a=r['assessment']
 lines.extend(['',f"### {a['priority']}. {r['title']} — {a['final']}",'',
 f"원문: [{r['no']}]({r['url']})",'',
 f"- 후킹 가능성: {a['hook']}",
 f"- 첫 누적 조회: {r['views']}회 / 게시 후 평균: {r['lifetime_avg_views_per_hour']:.2f}회/시간",
 f"- 관측 구간: +{r['view_delta']}회 / {r['interval_views_per_hour']:.2f}회/시간. 수집 영향 가능성 때문에 인기 판단에는 사용하지 않음.",
 f"- 선정 근거: {a['reason']}",
 f"- 원문 범위: {a['evidence']}",
 f"- 자료 확인: {a['visual_review']}",
 f"- 출처 상태: {a['source_status']}",
 f"- 영상화 이용 허락: {a['rights_status']}"])
 if r['no']=='79309':
  lines.extend(['',
  '게시자는 국산 게임인데 중문판만 보이던 상황에서 한글화 패치 공개가 다른 사람의 기억을 깨워 오래된 하드디스크의 한글 데모를 발견하게 했다고 서술한다. 정식판·해외판·한글 패치·한글 데모를 구분하는 질문과 발견의 보상이 있어 가장 먼저 검토할 만하다.',
  '',
  '원문 마지막 문장은 데모판이라는 설명과 정식한글판이라는 표현을 함께 쓴다. 이를 정식판 전체 복구로 전하지 않는다. 이미지 1~5에서는 광고·중문 메뉴·한글 타이틀·한글 메뉴를 확인했다. 발굴 파일의 정체와 원본성은 별도 검증이 필요하다. 원문에 없는 유령·저주·숨겨진 피해 사건을 추가하지 않는다.'])
 else:
  lines.extend(['',
  '게시자는 예전에 소개한 온라인 게임의 접속과 서버 동작을 개인 복각 프로젝트로 구현 중이라고 서술한다. 로그인 화면·게임 화면·추출 데이터가 있어 자료가 남아 있어도 서버 환경이 사라지면 이용하기 어렵다는 문제를 설명할 수 있다.',
  '',
  '기술 용어를 압축할 필요가 있고, 독립적인 작동 검증은 수행하지 않았다. 공식 서버 재개·정식 서비스 부활·작업 완료로 표현하지 않는다. 이미지 6의 애니메이션 전체는 검토하지 않았으며 후보 평가의 핵심 증거는 본문과 다른 정지 자료다. 실제 게임 파일을 실행하거나 외부 디스코드에 참여하지 않았다.'])
lines.extend(['','## 보류 2건','',
'- **78918 · 유실된 뮤직비디오**: 일부 화면은 있는데 전체 자료가 보이지 않는 정보 격차가 있어 후킹 가능성은 높음. 본문과 정지 이미지 6개를 확인했지만 링크 영상의 재생·음성·맥락을 확인하지 않았다. 이미지 2에는 여성이 속박된 듯한 장면이 있어 민감성 재검토도 필요하다. 이미지 5의 성은 게시자가 비교용으로 붙인 예시이며 원본 뮤직비디오 프레임이라고 확정하지 않는다. 최종 후보에 포함하지 않음.',
'- **80311 · 우연한 발굴 경험**: 수집 본문은 영상 링크와 미리보기 문구 위주다. 영상에서 설명하는 발굴 과정과 수위를 확인하지 못해 후킹·전개 평가를 보류했다. 최종 후보에 포함하지 않음.',
'',
'## 제외 소재와 근거 관리','',
'인도네시아 빙산 시리즈 1~5층은 글 전체가 정치·민감 사건·높은 수위 내용과 일반 작품 정보를 섞은 모음이다. 이번 작업은 게시글 단위 후보 목록이므로 전체 글을 제외했다. 독립적인 비민감 항목을 추후 별도 출처로 검토할 수 있으나 이번 후보로 선택하지 않았다. 1층 P2에서 작성자는 제미나이로 내용을 옮겼으며 정보 부족·오역·오정보 가능성이 있다고 밝혔다. 다른 층 전체의 작성 도구를 확정하지 않으며, 게시글의 단정적인 사실 주장도 그대로 검증된 사실로 쓰지 않는다.',
'',
'제목 단계 제외 글 3개는 본문을 읽지 않았다. 본문 단계 제외 글 13개 중 이미지 전체를 확인하지 않은 글은 이미지에 대한 관찰·정책 적합성을 주장하지 않았다. 확인된 텍스트만으로 제외 사유가 충분한 글은 추가 수집을 하지 않았다.',
'',
'플랫폼 정책별 위반 여부는 미검증이다. 사용자의 실제 사건·정치·민감 내용·수위 제외 기준을 적용했으며, 이 기준의 모든 항목이 특정 플랫폼의 금지 항목이라는 의미는 아니다.',
'',
'## 문서와 데이터','',
'- [선별 지침](../../POST_SELECTION_GUIDELINES.md)',
'- [P-003 프롬프트](../../prompts/MYSTERY_POST_SELECTION_v3.md)',
'- [최종 후보 JSON](final_candidates.json)',
'- [전체 선정 JSON](selection_results.json)',
'- [20건 지표 CSV](metrics20.csv)',
'- [원문 HTML 목록 1차](listing.html), [2차](listing_second.html)',
'- [측정 시각](snapshots.json)',
'- 본문 근거: bodies/의 글 번호별 HTML·Markdown. 이미지 근거: images/의 글 번호별 원본·정지 PNG·검토용 모음.'])
(root/'SELECTION_REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
with (root/'metrics20.csv').open('w',encoding='utf-8-sig',newline='') as file:
 writer=csv.writer(file)
 writer.writerow(['no','title','url','published_at_kst','first_collected_at_utc','first_views','elapsed_hours','lifetime_avg_views_per_hour','second_collected_at_utc','second_views','interval_hours','view_delta','interval_views_per_hour','stage1','final','hook'])
 for r in combined:
  a=r['assessment']
  writer.writerow([r['no'],r['title'],r['url'],r['published_at_kst'],r['collected_at_utc'],r['views'],r['elapsed_hours'],r['lifetime_avg_views_per_hour'],r['second_collected_at_utc'],r['second_views'],r['interval_hours'],r['view_delta'],r['interval_views_per_hour'],a['stage1'],a['final'],a['hook']])
print('Rows:',len(rows),'Candidates:',len(candidate_rows),'Final counts:',dict(counts))
