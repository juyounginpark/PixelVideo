from common import R,read,native_key
from typography import Overlay
from PIL import Image
o=Overlay();s=read(R/'ep07/episode.json')
for sid,f in [('S01',80),('S02',45),('S08',42),('S08',75),('S07',60)]:
    shot=next(x for x in s['shots'] if x['id']==sid);folder=R/'cache/native'/native_key(shot,[270,480]);p=folder/'manifest.json'
    if not p.exists() or str(f) not in read(p)['frames']:continue
    records=read(p)['frames'];im,q=o.frame(Image.open(folder/f'{f:04}.png'),shot,f,records[str(f)]['anchors']);im.save(R/'review'/f'current_{sid}_{f}.png')
    print(sid,f,'layout PASS')
