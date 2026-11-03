"""Fast-pace pass on the tidied VO: squeeze every silent gap (between lines AND the inner pauses) so the ad runs at a high pace.
Speech and breaths are untouched (no speed change); only true silence (< -38 dBFS, 10 ms RMS) is shortened, inside the silence, with 8 ms crossfades.
The demo gap (case-study sentence) is replaced by exactly the length of the sentence + short margins.
Outputs: audio/VO_Break_Pattern_FAST.wav (+m4a), audio/retime_map.json (old master time -> new time, piecewise-linear; used by the visuals and the SFX)."""
import json, subprocess
import numpy as np, scipy.io.wavfile as wav

SR = 48000
x = wav.read("audio/VO_Break_Pattern_EDITED.wav")[1].astype(np.float64) / 2 ** 31
hop = SR // 100
n = len(x) // hop
env = 20 * np.log10(np.sqrt((x[: n * hop].reshape(n, hop) ** 2).mean(1)) + 1e-9)
sil = env < -38.0

# demo gap = the long run that contains 43 s (old master timeline). Sentence cut from the case study: 24.90 -> 27.46 s (inside true silence dips)
CS_SRC0, CS_SRC1 = 24.90, 27.46
DEMO_PRE, DEMO_POST = 0.20, 0.22
DEMO_LEN = DEMO_PRE + (CS_SRC1 - CS_SRC0) + DEMO_POST

LEAD, TAIL = 0.12, 1.55


def target(d, a, b):
    if a == 0: return LEAD
    if b >= n * 0.01 - 0.02: return TAIL
    if a < 43.0 < b: return DEMO_LEN
    if d >= 1.0: return 0.26
    if d >= 0.5: return 0.20
    if d >= 0.25: return 0.14
    return d                                        # shorter than 250 ms: natural rhythm, keep


runs = []
i = 0
while i < n:
    if sil[i]:
        j = i
        while j < n and sil[j]: j += 1
        if (j - i) >= 20 or i == 0 or j >= n - 2: runs.append((i / 100, j / 100))
        i = j
    else:
        i += 1

# room tone for the demo gap: take a quiet stretch from the middle of the long demo run
demo_run = [r for r in runs if r[0] < 43.0 < r[1]][0]
room = x[int((demo_run[0] + 1.0) * SR):int((demo_run[1] - 1.0) * SR)].copy()


def tone(dur):
    m = int(round(dur * SR))
    reps = int(np.ceil(m / len(room))) + 1
    return np.tile(room, reps)[:m]


XF = int(0.003 * SR)


def xfade(a_, b_):
    """join without changing length (so the time map stays exact): 3 ms fade-out / fade-in, both inside silence"""
    if len(a_) < XF or len(b_) < XF: return np.concatenate([a_, b_])
    a_ = a_.copy(); b_ = b_.copy()
    a_[-XF:] *= np.linspace(1, 0, XF); b_[:XF] *= np.linspace(0, 1, XF)
    return np.concatenate([a_, b_])


out = np.zeros(0)
xs, ys = [0.0], [0.0]
pos = 0.0                                           # old time cursor
new_t = 0.0                                         # new time cursor (nominal, XF overlaps are negligible: 8 ms per join are re-added below)
for (a, b) in runs:
    d = b - a
    nlen = target(d, a, b)
    # speech before this run, copied 1:1
    seg = x[int(pos * SR):int(a * SR)]
    out = xfade(out, seg) if len(out) else seg
    if abs(nlen - d) < 1e-6:
        keep = x[int(a * SR):int(b * SR)]
    elif a < 43.0 < b:
        keep = tone(nlen)
    else:
        k = nlen * 0.5
        keep = np.concatenate([x[int(a * SR):int((a + k) * SR)], x[int((b - (nlen - k)) * SR):int(b * SR)]])
    out = xfade(out, keep)
    xs += [a, b]
    ys += [ys[-1] + (a - pos), ys[-1] + (a - pos) + nlen]
    pos = b
out = xfade(out, x[int(pos * SR):])
# monotonic map: any residual joins (8 ms each) are negligible vs 33 ms frames, but re-measure the true total
total_new = len(out) / SR
xs.append(len(x) / SR); ys.append(ys[-1] + (len(x) / SR - pos))
# gentle tidy: keep peak, no processing beyond the splices
wav.write("audio/VO_Break_Pattern_FAST.wav", SR, np.int32(np.clip(out, -1, 1) * (2 ** 31 - 1)))
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "audio/VO_Break_Pattern_FAST.wav", "-c:a", "aac", "-b:a", "256k", "audio/VO_Break_Pattern_FAST.m4a"], check=True)
json.dump({"xs": xs, "ys": ys, "old_total": len(x) / SR, "new_total": total_new, "demo_old": list(demo_run),
           "demo_new_start": float(np.interp(demo_run[0], xs, ys)), "demo_len": DEMO_LEN, "cs_src": [CS_SRC0, CS_SRC1], "cs_pre": DEMO_PRE},
          open("audio/retime_map.json", "w"), indent=1)
print(f"old {len(x)/SR:.2f}s -> new {total_new:.2f}s  ({len(runs)} silent runs, demo gap {demo_run[1]-demo_run[0]:.2f}s -> {DEMO_LEN:.2f}s)")
for (a, b) in runs:
    print(f"  {a:6.2f}-{b:6.2f} ({b-a:4.2f}s) -> {target(b-a,a,b):4.2f}s")
