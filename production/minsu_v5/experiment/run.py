"""Run a technical experiment style fixture. Does not select or consume a topic."""
from pathlib import Path
import argparse,sys,subprocess,time
E=Path(__file__).resolve().parent;sys.path.insert(0,str(E.parent));sys.path.insert(0,str(E))
from PIL import Image,ImageDraw
import imageio_ffmpeg
from common import read,write,sha
from overlay import GameOverlay

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--compose-only',action='store_true');args=ap.parse_args();review=E/'review';review.mkdir(exist_ok=True)
    if not args.compose_only:
        cmd=['C:/Program Files/Blender Foundation/Blender 5.0/blender.exe','-b','--python-exit-code','1','--python',str(E/'render.py')]
        with (review/'render.log').open('w',encoding='utf-8') as log:result=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT)
        if result.returncode:raise RuntimeError('Render failed: '+str(review/'render.log'))
    t=time.perf_counter();spec=read(E/'fixture.json');profile=read(E/'profile.json');index=read(review/'native.json');overlay=GameOverlay(spec,profile)
    root=E.parents[2];output=root/'exports/MINSU_EXPERIMENT_STYLE_PREVIEW.mp4';temp=output.with_name(output.stem+'.pending.mp4')
    cmd=[imageio_ffmpeg.get_ffmpeg_exe(),'-y','-f','rawvideo','-pix_fmt','rgb24','-s','1080x1920','-r','30','-i','-','-an','-c:v','libx264','-threads','4','-preset','fast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(temp)]
    selected=[0,45,75,76,105,106,149];images=[];qa=[]
    # Fixed background mask only outside a conservative geometry region. It never touches UI.
    mask=Image.new('L',tuple(profile['native']),255);ImageDraw.Draw(mask).rectangle((30,290,510,660),fill=0)
    with (review/'encode.log').open('w',encoding='utf-8') as log:
        process=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
        try:
            for f in range(spec['durationFrames']):
                rec=index['frames'][str(f)];path=Path(rec['path'])
                if sha(path)!=rec['sha256']:raise ValueError('Native cache integrity failed')
                with Image.open(path) as native:
                    im,record=overlay.frame(native,f,index['receipts'],mask);process.stdin.write(im.tobytes());qa.append(record)
                    if f in selected:
                        im.save(review/f'frame_{f:03}.png');images.append((f,im.resize((270,480))))
                    if f==106:
                        raw,_=overlay.frame(native,f,index['receipts'],mask,post=False);raw.save(review/'post_off.png')
        finally:process.stdin.close()
        if process.wait():raise RuntimeError('Encode failed')
    temp.replace(output)
    sheet=Image.new('RGB',(270*len(images),512),'#211D37');d=ImageDraw.Draw(sheet)
    for i,(f,im) in enumerate(images):sheet.paste(im,(270*i,32));d.text((270*i+10,8),f'frame {f} / {f/30:.2f}s',fill='white')
    sheet.save(review/'timeline.jpg',quality=93)
    # Check the actual final bitstream and extract a representative decoded frame.
    ff=imageio_ffmpeg.get_ffmpeg_exe();probe=subprocess.run([ff,'-v','error','-i',str(output),'-f','null','-'],capture_output=True,text=True)
    if probe.returncode or probe.stderr.strip():raise RuntimeError('MP4 decode failure '+probe.stderr)
    subprocess.run([ff,'-y','-v','error','-i',str(output),'-vf','select=eq(n\\,106)','-frames:v','1',str(review/'decoded_106.png')],check=True)
    preserved=read(review/'preservation_before.json');changed=[p for p,h in preserved.items() if sha(root/p)!=h]
    write(review/'technical_qa.json',{'technical':'PASS' if not changed else 'FAIL','font':overlay.fontQA,'frames':qa,'decodedEntireMP4':True,'sourceAndDeliveredFilesChanged':changed,'nativeRender':read(review/'render_metrics.json'),'composeSeconds':time.perf_counter()-t,'output':str(output),'outputSha256':sha(output),'textCacheHits':overlay.type.cacheHits,'textCacheMisses':overlay.type.cacheMisses,'scientificEpisodeApproval':False,'strawOriginalCompared':False,'audio':'not part of this technical fixture'})
    print(str(output));print('Compose seconds:',round(time.perf_counter()-t,3))

if __name__=='__main__':main()
