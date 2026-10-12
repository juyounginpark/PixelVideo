import json
import time
import urllib.request
from pathlib import Path
from PIL import Image,ImageDraw

root=Path('research/dcinside')
out=root/'images';out.mkdir(exist_ok=True)
data=json.loads((root/'sample20.json').read_text(encoding='utf-8'))
for row in data:
    if row['no'] not in ['79309','78237','78918']:continue
    thumbnails=[]
    for img in row['images']:
        target=out/f"{row['no']}_{img['number']}.png"
        try:
            rawfile=out/f"{row['no']}_{img['number']}.original"
            if img.get('lazy') or not rawfile.exists():
                req=urllib.request.Request(img['url'],headers={'User-Agent':'Mozilla/5.0','Referer':row['url']})
                time.sleep(1)
                with urllib.request.urlopen(req,timeout=30) as response:raw=response.read()
                rawfile.write_bytes(raw)
            with Image.open(rawfile) as source:
                source.seek(0)
                image=source.convert('RGB')
                image.save(target)
                image.thumbnail((600,650))
                cell=Image.new('RGB',(620,700),'white')
                cell.paste(image,((620-image.width)//2,35))
                ImageDraw.Draw(cell).text((10,10),f"{row['no']} image {img['number']}",fill='black')
                thumbnails.append(cell)
            print(row['no'],img['number'],'downloaded',flush=True)
        except Exception as error:
            print(row['no'],img['number'],type(error).__name__,str(error),flush=True)
            break
    if thumbnails:
        sheet=Image.new('RGB',(1240,700*((len(thumbnails)+1)//2)),'#cccccc')
        for i,cell in enumerate(thumbnails):sheet.paste(cell,((i%2)*620,(i//2)*700))
        sheet.save(out/f"{row['no']}_contact.jpg")
