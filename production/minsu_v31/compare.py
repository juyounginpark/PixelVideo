"""Evidence boards from real MP4s; no inferred reference camera parameters."""
import argparse,json,subprocess
from pathlib import Path
from PIL import Image,ImageDraw
import imageio_ffmpeg

R=Path(__file__).resolve().parent;ROOT=R.parents[1]

def decoded(path,seconds):
    raw=subprocess.check_output([imageio_ffmpeg.get_ffmpeg_exe(),'-v','error','-ss',str(seconds),'-i',str(path),'-frames:v','1','-vf','scale=270:480','-f','rawvideo','-pix_fmt','rgb24','-'])
    return Image.frombytes('RGB',(270,480),raw)

def main():
    p=argparse.ArgumentParser();p.add_argument('--final',action='store_true');a=p.parse_args()
    media={v['id']:ROOT/v['source'] for v in json.loads((R/'review/media_evidence.json').read_text('utf-8'))}
    # Similar editorial functions, not matching science claims or identical camera angles.
    rows=[('CHARACTER / HOOK',[1,2,3],24),('CONCEPT / DETAIL',[21,11,13],411),('INFORMATION / COMPARISON',[35,23,22],580)]
    canvas=Image.new('RGB',(1080,1554),'#102237');d=ImageDraw.Draw(canvas)
    entries=[]
    for row,(label,times,newframe) in enumerate(rows):
        y=row*518;d.text((8,y+4),label,fill='#FFBC5A')
        for col,key in enumerate(('ref3','ref4','ep05')):
            t=times[col];canvas.paste(decoded(media[key],t),(col*270,y+38));d.text((col*270+8,y+21),f'{key} / {t:.2f}s',fill='white')
            entries.append({'role':label,'source':str(media[key].relative_to(ROOT)),'timeSeconds':t})
        if a.final:
            path=ROOT/'exports/MINSU_EP06_V31_ICE.mp4';im=decoded(path,newframe/30)
        else:
            path=R/'ep06/preview'/f'{newframe:04}.png';im=Image.open(path).resize((270,480))
        canvas.paste(im,(810,y+38));d.text((818,y+21),f'EP06 V3.1 / {newframe/30:.2f}s',fill='white')
        entries.append({'role':label,'source':str(path.relative_to(ROOT)),'sourceFrame':newframe,'timeSeconds':newframe/30})
    name='FINAL_REFERENCE_COMPARISON' if a.final else 'DESIGN_REFERENCE_COMPARISON'
    canvas.save(R/'review'/f'{name}.jpg',quality=96)
    (R/'review'/f'{name}.json').write_text(json.dumps(entries,ensure_ascii=False,indent=2),'utf-8')
    print(name)

if __name__=='__main__':main()
