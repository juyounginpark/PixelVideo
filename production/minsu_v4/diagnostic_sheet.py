from common import R,read,write
from typography import Overlay
from PIL import Image,ImageDraw
from pathlib import Path
s=read(R/'ep07/episode.json');index=read(R/'ep07/final/native_index.json');o=Overlay();sheet=Image.new('RGB',(1080,1020*((len(s['shots'])+3)//4)),'#101b33');d=ImageDraw.Draw(sheet);errors=[]
for i,shot in enumerate(s['shots']):
    folder=Path(index[shot['id']]['folder']);records=read(folder/'manifest.json')['frames'];f=(shot['endFrame']-shot['startFrame'])//2
    if str(f) not in records:f=sorted(map(int,records))[0]
    im,_=o.frame(Image.open(folder/f'{f:04}.png'),shot,f,records[str(f)]['anchors'],check=False);im.save(R/'review'/f'diagnostic_{shot["id"]}.png')
    x=i%4*270;y=i//4*510;sheet.paste(im.resize((270,480),Image.Resampling.NEAREST),(x,y+30));d.text((x+5,y+5),shot['id']+' / DIAGNOSTIC',fill='white')
    try:o.frame(Image.open(folder/f'{f:04}.png'),shot,f,records[str(f)]['anchors'])
    except ValueError as e:errors.append(str(e))
sheet.crop((0,0,1080,510*((len(s['shots'])+3)//4))).save(R/'review/diagnostic.jpg',quality=95);write(R/'review/diagnostic_errors.json',errors);print(errors)
