from pathlib import Path
import sys,json,subprocess,time,argparse
J=Path(__file__).resolve().parent;sys.path.insert(0,str(J))
from overlay import Overlay
sys.path.append(str(J.parent/'minsu_v2'))
from common import read,write,sha,digest
from audio import FF,mux,measure
from audio_direction import build
from PIL import Image
ap=argparse.ArgumentParser();ap.add_argument('job',type=Path);ap.add_argument('--locale',default='ko');ap.add_argument('--preview',action='store_true');a=ap.parse_args();job=a.job.resolve();spec=read(job/'episode.json');index=read(job/'native_index.json');overlay=Overlay(spec,a.locale);begin=time.perf_counter();clips=[];records=[];hits=0
for shot in spec['shots']:
 native=index[shot['id']];folder=Path(native['folder']);start=shot['startFrame'];end=shot['endFrame'];captions=[c for c in spec['captions'][a.locale] if c['start']*30<end and c['end']*30>start]
 fontroot=J.parent/'retro_voxel/fonts'
 key=digest({'native':native['key'],'frames':sha(folder/'manifest.json'),'captions':captions,'labels':shot.get('labels'),'event':shot.get('emphasisEvent'),'locale':a.locale,'overlay':sha(J/'overlay.py'),'director':sha(J/'directors.py'),'font':sha(J.parent/'minsu_v5/typography.py'),'fontAssets':{p:sha(fontroot/p) for p in ['Galmuri11.ttf','Galmuri11-Bold.ttf','OFL.md']}});cache=job/'cache/ui'/key;cache.mkdir(parents=True,exist_ok=True);video=cache/'silent.mp4';receipt=cache/'receipt.json';qa=cache/'qa.json'
 key=digest([key,sha(J/'FONT_THEME.json'),sha(J/'STYLE_SPEC.json')]);cache=job/'cache/ui'/key;cache.mkdir(parents=True,exist_ok=True);video=cache/'silent.mp4';receipt=cache/'receipt.json';qa=cache/'qa.json'
 if receipt.exists() and video.exists() and read(receipt)['sha256']==sha(video):hits+=1;rows=read(qa)
 else:
  rows=[];process=subprocess.Popen([FF,'-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1080x1920','-r','30','-i','-','-an','-c:v','libx264','-threads','4','-preset','fast','-crf','18','-pix_fmt','yuv420p',str(video)],stdin=subprocess.PIPE,stderr=subprocess.PIPE)
  try:
   for f in range(start,end):
    path=folder/f'{f:04}.png'
    if sha(path)!=native['frames'][str(f)]['sha256']:raise ValueError('Native cache corrupted')
    with Image.open(path) as im:frame,row=overlay.frame(im,f,shot)
    process.stdin.write(frame.tobytes());rows.append(row)
    if (f-start) in (0,30,45,90,119):
     still=job/'review'/f'{a.locale}_{f:04}.png';still.parent.mkdir(exist_ok=True);frame.save(still)
  finally:process.stdin.close()
  error=process.stderr.read();code=process.wait()
  if code:raise RuntimeError(error.decode(errors='replace'))
  write(qa,rows);write(receipt,{'sha256':sha(video)})
 clips.append(video);records.extend(rows)
concat=job/'concat.txt';concat.write_text('\n'.join("file '"+str(p).replace('\\','/')+"'" for p in clips),encoding='utf8');silent=job/f'silent_{a.locale}.mp4'
subprocess.run([FF,'-v','error','-f','concat','-safe','0','-i',str(concat),'-c','copy','-y',str(silent)],check=True)
events=[{'frame':42,'time':1.4,'sound':'discovery','gainDb':-7,'event':'HOOK','duck':True},{'frame':380,'time':380/30,'sound':'whoosh','gainDb':-10,'event':'LIGHT_MOVE','duck':False},{'frame':486,'time':16.2,'sound':'whoosh','gainDb':-12,'event':'MACRO_ENTRY','duck':False},{'frame':646,'time':646/30,'sound':'discovery','gainDb':-7,'event':'PATH_DISCOVERY','duck':True},{'frame':890,'time':890/30,'sound':'success','gainDb':-9,'event':'PAYOFF','duck':True}]
for event in events:
 event['sound']={'whoosh':'soft_whoosh','success':'achievement'}.get(event['sound'],event['sound'])
 if event['event']=='HOOK':event['frame']=24;event['time']=.8
 if event['event']=='PAYOFF':event['frame']=918;event['time']=30.6
catalog_path=J.parent/'minsu_v2/audio/catalog.json';catalog=read(catalog_path);used_ids={spec['audio']['track'],*[e['sound'] for e in events]};asset_hashes={item['id']:sha(catalog_path.parent/item['path']) for group in ['bgm','sfx'] for item in catalog[group] if item['id'] in used_ids}
audio_key=digest([spec['audio'],events,spec['durationFrames'],sha(J.parent/'minsu_v5/audio_direction.py'),sha(catalog_path),asset_hashes]);audio=job/'cache/audio'/audio_key;mix=audio/'mix.wav';audio_receipt=audio/'receipt.json';audio_hit=mix.exists() and audio_receipt.exists() and read(audio_receipt)['sha256']==sha(mix)
if not audio_hit:
 audio.mkdir(parents=True,exist_ok=True);built=build(spec['durationFrames']/30,events,audio,spec['audio']);
 if built!=mix:
  import shutil;shutil.copy2(built,mix)
 qa_audio=read(audio/'audio_qa.json');qa_audio['intentionalPreDiscoveryDip']='20.8 seconds authored gain -15dB, then rise to -3dB at21.5';write(audio/'audio_qa.json',qa_audio)
 write(audio_receipt,{'sha256':sha(mix),'assetHashes':asset_hashes})
target=J.parents[1]/'exports'/f'MINSU_EP10_V6_LYCURGUS_{a.locale.upper()}.mp4';mux(silent,mix,target)
if a.preview:
 preview=target.with_name('MINSU_EP10_V6_PREVIEW.mp4');subprocess.run([FF,'-v','error','-i',str(target),'-vf','scale=540:960:flags=neighbor','-c:v','libx264','-crf','20','-c:a','copy','-y',str(preview)],check=True)
write(job/f'compose_{a.locale}.json',{'seconds':time.perf_counter()-begin,'uiCutCacheHits':hits,'audioCacheHit':audio_hit,'frameCount':len(records),'fontQA':overlay.fontQA,'target':str(target),'loudness':measure(target),'tts':False});write(job/f'ui_{a.locale}.json',records)
print(target)
