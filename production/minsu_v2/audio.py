"""Deterministic original music/SFX synthesis, stems, loudness and AAC delivery.

No TTS, web audio, samples, MIDI songs, or downloaded sound libraries.
"""
from pathlib import Path
import argparse, hashlib, json, math, re, subprocess, wave
import numpy as np
import imageio_ffmpeg

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / 'audio'
SR = 48000
FF = imageio_ffmpeg.get_ffmpeg_exe()

def write_wav(path, samples):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    a = np.asarray(samples)
    if a.ndim == 1: a = np.column_stack((a, a))
    if np.max(np.abs(a)) >= 1: raise ValueError(f'Clipping before write: {path}')
    with wave.open(str(path), 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(np.round(a * 32767).astype('<i2').tobytes())

def read_wav(path):
    with wave.open(str(path), 'rb') as w:
        assert w.getframerate() == SR and w.getsampwidth() == 2
        return np.frombuffer(w.readframes(w.getnframes()), '<i2').reshape(-1, w.getnchannels()).astype(float) / 32768

def ffmpeg(args):
    p = subprocess.run([FF, '-hide_banner', '-nostdin', *map(str,args)], capture_output=True, text=True, encoding='utf-8', errors='replace')
    if p.returncode: raise RuntimeError(p.stderr[-4000:])
    return p.stderr

def measure(path):
    log = ffmpeg(['-i',path,'-af','loudnorm=I=-19:TP=-1.2:LRA=7:print_format=json','-f','null','-'])
    data = json.loads(re.findall(r'\{[^{}]+\}',log)[-1])
    return data

def normalize(source, dest, target=-21):
    m = measure(source)
    filt = (f'loudnorm=I={target}:TP=-1.2:LRA=7:measured_I={m["input_i"]}:'
            f'measured_TP={m["input_tp"]}:measured_LRA={m["input_lra"]}:'
            f'measured_thresh={m["input_thresh"]}:linear=true:print_format=json')
    ffmpeg(['-y','-i',source,'-af',filt,'-ar',SR,'-c:a','pcm_s16le',dest])
    return measure(dest)

def tone(midi, duration, voice='pluck'):
    t = np.arange(round(duration*SR))/SR; f = 440*2**((midi-69)/12)
    if voice == 'bass':
        y = np.sin(2*np.pi*f*t) + .11*np.sin(6*np.pi*f*t)
        env = (1-np.exp(-t/.014))*np.exp(-t/1.2)
    else:
        y = np.sin(2*np.pi*f*t) + .22*np.sin(4*np.pi*f*t) + .06*np.sin(8*np.pi*f*t)
        env = (1-np.exp(-t/.004))*np.exp(-t/(.24 if voice=='pluck' else .6))
    env *= np.minimum(1,(duration-t)/.045)
    return y*env

def add(buffer, signal, start, gain, pan=0, circular=False):
    sig = signal[:,None] * np.array([math.sqrt((1-pan)/2),math.sqrt((1+pan)/2)]) * gain
    index = round(start*SR)
    if circular:
        ids=(np.arange(len(sig))+index)%len(buffer)
        np.add.at(buffer, ids, sig)
    else:
        if index<0 or index>=len(buffer): raise ValueError('Event outside timeline')
        n=min(len(sig),len(buffer)-index);buffer[index:index+n]+=sig[:n]

class MusicLibrary:
    def __init__(self): self.path=ASSETS/'catalog.json'
    def select(self, mood, track_id=None):
        if not mood:raise ValueError('Explicit episode mood required; no default subject music')
        entries=json.loads(self.path.read_text('utf-8'))['bgm']
        found=[x for x in entries if (track_id is None or x['id']==track_id) and mood in x['mood']
               and x.get('commercialUseAllowed') is True and x.get('socialPublishingAllowed') is True
               and x.get('license') and x.get('source')]
        found=[x for x in found if x.get('instrumental') is True and 90<=x.get('bpm',0)<=125
               and x.get('duration',0)>0 and (ASSETS/x.get('path','')).is_file()]
        if not found: raise ValueError('No licensed, matching BGM; no random fallback')
        return sorted(found,key=lambda x:x['id'])[0]

def generate_assets():
    ASSETS.mkdir(exist_ok=True)
    previous=json.loads((ASSETS/'catalog.json').read_text('utf-8')) if (ASSETS/'catalog.json').exists() else {}
    bpm=100; beat=60/bpm; duration=32*beat
    loop=np.zeros((round(duration*SR),2));score=[]
    # Original sparse AABA-style phrase, 8 bars. Cmaj7 / Am7 / Fmaj7 / G6.
    chords=[(48,[60,64,67,71]),(48,[60,64,67,71]),(45,[60,64,67,69]),(45,[60,64,67,69]),
            (41,[60,64,65,69]),(41,[60,64,65,69]),(43,[59,62,67,69]),(43,[59,62,67,69])]
    melody=[[76,None,79,74],[76,72,None,71],[72,None,76,79],[76,None,74,None],
            [77,None,76,72],[69,None,72,76],[74,None,71,69],[71,None,74,None]]
    rng=np.random.default_rng(41004)
    for bar,(bass,chord) in enumerate(chords):
        for j in range(4):
            at=(bar*4+j)*beat
            if j in (0,2): add(loop,tone(bass,.88,'bass'),at,.14,-.08,True)
            note=chord[(j+bar)%4]
            add(loop,tone(note,.85),at+.30,.055,(-1 if j%2 else 1)*.28,True)
            if melody[bar][j] is not None:
                n=melody[bar][j];add(loop,tone(n,1.1,'bell'),at,.075,.12,True)
                score.append({'beat':bar*4+j,'midi':n,'voice':'soft bell'})
            tt=np.arange(round(.12*SR))/SR
            if j in (0,2):
                kick=np.sin(2*np.pi*(48*tt+3*(1-np.exp(-tt*35))))*np.exp(-tt*40)*(1-np.exp(-tt*900))
                add(loop,kick,at,.105,0,True)
            else:
                noise=rng.normal(0,.23,len(tt));noise=np.convolve(noise,np.ones(5)/5,mode='same')
                click=noise*np.exp(-tt*70)*np.minimum(tt/.003,1)
                add(loop,click,at,.055,.1,True)
    raw=ASSETS/'bgm/curious_desert_100_raw.wav';write_wav(raw,loop)
    norm=ASSETS/'bgm/curious_desert_100.wav';loudness=normalize(raw,norm,-21)
    # The renderer sums note tails circularly; the loop boundary is a periodic signal.
    sfmeta=[]
    for name,dur in [('soft_pop',.16),('retro_boing',.34),('question_blip',.28),('ui_pop',.14),
                     ('discovery',1.0),('achievement',1.2),('water_drop',.24),('soft_whoosh',.35),('counter_tick',.07)]:
        t=np.arange(round(dur*SR))/SR
        if name in ('discovery','achievement'):
            y=np.zeros((len(t),2))
            notes=[72,76,79] if name=='discovery' else [67,72,76,79]
            for k,n in enumerate(notes):add(y,tone(n,.55,'bell'),k*.13,.18,k*.10-.15)
        elif name=='soft_whoosh':
            n=rng.normal(0,.3,len(t));n=np.convolve(n,np.ones(20)/20,'same')
            y=n*np.sin(np.pi*t/dur)**2*.9
        else:
            if name=='water_drop': phase=2*np.pi*(1500*t-650*t*t/dur)
            elif name=='retro_boing':phase=2*np.pi*(190*t+10*np.sin(t*31))
            elif name=='question_blip':phase=2*np.pi*(520*t+250*t*t/dur)
            elif name=='counter_tick':phase=2*np.pi*1100*t
            else:phase=2*np.pi*(580*t-250*t*t/dur)
            y=np.sin(phase)*np.exp(-t/(dur*.24))*np.minimum(t/.004,1)*np.minimum((dur-t)/.025,1)*.25
        p=ASSETS/'sfx'/f'{name}.wav';write_wav(p,y)
        sfmeta.append({'id':name,'path':str(p.relative_to(ASSETS)).replace('\\','/'),'duration':dur,
                       'license':'project-original-procedural','source':'audio.py:generate_assets','externalSamples':False,
                       'commercialUseAllowed':True,'socialPublishingAllowed':True,'creditsRequired':False})
    catalog={'bgm':[{'id':'curious_desert_100','path':'bgm/curious_desert_100.wav','mood':['exploration','observation','mechanism'],
             'bpm':bpm,'duration':duration,'loopable':True,'instrumental':True,'license':'project-original-procedural',
             'source':'audio.py:generate_assets','externalSamples':False,'creditsRequired':False,
             'commercialUseAllowed':True,'socialPublishingAllowed':True,'commercialAndSocialUse':'Original project synthesis, no third-party samples or composition',
             'measuredLUFS':float(loudness['input_i'])}], 'sfx':sfmeta,'ttsEnabled':False}
    # Upsert this generator's IDs; preserve user-added, independently licensed assets.
    for group in ('bgm','sfx'):
        owned={x['id'] for x in catalog[group]}
        catalog[group].extend(x for x in previous.get(group,[]) if x['id'] not in owned)
    (ASSETS/'catalog.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2),'utf-8')
    (ASSETS/'score.json').write_text(json.dumps({'bpm':bpm,'bars':8,'melody':score},indent=2),'utf-8')
    (ASSETS/'CREDITS.md').write_text('# MINSU original audio\n\nMusic: Curious Desert, 100 BPM. Sound effects: project procedural synthesis.\nCreated by the project synthesis code, no external samples, downloaded songs or cloned voices.\nNo third-party attribution requirement is introduced by these generated waveforms.\nSource: audio.py and score.json. This is provenance, not a guarantee of unique copyright ownership.\n','utf-8')

class AudioSynchronizer:
    def build(self, duration, events, output_dir, track_id=None,mood=None):
        if not math.isfinite(duration) or duration<=0:raise ValueError('Positive finite audio duration required')
        track=MusicLibrary().select(mood,track_id);music=read_wav(ASSETS/track['path']);used={track['id']:track}
        if duration>len(music)/SR and track.get('loopable') is not True:raise ValueError('Track cannot be looped')
        catalog=json.loads((ASSETS/'catalog.json').read_text('utf-8'))
        validate_audio_events(duration,events,catalog)
        out=Path(output_dir);out.mkdir(parents=True,exist_ok=True)
        n=round(duration*SR);bgm=np.tile(music,(math.ceil(n/len(music)),1))[:n].copy()
        env=np.ones(n);fi=min(n,round(.4*SR));fo=min(n,round(.8*SR))
        env[:fi]=np.linspace(0,1,fi);env[-fo:]=np.linspace(1,0,fo)
        duck=np.ones(n);sfx=np.zeros_like(bgm)
        registry={a['id']:a for a in catalog['sfx']};event_report=[]
        for ev in events:
            if ev['sound'] not in registry:raise ValueError('Unknown SFX')
            asset=registry[ev['sound']]
            if not (asset.get('license') and asset.get('source') and asset.get('commercialUseAllowed') is True and asset.get('socialPublishingAllowed') is True):
                raise ValueError('SFX usage permissions missing')
            used[asset['id']]=asset
            start=float(ev['time']);assert 0<=start<duration
            samples=read_wav(ASSETS/registry[ev['sound']]['path']);i=round(start*SR)
            count=min(len(samples),n-i);gain=10**(ev.get('gainDb',-3)/20)
            chunk=samples[:count].copy()
            if count<len(samples):
                fade=min(count,round(.012*SR));chunk[-fade:]*=np.linspace(1,0,fade)[:,None]
            sfx[i:i+count]+=chunk*gain
            if ev.get('duck',False):
                lo=max(0,i-round(.08*SR));hi=min(n,i+count+round(.25*SR))
                gate=np.ones(hi-lo);attack=i-lo;release=min(round(.25*SR),hi-i)
                value=10**(-4/20)
                gate[:attack]=np.linspace(1,value,attack) if attack else []
                gate[attack:]=value
                if release:gate[-release:]=np.linspace(value,1,release)
                duck[lo:hi]=np.minimum(duck[lo:hi],gate)
            event_report.append({**ev,'sampleIndex':i,'actualTime':i/SR,'syncErrorSeconds':abs(i/SR-start)})
        bgm*= (env*duck)[:,None]
        write_wav(out/'bgm.wav',bgm);write_wav(out/'sfx.wav',sfx)
        write_wav(out/'mix_raw.wav',bgm+sfx)
        normalized=normalize(out/'mix_raw.wav',out/'mix.wav',-19)
        credits=[]
        for asset in used.values():
            if asset.get('creditsRequired') and not asset.get('creditText'):raise ValueError('Required credit text is missing')
            credits.append(asset.get('creditText') or f"{asset['id']} — {asset['source']} / {asset['license']}")
        (out/'CREDITS.md').write_text('# Audio used in this export\n\n'+'\n\n'.join(credits)+'\n','utf-8')
        provenance=[{**a,'sha256':hashlib.sha256((ASSETS/a['path']).read_bytes()).hexdigest()} for a in used.values()]
        (out/'used_audio.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2),'utf-8')
        # Check genuine periodic boundary against neighboring sample differences.
        seam=float(np.max(np.abs(music[0]-music[-1])))
        typical=float(np.quantile(np.abs(np.diff(music,axis=0)),.999))
        windows=[float(np.sqrt(np.mean(bgm[i:i+SR//2]**2))) for i in range(SR//2,n-SR,SR//2)]
        if not windows:windows=[float(np.sqrt(np.mean(bgm**2)))]
        report={'duration':duration,'sampleRate':SR,'track':track,'events':event_report,
                'stems':['bgm.wav','sfx.wav'],'ttsEnabled':False,'duckDb':4,'fadeIn':.4,'fadeOut':.8,
                'bgmMeasurement':measure(out/'bgm.wav'),'mixMeasurement':normalized,
                'loopBoundaryStep':seam,'loopNeighborP999Step':typical,
                'loopClickCheckPassed':seam<=max(.002,typical*1.5),
                'minimumHalfSecondBgmRMS':min(windows),'bgmCoveragePassed':all(v>.0001 for v in windows),
                'peakPassed':float(normalized['input_tp'])<=-1,
                'auditoryReview':'Not yet listened to; waveform/loudness checks are not a listening test.'}
        (out/'audio_qa.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf-8')
        if not report['peakPassed'] or not report['loopClickCheckPassed']:raise RuntimeError('Audio QA failed')
        return out/'mix.wav'

def validate_audio_events(duration,events,catalog):
    """Read-only preflight before synthesis/file writes; preserves authored timing."""
    registry={a['id']:a for a in catalog['sfx']}
    for ev in events:
        t=ev.get('time',float('nan'));gain=ev.get('gainDb',-3)
        if not math.isfinite(t) or not 0<=t<duration:raise ValueError('SFX outside timeline')
        if not math.isfinite(gain) or not -60<=gain<=0:raise ValueError('SFX gain must be -60..0 dB')
        if not ev.get('event'):raise ValueError('SFX needs an associated visible event')
        asset=registry.get(ev.get('sound'))
        if not asset:raise ValueError('Unknown SFX')
        if not (asset.get('license') and asset.get('source') and asset.get('commercialUseAllowed') is True and asset.get('socialPublishingAllowed') is True):raise ValueError('SFX usage permissions missing')
        if not (ASSETS/asset['path']).is_file():raise ValueError('Missing SFX file')
        if asset.get('creditsRequired') and not asset.get('creditText'):raise ValueError('Required credit text is missing')
    return True


def mux(video, mix, output):
    # Copy video bit-for-bit: no caption/cut/frame timing change.
    ffmpeg(['-y','-i',video,'-i',mix,'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k',
            '-ar',SR,'-ac','2','-movflags','+faststart','-shortest',output])
    ffmpeg(['-v','error','-i',output,'-f','null','-'])
    m=measure(output)
    if float(m['input_tp'])>-1: raise RuntimeError(f'AAC peak exceeds -1 dBTP: {m}')
    return m

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--video',type=Path);p.add_argument('--spec',type=Path);p.add_argument('--output',type=Path)
    p.add_argument('--track');p.add_argument('--mood');p.add_argument('--generate-assets',action='store_true')
    args=p.parse_args()
    if not args.video and not args.generate_assets:p.error('Specify --generate-assets or an existing video/spec/output and explicit mood')
    if args.video and not (args.spec and args.output and args.mood):p.error('--video requires --spec, --output and --mood')
    if args.generate_assets:generate_assets()
    if args.video:
        spec=json.loads(args.spec.read_text('utf-8'))
        mix=AudioSynchronizer().build(spec['duration'],spec['audioEvents'],ROOT/'audio_mix',args.track,args.mood)
        print(json.dumps(mux(args.video,mix,args.output),indent=2))
    else:print('AUDIO_ASSETS_READY')
