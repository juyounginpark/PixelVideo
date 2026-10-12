"""Measure a real identical-input rerun without discarding the first-run evidence."""
import sys,time,subprocess
from common import R,ROOT,read,write,sha

def main():
    job=R/'ep07/final';video=ROOT/'exports/MINSU_EP07_V4_DARK_MATTER.mp4'
    first=read(job/'first_last_render.json');first_comp=read(job/'first_compose.json')
    before=sha(video);started=time.perf_counter()
    log=R/'review/cache_verification.log'
    with log.open('w',encoding='utf-8') as stream:
        subprocess.run([sys.executable,str(R/'run.py'),'verify-cache'],stdout=stream,stderr=subprocess.STDOUT,check=True)
    elapsed=time.perf_counter()-started
    native=read(job/'last_render.json');comp=read(job/'compose.json');after=sha(video)
    expected=read(R/'ep07/episode.json')['durationFrames']
    passed=(native['renderedFrames']==0 and native['reusedFrames']==expected
            and len(comp['uiCacheHits'])==10 and not comp['uiRenderedShots']
            and comp['audioCacheHit'] and before==after)
    report=dict(status='PASS' if passed else 'FAIL',sameInput=True,
                beforeSha256=before,afterSha256=after,bitIdentical=before==after,
                initialFullNativeSeconds=first['totalSeconds'],initialFullComposeSeconds=first_comp['totalSeconds'],
                warmNativeSeconds=native['totalSeconds'],warmComposeSeconds=comp['totalSeconds'],
                warmCommandWallSeconds=elapsed,renderedFrames=native['renderedFrames'],
                reusedFrames=native['reusedFrames'],uiCacheHits=comp['uiCacheHits'],
                audioCacheHit=comp['audioCacheHit'],assetCache=native['assetCache'],
                scope='Warm run uses identical delivered inputs. Initial full timings precede the S02 camera revision; no exact cold/warm speedup ratio or new-topic savings claim.')
    write(job/'CACHE_PROOF.json',report)
    print('CACHE_VERIFICATION',report['status'],round(elapsed,2),'seconds',flush=True)
    return 0 if passed else 1

if __name__=='__main__':raise SystemExit(main())
