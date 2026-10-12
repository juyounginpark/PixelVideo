"""Read existing logs; benchmark CPU composition without rendering/exporting video."""
import cProfile,io,json,pstats,re,statistics,sys,time,subprocess
from pathlib import Path
from PIL import Image
import imageio_ffmpeg
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R))
from typography import EditorialOverlay

def main():
    job=R/'ep06';spec=json.loads((job/'episode.json').read_text('utf-8'))
    raw=(job/'full_render.log').read_bytes();log=raw.decode('utf-16' if raw.startswith((b'\xff\xfe',b'\xfe\xff')) else 'utf-8',errors='replace')
    saves=[]
    for row in log.splitlines():
        m=re.search(r'^(\d+):(\d+\.\d+).*frames[\\/](\d+)\.png',row)
        if m:saves.append((int(m[3]),int(m[1])*60+float(m[2])))
    delta={f:t-saves[i-1][1] for i,(f,t) in enumerate(saves) if i and f==saves[i-1][0]+1}
    shots=[]
    for shot in spec['shots']:
        values=[delta[f] for f in range(shot['startFrame'],shot['endFrame']) if f in delta]
        shots.append({'id':shot['id'],'phase':shot['phase'],'intervals':len(values),'medianSeconds':round(statistics.median(values),4),'meanSeconds':round(statistics.mean(values),4)})
    full=json.loads((job/'review_failed/render_manifest_before.json').read_text('utf-8'))
    patch=json.loads((R/'ep06_repair_shot10/render_manifest.json').read_text('utf-8'))
    anchors=json.loads((job/'anchors.json').read_text('utf-8'));fx=json.loads((job/'effects.json').read_text('utf-8'))
    frames=[f for s in spec['shots'] for f in (s['startFrame']+15,(s['startFrame']+s['endFrame'])//2)]
    overlay=EditorialOverlay();images={};beg=time.perf_counter()
    for f in frames:
        with Image.open(job/'frames'/f'{f:04}.png') as im:images[f]=im.convert('RGB')
    load=time.perf_counter()-beg
    def compose():
        for f in frames:overlay.frame(images[f],f,spec,fx,anchors[str(f)])
    compose() # warm font/image caches
    timings=[]
    for _ in range(3):
        beg=time.perf_counter();compose();timings.append(time.perf_counter()-beg)
    prof=cProfile.Profile();prof.runcall(compose);buf=io.StringIO();pstats.Stats(prof,stream=buf).strip_dirs().sort_stats('cumtime').print_stats(16)
    (R/'optimization/composite_profile.txt').write_text(buf.getvalue(),'utf-8')
    enc=subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-hide_banner','-encoders'],capture_output=True,text=True).stdout
    root=R.parents[1];sizes={str(p.relative_to(root)):{'bytes':p.stat().st_size,'lines':len(p.read_text('utf-8').splitlines())} for p in [root/'AGENTS.md',root/'PROMPT_LOG.md',job/'episode.json',job/'anchors.json']}
    frame_files=list((job/'frames').glob('*.png'))
    report={'scope':'No new native render or video encode. Log intervals include pose/projection/render/PNG/checkpoint; CPU microbenchmark excludes encode and audio.',
      'render':{'frameCount':len(full['completed']),'loopSeconds':full['elapsedSeconds'],'patchFrameCount':len(patch['completed']),'patchLoopSeconds':patch['elapsedSeconds'],'parsedSaveLines':len(saves),'firstSaveAtSeconds':saves[0][1],'lastSaveAtSeconds':saves[-1][1],'shots':shots},
      'cpuComposite':{'framesPerRun':len(frames),'pngLoadSeconds':load,'warmRunSeconds':timings,'medianMsPerFrame':statistics.median(timings)/len(frames)*1000,'naive1050FrameSeconds':statistics.median(timings)/len(frames)*1050},
      'storage':{'nativePNGs':len(frame_files),'nativePNGBytes':sum(p.stat().st_size for p in frame_files)},
      'textArtifacts':sizes,'encoderBuildEntries':[line.strip() for line in enc.splitlines() if any(name in line for name in ('h264_qsv','h264_nvenc','libx264','h264_amf'))],
      'tokenUsage':'Not available in project artifacts; no measured token count or savings percentage.'}
    (R/'optimization/measurements.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf-8')
    print(json.dumps({'render':report['render'],'cpuComposite':report['cpuComposite'],'storage':report['storage'],'textArtifacts':sizes,'encoderBuildEntries':report['encoderBuildEntries']},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
