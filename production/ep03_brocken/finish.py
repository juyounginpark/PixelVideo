from pathlib import Path
import subprocess,sys,time,json
import imageio_ffmpeg
r=Path(__file__).resolve().parent
while True:
    p=r/'render_final.log';b=p.read_bytes() if p.exists() else b''
    s=b.decode('utf-16' if b.startswith(b'\xff\xfe') else 'utf-8',errors='replace')
    if 'RENDER_COMPLETE' in s:break
    if 'Traceback (most recent call last)' in s:raise RuntimeError(s[-2000:])
    time.sleep(3)
assert len(list((r/'frames').glob('*.png')))==276
for args in [['--preview'],[]]:subprocess.run([sys.executable,str(r/'compose.py'),*args],check=True)
v=r.parent.parent/'exports/MINSU_EP03_BROCKEN_SILENT_v1.mp4';ff=imageio_ffmpeg.get_ffmpeg_exe()
p=subprocess.run([ff,'-v','error','-i',str(v),'-f','null','-'],capture_output=True,text=True);assert p.returncode==0,p.stderr
reader=imageio_ffmpeg.read_frames(str(v));meta=next(reader);count=sum(1 for _ in reader)
assert count==1008,(count,meta)
info=subprocess.run([ff,'-i',str(v)],capture_output=True,text=True).stderr;assert 'Audio:' not in info
report={'decode_pass':True,'frames':count,'duration_seconds':42,'size':meta['size'],'has_audio':False}
(v.parent/'MINSU_EP03_BROCKEN_validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(report)
