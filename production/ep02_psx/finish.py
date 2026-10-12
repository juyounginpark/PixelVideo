from pathlib import Path
import subprocess,sys,time
ROOT=Path(__file__).resolve().parent
start=time.time();last=-1
while True:
    count=len(list((ROOT/'frames').glob('*.png')));bucket=count//36
    if bucket!=last:print(f'RENDER_FILES {count}/384',flush=True);last=bucket
    p=ROOT/'render.log';raw=p.read_bytes() if p.exists() else b''
    log=raw.decode('utf-16' if raw.startswith((b'\xff\xfe',b'\xfe\xff')) else 'utf-8',errors='replace')
    if 'RENDER_COMPLETE' in log:break
    if time.time()-start>1800:raise TimeoutError('Render monitoring timeout')
    time.sleep(3)
missing=[f for f in range(1,385) if not (ROOT/'frames'/f'{f:05d}.png').exists()]
assert not missing,missing
for name,args in [('compose.py',['--preview']),('compose.py',[]),('verify.py',[])]:subprocess.run([sys.executable,str(ROOT/name),*args],check=True)
print('DELIVERABLE_READY',flush=True)
