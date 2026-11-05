"""Remove nearly invisible alpha noise without repainting the character."""
from pathlib import Path
import numpy as np
from PIL import Image

root = Path(__file__).resolve().parents[1]
source = root / "source/emma-master-v3.png"
target = root / "source/emma-master-v3-clean.png"
pixels = np.array(Image.open(source).convert("RGBA"))
pixels[pixels[:, :, 3] < 16] = 0
Image.fromarray(pixels).save(target)
print(target)
