from pathlib import Path
import sys,math,json,hashlib
import numpy as np
from PIL import Image,ImageDraw
J=Path(__file__).resolve().parent;sys.path.insert(0,str(J.parent/'minsu_v5'))
from typography import TypographyTheme
sys.path.insert(0,str(J))
from directors import CaptionDirector
BAYER=np.array([[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]],dtype=float)/16-.5
class Overlay:
 def __init__(self,spec,locale):
  self.spec=spec;self.locale=locale;self.cues=spec['captions'][locale];self.director=CaptionDirector(self.cues);self.theme=TypographyTheme(locale)
  self.fontTheme=json.loads((J/'FONT_THEME.json').read_text('utf8'));self.style=json.loads((J/'STYLE_SPEC.json').read_text('utf8'))
  palette=self.fontTheme['palette'];prefix='v6_'+hashlib.sha256(json.dumps(palette,sort_keys=True).encode()).hexdigest()[:8]+'_';self.colors={name:prefix+name for name in palette};self.theme.colors.update({prefix+name:value for name,value in palette.items()})
  items=[{'role':c['role'],'lines':c['lines'],'english':[]} for c in self.cues]
  for shot in spec['shots']:
   items.extend({'role':'PIXEL_LABEL','lines':[l['text'][locale]],'english':[]} for l in shot.get('labels',[]))
  self.fontQA=self.theme.preflight({'shots':[{'labels':items,'captionPlan':[]}]})
 def frame(self,native,f,shot):
  a=np.asarray(native.convert('RGB'),dtype=float);h,w=a.shape[:2];threshold=np.tile(BAYER,((h+3)//4,(w+3)//4))[:h,:w,None]
  a=np.clip(np.round((a+threshold*8*.15)/8)*8,0,255).astype('uint8')
  im=Image.fromarray(a).convert('RGBA').resize((1080,1920),Image.Resampling.NEAREST);bounds=[]
  c,alphas=self.director.active(f)
  if c:
   family=self.fontTheme['roles'][c['role']];face=self.fontTheme['families'][family];scale=self.fontTheme['scale'][self.locale][family]
   if c['role']=='PIXEL_IMPACT' and f-round(c['start']*30)<2:scale-=1
   for i,(line,alpha) in enumerate(zip(c['lines'],alphas)):
    text=self.theme.line(line,face,scale,self.colors[c.get('color','white')],self.colors[c.get('accent',c.get('color','white'))],tuple(c.get('words',[]))).copy()
    if text.width>980:raise ValueError('Caption overflow; split '+line)
    text.putalpha(text.getchannel('A').point(lambda a:round(a*alpha)));x=(1080-text.width)//2;y=self.style['caption']['position'][1]+i*100+int((1-alpha)*4);im.alpha_composite(text,(x,y));bounds.append([x,y,x+text.width,y+text.height])
  for l in shot.get('labels',[]):
   text=self.theme.line(l['text'][self.locale],'PIXEL_BODY',self.fontTheme['scale'][self.locale]['LABEL'],self.colors[l.get('color','cyan')],self.colors[l.get('color','cyan')],());x=round(l['x']-text.width/2);y=l['y']
   if x<20 or x+text.width>1060:raise ValueError('Label outside safe area')
   im.alpha_composite(text,(x,y));bounds.append([x,y,x+text.width,y+text.height])
  event=shot.get('emphasisEvent',{});pulse=max(0,1-abs(f-event.get('frame',-100))/9)
  if event.get('spark') and pulse:
   d=ImageDraw.Draw(im);cx,cy=event.get('screenTarget',[600,800]);color=self.theme.colors['yellow']
   for i in range(6):
    ang=i*math.tau/6;r=90+(1-pulse)*90;x=round(cx+math.cos(ang)*r);y=round(cy+math.sin(ang)*r);d.rectangle((x-4,y-4,x+4,y+4),fill=color)
  post=self.style['post'];a=np.asarray(im.convert('RGB')).copy();a[::post['scanlinePeriod']]=(a[::post['scanlinePeriod']]*(1-post['opacity'])).astype('uint8')
  return Image.fromarray(a),{'frame':f,'textBounds':bounds,'fallbacks':0}
