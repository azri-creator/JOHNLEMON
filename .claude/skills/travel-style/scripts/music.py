"""Soft original ambient pad in D (slow chord drift) + one bell at the logo reveal.
Usage: python3 -I music.py <out.wav> <duration> <bell_at>"""
import sys, wave, math, array

OUT, DUR, BELL = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
SR = 24000
N = int(DUR * SR)
f = lambda m: 440 * 2 ** ((m - 69) / 12)
# chords (midi), each held CH seconds with long crossfades
CHORDS = [[50, 57, 62, 66, 69], [47, 54, 62, 66, 69], [43, 50, 59, 62, 66], [45, 52, 57, 61, 64], [50, 57, 62, 66, 69]]
CH = DUR / (len(CHORDS) - 0.6)
XF = 3.0
buf = array.array('f', [0.0]) * N
for ci, ch in enumerate(CHORDS):
    t0 = ci * CH - XF / 2
    t1 = t0 + CH + XF
    a, b = max(0, int(t0 * SR)), min(N, int(t1 * SR))
    for m in ch:
        fr = f(m)
        amp = 0.11 if m < 52 else 0.07
        for det in (-0.35, 0.35):
            w = 2 * math.pi * (fr + det) / SR
            ph = (m * 1.7 + det) % 6.28
            for i in range(a, b):
                t = i / SR
                env = min(1.0, (t - t0) / XF, (t1 - t) / XF)
                if env <= 0:
                    continue
                s = math.sin(w * i + ph) + 0.18 * math.sin(2 * w * i + ph)
                buf[i] += amp * env * s
# slow breathing
for i in range(N):
    buf[i] *= 0.82 + 0.18 * math.sin(2 * math.pi * 0.07 * i / SR)
# bell at logo reveal (D5 with inharmonic partials)
bi = int(BELL * SR)
for ratio, amp, dec in ((1.0, 0.30, 2.6), (2.76, 0.12, 1.4), (5.4, 0.05, 0.7), (2.0, 0.10, 2.0)):
    w = 2 * math.pi * f(74) * ratio / SR
    for i in range(bi, min(N, bi + int(4 * SR))):
        t = (i - bi) / SR
        buf[i] += amp * math.exp(-t / dec * 2.2) * min(1, t / 0.004) * math.sin(w * (i - bi))
peak = max(abs(x) for x in buf) or 1
w = wave.open(OUT, 'w'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
w.writeframes(array.array('h', (int(x / peak * 0.8 * 32767) for x in buf)).tobytes())
w.close()
print("ok", N / SR)
