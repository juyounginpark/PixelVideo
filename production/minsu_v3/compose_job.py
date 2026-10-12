"""Compose existing native frames, semantic graphics, local music/SFX and output QA."""
import argparse,json,sys,subprocess
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R.parent/'minsu_v2'))
from graphics import EffectRenderer
from effects import audio_events
from audio import AudioSynchronizer,mux,FF
import imageio_ffmpeg

def compose(job,output=None,preview=False):
    spec=json.loads((job/'spec.json').read_text('utf-8'));timeline=json.loads((job/'effects.json').read_text('utf-8'));anchors=json.loads((job/'anchors.json').read_text('utf-8'))
    renderer=EffectRenderer();reports=[];frames=sorted(int(p.stem) for p in (job/'frames').glob('*.png'))
    if preview:frames=[f for f in frames if str(f) in anchors]
    if not preview and frames!=list(range(spec['durationFrames'])):raise ValueError('Missing frames')
    if not preview and json.loads((job/'render_manifest.json').read_text('utf-8'))['completed']!=frames:raise ValueError('Render manifest does not validate every frame')
    def frame(f,previous=None):
        im=Image.open(job/'frames'/f'{f:04}.png')
        if im.size!=(540,960):raise ValueError('Wrong native pixel resolution')
        return renderer.frame(im.resize((1080,1920),Image.Resampling.NEAREST),f,spec,timeline,anchors[str(f)],previous)
    if preview:
        out=job/'preview';out.mkdir(exist_ok=True)
        selected=frames if len(frames)<=20 else sorted(set([0,spec['durationFrames']-1]+[e['frame']+5 for e in timeline['EffectTimeline'] if e['frame']+5<spec['durationFrames']]))
        sheet=Image.new('RGB',(270*min(5,len(selected)),510*((len(selected)+4)//5)),'#18212a');d=ImageDraw.Draw(sheet)
        for i,f in enumerate(selected):
            if f not in frames:continue
            im,qa=frame(f);reports.append(qa);im.save(out/f'{f:04}.png');sheet.paste(im.resize((270,480)),((i%5)*270,(i//5)*510));d.text(((i%5)*270+8,(i//5)*510+482),str(f),fill='white')
        sheet.save(out/'contact.jpg',quality=92);(out/'qa.json').write_text(json.dumps(reports),'utf-8');return
    silent=job/'silent.mp4'
    cmd=[FF,'-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1080x1920','-r',str(spec['fps']),'-i','-',
         '-an','-vf','scale=out_color_matrix=bt709:out_range=tv,setparams=range=limited:color_primaries=bt709:color_trc=bt709:colorspace=bt709','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p',
         '-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709','-movflags','+faststart',str(silent)]
    with (job/'encode.log').open('w') as log:
        proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
        try:
            previous=None;cut_previous=None;cut_starts={s['startFrame'] for s in spec['shots']}
            for f in frames:
                if f in cut_starts:cut_previous=previous
                im,qa=frame(f,cut_previous);reports.append(qa);proc.stdin.write(im.tobytes());previous=im
        finally:proc.stdin.close()
        if proc.wait():raise RuntimeError('Encoding failed')
    mix=AudioSynchronizer().build(spec['durationFrames']/spec['fps'],audio_events(timeline),job/'audio',track_id=spec.get('audioTrack'),mood=spec['audioMood'])
    loud=mux(silent,mix,output);count,seconds=imageio_ffmpeg.count_frames_and_secs(str(output))
    reader=imageio_ffmpeg.read_frames(str(output));metadata=next(reader);reader.close()
    assert count==spec['durationFrames'] and abs(seconds-spec['durationFrames']/spec['fps'])<.04
    assert metadata['size']==(1080,1920) and metadata['fps']==spec['fps'] and metadata['audio_codec']=='aac'
    assert 'bt709' in metadata['pix_fmt'] and 'unknown' not in metadata['pix_fmt'],'Missing color metadata'
    qa={'fullDecodePassed':True,'metadata':metadata,'frameCount':count,'loudness':loud,'effectCounts':timeline['counts'],
        'uiFramesValidated':len(reports),'ttsEnabled':False,'sourceReceipt':spec.get('sourceReceipt'),
        'limits':['Projected geometry masks do not solve inter-object occlusion','No human listening approval','No retention measurement']}
    (job/'ui_qa.json').write_text(json.dumps(reports),'utf-8');(job/'FINAL_QA.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),'utf-8')
    print('VIDEO_COMPLETE',output)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--job',required=True,type=Path);p.add_argument('--output',type=Path);p.add_argument('--preview',action='store_true');a=p.parse_args()
    if not a.preview and not a.output:p.error('--output is required')
    compose(a.job,a.output,a.preview)
