from pathlib import Path
ROOT=Path(__file__).resolve().parent
base=(ROOT.parent/'ep02_cinema/compose.py').read_text(encoding='utf-8').split('TIMES=')[0]
base=base.replace('W,H,FPS,DURATION=720,1280,24,50','W,H,FPS,DURATION=720,1280,24,45')
base=base.replace("str(ROOT/'fonts'/'Jua-Regular.ttf')","'C:/Windows/Fonts/malgunbd.ttf'")
base=base.replace("CREAM='#FFF6E7';INK='#56464A';MUTED='#8D7470';ROSE='#C98580';MINT='#9DCABB'","CREAM='#E8E6D8';INK='#252B39';MUTED='#656C71';ROSE='#6F725D';MINT='#89AAA6'")
base=base.replace('radius=17','radius=2').replace('radius=19','radius=2').replace('radius=22','radius=3').replace('radius=26','radius=3')
base=base.replace("Image.open(ROOT/'frames_final'/f'{idx:05d}.png').convert('RGB')","render_frame(idx)")
base=base.replace("Image.open(ROOT/'frames_final'/'00001.png').convert('RGB')","render_frame(1)")
base=base.replace('def frame(t):','def source_frame(t):')
assert 'frames_final' not in base and 'Jua' not in base
helper='''
import numpy as np
from functools import lru_cache
@lru_cache(maxsize=32)
def cached_render(index):
    image=Image.open(ROOT/'frames'/f'{index:05d}.png').convert('RGB')
    a=np.asarray(image,dtype=np.float32)
    bayer=np.array([[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]],dtype=np.float32)/16-.5
    pattern=np.tile(bayer,(image.height//4+1,image.width//4+1))[:image.height,:image.width,None]
    a=np.clip(np.round((a+pattern*4)/8)*8,0,255).astype(np.uint8)
    return Image.fromarray(a).resize((W,H),Image.Resampling.NEAREST)
def render_frame(index):return cached_render(index).copy()
def frame(t):return source_frame(t*1.2 if t<25 else t+5)

TIMES=[0,1.7,3.75,5.42,8.33,10.67,12.5,13.92,15.83,18.33,20.83,23.5,27,32,36,44.875]
if '--preview' in sys.argv:
    # Use exact sampled source frames while reviewing the incomplete render.
    source_times=[0,2,4.5,6.5,10,12.8,15,16.7,19,22,25,28.2,32,37,41,49.875]
    sheet=Image.new('RGB',(1080,2040),CREAM)
    for j,st in enumerate(source_times):
        im=source_frame(st);im.save(ROOT/f'preview_{j:02d}.png')
        sheet.paste(im.resize((270,480),Image.Resampling.NEAREST),((j%4)*270,(j//4)*510))
        txt(ImageDraw.Draw(sheet),((j%4)*270+8,(j//4)*510+484),f'{(st/1.2 if st<30 else st-5):.1f}s',17)
    sheet.save(EXPORT/'MINSU_EP02_PSX_LOWPOLY_contact.jpg',quality=95)
    print('PREVIEW_COMPLETE');sys.exit()

out=EXPORT/'MINSU_EP02_PSX_LOWPOLY_SILENT_v3.mp4'
cmd=[FF,'-hide_banner','-loglevel','warning','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','medium','-crf','17','-pix_fmt','yuv420p','-movflags','+faststart',str(out)]
with open(ROOT/'encode.log','w',encoding='utf-8') as log:
    p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
    for i in range(FPS*DURATION):
        p.stdin.write(frame(i/FPS).tobytes())
        if i%120==0:print(f'COMPOSITE {i}/{FPS*DURATION}',flush=True)
    p.stdin.close()
    if p.wait():raise RuntimeError('encoding failed')
print('COMPLETE',out,flush=True)
'''
(ROOT/'compose.py').write_text(base+helper,encoding='utf-8')
print('COMPOSITOR_READY')
