"""Measure warm reuse without replacing the final-delivery receipt."""
import subprocess,sys,time
from common import *
job=R/'ep08';out=R/'review/cache_benchmark';out.mkdir(exist_ok=True)
start=time.perf_counter()
with (out/'native.log').open('w') as f:subprocess.run(['C:/Program Files/Blender Foundation/Blender 5.0/blender.exe','-b','--python',str(R/'render.py'),'--','--job',str(job)],stdout=f,stderr=subprocess.STDOUT,check=True)
native=read(job/'final/last_render.json')
assert not native['errors'] and native['renderedFrames']==0 and native['reusedFrames']==1020
p=job/'final/compose_ko_MOBILE.json';original=p.read_bytes()
try:
 with (out/'compose.log').open('w') as f:subprocess.run([sys.executable,str(R/'compose.py'),'--output',str(out/'cached.mp4')],stdout=f,stderr=subprocess.STDOUT,check=True)
 ui=read(p);assert len(ui['uiCacheHits'])==9 and ui['audioCacheHit']
 write(out/'receipt.json',dict(nativeRenderSeconds=native['renderSeconds'],nativeWallSeconds=native['totalSeconds'],nativeReusedFrames=native['reusedFrames'],assetCache=native['assetCache'],uiCacheHits=ui['uiCacheHits'],uiCompositeSeconds=ui['totalSeconds'],audioCacheHit=ui['audioCacheHit'],totalWallSeconds=time.perf_counter()-start,benchmarkVideo=str(out/'cached.mp4')))
finally:p.write_bytes(original)
print('Warm cache PASS: 1020 native frames, 9 UI clips, audio')
