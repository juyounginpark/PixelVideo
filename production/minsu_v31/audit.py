"""Evidence from the encoded film, plus preservation and native pixel checks."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import imageio_ffmpeg
R=Path(__file__).resolve().parent;ROOT=R.parents[1]
sys.path.insert(0,str(R))
from typography import EditorialOverlay

def run(job,video,sample):
    spec=json.loads((job/'episode.json').read_text('utf-8'));start,end=spec['sampleFrames'] if sample else (0,spec['durationFrames'])
    out=job/('sample_review' if sample else 'review');out.mkdir(exist_ok=True)
    width,height=270,480;size=width*height*3;fps=30
    wanted=set(range(0,end-start,6 if sample else 15))|{end-start-1}
    if not sample:
        for s in spec['shots']:
            wanted.update([s['startFrame'],s['startFrame']+2,s['endFrame']-1])
            for e in s['events']:wanted.update(max(0,min(end-1,e['frame']+d)) for d in (-3,0,3,9,18))
    images={};diffs=[];previous=None;i=0
    command=[imageio_ffmpeg.get_ffmpeg_exe(),'-v','error','-i',str(video),'-an','-vf',f'scale={width}:{height}','-pix_fmt','rgb24','-f','rawvideo','-']
    with (out/'decode.log').open('w') as log:
        proc=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=log)
        while True:
            data=proc.stdout.read(size)
            if not data:break
            if len(data)!=size:raise RuntimeError('Truncated decode')
            current=np.frombuffer(data,np.uint8).reshape(height,width,3)
            if previous is not None:diffs.append({'frame':start+i,'meanDifference':float(np.abs(current.astype(float)-previous).mean()),'brightnessDifference':float(current.mean()-previous.mean())})
            if i in wanted:images[start+i]=Image.fromarray(current.copy())
            previous=current.copy();i+=1
        proc.stdout.close()
        if proc.wait():raise RuntimeError('Decode failure')
    assert i==end-start
    font=ImageFont.truetype(str(ROOT/'production/minsu_v2/fonts/NanumGothic-ExtraBold.ttf'),22)
    def sheet(frames,name,cols=4):
        canvas=Image.new('RGB',(width*cols,510*((len(frames)+cols-1)//cols)),'#102237');d=ImageDraw.Draw(canvas)
        for n,f in enumerate(frames):
            x=n%cols*width;y=n//cols*510;canvas.paste(images[f],(x,y+30));d.text((x+8,y+6),f'{f:04} / {f/30:.2f}s',font=font,fill='white')
        canvas.save(out/name,quality=95)
    if sample:
        frames=sorted(images)
        for n in range(0,len(frames),16):sheet(frames[n:n+16],f'encoded_sample_{n//16}.jpg')
    else:
        for s in spec['shots']:
            frames=sorted(f for f in images if s['startFrame']<=f<s['endFrame'])
            sheet(frames,s['id']+'.jpg')
        chosen=[]
        for s in spec['shots']:
            mid=(s['startFrame']+s['endFrame'])//2;chosen.append(min(images,key=lambda f:abs(f-mid)))
        sheet(chosen,'storyboard.jpg')
    boundaries={s['startFrame'] for s in spec['shots']}
    cut_free=[d for d in diffs if d['frame'] not in boundaries]
    native=Image.open(job/'frames'/'0411.png').convert('RGB');assert native.size==(540,960)
    up=np.asarray(native.resize((1080,1920),Image.Resampling.NEAREST));blocks=up.reshape(960,2,540,2,3)
    nearest_ok=bool(np.all(blocks==blocks[:,0:1,:,0:1,:]))
    nativeqa=json.loads((job/'native_qa.json').read_text('utf-8'))
    densities={m['texelsPerUnit'] for m in nativeqa['materials'] if m['texelsPerUnit'] is not None};assert densities=={16}
    # Inspection magnification only; no sharpening or image fabrication.
    anchors=json.loads((job/'anchors.json').read_text('utf-8'));cx,cy=anchors['411']['slider']['point'];cx=int(cx/2);cy=int(cy/2)
    # Exercise the real compositor, rather than merely re-testing Pillow's resize.
    # Frame 306 has semantic labels but no reaction particles; mask the actual UI.
    fx=json.loads((job/'effects.json').read_text('utf-8'))
    source=Image.open(job/'frames'/'0306.png').convert('RGB')
    actual,layout=EditorialOverlay().frame(source,306,spec,fx,anchors['306'])
    expected=np.asarray(source.resize((1080,1920),Image.Resampling.NEAREST))
    mask=np.ones((1920,1080),dtype=bool)
    for item in layout['text']:
        x0,y0,x1,y1=item['rect'];mask[max(0,int(y0)-16):min(1920,int(y1)+17),max(0,int(x0)-16):min(1080,int(x1)+17)]=False
    fraction=float(np.all(np.asarray(actual)==expected,axis=2)[mask].mean())
    assert fraction==1.0,('Actual composite modifies native pixels outside UI',fraction)
    assert mask.sum()>1500000
    crop=native.crop((cx-75,cy-65,cx+75,cy+85)).resize((600,600),Image.Resampling.NEAREST)
    proof=Image.new('RGB',(1080,720),'#102237');d=ImageDraw.Draw(proof)
    proof.paste(native.resize((360,640),Image.Resampling.NEAREST),(0,40));proof.paste(crop,(440,60))
    d.text((20,12),'540×960 실제 네이티브 렌더',font=font,fill='white');d.text((460,12),'접촉체 윤곽·텍셀 확대 (Nearest)',font=font,fill='white')
    proof.save(out/'pixel_proof.jpg',quality=96)
    before=json.loads((R/'review/preservation_before.json').read_text('utf-8'))
    changes=[p for p,sha in before.items() if not (ROOT/p).is_file() or hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=sha]
    assert not changes,changes
    final=json.loads((job/('sample' if sample else 'delivery')/'FINAL_QA.json').read_text('utf-8'))
    audio=json.loads((job/('sample' if sample else 'delivery')/'audio/audio_qa.json').read_text('utf-8'))
    assert final['fullDecodePassed'] and audio['peakPassed'] and audio['loopClickCheckPassed'] and audio['bgmCoveragePassed']
    assert max((e['syncErrorSeconds'] for e in audio['events']),default=0)<=1/48000
    qa={'video':str(video),'decodedFrames':i,'final':final,'preservation':{'checked':len(before),'changed':changes},
        'nearest2xBeforeUI':nearest_ok,'actualCompositePixelCheck':{'frame':306,'pixelsOutsideUI':int(mask.sum()),'exactNearestMatchFraction':fraction},'materialTexelsPerWorldUnit':list(densities),'native':nativeqa,
        'identicalAdjacentFrames':sum(d['meanDifference']==0 for d in cut_free),
        'largeBrightnessChangesWithinShots':[d for d in cut_free if abs(d['brightnessDifference'])>20],
        'audioEventCount':len(audio['events']),'maxAudioPlacementError':max((e['syncErrorSeconds'] for e in audio['events']),default=0),
        'visualReview':'Pending separate qualitative observation. These checks do not award editorial quality.',
        'limits':['Diagram motion is authored, not a physical calculation','No real-time playback, human listening or phone app test']}
    (out/'QA.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),'utf-8');(out/'frame_differences.json').write_text(json.dumps(diffs),'utf-8')
    print('AUDIT_COMPLETE',i,'preserved',len(before),'sameFrames',qa['identicalAdjacentFrames'])

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--job',type=Path,default=R/'ep06');p.add_argument('--video',type=Path,required=True);p.add_argument('--sample',action='store_true');a=p.parse_args();run(a.job,a.video,a.sample)
