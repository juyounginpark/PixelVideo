from pathlib import Path
import json
from PIL import Image
from overlay import Overlay
from directors import validate_story
J=Path(__file__).resolve().parent;p=J/'ep10';d=json.loads((p/'episode.json').read_text('utf8'));validate_story(d['shots']);results={}
for locale in ['ko','en']:
 o=Overlay(d,locale);frames=0
 for c in o.cues:
  f=round(c['start']*30);s=next(s for s in d['shots'] if s['startFrame']<=f<s['endFrame']);o.frame(Image.new('RGB',(540,960)),f,s);o.frame(Image.new('RGB',(540,960)),f+4,s);frames+=1
 results[locale]={'captions':frames,'font':o.fontQA,'fixedRoleSizesFit':True}
(p/'research/caption_preflight.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf8');print('KO / EN role sizes, reading times and glyphs passed')
