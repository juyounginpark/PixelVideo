"""Conservative focal-object vs typography audit, separate from text-only checks."""
from common import R,read,write
from typography import Overlay,intersection
from PIL import Image
from collections import Counter
s=read(R/'ep07/episode.json');o=Overlay();errors=[]
for shot in s['shots']:
    p=R/'ep07/final/preflight'/f'{shot["id"]}.json'
    if not p.exists():continue
    records=read(p)
    for f,row in records.items():
        _,q=o.frame(Image.new('RGB',(270,480)),shot,int(f),row['anchors'],check=False)
        for subject in ('outer','head'):
            if subject not in row['anchors']:continue
            for b in q['texts']:
                if intersection(row['anchors'][subject]['rect'],b['rect'])>0:errors.append(dict(shot=shot['id'],frame=int(f),subject=subject,text=b['text']))
print('Historical-preflight focal overlaps',dict(Counter(x['shot'] for x in errors)));print(errors[:4]);print(errors[-4:]);write(R/'review/layout_risks.json',errors)
