from pathlib import Path
import sys,json
from PIL import Image
J=Path(__file__).resolve().parent;sys.path.insert(0,str(J));from overlay import Overlay
p=J/'ep10';d=json.loads((p/'episode.json').read_text('utf8'));idx=json.loads((p/'native_index.json').read_text());o=Overlay(d,'ko');sheet=Image.new('RGB',(900,800))
for i,s in enumerate(d['shots']):
 f=s['startFrame']+45;file=Path(idx[s['id']]['folder'])/f'{f:04}.png';frame,_=o.frame(Image.open(file),f,s);frame.save(p/f'art_{s["id"]}.png');sheet.paste(frame.resize((225,400)),(i%4*225,i//4*400))
sheet.save(p/'art_contact.jpg')
for locale in ['ko','en']:
 o=Overlay(d,locale)
 for c in o.cues:
  f=round(c['start']*30);s=next(s for s in d['shots'] if s['startFrame']<=f<s['endFrame']);o.frame(Image.new('RGB',(540,960)),f,s)
print('All localized text fits fixed role sizes')
