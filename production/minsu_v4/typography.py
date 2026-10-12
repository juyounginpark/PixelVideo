"""Two explicit pixel faces, hard glyph coverage and cached binary glyph layers."""
import math
from functools import lru_cache
from PIL import Image,ImageDraw,ImageFont,ImageFilter
from fontTools.ttLib import TTFont
from common import ROOT,config

class TypographyTheme:
    def __init__(self):
        self.theme=config('TYPOGRAPHY_THEME');self.colors=config('STYLE_SPEC')['palette']
        self.fonts={};self.cmaps={}
        for key,d in self.theme['fonts'].items():
            p=ROOT/d['path']
            if not p.exists() or not (ROOT/d['license']).exists():raise ValueError('Missing licensed font '+key)
            self.fonts[key]=ImageFont.truetype(str(p),d['basePx']);font=TTFont(p)
            self.cmaps[key]=font.getBestCmap();font.close()
    def check(self,text,face):
        missing=sorted(set(c for c in text if not c.isspace() and ord(c) not in self.cmaps[face]))
        if missing:raise ValueError(f'Glyph fallback forbidden: {face} {missing}')
    def preflight(self,spec):
        count=0
        for s in spec['shots']:
            for c in s['captionPlan']+s['labels']:
                face=self.theme['roles'][c['role']]['font']
                for text in c['lines']:self.check(text,face);count+=len(text)
                for text in c['english']:self.check(text,'PIXEL_BODY');count+=len(text)
        return dict(checkedCharacters=count,fallbacks=0,fontFaces=list(self.fonts))
    @lru_cache(maxsize=1024)
    def line(self,text,face,scale,color,accent,words):
        self.check(text,face);font=self.fonts[face];pad=2
        advances=[round(font.getlength(ch))+1 for ch in text];w=sum(advances)+2*pad
        mask=Image.new('L',(w,18));d=ImageDraw.Draw(mask);x=pad
        # Use a common baseline and disable antialiasing before integer scaling.
        highlighted=set()
        for word in words:
            at=text.find(word)
            while at>=0:highlighted.update(range(at,at+len(word)));at=text.find(word,at+1)
        base=Image.new('RGBA',mask.size);bd=ImageDraw.Draw(base)
        for i,ch in enumerate(text):
            cm=Image.new('L',mask.size);ImageDraw.Draw(cm).text((x,14),ch,font=font,anchor='ls',fill=255)
            cm=cm.point(lambda v:255 if v>=128 else 0);mask=Image.fromarray(__import__('numpy').maximum(__import__('numpy').array(mask),__import__('numpy').array(cm)))
            glyph=Image.new('RGBA',mask.size,self.colors[accent if i in highlighted else color]);base.paste(glyph,(0,0),cm);x+=advances[i]
        outline=mask.filter(ImageFilter.MaxFilter(3));out=Image.new('RGBA',mask.size)
        out.paste(Image.new('RGBA',mask.size,self.colors['navy']),(0,0),outline);out.alpha_composite(base)
        bbox=outline.getbbox()
        if not bbox:return Image.new('RGBA',(1,1))
        # Keep fixed cap height, so line metrics are stable across text.
        out=out.crop((0,1,w,17));return out.resize((w*scale,16*scale),Image.Resampling.NEAREST)
    def item(self,im,c,local):
        if not c['start']<=local<c['end']:return []
        style=self.theme['roles'][c['role']];age=local-c['start'];scale=style['scale']
        if style['motion']=='pop' and age<6:scale=max(2,scale-2+(age//3))
        y=c['y']+(6 if age<3 and style['motion']=='step' else 0);rects=[]
        if c['role']=='FACT_PANEL':
            widths=[self.line(t,style['font'],scale,style['color'],style['accent'],()).width for t in c['lines']]+[self.line(t,'PIXEL_BODY',3,'white','white',()).width for t in c['english']]
            w=max(widths)+36;h=len(c['lines'])*(12*style['scale']+15)+12+len(c['english'])*48+10
            ImageDraw.Draw(im).rectangle(((1080-w)//2,y-4,(1080+w)//2,y+h),fill=self.colors['navy'],outline=self.colors['teal'],width=3)
        for text in c['lines']:
            layer=self.line(text,style['font'],scale,style['color'],style['accent'],tuple(c.get('highlight',[])))
            x=(1080-layer.width)//2
            if layer.width>930:raise ValueError(f'Text too wide: {c["role"]} {text} ({layer.width})')
            im.alpha_composite(layer,(x,y));b=layer.getbbox();rects.append({'role':c['role'],'lang':'ko','rect':[x+b[0],y+b[1],x+b[2],y+b[3]],'text':text});y+=12*style['scale']+15
        y+=12
        for text in c['english']:
            layer=self.line(text,'PIXEL_BODY',3,'white','white',());x=(1080-layer.width)//2
            if layer.width>930:raise ValueError('English too wide: '+text)
            im.alpha_composite(layer,(x,y));b=layer.getbbox();rects.append({'role':c['role'],'lang':'en','rect':[x+b[0],y+b[1],x+b[2],y+b[3]],'text':text});y+=48
        return rects

def intersection(a,b):return max(0,min(a[2],b[2])-max(a[0],b[0]))*max(0,min(a[3],b[3])-max(a[1],b[1]))
class Overlay:
    def __init__(self):self.type=TypographyTheme()
    def frame(self,native,shot,local,anchors,check=True):
        factor=1080//native.width
        if (native.width*factor,native.height*factor)!=(1080,1920):raise ValueError('Non-integer native upscale')
        im=native.convert('RGB').resize((1080,1920),Image.Resampling.NEAREST).convert('RGBA');bounds=[]
        for c in shot['labels']+shot['captionPlan']:bounds+=self.type.item(im,c,local)
        event=shot['emphasisEvent'];preset=config('EFFECT_PRESETS')['presets'][event['preset']];age=local-event['frame']
        if preset['spark'] and 0<=age<14 and event['target'] in anchors:
            a=anchors[event['target']];cx,cy=a['point'];d=ImageDraw.Draw(im)
            for j in range(6):
                theta=j*math.tau/6;r=145+age*3;x=round((cx+math.cos(theta)*r)/4)*4;y=round((cy+math.sin(theta)*r)/4)*4
                d.rectangle((x-4,y-12,x+4,y+12),fill=self.type.colors['yellow']);d.rectangle((x-12,y-4,x+12,y+4),fill=self.type.colors['yellow'])
        if check:
            safe=self.type.theme['safeRect']
            for b in bounds:
                r=b['rect']
                if r[0]<safe[0] or r[1]<safe[1] or r[2]>safe[2] or r[3]>safe[3]:raise ValueError(f'Caption outside safe region {shot["id"]}/{local}: {b}')
                for subject in ('head','outer'):
                    if subject in anchors and intersection(r,anchors[subject]['rect'])>0:raise ValueError(f'Caption covers {subject} {shot["id"]}/{local}')
            for i,a in enumerate(bounds):
                for b in bounds[i+1:]:
                    if intersection(a['rect'],b['rect'])>0:raise ValueError(f'Text collision {shot["id"]}/{local}: {a["text"]} / {b["text"]}')
        return im.convert('RGB'),{'localFrame':local,'texts':bounds,'fallbacks':0}
