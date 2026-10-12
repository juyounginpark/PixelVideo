"""New exact-frame extraction from the actual MP4s for this review."""
from common import R,ROOT,write,sha
from pathlib import Path
import subprocess,json
from PIL import Image,ImageDraw
import imageio_ffmpeg
out=R/'review/media';out.mkdir(parents=True,exist_ok=True)
sources={'ref3':next((ROOT/'references').glob('똥,*.mp4')),'ref4':next((ROOT/'references').glob('안 만졌는데*.mp4')),'ep06':ROOT/'exports/MINSU_EP06_V31_ICE.mp4'}
times={'ref3':[1,4.5,5,11.5,12.5,16,26,37,48],'ref4':[0,.5,1,2,3,5,6,9,10,11,13,15,18,24,30],'ep06':[.2,.8,1.4,2.1,3.5,6,8.7,11.1,13.9,16.2,19.1,23,26.5,30,33.5]}
evidence=[]
for name,path in sources.items():
    reader=imageio_ffmpeg.read_frames(str(path));meta=next(reader);reader.close();actual=[t for t in times[name] if t<meta['duration']-.75]
    canvas=Image.new('RGB',(1080,414*((len(actual)+4)//5)),'#101b33');d=ImageDraw.Draw(canvas)
    for i,t in enumerate(actual):
        dest=out/f'{name}_{t:05.2f}.png'
        subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-v','error','-y','-ss',str(t),'-i',str(path),'-frames:v','1','-vf','scale=432:768',str(dest)],check=True)
        im=Image.open(dest);x=i%5*216;y=i//5*414;canvas.paste(im.resize((216,384)),(x,y+30));d.text((x+4,y+7),f'{name} {t:.2f}s',fill='white')
    canvas.save(out/f'{name}_sequence.jpg',quality=95)
    evidence.append(dict(name=name,path=str(path),sha256=sha(path),times=actual,metadata=meta,observation='Actual decoded frames; no claim of audio listening or continuous real-time viewing'))
write(R/'review/media_review.json',evidence);print('Actual MP4 review extraction',len(evidence))
