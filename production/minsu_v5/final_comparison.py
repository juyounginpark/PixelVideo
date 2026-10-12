from common import *
from PIL import Image,ImageDraw
import subprocess,imageio_ffmpeg
out=R/'review/comparison';out.mkdir(exist_ok=True);sources={x['name']:Path(x['path']) for x in read(R/'review/media_review.json')};sources['ep08']=ROOT/'exports/MINSU_EP08_V5_RED_RAIN_KO.mp4';ff=imageio_ffmpeg.get_ffmpeg_exe()
sets=[('event',[('ref3',1),('ref4',.5),('ep07',.5),('ep08',.5)]),('discovery',[('ref3',37),('ref4',18),('ep07',22),('ep08',15.8)])]
sheet=Image.new('RGB',(1440,1360),'#172339');d=ImageDraw.Draw(sheet);evidence=[]
for row,(purpose,items) in enumerate(sets):
 for col,(name,t) in enumerate(items):
  p=out/f'{name}_{purpose}.png';subprocess.run([ff,'-v','error','-y','-ss',str(t),'-i',str(sources[name]),'-frames:v','1',str(p)],check=True)
  im=Image.open(p);sheet.paste(im.resize((360,640)),(col*360,row*680+35));d.text((col*360+8,row*680+10),f'{name.upper()} / {purpose} / {t}s',fill='white');evidence.append(dict(source=str(sources[name]),sourceSha256=sha(sources[name]),time=t,frame=str(p.relative_to(ROOT))))
sheet.save(out/'reference_comparison.jpg',quality=96);write(out/'evidence.json',evidence)
# Pixel crops are explicitly native-output crops; source resolutions differ.
crop=Image.new('RGB',(1080,600),'#172339');dc=ImageDraw.Draw(crop)
for i,name in enumerate(['ref3','ref4','ep08']):
 im=Image.open(out/f'{name}_event.png');x=int(im.width*.25);y=int(im.height*.30);piece=im.crop((x,y,x+180,y+250)).resize((360,500),Image.Resampling.NEAREST);crop.paste(piece,(i*360,50));dc.text((i*360+8,12),f'{name}: native crop x2, {im.width}x{im.height}',fill='white')
crop.save(out/'reference_pixel_crops.png')
