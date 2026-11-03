"""Footage + B-roll for the HyperFrames project (everything lands in hf/assets/).

1) hf/assets/video/main.mp4 : the EDL segments of $SRC_MOV joined in order, light natural face lift (tone curve only,
   no colour look), 30 fps, short GOP (-g 10) so the renderer seeks fast, tagged BT.709. HLG/PQ sources are
   tone-mapped to SDR first (the footage grade is otherwise untouched).
2) B-roll : AI example clips/stills re-used from earlier projects (labelled 'Contoh visual AI' on screen).
   PER VIDEO: edit CLIPS / STILLS. Paths are relative to $BROLL_DIR (default: the repo's input/ folder).
3) Logos for the end card: $LOGO_ICON and $LOGO_TEXT (the student's own brand). Optional.

  SRC_MOV=<footage> SRC_DUR=<s> BROLL_DIR=<folder> /usr/bin/python3 scripts/prep_footage.py [main] [broll]"""
import json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from edl import SEGS, SRC
ROOT = os.path.abspath(os.path.join(HERE, "..")); A = os.path.join(ROOT, "hf", "assets")
BROLL = os.environ.get("BROLL_DIR") or os.path.abspath(os.path.join(ROOT, "..", "..", "input"))
LOOK = "curves=master='0/0 0.25/0.30 0.5/0.56 0.75/0.79 1/1',eq=saturation=1.03"
# HDR (HLG / PQ) -> SDR BT.709, only used when the source is HDR
HDR2SDR = ("zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=hable:desat=0,"
           "zscale=t=bt709:m=bt709:r=tv,format=yuv420p")
TAG = ["-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-color_range", "tv"]
ENC = ["-c:v", "libx264", "-preset", "medium", "-pix_fmt", "yuv420p", "-g", "10", *TAG]
ff = lambda *a: subprocess.run(["ffmpeg", "-v", "error", "-y", *a], check=True)

# ---- PER VIDEO: B-roll (name: (file relative to BROLL_DIR, start s, duration s)) ----
CLIPS = {
    "ai_xray": ("Product Video/Good Shot 4.mp4", 0.0, 6.0),
    "ai_dispenser": ("Product Video/Good Shot 1.mp4", 0.0, 6.0),
    "ai_drink": ("Product Video/Good Shot 5.mp4", 0.0, 6.0),
    "ai_fashion": ("broll/Fashion Use-Case.mov", 0.0, 4.0),
}
STILLS = {  # name: (file relative to BROLL_DIR, time s)
    "ai_img_kitchen": ("Product Video/Good Shot 2.mp4", 2.0),
    "ai_poster_sofa": ("broll/sofa_poster.mp4", 9.5),
    "ai_img_dispenser": ("Product Video/Good Shot 3.mp4", 3.0),
    "ai_img_sofa": ("broll/sofa_poster.mp4", 5.2),
    "ai_img_drink": ("broll/Video Hak Sendiri.mp4", 9.0),
    "ai_img_dark": ("Product Video/Good Shot 1.mp4", 3.0),
}
REAL_CONTENT_T = 20.5  # a still of the presenter for the "konten sebenar" card (his own real content)


def is_hdr(path):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", path], capture_output=True, text=True).stderr
    return any(k in r for k in ("arib-std-b67", "smpte2084", "bt2020"))


def main():
    os.makedirs(os.path.join(A, "video"), exist_ok=True); os.makedirs(os.path.join(A, "img"), exist_ok=True)
    pre = (HDR2SDR + ",") if is_hdr(SRC) else ""
    if pre: print("HDR source -> tone-mapped to SDR BT.709 (render with --sdr)")
    parts = [f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS[s{i}]" for i, (a, b) in enumerate(SEGS)]
    fc = ";".join(parts) + ";" + "".join(f"[s{i}]" for i in range(len(SEGS))) + f"concat=n={len(SEGS)}:v=1:a=0,{pre}{LOOK},fps=30[out]"
    ff("-i", SRC, "-filter_complex", fc, "-map", "[out]", *ENC, "-crf", "15", "-an", os.path.join(A, "video", "main.mp4"))
    ff("-ss", str(REAL_CONTENT_T), "-i", SRC, "-frames:v", "1", "-vf", f"{pre}{LOOK},scale=540:-1", "-q:v", "2", os.path.join(A, "img", "real_content.jpg"))


def broll():
    os.makedirs(os.path.join(A, "video"), exist_ok=True); os.makedirs(os.path.join(A, "img"), exist_ok=True)
    for k, (f, a, d) in CLIPS.items():
        p = os.path.join(BROLL, f)
        if not os.path.exists(p): print("missing B-roll (skipped):", p); continue
        ff("-ss", str(a), "-t", str(d), "-i", p, "-an", "-vf", "scale=540:960:force_original_aspect_ratio=increase,crop=540:960,fps=30",
           *ENC, "-crf", "18", os.path.join(A, "video", f"{k}.mp4"))
    for k, (f, t) in STILLS.items():
        p = os.path.join(BROLL, f)
        if not os.path.exists(p): print("missing still (skipped):", p); continue
        ff("-ss", str(t), "-i", p, "-frames:v", "1", "-vf", "scale=540:960:force_original_aspect_ratio=increase,crop=540:960", "-q:v", "2",
           os.path.join(A, "img", f"{k}.jpg"))
    for name, env in (("logo_icon.png", "LOGO_ICON"), ("logo_text.png", "LOGO_TEXT")):
        if os.environ.get(env) and os.path.exists(os.environ[env]):
            ff("-i", os.environ[env], os.path.join(A, "img", name))


if __name__ == "__main__":
    w = sys.argv[1:] or ["main", "broll"]
    if "main" in w: main()
    if "broll" in w: broll()
