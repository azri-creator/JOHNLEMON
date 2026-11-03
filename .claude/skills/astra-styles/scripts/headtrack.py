#!/usr/bin/env python3
"""Head-top / head-centre track from a person matte (VP9-alpha webm), 4 samples per second.
Usage: python3 headtrack.py <matte.webm> <out.json> [fps=4]
Output: [[t, top_y, centre_x], ...] in the matte's own pixel space (e.g. 1920x1080). build.py reads this as
HT to pivot every camera push on the face and to place hero words above the head."""
import sys, json, subprocess
import numpy as np
src, out = sys.argv[1], sys.argv[2]
fps = float(sys.argv[3]) if len(sys.argv) > 3 else 4.0
pr = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                     "-of", "csv=p=0", src], capture_output=True, text=True).stdout.strip().split(",")
W, H = int(pr[0]), int(pr[1])
w = 320; h = int(round(w * H / W / 2) * 2)
cmd = ["ffmpeg", "-v", "error", "-c:v", "libvpx-vp9", "-i", src, "-vf", f"fps={fps},alphaextract,scale={w}:{h}",
       "-f", "rawvideo", "-pix_fmt", "gray", "-"]
raw = subprocess.run(cmd, capture_output=True).stdout
frames = np.frombuffer(raw, dtype=np.uint8).reshape(-1, h, w)
res = []
for i, f in enumerate(frames):
    m = f > 128
    rows = np.where(m.sum(1) >= 3)[0]            # ignore stray pixels
    if len(rows) == 0:
        continue
    top = rows[0]
    band = m[top:top + max(2, int(h * .12))]      # the head, not the shoulders
    ys, xs = np.nonzero(band)
    res.append([round(i / fps, 2), int(round(top * H / h)), int(round(xs.mean() * W / w))])
json.dump(res, open(out, "w"))
print(len(res), "samples; first", res[:2], "last", res[-1:])
