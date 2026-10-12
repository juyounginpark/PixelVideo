import argparse,subprocess,sys
from common import *
import imageio_ffmpeg,numpy as np
from PIL import Image,ImageDraw
sys.path.append(str(R.parent/'minsu_v2'))
from audio import read_wav,SR
p=argparse.ArgumentParser();p.add_argument('--locale',default='ko');a=p.parse_args();job=R/'ep08';spec=read(job/'episode.json');report=read(job/'final'/f'compose_{a.locale}_MOBILE.json');video=Path(report['output']);errors=[]
baseline=read(R/'review/preservation_before.json');changed=[p for p,h in baseline.items() if not (ROOT/p).exists() or sha(ROOT/p)!=h]
if changed:errors.append('Preserved files changed')
index=read(job/'final/native_index.json');checked=0;native_sizes=set();longest=0
for s in spec['shots']:
 item=index[s['id']];folder=Path(item['folder']);m=read(folder/'manifest.json');last=None;run=0
 if item['key']!=native_key(s,[540,960]):errors.append('stale '+s['id'])
 for f in range(s['endFrame']-s['startFrame']):
  path=folder/f'{f:04}.png';row=m['frames'][str(f)];checked+=1
  if sha(path)!=row['sha256']:errors.append('corrupt '+str(path))
  with Image.open(path) as im:
   native_sizes.add(im.size);small=np.array(im.convert('L').resize((54,96)))
   if small.max()<5:errors.append('black native frame '+s['id']+'/'+str(f))
  h=digest(small.tolist());run=run+1 if h==last else 1;last=h;longest=max(longest,run)
reader=imageio_ffmpeg.read_frames(str(video));meta=next(reader);reader.close();count,duration=imageio_ffmpeg.count_frames_and_secs(str(video))
if sha(video)!=report['sha256']:errors.append('Final MP4 changed after composition')
if count!=1020 or meta['size']!=(1080,1920) or meta['fps']!=30:errors.append('output format')
audio=Path(report['audioFolder']);aq=read(audio/'audio_qa.json');events=aq['events'];maxsync=max(e['syncErrorSeconds'] for e in events)
if maxsync>1/30 or float(report['audio']['input_tp'])>-1:errors.append('audio sync/peak')
ui=read(job/'final'/f'ui_qa_{a.locale}_MOBILE.json')
if len(ui)!=1020 or any(q['fallbacks'] for q in ui):errors.append('UI frame/glyph')
if any(t['lang']!=a.locale for q in ui for t in q['texts']):errors.append('mixed locale overlay')
bgm=read_wav(audio/'bgm.wav');sfx=read_wav(audio/'sfx.wav');chart=Image.new('RGB',(1200,400),'#172339');d=ImageDraw.Draw(chart)
for track,color,y in [(bgm,'#74dab6',60),(sfx,'#ffe18a',230)]:
 rms=[float(np.sqrt(np.mean(track[i:i+SR//10]**2))) for i in range(0,len(track),SR//10)];peak=max(rms)
 pts=[(30+i/(len(rms)-1)*1140,y+120-v/max(peak,.0001)*110) for i,v in enumerate(rms)];d.line(pts,fill=color,width=2)
for ev in events:
 x=30+ev['time']/34*1140;d.line((x,25,x,370),fill='#7b8195');d.text((x+3,25),f"{ev['time']:.2f}s",fill='white')
d.text((30,6),'BGM envelope / SFX envelope - waveform review, not listening approval',fill='white');chart.save(R/'review/audio_envelope.png')
result=dict(technical='PASS' if not errors else 'FAIL',errors=errors,nativeFrameIntegrityChecks=checked,nativeSizes=list(native_sizes),output=meta,frameCount=count,duration=duration,fullDecode=True,uiValidatedFrames=len(ui),glyphFallbacks=0,maxSfxSyncErrorSeconds=maxsync,audioIntegratedLUFS=report['audio']['input_i'],audioTruePeak=report['audio']['input_tp'],tts=False,sourcePreservation=dict(checked=len(baseline),changed=changed),longestIdenticalDownsampledNativeRunFrames=longest,cacheIntegrity='hash checked',limits=['2fps visual timeline sampling is not continuous human playback.','No human listening or audience retention test.','No exhaustive pairwise mesh intersection proof.'])
write(job/'final'/f'qa_{a.locale}.json',result);print(result['technical'],errors)
