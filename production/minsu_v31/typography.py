"""Six semantic typography roles at delivery resolution, after nearest upscale."""
import math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parent;ROOT=R.parents[1]
FONTS={'display':ROOT/'production/ep02_cinema/fonts/Jua-Regular.ttf','body':ROOT/'production/minsu_v2/fonts/NanumGothic-ExtraBold.ttf','pixel':ROOT/'production/retro_voxel/fonts/Galmuri11-Bold.ttf','symbol':Path('C:/Windows/Fonts/seguisym.ttf')}
PALETTE={'ink':'#102237','white':'#FFF6E8','amber':'#FFC554','cyan':'#70E1EF','coral':'#FF796A','muted':'#AECDD8'}
ROLES={
 'HOOK_TITLE':dict(font='display',size=113,stroke=8,color='white',accent='amber',motion='pop',gap=9),
 'EXPLANATION_CAPTION':dict(font='body',size=61,stroke=5,color='white',accent='amber',motion='slide',gap=17),
 'IMPACT_CAPTION':dict(font='display',size=148,stroke=10,color='white',accent='amber',motion='impact',gap=6),
 'MICRO_LABEL':dict(font='pixel',size=33,stroke=2,color='muted',accent='cyan',motion='reveal',gap=9),
 'FACT_PANEL':dict(font='body',size=44,stroke=0,color='white',accent='coral',motion='panel',gap=14),
 'RESULT_TITLE':dict(font='display',size=110,stroke=7,color='white',accent='cyan',motion='rise',gap=10)}

def ease(p):
    p=max(0,min(1,p));return p*p*(3-2*p)

class Typography:
    def __init__(self):self.fonts={}
    def font(self,name,size):
        key=(name,size)
        if key not in self.fonts:self.fonts[key]=ImageFont.truetype(str(FONTS[name]),size)
        return self.fonts[key]
    def draw(self,im,item,frame,center=510):
        role=item['role'];style=ROLES[role];age=frame-item['startFrame'];remaining=item['endFrame']-frame
        if age<0 or remaining<=0:return []
        p=ease(age/8);motion=style['motion'];scale=1
        if motion=='pop':scale=.84+.24*ease(age/4)-.08*ease((age-4)/5)
        if motion=='impact':scale=.58+.57*ease(age/3)-.15*ease((age-3)/5)
        size=round(style['size']*scale);font=self.font(style['font'],size);stroke=max(1,round(style['stroke']*scale))
        lines=[s.replace('−','-').replace('–','-') for s in item['lines']];wide=max(font.getlength(s) for s in lines)
        if wide>850:
            size=math.floor(size*850/wide);font=self.font(style['font'],size)
        y=item.get('y') or (1350 if role=='EXPLANATION_CAPTION' else 280)
        shift=(1-p)*25 if motion in ('slide','rise','panel') else 0
        if motion=='rise':y+=shift
        layer=Image.new('RGBA',im.size);d=ImageDraw.Draw(layer);bounds=[]
        if role=='FACT_PANEL':
            height=len(lines)*(size+style['gap'])+30
            d.rectangle((95,y-22,925,y+height),fill='#142B40',outline=PALETTE['cyan'],width=3)
        for j,text in enumerate(lines):
            if role=='RESULT_TITLE' and age<j*9:continue
            glyphs=[self.font('symbol',size) if ch in '↓↑→' or (ch=='…' and style['font']=='display') else font for ch in text]
            w=sum(g.getlength(ch) for g,ch in zip(glyphs,text));x=center-w/2+(shift if motion=='slide' else 0)
            yy=y+j*(size+style['gap']);baseline=yy-font.getbbox('가',anchor='ls')[1];mask=set()
            for word in item.get('highlight',[]):
                at=text.find(word)
                while at>=0:
                    mask.update(range(at,at+len(word)));at=text.find(word,at+1)
            dx=x
            for k,ch in enumerate(text):
                color=PALETTE[style['accent'] if k in mask else style['color']]
                glyph=glyphs[k]
                d.text((dx+3,baseline+7),ch,font=glyph,anchor='ls',fill='#081222',stroke_width=stroke+2,stroke_fill='#081222')
                d.text((dx,baseline),ch,font=glyph,anchor='ls',fill=color,stroke_width=stroke,stroke_fill=PALETTE['ink']);dx+=glyph.getlength(ch)
            actual=d.textbbox((x,baseline),text,font=font,anchor='ls',stroke_width=stroke+2)
            bounds.append([actual[0]-3,actual[1],actual[2]+4,actual[3]+7])
        opacity=min(1,age/4) if motion in ('slide','reveal','panel') else 1
        opacity*=min(1,remaining/4)
        if opacity<1:layer.putalpha(layer.getchannel('A').point(lambda v:round(v*opacity)))
        im.alpha_composite(layer)
        return [{'role':role,'rect':b,'lines':lines} for b in bounds]

    def label(self,im,text,xy,accent='cyan',size=33,center=False,panel=True):
        text=text.replace('−','-').replace('–','-')
        d=ImageDraw.Draw(im);font=self.font('pixel',size);w=font.getlength(text);x,y=xy
        if center:x-=w/2
        if panel:d.rectangle((x-12,y-8,x+w+12,y+size+10),fill='#102237',outline=PALETTE[accent],width=2)
        d.text((x,y),text,font=font,anchor='lt',fill=PALETTE[accent],stroke_width=1,stroke_fill='#102237')
        return [x-12,y-8,x+w+12,y+size+10]

class EditorialOverlay:
    def __init__(self):self.type=Typography()
    def frame(self,native,frame,spec,timeline,anchors):
        if native.size!=(540,960):raise ValueError('Native image must be 540x960')
        im=native.convert('RGB').resize((1080,1920),Image.Resampling.NEAREST).convert('RGBA')
        shot=next(s for s in spec['shots'] if s['startFrame']<=frame<s['endFrame']);phase=shot['phase'];bounds=[]
        t=self.type;d=ImageDraw.Draw(im)
        # Each auxiliary mark has a declared semantic purpose.
        if shot.get('diagram'):
            text='분자 모식도 · 크기·시간 확대' if phase in ('structure','path','discovery') else '조건 비교 모식도' if phase=='compare' else '접촉부 모식도'
            r=t.label(im,text,(86,186),size=30,accent='muted',panel=False);bounds.append({'role':'MICRO_LABEL','rect':r,'lines':[text]})
        if phase=='structure':
            r=t.label(im,'표면: 자리 이동',(105,580),accent='amber',size=36);bounds.append({'role':'MICRO_LABEL','rect':r})
            r=t.label(im,'내부: 제자리 진동',(112,1190),accent='cyan',size=34);bounds.append({'role':'MICRO_LABEL','rect':r})
        if phase=='path':
            r=t.label(im,'물 분자 하나를 따라가면',(112,470),accent='amber',size=33);bounds.append({'role':'MICRO_LABEL','rect':r})
        if phase=='contact':
            a=anchors['surface'];x,y=a['point'];d.line([(220,590),(220,y-45),(x,y)],fill=PALETTE['amber'],width=5)
            r=t.label(im,'접촉면',(125,526),accent='amber',size=43);bounds.append({'role':'MICRO_LABEL','rect':r})
        if phase=='compare':
            for x,title,color in [(260,'−100°C','cyan'),(760,'−7°C','amber')]:
                r=t.label(im,title,(x,660),accent=color,size=53,center=True);bounds.append({'role':'FACT_PANEL','rect':r})
            if frame>=552:
                for x,txt in [(260,'마찰 큼'),(760,'마찰 작음')]:
                    r=t.label(im,txt,(x,1200),accent='coral',size=42,center=True);bounds.append({'role':'FACT_PANEL','rect':r})
            r=t.label(im,'강철–얼음 실험 · Weber 외 (2018)',(105,1515),accent='muted',size=28,panel=False);bounds.append({'role':'FACT_PANEL','rect':r})
        if phase=='factors':
            for f,x,word,color in [(636,140,'온도','amber'),(659,410,'압력','coral'),(693,680,'속도','cyan')]:
                if frame>=f:
                    r=t.label(im,word,(x,505),accent=color,size=48);bounds.append({'role':'MICRO_LABEL','rect':r})
        if phase=='before_after':
            for text,xy,color in [('출발 위치',(150,570),'muted'),('이동한 뒤',(640,1100),'amber')]:
                r=t.label(im,text,xy,accent=color,size=35);bounds.append({'role':'MICRO_LABEL','rect':r})
        if phase=='result':
            r=t.label(im,'얼음이 미끄러운 이유',(110,1490),accent='muted',size=33,panel=False);bounds.append({'role':'MICRO_LABEL','rect':r})
        # Short motion marks around the real event target. No ambient confetti.
        for event in timeline['EffectTimeline']:
            if not event['frame']<=frame<event['endFrame']:continue
            if event['type'] not in ('PIXEL_SPARK','REACTION_BURST','QUESTION_POP'):continue
            a=anchors.get(event['target']);
            if not a:continue
            x,y=a['point'];r=max(65,min(190,(a['rect'][2]-a['rect'][0])*.65));age=(frame-event['frame'])/max(1,event['endFrame']-event['frame'])
            if event['type']=='QUESTION_POP':
                t.label(im,'?',(min(885,a['rect'][2]+22),max(550,a['rect'][1]-30)),accent='amber',size=72,panel=False)
            else:
                for j in range(6):
                    ang=j*math.tau/6;xx=round(x+math.cos(ang)*r*(1+.30*age));yy=round(y+math.sin(ang)*r*(1+.30*age))
                    if event['type']=='PIXEL_SPARK':
                        d.line((xx-9,yy,xx+9,yy),fill=PALETTE['amber'],width=4);d.line((xx,yy-9,xx,yy+9),fill=PALETTE['amber'],width=4)
                    else:d.line((xx,yy,xx+math.cos(ang)*24,yy+math.sin(ang)*24),fill=PALETTE['white'],width=5)
        for item in shot['typography']:bounds.extend(t.draw(im,item,frame))
        for b in bounds:
            x0,y0,x1,y1=b['rect']
            if not (65<=x0<x1<=1008 and 160<=y0<y1<=1610):raise ValueError(f'Text outside safe layout at {frame}: {b}')
        # Native scientific objects can be layered behind labels only outside their focal center.
        protected=['minsu'] if 'minsu' in anchors else (['molecule'] if phase=='path' else ['slider'] if phase=='discovery' else [])
        for name in protected:
            ar=anchors[name]['rect']
            for b in bounds:
                br=b['rect'];intersection=max(0,min(ar[2],br[2])-max(ar[0],br[0]))*max(0,min(ar[3],br[3])-max(ar[1],br[1]))
                if intersection>0:raise ValueError(f'Text covers {name} at {frame}: {b}')
        return im.convert('RGB'),{'frame':frame,'phase':phase,'text':bounds,'visualMode':shot['visualMode']}

def sheet(path):
    t=Typography();im=Image.new('RGBA',(1080,1920),'#102237')
    samples=[('HOOK_TITLE',['단단한 얼음,','왜 미끄러울까?'],['왜 미끄러울까?']),('EXPLANATION_CAPTION',['닿는 표면을 보자'],['표면']),
             ('IMPACT_CAPTION',['저항 ↓'],['저항']),('MICRO_LABEL',['표면: 자리 이동'],['표면']),('FACT_PANEL',['강철–얼음 실험 · −100°C'],['−100°C']),
             ('RESULT_TITLE',['움직이는 표면'],['표면'])]
    ys=[110,440,655,1020,1250,1505]
    for (role,lines,hi),y in zip(samples,ys):
        t.label(im,role,(90,y-40),accent='muted',size=22,panel=False)
        t.draw(im,dict(role=role,lines=lines,highlight=hi,startFrame=0,endFrame=100,y=y),30,center=540)
    im.convert('RGB').save(path)
