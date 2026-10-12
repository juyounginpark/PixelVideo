"""Compose authored semantic typography after native pixel rendering; local audio only."""
import argparse,json,subprocess,sys,hashlib
from pathlib import Path
from PIL import Image,ImageDraw
import imageio_ffmpeg
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R));sys.path.append(str(R.parent/'minsu_v3'));sys.path.append(str(R.parent/'minsu_v2'))
from typography import EditorialOverlay,sheet
from effects import audio_events
from audio import AudioSynchronizer,mux,FF
from editorial import validate

def main():
    p=argparse.ArgumentParser();p.add_argument('--job',type=Path,default=R/'ep06');p.add_argument('--output',type=Path);p.add_argument('--sample',action='store_true');p.add_argument('--preview',action='store_true');p.add_argument('--preflight',action='store_true');a=p.parse_args()
    job=a.job;spec=json.loads((job/'episode.json').read_text('utf-8'));fx=json.loads((job/'effects.json').read_text('utf-8'))
    (job/'EDITORIAL_PLAN_QA.json').write_text(json.dumps(validate(spec),ensure_ascii=False,indent=2),'utf-8')
    anchors=json.loads((job/('preflight_anchors.json' if a.preflight else 'anchors.json')).read_text('utf-8'))
    renderer=EditorialOverlay();sheet(R/'review/typography.png')
    first,last=spec['sampleFrames'] if a.sample else (0,spec['durationFrames'])
    if a.preflight:
        errors=[]
        for f in range(first,last):
            try:renderer.frame(Image.new('RGB',(540,960),'#17374B'),f,spec,fx,anchors[str(f)])
            except Exception as e:errors.append({'frame':f,'error':str(e)})
        result={'frames':last-first,'errors':errors};(job/'PREFLIGHT_QA.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),'utf-8');print('PREFLIGHT_UI',last-first,'errors',len(errors));print(json.dumps(errors[:8],ensure_ascii=False));return 1 if errors else 0
    def picture(f):return renderer.frame(Image.open(job/'frames'/f'{f:04}.png'),f,spec,fx,anchors[str(f)])
    if a.preview:
        out=job/'preview';out.mkdir(exist_ok=True);frames=sorted(int(x.stem) for x in (job/'frames').glob('*.png') if str(int(x.stem)) in anchors)
        if len(frames)>30:frames=sorted(set([first,last-1]+[(s['startFrame']+s['endFrame'])//2 for s in spec['shots'] if first<=s['startFrame']<last]+[f for f in range(first,last,15) if a.sample]))
        frames=[f for f in frames if first<=f<last and str(f) in anchors]
        canvas=Image.new('RGB',(1080,510*((len(frames)+3)//4)),'#102237');d=ImageDraw.Draw(canvas)
        for i,f in enumerate(frames):
            im,qa=picture(f);im.save(out/f'{f:04}.png');x=i%4*270;y=i//4*510;canvas.paste(im.resize((270,480)),(x,y+30));d.text((x+8,y+7),f'{f:04} / {f/30:.2f}s',fill='white')
        canvas.save(out/('sample_sheet.jpg' if a.sample else 'storyboard.jpg'),quality=95);print('PREVIEW_COMPLETE',len(frames));return 0
    if not a.output:p.error('--output is required for video')
    done=set(json.loads((job/'render_manifest.json').read_text('utf-8'))['completed'])
    if not all(f in done and (job/'frames'/f'{f:04}.png').is_file() for f in range(first,last)):raise ValueError('Incomplete source frames')
    out=job/('sample' if a.sample else 'delivery');out.mkdir(exist_ok=True);silent=out/'silent.mp4';a.output.parent.mkdir(exist_ok=True)
    command=[FF,'-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1080x1920','-r','30','-i','-','-an',
       '-vf','scale=out_color_matrix=bt709:out_range=tv,setparams=range=limited:color_primaries=bt709:color_trc=bt709:colorspace=bt709',
       '-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709','-movflags','+faststart',str(silent)]
    reports=[]
    with (out/'encode.log').open('w') as log:
        proc=subprocess.Popen(command,stdin=subprocess.PIPE,stderr=log)
        try:
            for f in range(first,last):
                im,report=picture(f);reports.append(report);proc.stdin.write(im.tobytes())
                if f%120==0:print('COMPOSING',f,flush=True)
        finally:proc.stdin.close()
        if proc.wait():raise RuntimeError('Encode failed')
    events=audio_events(fx)
    events += [dict(frame=326,time=326/30,sound='soft_pop',event='Tracked molecule changes position',gainDb=-9,duck=False),dict(frame=388,time=388/30,sound='soft_whoosh',event='Contact slider accelerates along mobile surface',gainDb=-8,duck=False)]
    selected=[{**e,'sourceFrame':e['frame'],'frame':e['frame']-first,'time':(e['frame']-first)/30} for e in events if first<=e['frame']<last]
    mix=AudioSynchronizer().build((last-first)/30,selected,out/'audio',track_id=spec['audioTrack'],mood=spec['audioMood'])
    loud=mux(silent,mix,a.output);count,duration=imageio_ffmpeg.count_frames_and_secs(str(a.output));reader=imageio_ffmpeg.read_frames(str(a.output));metadata=next(reader);reader.close()
    assert count==last-first and abs(duration-(last-first)/30)<.04
    assert metadata['size']==(1080,1920) and metadata['fps']==30 and metadata['audio_codec']=='aac'
    qa={'fullDecodePassed':True,'metadata':metadata,'frameCount':count,'sourceFrameRange':[first,last],'uiFramesValidated':len(reports),
        'loudness':loud,'effectCounts':fx['counts'],'ttsEnabled':False,'source':spec['source'],'sha256':hashlib.sha256(a.output.read_bytes()).hexdigest(),
        'limits':['Authored molecular diagram, not physical simulation','No real-time playback or listening approval implied']}
    (out/'FINAL_QA.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),'utf-8');(out/'ui_qa.json').write_text(json.dumps(reports,ensure_ascii=False),'utf-8')
    print('VIDEO_COMPLETE',a.output)
    return 0

if __name__=='__main__':raise SystemExit(main())
