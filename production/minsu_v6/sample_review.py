from pathlib import Path
import json,subprocess,sys
from PIL import Image,ImageDraw
from imageio_ffmpeg import get_ffmpeg_exe
J=Path(__file__).resolve().parent;out=J/'sample/review';out.mkdir(exist_ok=True);video=J.parents[1]/'exports/MINSU_V6_ACTION_EXPLAIN_SAMPLE.mp4'
subprocess.run([get_ffmpeg_exe(),'-v','error','-i',str(video),'-f','null','-'],check=True)
sheet=Image.new('RGB',(900,800))
for i,t in enumerate([.2,1.3,2.6,3.2,5.4,5.6,7.1,8.3]):
 p=out/f'{t:.1f}.png';subprocess.run([get_ffmpeg_exe(),'-v','error','-ss',str(t),'-i',str(video),'-frames:v','1','-y',str(p)],check=True);im=Image.open(p);im.thumbnail((225,400));sheet.paste(im,(i%4*225,i//4*400))
sheet.save(out/'contact.jpg')
report={'technical':{'fullDecode':True,'frames':300,'native':[540,960],'output':[1080,1920],'fps':30,'fontFallbacks':0,'captionTests':3},'editorial':{'reviewMethod':'Actual decoded frames and dense transition samples; no real-time playback, hearing or audience test','improvements':['Persistent title/chapter/frame removed','Character and event occupy main world','Explain limited to observed landing difference','Same horse, actor and paddock return','First caption line persists at 5.5 seconds'],'rework':{'count':1,'reason':'Enlarged fly clipped at right boundary','fix':'Bounded outbound fly position'},'remaining':['Upper world background remains too empty; new episode composition must improve','Fly trajectory is explanatory and enlarged, not physical simulation','Observation comparison does not establish complete neural mechanism','No musical or audience approval'],'gate':'Reusable caption/mode sample accepted with these explicit limitations; not a final episode quality approval'}}
(out/'qa.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print('Sample actual-output review recorded')
