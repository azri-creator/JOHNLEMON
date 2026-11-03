"""Clean Launch Motion VO, step 2: assemble the chosen line chunks into the timeline VO master.

- Each chunk is only trimmed at its own leading/trailing silence; speech inside a chunk is never cut or padded.
- Pause after each line: plan.gaps.in_scene inside a scene, plan.gaps.scene_change when the next line starts a new scene.
- Clarity chain: HPF 75 Hz, -1.5 dB @220 Hz, +3 dB presence @3.2 kHz, +1.5 dB air, 2.5:1 compression,
  then two-pass EBU R128 to -16 LUFS / -1.5 dBTP.

Writes <project>/<plan.name>_VO.wav, hf/assets/vo.wav and vo/vo_words.json (the timing source: every word gets
id "word#n", start/end seconds, its line and its scene).

usage: /usr/bin/python3 scripts/build_vo.py
"""
import json, os, re, subprocess
import numpy as np
from common import ASSETS, PROJ, WORDS_JSON, ffmpeg, load_plan, script_lines

plan = load_plan()
LINES = os.path.join(PROJ, "vo", "takes", "lines")
FF = ffmpeg()
SR = 48000
G = plan["gaps"]
CLARITY = ("highpass=f=75,equalizer=f=220:t=q:w=1.0:g=-1.5,equalizer=f=3200:t=q:w=1.1:g=3,"
           "treble=g=1.5:f=7000,acompressor=threshold=-22dB:ratio=2.5:attack=8:release=120:makeup=1.5")
sel = json.load(open(os.path.join(LINES, "selection.json"), encoding="utf-8"))["selection"]
scene_of = plan["line_scene"]


def decode(path):
    raw = subprocess.run([FF, "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).astype(np.float64)


def words_from(al):
    out, cur = [], None
    for c, s, e in zip(al["characters"], al["character_start_times_seconds"], al["character_end_times_seconds"]):
        if c.isspace():
            if cur: out.append(cur); cur = None
            continue
        if cur is None: cur = {"w": "", "s": s, "e": e}
        cur["w"] += c; cur["e"] = e
    if cur: out.append(cur)
    return out


hop = int(0.005 * SR)
pieces, words, t = [np.zeros(int(G["lead_in"] * SR))], [], G["lead_in"]
for idx, item in enumerate(sel):
    base = os.path.join(LINES, item["chosen"])
    x = decode(base + ".mp3")
    al = json.load(open(base + ".align.json", encoding="utf-8"))["alignment"]
    db = np.array([20 * np.log10(np.sqrt(np.mean(x[i:i + hop] ** 2)) + 1e-9) for i in range(0, len(x) - hop, hop)])
    voiced = np.where(db > -50)[0]
    a = max(0, voiced[0] * hop - int(0.03 * SR))
    b = min(len(x), (voiced[-1] + 1) * hop + int(0.09 * SR))
    seg = x[a:b].copy()
    fd = int(0.01 * SR); seg[:fd] *= np.linspace(0, 1, fd); seg[-fd:] *= np.linspace(1, 0, fd)
    off = t - a / SR
    for w in words_from(al):
        words.append({"w": w["w"], "s": round(max(t, w["s"] + off), 3), "e": round(min(t + len(seg) / SR, w["e"] + off), 3),
                      "line": item["line"], "scene": scene_of[item["line"] - 1]})
    pieces.append(seg); t += len(seg) / SR
    if idx + 1 < len(sel):
        gap = G["scene_change"] if scene_of[idx + 1] != scene_of[idx] else G["in_scene"]
        pieces.append(np.zeros(int(gap * SR))); t += gap
y = np.concatenate(pieces)

count = {}
for w in words:
    k = re.sub(r"[^a-z0-9?.!…]", "", w["w"].lower())
    count[k] = count.get(k, 0) + 1
    w["id"] = f"{k}#{count[k]}"

aud = ASSETS; os.makedirs(aud, exist_ok=True)
raw = os.path.join(aud, "_vo_raw.wav"); tmp = raw + ".f32"
y.astype(np.float32).tofile(tmp)
subprocess.run([FF, "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", tmp, "-af", CLARITY, "-c:a", "pcm_f32le", raw], check=True)
os.remove(tmp)
meas = subprocess.run([FF, "-hide_banner", "-nostats", "-i", raw, "-af", "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                      capture_output=True, text=True).stderr
m = json.loads(meas[meas.rindex("{"):meas.rindex("}") + 1])
master = os.path.join(PROJ, f"{plan['name']}_VO.wav")
af = (f"loudnorm=I=-16:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:"
      f"measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
subprocess.run([FF, "-v", "error", "-y", "-i", raw, "-af", af, "-ar", str(SR), "-c:a", "pcm_s24le", master], check=True)
os.remove(raw)
subprocess.run([FF, "-v", "error", "-y", "-i", master, "-c", "copy", os.path.join(aud, "vo.wav")], check=True)
json.dump({"source": "lines", "duration": round(len(y) / SR, 3), "words": words},
          open(WORDS_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
script = " ".join(" ".join(l.split()) for l in script_lines(plan))
print(f"VO master {len(y) / SR:.2f}s, {len(words)} words, text==script: {' '.join(w['w'] for w in words) == script} -> {master}")
