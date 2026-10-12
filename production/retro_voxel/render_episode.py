"""Manifest-driven compositing into 1080p/30fps silent H.264."""
import argparse,json,subprocess,sys
from pathlib import Path
from PIL import Image
import imageio_ffmpeg
from ui import RetroUI
def run(manifest,preview=False):
    p=Path(manifest).resolve();spec=json.loads(p.read_text(encoding='utf-8'));root=p.parent
    fps=spec['fps'];duration=spec['duration'];count=int(fps*duration)
    assert fps==30 and 35<=duration<=60
    assert sum(c['duration'] for c in spec['cuts'])==duration
    ui=RetroUI(spec['series'],spec['auxiliary'],spec['question'])
    for c in spec['cuts']:
        assert c['camera'] in 'ABCDE' and c['action'] and len(c['lines'])==2
        for line in c['lines']:ui.validate_text(line,48,860)
    cuts=spec['cuts'];starts=[];current=0
    for c in cuts:starts.append(current);current+=c['duration']
    def composite(n):
        t=(n-1)/fps;k=max(i for i,start in enumerate(starts) if t>=start)
        c=cuts[k]
        world=Image.open(root/'frames'/f'{n:04}.png').convert('RGB')
        assert world.size==(360,496),world.size
        return ui.compose(world,c['lines'],c.get('tags',[]),c.get('event'),t-starts[k])
    if preview:
        folder=root/'preview';folder.mkdir(exist_ok=True)
        for n in spec['preview_frames']:
            composite(n).save(folder/f'{n:04}.png')
        print('PREVIEWS_OK');return
    missing=[n for n in range(1,count+1) if not (root/'frames'/f'{n:04}.png').exists()]
    if missing:raise RuntimeError(f'Missing {len(missing)} native frames, first {missing[:8]}')
    dest=(root/spec['output']).resolve();dest.parent.mkdir(exist_ok=True,parents=True)
    cmd=[imageio_ffmpeg.get_ffmpeg_exe(),'-y','-f','rawvideo','-pix_fmt','rgb24','-s','1080x1920','-r',str(fps),'-i','pipe:0','-an','-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p','-movflags','+faststart',str(dest)]
    with (root/'encode.log').open('w') as log:
        proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
        try:
            for n in range(1,count+1):
                proc.stdin.write(composite(n).tobytes())
                if n%90==0:print(f'COMPOSE {n}/{count}',flush=True)
            proc.stdin.close();code=proc.wait()
            if code:raise RuntimeError(f'Encoder exit {code}')
        except:
            proc.kill();raise
    # Decode every frame and inspect actual metadata; no audio is produced.
    ff=imageio_ffmpeg.get_ffmpeg_exe()
    result=subprocess.run([ff,'-v','error','-i',str(dest),'-f','null','-'],capture_output=True)
    assert result.returncode==0 and not result.stderr,result.stderr
    reader=imageio_ffmpeg.read_frames(str(dest));meta=next(reader);actual=sum(1 for _ in reader)
    assert meta['size']==(1080,1920) and meta['fps']==30 and actual==count,(meta,actual)
    info=subprocess.run([ff,'-i',str(dest)],capture_output=True).stderr.decode('utf-8',errors='replace')
    assert 'Audio:' not in info
    (root/'VALIDATION.json').write_text(json.dumps({'size':[1080,1920],'fps':30,'duration':duration,'frames':actual,'audio':False,'full_decode':True,'ui_bounds':'passed','native_3d_frames':count},indent=2),encoding='utf-8')
    print('VIDEO_VALIDATED',dest,flush=True)
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('manifest');a.add_argument('--preview',action='store_true');v=a.parse_args();run(v.manifest,v.preview)
