"""Assemble still comparison/evidence, run tests and verify protected source hashes."""
import hashlib,json,subprocess,sys
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parent;ROOT=R.parents[1];OUT=R/'design_revision'
font=ImageFont.truetype(str(R/'fonts/NanumGothic-ExtraBold.ttf'),24)
names=['neutral','curious','surprise','happy','side','back']
sheet=Image.new('RGB',(270*6,530),'#18212a');d=ImageDraw.Draw(sheet)
for i,name in enumerate(names):
    im=Image.open(OUT/f'{name}.png').convert('RGB')
    im.resize((1080,1920),Image.Resampling.NEAREST).save(OUT/f'{name}_1080.png')
    sheet.paste(im.resize((270,480),Image.Resampling.NEAREST),(i*270,40));d.text((i*270+15,5),name,font=font,fill='white')
sheet.save(OUT/'character_sheet.png')

items=[('레퍼런스 3 · 12초',ROOT/'research/reels_v2/ref3/12.0.png'),
       ('레퍼런스 4 · 2초',ROOT/'research/reels_v2/ref4/02.0.png'),
       ('기존 V2',R/'preview/0112.png'),('V2.1 정지 검증',OUT/'happy_1080.png')]
compare=Image.new('RGB',(360*4,700),'#18212a');d=ImageDraw.Draw(compare)
for i,(label,path) in enumerate(items):
    im=Image.open(path).convert('RGB');im.thumbnail((360,640))
    compare.paste(im,(i*360+(360-im.width)//2,50));d.text((i*360+12,12),label,font=font,fill='white')
compare.save(OUT/'reference_comparison.jpg',quality=94)

before=json.loads((OUT/'preservation_before.json').read_text('utf-8'));protected={}
for group,files in before.items():
    modified=[p for p,sha in files.items() if not (ROOT/p).exists() or hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=sha]
    protected[group]={'count':len(files),'modified':modified}
newvideos=[p.relative_to(ROOT).as_posix() for p in (ROOT/'exports').glob('*.mp4') if p.relative_to(ROOT).as_posix() not in before['videos']]
assert not newvideos and all(not g['modified'] for g in protected.values())
test=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(R),'-p','test*.py'],capture_output=True,text=True)
assert test.returncode==0,test.stderr
white={}
for name in ['legacy_outline','legacy_raw','without_weighted_normals','box_blend_safe']:
    a=np.asarray(Image.open(OUT/f'{name}.png').convert('RGB'));white[name]=int(np.all(a>=235,axis=2).sum())
qa={'protected':protected,'newVideos':newvideos,'tests':{'returncode':test.returncode,'output':test.stdout+test.stderr},
    'nearWhitePixelsInSameCameraDiagnostic':white,'limits':'White-pixel threshold is an artifact diagnostic for these controlled stills only; not a general appearance score.'}
(OUT/'validation.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),'utf-8')
print(json.dumps(qa,ensure_ascii=False,indent=2))
