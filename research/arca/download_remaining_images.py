import json
import time
import urllib.request
from pathlib import Path
from PIL import Image

root=Path('research/arca/stage2')
out=root/'images';out.mkdir(exist_ok=True)
for id_ in ['144105830','141277397','140379923','139967377']:
 row=json.loads((root/f'{id_}.json').read_text(encoding='utf-8'))
 for img in row['images']:
  number=img['number']
  target=out/f'{id_}_{number}.image'
  try:
   if not target.exists():
    time.sleep(1)
    req=urllib.request.Request(img['url'],headers={'User-Agent':'Mozilla/5.0','Referer':row['url']})
    with urllib.request.urlopen(req,timeout=30) as response:data=response.read()
    target.write_bytes(data)
   with Image.open(target) as source:
    source.seek(0)
    image=source.convert('RGB')
    image.save(out/f'{id_}_{number}.png')
    print(id_,number,image.size,flush=True)
    if image.height>2200:
     for n,y in enumerate(range(0,image.height,1800),1):
      image.crop((0,y,image.width,min(y+1900,image.height))).save(out/f'{id_}_{number}_part{n}.png')
  except Exception as error:
   print(id_,number,type(error).__name__,str(error),flush=True)
   break
