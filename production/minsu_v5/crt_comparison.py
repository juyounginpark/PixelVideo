"""Same native frames encoded to MP4 for bright/dark/text A/B/C/D inspection."""
from common import *
from typography import Overlay
from PIL import Image,ImageDraw
import subprocess,imageio_ffmpeg,numpy as np
out=R/'review/crt';out.mkdir(exist_ok=True);spec=read(R/'ep08/episode.json');idx=read(R/'ep08/final/native_index.json');ff=imageio_ffmpeg.get_ffmpeg_exe();report=[]
for preset in ['OFF','REFERENCE','MOBILE','STRONG']:
 folder=out/preset;folder.mkdir(exist_ok=True);o=Overlay(post=preset);o.type.preflight(spec)
 for i,(sid,f) in enumerate([('S01',60),('S04',45)]):
  shot=next(s for s in spec['shots'] if s['id']==sid);native=Path(idx[sid]['folder']);row=read(native/'manifest.json')['frames'][str(f)];im,q=o.frame(Image.open(native/f'{f:04}.png'),shot,f,row['anchors']);im.save(folder/f'{i:01}.png')
 video=out/(preset+'.mp4')
 subprocess.run([ff,'-v','error','-y','-framerate','.5','-i',str(folder/'%01d.png'),'-t','4','-r','30','-c:v','libx264','-threads','2','-preset','fast','-crf','18','-pix_fmt','yuv420p',str(video)],check=True)
 for i,t in enumerate([.5,2.5]):subprocess.run([ff,'-v','error','-y','-ss',str(t),'-i',str(video),'-frames:v','1',str(folder/f'decoded_{i}.png')],check=True)
 report.append(dict(preset=preset,settings=config('POST_PROCESS_PRESETS')['presets'][preset],mp4=str(video.relative_to(ROOT)),sha256=sha(video),method='Repeated diagnostic stills encoded and decoded; not an animation approval'))
sheet=Image.new('RGB',(1440,1320),'#172339');d=ImageDraw.Draw(sheet)
for j,p in enumerate(['OFF','REFERENCE','MOBILE','STRONG']):
 for i in [0,1]:
  im=Image.open(out/p/f'decoded_{i}.png');sheet.paste(im.resize((360,640)),(j*360,i*660+20));d.text((j*360+8,i*660+4),p,fill='white')
sheet.save(out/'comparison.jpg',quality=96)
# Native resolution crops retain the output-pixel scanline evidence.
crop=Image.new('RGB',(1200,1200))
for j,p in enumerate(['OFF','REFERENCE','MOBILE','STRONG']):
 for i,box in enumerate([(330,120,630,420),(300,250,600,550),(450,1500,750,1800)]):
  im=Image.open(out/p/f'decoded_{0 if i!=1 else 1}.png');crop.paste(im.crop(box),(j*300,i*400+25));ImageDraw.Draw(crop).text((j*300+4,i*400+4),p+' '+['bright/title','dark','text'][i],fill='white')
crop.save(out/'pixel_crops.png');write(out/'evidence.json',report)
