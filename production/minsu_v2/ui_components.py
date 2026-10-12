"""Optional event UI components. Not automatically inserted into every episode."""
from pathlib import Path
import math
from PIL import ImageDraw, ImageFont
R=Path(__file__).resolve().parent
PIXEL=R.parent/'retro_voxel/fonts/Galmuri11-Bold.ttf'
TEXT=R/'fonts/NanumGothic-ExtraBold.ttf'

def font(size,pixel=True):return ImageFont.truetype(str(PIXEL if pixel else TEXT),size)

def panel(im,x,y,w,h,color='#192239',border='#7B7ED1'):
    d=ImageDraw.Draw(im);d.rectangle((x+7,y+7,x+w+7,y+h+7),fill='#10131C')
    d.rectangle((x,y,x+w,y+h),fill=color,outline=border,width=4)
    for cx,cy in [(x,y),(x+w-9,y),(x,y+h-9),(x+w-9,y+h-9)]:d.rectangle((cx,cy,cx+9,cy+9),fill=border)
    return (x,y,x+w+7,y+h+7)

def fitted(d,text,f,maxwidth):
    if d.textlength(text,font=f)>maxwidth:raise ValueError('UI text too wide; rewrite: '+text)

class FactTooltip:
    def draw(self,im,event,t):
        x,y=event.get('position',(110,390));w=760;d=ImageDraw.Draw(im);f=font(40);body=font(38,False)
        fitted(d,event['title'],f,w-48);fitted(d,event['text'],body,w-48)
        rect=panel(im,x,y,w,154)
        d.text((x+24,y+17),event['title'],font=f,fill='#FFE08A')
        d.text((x+24,y+84),event['text'],font=body,fill='#E8ECF6')
        return [rect]

class ImpactCaption:
    def draw(self,im,event,t):
        elapsed=t-event['start'];scale=1+.10*math.sin(min(1,max(0,elapsed/.18))*math.pi)
        f=font(round(92*scale),False);d=ImageDraw.Draw(im);text=event['text'];fitted(d,text,f,760)
        width=d.textlength(text,font=f);x=495-width/2;y=event.get('y',430)
        d.text((x,y),text,font=f,fill='#FFE06B',stroke_width=6,stroke_fill='#202430')
        return [d.textbbox((x,y),text,font=f,stroke_width=6)]

class TimeLapseHUD:
    def draw(self,im,event,t):
        speed=event['speed'];actual=event['sourceSecondsPerTimelineSecond']
        if speed<=0 or abs(speed-actual)>1e-8:raise ValueError('HUD speed must match simulated time scale')
        x,y=event.get('position',(120,330));d=ImageDraw.Draw(im);rect=panel(im,x,y,235,83,border='#88DCC5')
        for dx in (20,43):d.polygon([(x+dx,y+22),(x+dx,y+58),(x+dx+19,y+40)],fill='#98EACE')
        d.text((x+79,y+12),f'×{speed:g}',font=font(46),fill='#E7FFED')
        return [rect]

class DialogueBox:
    def draw(self,im,event,t):
        lines=event['lines']
        if not 1<=len(lines)<=2:raise ValueError('Dialogue needs 1..2 lines')
        x,y=event.get('position',(100,1200));w=780;d=ImageDraw.Draw(im);f=font(43)
        for line in lines:fitted(d,line,f,w-66)
        rect=panel(im,x,y,w,220,color='#F2F3DF',border='#487CC0')
        d.rectangle((x+11,y+11,x+w-11,y+209),outline='#487CC0',width=2)
        total=sum(map(len,lines));ratio=min(1,max(0,(t-event['start'])/event.get('typingDuration',.9)));remaining=math.floor(total*ratio)
        for j,line in enumerate(lines):
            show=line[:remaining];remaining=max(0,remaining-len(line))
            d.text((x+29,y+35+j*68),show,font=f,fill='#233755' if j==0 else '#167F73')
        if ratio>=1:d.polygon([(x+w-45,y+175),(x+w-23,y+175),(x+w-34,y+188)],fill='#345580')
        return [rect]

class QuizPanel:
    def draw(self,im,event,t):
        options=event['options']
        if len(options)!=2:raise ValueError('Quiz expects exactly two options')
        correct=event['correctIndex']
        if correct not in (0,1):raise ValueError('Verified correct option required')
        x,y=event.get('position',(105,500));w=770;d=ImageDraw.Draw(im);f=font(43)
        fitted(d,event['question'],f,w-50);rect=panel(im,x,y,w,270,border='#75B7D4')
        d.text((x+25,y+20),event['question'],font=f,fill='#FFE08A')
        reveal=t>=event.get('revealTime',float('inf'))
        for j,text in enumerate(options):
            fitted(d,text,f,310);left=x+25+j*365
            color='#216D61' if reveal and j==correct else '#303D56'
            d.rectangle((left,y+95,left+340,y+180),fill=color,outline='#87DEBF' if reveal and j==correct else '#63728D',width=3)
            d.text((left+24,y+115),text,font=f,fill='#FFFFFF')
        if reveal:d.text((x+25,y+210),'정답: '+options[correct],font=font(32),fill='#A7F6D2')
        return [rect]

COMPONENTS={c.__name__:c for c in (FactTooltip,ImpactCaption,TimeLapseHUD,DialogueBox,QuizPanel)}

if __name__=='__main__':
    from PIL import Image
    examples=[('FactTooltip',{'title':'비늘 사이 통로','text':'물은 피부 표면을 따라 이동'}),
              ('ImpactCaption',{'text':'발견!','start':0}),('TimeLapseHUD',{'speed':8,'sourceSecondsPerTimelineSecond':8}),
              ('DialogueBox',{'lines':['물이 모이는 곳은','비늘 사이의 작은 틈!'],'start':0}),
              ('QuizPanel',{'question':'모인 물은 어디로?','options':['입으로','혈관으로'],'correctIndex':0,'revealTime':.5})]
    out=R/'component_previews';out.mkdir(exist_ok=True)
    for name,event in examples:
        im=Image.new('RGB',(1080,1920),'#343D46');bounds=COMPONENTS[name]().draw(im,event,1)
        for x,y,x1,y1 in bounds:assert 90<=x<x1<=900 and 220<=y<y1<=1500,(name,bounds)
        im.save(out/f'{name}.png')
    print('OPTIONAL_UI_PREVIEWS',len(examples))
