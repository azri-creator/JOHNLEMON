"""Verify a rendered Clean Launch Motion MP4 against the delivery spec.

Checks: 1080x1920, 30 fps, H.264 + AAC 48 kHz; integrated loudness (target -14 LUFS +-0.5) and true peak (<= -1.3 dBTP);
VO sync (cross-correlation lag of hf/assets/vo.wav against the MP4 audio, target 0 ms); the longest near-silence
inside the speech (< -50 dB in 10 ms windows, target < ~0.35 s).

usage: /usr/bin/python3 scripts/verify.py <video.mp4>
"""
import json, os, re, subprocess, sys
import numpy as np
from common import ASSETS, ffmpeg, load_words

FF = ffmpeg()
FP = os.path.join(os.path.dirname(FF), "ffprobe") if os.path.exists(os.path.join(os.path.dirname(FF), "ffprobe")) else "ffprobe"
video = sys.argv[1]


def probe():
    try:
        out = subprocess.run([FP, "-v", "error", "-show_entries", "stream=codec_type,codec_name,profile,width,height,r_frame_rate,sample_rate,channels,pix_fmt,color_primaries",
                              "-show_entries", "format=duration", "-of", "json", video], capture_output=True, text=True, check=True).stdout
        return json.loads(out)
    except Exception as e:  # ffprobe missing
        return {"error": str(e)}


def pcm(path, sr=8000, dur=None):
    cmd = [FF, "-v", "error", "-i", path, "-ac", "1", "-ar", str(sr)] + (["-t", str(dur)] if dur else []) + ["-f", "f32le", "-"]
    return np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.float32).astype(np.float64)


info = probe()
for s in info.get("streams", []):
    print("stream:", {k: v for k, v in s.items() if k != "index"})
print("duration:", info.get("format", {}).get("duration"))

log = subprocess.run([FF, "-hide_banner", "-nostats", "-i", video, "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
I = re.findall(r"I:\s+(-?[\d.]+) LUFS", log)
TP = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", log)
print(f"loudness: {I[-1] if I else '?'} LUFS integrated (target -14), true peak {TP[-1] if TP else '?'} dBFS (target <= -1.3)")

vo_path = os.path.join(ASSETS, "vo.wav")
if os.path.exists(vo_path):
    a, b = pcm(vo_path, dur=20), pcm(video, dur=20)
    n = min(len(a), len(b))
    a, b = a[:n] - a[:n].mean(), b[:n] - b[:n].mean()
    m = 400  # +-50 ms at 8 kHz
    lags = range(-m, m + 1)
    cc = [np.dot(a[max(0, -l):n - max(0, l)], b[max(0, l):n - max(0, -l)]) for l in lags]
    print(f"VO sync lag: {(np.argmax(cc) - m) / 8:.1f} ms (target 0)")

words = load_words()
x = pcm(video, sr=16000)
hop = 160
db = 20 * np.log10(np.sqrt(np.add.reduceat(x[: len(x) // hop * hop] ** 2, np.arange(0, len(x) // hop * hop, hop)) / hop) + 1e-9)
s0, e0 = int(words[0]["s"] * 100), int(words[-1]["e"] * 100)
run = best = 0
best_at = 0
for i in range(s0, min(e0, len(db))):
    run = run + 1 if db[i] < -50 else 0
    if run > best:
        best, best_at = run, i
print(f"longest near-silence inside speech: {best / 100:.2f}s at {best_at / 100 - best / 100:.2f}s (target < ~0.35)")
