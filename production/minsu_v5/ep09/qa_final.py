from pathlib import Path
import sys,subprocess,json,html,re
import imageio_ffmpeg
from PIL import Image,ImageDraw
J=Path(__file__).resolve().parent;sys.path.insert(0,str(J.parent));sys.path.insert(0,str(J));sys.path.append(str(J.parent.parent/'minsu_v2'))
from common import read,write,sha,ROOT
from audio import FF,measure
from contracts import verify

def main():
 spec=read(J/'episode.json');contracts=verify();quality=J/'final';native=read(quality/'native_index.json');reports={};errors=[]
 for shot in spec['shots']:
  item=native[shot['id']];records=item['frames'];folder=Path(item['folder'])
  if len(records)!=120:errors.append('Missing cut frames '+shot['id'])
  for f in range(120):
   if sha(folder/f'{f:04}.png')!=records[str(f)]['sha256']:errors.append('Native integrity '+shot['id'])
 for locale in ['ko','en']:
  output=ROOT/'exports'/f'MINSU_EP09_STRIPES_{locale.upper()}.mp4';reader=imageio_ffmpeg.read_frames(str(output));meta=next(reader);reader.close();count,duration=imageio_ffmpeg.count_frames_and_secs(str(output));decoded=subprocess.run([FF,'-v','error','-i',str(output),'-f','null','-'],capture_output=True,text=True)
  q=read(quality/f'compose_{locale}.json');measurements=measure(output)
  if count!=1080 or abs(duration-36)>.04 or meta['size']!=(1080,1920) or meta['fps']!=30:errors.append('Output format '+locale)
  if meta.get('audio_codec')!='aac' or decoded.returncode or decoded.stderr.strip():errors.append('Decode/audio '+locale)
  if q['font']['fallbacks']:errors.append('Glyph fallback '+locale)
  if float(measurements['input_tp'])>-1:errors.append('True peak '+locale)
  ui=read(quality/f'ui_{locale}.json')
  if len(ui)!=1080:errors.append('Incomplete UI QA '+locale)
  reports[locale]={'path':str(output),'sha256':sha(output),'frameCount':count,'duration':duration,'metadata':meta,'audioMeasurement':measurements,'fonts':q['font'],'uiCheckedFrames':len(ui),'audioCacheHit':q['audioCacheHit'],'fullVideoAndAudioDecode':True}
 geometry=read(J/'research/geometry_qa.json')
 if geometry['errors']:errors.append('Protected geometry clipped in viewport')
 out=J/'review/final';out.mkdir(parents=True,exist_ok=True)
 # Same functional comparisons; source artwork and script are not copied.
 reference=ROOT/'production/minsu_v5/experiment/review/straw/exact_051.50.png'
 ref4=ROOT/'production/minsu_v5/review/media/ref4_09.00.png'
 episode=quality/'S05_090_ko.png'
 comparison=Image.new('RGB',(1620,1000),'#211d37');draw=ImageDraw.Draw(comparison)
 for i,(label,path) in enumerate([('STRAW / ACTION -> RESULT',reference),('REF4 / CHARACTER REACTION',ref4),('EP09 / PATTERN DISCOVERY',episode)]):
  if not path.exists():continue
  with Image.open(path) as im:comparison.paste(im.resize((540,960),Image.Resampling.NEAREST),(i*540,40))
  draw.text((i*540+10,12),label,fill='white')
 comparison.save(out/'reference_comparison.jpg',quality=95)
 # Subtitle files are separate locale exports, not simultaneous overlay text.
 for locale in ['ko','en']:
  lines=[]
  def stamp(frame):
   milliseconds=round(frame*1000/30);seconds,ms=divmod(milliseconds,1000);minutes,secs=divmod(seconds,60);hours,mins=divmod(minutes,60);return f'{hours:02}:{mins:02}:{secs:02},{ms:03}'
  cue=0
  for shot in spec['shots']:
   segments=[(shot['startFrame'],shot['endFrame'],shot['captionPlan'][locale])]
   if shot['phase']=='check':
    event=shot['startFrame']+shot['emphasisEvent']['frame'];question=['체크무늬라면?','착륙도 달라질까?'] if locale=='ko' else ['Would checks work too?','Change the pattern.'];segments=[(shot['startFrame'],event,question),(event,shot['endFrame'],shot['captionPlan'][locale])]
   for begin,end,text in segments:
    cue+=1;lines.append(str(cue)+'\n'+stamp(begin)+' --> '+stamp(end)+'\n'+'\n'.join(text)+'\n')
  (ROOT/'exports'/f'MINSU_EP09.{locale}.srt').write_text('\n'.join(lines),'utf-8')
 report={'technical':'PASS' if not errors else 'FAIL','errors':errors,'outputs':reports,'sourceContracts':contracts,'geometryFramesChecked':geometry['checkedFrames'],'nativeFramesChecked':1080,'tts':False,'humanAudioListening':False,'humanRealtimePlayback':False,'viewerEngagementTest':False}
 write(out/'technical_qa.json',report)
 if errors:raise ValueError(errors)
 print('KO/EN final technical QA PASS / 1080 frames each')
if __name__=='__main__':main()
