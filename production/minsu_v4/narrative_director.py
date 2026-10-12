"""Topic-agnostic structured story compiler; never invents a missing source/topic."""
from common import R,ROOT,read,write,sha,validation,digest,config
class NarrativeDirector:
    def compile(self,episode):
        technical=validation(episode)
        if set(s['narrativeRole'] for s in episode['shots'])!={'기','승','전','결'}:raise ValueError('Incomplete story arc')
        if episode['shots'][0]['narrativeRole']!='기' or episode['shots'][-1]['narrativeRole']!='결':raise ValueError('Opening/ending missing')
        changes=[]
        for a,b in zip(episode['shots'],episode['shots'][1:]):
            if a['primarySubject']==b['primarySubject'] and a['newInformation']==b['newInformation']:raise ValueError('Redundant consecutive shots')
            changes.append(dict(fromShot=a['id'],toShot=b['id'],reason=a['nextShotConnection']))
        versions={p.stem:sha(p) for p in (R/'config').glob('*.json') if p.stem!='TEMPLATE_REGISTRY'}
        # This is the sole episode payload; shared master specifications stay referenced.
        payload={k:episode[k] for k in ('topicId','evidence','goal','newAssets','storyMap','shots','configVersion','science','source')}
        payload['sharedConfigHashes']=versions
        return dict(episodePayload=payload,shotConnections=changes,technical=technical,requiresEditorialReview=True,externalLLMRequestsMade=0)
if __name__=='__main__':
    s=read(R/'ep07/episode.json');result=NarrativeDirector().compile(s);write(R/'ep07/episode_request.json',result['episodePayload']);write(R/'ep07/narrative_qa.json',{k:v for k,v in result.items() if k!='episodePayload'})
    text='# EP07 V4 — Story Map / 사건 콘티\n\n'
    text+='기존 공급 8번 암흑물질, 한국어 주 자막+영어 보조 자막, 총 '+str(s['durationFrames']/30)+'초. 공통 설정 4.0.0.\n\n'
    for k,v in s['storyMap'].items():text+=f'- **{k}**: {v}\n'
    for x in s['shots']:
        text+=f'\n## {x["id"]} / {x["startFrame"]/30:.2f}–{x["endFrame"]/30:.2f}초\n\n'
        for k in config('SCENE_SCHEMA')['requiredShotFields']:
            value=x[k]
            if isinstance(value,(dict,list)):
                import json
                value=json.dumps(value,ensure_ascii=False)
            text+=f'- **{k}**: {value}\n'
    (R/'ep07/STORYBOARD.md').write_text(text,'utf-8');print('One structured episode payload compiled; no per-shot LLM requests')
