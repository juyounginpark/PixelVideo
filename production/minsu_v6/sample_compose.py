from pathlib import Path
import sys,json,subprocess,time
from PIL import Image,ImageDraw
import numpy as np
from imageio_ffmpeg import get_ffmpeg_exe
J=Path(__file__).resolve().parent;sys.path.insert(0,str(J.parent/'minsu_v5'))
from typography import TypographyTheme
sys.path.insert(0,str(J))
from directors import CaptionDirector
cues=[{'start':1.1,'end':3,'lines':['왜 못 앉을까?'],'role':'PIXEL_TITLE','color':'yellow'},
 {'start':3,'end':5.5,'lines':['줄무늬에 접근한 등에는'],'role':'PIXEL_BODY','color':'white'},
 {'start':5.5,'end':8.2,'lines':['줄무늬에 접근한 등에는','착륙 직전 감속하지 못했다.'],'newText':'착륙 직전 감속하지 못했다.','role':'PIXEL_BODY','color':'white'},
 {'start':8.2,'end':10,'lines':['차이는 착륙 순간!'],'role':'PIXEL_IMPACT','color':'yellow'}]
theme=TypographyTheme('ko');pre=theme.preflight({'shots':[{'labels':[],'captionPlan':[{'role':c['role'],'lines':c['lines'],'english':[]} for c in cues]+[{'role':'PIXEL_LABEL','lines':['민무늬','줄무늬','흡혈등에 · 크기와 비행 모식도'],'english':[]}]}]});director=CaptionDirector(cues)
theme.colors['cyan']='#79D5DA'
out=J/'sample/ui';out.mkdir(parents=True,exist_ok=True);begin=time.perf_counter()
for f in range(300):
 im=Image.open(J/'sample/native'/f'{f:04}.png').convert('RGBA').resize((1080,1920),Image.Resampling.NEAREST)
 c,alphas=director.active(f)
 if c:
  face='PIXEL_BODY' if c['role']=='PIXEL_BODY' else 'PIXEL_DISPLAY';scale=5 if face=='PIXEL_BODY' else 7
  for i,(line,alpha) in enumerate(zip(c['lines'],alphas)):
   text=theme.line(line,face,scale,c['color'],c['color'],()).copy()
   if text.width>980:raise ValueError('Split caption, do not shrink: '+line)
   text.putalpha(text.getchannel('A').point(lambda a:int(a*alpha)))
   im.alpha_composite(text,((1080-text.width)//2,1550+i*100+int((1-alpha)*4)))
 if 90<=f<210:
  for line,x in [('민무늬',325),('줄무늬',755)]:
   text=theme.line(line,'PIXEL_BODY',3,'cyan','cyan',());im.alpha_composite(text,(x-text.width//2,1160))
  text=theme.line('흡혈등에 · 크기와 비행 모식도','PIXEL_BODY',3,'white','white',());im.alpha_composite(text,((1080-text.width)//2,1410))
 a=np.asarray(im.convert('RGB')).copy();a[::4]=(a[::4]*.94).astype('uint8');Image.fromarray(a).save(out/f'{f:04}.png')
target=J.parents[1]/'exports/MINSU_V6_ACTION_EXPLAIN_SAMPLE.mp4'
subprocess.run([get_ffmpeg_exe(),'-v','error','-framerate','30','-i',str(out/'%04d.png'),'-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart','-y',str(target)],check=True)
(J/'sample/captions.json').write_text(json.dumps(cues,ensure_ascii=False,indent=2),encoding='utf8');(J/'sample/ui_qa.json').write_text(json.dumps({'fontQA':pre,'captionContinuity':'Retained first line at 5.5s does not refade','composeSeconds':time.perf_counter()-begin,'output':str(target)},ensure_ascii=False,indent=2),encoding='utf8')
print(target)
