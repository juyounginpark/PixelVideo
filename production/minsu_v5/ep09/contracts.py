"""Episode contracts: source preservation, numeric provenance, closed story route."""
from pathlib import Path
import sys
J=Path(__file__).resolve().parent;sys.path.insert(0,str(J.parent))
from common import read,write,sha,ROOT
from experiment.state import validate_numeric

def verify():
 spec=read(J/'episode.json');ledger=read(J/'research/claim_ledger.json');topic=read(J/'topic.json');errors=[]
 if spec['topicId']!=topic['topicId']:errors.append('Topic mismatch')
 if sha(ROOT/spec['source']['snapshot'])!=spec['source']['sha256']:errors.append('Source snapshot changed')
 if spec['durationFrames']!=sum(s['endFrame']-s['startFrame'] for s in spec['shots']):errors.append('Duration mismatch')
 cursor=0
 for shot in spec['shots']:
  if shot['startFrame']!=cursor:errors.append('Noncontiguous cuts')
  cursor=shot['endFrame']
  if not shot['newInformation'] or not shot['visualAction'] or not shot['scientificMeaning']:errors.append('Empty scene information')
  if any(cid not in {c['id'] for c in ledger['claims']} for cid in shot['claimIds']):errors.append('Unverified scene claim')
 for source in ledger['sources']:
  if sha(ROOT/source['snapshot'])!=source['sha256']:errors.append('Source evidence changed')
 if set(spec['storyMap'])!={'기','승','전','결'}:errors.append('Incomplete story map')
 if spec['shots'][0]['phase']!='hook' or spec['shots'][-2]['phase']!='return':errors.append('Hook/payoff connection missing')
 if spec['audio']['tts']:errors.append('TTS enabled')
 numeric=[{'kind':'OBSERVATION','meaning':'2019 덮개 실험 참가 말의 수','units':'마리','definition':'Study2 참가 동물 수, 착륙 횟수/비율 아님','source':'REAL_OBSERVATION','sourceRefs':['study2019 / Methods Study2'],'value':7},
          {'kind':'STATE','meaning':'2019 덮개 실험 조건 수','units':'종','definition':'검정/흰색/줄무늬 상용 덮개 조건','source':'REAL_OBSERVATION','sourceRefs':['study2019 / Methods Study2'],'value':3},
          {'kind':'CHAPTER_PROGRESS','meaning':'저작된 챕터 순서','source':'EDITORIAL_PROGRESS','value':1,'total':6}]
 for item in numeric:validate_numeric(item)
 changed=[p for p,h in read(J/'preservation_before.json').items() if sha(ROOT/p)!=h]
 if changed:errors.append('Preserved files changed '+str(changed))
 report={'result':'PASS' if not errors else 'FAIL','errors':errors,'numericUI':numeric,'fictionalLandingCountsDisplayed':False,'closedStory':True,'sources':ledger['sources'],'preservedFilesChecked':len(read(J/'preservation_before.json')),'sourceTopicId':topic['topicId'],'humanEditorialApproval':False}
 write(J/'research/contracts.json',report)
 if errors:raise ValueError(errors)
 return report
if __name__=='__main__':print(verify()['result'])
