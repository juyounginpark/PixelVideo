"""One command per quality gate. No topic choice, no per-cut model requests."""
import argparse,subprocess,sys,time
from pathlib import Path
from common import R,ROOT,read,write
from narrative_director import NarrativeDirector
BLENDER=Path('C:/Program Files/Blender Foundation/Blender 5.0/blender.exe')
def call(name,args):
    log=R/'review'/f'{name}.log';start=time.perf_counter()
    with log.open('w',encoding='utf-8') as f:p=subprocess.run([str(x) for x in args],stdout=f,stderr=subprocess.STDOUT)
    # Blender may return zero after a Python exception; enforce our success marker.
    text=log.read_text('utf-8',errors='replace')
    if p.returncode or 'Traceback (most recent call last)' in text:raise RuntimeError(f'{name} failed: {log}\n{text[-1200:]}')
    print(name,'complete',round(time.perf_counter()-start,1),'s',flush=True)
def main():
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['sample','preview','final','verify-cache']);a=p.parse_args();job=R/'ep07';spec=read(job/'episode.json')
    compiled=NarrativeDirector().compile(spec);write(job/'episode_request.json',compiled['episodePayload']);write(job/'narrative_qa.json',{k:v for k,v in compiled.items() if k!='episodePayload'})
    quality='preview' if a.stage=='preview' else 'final';ids=','.join(spec['sampleShots']) if a.stage=='sample' else None
    if a.stage in ('preview','final'):
        gate=read(job/'sample_review/GATE.json')
        if gate.get('decision')!='PROCEED_WITH_STATED_LIMITS':raise ValueError('Sample visual gate not reviewed')
        if spec['status']!='selected':raise ValueError('Source not confirmed after sample gate')
    if a.stage=='final':
        if read(job/'preview/review/GATE.json').get('decision')!='PROCEED_WITH_STATED_LIMITS':raise ValueError('Preview visual gate not reviewed')
    write(job/'state.json',dict(stage=a.stage+'_running',editorialAutomaticPass=False))
    render=[BLENDER,'-b','--python',R/'render.py','--','--job',job,'--quality',quality]
    comp=[sys.executable,R/'compose.py','--job',job,'--quality',quality]
    if ids:render+=['--shots',ids];comp+=['--shots',ids]
    if a.stage!='verify-cache':
        call(a.stage+'_preflight',render+['--preflight'])
        call(a.stage+'_ui_preflight',comp+['--preflight'])
    call(a.stage+'_render',render)
    target=ROOT/'exports'/({'sample':'MINSU_V4_GRAVITY_SAMPLE.mp4','preview':'MINSU_EP07_V4_DARK_MATTER_PREVIEW.mp4','final':'MINSU_EP07_V4_DARK_MATTER.mp4','verify-cache':'MINSU_EP07_V4_DARK_MATTER.mp4'}[a.stage])
    call(a.stage+'_compose',comp+['--output',target])
    write(job/'state.json',dict(stage=a.stage,output=str(target),next='actual image/sequence review',editorialAutomaticPass=False))
if __name__=='__main__':main()
