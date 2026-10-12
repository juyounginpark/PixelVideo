import json,csv
from pathlib import Path
from datetime import datetime
root=Path(__file__).parent
d=json.loads((root/'bodies.json').read_text(encoding='utf-8'))
stamp=datetime.fromisoformat(d['collected_at_utc'])
reasons={
'185585057':('제외','실제 행인의 외모·문신을 공포로 소비하며 사건 전개·결말이 부족함'),
'185382037':('조건부 후보','수면 중 체험 주장. 소리 중단→움직임 제한→감각·그림자→풀려 나옴의 완결 흐름. 1인 역할극 가능, 이용 허락 미확인'),
'185244234':('제외','제목에 실제 자살 사건·혐주의 명시. 본문 요청하지 않음'),
'184991184':('보류','후속 글. 이미지 2장과 연결된 이전 글이 핵심이나 미확인'),
'184553410':('제외','본문에 약물·주사기·피 묘사와 민감한 관계 암시. 원문 전체 제외'),
'184359754':('보류','이미지 1장이 본문 핵심. 이미지 미확인'),
'183814700':('제외','실명 배우의 개인사 체험담으로 보이는 제목. 엄격한 실제 인물 필터로 제외, 본문 미확인'),
'183785098':('제외','실제 전쟁 생존자 경험·민감한 사건. 본문 요청하지 않음'),
'183342739':('제외','군사 인터뷰로 제시된 실제 경험 자료. 엄격한 실제 사건 필터로 제외, 본문 미확인'),
'183327362':('제외','실제 사망한 지인의 개인사·상실을 소재로 한 제목. 본문 미확인'),
}
rows=[]
for r in d['articles']:
    state,reason=reasons.get(r['id'],('보류','제목만으로 제외 확정 불가. HTTP 429로 추가 본문 수집 중단, 내용·매체 미확인'))
    age=(stamp-datetime.fromisoformat(r['published_at'].replace('Z','+00:00'))).total_seconds()/3600
    v=int(r['views_displayed'].replace(',',''))
    rows.append(dict(id=r['id'],title=r['title'],url=r['url'],status=state,reason=reason,published_at=r['published_at'],views=v,average_views_per_hour=round(v/age,2),body_collected='text' in r))
(root/'selection_results.json').write_text(json.dumps({'source_url':d['source_url'],'collected_at_utc':d['collected_at_utc'],'scope':'first listing page, 20 posts; partial body review; not overall ranking','articles':rows},ensure_ascii=False,indent=2),encoding='utf-8')
(root/'final_candidates.json').write_text(json.dumps([r for r in rows if r['status']=='조건부 후보'],ensure_ascii=False,indent=2),encoding='utf-8')
with (root/'metrics20.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
lines=['# 실화·썰 카테고리 역할극 후보 검토','',f'원본 목록: {d["source_url"]}','',f'목록 측정: {stamp.astimezone().isoformat()} / UTC {d["collected_at_utc"]}','',
'첫 페이지 공지 제외 20건. 전체 게시판·인기 상위 표본이 아니다. 제목 1차와 본문 2차를 구분했다. 본문 HTML 5건 수집 뒤 다음 글에서 HTTP 429가 발생해 추가 요청 없이 중단했다. 그중 텍스트 핵심 3건은 판단했고 이미지 의존 2건은 보류했다. 다른 10건은 제목 단계에서 보류다. 제목 제외 5건, 본문 제외 2건, 보류 12건, 최종 조건부 후보 1건. 미확인 자료를 읽은 것처럼 판정하지 않았다.','',
'기존 제외 기준을 유지했다. 카테고리의 실화 표시는 진위 증명이 아니다. 수면·꿈 체험은 익명 주장으로 검토하며 실제 범죄·피해·정치·민감한 개인사를 공포로 소비하는 글은 제외한다. 이용 허락과 플랫폼별 정책 적합성은 별도 미확인이다.','',
'## 20건 전체 판정','','| 글 | 판정 | 조회 | 누적 평균 조회/시간 | 근거 |','| --- | --- | ---: | ---: | --- |']
for r in rows: lines.append(f'| [{r["title"]}]({r["url"]}) | {r["status"]} | {r["views"]} | {r["average_views_per_hour"]:.2f} | {r["reason"]} |')
lines+=['','조회 지표 = 목록 누적 조회수 ÷ (목록 수집시각 − 게시시각)의 시간. 첫 스냅샷만 사용했으며 최근 상승세·구간 속도는 미측정이다. 게시 나이가 서로 달라 이 수치만으로 우열을 정하지 않는다. 원시 ISO 시각·조회수는 articles.json과 metrics20.csv에 보존했다.','',
'## 최종 후보와 제작 판단','','[방금 가위 눌렸는데 개무서웠음](https://arca.live/b/spooky/185382037): 후킹은 소리의 갑작스러운 중단과 움직임 제한의 결합이다. 불이 켜져 있는 방을 유지해 어둠에 의존하지 않고 몸의 변화와 주관 감각으로 진행한다. 기승전결이 원문에 있으며 마지막 탈출은 보여줄 수 있지만 정체가 밝혀지는 반전은 없다. 원문에 상대의 발화가 없어 1인 역할극이 적합하다. 공포 체험·통증 반응은 있으나 실제 범죄·피해 사건이나 고어 장면은 없다. 각색·게시 허락은 미확인이다. 후킹 평가가 실제 시청 유지율을 보장하지 않는다.','',
'[후보별 대본](SCRIPTS.md)에 목표 60초의 대사·행동·구도·자막, 원문과 각색의 경계, 레퍼런스 타임코드를 기록했다. 녹음 및 영상은 미제작이며 길이는 추정이다. 이번 신규 카테고리 결과는 기존 한국 괴담 후보와 합산하지 않는다.','',
'## 한계와 다음 수집','','보류 12건은 최종 후보가 아니다. 제한이 해소된 뒤 본문과 핵심 매체를 확인해야 한다. 현재 턴에서 재시도·반복 측정·예약 수집을 하지 않았다. 같은 시리즈의 식물 2건은 이전 이야기와 후속 이미지까지 확인한 뒤 중복 여부를 판단해야 한다.']
(root/'REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('20 판정; 조건부 1, 제외 7, 보류 12')
