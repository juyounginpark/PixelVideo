from pathlib import Path
import json
from PIL import Image
from overlay import Overlay
J=Path(__file__).resolve().parent;job=J/'ep10';spec=json.loads((job/'episode.json').read_text('utf8'));index=json.loads((job/'native_index.json').read_text('utf8'));s=spec['shots'][0];o=Overlay(spec,'ko');sheet=Image.new('RGB',(1350,400))
for i,f in enumerate([0,12,24,30,60,119]):
 file=Path(index['S01']['folder'])/f'{f:04}.png';im,q=o.frame(Image.open(file),f,s);sheet.paste(im.resize((225,400)),(i*225,0))
sheet.save(job/'hook_contact.jpg')
