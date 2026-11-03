"""Refine word anchors on the voice energy envelope (Whisper word starts drift 0.2-0.3 s) and write them into
timing.json "T". Input: work/anchors.json = {"name": whisper_start_seconds, ...} on the OUTPUT timeline
(pick the names from work/words.json made by transcribe_words.py). Needs work/audio/voice.wav (make_audio.py) or
VOICE=/path/to.wav.   Usage: /usr/bin/python3 scripts/refine_times.py
Each start moves to the onset after the local envelope minimum (+-0.12 s window), clamped to -0.10..+0.15 s from
Whisper because soft s-/f- onsets read late on RMS."""
import json, os, wave
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEY = json.load(open(os.path.join(ROOT, "work", "anchors.json")))
w = wave.open(os.environ.get("VOICE", os.path.join(ROOT, "work", "audio", "voice.wav")))
sr, n = w.getframerate(), w.getnchannels()
x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32).reshape(-1, n).mean(1) / 32768
h = sr // 100
env = 20 * np.log10(np.sqrt(np.convolve(x ** 2, np.ones(h) / h, "same")[::h]) + 1e-9)  # 10 ms frames
out = {}
for k, t in KEY.items():
    a, b = max(0, int((t - .12) * 100)), int((t + .12) * 100)
    m = a + int(np.argmin(env[a:b]))
    on = m
    while on < min(m + 40, len(env) - 1) and env[on] < max(env[m] + 9, -38): on += 1
    out[k] = round(min(max(on / 100, t - .10), t + .15), 2)
    print(f"{k:14s} whisper {t:6.2f}  onset {out[k]:6.2f}  ({out[k] - t:+.2f})")
p = os.path.join(ROOT, "timing.json"); tm = json.load(open(p)); tm["T"].update(out)
json.dump(tm, open(p, "w"), indent=1, ensure_ascii=False); print("updated", p)
