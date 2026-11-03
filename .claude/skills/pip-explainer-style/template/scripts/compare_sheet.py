"""Side-by-side check against a reference video (an approved earlier cut, or the reference the user sent).
  /usr/bin/python3 scripts/compare_sheet.py <render.mp4> <reference.mp4> qc/compare.jpg 0.3 3.2 6.2 ...
Each tile: left = this build, right = reference, at the same timestamp."""
import os, subprocess, sys, tempfile
from PIL import Image, ImageDraw
mine, ref, out, ts = sys.argv[1], sys.argv[2], sys.argv[3], [float(x) for x in sys.argv[4:]]
W, H, per = 270, 480, 3
tmp = tempfile.mkdtemp()
grab = lambda v, t, p: subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t}", "-i", v, "-frames:v", "1", p], check=True)
rows = (len(ts) + per - 1) // per
s = Image.new("RGB", (per * (2 * W + 16), rows * (H + 24)), (30, 30, 30)); d = ImageDraw.Draw(s)
for i, t in enumerate(ts):
    a, b = os.path.join(tmp, f"a{i}.png"), os.path.join(tmp, f"b{i}.png"); grab(mine, t, a); grab(ref, t, b)
    x, y = (i % per) * (2 * W + 16), (i // per) * (H + 24)
    s.paste(Image.open(a).convert("RGB").resize((W, H)), (x, y + 24)); s.paste(Image.open(b).convert("RGB").resize((W, H)), (x + W, y + 24))
    d.text((x + 4, y + 5), f"t={t:.2f}s  this build", fill=(255, 230, 0)); d.text((x + W + 4, y + 5), "reference", fill=(150, 220, 255))
os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True); s.save(out, quality=88); print("wrote", out)
