"""Create lossless web posters and review contact sheets from Blender renders."""
from pathlib import Path
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[2]
RENDERS=ROOT/'docs/dioramas'
SCENES=[('ai','AI systems'),('photography','Photography'),('graphic-arts','Brand'),('events','Live experiences'),('fabrication','Fabrication'),('family','Family')]

def sheet(suffix,filename):
 canvas=Image.new('RGB',(1800,1120),'#faf9f6');draw=ImageDraw.Draw(canvas)
 for i,(slug,title) in enumerate(SCENES):
  im=Image.open(RENDERS/(slug+suffix+'.png')).convert('RGBA');im.thumbnail((600,510))
  x=i%3*600;y=i//3*560
  canvas.paste(im,(x+(600-im.width)//2,y),im)
  draw.text((x+22,y+516),title,fill='#182b36',font_size=25)
 canvas.save(RENDERS/filename,quality=90)

for slug,_ in SCENES:
 Image.open(RENDERS/(slug+'.png')).save(ROOT/'site/public/dioramas'/(slug+'.webp'),format='WEBP',lossless=True,method=6)
sheet('','after.jpg')
sheet('-plan','plan.jpg')
sheet('-rear','rear.jpg')
print('Posters and three review sheets refreshed.')
