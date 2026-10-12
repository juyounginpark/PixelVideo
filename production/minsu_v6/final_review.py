from pathlib import Path
import json,subprocess,hashlib,sys,re
from PIL import Image,ImageDraw
from imageio_ffmpeg import get_ffmpeg_exe
J=Path(__file__).resolve().parent;ROOT=J.parents[1];job=J/'ep10';out=job/'review/final';out.mkdir(parents=True,exist_ok=True)
ff=get_ffmpeg_exe();results={};times=[0,.5,.77,.8,1,1.4,2,3.5,5,7.8,8.2,10.3,10.5,11.8,12.2,13.2,15.5,15.97,16.03,17,18.87,18.97,20.5,21.5,23.8,24.03,25,27.5,28.7,29.5,30.6,31.8]
for locale in ['ko','en']:
 video=ROOT/'exports'/f'MINSU_EP10_V6_LYCURGUS_{locale.upper()}.mp4'
 if not video.exists():continue
 decoded=subprocess.run([ff,'-v','error','-i',str(video),'-progress','pipe:1','-nostats','-f','null','-'],capture_output=True)
 counts=re.findall(r'frame=(\d+)',decoded.stdout.decode(errors='replace'));decoded_count=int(counts[-1]) if counts else None
 info=subprocess.run([ff,'-hide_banner','-i',str(video)],capture_output=True,text=True,encoding='utf8',errors='replace').stderr
 files=[]
 for t in times:
  file=out/f'{locale}_{t:05.2f}.png';subprocess.run([ff,'-v','error','-ss',str(t),'-i',str(video),'-frames:v','1','-y',str(file)],check=True);files.append(file)
 for page in range(2):
  sheet=Image.new('RGB',(900,1600),'#192131');draw=ImageDraw.Draw(sheet)
  for i,file in enumerate(files[page*16:(page+1)*16]):
   im=Image.open(file);im.thumbnail((225,400));sheet.paste(im,(i%4*225,i//4*400));draw.text((i%4*225+5,i//4*400+5),file.stem,fill='white')
  sheet.save(out/f'{locale}_contact_{page}.jpg')
 ui=json.loads((job/f'ui_{locale}.json').read_text('utf8'));native=json.loads((job/'native_index.json').read_text('utf8'));bad=[]
 for shot,item in native.items():
  for fs,rec in item['frames'].items():
   rect=rec['anchors'].get('cup')
   if rect and (min(rect)<0 or max(rect)>1):bad.append({'frame':int(fs),'target':'cup','rect':rect})
 collisions=[]
 for row in ui:
  rects=row['textBounds']
  for i,a in enumerate(rects):
   for b in rects[i+1:]:
    if min(a[2],b[2])>max(a[0],b[0]) and min(a[3],b[3])>max(a[1],b[1]):collisions.append(row['frame'])
 loudness=json.loads((job/f'compose_{locale}.json').read_text('utf8'))['loudness']
 results[locale]={'decodePassed':decoded.returncode==0,'decodedFrameCount':decoded_count,'formatPassed':'1080x1920' in info and '30 fps' in info and 'Audio: aac' in info,'decodeErrors':decoded.stderr.decode(errors='replace'),'outputSHA256':hashlib.sha256(video.read_bytes()).hexdigest(),'mediaInfo':info,'uiFrames':len(ui),'glyphFallbacks':sum(r['fallbacks'] for r in ui),'textCollisions':collisions,'cupOutOfFrame':bad,'reviewFrames':len(files),'audioAnalysis':loudness,'audioPeakPassed':float(loudness['input_tp'])<=-1}
baseline=json.loads((J/'review/preservation_before.json').read_text('utf8'));changed=[path for path,h in baseline.items() if not (ROOT/path).exists() or hashlib.sha256((ROOT/path).read_bytes()).hexdigest()!=h]
results['preservation']={'checkedFiles':len(baseline),'changedFiles':changed};(out/'technical_qa.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps({k:{'decode':v['decodePassed'],'frames':v['uiFrames'],'cupClipping':len(v['cupOutOfFrame'])} for k,v in results.items() if k!='preservation'}))
