"""Wait for render completion, then apply reviewed partial fix and deliver sequentially."""
from pathlib import Path
import subprocess,sys,time,json
R=Path(__file__).resolve().parent;ROOT=R.parents[1];BLENDER='C:/Program Files/Blender Foundation/Blender 5.0/blender.exe'
status=R/'pipeline_status.json'
def stage(name):
    status.write_text(json.dumps({'stage':name,'timestamp':time.time()},indent=2),'utf-8');print(name,flush=True)
def run(name,cmd):
    stage(name)
    with (R/f'{name}.log').open('w',encoding='utf-8') as log:
        p=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
    if p.returncode:raise RuntimeError(name+' failed; inspect '+str(R/f'{name}.log'))
try:
    stage('waiting_for_full_render');deadline=time.time()+3600
    while True:
        try:data=json.loads((R/'render_manifest.json').read_text('utf-8'))
        except (FileNotFoundError,json.JSONDecodeError):data={}
        if len(data.get('completed',[]))==1080:break
        if time.time()>deadline:raise TimeoutError('Full render did not complete')
        time.sleep(2)
    run('hook_patch',[BLENDER,'-b','--python',str(R/'patch_hook.py')])
    run('hook_render',[BLENDER,'-b','--python',str(R/'render.py'),'--','--shot','SHOT_01'])
    run('motion_qa',[BLENDER,'-b','--python',str(R/'audit_motion.py')])
    run('compose',[sys.executable,str(R/'compose.py')])
    run('audio_deliver',[sys.executable,str(R/'deliver.py')])
    run('final_qa',[sys.executable,str(R/'qa.py')])
    run('final_preview',[sys.executable,str(R/'compose.py'),'--preview'])
    run('motion_reviews',[sys.executable,str(R/'motion_reviews.py')])
    stage('complete')
except Exception as e:
    status.write_text(json.dumps({'stage':'failed','error':str(e)},indent=2),'utf-8');raise
