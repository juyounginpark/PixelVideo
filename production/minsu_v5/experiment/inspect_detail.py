from pathlib import Path
import sys,subprocess
from PIL import Image,ImageDraw
import imageio_ffmpeg
E=Path(__file__).resolve().parent;sys.path.insert(0,str(E.parent))
from common import read,write,sha
folder=E/'review/straw';src=Path(read(folder/'source.json')['path']);ff=imageio_ffmpeg.get_ffmpeg_exe()
times=[40,42,44,46,48,50,50.5,51,51.5,52,52.5,53,53.5,54,56,62,68,74,122,126,157,161,163,173]
for t in times:
    path=folder/f'exact_{t:06.2f}.png'
    subprocess.run([ff,'-y','-v','error','-ss',str(t),'-i',str(src),'-frames:v','1',str(path)],check=True)
sheet=Image.new('RGB',(1080,414*5),'#18152b');d=ImageDraw.Draw(sheet)
for i,t in enumerate(times):
    with Image.open(folder/f'exact_{t:06.2f}.png') as im:sheet.paste(im.resize((216,384)),((i%5)*216,(i//5)*414+30))
    d.text(((i%5)*216+5,(i//5)*414+8),f'{t:.2f}s',fill='white')
sheet.save(folder/'detail.jpg',quality=95)
write(folder/'exact_frames.json',{'sourceSha256':sha(src),'times':times,'method':'FFmpeg seek with frame decode; source 30fps'})
