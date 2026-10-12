"""Update review-only metadata; no render or repeated benchmarks."""
from pathlib import Path
import json
E=Path(__file__).resolve().parent;folder=E/'review'
path=folder/'DELIVERY.json';data=json.loads(path.read_text('utf-8'));data['metrics']['compositionOnlyRevisionCount']=2
obsolete='Small gray background edge at upper-right of experiment viewport remains; no object is clipped.'
data['editorial']['limits']=[x for x in data['editorial']['limits'] if x!=obsolete]
data['editorial']['improved']+='; fixed 12px viewport border removes the visible background corner at the crop boundary'
path.write_text(json.dumps(data,ensure_ascii=False,indent=2),'utf-8')
page=folder/'REPORT.html';page.write_text(page.read_text('utf-8').replace('<li>'+obsolete+'</li>',''),'utf-8')
# Local report links must resolve before handoff.
import re
for ref in re.findall(r'(?:href|src)="([^"]+)"',page.read_text('utf-8')):
    if not (folder/ref).resolve().exists():raise ValueError('Missing delivery link '+ref)
print('Report links verified; final preview:',data['output'])
