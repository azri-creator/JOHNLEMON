# Mix: VO (gain only) + supplied kids-story song (0.75x, low-passed, ~20 dB under the voice, ducked)
# + soft synthesized whiteboard SFX: marker scribble under every pen stroke, pops, paper swish on board pushes.
import numpy as np, wave, os, subprocess, json
P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = f"{P}/hf/assets"; SR = 48000; DUR = 61.8; N = int(SR * DUR)
def load(p):
    w = wave.open(p); x = np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, 2).astype(np.float32) / 32768
    assert w.getframerate() == SR; return x
def db(v): return 10 ** (v / 20)
vo = np.zeros((N, 2), np.float32); v = load(f"{A}/vo_src.wav")[:N]; vo[:len(v)] = v
vo *= db(6.0)
song = load(f"{A}/song_src.wav")[:N]; song = np.pad(song, ((0, N - len(song)), (0, 0)))
fi = int(1.2 * SR); song[:fi] *= np.linspace(0, 1, fi)[:, None]
mono = np.abs(vo.mean(1)); hop = SR // 100
env = np.array([mono[i:i + hop].max() for i in range(0, N, hop)])
act = (env > db(-36)).astype(float)
act = np.clip(np.convolve(act, np.ones(30) / 30, "same") * 1.6, 0, 1)
act = np.repeat(act, hop)[:N]
song *= (db(-22.0) * (1 - act * (1 - db(-4))))[:, None]

rng = np.random.default_rng(7)
sfx = np.zeros((N, 2), np.float32)
def place(sig, t, g, pan=0.0):
    i = int(t * SR)
    if i >= N: return
    sig = sig[:N - i] * db(g)
    sfx[i:i + len(sig), 0] += sig * (1 - pan); sfx[i:i + len(sig), 1] += sig * (1 + pan)
def bandnoise(n, lo, hi):
    X = np.fft.rfft(rng.normal(0, 1, n)); f = np.fft.rfftfreq(n, 1 / SR)
    X[(f < lo) | (f > hi)] = 0; y = np.fft.irfft(X, n); return y / (np.abs(y).max() + 1e-9)
def scribble(d, kind):
    n = int(d * SR); t = np.arange(n) / SR
    y = bandnoise(n, 1800, 6500) * 0.7 + bandnoise(n, 500, 1500) * 0.3
    rate = rng.uniform(8, 11) if kind != "draw" else rng.uniform(3, 5)
    am = 0.45 + 0.55 * np.abs(np.sin(np.pi * rate * t + rng.uniform(0, 3)))
    e = np.minimum(1, np.minimum(t / 0.03, (d - t) / 0.05).clip(0))
    return (y * am * e).astype(np.float32)
def popsnd():
    n = int(0.09 * SR); t = np.arange(n) / SR; f = rng.uniform(480, 620)
    y = np.sin(2 * np.pi * (f * t + 2600 * t * t)) * np.exp(-t / 0.025); return (y / np.abs(y).max()).astype(np.float32)
def swish(d=0.4):
    n = int(d * SR); t = np.arange(n) / SR; y = bandnoise(n, 300, 2600)
    e = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 2; return (y * e).astype(np.float32)

ev = json.load(open(f"{P}/scripts/events.json"))
for t0, t1, k in ev["pen"]: place(scribble(t1 - t0, k), t0, -33 if k != "draw" else -35, 0.25)
for t in ev["pop"]: place(popsnd(), t, -35, rng.uniform(-0.3, 0.3))
for t in ev["push"]: place(swish(0.6), t, -38, -0.2); place(scribble(0.55, "draw"), t + 0.03, -37, 0.25)

mix = vo + song + sfx
c = db(-1.0); k = c * 0.7
mix = np.where(np.abs(mix) > k, np.sign(mix) * (k + (c - k) * np.tanh((np.abs(mix) - k) / (c - k))), mix)
fo = int(1.0 * SR); mix[-fo:] *= np.linspace(1, 0, fo)[:, None]
def wr(p, x):
    w = wave.open(p, "w"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes()); w.close()
os.makedirs(f"{P}/stems", exist_ok=True)
wr(f"{A}/mix.wav", mix); wr(f"{P}/stems/song_bed.wav", song); wr(f"{P}/stems/sfx.wav", sfx); wr(f"{P}/stems/voice.wav", vo)
for name in ("hf/assets/mix.wav", "stems/voice.wav", "stems/song_bed.wav", "stems/sfx.wav"):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", f"{P}/{name}", "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
    print(name, [l.strip() for l in r.splitlines() if l.strip().startswith(("I:", "Peak:"))][-2:])
