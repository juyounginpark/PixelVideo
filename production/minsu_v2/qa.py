"""Inspectable output checks. Does not infer aesthetics or retention from differences."""
from pathlib import Path
import argparse, json, re, subprocess, hashlib, math
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import imageio_ffmpeg
from content import SceneCompiler
from audio import measure
R=Path(__file__).resolve().parent;ROOT=R.parents[1];FF=imageio_ffmpeg.get_ffmpeg_exe()

def command(args):
    p=subprocess.run([FF,'-hide_banner','-nostdin',*map(str,args)],capture_output=True,text=True,encoding='utf-8',errors='replace')
    if p.returncode:raise RuntimeError(p.stderr[-2000:])
    return p.stdout,p.stderr

def video_hash(path):return command(['-i',path,'-map','0:v:0','-c:v','copy','-f','hash','-hash','sha256','-'])[0].strip()

def audio_only_qa():
    silent=ROOT/'exports/MINSU_EP04_THORNY_DEVIL_SILENT_v1.mp4';final=ROOT/'exports/MINSU_EP04_THORNY_DEVIL_BGM_SFX_v1.mp4'
    _,info=command(['-i',final,'-f','null','-'])
    report={'file':str(final.relative_to(ROOT)),'fullDecodePassed':True,'videoStreamUnchanged':video_hash(silent)==video_hash(final),
            'AACPresent':'Audio: aac' in info,'loudness':measure(final),'voiceNarration':False,
            'stems':'production/minsu_v2/audio_mix','humanListeningReview':False}
    (R/'AUDIO_V1_QA.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf-8')
    if not report['videoStreamUnchanged'] or not report['AACPresent']:raise RuntimeError(report)
    return report

def final_qa():
    spec=json.loads((R/'episode.json').read_text('utf-8'));SceneCompiler().validate(spec)
    export=ROOT/'exports/MINSU_EP04_V2_BGM_SFX.mp4';_,info=command(['-i',export,'-f','null','-'])
    reader=imageio_ffmpeg.read_frames(str(export),pix_fmt='rgb24');metadata=next(reader);count=0
    for _ in reader:count+=1
    framepaths=[R/'frames'/f'{i:04}.png' for i in range(1,1081)]
    missing=[p.name for p in framepaths if not p.exists()]
    sizes={Image.open(p).size for p in framepaths if p.exists()}
    records=json.loads((R/'ui_qa.json').read_text('utf-8'))
    overlaps=[{'frame':r['frame'],'subjects':r['faceAnchorOverlaps']} for r in records if r['faceAnchorOverlaps']]
    # Local event image changes, reported as diagnostic evidence, never subjective pass/fail.
    pairs=[(9,25),(56,93),(365,465),(512,625),(693,735),(820,900)]
    diffs=[]
    for a,b in pairs:
        im0=np.array(Image.open(R/'frames'/f'{a:04}.png')).astype(float)
        im1=np.array(Image.open(R/'frames'/f'{b:04}.png')).astype(float)
        diffs.append({'frames':[a,b],'meanAbsolutePixelDifference':round(float(np.mean(abs(im1-im0))),3)})
    report={'fullDecodePassed':True,'metadata':metadata,'frameCount':count,'expectedFrames':1080,
            'missingNativeFrames':missing,'nativeSizes':list(sizes),'AACPresent':'Audio: aac' in info,
            'BT709Tagged':'bt709' in info,'H264Present':'Video: h264' in info,'YUV420pPresent':'yuv420p' in info,
            'loudness':measure(export),'uiFramesValidated':len(records),'faceAnchorOverlapWarnings':overlaps,
            'eventFrameDifferences':diffs,'characterAssets':json.loads((R/'asset_manifest.json').read_text('utf-8')),
            'limits':['Pixel differences do not prove meaningful motion.','Face-anchor tests are not full silhouette occlusion tests.',
                      'No real Instagram app viewing, audience retention measurement or human listening approval.',
                      'External water paths are schematic; no numerical capillary fluid solver.']}
    (R/'FINAL_QA.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf-8')
    assert count==1080 and not missing and sizes=={(540,960)} and metadata['size']==(1080,1920)
    assert metadata['fps']==30 and report['AACPresent'] and float(report['loudness']['input_tp'])<=-1
    assert report['BT709Tagged'] and report['H264Present'] and report['YUV420pPresent']
    return report

def comparison():
    from compose import OverlayComposer
    spec=json.loads((R/'episode.json').read_text('utf-8'));composer=OverlayComposer(spec,json.loads((R/'anchors.json').read_text('utf-8')))
    old=ROOT/'exports/MINSU_EP04_THORNY_DEVIL_SILENT_v1.mp4';out=R/'comparison';out.mkdir(exist_ok=True)
    samples=[('관찰 / 반응',4,2.8),('모세관',16.5,15.5),('입 도달',28,24.5)]
    sheet=Image.new('RGB',(1080,1080),'#172129');d=ImageDraw.Draw(sheet);f=ImageFont.truetype(str(R/'fonts/NanumGothic-ExtraBold.ttf'),24)
    for j,(title,a,b) in enumerate(samples):
        path=out/f'v1_{j}.png';command(['-y','-ss',a,'-i',old,'-frames:v','1',path])
        im,_=composer.frame(round(b*30)+1);im.save(out/f'v2_{j}.png')
        for row,img in enumerate((Image.open(path),im)):
            thumb=img.resize((270,480));x=j*360+45;y=row*535+30;sheet.paste(thumb,(x,y));d.text((j*360+35,y+480),f'V{row+1} · {title}',font=f,fill='white')
    sheet.save(ROOT/'exports/MINSU_EP04_V1_V2_COMPARE.jpg',quality=95)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--audio-only',action='store_true');a=p.parse_args()
    if a.audio_only:print(json.dumps(audio_only_qa(),ensure_ascii=False,indent=2))
    else:final_qa();comparison();print('FINAL_QA_WRITTEN')
