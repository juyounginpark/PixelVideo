from pathlib import Path
import sys,math
import numpy as np
from PIL import Image,ImageDraw
J=Path(__file__).resolve().parent;sys.path.insert(0,str(J.parent));sys.path.insert(0,str(J.parent/'experiment'))
from common import read,digest
from typography import TypographyTheme,intersection
from experiment.overlay import native_post

class EpisodeOverlay:
 def __init__(self,spec,locale='ko'):
  self.spec=spec;self.locale=locale;self.profile=read(J.parent/'experiment/profile.json');self.type=TypographyTheme(locale);p=self.profile
  self.keys={k:p['version']+'_'+digest(p['colors'])[:12]+'_'+k for k in p['colors']};self.type.colors.update({self.keys[k]:v for k,v in p['colors'].items()})
  alltexts=[]
  for shot in spec['shots']:alltexts += [shot['chapter'],shot['chapterEn'],*shot['captionPlan']['ko'],*shot['captionPlan']['en']]
  alltexts += [spec['title'],spec['titleEn'],'비행·크기·시간 단순화 모식도','Simplified flight, size and time','민무늬','줄무늬','체크무늬','옅은 대비','Uniform','Stripes','Checks','Faint','착륙 관찰','착륙 감소','Landing observed','Fewer landings','가설 · 시각 기제 연구 중','Hypothesis: visual mechanism still studied','7마리 · 3종 덮개','7 horses / 3 coats','2019 덮개 실험','2019 coat experiment','1 / 6','2 / 6','3 / 6','4 / 6','5 / 6','6 / 6','PLOS ONE 2019 · JEB 2023','네 생각은?','What did you expect?','같은 말 · 덮개 교체','Same horse / new coat','완벽한 차단 아님','Not total protection']
  alltexts+=['흡혈등에 · 크기·비행 모식도','Horseflies / simplified flight','체크무늬라면?','착륙도 달라질까?','Would checks work too?','Change the pattern.','2019 상용덮개 실험','2019 commercial coats','체크무늬도!','착륙이 줄었다!','Checks too!','Fewer landings.','연구: 2019 · 2020 · 2023','Studies: 2019 / 2020 / 2023']
  dummy={'shots':[{'labels':[],'captionPlan':[{'role':'PIXEL_TITLE','lines':alltexts,'english':[]},{'role':'PIXEL_BODY','lines':alltexts,'english':[]}]}]};self.fontQA=self.type.preflight(dummy)
 def text(self,im,text,face,scale,x,y,color,bounds):
  key=self.keys[color];layer=self.type.line(text,face,scale,key,key,())
  if layer.width>954:
   scale-=1;layer=self.type.line(text,face,scale,key,key,())
  if layer.width>954:raise ValueError('Caption too wide '+text)
  x=round(x-layer.width/2);im.alpha_composite(layer,(x,y));b=layer.getbbox()
  if b:bounds.append({'text':text,'rect':[x+b[0],y+b[1],x+b[2],y+b[3]]})
 def frame(self,native,shot,f,anchors):
  p=self.profile;factor=1080//native.width
  if native.width*factor!=1080 or native.height*factor!=1920:raise ValueError('Integer Nearest required')
  scene=native_post(native,p).resize((1080,1920),Image.Resampling.NEAREST);im=Image.new('RGBA',(1080,1920),p['colors']['NAVY']);d=ImageDraw.Draw(im);d.rectangle((40,80,1040,1800),fill=p['colors']['PANEL'],outline=p['colors']['PURPLE'],width=4)
  viewport=[64,362,1016,1250];im.paste(scene.crop((64,502,1016,1390)),(64,362));d.rectangle(viewport,outline=p['colors']['WHITE'],width=8);b=[];ko=self.locale=='ko'
  self.text(im,self.spec['title'] if ko else self.spec['titleEn'],'PIXEL_DISPLAY',6 if ko else 5,540,102,'YELLOW',b)
  self.text(im,shot['chapter'] if ko else shot['chapterEn'],'PIXEL_DISPLAY',4,540,226,'WHITE',b)
  chapter=int(shot['chapter'][0]);self.text(im,f'{chapter} / 6','PIXEL_BODY',3,540,304,'WHITE',b)
  labels={'plain':('민무늬','Uniform'),'white':('민무늬','Uniform'),'stripe':('줄무늬','Stripes'),'check':('체크무늬','Checks'),'faint':('옅은 대비','Faint')}
  for i,side in enumerate(['left','right']):
   if shot['phase'] in ['coat','patch']:continue
   x=305 if i==0 else 775;text=labels[shot['scene'][side]][0 if ko else 1];self.text(im,text,'PIXEL_BODY',3,x,1272,'WHITE',b)
   if f>=80:
    text=('착륙 관찰' if i==0 else '착륙 감소') if ko else ('Landing observed' if i==0 else 'Fewer landings')
    if shot['phase']=='ending':text='완벽한 차단 아님' if ko else 'Not total protection'
    if shot['phase']=='ending' and i==0:continue
    self.text(im,text,'PIXEL_BODY',3,x,1336,'MINT',b)
  if shot['phase']=='coat':self.text(im,'같은 말 · 덮개 교체' if ko else 'Same horse / new coat','PIXEL_BODY',3,540,1290,'WHITE',b)
  if shot['phase']=='trial':self.text(im,'7마리 · 3종 덮개' if ko else '7 horses / 3 coats','PIXEL_DISPLAY',4,540,1394,'YELLOW',b)
  lines=shot['captionPlan'][self.locale];base=1510 if shot['phase']=='trial' else 1458
  prereveal=shot['phase']=='check' and f<shot['emphasisEvent']['frame']
  if prereveal:lines=['체크무늬라면?','착륙도 달라질까?'] if ko else ['Would checks work too?','Change the pattern.']
  if shot['phase']=='check' and not prereveal:
   age=f-shot['emphasisEvent']['frame'];scale=6 if age<4 else 7
   self.text(im,'체크무늬도!' if ko else 'Checks too!','PIXEL_DISPLAY',scale,540,1454,'MINT',b)
   self.text(im,'착륙이 줄었다!' if ko else 'Fewer landings.','PIXEL_BODY',5 if ko else 4,540,1580,'MINT',b)
  else:
   for i,text in enumerate(lines):self.text(im,text,'PIXEL_BODY',5 if ko else 4,540,base+i*86,'YELLOW' if prereveal else 'PURPLE' if shot['phase']=='patch' else 'MINT' if shot['phase'] in ['check','return'] else 'WHITE',b)
  foot='가설 · 시각 기제 연구 중' if shot['phase']=='patch' else '흡혈등에 · 크기·비행 모식도';footEn='Hypothesis: visual mechanism still studied' if shot['phase']=='patch' else 'Horseflies / simplified flight'
  if shot['phase']=='trial':foot='2019 상용덮개 실험';footEn='2019 commercial coats'
  self.text(im,foot if ko else footEn,'PIXEL_BODY',3,540,1676,'PURPLE' if shot['phase']=='patch' else 'WHITE',b)
  self.text(im,'연구: 2019 · 2020 · 2023' if ko else 'Studies: 2019 / 2020 / 2023','PIXEL_BODY',2,540,1744,'WHITE',b)
  event=shot['emphasisEvent'];age=f-event['frame']
  if event.get('uiPreset',event['preset'])=='DISCOVERY' and 0<=age<12:
   for i in range(8):
    angle=i*math.tau/8;cx=775+math.cos(angle)*(175+age*4);cy=860+math.sin(angle)*(175+age*4);x=round(cx/4)*4;y=round(cy/4)*4;d.rectangle((x-4,y-12,x+4,y+12),fill=p['colors']['MINT']);d.rectangle((x-12,y-4,x+12,y+4),fill=p['colors']['MINT'])
  for i,q in enumerate(b):
   r=q['rect']
   if r[0]<54 or r[1]<90 or r[2]>1026 or r[3]>1790:raise ValueError('Unsafe caption '+str(q))
   if any(intersection(r,v['rect']) for v in b[i+1:]):raise ValueError('Overlapping text '+str(q))
   if intersection(r,viewport):raise ValueError('Text covers science viewport')
  arr=np.asarray(im.convert('RGB')).copy();arr[::4]=(arr[::4].astype(np.float32)*.94).astype('uint8')
  return Image.fromarray(arr),{'frame':f,'texts':b,'nativeAnchors':anchors,'fallbacks':0}
