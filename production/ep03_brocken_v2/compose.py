from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
import math,sys,ast,subprocess,json
import numpy as np
import imageio_ffmpeg
from functools import lru_cache
R=Path(__file__).resolve().parent;E=R.parent.parent/'exports';W,H,FPS,DURATION=720,1280,24,28
PHOTO=Image.open(R.parent/'ep03_brocken/brocken_photo.jpg').convert('RGB')
def font(n):return ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf',n)
def txt(d,p,st,n=34,color='#F5F0DD',anchor='la',stroke=0):d.text(p,st,font=font(n),fill=color,anchor=anchor,stroke_width=stroke,stroke_fill='#173B43')
def ease(x):x=max(0,min(1,x));return x*x*(3-2*x)
def lerp(a,b,q):return a+(b-a)*q
source=(R.parent/'ep02_pet/compose.py').read_text(encoding='utf-8');node=next(n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name=='shell')
exec(compile(ast.Module(body=[node],type_ignores=[]),'<shell>','exec'));SHELL=shell()
@lru_cache(maxsize=48)
def plate(i):
    im=Image.open(R/'frames'/f'{i:05d}.png').convert('RGB').crop((24,72,408,756))
    im=im.resize((360,640),Image.Resampling.LANCZOS)
    a=np.asarray(im,dtype=float);im=Image.fromarray(np.clip(np.round(a/8)*8,0,255).astype('uint8'))
    return im.resize((W,H),Image.Resampling.NEAREST)

def figure(d,cx,cy,scale,angle,shadow=False):
    def box(coords,fill):d.rectangle(tuple(int(v) for v in coords),fill=fill)
    skin='#E1B58E';hair='#2F333A';coat='#438B8A';pants='#304957'
    if shadow:skin=hair=coat=pants='#456A71'
    def rect(x0,y0,x1,y1,fill):box((cx+x0*scale,cy+y0*scale,cx+x1*scale,cy+y1*scale),fill)
    rect(-25,-75,25,-24,skin);rect(-25,-80,25,-65,hair);rect(-31,-20,31,60,coat)
    rect(-27,60,-4,122,pants);rect(5,60,27,122,pants)
    # Same rigid shoulder rotation for the demonstrator and his projection.
    sx,sy=cx+36*scale,cy-12*scale
    ex=sx+math.sin(angle)*65*scale;ey=sy+math.cos(angle)*65*scale
    d.line((sx,sy,ex,ey),fill=coat,width=max(1,int(21*scale)))
    d.ellipse((ex-11*scale,ey-11*scale,ex+11*scale,ey+11*scale),fill=skin)
    rect(-52,-15,-34,58,coat)

def diagram(t):
    u=t-14.5;im=Image.new('RGB',(W,H),'#173C47');d=ImageDraw.Draw(im)
    d.polygon([(0,1010),(276,685),(394,730),(457,1280),(0,1280)],fill='#42766E')
    # Mist field gently shifts; the explanatory motion remains the dominant cue.
    drift=math.sin(u*.9)*8
    for x,y,rr in [(572,632,109),(650,791,123),(591,970,111)]:d.ellipse((x-rr+drift,y-rr,x+rr+drift,y+rr),fill='#729A9B')
    light=ease(u/.7);shadow=ease((u-.9)/.85)
    # Rays terminate at the body. Occluded region grows behind it.
    if shadow>0:
        endpoint=(lerp(315,655,shadow),lerp(600,949,shadow))
        d.polygon([(283,475),(315,597),endpoint,(lerp(283,580,shadow),lerp(475,712,shadow))],fill='#456C70')
    sun=(88,321);d.ellipse((44,277,132,365),fill='#F3CA70')
    for k,(x,y) in enumerate([(271,440),(265,480)]):
        p=ease((u-.18-k*.12)/.55);d.line((110,341,lerp(110,x,p),lerp(341,y,p)),fill='#F3C875',width=5)
    # Travelling light markers make the order of the diagram readable.
    if .5<u<2.3:
        p=(u*.9)%1;x=lerp(110,269,p);y=lerp(341,460,p);d.ellipse((x-5,y-5,x+5,y+5),fill='#FFF1B3')
    gesture=1.50*ease((u-2.25)/.45)*(1-ease((u-3.2)/.45))
    gesture+=1.35*ease((u-4.05)/.4)*(1-ease((u-5.1)/.45))
    figure(d,294,524,1.05,gesture)
    if shadow>0:
        layer=Image.new('RGBA',im.size);ld=ImageDraw.Draw(layer);figure(ld,552,765,1.12,gesture,True)
        layer.putalpha(layer.getchannel('A').point(lambda a:int(a*shadow)));im=Image.alpha_composite(im.convert('RGBA'),layer).convert('RGB');d=ImageDraw.Draw(im)
    txt(d,(88,387),'햇빛',28,anchor='ma');txt(d,(294,686),'민수',28,anchor='ma');txt(d,(585,961),'안개',28,anchor='ma')
    return im

def photo(t):
    u=t-20.5
    im=Image.new('RGB',(W,H),'#173C47');d=ImageDraw.Draw(im)
    txt(d,(46,133),'실제 브로켄 현상',36)
    # Begin with context, then continuously zoom toward the observed silhouette.
    q=ease((u-.55)/2.0)
    crop=tuple(round(lerp(a,b,q)) for a,b in zip((0,0,640,480),(164,210,438,452)))
    ph=ImageOps.contain(PHOTO.crop(crop),(646,733),Image.Resampling.LANCZOS)
    x=(W-ph.width)//2;y=285+(733-ph.height)//2
    im.paste(ph,(x,y));d=ImageDraw.Draw(im)
    # A short external marker points to the actual photographed glory, no new shadow.
    if u>.6 and u<2.2:
        center=(x+ph.width*.37,y+ph.height*.63)
        d.line((center[0]-50,center[1]+70,center[0]-8,center[1]+12),fill='#F1D189',width=3)
    txt(d,(46,1190),'Mick Garratt / CC BY-SA 2.0',22)
    return im

CAPTIONS=[
 (0,2.75,['내가 손을 들자,','안개 속 거인도 들었다.']),
 (2.75,3.8,[]),
 (3.8,5.7,['이번엔 갑자기 손을 내렸다.']),
 (5.7,8.5,['옆으로 한 발 옮겨도,','동작이 정확히 겹쳤다.']),
 (8.5,10.6,[]),
 (10.6,12,['뒤를 돌아보니,']),
 (12,14.5,['해가 민수의 등을 비추고 있었다.']),
 (14.5,16.7,['햇빛이 몸에 가려지면서']),
 (16.7,18.5,['앞쪽 안개에 그림자가 생긴다.']),
 (18.5,20.5,['거인은,','민수 자신의 그림자였다.']),
 (20.5,23,['실제로 관찰되는','브로켄 현상.']),
 (23,25.5,['안개가 거리 감각을 흐려','더 거대하게 보일 수 있다.']),
 (25.5,28,['내가 멈추면,','저것도 멈춘다.'])]
def wrap(lines,width=604):
    d=ImageDraw.Draw(Image.new('RGB',(1,1)));result=[]
    for line in lines:
        words=line.split(' ');cur=''
        for word in words:
            nxt=(cur+' '+word).strip()
            if cur and d.textbbox((0,0),nxt,font=font(34))[2]>width:result.append(cur);cur=word
            else:cur=nxt
        if cur:result.append(cur)
    assert len(result)<=2,result
    return result
def frame(t):
    if t<14.5:im=plate(min(348,int(t*24)+1)).copy()
    elif t<20.5:im=diagram(t)
    elif t<25.5:im=photo(t)
    else:im=plate(min(408,349+int((t-25.5)*24))).copy()
    d=ImageDraw.Draw(im)
    if t<14.5 or t>=25.5:
        d.rectangle((43,88,115,124),fill='#213E47');txt(d,(51,92),'각색',22)
    elif t<20.5:
        d.rectangle((43,88,163,124),fill='#254B51');txt(d,(51,92),'원리 도식',22)
    if 2.75<=t<3.8:
        layer=Image.new('RGBA',(W,H));ld=ImageDraw.Draw(layer);ld.rectangle((68,154,652,307),fill=(17,47,57,231))
        txt(ld,(360,176),'산에서 나를',40,anchor='ma');txt(ld,(360,231),'따라 하는 거인',44,anchor='ma')
        im=Image.alpha_composite(im.convert('RGBA'),layer).convert('RGB')
    lines=wrap(next(lines for a,b,lines in CAPTIONS if a<=t<b))
    if lines:
        y=1049-(len(lines)-1)*23
        layer=Image.new('RGBA',(W,H));ld=ImageDraw.Draw(layer)
        ld.rounded_rectangle((42,y-17,678,y+46*len(lines)+11),radius=4,fill=(17,43,50,232))
        for j,line in enumerate(lines):txt(ld,(360,y+j*46),line,34,anchor='ma')
        im=Image.alpha_composite(im.convert('RGBA'),layer).convert('RGB')
    # Device identity is emphasized only at entry and exit; story occupies 90.25%.
    device=(1-ease(t/.8)) if t<.8 else (ease((t-26.7)/1.1) if t>26.7 else 0)
    x=round(18+36*device);y=round(32+72*device);ww=720-2*x;hh=round(ww*16/9)
    bg=Image.blend(Image.new('RGB',(W,H),'#B8D4B2'),SHELL,device)
    bg.paste(im.resize((ww,hh),Image.Resampling.NEAREST),(x,y))
    if device>.7:
        txt(ImageDraw.Draw(bg),(360,49),'MINSU',22,'#355A57','ma')
    if t<.28:
        yy=y+round(t/.28*hh);ImageDraw.Draw(bg).rectangle((x,yy,x+ww-1,min(y+hh-1,yy+2)),fill='#DCEBC8')
    return bg

if '--preview' in sys.argv:
    times=[.75,1.7,3.1,4.7,6.9,9.45,12.8,15.1,17.4,19.4,22.5,27.2]
    if '--draft' in sys.argv:
        original=plate
        def plate(i):
            candidates=[int(p.stem) for p in (R/'frames').glob('*.png')];return original(min(candidates,key=lambda f:abs(f-i)))
    sheet=Image.new('RGB',(1440,1920))
    for j,t in enumerate(times):sheet.paste(frame(t).resize((360,640)),((j%4)*360,(j//4)*640))
    sheet.save(E/'MINSU_EP03_BROCKEN_v2_PREVIEW.jpg',quality=95);sys.exit()
out=E/'MINSU_EP03_BROCKEN_ACTION_SILENT_v2.mp4';ff=imageio_ffmpeg.get_ffmpeg_exe()
cmd=[ff,'-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','720x1280','-r','24','-i','-','-an','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(out)]
with open(R/'encode.log','w') as log:
    p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
    for i in range(FPS*DURATION):p.stdin.write(frame(i/FPS).tobytes())
    p.stdin.close()
    if p.wait():raise RuntimeError('encode failure')
print('COMPLETE',out)
