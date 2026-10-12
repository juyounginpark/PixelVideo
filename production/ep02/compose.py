"""Composite the independently rendered 3D animation and 2D typography into a silent reel."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps
import subprocess, imageio_ffmpeg, math, json, sys

ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parent.parent
EXPORT=PROJECT/'exports';EXPORT.mkdir(exist_ok=True)
W,H,FPS,DURATION=720,1280,24,43
FONT='C:/Windows/Fonts/malgunbd.ttf'
REG='C:/Windows/Fonts/malgun.ttf'
NAVY='#17243B'; WHITE='#F7F7F2'; YELLOW='#FFD65A'; TEAL='#72D2CC'
fonts={}
def font(n,bold=True):
    k=(n,bold)
    if k not in fonts:fonts[k]=ImageFont.truetype(FONT if bold else REG,n)
    return fonts[k]
def tx(d,xy,s,n=34,fill=WHITE,anchor='la',bold=True):d.text(xy,s,font=font(n,bold),fill=fill,anchor=anchor)
def panel(d,rect,fill=NAVY,edge='#C8D9E7',width=2):
    x0,y0,x1,y1=rect;c=10
    pts=[(x0+c,y0),(x1-c,y0),(x1,y0+c),(x1,y1-c),(x1-c,y1),(x0+c,y1),(x0,y1-c),(x0,y0+c)]
    d.polygon([(x+4,y+6) for x,y in pts],fill='#0B1322')
    d.polygon(pts,fill=fill);d.line(pts+[pts[0]],fill=edge,width=width)
def caption(d,lines,label=None,y=995,highlight=None):
    height=54+len(lines)*48+(26 if label else 0)
    panel(d,(45,y,675,y+height))
    yy=y+20
    if label:tx(d,(70,yy),label,20,TEAL);yy+=30
    for s in lines:tx(d,(360,yy),s,35,YELLOW if s==highlight else WHITE,'ma');yy+=48
def chip(d,s,y=170):
    width=d.textbbox((0,0),s,font=font(23))[2]+38
    panel(d,(46,y,46+width,y+48),edge=TEAL)
    tx(d,(65,y+9),s,23,TEAL)
def top(d,actual=False):
    panel(d,(45,62,675,119),edge='#5C748C')
    tx(d,(65,76),'민수의 미스터리',24)
    tx(d,(651,78),'EP. 02',20,YELLOW,'ra')
    tx(d,(49,132),'실제 자료' if actual else '민수의 체험은 각색',16,'#DDE8E7')

photo=Image.open(PROJECT/'research/namuwiki/assets/vending_sdot.jpg').convert('RGB')
opening=None
def photo_scene(t):
    im=Image.new('RGB',(W,H),NAVY);d=ImageDraw.Draw(im)
    for x in range(0,W,36):d.line((x,0,x,H),fill='#1C2B44')
    for y in range(0,H,36):d.line((0,y,W,y),fill='#1C2B44')
    # A subtle move inside a source-photo card; never fabricate details.
    scale=1+.025*math.sin((t-23)/16*math.pi)
    ph=ImageOps.fit(photo,(int(588*scale),int(740*scale)),method=Image.Resampling.LANCZOS)
    left=(ph.width-588)//2;upper=(ph.height-740)//2
    ph=ph.crop((left,upper,left+588,upper+740))
    im.paste(ph,(66,225));d=ImageDraw.Draw(im)
    d.rectangle((63,222,657,968),outline='#B7CAD7',width=3)
    tx(d,(70,975),'사진: SDOT / Seattle Met 게재 · 촬영일 미확인',16,'#C9D6DF')
    return im

def frame(t):
    global opening
    if t<23:
        idx=min(552,int(t*FPS)+1)
        im=Image.open(ROOT/'frames'/f'{idx:05d}.png').convert('RGB')
    else:im=photo_scene(t)
    d=ImageDraw.Draw(im)
    top(d,t>=23)
    if t<3:
        caption(d,['이거 뭐 나오는 건데?'],'민수',y=1000)
        chip(d,'여섯 버튼이 전부 MYSTERY',y=185)
    elif t<5:
        panel(d,(45,188,675,355),edge=YELLOW,width=3)
        tx(d,(360,208),'음료를 고를 수 없는',42,WHITE,'ma')
        tx(d,(360,272),'자판기',54,YELLOW,'ma')
    elif t<9:
        caption(d,['체리네.'],'민수')
    elif t<12:
        chip(d,'며칠 뒤…')
    elif t<16:
        chip(d,'2018년 6월')
        caption(d,['없어졌네.'],'민수')
    elif t<20:
        chip(d,'난간에 남은 쪽지 · 재현')
        caption(d,['산책 갔음.'],'쪽지의 문구',highlight='산책 갔음.')
    elif t<23:
        pass
    elif t<27:
        chip(d,'미국 · 시애틀')
        caption(d,['실제로 있던 자판기다.'],highlight='실제로 있던 자판기다.')
    elif t<31:
        chip(d,'운영자는 공개되지 않았다')
        caption(d,['전기를 대주던 옆 가게도','주인은 모른다고 했다.'])
    elif t<35:
        chip(d,'2018년 6월 · 사라짐 보도')
        caption(d,['자판기는 사라졌고,','‘산책 갔음’ 쪽지가 남았다.'])
        tx(d,(70,1197),'근거: CHS 2018.06.30 / Atlas Obscura 2018.07.02',15,'#BBCDDD')
    elif t<38:
        chip(d,'확인된 기록은 여기까지')
        caption(d,['사라진 이유는','이 자료로 확인되지 않는다.'])
    elif t<40.5:
        chip(d,'음료 이름 대신 적힌 말')
        d.rectangle((254,449,484,526),outline=YELLOW,width=4)
        caption(d,['MYSTERY'],highlight='MYSTERY')
    else:
        # Return to the opening geometry, then hold its exact first state.
        base=Image.open(ROOT/'frames'/'00001.png').convert('RGB')
        dd=ImageDraw.Draw(base);top(dd,False)
        caption(dd,['이거 뭐 나오는 건데?'],'민수',y=1000)
        chip(dd,'여섯 버튼이 전부 MYSTERY',y=185)
        a=min(1,(t-40.5)/1.2)
        im=Image.blend(im,base,a)
    return im

preview='--preview' in sys.argv or '--early' in sys.argv
if preview:
    times=[0,3.5,6,10,14,18,21,25,29,33,36,42.9]
    if '--early' in sys.argv:times=[0,3.5,6,10,25,29,33,36]
    sheet=Image.new('RGB',(4*270,3*510),'#0B1322')
    for j,t in enumerate(times):
        im=frame(t);im.save(ROOT/f'preview_{t:g}.png')
        im=im.resize((270,480));sheet.paste(im,((j%4)*270,(j//4)*510))
        ImageDraw.Draw(sheet).text(((j%4)*270+8,(j//4)*510+484),f'{t:g}s',font=font(17),fill='white')
    sheet.save(EXPORT/'MINSU_EP02_contact_sheet.jpg',quality=92)
    print('PREVIEW_COMPLETE');sys.exit()

out=EXPORT/'MINSU_EP02_SILENT_v1.mp4'
ff=imageio_ffmpeg.get_ffmpeg_exe()
cmd=[ff,'-hide_banner','-loglevel','warning','-y','-f','rawvideo','-vcodec','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(out)]
with open(ROOT/'encode.log','w',encoding='utf-8') as log:
    p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
    for i in range(FPS*DURATION):
        im=frame(i/FPS);p.stdin.write(im.tobytes())
        if i%120==0:print(f'COMPOSITE {i}/{FPS*DURATION}',flush=True)
    p.stdin.close();rc=p.wait()
    if rc:raise RuntimeError(f'ffmpeg failed {rc}')
(EXPORT/'MINSU_EP02_manifest.json').write_text(json.dumps({'file':out.name,'width':W,'height':H,'fps':FPS,'duration_seconds':DURATION,'frames':FPS*DURATION,'audio':False,'scene':'production/ep02/MINSU_EP02.blend','photo':'research/namuwiki/assets/vending_sdot.jpg','photo_credit':'Courtesy SDOT / Seattle Met','photo_publication_rights':'not verified; review copy'},ensure_ascii=False,indent=2),encoding='utf-8')
print(f'COMPLETE {out}',flush=True)
