"""Wait for the local render, then encode and validate the deliverable."""
from pathlib import Path
import subprocess,sys,time,json
ROOT=Path(__file__).resolve().parent
start=time.time();last=-1
while True:
    count=len(list((ROOT/'frames_final').glob('*.png')))
    bucket=count//24
    if bucket!=last:print(f'RENDER_FILES {count}/384',flush=True);last=bucket
    log=(ROOT/'render.log').read_text(encoding='utf-16',errors='replace') if (ROOT/'render.log').exists() else ''
    # PowerShell versions may write either UTF-16 or UTF-8 logs.
    if 'RENDER_COMPLETE' not in log and (ROOT/'render.log').exists():log=(ROOT/'render.log').read_text(encoding='utf-8',errors='replace')
    if 'RENDER_COMPLETE' in log:break
    if time.time()-start>1800:raise TimeoutError('Render did not complete within the monitoring window')
    time.sleep(3)
missing=[f for f in range(1,385) if not (ROOT/'frames_final'/f'{f:05d}.png').exists()]
assert not missing,missing
for name,args in [('check_layout.py',[]),('compose.py',['--preview']),('compose.py',[]),('verify.py',[])]:
    subprocess.run([sys.executable,str(ROOT/name),*args],check=True)
print('DELIVERABLE_READY',flush=True)
