from pathlib import Path
import subprocess,json,re
import imageio_ffmpeg
ROOT=Path(__file__).resolve().parent
out=ROOT.parent.parent/'exports'/'MINSU_EP02_SILENT_v1.mp4'
ff=imageio_ffmpeg.get_ffmpeg_exe()
info=subprocess.run([ff,'-hide_banner','-i',str(out)],capture_output=True,text=True,encoding='utf-8',errors='replace').stderr
decode=subprocess.run([ff,'-v','error','-i',str(out),'-f','null','-'],capture_output=True,text=True,encoding='utf-8',errors='replace')
count,seconds=imageio_ffmpeg.count_frames_and_secs(str(out))
reader=imageio_ffmpeg.read_frames(str(out),pix_fmt='rgb24');meta=next(reader)
first=next(reader);last=first
for fr in reader:last=fr
import numpy as np
a=np.frombuffer(first,dtype=np.uint8).astype(float);b=np.frombuffer(last,dtype=np.uint8).astype(float)
report={'decode_pass':decode.returncode==0 and not decode.stderr.strip(),'width_height':meta['size'],'fps':meta['fps'],'frames':count,'duration_seconds':seconds,'audio_stream_present':bool(re.search(r'Stream .*Audio:',info)),'first_last_mean_pixel_difference':float(abs(a-b).mean()),'file_size_bytes':out.stat().st_size}
assert report['decode_pass'],decode.stderr
assert count==1032 and meta['size']==(720,1280) and meta['fps']==24
assert not report['audio_stream_present']
(out.parent/'MINSU_EP02_validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
