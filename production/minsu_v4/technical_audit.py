"""Artifact-backed technical QA; no aesthetic pass is derived from these checks."""
import argparse,sys,subprocess
from pathlib import Path
from PIL import Image
import numpy as np
from common import R,ROOT,read,write,sha,config,native_key
from typography import Overlay
import imageio_ffmpeg
sys.path.append(str(R.parent/'minsu_v2'))
from audio import read_wav,FF
def main():
    p=argparse.ArgumentParser();p.add_argument('--quality',choices=['preview','final'],default='final');a=p.parse_args();job=R/'ep07';spec=read(job/'episode.json');index=read(job/a.quality/'native_index.json');o=Overlay();errors=[];count=0;pixelChecks=[]
    for s in spec['shots']:
        folder=Path(index[s['id']]['folder']);man=read(folder/'manifest.json');size=config('STYLE_SPEC')['previewSize' if a.quality=='preview' else 'nativeSize']
        if index[s['id']]['key']!=native_key(s,size):errors.append('Stale native '+s['id'])
        n=s['endFrame']-s['startFrame']
        for f in range(n):
            row=man['frames'][str(f)];path=folder/f'{f:04}.png'
            if sha(path)!=row['sha256']:errors.append('Corrupt frame '+str(path))
            for subject in ('character','outer'):
                if subject in row['anchors']:
                    x0,y0,x1,y1=row['anchors'][subject]['rect']
                    if x0<20 or y0<60 or x1>1060 or y1>1810:errors.append(subject+' clipped '+s['id']+'/'+str(f))
            try:
                im,q=o.frame(Image.open(path),s,f,row['anchors']);count+=1
                if f==n//2:
                    native=np.array(Image.open(path).convert('RGB'));factor=1080//native.shape[1];expected=native.repeat(factor,0).repeat(factor,1);actual=np.array(im)
                    mask=np.ones((1920,1080),bool)
                    for b in q['texts']:
                        x0,y0,x1,y1=map(int,b['rect']);mask[max(0,y0-10):min(1920,y1+10),max(0,x0-10):min(1080,x1+10)]=False
                    # Measure a fixed UI-free bottom strip; event sparks/FACT panels stay above it.
                    mask[:1740,:]=False;equal=np.all(expected==actual,axis=2)
                    pixelChecks.append(dict(shot=s['id'],equalFraction=float(equal[mask].mean()),pixels=int(mask.sum())))
            except ValueError as e:errors.append(str(e))
    comp=read(job/a.quality/'compose.json');audio=read(Path(comp['audioFolder'])/'audio_qa.json')
    reader=imageio_ffmpeg.read_frames(comp['output']);metadata=next(reader);reader.close()
    if metadata['size']!=(1080,1920) or metadata['fps']!=30 or metadata['codec']!='h264' or metadata['audio_codec']!='aac':errors.append('Output format mismatch')
    # Verify actual AAC-decoded timing against the source mix, not just event counters.
    decoded=job/a.quality/'decoded_audio_qa.wav'
    subprocess.run([FF,'-v','error','-y','-i',comp['output'],'-map','0:a:0','-ar','48000','-ac','2','-c:a','pcm_s16le',str(decoded)],check=True)
    ref=read_wav(Path(comp['audioFolder'])/'mix.wav').mean(1)[::8];actual=read_wav(decoded).mean(1)[::8];n=min(len(ref),len(actual));ref=ref[:n];actual=actual[:n]
    fftsize=1<<(2*n-1).bit_length();corr=np.fft.irfft(np.fft.rfft(actual,fftsize)*np.conj(np.fft.rfft(ref,fftsize)),fftsize)
    lags=np.arange(-300,301);peak=int(np.argmax(corr[lags%fftsize]));lag=int(lags[peak]);confidence=float(corr[lag%fftsize]/(np.linalg.norm(ref)*np.linalg.norm(actual)));aac_shift=lag/6000
    if abs(aac_shift)>1/30 or confidence<.90:errors.append('Decoded AAC alignment mismatch')
    baseline=read(R/'review/preservation_before.json');changed=[p for p,h in baseline.items() if sha(ROOT/p)!=h]
    events=audio['events'];sync=max([abs(e['syncErrorSeconds']) for e in events] or [0])
    if sync>1/48000:errors.append('SFX sample placement mismatch')
    expected=[s['startFrame']+s['emphasisEvent']['frame'] for s in spec['shots']]
    if [e['frame'] for e in events]!=expected:errors.append('SFX event frame mismatch')
    if not audio['peakPassed'] or not audio['loopClickCheckPassed'] or not audio['bgmCoveragePassed']:errors.append('Audio QA failure')
    if any(x['equalFraction']!=1 for x in pixelChecks):errors.append('Native nearest upscale mismatch')
    report=dict(status='PASS' if not errors and not changed else 'FAIL',checkedNativeAndUIFrames=count,errors=errors,outputMetadata=metadata,fontCoverage=o.type.preflight(spec),pixelNearestEvidence=pixelChecks,audioEventCount=len(events),maxAudioSyncErrorSeconds=sync,aacDecodedAlignmentSeconds=aac_shift,aacCorrelation=confidence,audioPeakPassed=audio['peakPassed'],audioLoopPassed=audio['loopClickCheckPassed'],audioTimingReported=events,audioFinalMeasurement=comp['audio'],preservedFiles=len(baseline),preservationChanges=changed,ttsEnabled=False,editorialPass=False)
    write(job/a.quality/'TECHNICAL_QA.json',report);print('TECHNICAL_QA',report['status'],count,'frames',len(errors),'errors');return 1 if errors or changed else 0
if __name__=='__main__':raise SystemExit(main())
