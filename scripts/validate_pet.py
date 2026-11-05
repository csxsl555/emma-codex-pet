"""Validate the shipped v1 atlas without a machine-specific skill dependency."""
from pathlib import Path
import hashlib
import json
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]

def validate():
    path = ROOT / "package/spritesheet.png"
    meta = json.loads((ROOT / "package/pet.json").read_text(encoding="utf-8"))
    errors = []
    image = Image.open(path)
    if image.size != (1536, 1872) or image.mode != "RGBA":
        errors.append("Expected a 1536x1872 RGBA atlas")
    if meta.get("id") != "bvb-emma-2627" or meta.get("spritesheetPath") != "spritesheet.png":
        errors.append("Unexpected metadata or sprite path")
    data = np.array(image.convert("RGBA"))
    if np.any(data[data[:,:,3] == 0, :3]):
        errors.append("RGB residue in fully transparent pixels")
    counts = [6,8,8,4,5,8,6,6,6]
    if not errors:
        for row, count in enumerate(counts):
            for col in range(8):
                alpha = data[row*208:(row+1)*208,col*192:(col+1)*192,3]
                if col >= count:
                    if np.any(alpha): errors.append(f"Unused cell {row},{col} is not empty")
                else:
                    ys,xs = np.where(alpha>16)
                    if len(xs)<50:
                        errors.append(f"Empty used cell {row},{col}")
                    elif min(xs.min(),ys.min(),191-xs.max(),207-ys.max())<8:
                        errors.append(f"Cell {row},{col} has insufficient padding")
    result = {"ok":not errors,"file":"package/spritesheet.png","format":"PNG","mode":image.mode,"width":image.width,"height":image.height,"sprite_version_number":1,"occupied_frames":57,"sha256":hashlib.sha256(path.read_bytes()).hexdigest(),"errors":errors}
    (ROOT/"validation.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    return result

if __name__ == "__main__":
    result=validate()
    print(json.dumps(result,indent=2))
    raise SystemExit(0 if result["ok"] else 1)
