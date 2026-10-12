"""Validate every authored UI/effect frame against projected native geometry."""
import json,argparse
from pathlib import Path
from PIL import Image
from graphics import EffectRenderer
p=argparse.ArgumentParser();p.add_argument('--job',required=True,type=Path);a=p.parse_args()
spec=json.loads((a.job/'spec.json').read_text('utf-8'));timeline=json.loads((a.job/'effects.json').read_text('utf-8'))
anchors=json.loads((a.job/'preflight_anchors.json').read_text('utf-8'));renderer=EffectRenderer();errors=[]
for f in range(spec['durationFrames']):
    try:renderer.frame(Image.new('RGB',(1080,1920),'#777777'),f,spec,timeline,anchors[str(f)])
    except Exception as e:errors.append({'frame':f,'error':str(e)})
motion=json.loads((a.job/'preflight_motion.json').read_text('utf-8'));by={r['frame']:r for r in motion}
checks={'orientationBeforeRise':by[359]['largeAngleDegrees']>70 and abs(by[359]['largeHeight']-by[240]['largeHeight'])<.03,
        'smallPeanutDescends':by[470]['smallFocusZ']<by[360]['smallFocusZ'],
        'largeNutRises':by[590]['largeHeight']-by[480]['largeHeight']>.35,
        'returnsHorizontal':by[719]['largeAngleDegrees']<1,
        'exceptionStaysLow':abs(by[809]['nonrisingHeight']-by[720]['nonrisingHeight'])<.001}
report={'frames':spec['durationFrames'],'errors':errors,'motionChecks':checks,'limits':'Authored kinematic diagram; not a physical simulation or perceptual quality test'}
(a.job/'PREFLIGHT_QA.json').write_text(json.dumps(report,indent=2),'utf-8')
print(json.dumps(report,indent=2));assert not errors and all(checks.values())
