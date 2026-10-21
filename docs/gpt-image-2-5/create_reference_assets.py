"""Rebuild original, deterministic reference fixtures; no API calls.

Run: uv run python docs/gpt-image-2-5/create_reference_assets.py
Optional --font/--cjk-font accept local font paths on other platforms.
The rendered PNG inputs ship with the skill; regeneration is not required.
"""
import argparse
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
DEST = ROOT / 'skills/gpt-image/assets/gpt-image-2-5'
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--font', default='/System/Library/Fonts/Helvetica.ttc')
parser.add_argument('--cjk-font', default='/System/Library/Fonts/STHeiti Light.ttc')
args = parser.parse_args()
DEST.mkdir(parents=True, exist_ok=True)

def font(size, cjk=False):
    return ImageFont.truetype(args.cjk_font if cjk else args.font, size)

def canvas(size=(1024, 1024), bg='#efe9dc'):
    im = Image.new('RGB', size, bg)
    return im, ImageDraw.Draw(im)

def save(im, name):
    im.save(DEST / name, optimize=True)

def center(draw, y, text, size, fill='#22342f', cjk=False, width=1152):
    draw.text((width // 2, y), text, font=font(size, cjk), fill=fill, anchor='mt')

def bottle(draw, x, y, scale=1):
    def box(values):
        return tuple(int((x if i % 2 == 0 else y) + v * scale) for i, v in enumerate(values))
    draw.rounded_rectangle(box((0, 95, 260, 590)), radius=int(52 * scale), fill='#e0ddd0', outline='#405550', width=max(1,int(4*scale)))
    draw.rounded_rectangle(box((55, 0, 205, 110)), radius=int(12*scale), fill='#354e40')
    draw.rectangle(box((35, 230, 225, 460)), fill='#f8f2e1')
    for ty, text, sz in [(270,'MORA',39),(340,'COLD BREW',22),(390,'250 ml',22)]:
        draw.text((int(x+130*scale),int(y+ty*scale)), text, font=font(int(sz*scale)), anchor='mt', fill='#253c31')

im,d=canvas()
d.ellipse((290,470,730,850), fill='#282e34')
d.ellipse((375,470,640,800), fill='#faf7ed')
d.polygon([(350,335),(295,140),(453,250)], fill='#282e34')
d.polygon([(640,335),(725,140),(557,245)], fill='#282e34')
d.ellipse((340,225,675,550),fill='#faf7ed',outline='#282e34',width=5)
d.ellipse((363,270,487,445),fill='#282e34')
d.ellipse((429,342,445,360),fill='white')
d.ellipse((569,342,585,360),fill='#282e34')
d.ellipse((458,419,560,500),fill='#dedacf')
d.ellipse((482,420,538,450),fill='#282e34')
d.rounded_rectangle((345,495,670,540),radius=20,fill='#b74635')
d.ellipse((473,521,523,569),fill='#c3a15f')
d.ellipse((341,780,456,872),fill='#faf7ed')
d.ellipse((556,780,671,872),fill='#faf7ed')
save(im,'dog.png')

im,d=canvas(bg='#eadfbf')
rng=random.Random(25)
for _ in range(24000):
    x,y=rng.randrange(1024),rng.randrange(1024)
    d.point((x,y), fill=rng.choice(['#d6cba9','#f2e8ca','#e0d1b0']))
d.rectangle((615,465,858,800),fill='#a57935')
d.rectangle((653,790,680,936),fill='#334b70')
d.rectangle((805,790,832,936),fill='#334b70')
d.ellipse((230,184,360,315),fill='#a57935')
d.polygon([(250,315),(345,315),(450,655),(178,655)],fill='#4c6482')
d.line([(210,650),(185,890),(135,910)],fill='#384353',width=18)
d.line([(388,650),(423,874),(478,891)],fill='#384353',width=18)
for offset in (-4,0,4):
    d.line([(250+offset,310),(175+offset,660),(450+offset,660),(345+offset,310)],fill='#45423a',width=2)
d.text((65,62),'STUDY',font=font(62),fill='#42402f')
save(im,'pencil-style.png')

im,d=canvas()
d.ellipse((270,848,777,944), fill='#c4c2ae')
bottle(d,360,160,1.2)
save(im,'bottle.png')

im,d=canvas(bg='#e5d6ae')
d.polygon([(0,0),(750,0),(240,1024),(0,1024)],fill='#f5e5be')
d.polygon([(265,680),(820,660),(1024,925),(610,960)],fill='#8b9279')
d.rectangle((60,720,680,928),fill='#d3ceba')
d.rounded_rectangle((260,425,480,735),radius=35,fill='#8b774f')
d.ellipse((275,397,465,457),fill='#aa9162')
d.text((65,62),'LIGHT STUDY',font=font(44),fill='#6b694c')
save(im,'lighting-reference.png')

im=Image.new('RGBA',(1024,1024),(255,255,255,0));d=ImageDraw.Draw(im)
d.text((512,420),'MORA',font=font(190),anchor='mt',fill='#253c31')
save(im,'approved-wordmark.png')

for name,chinese in [('tea-poster.png',True),('english-poster.png',False)]:
    im,d=canvas((1152,1536),'#f3ebd5')
    center(d,100,'山间冷泡' if chinese else 'MOUNTAIN BREW',88 if chinese else 76,cjk=chinese)
    center(d,222,'清爽每一天' if chinese else 'FRESH EVERY DAY',42,cjk=chinese)
    d.ellipse((237,1150,949,1260),fill='#c3c6af')
    bottle(d,389,403,1.45)
    center(d,1310,'16 元' if chinese else '$16',70,cjk=chinese)
    center(d,1430,'9月8日' if chinese else 'SEPTEMBER 8',38,cjk=chinese)
    save(im,name)

im,d=canvas((1536,1024),'#fffdf7')
d.line([(150,860),(150,150),(980,150),(1390,390),(1390,920),(150,860),(980,630),(1390,920)],fill='#343b39',width=6)
d.line([(980,150),(980,630)],fill='#343b39',width=6)
d.rectangle((290,260,650,495),outline='#343b39',width=6)
d.line([(470,260),(470,495)],fill='#343b39',width=5)
d.polygon([(290,650),(680,590),(830,700),(410,795)],fill='#dddcd5',outline='#343b39',width=5)
d.polygon([(290,650),(290,545),(675,488),(680,590)],fill='#eeede8',outline='#343b39',width=5)
d.polygon([(825,700),(1110,667),(1200,736),(902,784)],outline='#343b39',width=5)
d.line([(902,784),(902,860)],fill='#343b39',width=5)
d.line([(1200,736),(1200,812)],fill='#343b39',width=5)
d.text((282,203),'WINDOW',font=font(30),fill='#546055')
d.text((375,585),'SOFA',font=font(30),fill='#546055')
d.text((925,700),'TABLE',font=font(30),fill='#546055')
save(im,'room-sketch.png')

im,d=canvas()
d.rectangle((65,110,450,900),fill='#c7a47c')
for x in range(70,450,9):
    d.line([(x,110),(x+8,900)],fill='#ad8c63',width=2)
d.rectangle((515,110,955,485),fill='#ede6d6')
for x in range(515,955,8):d.line([(x,110),(x,485)],fill='#d7cdbc',width=2)
for y in range(110,485,8):d.line([(515,y),(955,y)],fill='#e0d7c6',width=2)
d.ellipse((585,580,885,865),fill='#687958')
save(im,'materials.png')

im,d=canvas()
body=[(330,180),(440,125),(585,125),(695,180),(625,865),(400,865)]
left=[(330,180),(260,250),(130,650),(265,710),(405,355)]
right=[(695,180),(765,250),(900,650),(765,710),(620,355)]
for polygon in (left,right,body):d.polygon(polygon,fill='#b76d43',outline='#5a4533',width=5)
d.polygon([(440,125),(512,290),(585,125)],fill='#efe9dc')
d.line([(512,290),(512,860)],fill='#5a4533',width=4)
for y in (380,510,640,770):d.ellipse((530,y,550,y+20),fill='#372f29')
save(im,'coat.png')
marked=im.copy();md=ImageDraw.Draw(marked)
md.ellipse((663,205,967,755),outline='#d0343a',width=12)
md.text((480,65),'RECOLOR THIS SLEEVE',font=font(32),fill='#d0343a')
md.line([(805,108),(817,240)],fill='#d0343a',width=7)
save(marked,'coat-annotated.png')
mask=Image.new('RGBA',im.size,(255,255,255,255));md=ImageDraw.Draw(mask)
md.polygon(right,fill=(255,255,255,0))
save(mask,'sleeve-mask.png')
print(f'Wrote {len(list(DEST.glob("*.png")))} reference fixtures to {DEST}')
