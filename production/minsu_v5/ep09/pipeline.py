from pathlib import Path
import sys,argparse,subprocess,time
J=Path(__file__).resolve().parent;sys.path.insert(0,str(J.parent));sys.path.insert(0,str(J));sys.path.append(str(J.parent.parent/'minsu_v2'))
from common import read,write,sha,digest,ROOT
from PIL import Image,ImageDraw
import imageio_ffmpeg
from overlay import EpisodeOverlay
from audio import FF,ASSETS,mux
from audio_direction import build

def call_render(quality,shots,stills=False):
 folder=J/quality;folder.mkdir(exist_ok=True)
 cmd=['C:/Program Files/Blender Foundation/Blender 5.0/blender.exe','-b','--python-exit-code','1','--python',str(J/'render.py'),'--','--quality',quality]
 if shots:cmd+=['--shots',shots]
 if stills:cmd+=['--stills']
 with (folder/'render.log').open('w',encoding='utf-8') as f:p=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT)
 if p.returncode:raise RuntimeError('Blender failed; '+str(folder/'render.log'))

def compose(quality,locale,output,stills=False,shots=None):
 start=time.perf_counter();spec=read(J/'episode.json');folder=J/quality;index=read(folder/'native_index.json');overlay=EpisodeOverlay(spec,locale);clips=[];events=[];cursor=0;frames=[];uihit=0
 selected=[s for s in spec['shots'] if not shots or s['id'] in shots.split(',')]
 for shot in selected:
  item=index[shot['id']];native=Path(item['folder']);records=item['frames'];n=shot['endFrame']-shot['startFrame']
  if stills:
   for fs,rec in records.items():
    f=int(fs)
    with Image.open(native/f'{f:04}.png') as image:im,q=overlay.frame(image,shot,f,rec['anchors'])
    im.save(folder/f'{shot["id"]}_{f:03}_{locale}.png');frames.append(q)
   continue
  key=digest({'native':item['key'],'records':sha(native/'manifest.json'),'captions':shot,'locale':locale,'overlay':sha(J/'overlay.py'),'font':sha(J.parent/'typography.py'),'profile':sha(J.parent/'experiment/profile.json')});cache=J/'cache/ui'/key;cache.mkdir(parents=True,exist_ok=True);video=cache/'silent.mp4';receipt=cache/'receipt.json'
  if receipt.exists() and video.exists() and sha(video)==read(receipt)['sha256']:uihit+=1;qa=read(cache/'ui.json')
  else:
   qa=[];cmd=[FF,'-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1080x1920','-r','30','-i','-','-an','-c:v','libx264','-threads','4','-preset','fast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(video)]
   with (cache/'encode.log').open('w') as log:
    process=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
    try:
     for f in range(n):
      rec=records[str(f)];path=native/f'{f:04}.png'
      if sha(path)!=rec['sha256']:raise ValueError('Native integrity')
      with Image.open(path) as image:im,q=overlay.frame(image,shot,f,rec['anchors'])
      qa.append(q);process.stdin.write(im.tobytes())
      if f in [0,60,90,119]:im.save(folder/f'{shot["id"]}_{f:03}_{locale}.png')
    finally:process.stdin.close()
    if process.wait():raise RuntimeError('Encoder failed')
   write(cache/'ui.json',qa);write(receipt,{'sha256':sha(video)})
  clips.append(video);frames+=qa;e=shot['emphasisEvent'];audioPreset=e.get('audioPreset',e['preset']);fx=read(J.parent/'config/EFFECT_LIBRARY.json')['presets'][audioPreset]
  if fx['sound']:events.append({'frame':cursor+e['frame'],'time':(cursor+e['frame'])/30,'sound':fx['sound'],'gainDb':fx['gainDb'],'event':shot['visualAction'],'duck':audioPreset=='DISCOVERY'})
  cursor+=n;print('COMPOSE',shot['id'],locale,flush=True)
 if stills:
  write(folder/f'still_qa_{locale}.json',{'font':overlay.fontQA,'frames':frames});return
 assembly=J/'cache/assembly'/digest([sha(p) for p in clips]);assembly.mkdir(parents=True,exist_ok=True);silent=assembly/'silent.mp4'
 if not silent.exists():
  listing=assembly/'concat.txt';listing.write_text(''.join("file '"+str(p).replace('\\','/')+"'\n" for p in clips),'utf-8');subprocess.run([FF,'-v','error','-y','-f','concat','-safe','0','-i',str(listing),'-c','copy',str(silent)],check=True)
 audio=J/'cache/audio'/digest({'events':events,'settings':spec['audio'],'frames':cursor,'offset':selected[0]['startFrame'],'audioCode':sha(J.parent/'audio_direction.py')});mix=audio/'mix.wav';audioreceipt=audio/'receipt.json';audiohit=mix.exists() and audioreceipt.exists() and sha(mix)==read(audioreceipt)['sha256']
 if not audiohit:
  mix=build(cursor/30,events,audio,spec['audio'],selected[0]['startFrame']/30);write(audioreceipt,{'sha256':sha(mix)})
 output.parent.mkdir(exist_ok=True);audioqa=mux(silent,mix,output);count,duration=imageio_ffmpeg.count_frames_and_secs(str(output));assert count==cursor
 write(folder/f'compose_{locale}.json',{'frames':count,'duration':duration,'font':overlay.fontQA,'uiCacheHits':uihit,'audioCacheHit':audiohit,'audioFolder':str(audio),'audio':audioqa,'seconds':time.perf_counter()-start,'textCacheHits':overlay.type.cacheHits,'output':str(output),'sha256':sha(output),'tts':False});write(folder/f'ui_{locale}.json',frames)
 print('VIDEO',output,flush=True)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['stills','sample','preview','final','english','compose']);ap.add_argument('--shots');ap.add_argument('--reuse-final-native',action='store_true');a=ap.parse_args();quality='preview' if a.mode=='preview' and not a.reuse_final_native else 'final';stills=a.mode=='stills';locale='en' if a.mode=='english' else 'ko'
 if a.mode in ['preview','final','english']:
  gates=read(J/'gates.json');needed=['ART_PREVIEW'] if a.mode=='preview' else ['ART_PREVIEW','EDITING_PREVIEW']
  for gate in needed:
   if gates[gate]['decision'] not in ['PASS','PROCEED_WITH_STATED_LIMITS']:raise ValueError('Gate not reviewed '+gate)
 if a.mode not in ['english','compose']:call_render(quality,a.shots,stills)
 if a.mode not in ['english','compose']:write(J/quality/(a.mode+'_render_metrics.json'),read(J/quality/'render_metrics.json'))
 name={'sample':'MINSU_EP09_ART_SAMPLE.mp4','preview':'MINSU_EP09_PREVIEW.mp4','final':'MINSU_EP09_STRIPES_KO.mp4','english':'MINSU_EP09_STRIPES_EN.mp4','compose':'MINSU_EP09_STRIPES_KO.mp4'}.get(a.mode,'stills')
 output=ROOT/'exports'/name;compose(quality,locale,output,stills,a.shots)
 if a.mode=='preview' and a.reuse_final_native:
  tmp=output.with_name(output.stem+'.low.mp4');subprocess.run([FF,'-y','-v','error','-i',str(output),'-vf','scale=540:960:flags=neighbor','-c:v','libx264','-threads','4','-preset','fast','-crf','20','-c:a','copy',str(tmp)],check=True);tmp.replace(output)
  q=read(J/quality/'compose_ko.json');q.update(sha256=sha(output),outputResolution=[540,960],nativeCacheSharedWithFinal=True);write(J/quality/'compose_ko.json',q)
 if not stills:write(J/quality/(a.mode+'_compose_'+locale+'.json'),read(J/quality/f'compose_{locale}.json'))
if __name__=='__main__':main()
