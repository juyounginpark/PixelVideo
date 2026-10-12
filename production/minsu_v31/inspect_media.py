"""Read the actual reference and EP05 MP4s; preserve provenance and time samples."""
import hashlib,json,subprocess
from pathlib import Path
import imageio_ffmpeg
import numpy as np
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent/'review'
OUT.mkdir(exist_ok=True)
baseline={}
for folder in ('research/namuwiki','prompts'):
    for p in (ROOT/folder).rglob('*'):
        if p.is_file():baseline[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
for p in (ROOT/'exports').glob('*.mp4'):baseline[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
if not (OUT/'preservation_before.json').exists():(OUT/'preservation_before.json').write_text(json.dumps(baseline,ensure_ascii=False,indent=2),'utf-8')
paths={'ref3':next((ROOT/'references').glob('똥,*.mp4')),'ref4':next((ROOT/'references').glob('안 만졌는데*.mp4')),'ep05':ROOT/'exports/MINSU_EP05_V3_BRAZIL_NUT.mp4'}
allmeta=[]
for key,path in paths.items():
    folder=OUT/key;folder.mkdir(exist_ok=True)
    reader=imageio_ffmpeg.read_frames(str(path));meta=next(reader);reader.close()
    fps=meta['fps'];stride=round(fps);w,h=216,384
    command=[imageio_ffmpeg.get_ffmpeg_exe(),'-v','error','-i',str(path),'-an','-vf',f'scale={w}:{h}','-f','rawvideo','-pix_fmt','rgb24','-']
    proc=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    frames=[];changes=[];previous=None;i=0
    while True:
        raw=proc.stdout.read(w*h*3)
        if not raw:break
        if len(raw)!=w*h*3:raise RuntimeError('Truncated frame')
        arr=np.frombuffer(raw,np.uint8).reshape(h,w,3)
        if previous is not None:
            diff=float(np.abs(arr.astype(float)-previous).mean())
            if diff>12:changes.append({'frame':i,'time':round(i/fps,3),'meanChange':round(diff,2)})
        previous=arr.copy()
        if i%stride==0:
            im=Image.fromarray(arr);target=folder/f'{i:04}.jpg';im.save(target,quality=95);frames.append((i,im.copy()))
        i+=1
    proc.stdout.close();error=proc.stderr.read().decode('utf-8','replace');proc.stderr.close()
    if proc.wait():raise RuntimeError(error)
    for start in range(0,len(frames),20):
        batch=frames[start:start+20];sheet=Image.new('RGB',(1080,408*((len(batch)+4)//5)),'#101926');d=ImageDraw.Draw(sheet)
        for j,(f,im) in enumerate(batch):
            x=j%5*216;y=j//5*408;sheet.paste(im,(x,y+24));d.text((x+7,y+5),f'{key}  {f/fps:.2f}s / {f}',fill='white')
        sheet.save(folder/f'sequence_{start:03}.jpg',quality=94)
    allmeta.append({'id':key,'source':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                    'metadata':meta,'decodedFrames':i,'sampling':'every exact 1 second, all frames decoded',
                    'largeFrameChangesNotConfirmedCuts':changes,'listening':'not performed; no audio-content claims'})
(OUT/'media_evidence.json').write_text(json.dumps(allmeta,ensure_ascii=False,indent=2),'utf-8')
print(json.dumps([{'id':x['id'],'frames':x['decodedFrames'],'duration':x['metadata']['duration'],'changeCandidates':len(x['largeFrameChangesNotConfirmedCuts'])} for x in allmeta]))
