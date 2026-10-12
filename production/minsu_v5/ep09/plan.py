from pathlib import Path
from datetime import datetime,timezone,timedelta
import sys,requests
J=Path(__file__).resolve().parent;R=J.parent;sys.path.insert(0,str(R))
from common import read,write,sha,ROOT
if (J/'episode.json').exists():raise ValueError('Existing episode selection/story is preserved. Use pipeline.py to render or an explicit revision script to edit.')
topic=read(J/'topic.json');assert topic['topicId']=='namu-cache-listing-063'
now=datetime.now(timezone(timedelta(hours=9))).isoformat()
log=ROOT/'PROMPT_LOG.md'
if '## P-050 — EP09 줄무늬 착륙 실험 콘티' not in log.read_text('utf-8'):
 with log.open('a',encoding='utf-8') as f:f.write('\n\n## P-050 — EP09 줄무늬 착륙 실험 콘티\n'+now+'\n실행 전 기록. 기존 캐시 li63의 얼룩말 줄무늬,86점. 36초9컷. 민무늬와 줄무늬에 다가온 흡혈등에가 다르게 착륙하는 사건으로 시작한다. 민수가 같은 말의 덮개를 바꾸며 냄새/동물 차이 가설을 검사한다. 2019 연구의 7마리·검정/흰색/줄무늬3덮개 조건을 숫자로 표시하고 실제 착륙률은 임의 생성하지 않는다. 가까이 와서 착륙하는 단계가 달라지는 슬로모션 모식도→체크무늬에서도 효과라는 반전→2023 연구의 선명한/옅은 대비 비교→큰 검은 영역을 작게 나누는 설명은 가설로 표시→처음 말로 돌아와 착륙 감소와 미확인 시각 기제를 구분해 끝낸다. 모형 파리 경로는 실제 궤적 복제가 아니며 크기·시간을 확대했다. 공통 프레임에 3개 실험 챕터, 노랑 질문/예상, 민트 확인 결과, 보라 가설, 흰색 설명. 민수는 관찰·덮개 씌우기·비교·발견 행동을 수행한다. 현장 연구를 수행한 실존 인물로 표현하지 않는다. 로컬 음악의 발견 직전 강약과 행동 시점 SFX, 무TTS, 별도영문판.\n')
urls={'study2019':'https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0210831','study2023':'https://pmc.ncbi.nlm.nih.gov/articles/PMC10088525/','university2019':'https://www.bristol.ac.uk/news/2019/february/zebra-stripes.html'}
sources=[]
for key,url in urls.items():
 p=J/'research'/f'{key}.html';p.parent.mkdir(exist_ok=True)
 if not p.exists():
  response=requests.get(url,timeout=45);response.raise_for_status();p.write_bytes(response.content)
 sources.append({'id':key,'url':url,'snapshot':str(p.relative_to(ROOT)),'sha256':sha(p)})
claims=[{'id':'C1','claim':'Striped coats reduced horsefly landings relative to uniform coats.','source':'study2019','location':'Study 2 and Coat experiment results','conditions':'7 domestic horses, three commercial coats worn in randomized order; materials were not standardized.','notClaimed':'all flies, total protection or a universal effect size'},
 {'id':'C2','claim':'Approaching flies failed to decelerate normally near zebra pelage in study videos.','source':'study2019','location':'Flight trajectories results and Fig3','conditions':'2019 sampled captive animals; animation is explanatory, not measured tracks.','notClaimed':'known neural illusion or every trajectory'},
 {'id':'C3','claim':'Checked patterns can reduce landings; parallel stripes are not required.','source':'study2023','location':'Introduction describing How et al2020','conditions':'patterned coats on domestic horses','notClaimed':'all check patterns repel all insects'},
 {'id':'C4','claim':'High contrast stripes deterred landings more effectively than lightly contrasting stripes in the study.','source':'study2023','location':'Abstract, contrast experiment','conditions':'identically arranged coat patterns with varied contrast','notClaimed':'human visual contrast equals fly perception'},
 {'id':'C5','claim':'Small dark patches are a proposed explanation; the full visual mechanism remains unresolved.','source':'study2023','location':'Abstract and discussion working hypothesis','conditions':'hypothesis rather than definitive neural mechanism','notClaimed':'proved sole evolutionary cause'}]
write(J/'research/claim_ledger.json',{'sources':sources,'claims':claims,'reviewedAt':now,'sourceIndexPreserved':True})
story={'기':'파리는 민무늬에는 앉지만 줄무늬에서는 착륙을 놓친다.','승':'같은 말의 덮개만 바꿔 관찰해 동물 차이와 무늬 효과를 분리한다.','전':'차이는 가까운 착륙 단계. 체크무늬와 강한 대비도 효과를 보여 단순 줄무늬 착시만으로 설명할 수 없음을 발견한다.','결':'착륙 감소는 확인됐지만 시각 기제는 연구 중. 처음 장면의 보호 효과를 이해한다.'}
rows=[
 ('hook','기','1. 뜻밖의 착륙','A strange landing','SURPRISE',['무늬만 다른데','착륙이 달라진다'],['Same approach.','Different landing.'],'plain','stripe','HOOK',38,'파리가 한쪽에 앉고 다른 쪽에서 방향을 바꾼다','왜 한쪽만 못 앉을까?','흡혈등에의 착륙 차이'),
 ('coat','승','2. 같은 말로 시험','Same horse, new coat','POINT',['냄새 때문일까?','같은 말에 덮개만 교체'],['Could it be the smell?','Change only the coat.'],'plain','stripe','CLUE',70,'민수가 덮개를 내려 말의 몸통을 가린다','동물이 달라서 그런 걸까?','동물 차이를 통제하는 덮개 실험'),
 ('trial','승','2. 같은 말로 시험','Same horse, new coat','OBSERVE',['검정·흰색보다','줄무늬에 착륙이 적었다'],['Fewer landings on stripes','than black or white coats.'],'white','stripe','CLUE',66,'두 덮개의 비행과 착륙 결과를 비교한다','덮개를 바꾸면 결과도 달라질까?','2019실험의 7마리·3종덮개 조건과 착륙감소'),
 ('macro','전','3. 마지막 순간','The final approach','EXPLAIN',['멀리서 피하는 게 아니다','차이는 가까운 착륙 단계'],['They still approach.','The difference is up close.'],'plain','stripe','NONE',60,'옆면 확대에서 회색 쪽은 감속해 앉고 줄무늬 쪽은 지나친다','언제 비행이 달라질까?','다가옴과 안정된 착륙은 다른 사건'),
 ('check','전','4. 줄무늬만 될까?','Only parallel stripes?','DISCOVER',['체크무늬에서도','착륙이 줄었다!'],['Checks reduced','landings too!'],'plain','check','DISCOVERY',62,'민수가 체크덮개를 펼치고 접근한 파리가 궤도를 바꾼다','평행한 줄이 꼭 필요할까?','체크무늬 효과는 평행줄만의 착시 설명에 반례'),
 ('contrast','전','5. 선명함을 바꾸면','Change the contrast','POINT',['옅은 줄무늬보다','선명한 흑백 대비가 효과적'],['High contrast worked better','than faint stripes.'],'faint','stripe','CLUE',62,'같은 줄 배치의 대비만 다른 두 덮개에 접근한 파리를 비교한다','무늬의 어떤 부분이 중요할까?','2023연구의 대비조건 차이'),
 ('patch','전','5. 선명함을 바꾸면','Change the contrast','THINK',['큰 검은 영역을','작게 나눈 덕분일까?'],['Do smaller dark patches','make the difference?'],'plain','stripe','NONE',55,'넓은 검은 표면 위에 흰 구획이 드러나 작은 패치로 분할된다','착륙 표적이 작아지는 걸까?','큰 검은 패치를 없애는 설명은 연구가설'),
 ('return','결','6. 처음 장면 다시 보기','Back to the first scene','CELEBRATE',['줄무늬는 흡혈등에의','착륙을 줄이는 효과가 있다'],['Stripes can reduce','horsefly landings.'],'plain','stripe','PAYOFF',64,'처음 두 말을 다시 보여 주고 민수가 비교결과를 가리킨다','처음 이상한 장면은 무엇을 뜻했나?','확인된 효과를 처음 사건에 적용'),
 ('ending','결','6. 처음 장면 다시 보기','Back to the first scene','OBSERVE',['정확한 시각 기제는 연구 중','완벽한 방패는 아니다'],['The visual mechanism is still studied.','It is not a perfect shield.'],'stripe','check','NONE',60,'무늬에 접근해 실제로 앉는 파리 하나도 보여 과장을 막는다','어디까지 확인됐을까?','효과와 미확인 원리·예외를 구분')]
shots=[]
for i,(phase,role,chapter,chapterEn,action,ko,en,left,right,fx,ef,visual,q,info) in enumerate(rows):
 shots.append({'id':f'S{i+1:02}','startFrame':i*120,'endFrame':(i+1)*120,'phase':phase,'narrativeRole':role,'sceneType':'EVENT_SCENE' if i==0 else 'COMPARISON_SCENE','primarySubject':'horses and horsefly','viewerQuestion':q,'newInformation':info,'visualAction':visual,'scientificMeaning':info,'characterEmotion':action,'cameraPlan':{'purpose':visual,'preset':'MACRO' if phase in ['macro','patch'] else 'PAIR' if phase!='coat' else 'SINGLE'},'captionPlan':{'ko':ko,'en':en},'chapter':chapter,'chapterEn':chapterEn,'scene':{'action':action,'left':left,'right':right},'emphasisEvent':{'preset':fx,'frame':ef,'target':'right'},'nextShotConnection':rows[i+1][-2] if i<8 else '처음 질문의 범위 안에서 선택하며 끝낸다','claimIds':[['C1'],['C1'],['C1'],['C2'],['C3'],['C4'],['C5'],['C1'],['C5']][i],'diagramDisclaimer':True})
spec={'episode':'EP09','topicId':topic['topicId'],'verificationStatus':'VERIFIED_EXPLAINED','title':'파리는 왜 못 앉을까?','titleEn':'Why miss the landing?','durationFrames':1080,'fps':30,'storyMap':story,'shots':shots,'source':topic['sourcePosition'],'science':claims,'commonProfile':'straw-game-1.0.0','audio':{'tts':False,'track':'curious_desert_100','mood':'observation','energy':[{'time':0,'db':-2},{'time':4,'db':-5},{'time':12,'db':-4},{'time':17.7,'db':-18},{'time':18.05,'db':0},{'time':24,'db':-5},{'time':28,'db':-2},{'time':34,'db':-6}]}}
if not (J/'episode.json').exists():write(J/'episode.json',spec)
write(J/'gates.json',{'TOPIC':{'decision':'PASS_WITH_SCOPED_FACTS','score':86,'evidence':'research/claim_ledger.json'},'STORY':{'decision':'PASS','reason':'사건→동일동물비교→착륙단계→체크반례→대비→가설→결론'},'STORYBOARD':{'decision':'PASS','reason':'실물역할극/비교/근접비행/덮개전환/패치확대를 구분'},'ART_PREVIEW':{'decision':'PENDING'},'EDITING_PREVIEW':{'decision':'PENDING'},'FINAL_QA':{'decision':'PENDING'}})
print('EP09 story compiled, 36 seconds / 9 shots')
