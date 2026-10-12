from common import *
from typography import Overlay
from PIL import Image,ImageDraw
spec=read(R/'ep08/episode.json');idx=read(R/'ep08/final/native_index.json');overlay=Overlay();fonts=overlay.type.preflight(spec);errors=[];panels=[]
out=R/'review/ui_stills';out.mkdir(exist_ok=True)
for s in spec['shots']:
 folder=Path(idx[s['id']]['folder']);rows=read(folder/'manifest.json')['frames']
 for k,row in rows.items():
  f=int(k)
  try:im,qa=overlay.frame(Image.open(folder/f'{f:04}.png'),s,f,row['anchors'])
  except ValueError as e:
   errors.append(str(e))
   try:im,qa=overlay.frame(Image.open(folder/f'{f:04}.png'),s,f,row['anchors'],False)
   except ValueError:continue
  im.save(out/f'{s["id"]}_{f:03}.png')
  if f==(s['endFrame']-s['startFrame'])//2:panels.append((s['id'],im))
sheet=Image.new('RGB',(1080,1980),'#142034');d=ImageDraw.Draw(sheet)
for i,(sid,im) in enumerate(panels):
 x=i%3*360;y=i//3*660;sheet.paste(im.resize((360,640)),(x,y+20));d.text((x+8,y+3),sid,fill='white')
sheet.save(out/'grid.jpg');write(out/'qa.json',dict(fonts=fonts,errors=errors));print(errors)
