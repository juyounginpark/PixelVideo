from pathlib import Path
from PIL import Image,ImageDraw
import json
from compose import OverlayComposer
R=Path(__file__).resolve().parent;out=R/'review';out.mkdir(exist_ok=True)
c=OverlayComposer(json.loads((R/'episode.json').read_text('utf-8')),json.loads((R/'anchors.json').read_text('utf-8')))
sequences={'HOOK':[1,9,15,18,24,35,50],'REACTION':[56,60,68,85,100,128],
           'MECHANISM':[362,381,410,440,470,505],'MOUTH':[676,705,712,728,741,780,808],
           'DISCOVERY':[820,846,865,889,930,959]}
for name,frames in sequences.items():
    sheet=Image.new('RGB',(216*len(frames),408),'#18242B');d=ImageDraw.Draw(sheet)
    for j,f in enumerate(frames):
        im,qa=c.frame(f);sheet.paste(im.resize((216,384)),(j*216,0));d.text((j*216+8,388),f'{(f-1)/30:.3f}s',fill='white')
    sheet.save(out/f'{name}.jpg',quality=96)
print('MOTION_REVIEW_SHEETS',len(sequences))
