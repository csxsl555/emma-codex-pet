"""Pack generated Emma poses into Codex's existing 8x9 local pet format.

Only removes alpha noise, crops, scales proportionally and aligns frames.
The user explicitly authorized this processing; source artwork stays intact.
"""
from pathlib import Path
import hashlib
import json
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
for folder in ("package", "preview"):
    (ROOT / folder).mkdir(exist_ok=True)
COUNTS = [6, 8, 8, 4, 5, 8, 6, 6, 6]
NAMES = ["idle", "running-right", "running-left", "waving", "jumping", "failed", "waiting", "running", "review"]
DURATIONS = [[280,110,110,140,140,320], [120]*7+[220], [120]*7+[220], [140]*3+[280], [140]*4+[280], [140]*7+[240], [150]*5+[260], [120]*5+[220], [150]*5+[280]]

def runs(indices, gap=1):
    return [group for group in np.split(indices, np.where(np.diff(indices) > gap)[0]+1) if len(group)]

pixels = np.array(Image.open(ROOT / "source/emma-sprites-v3.png").convert("RGBA"))
pixels[pixels[:,:,3] < 16] = 0
source = Image.fromarray(pixels)
source.save(ROOT / "source/emma-sprites-v3-clean.png")
alpha = pixels[:,:,3]
row_groups = [g for g in runs(np.where((alpha>64).sum(axis=1)>4)[0]) if len(g)>30]
assert len(row_groups) == 9, f"Expected nine rows, found {len(row_groups)}"
atlas = Image.new("RGBA", (1536,1872))
contact = Image.new("RGB", (192*8, 240*9), "#e8edf2")
draw = ImageDraw.Draw(contact)
rows_report = []
for row, (group, count, name) in enumerate(zip(row_groups, COUNTS, NAMES)):
    y0, y1 = int(group[0]), int(group[-1])+1
    columns = [g for g in runs(np.where((alpha[y0:y1]>64).sum(axis=0)>1)[0], gap=2) if len(g)>15]
    assert len(columns) == count, f"{name}: expected {count} poses, found {len(columns)}: {[(int(g[0]),int(g[-1])) for g in columns]}"
    crops = []
    boxes = []
    for col, xs in enumerate(columns):
        # Midpoints of genuine clear gutters avoid borrowing neighboring pixels.
        left = 0 if col==0 else (int(columns[col-1][-1])+int(xs[0]))//2
        right = source.width if col==count-1 else (int(xs[-1])+int(columns[col+1][0]))//2
        top = 0 if row==0 else (int(row_groups[row-1][-1])+y0)//2
        bottom = source.height if row==8 else (y1+int(row_groups[row+1][0]))//2
        crop = source.crop((left,top,right,bottom))
        box = crop.getchannel("A").point(lambda x: 255 if x>=32 else 0).getbbox()
        assert box is not None
        crop = crop.crop(box)
        crops.append(crop)
        boxes.append([left+box[0],top+box[1],left+box[2],top+box[3]])
    scale = min(176/max(im.height for im in crops), 164/max(im.width for im in crops))
    cells = []
    for col,crop in enumerate(crops):
        resized = crop.resize((round(crop.width*scale),round(crop.height*scale)), Image.Resampling.LANCZOS)
        data = np.array(resized)
        data[data[:,:,3]<8] = 0
        resized = Image.fromarray(data)
        x = (192-resized.width)//2
        jump_lift = [0,6,12,6,0][col] if row==4 else 0
        y = 194-resized.height-jump_lift
        assert x>=10 and y>=10 and x+resized.width<=182 and y+resized.height<=198, (name,col,x,y,resized.size)
        cell = Image.new("RGBA",(192,208))
        cell.alpha_composite(resized,(x,y))
        atlas.alpha_composite(cell,(col*192,row*208))
        bg = Image.new("RGBA",cell.size,"#e8edf2")
        bg.alpha_composite(cell)
        contact.paste(bg.convert("RGB"),(col*192,row*240+28))
        cells.append(cell)
    draw.text((8,row*240+8), f"{row+1:02d}  {name}  /  {count} frames", fill="#26313d")
    # White-backed GIF avoids GIF's one-bit alpha jagged edges. PNG remains RGBA.
    gif_frames = []
    for cell in cells:
        bg=Image.new("RGBA",cell.size,"#f5f5f3")
        bg.alpha_composite(cell)
        gif_frames.append(bg.convert("RGB"))
    gif_frames[0].save(ROOT/f"preview/{name}.gif",save_all=True,append_images=gif_frames[1:],duration=DURATIONS[row],loop=0)
    if row==0:
        cells[0].save(ROOT/"preview/emma-idle.png")
    rows_report.append({"state":name,"count":count,"source_boxes":boxes,"scale":scale})

atlas.save(ROOT/"package/spritesheet.png")
contact.save(ROOT/"preview/contact-sheet.png")
metadata = {
    "id":"bvb-emma-2627",
    "displayName":"Emma · BVB 26/27",
    "description":"多特蒙德吉祥物 Emma，3D 造型与 26/27 主场球衣，陪你学习、写代码和庆祝任务完成。",
    "spritesheetPath":"spritesheet.png"
}
(ROOT/"package/pet.json").write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
report={"format":"v1","size":list(atlas.size),"cell_size":[192,208],"occupied_frames":sum(COUNTS),"rows":rows_report,"sha256":hashlib.sha256((ROOT/"package/spritesheet.png").read_bytes()).hexdigest()}
(ROOT/"preview/packing-report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"size":atlas.size,"frames":sum(COUNTS),"sha256":report["sha256"]}))
