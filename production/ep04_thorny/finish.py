"""Wait for actual completed render markers, then composite and validate."""
import time,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parent
def read(p):
    if not p.exists():return ''
    b=p.read_bytes();return b.decode('utf-16' if b.startswith((b'\xff\xfe',b'\xfe\xff')) else 'utf-8',errors='replace')
started=time.time()
while True:
    logs=[read(R/n) for n in ['render.log','observation_final.log','hook_patch.log','capillary_patch.log','comparison_patch.log','cross_section_patch.log']]
    if all(marker in log for marker,log in zip(['RENDER_COMPLETE','OBSERVATION_PATCH_COMPLETE','HOOK_SEQUENCE_PATCH_COMPLETE','CAPILLARY_PATCH_COMPLETE','COMPARISON_PATCH_COMPLETE','CROSS_SECTION_PATCH_COMPLETE'],logs)):break
    if time.time()-started>1800:raise TimeoutError('No completed render within 30 minutes')
    time.sleep(5)
print('ALL_NATIVE_RENDER_STAGES_COMPLETE',flush=True)
subprocess.run([sys.executable,str(R.parent/'retro_voxel/render_episode.py'),str(R/'episode.json')],check=True)
subprocess.run([sys.executable,str(R/'review_assets.py')],check=True)
subprocess.run([sys.executable,str(R.parent/'retro_voxel/render_episode.py'),str(R/'episode.json'),'--preview'],check=True)
print('HANDOFF_READY',flush=True)
