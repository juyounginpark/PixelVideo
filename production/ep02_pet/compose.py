from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
import math,sys,subprocess,json
import imageio_ffmpeg
ROOT=Path(__file__).resolve().parent;PROJECT=ROOT.parent.parent;EXPORT=PROJECT/'exports'
W,H,FPS,DURATION=720,1280,24,47
FF=imageio_ffmpeg.get_ffmpeg_exe()
CREAM='#E8E6D8';INK='#252B39';MUTED='#656C71';ROSE='#6F725D';MINT='#89AAA6'
fonts={}
def font(size,bold=True):
    key=(size,bold)
    if key not in fonts:fonts[key]=ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf' if bold else 'C:/Windows/Fonts/malgun.ttf',size)
    return fonts[key]
def txt(d,xy,text,size=34,fill=INK,anchor='la',bold=True):
    text=text.replace('…','...').replace('“','"').replace('”','"').replace('·','/')
    d.text(xy,text,font=font(size,bold),fill=fill,anchor=anchor)
def pill(d,text,x=46,y=166):
    w=d.textbbox((0,0),text,font=font(21))[2]+34
    d.rounded_rectangle((x,y,x+w,y+44),radius=2,fill=CREAM,outline='#D1BDB0',width=1)
    txt(d,(x+17,y+8),text,21)
def identity(im,real=False):
    d=ImageDraw.Draw(im)
    d.rounded_rectangle((44,61,262,107),radius=2,fill=CREAM)
    txt(d,(61,71),'민수의 미스터리',23)
    txt(d,(665,77),'02',21,INK,'ra')
    # Distinguish fictional roleplay from the documented source section.
    txt(d,(47,119),'실제 자료' if real else '민수의 체험은 각색',16,MUTED)
def subtitles(im,lines,label=None):
    if not lines:return im
    layer=Image.new('RGBA',(W,H));d=ImageDraw.Draw(layer)
    hh=42*len(lines)+38+(26 if label else 0);y=1030
    d.rounded_rectangle((42,y,678,y+hh),radius=3,fill=(255,246,231,242),outline=(204,182,171,240),width=2)
    yy=y+17
    if label:txt(d,(65,yy),label,18,ROSE);yy+=28
    for line in lines:
        assert d.textbbox((0,0),line,font=font(32))[2]<590, line
        txt(d,(360,yy),line,32,INK,'ma');yy+=42
    return Image.alpha_composite(im.convert('RGBA'),layer).convert('RGB')
PHOTO=Image.open(PROJECT/'research/namuwiki/assets/vending_sdot.jpg').convert('RGB')
def actual(t):
    im=Image.new('RGB',(W,H),CREAM);d=ImageDraw.Draw(im)
    # Minimal dossier card; documentary imagery remains visibly photographic.
    txt(d,(52,176),'실제 자판기 사진',35)
    d.line((52,226,668,226),fill='#D8C2B1',width=2)
    if t<34.5:
        ph=ImageOps.contain(PHOTO,(598,735),Image.Resampling.LANCZOS)
    elif t<39:
        ph=ImageOps.fit(PHOTO.crop((110,290,650,780)),(598,735),Image.Resampling.LANCZOS)
    else:
        ph=ImageOps.contain(PHOTO,(598,735),Image.Resampling.LANCZOS)
    x=(W-ph.width)//2;y=247+(735-ph.height)//2
    d.rounded_rectangle((x-7,y-7,x+ph.width+7,y+ph.height+7),radius=8,fill='#E7D6C4')
    im.paste(ph,(x,y));d=ImageDraw.Draw(im)
    txt(d,(51,996),'사진: SDOT / Seattle Met 게재 · 촬영일 미확인',16,MUTED)
    return im

def background(t):
    if t<30:
        idx=int(t*12)+1
        return render_frame(idx)
    if t<47.5:return actual(t)
    # End with OTS returning to opening. Two-frame hold cadence matches native animation.
    local=30+min(1.999,(t-47.5)/2.5*2)
    idx=min(384,int(local*12)+1)
    im=render_frame(idx)
    if t>49.8:
        first=render_frame(1)
        im=Image.blend(im,first,min(1,(t-49.8)/.12))
    return im

def source_frame(t):
    im=background(t);identity(im,30<=t<47.5);d=ImageDraw.Draw(im)
    label=None;lines=[]
    if t<1.25:lines=['자판기가 사라졌다.']
    elif t<3.5:
        pill(d,'난간에 남은 쪽지 · 재현')
        lines=['남겨진 말은,','“산책 갔음.”']
    elif t<5.5:
        layer=Image.new('RGBA',(W,H));q=ImageDraw.Draw(layer)
        q.rounded_rectangle((73,353,647,598),radius=3,fill=(255,246,231,245))
        txt(q,(360,429),'산책 간',53,INK,'ma');txt(q,(360,497),'자판기',60,ROSE,'ma')
        im=Image.alpha_composite(im.convert('RGBA'),layer).convert('RGB')
    elif t<8.5:
        pill(d,'사라지기 전')
        lines=['처음 왔을 때부터','좀 이상한 자판기였다.']
    elif t<12:lines=['음료 이름 대신 여섯 버튼에','전부 “미스터리”라고 적혀 있었다.']
    elif t<14:lines=['무슨 음료가 나올지는…']
    elif t<17.5:lines=['눌러 보기 전에는 알 수 없었다.']
    elif t<21:lines=['나온 건 체리 콜라.','돈을 내도 음료를 고를 수는 없었다.']
    elif t<24:
        pill(d,'2018년 6월')
        lines=['다시 찾아간 날,','기계가 통째로 사라졌다.']
    elif t<27:lines=['어디로 옮겼다는 안내도 없이.']
    elif t<30:
        pill(d,'쪽지 재현')
        lines=['난간에는 딱 한 줄.','“산책 갔음.”']
    elif t<34.5:
        lines=['이 자판기는','실제로 시애틀에 있었다.']
    elif t<36.2:
        lines=['운영자는 공개되지 않았다.']
    elif t<39:
        lines=['전기를 대주던 옆 가게도','주인은 모른다고 했다.']
    elif t<43.5:
        lines=['2018년 6월의 사라짐과 쪽지는','당시 보도에도 남아 있다.']
    elif t<47.5:
        lines=['누가, 왜 옮겼는지는','이 자료로 확인되지 않는다.']
    else:
        lines=['남겨진 설명은 한 줄.','“산책 갔음.”'] if t<49.6 else ['자판기가 사라졌다.']
    return subtitles(im,lines,label)


import numpy as np
from functools import lru_cache
@lru_cache(maxsize=32)
def cached_render(index):
    image=Image.open(ROOT/'frames'/f'{index:05d}.png').convert('RGB')
    a=np.asarray(image,dtype=np.float32)
    bayer=np.array([[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]],dtype=np.float32)/16-.5
    pattern=np.tile(bayer,(image.height//4+1,image.width//4+1))[:image.height,:image.width,None]
    a=np.clip(np.round(a/8)*8,0,255).astype(np.uint8)
    return Image.fromarray(a).resize((W,H),Image.Resampling.NEAREST)
def render_frame(index):return cached_render(index).copy()
def frame(t):return source_frame(t*1.2 if t<25 else t+5)


# Only episode content and source attribution appear on screen.
def identity(im,real=False):
    pass

original_frame=frame

def shell():
    im=Image.new('RGB',(360,640),'#202437');d=ImageDraw.Draw(im)
    # Stepped pixel device silhouette, restrained mint/ink palette.
    for x,y in [(20,36),(329,83),(18,492),(333,576)]:
        d.rectangle((x,y,x+3,y+11),fill='#637288');d.rectangle((x-4,y+4,x+7,y+7),fill='#637288')
    d.rounded_rectangle((15,17,351,635),radius=36,fill='#101722')
    d.rounded_rectangle((9,8,347,630),radius=36,fill='#4B807E')
    d.rounded_rectangle((9,6,345,626),radius=34,fill='#B8D4B2',outline='#DFEACB',width=2)
    d.rounded_rectangle((22,46,338,601),radius=6,fill='#4B676A')
    d.rectangle((26,51,334,597),fill='#202C38')
    for x in [124,180,236]:
        d.ellipse((x-8,608,x+8,622),fill='#F5D484',outline='#796B61',width=1)
    return im.resize((720,1280),Image.Resampling.NEAREST)
SHELL=shell()

def boot(t):
    im=Image.new('RGB',(540,960),'#CCD7AA');d=ImageDraw.Draw(im)
    ink='#354C47'
    # Pixel avatar emblem on a boot screen, not production commentary.
    px,py,u=222,325,12
    for yy,row in enumerate(['01111110','11111111','11000011','10100101','10000001','10011001','01111110','00111100','01111110','11011011','00011000','00100100']):
        for xx,v in enumerate(row):
            if v=='1':d.rectangle((px+xx*u,py+yy*u,px+(xx+1)*u-1,py+(yy+1)*u-1),fill=ink)
    txt(d,(270,240),'민수의 미스터리',34,ink,'ma')
    txt(d,(270,535),'산책 간 자판기',30,ink,'ma')
    for k in range(6):
        d.rectangle((190+k*28,607,209+k*28,619),fill=ink if k<int(t*5)+1 else '#ABB993')
    return im

CAPTIONS=[]
def actual(t):
    im=Image.new('RGB',(720,1280),CREAM);d=ImageDraw.Draw(im)
    txt(d,(36,60),'실제 자판기',32,INK)
    ph=ImageOps.contain(PHOTO,(660,865),Image.Resampling.LANCZOS)
    im.paste(ph,((720-ph.width)//2,140))
    txt(ImageDraw.Draw(im),(36,1190),'사진 SDOT / Seattle Met',26,MUTED)
    return im

def subtitles(im,lines,label=None):
    CAPTIONS[:] = lines
    return im

def frame(t):
    im=SHELL.copy();d=ImageDraw.Draw(im)
    # Thin housing leaves 72.25 percent of the canvas for content.
    txt(d,(360,49),'MINSU',22,'#355A57','ma')
    st=max(0,min(44.999,t-.4))
    if t>45.4:st=0
    content=original_frame(st).resize((612,1088),Image.Resampling.NEAREST)
    im.paste(content,(54,104));d=ImageDraw.Draw(im)
    real=25<=st<42.5
    if not real:
        d.rectangle((74,124,140,157),fill='#253A3D')
        txt(d,(82,128),'각색',22,'#F7F1DA')
    if CAPTIONS:
        lines=[]
        for text in CAPTIONS:
            current=''
            for ch in text:
                if d.textbbox((0,0),current+ch,font=font(32))[2]>524:
                    lines.append(current);current=ch
                else:current+=ch
            if current:lines.append(current)
        top=1010-(len(lines)-1)*21
        d.rectangle((74,top-13,646,top+42*len(lines)+8),fill='#F8F2DF')
        for j,line in enumerate(lines):txt(d,(360,top+j*42),line,32,INK,'ma')
    # Boot happens over the hook; there is no waiting or loading copy.
    if t<.4:
        y=int(104+t/.4*1088)
        d.rectangle((54,y,665,min(1191,y+4)),fill='#EAF0C9')
    return im

if '--preview' in sys.argv:
    times=[0,.9,2,5,12,17,29,39]
    sheet=Image.new('RGB',(1440,1280))
    for j,t in enumerate(times):sheet.paste(frame(t).resize((360,640)),((j%4)*360,(j//4)*640))
    sheet.save(EXPORT/'MINSU_PET_TOON_PREVIEW.jpg',quality=94);sys.exit()
out=EXPORT/'MINSU_EP02_PET_TOON_SILENT_v4.mp4'
cmd=[FF,'-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','720x1280','-r','24','-i','-','-an','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(out)]
with open(ROOT/'encode.log','w') as log:
    p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
    for i in range(46*24):p.stdin.write(frame(i/24).tobytes())
    p.stdin.close()
    if p.wait():raise RuntimeError('encode failed')
print('COMPLETE',out)
