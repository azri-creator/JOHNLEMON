"""Stack chosen bands of the itinerary PDF pages into one tall strip for the 3D-tilt scroll.

Usage: python3 itin_strip.py <pages_dir> <segments.json> <out.jpg>

segments.json (pixel coords of the rendered pages, e.g. scale 5 -> 3060 px wide for Letter):
{
  "x": [660, 2400],                         # column to keep (the readable content column, no empty margins)
  "segments": [
    {"page": 1, "y": [100, 1325]},          # hero + stats row
    {"page": 1, "y": [2588, 2806]},         # stops band
    {"page": 1, "y": [2840, 3890], "white": [[1836, 2840, 2400, 3890]]},   # day list; paint over a sidebar
    {"page": 2, "y": [60, 1090]}
  ]
}
"white" boxes are page coords painted white: use them to remove anything that contradicts the script
(e.g. "Harga akan diumumkan" when the VO gives a price). Tell the user what was removed.
Prints the strip size and each segment's y offset (needed to place highlight lines and scroll targets).
Tip: find band edges by printing row means of the page (bright white = gaps between sections).
"""
import json
import sys

from PIL import Image, ImageDraw

pages_dir, seg_path, out = sys.argv[1], sys.argv[2], sys.argv[3]
cfg = json.load(open(seg_path))
x0, x1 = cfg["x"]
pages = {}
parts = []
for s in cfg["segments"]:
    p = s["page"]
    if p not in pages:
        pages[p] = Image.open(f"{pages_dir}/itin-p{p}.png").convert("RGB")
    y0, y1 = s["y"]
    c = pages[p].crop((x0, y0, x1, y1)).copy()
    d = ImageDraw.Draw(c)
    for wx0, wy0, wx1, wy1 in s.get("white", []):
        d.rectangle((wx0 - x0, wy0 - y0, wx1 - x0, wy1 - y0), fill=(255, 255, 255))
    parts.append(c)
W = x1 - x0
H = sum(c.height for c in parts)
strip = Image.new("RGB", (W, H), (255, 255, 255))
y = 0
offs = []
for c in parts:
    strip.paste(c, (0, y))
    offs.append(y)
    y += c.height
strip.save(out, quality=92)
strip.resize((W // 4, H // 4)).save(out.rsplit(".", 1)[0] + "_preview.jpg")
print("strip", W, H, "offsets", offs)
