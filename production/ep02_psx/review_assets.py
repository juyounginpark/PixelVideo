from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json
ROOT=Path(__file__).resolve().parent;EXPORT=ROOT.parent.parent/'exports'
font=ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf',28)
small=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',20)
sheet=Image.new('RGB',(1440,620),'#E8E6D8');d=ImageDraw.Draw(sheet)
d.text((24,13),'MINSU / LOW-POLY CHARACTER',font=font,fill='#252B39')
for i,(name,label) in enumerate([('front','FRONT'),('threequarter','THREE-QUARTER'),('back','BACK'),('face','FACE DETAIL')]):
    im=Image.open(ROOT/f'model_{name}.png').convert('RGB').resize((360,480),Image.Resampling.LANCZOS)
    sheet.paste(im,(360*i,58));d.text((360*i+18,550),label,font=small,fill='#252B39')
stats=json.loads((ROOT/'model_stats.json').read_text(encoding='utf-8'))
d.text((24,589),f"{stats['character_triangles_after_modifiers']:,} triangles / geometry preview before PSX treatment",font=small,fill='#656C71')
sheet.save(EXPORT/'MINSU_LOWPOLY_MODEL_SHEET.jpg',quality=96)

# Review completed samples without executing the full encoder.
source=(ROOT/'compose.py').read_text(encoding='utf-8').split('TIMES=')[0]
ns={'__file__':str(ROOT/'compose.py'),'__name__':'preview_only'}
exec(compile(source,str(ROOT/'compose.py'),'exec'),ns)
for t in [0,12.8]:ns['source_frame'](t).save(ROOT/f'psx_ui_{t:g}.png')
print('MODEL_SHEET_AND_UI_PREVIEW_READY')
