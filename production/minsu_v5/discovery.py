"""Cache-only discovery extension. No network crawler or substitute-topic fallback."""
from pathlib import Path
from urllib.parse import quote,urljoin
import json,hashlib,argparse
from topic_history import previous_topics,duplicate
from datetime import datetime,timezone,timedelta
R=Path(__file__).resolve().parent;ROOT=R.parents[1]
def read(p):return json.loads(Path(p).read_text('utf-8'))
def write(p,d):Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2),'utf-8')
stamp=datetime.now(timezone(timedelta(hours=9))).isoformat(timespec='seconds')
parser=argparse.ArgumentParser();parser.add_argument('--job',type=Path,required=True);args=parser.parse_args()
job=args.job.resolve()
if (job/'topic.json').exists():raise ValueError('Existing topic selection is immutable; use a new episode directory')
history=previous_topics();research_out=job/'discovery'
# A bounded editorial batch from the existing linked-category snapshots, not invented topics.
batch={'listing':[0,1,2,3,4,5,6,7,8,9,13,18,19,21,22,23,24,27,31,33,44,46,56,59,63,69,72,76,78,80,82,84,87,90],
       'history':[34,84,85,129,135],'main':[27]}
category={'listing':'자연과학 관련 정보','history':'역사 관련 정보','main':'인터넷 미스터리'}
shortlist={('listing',23):'red_rain',('listing',63):'zebra',('listing',44):'heatburst',('listing',90):'subice',('listing',72):'purr',('listing',87):'whale52',('listing',84):'titan',('history',84):'voynich',('listing',4):'mpemba',('history',135):'skull'}
reviews={
'red_rain':('VERIFIED_EXPLAINED',[24,24,18,9,9,9],'빨간 비가 흰 우산에 점을 남긴다','가라앉는 입자→배양된 조류로 색의 단서를 연결','캐릭터·비·병·현미경으로 가능',.10,['https://www.iangoddard.com/sampath2001.pdf','https://doi.org/10.1029/2002EO000250','https://www.microbiologyresearch.org/content/journal/micro/10.1099/mic.0.062711-0'],'2001년 시료의 붉은 색 원인에 범위 제한. 대량 공중 유입 경로는 미규명. 2013 DNA 검사는 별도 연구이고 2001 배양의 독립 재현으로 쓰지 않음'),
'zebra':('VERIFIED_EXPLAINED',[22,23,17,8,9,7],'파리가 민무늬 말에는 앉고 줄무늬에는 착륙을 놓친다','접근과 착륙을 분리한 비교','말 관절과 비행 곤충 추가 모델 필요',.15,['https://www.nature.com/articles/s41598-022-22333-7'],'줄무늬의 흡혈파리 착륙 감소 효과로 제한; 진화의 단일 원인으로 단정하지 않음'),
'subice':('VERIFIED_UNRESOLVED',[22,22,16,9,9,6],'얼음 아래로 내려간 카메라 앞에 붙박이 생물이 나타난다','먹이가 먼 곳의 정착 생물→해류 가설과 미확인 범위','빙붕·수중·생물 장면 비용 높음',.22,['https://www.bas.ac.uk/data/our-data/publication/breaking-all-the-rules-the-first-recorded-hard-substrate-sessile-benthic-community-far-beneath-an-antarctic-ice-shelf/'],'2021 실제 영상과 부착생물 확인; 영양분이 전혀 없다고 말하지 않음'),
'heatburst':('VERIFIED_EXPLAINED',[20,20,16,8,9,7],'밤에 창문을 열자 바람은 뜨겁고 온도계가 오른다','비 증발 후 하강 공기의 압축 가열','온도 변화가 자막 없이 즉시 보이기 어려움',.16,['https://www.weather.gov/abq/localfeatureheatburst'],'공기가 하강하며 압축 가열. 캐시의 단열팽창 서술은 채택하지 않음'),
'voynich':('VERIFIED_UNRESOLVED',[19,19,15,8,9,8],'책을 펼쳤는데 익숙한 글자가 하나도 없다','원본의 기호 규칙과 해독 실패를 구분','책 넘김은 가능하지만 시각 보상이 약함',.05,['https://beinecke.library.yale.edu/beinecke/collections/beinecke-cipher-voynich-manuscript'],'예일 소장 실물과 미해독 상태 확인; 해독 완료를 꾸미지 않음'),
'purr':('VERIFIED_EXPLAINED',[17,17,15,7,9,7],'가만히 있는 고양이 목이 떨린다','후두 조직의 수동 진동 실험','TTS 없는 시각 중심 영상에서 소리 현상 후킹 약함',.10,['https://www.sciencedirect.com/science/article/pii/S0960982223012307'],'2023 후두의 수동 발성 실험은 그르렁거리는 모든 이유를 설명하지 않음'),
'whale52':('VERIFIED_UNRESOLVED',[15,16,13,8,9,6],'바닷속 소리는 잡히는데 주인은 보이지 않는다','반복 신호 관측과 개체 미확인 구분','또 파형 도식 중심이 되기 쉬움',.48,['https://www.whoi.edu/oceanus/feature/a-lone-voice-crying-in-the-watery-wilderness/'],'52Hz 신호 추적 확인; 외로움이나 소통 불능은 확인되지 않음'),
'titan':('ALLEGED',[20,20,11,7,5,6],'손바닥만 한 딱정벌레의 아기 사진 칸이 비어 있다','성충 확인과 유충 정보의 공백','빈 칸을 반복하게 되어 실제 사건 부족',.08,['https://www.nhm.ac.uk/discover/what-is-the-biggest-beetle-in-the-world.html'],'성충 존재만 확인. 현재까지 유충 미발견이라는 핵심을 독립 확증하지 못해 보류'),
'mpemba':('DISPUTED',[23,23,13,8,8,9],'두 물통 중 뜨거운 쪽이 먼저 얼 듯하다','정의와 조건에 따라 비교 결과가 달라짐','얼음 EP06 및 상자 실험 EP05와 유사',.85,['https://www.nature.com/articles/srep37665'],'보편적 뜨거운 물 우선 결빙을 사실처럼 후킹하면 실패. 최근 얼음 편과 반복'),
'skull':('DEBUNKED',[19,18,14,7,8,6],'고대처럼 보이는 수정 해골에 현대 공구 흔적이 보인다','확대 관찰이 제작시대 주장을 뒤집음','정밀 수정 재질·도구흔적 확대 비용 높음',.08,['https://www.britishmuseum.org/collection/object/E_Am1898-1'],'박물관 소장품의 현대 제작 판정에 범위 제한. 모든 수정 유물을 일반화하지 않음')}
candidates=[]
for source,indices in batch.items():
 inventory=read(R/f'{source}_inventory.json');snapshot=ROOT/'research/namuwiki'/f'{source}.html'
 parent='https://namu.wiki/w/'+quote('미스터리 관련 정보'+('/'+category[source] if source!='main' else ''))
 for idx in indices:
  original=inventory[idx];key=shortlist.get((source,idx));name=original['text'].split(':')[0].strip()[:70]
  item=dict(topicId=f'namu-cache-{source}-{idx:03}',name=name,sourceUrl=parent,documentUrl=urljoin('https://namu.wiki',original['url']),category=category[source],
    sourcePosition=dict(snapshot=str(snapshot.relative_to(ROOT)),liIndex=idx,sha256=hashlib.sha256(snapshot.read_bytes()).hexdigest()),
    description=original['text'][:150],discoveredAt=stamp,lastCheckedAt=stamp,lastLiveCheckedAt=None,originalDiscoveryAt=None,
    verificationStatus='ALLEGED',verificationBasis='UNREVIEWED_CACHE_CLAIM; not a factual endorsement',interestScore=None,hookCandidates=[],
    visualPotential=None,storyPotential=None,productionCost=None,previousEpisodeSimilarity=None,rejectionReasons=[])
  # Deterministic exclusions precede the human editorial shortlist and science review.
  if idx in [2,3,6,18] and source=='listing':item['rejectionReasons'].append('기제작 또는 이미 기획된 소재와 중복')
  if source=='listing' and idx in [0,1,5,7,8,9,46]:item['rejectionReasons'].append('첫 2초 물리적 사건이 부족하고 추상 도식 의존')
  if any(w in original['text'] for w in ['사망','사상자','학살','신상','범죄']):item['rejectionReasons'].append('기존 피해 사건·민감 소재 제외 기준')
  if key:
   status,score,hook,story,cost,similarity,urls,scope=reviews[key]
   item.update(verificationStatus=status,verificationBasis=scope,scoreComponents=dict(zip(['hook25','event25','narrative20','surprise10','evidence10','feasibility10'],score)),interestScore=sum(score),visualPotential=hook,storyPotential=story,productionCost=cost,previousEpisodeSimilarity=similarity,evidenceUrls=urls,reviewKey=key)
   if sum(score)<80:item['rejectionReasons'].append('관심 점수 80 미만')
   if similarity>.7:item['rejectionReasons'].append('최근 영상과 장면/주제 유사도 높음')
   if status=='ALLEGED':item['rejectionReasons'].append('핵심 사실 독립 검증 부족')
   item['viewerAnswers']=[hook,'red_rain/zebra는 색/착륙 차이가 즉시 보임; 다른 후보는 조건 라벨 필요' if key in ['red_rain','zebra'] else '설명 보조 필요',story,cost,scope]
  elif not item['rejectionReasons']:item['rejectionReasons'].append('이번 상세 검토 10개 밖; 원문 주장 단계 보류')
  if duplicate(item,history):item['rejectionReasons'].append('Already selected in existing episode metadata')
  candidates.append(item)
assert len(candidates)==40 and sum('reviewKey' in x for x in candidates)==10
top=sorted([x for x in candidates if x.get('reviewKey') and x['previousEpisodeSimilarity']<.7 and x['verificationStatus']!='ALLEGED'],key=lambda x:x['interestScore'],reverse=True)[:5]
hooks={
'red_rain':[('흰 우산에 붉은 빗방울이 튄다','우산을 든 민수가 뒤로 물러선다','비가 빨갛다?'),('투명 병 속 붉은 입자가 바닥에 쌓인다','민수가 병을 들어 색 경계를 확인한다','색이 가라앉는다?'),('배양 접시에 조류가 자란다','민수가 현미경에서 고개를 번쩍 든다','빗물에서 자랐다?')],
'zebra':[('민무늬 말에는 파리, 줄무늬 말에는 착륙 실패','파리가 연속 접근한다','줄무늬의 뜻밖의 효과'),('민수가 말의 줄무늬 덮개를 걷는다','파리 착륙 위치가 바뀐다','무늬 하나 바꿨는데'),('파리 시점의 무늬 확대','착륙 직전 속도가 줄지 않는다','왜 못 앉을까?')],
'subice':[('어두운 바위에 붙은 생물','탐사 카메라 불빛이 켜진다','이 아래에 생명이?'),('끝없이 긴 얼음 시추공','케이블이 내려간다','빛도 없는데'),('부착생물과 먼 바다 단면','먹이 입자가 흘러온다','무엇을 먹을까?')],
'heatburst':[('밤의 온도계가 급상승','민수가 창문을 열고 놀란다','밤인데 더워진다?'),('마른 빗방울이 공중에서 사라진다','하강 바람이 퍼진다','비는 어디 갔지?'),('차갑던 바람 지표에서 가열','잎과 머리가 바람에 움직인다','뜨거운 돌풍')],
'voynich':[('읽을 수 없는 책 페이지','민수가 책을 돌려도 못 읽는다','무슨 글자지?'),('서로 다른 해독 카드','같은 문장에서 답이 갈린다','정말 풀렸을까?'),('오래된 종이와 이상한 식물 그림','페이지를 확대한다','책은 진짜인데')]
}
for x in top:
 x['hookCandidates']=[dict(HOOK_IMAGE=i,HOOK_ACTION=a,HOOK_CAPTION=c,VIEWER_GAP=x['storyPotential'],NEXT_REASON='관찰을 통해 처음 장면의 원인 또는 확인된 한계를 알게 된다') for i,a,c in hooks[x['reviewKey']]]
eligible=[x for x in top if x['interestScore']>=80 and not x['rejectionReasons']]
if not eligible:raise ValueError('No verified, sufficiently interesting, nonduplicate topic; no fallback')
selected=max(eligible,key=lambda x:x['interestScore'])
write(research_out/'candidates.json',candidates);write(research_out/'top10.json',[x for x in candidates if x.get('reviewKey')]);write(research_out/'top5_hooks.json',top)
selected['selectedHook']=0;selected['gate1']='PASS_WITH_SCOPED_FACTS';selected['scoreIsAudienceEvidence']=False
write(job/'topic.json',selected)
write(research_out/'discovery_receipt.json',dict(candidateCount=40,detailReviewCount=10,hookReviewCount=5,eligibleCount=len(eligible),selectedTopicId=selected['topicId'],snapshotRefresh='existing cache; live access unavailable',newDownloads=0,sourceMetadataPreserved=True,scoring='editorial judgment, not measured retention or an automatic quality guarantee',unreviewedStatus='ALLEGED means unverified cache claim here; held, not produced'))
print('40 candidates / 10 detailed / 5 hook sets; selected',selected['name'],selected['interestScore'])
