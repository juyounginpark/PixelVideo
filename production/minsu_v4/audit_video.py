"""Decode every actual MP4 frame; produce temporal review and mobile-size evidence."""
import argparse,subprocess
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
import imageio_ffmpeg
from common import R,ROOT,read,write,sha
def main():
    p=argparse.ArgumentParser();p.add_argument('--video',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--shots');a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    spec=read(R/'ep07/episode.json');shots=[s for s in spec['shots'] if not a.shots or s['id'] in a.shots.split(',')];reader=imageio_ffmpeg.read_frames(str(a.video));meta=next(reader);reader.close()
    command=[imageio_ffmpeg.get_ffmpeg_exe(),'-v','error','-i',str(a.video),'-an','-vf','scale=360:640:flags=neighbor','-f','rawvideo','-pix_fmt','rgb24','-'];proc=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    cursor=0;at=0;previous=None;duplicates=0;shotframes={s['id']:[] for s in shots};representatives=[];boundaries=[]
    for s in shots:boundaries.append((cursor,cursor+s['endFrame']-s['startFrame'],s));cursor=boundaries[-1][1]
    while True:
        raw=proc.stdout.read(360*640*3)
        if not raw:break
        if len(raw)!=360*640*3:raise ValueError('Partial frame')
        arr=np.frombuffer(raw,np.uint8).reshape(640,360,3)
        if previous is not None and np.array_equal(arr,previous):duplicates+=1
        previous=arr.copy();start,end,shot=next(x for x in boundaries if x[0]<=at<x[1]);local=at-start
        # Every 0.25 seconds plus exact event, extremes, and boundaries.
        if local%8==0 or local in (end-start-1,shot['emphasisEvent']['frame'],min(end-start-1,shot['emphasisEvent']['frame']+4), (end-start)//2):
            im=Image.fromarray(arr);im.save(a.out/f'{shot["id"]}_{local:03}.png');shotframes[shot['id']].append((local,im.copy()))
        if local==(end-start)//2:representatives.append((shot,at,Image.fromarray(arr)))
        at+=1
    proc.stdout.close();err=proc.stderr.read().decode();proc.stderr.close()
    if proc.wait():raise RuntimeError(err)
    if at!=cursor:raise ValueError(f'Frame count {at} != {cursor}')
    for sid,frames in shotframes.items():
        canvas=Image.new('RGB',(1080,660*((len(frames)+2)//3)),'#101b33');d=ImageDraw.Draw(canvas)
        for i,(f,im) in enumerate(frames):
            x=i%3*360;y=i//3*660;canvas.paste(im,(x,y+20));d.text((x+6,y+4),f'{sid} f{f} / {f/30:.2f}s',fill='white')
        canvas.save(a.out/f'{sid}_sequence.jpg',quality=96)
    canvas=Image.new('RGB',(1080,660*((len(representatives)+2)//3)),'#101b33');d=ImageDraw.Draw(canvas)
    for i,(s,f,im) in enumerate(representatives):
        x=i%3*360;y=i//3*660;canvas.paste(im,(x,y+20));d.text((x+6,y+4),f'{s["id"]} {f/30:.2f}s',fill='white')
    canvas.save(a.out/'overview.jpg',quality=96)
    baseline=read(R/'review/preservation_before.json');changed=[p for p,h in baseline.items() if sha(ROOT/p)!=h]
    report=dict(video=str(a.video),sha256=sha(a.video),metadata=meta,decodedFrames=at,exactDuplicateAdjacentFrames=duplicates,temporalSampling='every 8 frames (0.267 s), exact events and boundaries',mobileRaster=[360,640],preservationFiles=len(baseline),preservationChanges=changed,editorialApproval=False,limits=['Not a human listening test','No real-time playback or audience retention measurement'])
    write(a.out/'decode_qa.json',report);print('VIDEO_AUDIT',at,'frames; original changes',len(changed));return 0
if __name__=='__main__':raise SystemExit(main())
