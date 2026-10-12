"""Full-resolution 2D overlays over constant-resolution native Blender frames."""
from pathlib import Path
import argparse, json, subprocess, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg
from ui_components import COMPONENTS
from layout import place_label
R=Path(__file__).resolve().parent;ROOT=R.parents[1];FF=imageio_ffmpeg.get_ffmpeg_exe()
FONT=R/'fonts/NanumGothic-ExtraBold.ttf';PIXEL=R.parent/'retro_voxel/fonts/Galmuri11-Bold.ttf'
SAFE=(90,220,900,1500)

class PaletteQuantizationPass:
    def apply(self,im):
        a=np.asarray(im.convert('RGB'),dtype=np.float32)
        return Image.fromarray(np.clip(np.round(a/5)*5,0,255).astype('uint8'))

class SubtitleRenderer:
    def draw(self,im,event,t):
        d=ImageDraw.Draw(im);font=ImageFont.truetype(str(FONT),event.get('fontSize',66));bounds=[]
        lines=event['lines']
        if not 1<=len(lines)<=2 or any(not str(line).strip() for line in lines):raise ValueError('Captions require one or two nonempty lines')
        y=event.get('y',1326 if len(lines)==2 else 1380)
        for j,text in enumerate(lines):
            length=d.textlength(text,font=font)
            if length>790:raise ValueError('Caption too wide; rewrite: '+text)
            x=event.get('centerX',495)-length/2
            color='#83F4C1' if j==event.get('highlightLine') else '#FFFFFF'
            d.text((x+2,y+j*88+5),text,font=font,fill='#171C29',stroke_width=5,stroke_fill='#171C29')
            d.text((x,y+j*88),text,font=font,fill=color,stroke_width=4,stroke_fill='#17202A')
            b=d.textbbox((x,y+j*88),text,font=font,stroke_width=5);bounds.append(b)
        return bounds

class ObjectLabel:
    def draw(self,im,event,anchor):
        if anchor[2]<=0: return []
        d=ImageDraw.Draw(im);f=ImageFont.truetype(str(PIXEL),36);text=event['text'];w=d.textlength(text,font=f)+40;h=70
        # Anchor-derived position, constrained only to the safe rect; the leader preserves association.
        x,y,_,_=place_label(anchor,(w,h),event.get('protectedRects',()))
        d.line([(anchor[0],anchor[1]),(x+15,y+h)],fill='#C1FFF0',width=3)
        d.rectangle((x,y,x+w,y+h),fill='#18262E',outline='#76D9CA',width=3)
        d.text((x+20,y+12),text,font=f,fill='#A6F5D8')
        return [(x,y,x+w,y+h)]

class AchievementPopup:
    def draw(self,im,event,t):
        d=ImageDraw.Draw(im);f=ImageFont.truetype(str(PIXEL),40);text=event['text'];w=d.textlength(text,font=f)+115
        x=495-w/2;y=340-12*(1-min(1,(t-event['start'])/.18))
        d.rectangle((x+7,y+7,x+w+7,y+108+7),fill='#111924')
        d.rectangle((x,y,x+w,y+108),fill='#142F37',outline='#82DBB4',width=4)
        # Original open-book mark, not a copied star or platform interface.
        d.line([(x+22,y+42),(x+39,y+48),(x+56,y+42),(x+56,y+70),(x+39,y+76),(x+22,y+70),(x+22,y+42)],fill='#F8D373',width=4)
        d.text((x+76,y+28),text,font=f,fill='#FFE388')
        return [(x,y,x+w,y+108)]

class OverlayComposer:
    def __init__(self,spec,anchors):
        self.spec=spec;self.anchors=anchors;self.subtitle=SubtitleRenderer();self.label=ObjectLabel();self.achievement=AchievementPopup()
    def frame(self,index):
        t=(index-1)/self.spec['fps'];path=R/'frames'/f'{index:04}.png'
        if not path.exists():raise FileNotFoundError(path)
        im=Image.open(path).convert('RGB')
        if im.size!=tuple(self.spec['internalResolution']):raise ValueError('Unexpected native pixel size')
        if self.spec.get('rendererProfile')!='MINSU_V21':im=PaletteQuantizationPass().apply(im)
        im=im.resize(tuple(self.spec['outputResolution']),Image.Resampling.NEAREST)
        return self.overlay(im,index)
    def overlay(self,im,index):
        t=(index-1)/self.spec['fps']
        shot=next(s for s in self.spec['shots'] if s['startTime']<=t<s['endTime']);bounds=[]
        tag=shot.get('representationLabel')
        if tag is None and self.spec.get('episodeId')=='MINSU_EP04_V2' and shot['shotId'] in ('SHOT_04','SHOT_05','SHOT_06','SHOT_07'):
            tag='확대 모식도' if shot['shotId'] in ('SHOT_04','SHOT_05') else '물길 강조'
        if tag:
            d=ImageDraw.Draw(im);f=ImageFont.truetype(str(FONT),30)
            d.text((100,255),tag,font=f,fill='#F2EDD6',stroke_width=2,stroke_fill='#333C40')
        for c in shot['captionTimeline']:
            if c['start']<=t<c['end']:bounds+=self.subtitle.draw(im,c,t)
        panels=0
        for e in shot['uiEvents']:
            if e['start']<=t<e['end']:
                if e['kind']=='ObjectLabel':bounds+=self.label.draw(im,e,self.anchors[str(index)][e['anchor']])
                elif e['kind']=='AchievementPopup':bounds+=self.achievement.draw(im,e,t)
                elif e['kind'] in COMPONENTS:bounds+=COMPONENTS[e['kind']]().draw(im,e,t)
                else:raise ValueError('Unsupported UI kind '+e['kind'])
                panels+=1
        if panels>2:raise ValueError('Too many panels')
        for b in bounds:
            if not (SAFE[0]<=b[0]<b[2]<=SAFE[2] and SAFE[1]<=b[1]<b[3]<=SAFE[3]):raise ValueError(('UI outside safe rect',index,b))
        # Face anchor check: bounding sphere projected check is intentionally conservative.
        collisions=[]
        for subject in self.spec.get('faceAnchors',('minsu_face','thorny_head') if self.spec.get('episodeId')=='MINSU_EP04_V2' else ()):
            x,y,z=self.anchors[str(index)][subject]
            if z>0:
                for b in bounds:
                    if b[0]-32<x<b[2]+32 and b[1]-32<y<b[3]+32:collisions.append(subject)
        return im,{'frame':index,'shot':shot['shotId'],'bounds':bounds,'faceAnchorOverlaps':collisions,'panels':panels}

def run(preview=False):
    spec=json.loads((R/'episode.json').read_text('utf-8'));anchors=json.loads((R/'anchors.json').read_text('utf-8'));composer=OverlayComposer(spec,anchors)
    if preview:
        folder=R/'preview';folder.mkdir(exist_ok=True)
        samples=[1,15,24,50,68,112,163,235,280,352,390,470,530,605,680,728,741,820,865,920,985,1060]
        frames=[f for f in samples if (R/'frames'/f'{f:04}.png').exists()]
        sheet=Image.new('RGB',(270*5,510*math.ceil(len(frames)/5)),'#182127');draw=ImageDraw.Draw(sheet);records=[]
        for j,f in enumerate(frames):
            im,qa=composer.frame(f);records.append(qa);im.save(folder/f'{f:04}.png')
            sheet.paste(im.resize((270,480)),((j%5)*270,(j//5)*510));draw.text(((j%5)*270+10,(j//5)*510+484),f'{(f-1)/30:.2f}s | {qa["shot"]}',fill='white')
        sheet.save(folder/'contact.jpg',quality=92);(folder/'ui_qa.json').write_text(json.dumps(records,indent=2),'utf-8');print('PREVIEW_COMPLETE');return
    export=ROOT/'exports/MINSU_EP04_V2_SILENT.mp4'
    cmd=[FF,'-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1080x1920','-r','30','-i','-',
         '-an','-vf','scale=out_color_matrix=bt709:out_range=tv','-c:v','libx264','-preset','fast','-crf','18',
         '-pix_fmt','yuv420p','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709','-movflags','+faststart',str(export)]
    records=[]
    with open(R/'encode.log','w') as log:
        p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
        try:
            for index in range(1,1081):
                im,qa=composer.frame(index);records.append(qa);p.stdin.write(im.tobytes())
                if index%120==0:print('COMPOSE',index,flush=True)
        finally:p.stdin.close()
        if p.wait():raise RuntimeError('FFmpeg failed')
    (R/'ui_qa.json').write_text(json.dumps(records,indent=2),'utf-8')
    print('SILENT_ENCODE_COMPLETE',export)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--preview',action='store_true');run(p.parse_args().preview)
