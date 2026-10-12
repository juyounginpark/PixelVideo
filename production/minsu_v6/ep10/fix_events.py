from pathlib import Path
import json
p=Path(__file__).with_name('episode.json');d=json.loads(p.read_text('utf8'));d['shots'][0]['emphasisEvent']['frame']=24;d['shots'][-1]['emphasisEvent']['frame']=918
p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
