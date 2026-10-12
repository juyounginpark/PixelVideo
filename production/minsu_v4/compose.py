"""Shot UI/encode cache + independent local audio cache; never calls an LLM."""
import argparse,sys,subprocess,time
from pathlib import Path
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R));sys.path.append(str(R.parent/'minsu_v2'))
from PIL import Image,ImageDraw
import imageio_ffmpeg
from common import read,write,sha,digest,config,validation,native_key
from typography import Overlay
from audio import AudioSynchronizer,mux,FF,ASSETS

def selected(spec,ids):return [s for s in spec['shots'] if not ids or s['id'] in ids.split(',')]
def main():
    p=argparse.ArgumentParser();p.add_argument('--job',type=Path,default=R/'ep07');p.add_argument('--quality',choices=['preview','final'],default='final');p.add_argument('--shots');p.add_argument('--stills',action='store_true');p.add_argument('--preflight',action='store_true');p.add_argument('--output',type=Path);a=p.parse_args()
    started=time.perf_counter();spec=read(a.job/'episode.json');validation(spec);shots=selected(spec,a.shots);overlay=Overlay();fontqa=overlay.type.preflight(spec);out=a.job/a.quality;out.mkdir(exist_ok=True);index=read(out/'native_index.json');report={'fonts':fontqa,'uiCacheHits':[],'uiRenderedShots':[],'errors':[]}
    if a.preflight:
        for s in shots:
            records=read(out/'preflight'/f'{s["id"]}.json')
            for f,row in records.items():
                try:overlay.frame(Image.new('RGB',(270,480),'#102237'),s,int(f),row['anchors'])
                except ValueError as e:report['errors'].append(str(e))
        write(out/'preflight_ui.json',report);print('UI_PREFLIGHT',len(report['errors']),report['errors'][:5]);return 1 if report['errors'] else 0
    if a.stills:
        results=[];review=out/'stills';review.mkdir(exist_ok=True)
        for s in shots:
            folder=Path(index[s['id']]['folder']);records=read(folder/'manifest.json')['frames']
            n=s['endFrame']-s['startFrame'];wanted=sorted(set([0,n//2,n-1,s['emphasisEvent']['frame'],min(n-1,s['emphasisEvent']['frame']+8)]))
            for f in wanted:
                if str(f) not in records:continue
                im,q=overlay.frame(Image.open(folder/f'{f:04}.png'),s,f,records[str(f)]['anchors']);im.save(review/f'{s["id"]}_{f:03}.png');results.append((s['id'],f,im))
        sheet=Image.new('RGB',(1080,510*((len(results)+3)//4)),'#101b33');d=ImageDraw.Draw(sheet)
        for i,(sid,f,im) in enumerate(results):
            x=i%4*270;y=i//4*510;sheet.paste(im.resize((270,480),Image.Resampling.NEAREST),(x,y+30));d.text((x+7,y+8),f'{sid} / {f}',fill='white')
        sheet.save(review/'sequence.jpg',quality=95);write(review/'technical.json',report);print('STILLS',len(results));return 0
    if not a.output:p.error('--output required')
    videos=[];events=[];cursor=0;ui_reports=[]
    for s in shots:
        item=index[s['id']];folder=Path(item['folder']);manifest=read(folder/'manifest.json');n=s['endFrame']-s['startFrame'];records=manifest['frames']
        if item['key']!=native_key(s,config('STYLE_SPEC')['previewSize' if a.quality=='preview' else 'nativeSize']):raise ValueError('Native cache is stale for current SceneSpec/code: '+s['id'])
        if len(records)!=n:raise ValueError('Native shot incomplete '+s['id'])
        # Recheck content integrity at the consumption boundary, including cached frames.
        for f in range(n):
            if sha(folder/f'{f:04}.png')!=records[str(f)]['sha256']:raise ValueError('Corrupt native frame')
        visible_fx={k:{'spark':v['spark']} for k,v in config('EFFECT_PRESETS')['presets'].items()}
        key=digest(dict(native=item['key'],nativeManifest=sha(folder/'manifest.json'),captionPlan=s['captionPlan'],labels=s['labels'],event=s['emphasisEvent'],effects=visible_fx,theme=config('TYPOGRAPHY_THEME'),typographyCode=sha(R/'typography.py'),composer=sha(R/'compose.py'),fonts=[sha(R.parents[1]/d['path']) for d in config('TYPOGRAPHY_THEME')['fonts'].values()]))
        clipdir=R/'cache/ui'/key;clipdir.mkdir(parents=True,exist_ok=True);video=clipdir/'silent.mp4';receipt=clipdir/'manifest.json'
        if receipt.exists() and video.exists() and read(receipt)['sha256']==sha(video):report['uiCacheHits'].append(s['id']);ui_reports+=read(clipdir/'ui_qa.json')
        else:
            report['uiRenderedShots'].append(s['id']);qa=[]
            cmd=[FF,'-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1080x1920','-r','30','-i','-','-an','-vf','scale=out_color_matrix=bt709:out_range=tv,setparams=range=limited:color_primaries=bt709:color_trc=bt709:colorspace=bt709','-c:v','libx264','-threads','4','-preset','fast','-crf','18','-pix_fmt','yuv420p','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709','-movflags','+faststart',str(video)]
            with (clipdir/'encode.log').open('w') as log:
                proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
                try:
                    for f in range(n):
                        im,q=overlay.frame(Image.open(folder/f'{f:04}.png'),s,f,records[str(f)]['anchors']);qa.append(q);proc.stdin.write(im.tobytes())
                finally:proc.stdin.close()
                if proc.wait():raise RuntimeError('Encoder failure '+s['id'])
            write(clipdir/'ui_qa.json',qa);write(receipt,dict(key=key,sha256=sha(video),frames=n));ui_reports+=qa
        videos.append(video);e=s['emphasisEvent'];preset=config('EFFECT_PRESETS')['presets'][e['preset']];ef=cursor+e['frame'];events.append(dict(frame=ef,time=ef/30,sound=preset['sound'],gainDb=preset['gainDb'],event=s['visualAction'],duck=e['type']=='DISCOVERY'));cursor+=n
        print('V4_COMPOSE',s['id'],'HIT' if s['id'] in report['uiCacheHits'] else 'RENDER',flush=True)
    # Separate assembly identity, so an audio-only change copies video without recomposition.
    assemblykey=digest([sha(v) for v in videos]);assembly=R/'cache/assembly'/assemblykey;assembly.mkdir(parents=True,exist_ok=True);silent=assembly/'silent.mp4'
    assembly_receipt=assembly/'manifest.json'
    if not (silent.exists() and assembly_receipt.exists() and read(assembly_receipt)['sha256']==sha(silent)):
        listing=assembly/'concat.txt';listing.write_text(''.join("file '"+str(v).replace('\\','/')+"'\n" for v in videos),'utf-8')
        subprocess.run([FF,'-v','error','-y','-f','concat','-safe','0','-i',str(listing),'-c','copy','-movflags','+faststart',str(silent)],check=True)
        write(assembly_receipt,dict(sha256=sha(silent),key=assemblykey))
    catalog=read(ASSETS/'catalog.json');used_ids={spec['audio']['track'],*[e['sound'] for e in events]};assets=[x for x in catalog['bgm']+catalog['sfx'] if x['id'] in used_ids]
    audiokey=digest(dict(settings=spec['audio'],events=events,duration=cursor/30,assets={x['id']:sha(ASSETS/x['path']) for x in assets},licenses=assets,engine=sha(R.parent/'minsu_v2/audio.py')));audio=R/'cache/audio'/audiokey;mix=audio/'mix.wav';receipt=audio/'manifest.json'
    hit=receipt.exists() and mix.exists() and read(receipt)['sha256']==sha(mix)
    if hit:hit=all((audio/f).exists() and sha(audio/f)==h for f,h in read(receipt).get('files',{}).items()) and bool(read(receipt).get('files'))
    if not hit:
        mix=AudioSynchronizer().build(cursor/30,events,audio,track_id=spec['audio']['track'],mood=spec['audio']['mood']);write(receipt,dict(sha256=sha(mix),key=audiokey,files={p.name:sha(p) for p in audio.iterdir() if p.is_file() and p.name!='manifest.json'}))
    a.output.parent.mkdir(exist_ok=True);loud=mux(silent,mix,a.output);count,duration=imageio_ffmpeg.count_frames_and_secs(str(a.output));assert count==cursor and abs(duration-cursor/30)<.04
    report.update(duration=duration,frameCount=count,fullDecode=True,validatedUIFrames=len(ui_reports),audioCacheHit=hit,audioFolder=str(audio),nativeSize=config('STYLE_SPEC')['previewSize' if a.quality=='preview' else 'nativeSize'],audio=loud,tts=False,totalSeconds=time.perf_counter()-started,sha256=sha(a.output),output=str(a.output),editorialApproval=False)
    write(out/('sample_compose.json' if a.shots else 'compose.json'),report);write(out/'ui_qa.json',ui_reports);print('V4_VIDEO',a.output,'seconds',round(report['totalSeconds'],1));return 0
if __name__=='__main__':raise SystemExit(main())
