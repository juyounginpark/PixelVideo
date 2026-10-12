from pathlib import Path
import json,hashlib,os
R=Path(__file__).resolve().parent;ROOT=R.parents[1]
RENDERER_VERSION='5.0.1'
def read(p):return json.loads(Path(p).read_text('utf-8'))
def write(p,d):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_suffix(p.suffix+'.tmp')
    tmp.write_text(json.dumps(d,ensure_ascii=False,indent=2),'utf-8');os.replace(tmp,p)
def digest(data):return hashlib.sha256(json.dumps(data,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def config(name):return read(R/'config'/f'{name}.json')
def dependencies(names):return {x:sha(R/x) for x in names}
def native_key(shot,size):
    # Absolute start time is excluded: this director evaluates all motion in shot-local time.
    scene={k:shot[k] for k in ('phase','scene','cameraPlan')}
    event=shot['emphasisEvent'];preset=config('EFFECT_PRESETS')['presets'][event['preset']]
    scene['cameraEvent']={k:event[k] for k in ('frame','target')};scene['cameraEvent']['punch']=preset['cameraPunch']
    scene['length']=shot['endFrame']-shot['startFrame']
    if shot['phase'] in ('observe','fit','conclusion'):scene['characterDirectorVersion']=sha(R/'character_director.py')
    return digest(dict(sceneSpecHash=digest(scene),assetVersion=sha(R/'galaxy_scene.py'),materialVersion=sha(R/'art_v4.py'),shaderVersion=sha(R/'art_v4.py'),cameraVersion=digest(config('CAMERA_PRESETS')),rendererVersion=[RENDERER_VERSION,sha(R/'render.py')],characterVersion=sha(R.parent/'minsu_v2/design_system.py'),baseGeometryVersion=sha(R.parent/'minsu_v2/art.py'),legacyMaterials=sha(R.parent/'minsu_v31/style.py'),legacyEngine=sha(R.parent/'minsu_v2/engine.py'),size=size,style=config('STYLE_SPEC')))
def validation(spec):
    schema=config('SCENE_SCHEMA');errors=[]
    for field in schema['requiredStoryMap']:
        if not spec.get('storyMap',{}).get(field):errors.append('storyMap.'+field)
    for field in schema['requiredScience']:
        if not spec.get('science',{}).get(field):errors.append('science.'+field)
    cursor=0;infos=set()
    for s in spec['shots']:
        for k in schema['requiredShotFields']:
            if not s.get(k):errors.append(s['id']+'.'+k)
        if s['startFrame']!=cursor or s['endFrame']<=cursor:errors.append('noncontiguous '+s['id'])
        n=s['endFrame']-s['startFrame'];cursor=s['endFrame']
        if n>150:errors.append('requires >5s explicit change review '+s['id'])
        if s['newInformation'] in infos:errors.append('duplicate information '+s['id'])
        infos.add(s['newInformation'])
        if not 0<=s['emphasisEvent']['frame']<n:errors.append('event outside shot '+s['id'])
        for c in s['captionPlan']:
            if not c.get('english'):errors.append('missing English '+s['id'])
            if (c['end']-c['start'])/30<len(''.join(c['lines']))/11:errors.append('insufficient reading time '+s['id'])
    if cursor!=spec['durationFrames']:errors.append('duration mismatch')
    source=spec['source'];p=ROOT/source['path']
    if sha(p)!=source['sha256'] or source['name'] not in p.read_text('utf-8'):errors.append('source changed/missing')
    if spec['audio']['tts']:errors.append('TTS must stay disabled')
    if errors:raise ValueError(errors)
    return {'schema':'PASS','sourceHash':'PASS','shots':len(spec['shots']),'editorialApproval':False}
