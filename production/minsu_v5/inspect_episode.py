"""Decode exact MP4 timestamps and preserve visual inspection evidence."""
import argparse,subprocess
from common import *
from PIL import Image,ImageDraw
import imageio_ffmpeg
p=argparse.ArgumentParser();p.add_argument('--video',type=Path,required=True);p.add_argument('--stage',required=True);a=p.parse_args()
out=R/'review'/a.stage;out.mkdir(exist_ok=True);spec=read(R/'ep08/episode.json');ff=imageio_ffmpeg.get_ffmpeg_exe()
def extract(t,name,size=(540,960)):
 dest=out/(name+'.png');subprocess.run([ff,'-v','error','-y','-ss',str(t),'-i',str(a.video),'-frames:v','1','-vf',f'scale={size[0]}:{size[1]}',str(dest)],check=True);return Image.open(dest).copy()
def sheet(items,name,cols,w,h):
 im=Image.new('RGB',(cols*w,((len(items)+cols-1)//cols)*(h+25)),'#172339');d=ImageDraw.Draw(im)
 for i,(label,pic) in enumerate(items):
  x=i%cols*w;y=i//cols*(h+25);im.paste(pic.resize((w,h)),(x,y+25));d.text((x+6,y+5),label,fill='white')
 im.save(out/(name+'.jpg'),quality=95)
items=[]
for s in spec['shots']:
 t=(s['startFrame']+s['endFrame'])/60;items.append((s['id']+f' {t:.2f}s',extract(t,s['id'])))
sheet(items,'cut_grid',3,360,640)
for label,start,end in [('hook',0,3),('settling',7,11),('discovery',14,18),('return',30,34)]:
 times=[start+(end-start)*i/12 for i in range(12)];items=[(f'{t:.2f}s',extract(t,label+f'_{i:02}',(216,384))) for i,t in enumerate(times)];sheet(items,label+'_sequence',6,216,384)
# Whole episode at two samples/second, split into manageable review pages.
for page in range(4):
 times=[i/2 for i in range(page*18,min((page+1)*18,68))]
 items=[(f'{t:.1f}s',extract(t,f'timeline_{int(t*2):02}',(180,320))) for t in times];sheet(items,'timeline_'+str(page),6,180,320)
write(out/'receipt.json',dict(video=str(a.video),sha256=sha(a.video),duration=spec['durationFrames']/30,method='Decoded exact MP4 frames; 2fps whole-episode sequence plus 3-4fps important actions. Not realtime playback or human listening.',files=[p.name for p in out.glob('*.jpg')]))
print('Decoded review evidence',out)
