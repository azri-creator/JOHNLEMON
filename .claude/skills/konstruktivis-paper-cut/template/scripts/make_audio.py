# Mix: original voice (untouched apart from gain + soft limit) + supplied song, low and ducked
# under the voice, + soft synthesized paper whooshes / stamps at the scene handoffs.
# Song offset puts its drop (40.08 s in the song) on the door opening at 18.33 s,
# so the song's own ending lands on the CTA instead of a fade.
import numpy as np, wave, os, subprocess, json
P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = f"{P}/hf/assets"; SR = 48000; DUR = 57.0; N = int(SR * DUR)

def load(p):
    w = wave.open(p); x = np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, 2).astype(np.float32) / 32768
    assert w.getframerate() == SR; return x

def db(v): return 10 ** (v / 20)

vo = np.zeros((N, 2), np.float32); v = load(f"{A}/vo_src.wav")[:N]; vo[: len(v)] = v
song_all = load(f"{A}/song_src.wav")
OFF = 40.08 - 18.33
song = song_all[int(OFF * SR): int(OFF * SR) + N]
song = np.pad(song, ((0, N - len(song)), (0, 0)))
fi = int(0.5 * SR); song[:fi] *= np.linspace(0, 1, fi)[:, None]

# voice-activity envelope (smoothed) for ducking
mono = np.abs(vo.mean(1)); hop = SR // 100
env = np.array([mono[i:i + hop].max() for i in range(0, N, hop)])
act = (env > db(-38)).astype(float)
k = np.ones(25) / 25; act = np.clip(np.convolve(act, k, "same") * 1.6, 0, 1)
act = np.repeat(act, hop)[:N]
song *= (db(-18.5) * (1 - act * (1 - db(-5))))[:, None]   # bed ≈ -29 LUFS, -5 dB more under speech

# SFX
rng = np.random.default_rng(3)
sfx = np.zeros((N, 2), np.float32)
def place(sig, t, g, pan=0.0):
    i = int(t * SR); sig = sig[: N - i] * db(g)
    sfx[i:i + len(sig), 0] += sig * (1 - pan) ; sfx[i:i + len(sig), 1] += sig * (1 + pan)
def whoosh(d=0.5, f0=400, f1=2400):
    n = int(d * SR); t = np.arange(n) / SR; x = rng.normal(0, 1, n)
    f = f0 * (f1 / f0) ** (t / d); y = np.zeros(n); lp = 0; bp = 0
    for i in range(n):   # simple resonant sweep (state-variable filter)
        c = 2 * np.sin(np.pi * f[i] / SR); lp += c * bp; hp = x[i] - lp - 0.35 * bp; bp += c * hp; y[i] = bp
    e = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 2
    return (y * e / (np.abs(y).max() + 1e-9)).astype(np.float32)
def thock(f=150):
    n = int(0.22 * SR); t = np.arange(n) / SR
    y = np.sin(2 * np.pi * (f * t - 35 * t * t)) * np.exp(-t / 0.05) + rng.normal(0, 1, n) * np.exp(-t / 0.006) * 0.4
    return (y / np.abs(y).max()).astype(np.float32)
def tick():
    n = int(0.05 * SR); t = np.arange(n) / SR
    y = np.sin(2 * np.pi * 1800 * t) * np.exp(-t / 0.008); return (y / np.abs(y).max()).astype(np.float32)

for t, d in [(5.95, 0.5), (8.7, 0.45), (13.75, 0.5), (18.0, 0.6), (22.6, 0.5), (31.05, 0.45), (35.55, 0.5), (39.95, 0.45), (44.8, 0.45), (49.6, 0.45), (52.55, 0.5), (54.4, 0.6)]:
    place(whoosh(d), t, -27, rng.uniform(-0.3, 0.3))
for t in [51.2, 51.87, 52.31]: place(thock(), t - 0.02, -22)
for t in [23.66, 24.03, 24.91, 25.63, 26.49]: place(tick(), t, -31, 0.2)       # landings on the stairs
for t in [39.05, 53.8]: place(thock(220), t, -25)                            # taps
for t in [10.96, 11.27, 12.5, 26.86, 27.27, 30.71, 30.96, 43.18, 44.22]: place(thock(260), t, -30, rng.uniform(-0.4, 0.4))

mix = vo * db(2.0) + song + sfx
# soft limiter (tanh above -3 dBFS knee), ceiling -1 dBFS
c = db(-1.0); mix = np.where(np.abs(mix) > c * 0.7, np.sign(mix) * (c * 0.7 + (c * 0.3) * np.tanh((np.abs(mix) - c * 0.7) / (c * 0.3))), mix)
fo = int(0.6 * SR); mix[-fo:] *= np.linspace(1, 0, fo)[:, None]

def wr(p, x):
    w = wave.open(p, "w"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes()); w.close()
os.makedirs(f"{P}/stems", exist_ok=True)
wr(f"{A}/mix.wav", mix); wr(f"{P}/stems/song_bed.wav", song); wr(f"{P}/stems/sfx.wav", sfx)
r = subprocess.run(["ffmpeg", "-hide_banner", "-i", f"{A}/mix.wav", "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
print([l.strip() for l in r.splitlines() if l.strip().startswith(("I:", "Peak:", "LRA:"))][-3:])
r = subprocess.run(["ffmpeg", "-hide_banner", "-i", f"{P}/stems/song_bed.wav", "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
print("bed", [l.strip() for l in r.splitlines() if l.strip().startswith("I:")][-1:])
