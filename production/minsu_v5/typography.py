"""Persistent glyph atlases, binary pixel text cache, one language per output."""
from PIL import Image,ImageDraw,ImageFont,ImageFilter
from fontTools.ttLib import TTFont
from functools import lru_cache
import math,numpy as np
from common import R,ROOT,read,write,sha,digest,config

class TypographyTheme:
 def __init__(self,locale='ko'):
  if locale not in ('ko','en'):raise ValueError('One supported locale per output')
  self.locale=locale;self.theme=config('FONT_THEME');self.colors=config('STYLE_SPEC')['palette'];self.fonts={};self.cmaps={};self.atlases={};self.glyphs={};self.cacheHits=0;self.cacheMisses=0
  for key,d in self.theme['fonts'].items():
   path=ROOT/d['path']
   if not path.exists() or not (ROOT/d['license']).exists():raise ValueError('Missing licensed font '+key)
   self.fonts[key]=ImageFont.truetype(str(path),12);font=TTFont(path);self.cmaps[key]=font.getBestCmap();font.close()
 def check(self,text,face):
  missing=[c for c in set(text) if not c.isspace() and ord(c) not in self.cmaps[face]]
  if missing:raise ValueError('Glyph fallback forbidden '+str(missing))
 def preflight(self,spec):
  sets={k:set('0123456789 .,:!?/-') for k in self.fonts};count=0
  for s in spec['shots']:
   for c in s['labels']+s['captionPlan']:
    face=self.theme['roles'][c['role']]['font']
    for t in c['lines']+c['english']:self.check(t,face);sets[face].update(t);count+=len(t)
  receipts=[]
  for face,chars in sets.items():
   chars=sorted(chars);key=digest(dict(face=sha(ROOT/self.theme['fonts'][face]['path']),chars=chars,basePx=12,version=1));folder=R/'cache/glyph_atlas'/key;file=folder/'atlas.png';meta=folder/'manifest.json'
   hit=file.exists() and meta.exists() and read(meta)['sha256']==sha(file)
   if hit:im=Image.open(file).convert('L');glyphs=read(meta)['glyphs']
   else:
    im=Image.new('L',(512,20*((len(chars)+31)//32)));d=ImageDraw.Draw(im);glyphs={}
    for i,c in enumerate(chars):
     x=i%32*16;y=i//32*20;d.text((x+1,y+14),c,font=self.fonts[face],fill=255,anchor='ls');glyphs[c]=dict(box=[x,y,x+16,y+20],advance=round(self.fonts[face].getlength(c))+1)
    im=im.point(lambda v:255 if v>=128 else 0);folder.mkdir(parents=True,exist_ok=True);im.save(file);write(meta,dict(glyphs=glyphs,sha256=sha(file)))
   self.atlases[face]=im;self.glyphs[face]=glyphs;receipts.append(dict(face=face,key=key,reused=hit,characters=len(chars)))
  return dict(checkedCharacters=count,fallbacks=0,locale=self.locale,atlases=receipts)
 @lru_cache(maxsize=512)
 def line(self,text,face,scale,color,accent,words):
  self.check(text,face);key=digest([text,face,scale,color,accent,words,sha(ROOT/self.theme['fonts'][face]['path']),sha(R/'typography.py')]);path=R/'cache/text'/f'{key}.png'
  if path.exists():self.cacheHits+=1;return Image.open(path).convert('RGBA')
  self.cacheMisses+=1;glyphs=self.glyphs[face];w=sum(glyphs[c]['advance'] for c in text)+4;mask=Image.new('L',(w,20));base=Image.new('RGBA',(w,20));x=2;highlighted=set()
  for word in words:
   start=text.find(word)
   while start>=0:highlighted.update(range(start,start+len(word)));start=text.find(word,start+1)
  for i,c in enumerate(text):
   g=glyphs[c];cm=self.atlases[face].crop(g['box']);mask.paste(cm,(x-1,0),cm);base.paste(Image.new('RGBA',cm.size,self.colors[accent if i in highlighted else color]),(x-1,0),cm);x+=g['advance']
  outline=mask.filter(ImageFilter.MaxFilter(3));out=Image.new('RGBA',mask.size);out.paste(Image.new('RGBA',mask.size,self.colors['navy']),(0,0),outline);out.alpha_composite(base)
  out=out.crop((0,1,w,17)).resize((w*scale,16*scale),Image.Resampling.NEAREST);path.parent.mkdir(parents=True,exist_ok=True);out.save(path);return out
 def item(self,im,c,f):
  if not c['start']<=f<c['end']:return []
  style=self.theme['roles'][c['role']];scale=style['scale'];age=f-c['start'];lines=c['lines'] if self.locale=='ko' else c['english']
  if self.locale=='en' and c['role'] in ('PIXEL_BODY','PIXEL_TITLE','PIXEL_IMPACT'):scale=max(4,scale-1)
  if style['motion']=='pop' and age<4:scale=max(3,scale-1)
  words=tuple(c.get('highlight',[])) if self.locale=='ko' else tuple(c.get('highlightEn',[]))
  layers=[self.line(t,style['font'],scale,style['color'],style['accent'],words) for t in lines];width=max(l.width for l in layers);y=c['y']+(4 if age<3 and style['motion']=='step' else 0);rects=[]
  if width>950:raise ValueError('Caption too wide '+str((self.locale,c['role'],lines,width)))
  gap=16*scale+10;center=int(c.get('x',540))
  if c['role'] in ('PIXEL_BODY','PIXEL_INFO'):
   d=ImageDraw.Draw(im);h=gap*len(layers)-10;d.rectangle((center-width//2-18,y-8,center+(width+1)//2+18,y+h+8),fill=self.colors['purple'])
   if c['role']=='PIXEL_INFO':d.rectangle((center-width//2-18,y-8,center+(width+1)//2+18,y+h+8),outline=self.colors['teal'],width=2)
  for t,layer in zip(lines,layers):
   x=center-layer.width//2;im.alpha_composite(layer,(x,y));b=layer.getbbox()
   if b:rects.append(dict(role=c['role'],lang=self.locale,text=t,rect=[x+b[0],y+b[1],x+b[2],y+b[3]]))
   y+=gap
  return rects

def intersection(a,b):return max(0,min(a[2],b[2])-max(a[0],b[0]))*max(0,min(a[3],b[3])-max(a[1],b[1]))
def crt(im,preset,bounds):
 d=config('POST_PROCESS_PRESETS');p=d['presets'][preset]
 if p['opacity']==0 and p['bleed']==0:return im
 a=np.array(im,dtype=np.uint8);period=p['period'];dark=round(255*(1-p['opacity']));a[d['phase']::period]=(a[d['phase']::period].astype(np.uint16)*dark//255).astype(np.uint8)
 if p['bleed']:
  before=a.copy();weight=round(p['bleed']*128)
  for ch,shift in [(0,1),(2,-1)]:
   shifted=np.roll(before[:,:,ch],shift,axis=1);edge=0 if shift==1 else -1;shifted[:,edge]=before[:,edge,ch]
   a[:,:,ch]=((before[:,:,ch].astype(np.uint16)*(256-weight)+shifted.astype(np.uint16)*weight)//256).astype(np.uint8)
  ui_percent=round(d['uiBleedMultiplier']*100)
  for b in bounds:
   x0,y0,x1,y1=map(int,b['rect']);a[y0:y1,x0:x1]=((a[y0:y1,x0:x1].astype(np.uint16)*ui_percent+before[y0:y1,x0:x1].astype(np.uint16)*(100-ui_percent))//100).astype(np.uint8)
 return Image.fromarray(a)

class Overlay:
 def __init__(self,locale='ko',post='MOBILE'):self.type=TypographyTheme(locale);self.post=post
 def frame(self,native,shot,f,anchors,check=True):
  factor=1080//native.width
  if native.height*factor!=1920:raise ValueError('Noninteger upscale')
  im=native.convert('RGB').resize((1080,1920),Image.Resampling.NEAREST).convert('RGBA');bounds=[]
  event=shot['emphasisEvent'];fx=config('EFFECT_LIBRARY')['presets'][event['preset']];age=f-event['frame']
  if fx['spark'] and 0<=age<12 and event['target'] in anchors:
   cx,cy=anchors[event['target']]['point'];d=ImageDraw.Draw(im);radius=290 if event['preset']=='DISCOVERY' else 220
   for i in range(8):
    ang=i*math.tau/8;r=radius+age*6;x=round((cx+math.cos(ang)*r)/4)*4;y=round((cy+math.sin(ang)*r)/4)*4;d.rectangle((x-4,y-16,x+4,y+16),fill=self.type.colors['yellow']);d.rectangle((x-16,y-4,x+16,y+4),fill=self.type.colors['yellow'])
  for c in shot['labels']+shot['captionPlan']:
   if c.get('anchor') in anchors:
    a=anchors[c['anchor']];c={**c,'x':round(a['point'][0]),'y':round(a['rect'][1]-90)}
   bounds+=self.type.item(im,c,f)
  if check:
   safe=self.type.theme['safeRect']
   for b in bounds:
    r=b['rect']
    if r[0]<safe[0] or r[1]<safe[1] or r[2]>safe[2] or r[3]>safe[3]:raise ValueError('Text out of bounds '+shot['id']+'/'+str(f))
    for subject in shot['protectedSubjects']:
     if subject in anchors and intersection(r,anchors[subject]['rect'])>0:raise ValueError('Text covers '+subject+' '+shot['id']+'/'+str(f))
   for i,b in enumerate(bounds):
    if any(intersection(b['rect'],q['rect'])>0 for q in bounds[i+1:]):raise ValueError('Text collision '+shot['id'])
  return crt(im.convert('RGB'),self.post,bounds),dict(localFrame=f,texts=bounds,locale=self.type.locale,postPreset=self.post,fallbacks=0)
