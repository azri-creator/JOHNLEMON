# ===== TEMPLATE NOTE (Astra Styles skill) =====
# This is the exact build of VGC "AI Edit Merapu" (45.3 s). It is a WORKED EXAMPLE, not a generic generator:
# - Config blocks to replace per video: CAM, WOB/CH (chaos beat, optional), TT, SCRIM_L/SCRIM_T, P1/P2/SUBS, CARDS/CARD_H/CA_FWD,
#   FB/FB_AR/RIM, TH/FAN, LY, UI.
# - The timeline list J (further down) has beat times hard-coded for the Merapu script: re-time or delete beats you do not use.
# - Needs hf/build/headtrack.json (scripts/headtrack.py) and the assets listed in references/pipeline.md section 1.
# ==============================================
# Voice + original synthesized beds + unique synthesized SFX for "AI Edit Merapu".
# Run from the project dir:  python3 scripts/audio.py
# Calm bed (slow, low, ~20 dB under voice) everywhere except the chaos beat (4.1–8.42 s),
# which gets a deliberately tacky bouncy loop that dies on a record scratch at "kejap".
import numpy as np, subprocess, wave
from scipy import signal

SR = 48000; DUR = 45.3; n = int(DUR * SR)
CH0, CH1 = 4.1, 8.42

def rd(p):
    w = wave.open(p); ch = w.getnchannels()
    d = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    return d.reshape(-1, ch).mean(1) if ch > 1 else d
def wr(p, x):
    x = np.clip(x, -1, 1)
    if x.ndim == 1: x = np.stack([x, x], 1)
    w = wave.open(p, 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((x * 32767).astype(np.int16).tobytes()); w.close()
def sos(kind, f, order=2): return signal.butter(order, f, kind, fs=SR, output='sos')
def lp(x, f): return signal.sosfilt(sos('low', min(f, SR / 2 - 200)), x)
def hp(x, f): return signal.sosfilt(sos('high', max(20, f)), x)
def bp(x, lo, hi): return signal.sosfilt(sos('band', [max(30, lo), min(SR / 2 - 200, hi)]), x)
def put(buf, x, t0, g=1.0):
    i0 = int(t0 * SR); j = min(len(buf), i0 + len(x))
    if 0 <= i0 < len(buf): buf[i0:j] += g * x[:j - i0]
def env(x, win=.05):
    k = int(win * SR); return np.sqrt(np.convolve(x ** 2, np.ones(k) / k, mode='same') + 1e-12)
def tt(d): return np.arange(int(d * SR)) / SR
def db(v): return 10 ** (v / 20)

voice = rd('hf/build/voice48.wav'); voice = np.pad(voice, (0, max(0, n - len(voice))))[:n] * db(-1.5)
wr('hf/assets/audio/voice.wav', voice)
venv = env(voice); act = venv > db(-40); vo_rms = np.sqrt(np.mean(voice[act] ** 2))
t = np.arange(n) / SR
R = np.random.default_rng(2026)

# ---------------- calm bed: D major-ish 9th pads, 68 BPM, soft pluck ----------------
bed = np.zeros(n)
CH = [(73.42, [293.66, 369.99, 440.0, 659.25]), (61.74, [246.94, 293.66, 369.99, 554.37]),
      (55.0, [220.0, 277.18, 329.63, 493.88]), (65.41, [261.63, 329.63, 392.0, 587.33])]  # D, Bm, A, C(add9) colour
BT = 60 / 68; BAR = 4 * BT
for b in range(int(DUR / BAR) + 2):
    b0 = b * BAR; root, ch = CH[b % 4]; x = tt(BAR + .6)
    pad = sum(np.sin(2 * np.pi * f * d * x + R.uniform(0, 6)) for f in ch for d in (.997, 1.003))
    pad = lp(pad, 1400) * np.minimum(x / 1.2, 1) * np.minimum((BAR + .6 - x) / .8, 1)
    put(bed, pad * .16, b0)
    sub = np.sin(2 * np.pi * root * x) * np.minimum(x / .3, 1) * np.minimum((BAR + .6 - x) / .6, 1)
    put(bed, sub * .22, b0)
    for k, f in enumerate([ch[0] * 2, ch[2] * 2, ch[1] * 2, ch[3]]):
        y = tt(1.4); pl = np.sin(2 * np.pi * f * y) * np.exp(-y * 4.5) + .3 * np.sin(4 * np.pi * f * y) * np.exp(-y * 7)
        put(bed, lp(pl, 3200) * .05, b0 + k * BT + BT * .5)
bed = lp(bed, 3800)

# ---------------- chaos loop: 150 BPM bouncy square lead, cowbell, kick ----------------
cha = np.zeros(n); B2 = 60 / 150
for k in range(int((CH1 - CH0) / (B2 / 2)) + 1):
    t0 = CH0 + k * B2 / 2
    if k % 2 == 0:
        y = tt(.25); kk = np.sin(2 * np.pi * np.cumsum(50 + 120 * np.exp(-y * 30)) / SR) * np.exp(-y * 9); put(cha, kk * .9, t0)
    y = tt(.12); cb = (signal.square(2 * np.pi * 540 * y) + signal.square(2 * np.pi * 800 * y)) * np.exp(-y * 28); put(cha, bp(cb, 400, 4000) * .12, t0 + B2 / 4)
    f = [523.25, 659.25, 783.99, 1046.5, 783.99, 659.25, 880.0, 698.46][k % 8]
    y = tt(B2 / 2); ld = signal.square(2 * np.pi * f * y, .3) * np.exp(-y * 5); put(cha, lp(ld, 5000) * .16, t0)
cha *= np.clip((t - CH0) / .05, 0, 1) * (t < CH1)

# normalise beds against the voice, then duck under speech
def level(x, a, b, under):
    m = (t >= a) & (t < b); r = np.sqrt(np.mean(x[m] ** 2)) + 1e-9
    return x * (vo_rms * db(-under) / r)
bed = level(bed, 0, DUR, 21)
bed *= np.clip(t / 1.5, 0, 1) * np.clip((DUR - t) / 1.5, 0, 1)
bed *= np.where((t > CH0 - .05) & (t < 9.1), 0, 1)                 # bed drops out for the chaos beat
bed *= np.clip((t - 9.1) / 1.2, 0, 1) * (t >= 9.1) + (t < CH0)      # and swells back after "kejap"
cha = level(cha, CH0, CH1, 12)
duck = 1 - .45 * np.clip((env(voice, .12) - db(-36)) / (db(-22) - db(-36)), 0, 1)
music = (bed + cha) * duck
wr('hf/assets/audio/music.wav', music)

# ---------------- SFX (each synthesized fresh; no sample reused) ----------------
sfx = np.zeros(n)
def whoosh(t0, d=.45, lo=300, hi=2600, g=1.0):
    y = tt(d); s = R.uniform(.8, 1.25)
    w = bp(R.standard_normal(len(y)), lo * s, hi * s) * np.sin(np.pi * np.clip(y / d, 0, 1)) ** 2
    put(sfx, w * .07 * g, t0 - d * .55)
def tick(t0, g=1.0):
    y = tt(.03); put(sfx, hp(R.standard_normal(len(y)), R.uniform(2500, 4200)) * np.exp(-y * 260) * .05 * g, t0)
def click(t0):
    y = tt(.09); put(sfx, (np.sin(2 * np.pi * R.uniform(1500, 1900) * y) * np.exp(-y * 70) + .5 * hp(R.standard_normal(len(y)), 3000) * np.exp(-y * 200)) * .12, t0)
def blip(t0, f):
    y = tt(.32); put(sfx, (np.sin(2 * np.pi * f * y) * np.exp(-y * 14) + .6 * np.sin(2 * np.pi * f * 1.5 * y) * np.exp(-np.maximum(y - .07, 0) * 14) * (y > .07)) * .09, t0)
def sparkle(t0):
    for k in range(9):
        f = R.uniform(2400, 5200); y = tt(.4); put(sfx, np.sin(2 * np.pi * f * y) * np.exp(-y * 11) * .025, t0 + k * .035)
# Astra blur-ins: soft airy whooshes, low level
for t0 in [.18, 9.14, 10.32, 12.12, 13.62, 14.4, 18.1, 18.65, 20.45, 21.5, 25.3, 26.24, 28.09, 28.79, 29.78, 30.68,
           31.66, 33.56, 34.35, 37.12, 38.03, 39.03, 39.68, 40.4, 41.48, 42.84, 43.73, 44.5]:
    whoosh(t0, g=R.uniform(.7, 1.0))
whoosh(24.44, .3, 600, 5000, 1.4); whoosh(24.8, .35, 300, 2400, 1.2)
for a, b, m in [(14.62, 17.2, 47), (21.6, 23.3, 23)]:
    for i in range(m): tick(a + (b - a) * i / m, R.uniform(.6, 1.0))
click(17.9); click(23.45)
for t0, f in [(35.08, 880), (35.63, 988), (36.09, 1175)]: blip(t0, f)
sparkle(44.55)
# chaos SFX: cartoon boing, pops, slide whistle, horn, boom
def boing(t0):
    y = tt(.5); f = 180 + 120 * np.sin(2 * np.pi * 9 * y) * np.exp(-y * 4)
    put(sfx, np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-y * 5) * .22, t0)
def pop(t0):
    y = tt(.12); f = 900 * np.exp(-y * 25) + 300; put(sfx, np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-y * 35) * .2, t0)
def whistle(t0, up=True):
    y = tt(.45); f = (600 + 1400 * y / .45) if up else (2000 - 1400 * y / .45)
    put(sfx, np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * y / .45) * .1, t0)
def horn(t0):
    y = tt(.55); x = sum(signal.sawtooth(2 * np.pi * f * y) for f in (349, 440, 523)); put(sfx, lp(x, 2500) * np.minimum(y / .02, 1) * np.exp(-y * 2.5) * .06, t0)
def boom(t0):
    y = tt(.9); put(sfx, (np.sin(2 * np.pi * np.cumsum(40 + 90 * np.exp(-y * 12)) / SR) + .4 * lp(R.standard_normal(len(y)), 900)) * np.exp(-y * 4.5) * .3, t0)
boing(4.14); pop(4.47); horn(5.31); pop(5.64); whistle(5.97); pop(6.46); whistle(6.82, False)
pop(7.1); pop(7.4); pop(7.55); boing(7.7); pop(7.86); boom(8.05)
# record scratch at "kejap"
y = tt(.42); f = 180 + 900 * np.abs(np.sin(2 * np.pi * 3.2 * y))
sc = bp(R.standard_normal(len(y)) * (1 + np.sin(2 * np.pi * np.cumsum(f) / SR)), 300, 3500) * np.exp(-y * 4)
put(sfx, sc * .22, 8.42)
sfx *= 1 - .35 * np.clip((env(voice, .08) - db(-34)) / (db(-20) - db(-34)), 0, 1)
wr('hf/assets/audio/sfx.wav', sfx)
mix = voice + music + sfx
print('voice rms dBFS %.1f | music %.1f | sfx peak %.1f | mix peak %.2f' % (
    20 * np.log10(vo_rms), 20 * np.log10(np.sqrt(np.mean(music ** 2)) + 1e-9), 20 * np.log10(np.abs(sfx).max() + 1e-9), np.abs(mix).max()))
