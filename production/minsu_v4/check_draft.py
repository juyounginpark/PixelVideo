from common import read,R
from typography import Overlay
from PIL import Image
from collections import Counter
s=read(R/'ep07/episode.json');o=Overlay()
for x in s['shots']:
    try:o.frame(Image.new('RGB',(270,480)),x,50,{})
    except ValueError as e:print(x['id'],str(e))
p=R/'ep07/final/last_render.json'
if p.exists():
    d=read(p);print('clipping',dict(Counter(x['shot'] for x in d['errors'])));print('renderSecs',d['totalSeconds'])
