# Paper grain overlay -> hf/assets/grain.png (1080x1920, used at multiply 20 % + screen 7 %)
import os, numpy as np
from PIL import Image, ImageFilter
P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rng = np.random.default_rng(7)
W, H = 1080, 1920
fine = rng.normal(0, 1, (H, W))
blot = np.array(Image.fromarray((rng.random((60, 34)) * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC).filter(ImageFilter.GaussianBlur(30)), float) / 255 - 0.5
fib = np.array(Image.fromarray((rng.random((H // 2, W // 8)) * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC), float) / 255 - 0.5
v = 128 + fine * 16 + blot * 40 + fib * 10
os.makedirs(f"{P}/hf/assets", exist_ok=True)
Image.fromarray(np.clip(v, 0, 255).astype(np.uint8)).save(f"{P}/hf/assets/grain.png", optimize=True)
