"""Master audio for a Epic Style ad: cleaned VO + slowed, ducked soundtrack + soft SFX, then the outro's own audio.

Usage: python3 mix.py <audio.json>    (paths relative to the json's folder)
{
  "vo": "work/vo_clean.wav",           "vo_gain_db": 3.9,     # bring the cleaned VO to ~-16 LUFS (measure, then set)
  "main_len": 77.067,                                         # = presenter (TouchUp) length
  "music": "/path/song.mp4",
  "music_parts": [[0, 35.6], [72, 95.7]],  # source seconds: the quiet intro + the breakdown, never the drops
  "tempo": 0.75, "music_db": -10,          # aim: bed ~20 dB under the voice (check with --check)
  "outro": "work/outro.wav", "outro_len": 9.1, "outro_gain_db": -5.3,   # match outro to ~-16 LUFS
  "sfx_dir": "work/sfx",
  "lifts": [3.55, 5.35],                   # every lift transition start (whoosh lands 0.3 s early)
  "pops": [0.35, 3.75],                    # title landings
  "beds": [["wind.wav", 0.0, 0.55], ["hum.wav", 29.2, 0.8], ["ice.wav", 47.15, 1.0]],
  "out": "assets/audio_mix.m4a"
}
Add --check to also write work/bed_check.wav and print the voice-over-music gap (median should be ~20 dB+).
"""
import json
import os
import subprocess
import sys

cfg_path = sys.argv[1]
check = "--check" in sys.argv
os.chdir(os.path.dirname(os.path.abspath(cfg_path)))
c = json.load(open(os.path.basename(cfg_path)))
T, OT = c["main_len"], c["outro_len"]
sfx = c.get("sfx_dir", "work/sfx")
ev = [(f"{sfx}/lift.wav", t - 0.3, 1.0) for t in c.get("lifts", [])] + [(f"{sfx}/pop.wav", t, 0.5) for t in c.get("pops", [])]
ev += [(f"{sfx}/{f}", t, g) for f, t, g in c.get("beds", [])]
ins = ["-i", c["vo"], "-i", c["music"], "-i", c["outro"]]
for f, _, _ in ev:
    ins += ["-i", f]
tempo = c.get("tempo", 0.75)
fc = [f"[0:a]volume={c.get('vo_gain_db', 0)}dB,alimiter=limit=0.84:level=disabled,apad=whole_dur={T},atrim=0:{T},asplit=2[vo][sc]"]
parts = c["music_parts"]
fc.append(f"[1:a]asplit={len(parts)}" + "".join(f"[m{i}]" for i in range(len(parts))))
for i, (a, b) in enumerate(parts):
    fc.append(f"[m{i}]atrim={a}:{b},asetpts=PTS-STARTPTS,atempo={tempo}[p{i}]")
chain = "[p0]"
for i in range(1, len(parts)):
    fc.append(f"{chain}[p{i}]acrossfade=d=1.0:c1=qsin:c2=qsin[x{i}]")
    chain = f"[x{i}]"
fc.append(f"{chain}lowpass=f=3800,equalizer=f=350:t=q:w=0.8:g=-2,volume={c.get('music_db', -10)}dB,apad=whole_dur={T},atrim=0:{T},"
          f"afade=t=in:st=0:d=1.5,afade=t=out:st={T - 1.3}:d=1.3[mus]")
fc.append("[mus][sc]sidechaincompress=threshold=0.05:ratio=3:attack=25:release=450:makeup=1[bed]")
core = list(fc)
sx = []
for i, (f, t, g) in enumerate(ev):
    d = int(max(0, t) * 1000)
    fc.append(f"[{3 + i}:a]volume={g},adelay={d}|{d}[s{i}]")
    sx.append(f"[s{i}]")
if sx:
    fc.append("".join(sx) + f"amix=inputs={len(sx)}:normalize=0,volume=-12dB,apad=whole_dur={T},atrim=0:{T}[sfx]")
    fc.append(f"[vo][bed][sfx]amix=inputs=3:normalize=0,atrim=0:{T}[main]")
else:
    fc.append(f"[vo][bed]amix=inputs=2:normalize=0,atrim=0:{T}[main]")
fc.append(f"[2:a]volume={c.get('outro_gain_db', 0)}dB,atrim=0:{OT},afade=t=in:st=0:d=0.15[out]")
fc.append("[main][out]concat=n=2:v=0:a=1,alimiter=limit=0.89:level=disabled[m]")
subprocess.run(["ffmpeg", "-v", "error", "-y"] + ins + ["-filter_complex", ";".join(fc), "-map", "[m]",
                "-ar", "48000", "-ac", "2", "-c:a", "aac", "-b:a", "224k", c["out"]], check=True)
print("wrote", c["out"])
if check:
    import numpy as np
    subprocess.run(["ffmpeg", "-v", "error", "-y"] + ins[:4] + ["-filter_complex", ";".join(core) + ";[vo]anullsink",
                    "-map", "[bed]", "work/bed_check.wav"], check=True)

    def rd(f):
        r = subprocess.run(["ffmpeg", "-v", "error", "-i", f, "-ac", "1", "-ar", "16000", "-f", "s16le", "-"], capture_output=True).stdout
        return np.frombuffer(r, np.int16).astype(float) / 32768
    v = rd(c["vo"]) * 10 ** (c.get("vo_gain_db", 0) / 20)
    b = rd("work/bed_check.wav")
    n, w = min(len(v), len(b)), 8000
    gaps = []
    for i in range(0, n - w, w):
        vv = 20 * np.log10(np.sqrt(np.mean(v[i:i + w] ** 2)) + 1e-9)
        bb = 20 * np.log10(np.sqrt(np.mean(b[i:i + w] ** 2)) + 1e-9)
        if vv > -40:
            gaps.append(vv - bb)
    print("voice over music dB: median %.1f, min %.1f" % (np.median(gaps), np.min(gaps)))
