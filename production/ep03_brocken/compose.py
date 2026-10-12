from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
import sys,subprocess,ast,json,math
import numpy as np
import imageio_ffmpeg
from functools import lru_cache
R=Path(__file__).resolve().parent;EXPORT=R.parent.parent/'exports';W,H=720,1280;FPS=24;DURATION=42
def font(n):return ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf',n)
def text(d,xy,st,size=32,color='#233D40',anchor='la'):d.text(xy,st,font=font(size),fill=color,anchor=anchor)
# Reuse the reviewed shell geometry, without importing episode-specific copy.
source=(R.parent/'ep02_pet/compose.py').read_text(encoding='utf-8')
node=next(n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name=='shell')
exec(compile(ast.Module(body=[node],type_ignores=[]),'<shell>','exec'))
SHELL=shell();PHOTO=Image.open(R/'brocken_photo.jpg').convert('RGB')
@lru_cache(maxsize=48)
def render(i):
    im=Image.open(R/'frames'/f'{i:05d}.png').convert('RGB')
    im=im.crop((24,85,336,640))
    arr=np.asarray(im).astype(float);im=Image.fromarray(np.clip(np.round(arr/8)*8,0,255).astype('uint8'))
    return im.resize((612,1088),Image.Resampling.NEAREST)
def diagram(t):
    im=Image.new('RGB',(612,1088),'#DDE5D6');d=ImageDraw.Draw(im)
    text(d,(306,94),'햇빛 · 민수 · 안개',34,anchor='ma')
    d.ellipse((35,250,115,330),fill='#F0CC74')
    d.polygon([(0,690),(240,560),(370,610),(400,820),(0,900)],fill='#628B80')
    for x,y in [(460,380),(500,450),(440,520),(500,590)]:d.ellipse((x-55,y-60,x+95,y+110),fill='#B0C7C3')
    # Sun is behind the observer. Parallel rays reach the mist beyond him.
    d.polygon([(247,426),(271,538),(531,686),(499,589)],fill='#89A6A0')
    d.line((115,295,236,435),fill='#D3AC5E',width=5)
    d.line((115,325,231,469),fill='#D3AC5E',width=5)
    d.rectangle((232,460,268,540),fill='#408582');d.rectangle((235,420,265,457),fill='#E1B88F');d.rectangle((232,414,268,430),fill='#34373F')
    d.line((242,537,239,579),fill='#344957',width=12);d.line((260,537,266,579),fill='#344957',width=12)
    d.ellipse((466,477,497,512),fill='#567C7C');d.rectangle((463,511,500,589),fill='#567C7C');d.line((473,585,464,651),fill='#567C7C',width=12);d.line((492,585,502,651),fill='#567C7C',width=12)
    text(d,(75,350),'햇빛',27,anchor='ma');text(d,(250,610),'민수',27,anchor='ma');text(d,(490,700),'안개 속 그림자',25,anchor='ma')
    return im
def photo(t):
    im=Image.new('RGB',(612,1088),'#E8E6D8');d=ImageDraw.Draw(im)
    text(d,(32,76),'실제 촬영 사진',32)
    source=PHOTO if t<35 else PHOTO.crop((170,220,420,440))
    ph=ImageOps.contain(source,(564,450),Image.Resampling.LANCZOS)
    im.paste(ph,((612-ph.width)//2,210))
    text(d,(32,700),'브로켄 현상',38)
    text(d,(32,764),'2016. 10. 09 / 영국',24)
    text(d,(32,1004),'Mick Garratt / CC BY-SA 2.0',22)
    return im
CAPTIONS=[
 (0,3,['내가 손을 들자,','저것도 손을 들었다.']),
 (3,6,[]),
 (6,10,['안개 속에','사람 형체가 서 있었다.']),
 (10,15,['옆으로 움직이자,','같은 방향으로 움직였다.']),
 (15,19,['몸을 낮추자,','저쪽도 낮아졌다.']),
 (19,23,['민수 뒤에는','해가 떠 있었다.']),
 (23,27,['햇빛이 민수를 지나,','앞쪽 안개에 그림자를 만든 것.']),
 (27,31,['거인의 정체는','민수 자신의 그림자였다.']),
 (31,35,['실제로 관찰되는','브로켄 현상이다.']),
 (35,39,['안개 속에선 크기를 가늠하기 어려워','거대하게 보일 수 있다.']),
 (39,42,['같이 움직일 수밖에 없었다.'])]
def frame(t):
    im=SHELL.copy();d=ImageDraw.Draw(im);text(d,(360,49),'MINSU',22,'#355A57','ma')
    if t<23:content=render(min(276,int(t*12)+1)).copy()
    elif t<31:content=diagram(t)
    elif t<39:content=photo(t)
    else:
        q=max(0,1.5-abs((t-39)-1.5));content=render(int(q*12)+1).copy()
    im.paste(content,(54,104));d=ImageDraw.Draw(im)
    tag='각색' if t<23 or t>=39 else ('원리 도식' if t<31 else '')
    if tag:
        width=d.textbbox((0,0),tag,font=font(22))[2]+20;d.rectangle((74,124,74+width,159),fill='#253A3D');text(d,(84,128),tag,22,'#F5F0DF')
    if 3<=t<6:
        d.rectangle((91,183,629,330),fill='#243E43')
        text(d,(360,199),'산에서 나를',40,'#F5EDCD','ma');text(d,(360,252),'따라 하는 거인',44,'#F5EDCD','ma')
    lines=next(lines for a,b,lines in CAPTIONS if a<=t<b)
    y=1010-(len(lines)-1)*21
    if lines:
        d.rectangle((74,y-13,646,y+42*len(lines)+8),fill='#F8F2DF')
        for j,line in enumerate(lines):
            assert d.textbbox((0,0),line,font=font(32))[2]<=544,line
            text(d,(360,y+j*42),line,32,anchor='ma')
    if t<.35:
        yy=int(104+t/.35*1088);d.rectangle((54,yy,665,min(1191,yy+3)),fill='#D6E5BD')
    return im
if '--preview' in sys.argv:
    times=[1.5,4,6.6,11.2,16.2,21,25,33]
    if '--draft' in sys.argv:
        original=render
        def render(i):
            candidates=[int(p.stem) for p in (R/'frames').glob('*.png')];return original(min(candidates,key=lambda x:abs(x-i)))
    sheet=Image.new('RGB',(1440,1280))
    for j,t in enumerate(times):sheet.paste(frame(t).resize((360,640)),((j%4)*360,(j//4)*640))
    sheet.save(EXPORT/'MINSU_EP03_BROCKEN_PREVIEW.jpg',quality=95);sys.exit()
out=EXPORT/'MINSU_EP03_BROCKEN_SILENT_v1.mp4';ff=imageio_ffmpeg.get_ffmpeg_exe()
cmd=[ff,'-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','720x1280','-r','24','-i','-','-an','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(out)]
with open(R/'encode.log','w') as log:
    p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
    for i in range(FPS*DURATION):p.stdin.write(frame(i/FPS).tobytes())
    p.stdin.close()
    if p.wait():raise RuntimeError('encode failure')
print('COMPLETE',out)
