"""Full-resolution UI; small effects rasterized on the same 540x960 pixel grid."""
import math,sys
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter
R=Path(__file__).resolve().parent;V2=R.parent/'minsu_v2';sys.path.insert(0,str(V2))
from compose import SubtitleRenderer
from layout import place_label,intersects
from effects import pop_scale,smooth
FONT=V2/'fonts/NanumGothic-ExtraBold.ttf'

class EffectRenderer:
    def frame(self,image,frame,spec,timeline,anchors,previous=None):
        im=image.convert('RGB');fps=spec['fps'];active=[e for e in timeline['EffectTimeline'] if e['frame']<=frame<e['endFrame']]
        bounds=[];report=[];protected=[a['rect'] for a in anchors.values() if a.get('protect')]
        shot=next(s for s in spec['shots'] if s['startFrame']<=frame<s['endFrame'])
        if shot.get('representationLabel'):
            d=ImageDraw.Draw(im);f=ImageFont.truetype(str(FONT),34)
            protected.append(d.textbbox((100,235),shot['representationLabel'],font=f,stroke_width=2))
        # Subject masks supplied by projected mesh geometry; missing masks never dim the whole frame.
        for e in active:
            if e['type']!='DARK_FOCUS':continue
            a=anchors[e['target']]
            if not a.get('polygons'):raise ValueError('Dark focus requires subject geometry mask')
            mask=Image.new('L',im.size);d=ImageDraw.Draw(mask)
            for poly in a['polygons']:d.polygon(poly,fill=255)
            mask=mask.filter(ImageFilter.GaussianBlur(3))
            age=(frame-e['frame'])/fps;left=(e['endFrame']-frame)/fps
            strength=.28*min(smooth(age/.18),smooth(left/.18))
            dark=Image.fromarray((np.asarray(im,dtype=float)*(1-strength)).astype('uint8'))
            im=Image.composite(im,dark,mask)
        overlay=Image.new('RGBA',(540,960));d=ImageDraw.Draw(overlay)
        for e in active:
            a=anchors.get(e['target'])
            if not a or a['depth']<=0:raise ValueError('Effect target is not visible: '+e['target'])
            x,y=a['point'];rect=a['rect'];age=(frame-e['frame'])/fps;p=(frame-e['frame'])/max(1,e['endFrame']-e['frame'])
            cx,cy=x/2,y/2;rad=max(18,min(70,(rect[2]-rect[0])/4));alpha=round(255*min(1,(1-p)*4))
            if e['type']=='PIXEL_SPARK':
                for j in range(7):
                    angle=j*math.tau/7+.2;r=rad*(1+.6*p);px=round(cx+math.cos(angle)*r);py=round(cy+math.sin(angle)*r)
                    color=[(255,211,97,alpha),(125,225,190,alpha),(232,248,224,alpha)][j%3]
                    d.line((px-3,py,px+3,py),fill=color,width=2);d.line((px,py-3,px,py+3),fill=color,width=2)
            elif e['type']=='REACTION_BURST':
                for j in range(6):
                    angle=j*math.tau/6;r=rad*(1+.25*p)
                    d.line((cx+math.cos(angle)*r,cy+math.sin(angle)*r,cx+math.cos(angle)*(r+9),cy+math.sin(angle)*(r+9)),fill=(255,216,116,alpha),width=2)
            elif e['type']=='OBJECT_HIGHLIGHT':
                bx=[v/2 for v in rect];color=(119,237,197,alpha);length=8
                for xx,yy,sx,sy in [(bx[0],bx[1],1,1),(bx[2],bx[1],-1,1),(bx[0],bx[3],1,-1),(bx[2],bx[3],-1,-1)]:
                    d.line((xx+sx*length,yy,xx,yy,xx,yy+sy*length),fill=color,width=2)
            elif e['type']=='QUESTION_POP':
                f=ImageFont.truetype(str(FONT),min(38,max(20,round((rect[3]-rect[1])*.20))))
                d.text((cx+rad*.7,rect[1]/2-35-8*p),'?',font=f,fill=(255,216,116,alpha),stroke_width=2,stroke_fill='#203039')
            report.append({'id':e['id'],'target':e['target'],'frame':frame})
        im=Image.alpha_composite(im.convert('RGBA'),overlay.resize(im.size,Image.Resampling.NEAREST))
        for e in active:
            if e['type'] not in ('IMPACT_CAPTION','DATA_REVEAL'):continue
            a=anchors[e['target']];age=(frame-e['frame'])/fps;d=ImageDraw.Draw(im)
            text=e['text']
            if e['type']=='DATA_REVEAL':
                data=e['data'];values=data.get('samples')
                if values:
                    available=[v for v in values if v['frame']<=frame]
                    if not available:continue
                    text=f"{data['label']} {available[-1]['value']}{data.get('unit','')}"
                else:text=data['label']+' '+data['value']
            size=round((62 if e['type']=='IMPACT_CAPTION' else 40)*pop_scale(age));font=ImageFont.truetype(str(FONT),size)
            w=d.textlength(text,font=font)+36;h=size+36
            label_anchor=(a['point'][0],a['rect'][1]-25) if e['type']=='IMPACT_CAPTION' else a['point']
            rect=place_label(label_anchor,(w,h),protected+bounds,safe=(95,235,895,1225))
            x,y=rect[:2]
            if e['type']=='DATA_REVEAL':d.rectangle(rect,fill='#182732',outline='#7BDABB',width=3)
            d.text((x+18,y+12),text,font=font,fill='#FFE08A',stroke_width=4,stroke_fill='#182732');bounds.append(rect)
        shot=next(s for s in spec['shots'] if s['startFrame']<=frame<s['endFrame'])
        if shot.get('representationLabel'):
            d=ImageDraw.Draw(im);f=ImageFont.truetype(str(FONT),34)
            d.text((100,235),shot['representationLabel'],font=f,fill='#E6F2DC',stroke_width=2,stroke_fill='#25313A')
            bounds.append(d.textbbox((100,235),shot['representationLabel'],font=f,stroke_width=2))
        for c in shot.get('captions',[]):
            if c['startFrame']<=frame<c['endFrame']:
                event={'lines':c['lines'],'highlightLine':c.get('highlightLine',len(c['lines'])-1),'y':c.get('y',1326),'centerX':495,'fontSize':62}
                # Measure on a temporary copy; never cover a protected event or face silently.
                tmp=im.copy();rects=SubtitleRenderer().draw(tmp,event,frame/fps)
                if any(intersects(b,p,4) for b in rects for p in protected+bounds):
                    event['y']=240;tmp=im.copy();rects=SubtitleRenderer().draw(tmp,event,frame/fps)
                    if any(intersects(b,p,4) for b in rects for p in protected+bounds):
                        raise ValueError('No safe base caption position')
                im=tmp;bounds+=rects
        for e in active:
            if e['type']=='TRANSITION_DIRECTOR':
                if e['transition']=='MATCH_CUT':continue # Native cut continuity checked by scene plan.
                if e['transition']!='WIPE':raise ValueError('Unknown transition')
                if previous is None:raise ValueError('Wipe requires preceding image')
                split=round(im.width*(frame-e['frame'])/(e['endFrame']-e['frame']))
                im.paste(previous.crop((split,0,im.width,im.height)),(split,0))
        for b in bounds:
            if not (90<=b[0]<b[2]<=900 and 220<=b[1]<b[3]<=1500):raise ValueError('UI outside safe area')
        return im.convert('RGB'),{'frame':frame,'effects':report,'textBounds':bounds,'targetCount':len(anchors)}
