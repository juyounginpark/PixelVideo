from pathlib import Path
import json
p=Path(__file__).with_name('episode.json');d=json.loads(p.read_text('utf8'))
for c in d['captions']['en']:
 c['lines']=[t.replace('reflected light looks green.','reflection looks green.') for t in c['lines']]
 c['newText']=c.get('newText','').replace('reflected light looks green.','reflection looks green.') or ''.join(c['lines'])
 if c['lines']==['Same cup. Different light!']:c['lines']=['Same cup.','Different light!']
for locale in ['ko','en']:
 for c in d['captions'][locale]:
  if c['start']==8.6:c['end']=10.4
  elif c['start']==11.2:c['start']=10.4;c['end']=12.2
  elif c['start']==13.6:c['start']=12.2;c['end']=15.8
p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
