"""Native dither -> integer Nearest -> persistent UI -> optional fixed scanlines."""
from pathlib import Path
import sys
import numpy as np
from PIL import Image,ImageDraw
E=Path(__file__).resolve().parent;sys.path.insert(0,str(E.parent))
from common import read,digest
from typography import TypographyTheme,intersection
from state import ExperimentState,validate_numeric,numeric_text,timeline_stage

BAYER=np.array([[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]],dtype=np.float32)/16-.5

def native_post(image,profile,background_mask=None):
    a=np.asarray(image.convert('RGB'),dtype=np.float32); h,w=a.shape[:2]; post=profile['post']; cfg=post['orderedDither']
    step=255/(cfg['levelsPerChannel']-1); threshold=np.tile(BAYER,((h+3)//4,(w+3)//4))[:h,:w,None]
    a=np.clip(np.round((a+threshold*step*cfg['strength'])/step)*step,0,255)
    if background_mask is not None:
        mask=np.asarray(background_mask.convert('L'))>127; noise=post['backgroundNoise']
        rng=np.random.default_rng(noise['seed']); n=rng.integers(-noise['amplitude'],noise['amplitude']+1,(h,w,1))
        a=np.clip(a+n*mask[:,:,None],0,255)
    return Image.fromarray(a.astype('uint8'))

class GameOverlay:
    def __init__(self,fixture,profile):
        self.spec=fixture; self.profile=profile; self.type=TypographyTheme('ko');self.states=[ExperimentState(o) for o in fixture['objects']]
        validate_numeric(fixture['numeric'])
        # Versioned color keys isolate shared V5 text-cache entries.
        self.keys={k:profile['version']+'_'+digest(profile['colors'])[:12]+'_'+k for k in profile['colors']}
        self.type.colors.update({self.keys[k]:v for k,v in profile['colors'].items()})
        texts=[fixture['title'],fixture['chapter'],*fixture['ui'].values(),numeric_text(fixture['numeric']),'회전 중','완료',*[o['label'] for o in fixture['objects']]]
        for o in fixture['objects']:
            for value in [o['previousValue'],o['currentValue']]:
                text=numeric_text({'kind':'STATE','meaning':o['observedProperties'][0],'units':o['displayUnits'],'definition':o['definition'],'source':o['evidenceStatus'],'sourceRefs':o.get('sourceRefs'),'value':value})
                texts.extend([text,'처음 '+text])
        dummy={'shots':[{'labels':[],'captionPlan':[{'role':'PIXEL_TITLE','lines':texts,'english':[]} ,{'role':'PIXEL_BODY','lines':texts,'english':[]}]}]}
        self.fontQA=self.type.preflight(dummy)

    def text(self,im,text,role,bounds,semantic=None,center=None):
        p=self.profile; style=p['roles'][role]; color=p['semantics'][semantic or style['semantic']]; key=self.keys[color]
        layer=self.type.line(text,style['font'],style['scale'],key,key,())
        x,y=center or style['center']; x=round(x-layer.width/2); y=round(y)
        if layer.width>960: raise ValueError('Text too long for game frame: '+text)
        im.alpha_composite(layer,(x,y)); b=layer.getbbox()
        if b: bounds.append({'role':role,'text':text,'semantic':semantic or style['semantic'],'rect':[x+b[0],y+b[1],x+b[2],y+b[3]]})

    def frame(self,native,f,receipts,background_mask=None,post=True):
        p=self.profile; w,h=p['output']; factor=w//native.width
        if native.width*factor!=w or native.height*factor!=h: raise ValueError('Noninteger upscale')
        scene=native_post(native,p,background_mask) if post else native.convert('RGB')
        scene=scene.resize((w,h),Image.Resampling.NEAREST)
        im=Image.new('RGBA',(w,h),p['colors']['NAVY']);d=ImageDraw.Draw(im);b=[]
        outer=p['frame']['outer'];vp=p['frame']['viewport']
        d.rectangle(outer,fill=p['colors']['PANEL'],outline=p['colors']['PURPLE'],width=p['frame']['borderPx'])
        # Fixed 224 output-pixel translation, preserving exact 2x native pixels.
        crop=scene.crop((vp[0],vp[1]+224,vp[2],vp[3]+224));im.paste(crop,(vp[0],vp[1]))
        d.rectangle(vp,outline=p['colors']['WHITE'],width=p['frame']['viewportBorderPx'])
        self.text(im,self.spec['title'],'FIXED_TITLE',b)
        self.text(im,self.spec['chapter'],'CHAPTER_TITLE',b)
        self.text(im,numeric_text(self.spec['numeric']),'INFO',b,'EXPLANATION',(540,306))
        values=[]
        for i,(obj,state) in enumerate(zip(self.spec['objects'],self.states)):
            value=state.at(f,receipts.get(obj['objectId']));values.append(value);x=self.spec['assetPresets']['labelPositions'][i][0]
            self.text(im,obj['label'],'OBJECT_LABEL',b,center=(x,1114))
            def number(v):return numeric_text({'kind':'STATE','meaning':obj['observedProperties'][0],'units':obj['displayUnits'],'definition':obj['definition'],'source':obj['evidenceStatus'],'sourceRefs':obj.get('sourceRefs'),'value':v})
            self.text(im,'처음 '+number(obj['previousValue']),'OBJECT_LABEL',b,center=(x,1174))
            self.text(im,number(value['value']),'RESULT_VALUE',b,value['semantic'],(x,1234))
            if value['pending']: self.text(im,'회전 중','OBJECT_LABEL',b,'EXPLANATION',(x,1330))
            elif value['committed']: self.text(im,'완료','OBJECT_LABEL',b,'SUCCESS',(x,1330))
        done=all(v['committed'] for v in values)
        body=self.spec['ui']['after' if done else 'during' if f>=min(o['operation']['startFrame'] for o in self.spec['objects']) else 'before']
        self.text(im,body,'BODY',b,'PRINCIPLE' if done else 'EXPLANATION')
        self.text(im,self.spec['ui']['definition'],'INFO',b,center=(540,1562))
        self.text(im,self.spec['ui']['provenance'],'OBJECT_LABEL',b,center=(540,1620))
        self.text(im,self.spec['ui']['ending' if done else 'initialEnding'],'ENDING_CHOICE',b,center=(540,1700))
        safe=p['frame']['safe']
        for j,box in enumerate(b):
            r=box['rect']
            if r[0]<safe[0] or r[1]<safe[1] or r[2]>safe[2] or r[3]>safe[3]: raise ValueError('Text outside safe frame '+str(box))
            if any(intersection(r,q['rect']) for q in b[j+1:]): raise ValueError('Text collision '+str(box))
            if intersection(r,vp): raise ValueError('UI covers experiment viewport')
        result=im.convert('RGB'); scan=p['post']['scanline']
        if post and scan['enabled']:
            a=np.array(result);a[::scan['period']]=(a[::scan['period']].astype(np.float32)*(1-scan['opacity'])).astype('uint8');result=Image.fromarray(a)
        return result,{'frame':f,'values':values,'stages':[timeline_stage(o,f) for o in self.spec['objects']],'textBounds':b,'glyphFallbacks':0,'technicalOnly':True}
