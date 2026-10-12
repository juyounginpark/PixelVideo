"""Fail on incomplete authored plans; flags are not a visual quality score."""
from collections import Counter

FIELDS=('StoryBeat','NewInformation','PrimaryVisualEvent','ViewerQuestion',
        'CharacterReaction','CameraPurpose','CaptionRole','EmphasisEvent','TransitionReason')
ROLES={'HOOK_TITLE','EXPLANATION_CAPTION','IMPACT_CAPTION','MICRO_LABEL','FACT_PANEL','RESULT_TITLE'}

def validate(spec):
    previous=0;seen_ids=set();warnings=[];modes=[];roles=Counter()
    for shot in spec['shots']:
        if shot['id'] in seen_ids:raise ValueError('Duplicate shot ID')
        seen_ids.add(shot['id'])
        if shot['startFrame']!=previous or shot['endFrame']<=previous:raise ValueError('Shot coverage has a gap, overlap or empty interval')
        for field in FIELDS:
            if not isinstance(shot.get(field),str) or not shot[field].strip():raise ValueError(f'{shot["id"]} requires {field}')
        if shot['StoryBeat'] not in ('기','승','전','결'):raise ValueError('Unrecognized story beat')
        if shot['CaptionRole'] not in ROLES:raise ValueError('Unrecognized primary caption role')
        if not shot.get('actions'):raise ValueError('Shot must declare a visible action')
        for item in shot['typography']:
            if item['role'] not in ROLES:raise ValueError('Unrecognized typography role')
            if not shot['startFrame']<=item['startFrame']<item['endFrame']<=shot['endFrame']:raise ValueError('Caption outside its shot')
            text=' '.join(item['lines'])
            if not text.strip():raise ValueError('Empty typography')
            if any(word not in text for word in item.get('highlight',[])):raise ValueError('Highlight is absent from caption')
            roles[item['role']]+=1
        if modes and modes[-1]['information']==shot['NewInformation']:
            warnings.append({'shot':shot['id'],'reason':'Same stated new information as previous shot; visual review required'})
        modes.append({'shot':shot['id'],'mode':shot['visualMode'],'frames':shot['endFrame']-shot['startFrame'],'information':shot['NewInformation']})
        if len(modes)>=3 and len({m['mode'] for m in modes[-3:]})==1:
            warnings.append({'shot':shot['id'],'reason':'Three consecutive shots share visual mode; review action/information changes'})
        previous=shot['endFrame']
    if previous!=spec['durationFrames']:raise ValueError('Shots do not cover the whole episode')
    if not spec.get('source',{}).get('local'):raise ValueError('Existing source provenance required; no fallback topic')
    if not spec.get('scientificSources'):raise ValueError('Scientific claims require primary sources')
    return {'shotCount':len(seen_ids),'durationFrames':previous,'requiredFields':list(FIELDS),'typographyRoles':dict(roles),'modes':modes,'warnings':warnings,'visualApproval':False}
