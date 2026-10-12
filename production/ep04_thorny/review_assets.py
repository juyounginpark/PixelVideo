"""Review-only contact sheets: never inserted into the episode UI."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib
R=Path(__file__).resolve().parent;D=R/'review';D.mkdir(exist_ok=True)
font=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',18)
sets={'hook':[1,13,25,37,49,61,73,89], 'capillary':[451,463,475,487,499,511,523,539], 'jaw':[811,821,831,841,851,861,871,889], 'back_drop':[901,913,925,937,949,961,973,989]}
stats={}
for name,frames in sets.items():
    if not all((R/'frames'/f'{n:04}.png').exists() for n in frames):continue
    sheet=Image.new('RGB',(720,560),'#111820');d=ImageDraw.Draw(sheet);hashes=[]
    for i,n in enumerate(frames):
        source=Image.open(R/'frames'/f'{n:04}.png').convert('RGB')
        thumb=source.resize((180,248),Image.Resampling.NEAREST)
        x=(i%4)*180;y=(i//4)*280
        sheet.paste(thumb,(x,y+28))
        d.text((x+6,y+4),f'{(n-1)/30:05.2f}s',font=font,fill='white')
        hashes.append(hashlib.sha256(source.tobytes()).hexdigest())
    stats[name]={'frames':frames,'distinct_images':len(set(hashes)),'note':'Distinct image count does not establish meaningful action; inspect progression visually.'}
    sheet.save(D/f'{name}_sequence.jpg',quality=95)
(D/'frame_evidence.json').write_text(json.dumps(stats,indent=2),encoding='utf-8')
print('REVIEW_SETS',list(stats))
