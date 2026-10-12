import json
import sys
import time
import urllib.request
from pathlib import Path
from PIL import Image

root = Path('research/arca/stage2')
out = root / 'images'
out.mkdir(parents=True, exist_ok=True)
ids = ['182069474','172135555','151936970','147416554','145574902']
for id_ in ids:
    record = json.loads((root/f'{id_}.json').read_text(encoding='utf-8'))
    for image in record['images']:
        number = image['number']
        try:
            req = urllib.request.Request(image['url'], headers={'User-Agent':'Mozilla/5.0','Referer':record['url']})
            time.sleep(1)
            with urllib.request.urlopen(req,timeout=25) as response:
                data = response.read()
            target = out / f'{id_}_{number}.image'
            target.write_bytes(data)
            with Image.open(target) as img:
                img.seek(0)
                img = img.convert('RGB')
                img.save(out/f'{id_}_{number}.png')
                print(id_,number,'size',img.size,flush=True)
                if img.height > 2200:
                    for n,y in enumerate(range(0,img.height,1800),1):
                        img.crop((0,y,img.width,min(y+1900,img.height))).save(out/f'{id_}_{number}_part{n}.png')
        except Exception as error:
            print(id_,number,type(error).__name__,str(error),flush=True)
            break
