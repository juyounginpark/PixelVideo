from pathlib import Path
import sys,argparse,subprocess
from PIL import Image,ImageDraw
import imageio_ffmpeg
J=Path(__file__).resolve().parent;sys.path.insert(0,str(J.parent))
from common import read,write,sha,ROOT

def main():
 ap=argparse.ArgumentParser();ap.add_argument('stage',choices=['sample','preview','final']);a=ap.parse_args();names={'sample':'MINSU_EP09_ART_SAMPLE.mp4','preview':'MINSU_EP09_PREVIEW.mp4','final':'MINSU_EP09_STRIPES_KO.mp4'};source=ROOT/'exports'/names[a.stage];out=J/'review'/a.stage;out.mkdir(parents=True,exist_ok=True);ff=imageio_ffmpeg.get_ffmpeg_exe();reader=imageio_ffmpeg.read_frames(str(source));meta=next(reader);reader.close();times=[i*.5 for i in range(int(meta['duration']*2))];times=sorted(set(times+[.2,.4,.8,1.2,1.6,1.8]))
 for t in times:
  p=out/f'{t:05.2f}.png';subprocess.run([ff,'-v','error','-y','-ss',str(t),'-i',str(source),'-frames:v','1','-vf','scale=324:576',str(p)],check=True)
 for page in range((len(times)+19)//20):
  batch=times[page*20:page*20+20];sheet=Image.new('RGB',(1080,414*((len(batch)+4)//5)),'#18152b');d=ImageDraw.Draw(sheet)
  for i,t in enumerate(batch):
   with Image.open(out/f'{t:05.2f}.png') as im:sheet.paste(im.resize((216,384)),((i%5)*216,(i//5)*414+30))
   d.text(((i%5)*216+7,(i//5)*414+8),f'{a.stage} {t:.2f}s',fill='white')
  sheet.save(out/f'sheet_{page}.jpg',quality=95)
 write(out/'evidence.json',{'path':str(source),'sha256':sha(source),'metadata':meta,'times':times,'scope':'Actual decoded MP4 frames; not realtime playback or human audio listening'})
 print(a.stage,meta['duration'],'sheets',(len(times)+19)//20)
if __name__=='__main__':main()
