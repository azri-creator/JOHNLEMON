"""Lay soft SFX events over the voice + music bed.
Usage: python3 -I mix_sfx.py <bed.wav 48k> <sfx_dir> <events.json> <out.wav>

events.json: [["lift", 5.6, 0.55], ["pop", 5.95, 0.35], ["jet", 21.3, 0.32], ["zoom", 23.65, 0.45], ...]
  name = a wav in sfx_dir (from media.sh sfx), time in s, linear gain.
  Typical: lift 0.55 on every lift, pop 0.35 on every title/pin, jet 0.32 under the flight, zoom 0.45 on the map zoom.
"""
import sys, wave, array, json

BED, SFX, EVF, OUT = sys.argv[1:5]
EV = json.load(open(EVF))


def rd(p):
    w = wave.open(p); assert w.getframerate() == 48000 and w.getsampwidth() == 2, p
    a = array.array('h', w.readframes(w.getnframes())); ch = w.getnchannels()
    return [a[i::ch] for i in range(ch)] if ch == 2 else [a, a]


L, R = [array.array('f', c) for c in rd(BED)]
for name, t, g in EV:
    s = rd(f"{SFX}/{name}.wav"); o = int(t * 48000)
    for i in range(min(len(s[0]), len(L) - o)):
        L[o + i] += s[0][i] * g; R[o + i] += s[1][i] * g
pk = max(max(abs(x) for x in L), max(abs(x) for x in R))
k = min(1.0, 29000 / pk)
out = array.array('h', [0]) * (2 * len(L))
out[0::2] = array.array('h', (int(x * k) for x in L)); out[1::2] = array.array('h', (int(x * k) for x in R))
w = wave.open(OUT, 'w'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(48000); w.writeframes(out.tobytes()); w.close()
print("peak scale", round(k, 3))
