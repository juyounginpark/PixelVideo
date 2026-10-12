from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import sys,json
r=Path(__file__).resolve().parent;out=r.parent.parent/'exports'
font=ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf',22)
groups={
 'INTRO':[0,.25,.55,.9,1.2,1.7,2.3,2.6],
 'TEST':[3.85,4.15,4.55,5.0,5.3,5.85,6.6,7.9],
 'REACTION':[8.55,8.75,9.0,9.5,10.5,11,11.6,12.9],
}
for name,times in groups.items():
    frames=[r/'frames'/f'{int(t*24)+1:05d}.png' for t in times]
    if not all(p.exists() for p in frames):continue
    sheet=Image.new('RGB',(1280,1216),'#172F39');d=ImageDraw.Draw(sheet)
    for j,(t,p) in enumerate(zip(times,frames)):
        im=Image.open(p).resize((320,569));x=(j%4)*320;y=(j//4)*608
        sheet.paste(im,(x,y));d.text((x+12,y+574),f'{t:.2f}s',font=font,fill='white')
    sheet.save(out/f'MINSU_EP03_v2_MOTION_{name}.jpg',quality=95)
print('REVIEW_ASSETS_READY')
