"""Current-run watcher: archive first timings, then batch independent QA jobs."""
import time,sys,shutil
from concurrent.futures import ThreadPoolExecutor
from common import R,ROOT,read,write
from run import call
deadline=time.monotonic()+2400
while True:
    state=R/'ep07/state.json';report=R/'ep07/final/compose.json'
    if state.exists() and report.exists() and read(state).get('stage')=='final':break
    if time.monotonic()>deadline:raise TimeoutError('Final production did not finish; inspect render/compose logs')
    time.sleep(3)
for name in ('last_render','compose'):
    dest=R/'ep07/final'/f'first_{name}.json'
    if not dest.exists():shutil.copy2(R/'ep07/final'/f'{name}.json',dest)
video=ROOT/'exports/MINSU_EP07_V4_DARK_MATTER.mp4'
with ThreadPoolExecutor(max_workers=2) as pool:
    jobs=[pool.submit(call,'final_video_audit',[sys.executable,R/'audit_video.py','--video',video,'--out',R/'ep07/final/review']),pool.submit(call,'final_technical_audit',[sys.executable,R/'technical_audit.py'])]
    for job in jobs:job.result()
call('final_compare',[sys.executable,R/'compare.py'])
write(R/'ep07/final/ready_for_editorial.json',dict(technical=read(R/'ep07/final/TECHNICAL_QA.json')['status'],requiresActualVisualReview=True))
print('FINAL_TECHNICAL_READY',flush=True)
