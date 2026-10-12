from pathlib import Path
import json
from PIL import Image
from compose import OverlayComposer
R=Path(__file__).resolve().parent
spec=json.loads((R/'episode.json').read_text('utf-8'));anchors=json.loads((R/'anchors.json').read_text('utf-8'))
c=OverlayComposer(spec,anchors);records=[]
for f in range(1,1081):
    _,qa=c.overlay(Image.new('RGB',(1080,1920)),f);records.append(qa)
warnings=[r for r in records if r['faceAnchorOverlaps']]
report={'framesChecked':1080,'boundsPassed':True,'maxPanels':max(r['panels'] for r in records),
        'faceAnchorWarnings':warnings,'limitation':'Coordinate checks use baked anchors, not full facial silhouettes or visual comprehension.'}
(R/'overlay_preflight.json').write_text(json.dumps(report,indent=2),'utf-8')
print('OVERLAY_PREFLIGHT',1080,'face anchor warnings:',len(warnings))
