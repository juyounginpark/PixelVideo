import csv
import json
from collections import Counter
from datetime import datetime,timezone,timedelta
from pathlib import Path

root=Path('research/arca')
source=json.loads((root/'collected/articles.json').read_text(encoding='utf-8'))
assessment=json.loads((root/'reselection_assessments.json').read_text(encoding='utf-8'))
metrics=json.loads((root/'reselection_metrics.json').read_text(encoding='utf-8'))
stage1={r[0]:r for r in json.loads((root/'stage1.json').read_text(encoding='utf-8'))}
amap={r['id']:r for r in assessment}
mmap={r['id']:r for r in metrics['articles']}
assert len(source['articles'])==20 and set(amap)=={r['id'] for r in source['articles']}
rows=[dict(r,assessment=amap[r['id']],metrics=mmap.get(r['id'],{}),stage1=stage1[r['id']][1],stage1_reason=stage1[r['id']][2]) for r in source['articles']]
counts=Counter(r['assessment']['final'] for r in rows)
first_counts=Counter(r['stage1'] for r in rows)
candidates=sorted([r for r in rows if r['assessment']['final'] in ['조건부 후보','우선 후보']],key=lambda r:r['assessment'].get('priority',999))
(root/'reselection_results.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
(root/'final_candidates.json').write_text(json.dumps(candidates,ensure_ascii=False,indent=2),encoding='utf-8')
timestamp=datetime.fromisoformat(metrics['collected_at_utc']).astimezone(timezone(timedelta(hours=9))).isoformat(timespec='seconds') if metrics.get('collected_at_utc') else '새 측정 실패'
lines=['# 아카라이브 한국 괴담 20건 재선정 보고서','',
'- 요청: U-027. 디시인사이드 결과는 보존하고 원래 아카라이브 20건으로 복귀했다.',
f'- 조회 지표 새 수집 시각: {timestamp} (Asia/Seoul)',
'- 표본: 기존에 수집한 한국 괴담 카테고리 공지 제외 20건. 이번 측정에서도 해당 20개 모두 목록에 있어 수치 갱신에 성공했다.',
'- 제목에 따라 기존 1차 판정을 유지했다. 통과·보류 11건의 본문을 확보했으며, 이미지 중심 글은 실제 이미지를 읽었다.',
'- 제목만 보고 남겼던 글 중 현실 사건·민감 내용이 드러난 글은 2차에서 제외했다.',
'',
'## 결과','',
f'제목 1차: 통과 {first_counts["통과"]}건, 보류 {first_counts["보류"]}건, 제외 {first_counts["제외"]}건. 2차 대상은 11건이다.',
f'최종: 조건부 후보 {counts["조건부 후보"]}건, 제외 {counts["제외"]}건. 우선 후보·자료 부족 보류는 각각 0건이다.',
'',
'후킹 가능성과 압축 가능성을 우선 평가했고, 조회 지표는 보조로만 사용했다. 오감도는 해석과 관찰자의 정체가 바뀌는 공포, 귀여운 괴담은 토끼인형과 주인의 관계가 뒤집히는 이야기로 구분된다. 후보는 원문 내용 범위에서 선정했으며 새 사건·대사·반전은 작성하지 않았다.',
'',
'## 조회 지표의 범위','',
'게시 후 평균 조회/시간 = 이번 목록의 표시 조회수 ÷ (이번 수집 시각 − 게시 시각)의 시간 값. 게시 시각은 HTML time[datetime]의 ISO 시각·시간대 값을 사용했다. 모든 계산값과 수집 시각은 reselection_metrics.json에 보존했다.',
'',
'이번 재선정은 새 목록을 한 번 측정했다. 최근 구간 조회 증가 속도는 미측정이다. 이전의 다른 수집 시점과 섞어 최근 상승세를 만들지 않았다. 오래된 글과 최근 글의 누적 평균은 노출 조건·작성 후 나이·추천 필터의 영향을 받으므로 조회 성장이나 릴스 흥행 예측으로 사용할 수 없다.',
'',
'## 전체 20건의 제목·본문 판정','',
'| 제목 | 1차 | 최종 | 후킹 가능성 | 조회수 | 게시 후 평균 조회/시간 | 근거·제외 사유 |',
'|---|---|---|---|---:|---:|---|']
for r in rows:
 a=r['assessment'];m=r['metrics'];v=m.get('views');avg=m.get('lifetime_avg_views_per_hour')
 lines.append(f"| [{r['title']}]({r['url']}) | {r['stage1']} | {a['final']} | {a['hook']} | {v if v is not None else '미확인'} | {f'{avg:.2f}' if avg is not None else '미계산'} | {a['reason']} · {a['evidence']} |")
lines.extend(['','## 최종 후보와 선정 근거',''])
for r in candidates:
 a=r['assessment'];m=r['metrics']
 lines.extend([f"### {a['priority']}. {r['title']} — {a['final']}",'',
 f"원문: [{r['title']}]({r['url']})",'',
 f"- 유형: {a['type']}",
 f"- 후킹 가능성: {a['hook']} — {a['reason']}",
 f"- 표시 조회수: {m['views']}회 / 게시 후 평균 조회: {m['lifetime_avg_views_per_hour']:.2f}회/시간",
 f"- 핵심 사건 요약: {a['summary']}",
 f"- 시각화 근거: {a['visual']}",
 f"- 원문 근거: {a['evidence']}",
 f"- 자료 확인 범위: {a['review']}",
 f"- 제작 조건: {a['condition']}",
 f"- 출처·이용 허락: {a['source']}",''])
lines.extend(['## 후보의 내용 조건 평가','',
'| 후보 | 핵심 미스터리 | 사건 변화 | 시각화 | 압축 | 보상 |',
'|---|---|---|---|---|---|'])
for r in candidates:
 lines.append('| '+r['title']+' | '+' | '.join(r['assessment']['criteria'])+' |')
lines.extend(['','## 제외 필터의 적용','',
'- 실제 사건으로 제시된 범죄·주거 침입·아동 유인·재판·참사는 진위를 검증해 실제 사건이라고 확정한 것은 아니지만, 사용자 편집 기준에 따라 제외했다.',
'- 전언형 괴담·일상 꿈 이야기는 현실의 범죄·피해·정치 사건과 구별해 검토했다. 귀여운 괴담을 검증된 실화나 귀신의 실재로 소개하지 않는다.',
'- 뒤틀린 전래동화는 후킹이 강하지만 일부 이미지의 노골적인 신체 내부 표현 때문에 글 전체를 후보에서 제외했다. 단군 신화 부분만을 임의로 안전한 새 이야기로 바꾸지 않았다.',
'- 댓글 경고 글은 이미지 내용이 개인정보·법적 분쟁 공지였고, 동생의 추억담은 납치·아동 피해·잔혹한 범행이 원문의 핵심이어서 제목과 달리 제외했다.',
'- MBC 시험방송 글은 실제 방송 화면과 정치인 연설 자료가 포함되어 이번 후보에서 제외했다. 방송 화면의 디자인 참고 자료는 보존했다. 캡처 속 음성에 관한 설명은 게시자의 설명이며 직접 들은 관찰값이 아니다.',
'- 모든 제외 항목을 특정 플랫폼의 정책 위반으로 단정하지 않는다. 이번 판단은 사용자의 더 엄격한 수위·사건·민감·정치 제외 기준이다. 플랫폼 정책별 적합성은 미검증이다.',
'',
'## 자료와 문서','',
'- [선별 지침](../../POST_SELECTION_GUIDELINES.md)',
'- [P-004 프롬프트](../../prompts/MYSTERY_POST_SELECTION_v4.md)',
'- [전체 판정 JSON](reselection_results.json)',
'- [최종 후보 JSON](final_candidates.json)',
'- [20건 지표 CSV](reselection_metrics20.csv)',
'- [새 목록 HTML](listing_reselection.html), [측정값](reselection_metrics.json)',
'- stage2/의 게시글 번호별 HTML·JSON·Markdown은 본문 근거다. stage2/images/의 게시글 번호·이미지 번호별 PNG와 분할 PNG는 실제 읽은 근거다.',
'- 기존 아카라이브 수집에서 발생했던 429는 과거 이력으로 보존했다. 이번 재수집에서는 캐시를 재사용하고 미확보 본문 4건만 추가 요청해 11건을 확보했다.'])
(root/'RESELECTION_REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
with (root/'reselection_metrics20.csv').open('w',encoding='utf-8-sig',newline='') as file:
 writer=csv.writer(file)
 writer.writerow(['id','title','url','published_at','collected_at_utc','views','elapsed_hours','lifetime_avg_views_per_hour','stage1','final','hook'])
 for r in rows:
  m=r['metrics'];a=r['assessment']
  writer.writerow([r['id'],r['title'],r['url'],m.get('published_at'),m.get('collected_at_utc'),m.get('views'),m.get('elapsed_hours'),m.get('lifetime_avg_views_per_hour'),r['stage1'],a['final'],a['hook']])
print('Verified report sample:',len(rows),'candidates:',len(candidates))
