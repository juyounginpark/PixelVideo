from pathlib import Path
import subprocess,json
from PIL import Image,ImageDraw,ImageFont
import imageio_ffmpeg
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'research'/'reels_v2';OUT.mkdir(parents=True,exist_ok=True)
ff=imageio_ffmpeg.get_ffmpeg_exe();font=ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf',20)
names=['해마는','지구가','똥,','안 만졌는데'];results=[]
for i,prefix in enumerate(names,1):
    paths=list((ROOT/'references').glob(prefix+'*.mp4'))
    if len(paths)!=1:raise RuntimeError((prefix,paths))
    p=paths[0];gen=imageio_ffmpeg.read_frames(str(p));meta=next(gen);gen.close()
    rows=[];folder=OUT/f'ref{i}';folder.mkdir(exist_ok=True)
    for t in [.5,2,5,12,20,min(30,meta['duration']-.3)]:
        target=folder/f'{t:04.1f}.png'
        subprocess.run([ff,'-y','-loglevel','error','-ss',str(t),'-i',str(p),'-frames:v','1',str(target)],check=True)
        rows.append((t,target))
    sheet=Image.new('RGB',(1080,690),'#121821');d=ImageDraw.Draw(sheet)
    for j,(t,impath) in enumerate(rows):
        im=Image.open(impath);im.thumbnail((180,640));x=j*180;sheet.paste(im,(x,40));d.text((x+5,8),f'R{i} {t:.1f}s',font=font,fill='white')
    sheet.save(OUT/f'ref{i}_sheet.jpg',quality=95)
    results.append({'id':i,'file':str(p.relative_to(ROOT)),'metadata':meta,'sample_seconds':[a for a,_ in rows]})
(OUT/'metadata.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
print('REFERENCE_FRAMES_READY')
