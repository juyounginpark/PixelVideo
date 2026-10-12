from pathlib import Path
import subprocess,json,re
import imageio_ffmpeg,numpy as np
ROOT=Path(__file__).resolve().parent;EXP=ROOT.parent.parent/'exports'
out=EXP/'MINSU_EP02_PSX_LOWPOLY_SILENT_v3.mp4';ff=imageio_ffmpeg.get_ffmpeg_exe()
info=subprocess.run([ff,'-hide_banner','-i',str(out)],capture_output=True,text=True,encoding='utf-8',errors='replace').stderr
decode=subprocess.run([ff,'-v','error','-i',str(out),'-f','null','-'],capture_output=True,text=True,encoding='utf-8',errors='replace')
count,seconds=imageio_ffmpeg.count_frames_and_secs(str(out))
r=imageio_ffmpeg.read_frames(str(out),pix_fmt='rgb24');meta=next(r);first=next(r);last=first
for f in r:last=f
report={'decode_pass':decode.returncode==0 and not decode.stderr.strip(),'output_size':meta['size'],'source_render_size':[360,640],'container_fps':meta['fps'],'source_animation_fps':12,'action_playback_speed':1.2,'frames':count,'duration_seconds':seconds,'has_audio':bool(re.search(r'Stream .*Audio:',info)),'first_last_mean_pixel_difference':float(abs(np.frombuffer(first,dtype=np.uint8).astype(float)-np.frombuffer(last,dtype=np.uint8).astype(float)).mean()),'bytes':out.stat().st_size}
assert report['decode_pass'],decode.stderr
assert count==1080 and meta['size']==(720,1280) and meta['fps']==24
assert not report['has_audio']
(EXP/'MINSU_EP02_PSX_LOWPOLY_validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
