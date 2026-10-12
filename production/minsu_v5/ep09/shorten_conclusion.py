from pathlib import Path
import json
J=Path(__file__).resolve().parent;p=J/'episode.json';spec=json.loads(p.read_text('utf-8'));spec['shots'][-1]['captionPlan']['ko'][0]='시각 원리는 연구 중';p.write_text(json.dumps(spec,ensure_ascii=False,indent=2),'utf-8')
