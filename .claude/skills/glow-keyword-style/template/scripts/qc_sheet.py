"""QC contact sheet: /usr/bin/python3 scripts/qc_sheet.py <video> <out.jpg> t1 t2 ... (seconds). Tiles 6 per row, time-labelled."""
import subprocess, sys, os, tempfile
from PIL import Image, ImageDraw
vid, out, ts = sys.argv[1], sys.argv[2], [float(x) for x in sys.argv[3:]]
tw, th = int(os.environ.get("TW", 300)), int(int(os.environ.get("TW", 300)) * 16 / 9)
tmp = tempfile.mkdtemp()
cols = 6; rows = (len(ts) + cols - 1) // cols
sheet = Image.new("RGB", (tw * cols, th * rows), (40, 40, 40)); d = ImageDraw.Draw(sheet)
for i, t in enumerate(ts):
    f = os.path.join(tmp, f"{i}.png")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t}", "-i", vid, "-frames:v", "1", f], check=True)
    im = Image.open(f).convert("RGB").resize((tw, th))
    x, y = (i % cols) * tw, (i // cols) * th
    sheet.paste(im, (x, y)); d.rectangle([x, y, x + 64, y + 22], fill=(0, 0, 0)); d.text((x + 4, y + 4), f"{t:.2f}", fill=(255, 255, 0))
sheet.save(out, quality=88)
