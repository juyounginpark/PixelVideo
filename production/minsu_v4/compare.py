"""Pair actual reference frames with actual delivered frames at matching editorial roles."""
from pathlib import Path
from PIL import Image,ImageDraw
from common import R
import argparse
p=argparse.ArgumentParser();p.add_argument('--quality',default='final',choices=['preview','final']);a=p.parse_args()
review=R/'ep07'/a.quality/'review';refs=R/'review/media'
rows=[('OBSERVATION',refs/'ref4_01.00.png',R/'review/media/ep06_01.40.png',review/'S02_045.png'),('MECHANISM',refs/'ref4_10.00.png',R/'review/media/ep06_13.90.png',review/'S05_052.png'),('DISCOVERY',refs/'ref3_12.50.png',R/'review/media/ep06_19.10.png',review/'S07_060.png')]
out=Image.new('RGB',(1080,690*len(rows)),'#101b33');d=ImageDraw.Draw(out)
for j,(role,ref,old,new) in enumerate(rows):
    for i,(label,path) in enumerate([('REFERENCE',ref),('EP06 V3.1',old),('EP07 V4',new)]):
        if not path.exists():raise FileNotFoundError(path)
        im=Image.open(path).convert('RGB').resize((360,640));x=i*360;y=j*690;out.paste(im,(x,y+40));d.text((x+7,y+8),role+' / '+label,fill='white')
out.save(review/'REFERENCE_COMPARISON.jpg',quality=97);print('Reference comparison:',review/'REFERENCE_COMPARISON.jpg')
