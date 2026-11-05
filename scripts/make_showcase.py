from pathlib import Path
from PIL import Image, ImageDraw

root=Path(__file__).resolve().parents[1]
atlas=Image.open(root/"package/spritesheet.png").convert("RGBA")
states=[("IDLE",0,[280,110,110,140,140,320]),("RUN",1,[120]*7+[220]),("WORK",7,[120]*5+[220])]
frames=[]
for t in range(0,6000,50):
    canvas=Image.new("RGBA",(576,242),"#f3f4f1")
    draw=ImageDraw.Draw(canvas)
    for slot,(name,row,durations) in enumerate(states):
        phase=t % sum(durations)
        col=0
        while phase>=durations[col]:
            phase-=durations[col]
            col+=1
        crop=atlas.crop((col*192,row*208,(col+1)*192,(row+1)*208))
        canvas.alpha_composite(crop,(slot*192,25))
        draw.text((slot*192+76,12),name,fill="#414739")
    frames.append(canvas.convert("RGB"))
frames[0].save(root/"preview/emma-showcase.gif",save_all=True,append_images=frames[1:],duration=50,loop=0)
print(root/"preview/emma-showcase.gif")
