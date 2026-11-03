"""Footage prep for a Glow Keyword build (writes into hf/assets/).

  graded   graded master of the source -> hf/assets/graded.mp4 (1080x1920, 30 fps, short GOP, BT.709)
           + hf/assets/lastframe.jpg (frame at SRC_END, used by the end-card freeze)
  cutout   presenter cut-outs for explainer layouts -> hf/assets/<name>.webm (VP9 + alpha)
           matte from `npx hyperframes remove-background`, alpha-merged onto the GRADED pixels (exact cut-out)

Usage:  SRC_MOV=/path/to/source.mov /usr/bin/python3 scripts/prep_footage.py graded [cutout]
The grade itself (per-shot balance + shared look) lives in grade.py and is unchanged from the Remotion version.
"""
import json, os, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from grade import SHOTS, look_chain

ROOT = os.path.abspath(os.path.join(HERE, ".."))
HF = os.path.join(ROOT, "hf"); A = os.path.join(HF, "assets"); WORK = os.path.join(ROOT, "work")
for d in (A, WORK, os.path.join(A, "fonts")): os.makedirs(d, exist_ok=True)
TM = json.load(open(os.path.join(ROOT, "timing.json")))
SRC_END = float(TM["SRC_END"])
TAG = ["-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-color_range", "tv"]

# explainer layouts that use the cut-out presenter (source seconds). Empty = no cut-out in this video.
# Example from Jago Prompt: {"cutout_a": (15.2, 27.8), "cutout_b": (37.3, 44.9)}
CUTOUTS = {k: tuple(v) for k, v in TM.get("CUTOUTS", {}).items()}


def src():
    s = os.environ.get("SRC_MOV")
    if not s or not os.path.exists(s):
        sys.exit("set SRC_MOV to the presenter source video")
    return s


def ff(*a):
    subprocess.run(["ffmpeg", "-v", "error", "-y", *a], check=True)


def graded():
    parts, labels = [], []
    shots = [(a, min(b, SRC_END + 0.2), eq, cb) for a, b, eq, cb in SHOTS if a < SRC_END + 0.2]
    for i, (a, b, eq, cb) in enumerate(shots):
        parts.append(f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS,{eq},{cb}[s{i}]"); labels.append(f"[s{i}]")
    fc = ";".join(parts) + ";" + "".join(labels) + f"concat=n={len(shots)}:v=1:a=0[cat];" + look_chain("cat", "lk") + \
        ";[lk]setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709:range=tv[out]"
    out = os.path.join(A, "graded.mp4")
    ff("-i", src(), "-filter_complex", fc, "-map", "[out]", "-r", "30", "-t", f"{SRC_END + 0.2:.3f}",
       "-c:v", "libx264", "-crf", "12", "-preset", "medium", "-g", "10", "-pix_fmt", "yuv420p", *TAG, "-an", out)
    # end-card freeze frame = the last shown frame of the footage
    ff("-ss", f"{max(0, SRC_END - 1 / 30):.4f}", "-i", out, "-frames:v", "1", "-q:v", "2", os.path.join(A, "lastframe.jpg"))
    # fonts ship with the skill template
    fsrc = os.path.join(ROOT, "assets", "fonts")
    if os.path.isdir(fsrc):
        for f in os.listdir(fsrc): shutil.copy(os.path.join(fsrc, f), os.path.join(A, "fonts", f))
    print("wrote", out)


def cutout(name, a, b):
    seg = os.path.join(WORK, f"{name}_seg.mp4"); matte = os.path.join(WORK, f"{name}_matte.webm")
    ff("-ss", f"{a}", "-to", f"{b}", "-i", os.path.join(A, "graded.mp4"), "-c:v", "libx264", "-crf", "8", "-pix_fmt", "yuv420p", *TAG, seg)
    # u2net_human_seg matte; if it says the weights aren't cached, copy ~/.u2net/u2net_human_seg.onnx into
    # ~/.cache/hyperframes/background-removal/models/
    subprocess.run(["npx", "--yes", "hyperframes", "remove-background", "--quality", "best", "-o", matte, seg], check=True, cwd=HF)
    out = os.path.join(A, f"{name}.webm")
    # exact cut-out: graded pixels + matte alpha (never the matte tool's own RGB), light 1 px edge soften
    ff("-i", seg, "-c:v", "libvpx-vp9", "-i", matte, "-filter_complex",
       "[1:v]alphaextract,gblur=sigma=0.8[m];[0:v][m]alphamerge,format=yuva420p",
       "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-crf", "20", "-b:v", "0", "-row-mt", "1", "-auto-alt-ref", "0", *TAG, "-an", out)
    print("wrote", out)


if __name__ == "__main__":
    what = sys.argv[1:] or ["graded"]
    if "graded" in what: graded()
    for k, (a, b) in CUTOUTS.items():
        if "cutout" in what or k in what: cutout(k, a, b)
