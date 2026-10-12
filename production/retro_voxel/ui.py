"""Reusable, fixed-coordinate RPG overlay. Korean pixel fonts, no baked 3D text."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
ROOT = Path(__file__).resolve().parent
W,H = 1080,1920
NAVY = '#142653'
BLUE = '#2268bd'
MINT = '#087968'  # dark mint retains contrast on the pale dialogue panel
class RetroUI:
    def __init__(self, series, auxiliary, question):
        self.fonts = {s:ImageFont.truetype(str(ROOT/'fonts'/n),s) for s,n in [(36,'Galmuri11.ttf'),(48,'Galmuri11.ttf'),(60,'Galmuri11-Bold.ttf')]}
        self.header = Image.new('RGB',(W,432),'#070a12')
        d=ImageDraw.Draw(self.header)
        series_width=self.fonts[36].getlength(series)
        icon_x=round((1080-series_width-54)/2/6)*6
        self._center(d,(icon_x+54+series_width/2,142),series,36,'#f2f5f5')
        # Original codex emblem: square page, folded corner and observation dot.
        d.rectangle((icon_x,130,icon_x+30,160),fill='#64c7bd')
        d.polygon([(icon_x+18,130),(icon_x+30,142),(icon_x+18,142)],fill=BLUE)
        d.rectangle((icon_x+6,148,icon_x+12,154),fill=NAVY)
        d.rectangle((76,240,1028,420),fill='#081a36')
        d.rectangle((64,228,1016,408),fill=BLUE)
        d.rectangle((76,240,1004,396),outline='#5b98dc',width=6)
        self._center(d,(540,268),auxiliary,36,'white')
        self._center(d,(540,337),question,60,'#ffe06a',stroke=3)
        self.validate_text(auxiliary,36,900)
        self.validate_text(question,60,900)
    def _center(self,d,xy,text,size,color,stroke=0):
        d.text(xy,text,font=self.fonts[size],anchor='mm',fill=color,stroke_width=stroke,stroke_fill=NAVY)
    def validate_text(self,text,size,maxwidth):
        width=self.fonts[size].getlength(text)
        if width>maxwidth:raise ValueError(f'Text exceeds fixed component: {text!r}: {width} > {maxwidth}')
    def compose(self,world,lines,tags=(),event=None,age=3):
        if len(lines)!=2:raise ValueError('Dialogue must contain exactly two lines')
        image=Image.new('RGB',(W,H),'#070a12')
        image.paste(world.resize((1080,1488),Image.Resampling.NEAREST),(0,432))
        image.paste(self.header,(0,0))
        d=ImageDraw.Draw(image)
        for i,text in enumerate(tags):
            self.validate_text(text,36,870)
            length=int(self.fonts[36].getlength(text))+36
            y=480+i*72
            d.rectangle((64,y,64+length,y+54),fill='#101726')
            d.text((82,y+27),text,font=self.fonts[36],anchor='lm',fill='#eef5ee')
        # Fixed screen-space dialogue panel. No resizing or coordinate jitter.
        d.rectangle((76,1356,1028,1608),fill='#071631')
        d.rectangle((64,1344,1016,1596),fill='#f3f6ef')
        d.rectangle((64,1344,1016,1596),outline=NAVY,width=6)
        d.rectangle((76,1356,1004,1584),outline=BLUE,width=6)
        for x in (64,992):
            for y in (1344,1572):d.rectangle((x,y,x+24,y+24),fill=BLUE)
        for i,line in enumerate(lines):
            self.validate_text(line,48,860)
            # Rapid stepped arrival, all text readable by 0.24s. No slow typing.
            if age>=i*.12:
                d.text((112,1425+i*78),line,font=self.fonts[48],anchor='lm',fill=NAVY if i==0 else MINT)
        d.polygon([(954,1548),(978,1548),(966,1560)],fill=BLUE)
        if event:
            self.validate_text(event,36,750)
            if age>.2:
                # Short stepwise pop-in; text arrives once the panel has opened.
                progress=min(1,(age-.2)/.18)
                half=round(57*progress/6)*6
                d.rectangle((172,1157-half,920,1157+half),fill=NAVY)
                if progress>=1:
                    d.rectangle((184,1112,908,1202),outline='#63c9bb',width=6)
                    self._center(d,(546,1157),event,36,'#f5e488')
        return image
