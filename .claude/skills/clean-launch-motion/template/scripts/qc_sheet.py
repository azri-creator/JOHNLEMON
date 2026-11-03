"""QC contact sheet: frames of a video at given times, tiled with timestamps. Optional second video (e.g. the
approved reference) is placed beside each frame for a side-by-side look comparison.

usage: /usr/bin/python3 scripts/qc_sheet.py <video> <out.jpg> <cols> <t1> <t2> ...
       /usr/bin/python3 scripts/qc_sheet.py <video> <out.jpg> <cols> --ref <ref.mp4> [--ref-times r1,r2,...] <t1> <t2> ...
"""
import io, subprocess, sys
from PIL import Image, ImageDraw
from common import ffmpeg

FF = ffmpeg()
args = sys.argv[1:]
video, out, cols = args[0], args[1], int(args[2])
rest = args[3:]
ref, ref_times = None, None
if rest and rest[0] == "--ref":
    ref, rest = rest[1], rest[2:]
    if rest and rest[0] == "--ref-times":
        ref_times, rest = [float(v) for v in rest[1].split(",")], rest[2:]
times = [float(v) for v in rest]
TW = 360


def grab(path, t, label, colour):
    raw = subprocess.run([FF, "-v", "error", "-ss", f"{t:.3f}", "-i", path, "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "-"],
                         capture_output=True, check=True).stdout
    im = Image.open(io.BytesIO(raw)).convert("RGB")
    im = im.resize((TW, int(TW * im.height / im.width)))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 150, 30], fill=colour)
    d.text((6, 8), f"{label} {t:6.2f}s", fill=(255, 255, 255))
    return im


tiles = []
for i, t in enumerate(times):
    a = grab(video, t, "HF", (43, 124, 245))
    if ref:
        b = grab(ref, ref_times[i] if ref_times else t, "REF", (36, 36, 58))
        pair = Image.new("RGB", (TW * 2 + 4, a.height), (255, 255, 255))
        pair.paste(b, (0, 0)); pair.paste(a, (TW + 4, 0))
        a = pair
    tiles.append(a)
tw, th = tiles[0].width, tiles[0].height
rows = (len(tiles) + cols - 1) // cols
sheet = Image.new("RGB", (cols * (tw + 10) + 10, rows * (th + 10) + 10), (30, 30, 36))
for i, im in enumerate(tiles):
    sheet.paste(im, (10 + (i % cols) * (tw + 10), 10 + (i // cols) * (th + 10)))
sheet.save(out, quality=88)
print("saved", out, sheet.size)
