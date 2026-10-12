"""Single-worker gated production entry point. Manual evidence cannot be auto-approved."""
import argparse,subprocess,sys,time
from common import *
BLENDER=Path('C:/Program Files/Blender Foundation/Blender 5.0/blender.exe')
def reviewed(job,name):
 g=read(job/'gates.json')[name]
 if g['decision'] not in ['PASS','PROCEED_WITH_STATED_LIMITS']:raise ValueError('Unreviewed gate '+name)
 if name in ['ART_PREVIEW','EDITING_PREVIEW']:
  if not g.get('observations') or not g.get('evidence'):raise ValueError('Actual visual review evidence required')
  if g.get('approvedSceneSpecHash')!=sha(job/'episode.json'):raise ValueError('SceneSpec changed after '+name+' review')
  for e in g['evidence']:
   if sha(ROOT/e['path'])!=e['sha256']:raise ValueError('Review evidence changed')
def main():
 p=argparse.ArgumentParser();p.add_argument('stage',choices=['sample','preview','final','localize']);p.add_argument('--job',type=Path,default=R/'ep08');p.add_argument('--shots');p.add_argument('--locale',choices=['ko','en'],default='ko');p.add_argument('--output',type=Path,required=True);a=p.parse_args();job=a.job.resolve()
 for g in ['TOPIC','STORY','STORYBOARD']:reviewed(job,g)
 if a.stage in ['preview','final','localize']:reviewed(job,'ART_PREVIEW')
 if a.stage in ['final','localize']:reviewed(job,'EDITING_PREVIEW')
 quality='preview' if a.stage=='preview' else 'final';ids=a.shots or ('S01' if a.stage=='sample' else None)
 log=job/'logs';log.mkdir(exist_ok=True);runs=[]
 def call(label,cmd):
  start=time.perf_counter()
  with (log/(label+'.log')).open('w',encoding='utf-8') as f:p=subprocess.run(list(map(str,cmd)),stdout=f,stderr=subprocess.STDOUT)
  runs.append(dict(stage=label,seconds=time.perf_counter()-start,returncode=p.returncode))
  write(log/'last_run.json',runs)
  write(log/(a.stage+'_runs.json'),runs)
  if p.returncode or 'Traceback (most recent call last)' in (log/(label+'.log')).read_text('utf-8',errors='replace'):raise RuntimeError(label+' failed; see log (Blender can return zero after a Python exception)')
 render=[BLENDER,'-b','--python',R/'render.py','--','--job',job,'--quality',quality]
 compose=[sys.executable,R/'compose.py','--job',job,'--quality',quality,'--locale',a.locale,'--output',a.output]
 if ids:render+=['--shots',ids];compose+=['--shots',ids]
 if a.stage!='localize':
  preview_index=read(job/'preview/native_index.json') if (job/'preview/native_index.json').exists() else {}
  wanted=[s for s in read(job/'episode.json')['shots'] if not ids or s['id'] in ids.split(',')]
  # Both native sizes share the exact aspect ratio. World-to-camera bounds are
  # normalized and recorded in final-output pixels, so resolution alone cannot alter them.
  projection_reuse=a.stage=='final' and all(preview_index.get(s['id'],{}).get('key')==native_key(s,config('STYLE_SPEC')['previewSize']) and (job/'preview/preflight'/f'{s["id"]}.json').exists() for s in wanted)
  if projection_reuse:
   runs.append(dict(stage='projection_cache',source='preview',reusedShots=len(wanted),reason='Matching native scene hashes and normalized camera projection'))
   call(a.stage+'_ui_check',compose+['--preflight','--quality','preview'])
  else:
   call(a.stage+'_projection',render+['--preflight'])
   if read(job/quality/'last_render.json')['errors']:raise ValueError('Native projection gate failed')
   call(a.stage+'_ui_check',compose+['--preflight'])
  call(a.stage+'_render',render)
  if read(job/quality/'last_render.json')['errors']:raise ValueError('Native gate failed')
 call(a.stage+'_compose',compose)
if __name__=='__main__':main()
