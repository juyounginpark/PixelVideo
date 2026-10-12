from pathlib import Path
from datetime import datetime,timezone,timedelta
import sys,subprocess
import imageio_ffmpeg
from PIL import Image,ImageDraw
E=Path(__file__).resolve().parent;sys.path.insert(0,str(E.parent))
from common import write,sha,ROOT

source=next(Path('C:/Users/0620f/Downloads').glob('빨대의 구멍은 몇 개*.mp4'))
log=ROOT/'PROMPT_LOG.md'
if '## U-092 — 빨대 원본 경로 제공' not in log.read_text('utf-8'):
    with log.open('a',encoding='utf-8') as f:
        f.write('\n\n## U-092 — 빨대 원본 경로 제공\n'+datetime.now(timezone(timedelta(hours=9))).isoformat()+'\n사용자 원문:\n"C:\\Users\\0620f\\Downloads\\빨대의 구멍은 몇 개 1개 2개 인터넷을 둘로 가른 질문, 빨대의 구멍은 몇 개일까요답이 갈리는 건 구멍을 입구로 세느냐, 뚫린 길로 세느냐, 뚫은 자국으로 세느냐의.mp4"\n실제 디스크 파일명에는 2개 뒤 🥤 이모지가 포함되어 있으며 동일 제목 파일 1개를 확인했다.\n')
out=E/'review/straw';out.mkdir(exist_ok=True)
reader=imageio_ffmpeg.read_frames(str(source));meta=next(reader);reader.close()
write(out/'source.json',{'path':str(source),'sha256':sha(source),'metadata':meta,'inspection':'decoded MP4 frames; not real-time playback or audio listening'})
ff=imageio_ffmpeg.get_ffmpeg_exe()
subprocess.run([ff,'-y','-v','error','-i',str(source),'-vf','fps=1/2,scale=324:576','-start_number','0',str(out/'sample_%03d.png')],check=True)
frames=sorted(out.glob('sample_*.png'))
for page in range((len(frames)+19)//20):
    batch=frames[page*20:page*20+20];sheet=Image.new('RGB',(216*5,414*((len(batch)+4)//5)),'#18152b');d=ImageDraw.Draw(sheet)
    for i,p in enumerate(batch):
        with Image.open(p) as im:sheet.paste(im.resize((216,384)),(216*(i%5),414*(i//5)+30))
        # fps=1/2 samples are centered at seconds 1,3,5...; not exact time stamps.
        d.text((216*(i%5)+6,414*(i//5)+8),f'~{(page*20+i)*2+1:02}s',fill='white')
    sheet.save(out/f'contact_{page}.jpg',quality=94)
print(meta);print('sheets:',(len(frames)+19)//20)
