"""Validate one structured episode response; never approve aesthetic gates by counts."""
from common import *

ROUTES={
 'VERIFIED_EXPLAINED':['event','clues','mechanism','understanding'],
 'VERIFIED_UNRESOLVED':['observation','anomaly','evidence_and_hypotheses','unknowns'],
 'DISPUTED':['event','competing_explanations','evidence','current_dispute'],
 'DEBUNKED':['claim','verification','why_believed','actual_conclusion']}

def episode_brief(topic,evidence,goal,new_assets):
 if topic['verificationStatus'] not in ROUTES:raise ValueError('ALLEGED topics are held')
 if topic['interestScore']<80 or topic['rejectionReasons']:raise ValueError('Topic gate failed')
 if not evidence:raise ValueError('Independent source review required')
 brief=dict(topicId=topic['topicId'],sourcePosition=topic['sourcePosition'],verificationStatus=topic['verificationStatus'],evidence=evidence,videoGoal=goal,newAssets=new_assets,storyRoute=ROUTES[topic['verificationStatus']],commonVersions={p.stem:sha(p) for p in (R/'config').glob('*.json')},responseContract='One JSON: Story Map, 3 visual hook options, all SceneSpecs, localized captions and event cues. Do not make one request per shot.')
 profile=R/'experiment/profile.json';brief['commonVersions']['EXPERIMENT_PROFILE']=sha(profile)
 brief['experimentContract']={'profile':str(profile.relative_to(ROOT)),'version':read(profile)['version'],'required':['object states with units, definition and evidence','operation completion before value update','same concept transferred to another object','conclusion answers initial question'],'numericKinds':read(profile)['numericKinds'],'noInventedMeasurements':True,'physicsAndEditorialReviewRequired':True}
 return brief

def story_checks(spec):
 validation(spec);errors=[];warnings=[]
 if len(spec.get('storyMap',{}))!=4:errors.append('Four narrative stages required')
 if not all(spec['hook'].get(k) for k in ['HOOK_IMAGE','HOOK_ACTION','HOOK_CAPTION','VIEWER_GAP','NEXT_REASON']):errors.append('Incomplete visual hook')
 total=spec['durationFrames'];abstract=sum(s['endFrame']-s['startFrame'] for s in spec['shots'] if s.get('abstractDiagram',s['sceneType']=='MACRO_SCENE'))
 if abstract/total>config('SCENE_SCHEMA').get('maxAbstractFraction',.35):warnings.append('Abstract screen time requires editorial review')
 last=None
 for s in spec['shots']:
  if not s.get('newInformation') or not s.get('scientificMeaning'):errors.append(s['id']+' lacks causal information')
  if s['endFrame']-s['startFrame']>150:warnings.append(s['id']+' >5 seconds; inspect meaningful change')
  signature=(s['phase'],s['cameraPlan']['preset'])
  if signature==last:warnings.append(s['id']+' repeats composition')
  last=signature
 if spec.get('experimentStory'):
  from experiment.state import validate_story,validate_object
  try:
   validate_story(spec['experimentStory'])
   for obj in spec.get('experimentObjects',[]):validate_object(obj)
   if not spec.get('experimentObjects'):errors.append('Experiment story needs object state records')
  except ValueError as exc:errors.append(str(exc))
 return dict(errors=errors,warnings=warnings,abstractFraction=abstract/total,automaticEditorialPass=False)

if __name__=='__main__':
 topic=read(R/'ep08/topic.json');s=read(R/'ep08/episode.json');write(R/'ep08/story_checks.json',story_checks(s))
 write(R/'ep08/compact_brief.json',episode_brief(topic,s['science'],'사건을 따라 2001 시료의 붉은 색 원인과 아직 모르는 점을 이해',['white umbrella','rain sample jar','microscope','culture dish','bark sample','warm courtyard','warm laboratory']))
