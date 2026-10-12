"""Post-encode evidence, preservation and frame/event contact sheets."""
import argparse,csv,hashlib,json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from graphics import EffectRenderer

ROOT=Path(__file__).resolve().parents[2]
FONT=ROOT/'production/minsu_v2/fonts/NanumGothic-ExtraBold.ttf'

def audit(job):
    spec=json.loads((job/'spec.json').read_text('utf-8'))
    fx=json.loads((job/'effects.json').read_text('utf-8'))
    anchors=json.loads((job/'anchors.json').read_text('utf-8'))
    final=json.loads((job/'FINAL_QA.json').read_text('utf-8'))
    preflight=json.loads((job/'PREFLIGHT_QA.json').read_text('utf-8'))
    audio=json.loads((job/'audio/audio_qa.json').read_text('utf-8'))
    before=json.loads((ROOT/'production/minsu_v2/design_revision/preservation_before.json').read_text('utf-8'))
    preservation={}
    for group,files in before.items():
        changed=[p for p,sha in files.items() if not (ROOT/p).is_file() or hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=sha]
        preservation[group]={'checked':len(files),'changed':changed}
    assert all(not x['changed'] for x in preservation.values()),preservation
    assert final['fullDecodePassed'] and final['frameCount']==spec['durationFrames']
    assert not preflight['errors'] and all(preflight['motionChecks'].values())
    assert audio['bgmCoveragePassed'] and audio['loopClickCheckPassed'] and audio['peakPassed']
    assert all(e['syncErrorSeconds']<=1/audio['sampleRate'] for e in audio['events'])
    assert all(abs(e['frame']/spec['fps']-e['time'])<1e-8 for e in audio['events'])
    render=EffectRenderer();out=job/'review';out.mkdir(exist_ok=True)
    def picture(f):
        im=Image.open(job/'frames'/f'{f:04}.png').resize((1080,1920),Image.Resampling.NEAREST)
        return render.frame(im,f,spec,fx,anchors[str(f)])[0]
    def sheet(frames,name,columns=5):
        im=Image.new('RGB',(270*columns,520*((len(frames)+columns-1)//columns)),'#18212A');d=ImageDraw.Draw(im)
        font=ImageFont.truetype(str(FONT),19)
        for i,f in enumerate(frames):
            x=(i%columns)*270;y=(i//columns)*520
            im.paste(picture(f).resize((270,480)),(x,y+32))
            d.text((x+8,y+6),f'{f:03} / {f/spec["fps"]:.2f}s',font=font,fill='white')
        im.save(out/name,quality=94)
    sheet([s['startFrame']+(s['endFrame']-s['startFrame'])//2 for s in spec['shots']],'cuts.jpg')
    for s in spec['shots']:
        frames=sorted(set([s['startFrame']+3,(s['startFrame']+s['endFrame'])//2,s['endFrame']-3]))
        sheet(frames,s['id']+'_motion.jpg',3)
    for e in fx['CameraEffectTimeline']:
        sheet([max(0,e['frame']-1),e['frame']+3,e['frame']+8,min(spec['durationFrames']-1,e['endFrame']+1)],e['eventId']+'_zoom.jpg',4)
    with (out/'effect_frames.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f);w.writerow(['eventId','shotId','effect','frame','endFrameExclusive','timeSeconds','target','intensity'])
        for e in fx['EffectTimeline']:w.writerow([e['eventId'],e['shotId'],e['type'],e['frame'],e['endFrame'],e['frame']/spec['fps'],e['target'],e['intensity']])
    items=[('레퍼런스 3 · 12초',ROOT/'research/reels_v2/ref3/12.0.png'),('레퍼런스 4 · 2초',ROOT/'research/reels_v2/ref4/02.0.png'),('기존 EP04 V2',ROOT/'production/minsu_v2/preview/0112.png')]
    comparison=Image.new('RGB',(360*4,700),'#18212A');d=ImageDraw.Draw(comparison);font=ImageFont.truetype(str(FONT),23)
    for i,(label,path) in enumerate(items):
        im=Image.open(path).convert('RGB');im.thumbnail((360,640));comparison.paste(im,(i*360+(360-im.width)//2,50));d.text((i*360+8,12),label,font=font,fill='white')
    comparison.paste(picture(105).resize((360,640)),(1080,50));d.text((1088,12),'신규 EP05 V3',font=font,fill='white')
    comparison.save(out/'reference_comparison.jpg',quality=94)
    result={'preservation':preservation,'preflight':preflight,'final':final,'audioEvents':len(audio['events']),
            'maxAudioSyncErrorSeconds':max((e['syncErrorSeconds'] for e in audio['events']),default=0),
            'bgmCoveragePassed':audio['bgmCoveragePassed'],'loopClickCheckPassed':audio['loopClickCheckPassed'],
            'actualEffectCounts':fx['counts'],'visualReview':'Review generated contact sheets separately; these assertions do not award an aesthetic score.'}
    (out/'DELIVERY_QA.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),'utf-8')
    print('DELIVERY_AUDIT_PASS',out)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--job',required=True,type=Path);a=p.parse_args();audit(a.job)
