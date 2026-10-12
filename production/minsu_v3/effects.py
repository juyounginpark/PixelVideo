"""Deterministic editorial decisions from authored visible events; no topic logic."""
import math
from collections import Counter

RULES={
 'QUESTION':('QUESTION_POP','IMPACT_CAPTION'),
 'SURPRISE':('PUNCH_ZOOM','REACTION_BURST'),
 'REALIZATION':('OBJECT_HIGHLIGHT','PIXEL_SPARK'),
 'DISCOVERY':('PIXEL_SPARK','IMPACT_CAPTION'),
 'EXPERIMENT':('OBJECT_HIGHLIGHT','DARK_FOCUS'),
 'COMPARISON':('DATA_REVEAL',),
 'IMPACT':('PUNCH_ZOOM','IMPACT_FREEZE','IMPACT_CAPTION'),
 'REACTION':('REACTION_BURST',),
 'TIME_PASSAGE':('DATA_REVEAL',),
 'SUCCESS':('PIXEL_SPARK','IMPACT_CAPTION'),
 'FAILURE':('REACTION_BURST',),
 'TRANSITION':('TRANSITION_DIRECTOR',),
 'CONCLUSION':('IMPACT_CAPTION',)}
SOUNDS={'QUESTION':'question_blip','SURPRISE':'retro_boing','DISCOVERY':'discovery',
        'IMPACT':'soft_pop','COMPARISON':'counter_tick','SUCCESS':'achievement',
        'TIME_PASSAGE':'counter_tick','REALIZATION':'ui_pop'}
BUDGETS={'PUNCH_ZOOM':5,'PIXEL_SPARK':6,'DARK_FOCUS':2,'IMPACT_FREEZE':1}

def smooth(x):
    x=max(0,min(1,x));return x*x*(3-2*x)

def punch_scale(seconds,intensity=2):
    amount={0:0,1:.06,2:.10,3:.12}[intensity]
    if seconds<0:return 1
    if seconds<.10:return 1+amount*smooth(seconds/.10)
    if seconds<.27:return 1+amount*(1-.6*smooth((seconds-.10)/.17))
    return 1+amount*.4*(1-smooth((seconds-.27)/.33))

def pop_scale(seconds):
    if seconds<.10:return .75+.37*smooth(seconds/.10)
    return 1.12-.12*smooth((seconds-.10)/.10)

class EffectDirector:
    def compile(self,spec):
        fps=spec['fps'];duration=spec['durationFrames'];effects=[];sounds=[];notes=[];counts=Counter();seen=set();lastsound={}
        if fps<=0 or duration<=0:raise ValueError('Invalid timeline')
        end=0
        for shot in spec['shots']:
            if shot['startFrame']!=end or shot['endFrame']<=end:raise ValueError('Shot gap/overlap')
            end=shot['endFrame'];actions={a['id']:a for a in shot['actions']}
            for ev in sorted(shot.get('events',[]),key=lambda e:e['frame']):
                if ev['id'] in seen:raise ValueError('Duplicate semantic event')
                seen.add(ev['id']);frame=ev['frame'];kind=ev['type'];intensity=ev.get('intensity',1)
                if kind not in RULES or intensity not in (0,1,2,3):raise ValueError('Invalid event kind/intensity')
                action=actions.get(ev.get('actionId'))
                if not action or not action.get('visibleChange'):raise ValueError('Effect without actual visible action')
                if not shot['startFrame']<=frame<shot['endFrame'] or not action['startFrame']<=frame<action['endFrame']:raise ValueError('Event outside associated action')
                if ev['target']!=action['target']:raise ValueError('Effect target/action target mismatch')
                if intensity==0:continue
                chosen=[]
                for effect in RULES[kind]:
                    if effect=='IMPACT_CAPTION':
                        if not ev.get('text'):continue
                        if len(ev['text'].split())>5:raise ValueError('Impact text exceeds five words')
                        base=[''.join(c['lines']).replace(' ','') for c in shot.get('captions',[]) if c['startFrame']<=frame<c['endFrame']]
                        if ev['text'].replace(' ','') in base:raise ValueError('Impact repeats base caption')
                    if effect=='DARK_FOCUS' and not ev.get('focus'):continue
                    if effect=='IMPACT_FREEZE' and not ev.get('freezeAllowed'):continue
                    if effect=='DATA_REVEAL' and not ev.get('data'):
                        notes.append({'event':ev['id'],'omitted':effect,'reason':'No measured or reviewed data'});continue
                    if effect=='DATA_REVEAL' and not ev['data'].get('provenance'):raise ValueError('Data display without provenance')
                    if effect=='TRANSITION_DIRECTOR' and ev.get('transition','HARD_CUT')=='HARD_CUT':continue
                    if effect in BUDGETS and counts[effect]>=BUDGETS[effect]:
                        notes.append({'event':ev['id'],'omitted':effect,'reason':'Effect budget'});continue
                    if len(chosen)>=3:break
                    if effect=='IMPACT_FREEZE':length=round(.13*fps)
                    elif effect=='IMPACT_CAPTION':length=round(.80*fps)
                    elif effect in ('OBJECT_HIGHLIGHT','DARK_FOCUS','DATA_REVEAL'):length=round(.95*fps)
                    elif effect=='TRANSITION_DIRECTOR':length=round(.20*fps)
                    else:length=round(.55*fps)
                    if effect in ('OBJECT_HIGHLIGHT','DATA_REVEAL') and ev.get('effectDurationFrames'):
                        length=min(round(3*fps),int(ev['effectDurationFrames']))
                    row={'id':ev['id']+':'+effect,'eventId':ev['id'],'shotId':shot['id'],'type':effect,
                         'frame':frame,'endFrame':min(shot['endFrame'],frame+length),'target':ev['target'],
                         'intensity':intensity,'text':ev.get('text'),'data':ev.get('data'),
                         'transition':ev.get('transition','HARD_CUT'),'role':'primary' if not chosen else 'secondary'}
                    # A single emphasis group at any instant. Do not obscure another event.
                    overlap=[e for e in effects if e['frame']<=frame<e['endFrame'] and e['type']!='PUNCH_ZOOM']
                    if len(overlap)+len(chosen)>=3:
                        notes.append({'event':ev['id'],'omitted':effect,'reason':'Concurrent effect limit'});continue
                    chosen.append(row);counts[effect]+=1
                effects.extend(chosen)
                sound=SOUNDS.get(kind)
                if sound and chosen and frame-lastsound.get(sound,-10*fps)>=round(.8*fps):
                    sounds.append({'frame':frame,'sound':sound,'eventId':ev['id'],'event':action['visibleChange'],
                                   'gainDb':-6 if intensity<2 else -4,'duck':intensity>=2})
                    lastsound[sound]=frame
        if end!=duration:raise ValueError('Incorrect episode duration')
        timeline={'fps':fps,'durationFrames':duration,'EffectTimeline':effects,
                  'CameraEffectTimeline':[e for e in effects if e['type']=='PUNCH_ZOOM'],
                  'CaptionAnimationTimeline':[e for e in effects if e['type']=='IMPACT_CAPTION'],
                  'ParticleTimeline':[e for e in effects if e['type'] in ('PIXEL_SPARK','REACTION_BURST')],
                  'SoundEffectTimeline':sounds,'counts':dict(counts),'omissions':notes}
        self.validate(timeline);return timeline

    def validate(self,timeline):
        for e in timeline['EffectTimeline']:
            if not 0<=e['frame']<e['endFrame']<=timeline['durationFrames']:raise ValueError('Effect outside video')
        keys=[(e['frame'],e['sound']) for e in timeline['SoundEffectTimeline']]
        if len(keys)!=len(set(keys)):raise ValueError('Duplicate sound at frame')
        return True

def held_frame(frame,timeline):
    for e in timeline['EffectTimeline']:
        if e['type']=='IMPACT_FREEZE' and e['frame']<=frame<e['endFrame']:return e['frame']
    return frame

def audio_events(timeline):
    return [{**e,'time':e['frame']/timeline['fps']} for e in timeline['SoundEffectTimeline']]
