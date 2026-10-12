from pathlib import Path
import json,hashlib,os
R=Path(__file__).resolve().parent;ROOT=R.parents[1];RENDERER_VERSION='5.0.1'
def read(p):return json.loads(Path(p).read_text('utf-8'))
def write(p,d):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_suffix(p.suffix+'.tmp');tmp.write_text(json.dumps(d,ensure_ascii=False,indent=2),'utf-8');os.replace(tmp,p)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(d):return hashlib.sha256(json.dumps(d,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
def config(n):return read(R/'config'/f'{n}.json')
def native_key(s,size):
 return digest(dict(sceneSpecHash=digest({k:s[k] for k in ['phase','scene','cameraPlan']}),length=s['endFrame']-s['startFrame'],event=[s['emphasisEvent']['frame'],config('EFFECT_LIBRARY')['presets'][s['emphasisEvent']['preset']]['punch']],assetVersion=sha(R/'rain_scene.py'),materialVersion=sha(R/'art_v5.py'),shaderVersion=sha(R/'art_v5.py'),characterVersion=sha(R/'character_director.py'),cameraVersion=config('CAMERA_PRESETS'),rendererVersion=[RENDERER_VERSION,sha(R/'render.py')],reusedModel=sha(R.parent/'minsu_v2/design_system.py'),size=size,style=config('STYLE_SPEC')))
def validation(spec):
 errors=[];cursor=0
 if spec['verificationStatus']=='ALLEGED':errors.append('Unverified alleged subject is on hold')
 if spec['shots'][0]['sceneType']!='EVENT_SCENE':errors.append('Opening must show a physical event')
 for s in spec['shots']:
  for k in config('SCENE_SCHEMA')['requiredShotFields']:
   if not s.get(k):errors.append(s['id']+'.'+k)
  if s['startFrame']!=cursor or s['endFrame']<=cursor:errors.append('timeline '+s['id'])
  cursor=s['endFrame']
  if s['scene']['action'] not in config('CHARACTER_LIBRARY')['actions']:errors.append('action')
  for c in s['captionPlan']+s['labels']:
   if not 0<=c['start']<c['end']<=s['endFrame']-s['startFrame']:errors.append('caption timing')
   if len(c['lines'])>2 or len(c['english'])>2:errors.append('long caption')
 if cursor!=spec['durationFrames']:errors.append('duration')
 source=spec['source'];path=ROOT/source['snapshot']
 if sha(path)!=source['sha256']:errors.append('source snapshot changed')
 if spec['audio']['tts']:errors.append('TTS')
 if errors:raise ValueError(errors)
 return dict(schema='PASS',editorialApproval=False)
