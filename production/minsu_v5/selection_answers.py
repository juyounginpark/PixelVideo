from common import *
keys=['firstTwoSeconds','visibleOddityWithoutTitle','concreteEvent','newMiddleClue','expectationDifference','takeaway','productionFeasibility','similarityToPrevious']
specific=['흰 우산에 붉은 빗방울이 떨어지고 얼룩이 늘어난다.','일반적인 무색 빗물과 달리 우산에 붉은 색이 남는다.','비를 모은 병에서 입자가 가라앉고 배양체가 자란다.','색을 띤 입자가 가라앉으며 배양에서 조류가 확인된다.','물 자체의 색처럼 보였지만 조사 결과 생물 입자가 색을 만든다.','2001 조사 시료의 색 원인은 조류 포자. 대량 공중 유입 과정은 미확인.','기존 민수·픽셀 재질·폰트·오디오를 재사용하고 우산·병·배양 접시를 제작할 수 있다.','얼음·견과·은하와 달리 야외 사건→채집→미세 관찰의 구조. 최근 에피소드와 낮은 유사성.']
for name in ['candidates','top10','top5_hooks']:
 p=R/'research'/f'{name}.json';rows=read(p)
 for t in rows:
  if 'reviewKey' not in t:continue
  if t['reviewKey']=='red_rain':answers=specific
  else:answers=[t['visualPotential'],'후킹 시안의 실제 행동으로 평가. 현상 자체가 보이지 않는 소재는 점수 감점.',t['visualPotential'],t['storyPotential'],t['verificationBasis'],t['verificationBasis'],t['productionCost'],str(t['previousEpisodeSimilarity'])+' — 제작 이력 비교에 대한 편집자 판단']
  t['viewerAnswers']=dict(zip(keys,answers))
 write(p,rows)
p=R/'ep08/topic.json';s=read(p);s['viewerAnswers']=dict(zip(keys,specific));write(p,s)
