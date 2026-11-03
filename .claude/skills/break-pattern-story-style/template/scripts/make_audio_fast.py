"""VGC Break Pattern ad (FAST cut): audio mix. Music = the supplied track "the gonk" (subtle, ducked under the voice); SFX re-timed with the VO time-map.
VO (edited, untouched) + original low/slow synthesised bed (84 BPM, A minor -> C major, low-passed) + sparse SFX + case-study original audio inside the demo gap only.
100 % code (numpy/scipy), no samples. Voice stays on top: music/SFX are ducked by the voice envelope. Output: hf/assets/audio/mix.wav (+ stems)."""
import json, subprocess, os, sys
import numpy as np, scipy.io.wavfile as wav, scipy.signal as sg

SR = 48000
import math
RM = json.load(open("audio/retime_map.json"))
DUR = math.ceil(RM["new_total"] * 30) / 30
def TM(t): return float(np.interp(t, RM["xs"], RM["ys"]))      # master (62.26 s) time -> fast-cut time
N = int(DUR * SR)
rng = np.random.default_rng(2610)

def T(n): return np.arange(n) / SR
def midi(m): return 440.0 * 2 ** ((m - 69) / 12)
def lp(x, fc, o=2): return sg.sosfilt(sg.butter(o, fc / (SR / 2), "low", output="sos"), x, axis=0)
def hp(x, fc, o=2): return sg.sosfilt(sg.butter(o, fc / (SR / 2), "high", output="sos"), x, axis=0)
def bp(x, a, b, o=2): return sg.sosfilt(sg.butter(o, [a / (SR / 2), min(b, SR / 2 * .95) / (SR / 2)], "band", output="sos"), x, axis=0)
def st(x, pan=0.0):
    a = (pan + 1) * np.pi / 4
    return np.stack([x * np.cos(a), x * np.sin(a)], 1).astype(np.float32)
def place(buf, sig, t, g=1.0):
    i = int(round(t * SR))
    if i >= len(buf): return
    j = min(len(buf), i + len(sig))
    if i < 0: sig = sig[-i:]; i = 0
    buf[i:j] += sig[: j - i] * g
def fade(x, a=0.01, r=0.01):
    n = len(x); y = x.copy()
    ia, ir = int(a * SR), int(r * SR)
    if ia: y[:ia] *= np.linspace(0, 1, ia)[:, None] if y.ndim == 2 else np.linspace(0, 1, ia)
    if ir: y[-ir:] *= np.linspace(1, 0, ir)[:, None] if y.ndim == 2 else np.linspace(1, 0, ir)
    return y
def reverb(x, rt=1.6, wet=0.25, seed=1):
    r = np.random.default_rng(seed); n = int(rt * SR); tt = T(n)
    ir = r.standard_normal((n, 2)) * np.exp(-tt * (6.9 / rt))[:, None]
    ir = lp(ir, 4500); ir[: int(0.012 * SR)] *= 0
    out = np.stack([sg.fftconvolve(x[:, c], ir[:, c])[: len(x)] for c in range(2)], 1)
    return (x + wet * out / (np.abs(out).max() + 1e-9) * np.abs(x).max()).astype(np.float32)

# ------------------------------------------------------------------ instruments (all soft; this is a bed, not a lead)
def pad(notes, dur, a=0.5, r=0.7):
    n = int(dur * SR); tt = T(n); out = np.zeros(n)
    for k, m in enumerate(notes):
        f = midi(m)
        for d in (-0.07, 0.07):
            out += np.sin(2 * np.pi * f * (1 + d * 0.01) * tt + k) + 0.25 * np.sin(2 * np.pi * 2 * f * tt)
    env = np.minimum(1, tt / a) * np.minimum(1, np.maximum(0, (dur - tt)) / r)
    return lp(out * env / (len(notes) * 2.0), 1800)
def pluck(m, dur=0.9):
    n = int(dur * SR); tt = T(n); f = midi(m)
    x = np.sin(2 * np.pi * f * tt) * np.exp(-tt * 4.2) + 0.35 * np.sin(2 * np.pi * 2 * f * tt) * np.exp(-tt * 9) + 0.12 * np.sin(2 * np.pi * 3.01 * f * tt) * np.exp(-tt * 14)
    x += hp(rng.standard_normal(n), 3000) * np.exp(-tt * 120) * 0.05
    return x * np.minimum(1, tt / 0.003)
def bell(m, dur=1.6):
    n = int(dur * SR); tt = T(n); f = midi(m)
    x = np.sin(2 * np.pi * f * tt) + 0.5 * np.sin(2 * np.pi * 2.76 * f * tt) * np.exp(-tt * 3) + 0.25 * np.sin(2 * np.pi * 5.4 * f * tt) * np.exp(-tt * 6)
    return x * np.exp(-tt * 2.2) * np.minimum(1, tt / 0.002)
def bass(m, dur=0.6):
    n = int(dur * SR); tt = T(n); f = midi(m)
    x = np.tanh(1.4 * np.sin(2 * np.pi * f * tt)) * np.exp(-tt * 2.2)
    return x * np.minimum(1, tt / 0.01)
def kick():
    n = int(0.34 * SR); tt = T(n); f = 44 + 70 * np.exp(-tt * 28)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 9)
def brush(n_ms=60):
    n = int(n_ms / 1000 * SR); tt = T(n)
    return bp(rng.standard_normal(n), 4500, 9500) * np.exp(-tt * 70)

# ------------------------------------------------------------------ music (84 BPM, bar = 2.857 s)
BPM = 84.0; BEAT = 60 / BPM; BAR = 4 * BEAT
MIN = [(33, [57, 60, 64]), (29, [53, 57, 60]), (36, [55, 60, 64]), (31, [55, 59, 62])]       # Am F C G (bass root, upper triad)
MAJ = [(36, [55, 60, 64]), (31, [55, 59, 62]), (33, [57, 60, 64]), (29, [53, 57, 60])]       # C G Am F
M = {k: np.zeros((N, 2), np.float32) for k in ("pad", "pl", "bs", "dr", "fx")}

def section(t0, t1, prog, padg=0.5, pl=0.0, plstep=2, bs=0.0, kk=0.0, hat=0.0, off=0):
    """a section re-anchors the beat at t0; pads are released with a 0.45 s tail so joins are click-free"""
    nb = int(np.ceil((t1 - t0) / BAR))
    for b in range(nb):
        bt = t0 + b * BAR
        if bt >= t1 - 0.05: break
        root, tri = prog[(b + off) % 4]
        d = min(BAR, t1 - bt) + 0.45
        if padg: place(M["pad"], st(pad(tri + [tri[0] + 12], d), 0), bt, padg)
        for s in range(8):
            tt = bt + s * BEAT / 2
            if tt >= t1 - 0.02: break
            if pl and s % plstep == 0:
                seq = [tri[0] + 12, tri[2], tri[1] + 12, tri[2] + 12, tri[0] + 24, tri[2], tri[1] + 12, tri[2]]
                place(M["pl"], st(pluck(seq[s]), -0.35 if (s // plstep) % 2 else 0.35), tt, pl)
            if bs and s in (0, 3, 4, 7 if bs > 0.7 else 99):
                place(M["bs"], st(bass(root + (12 if s == 7 else 0), BEAT * 1.2), 0), tt, bs)
            if kk and s in (0, 4): place(M["dr"], st(kick(), 0), tt, kk)
            if hat and s % 2 == 1: place(M["dr"], st(brush(), 0.4 if s % 4 == 1 else -0.4), tt, hat)

def music():
    section(0.0, 5.8, MIN, padg=0.45, pl=0.34, plstep=2, bs=0.0, hat=0.0)
    section(5.8, 13.9, MIN, padg=0.5, pl=0.42, plstep=1, bs=0.55, hat=0.55)
    # tension riser 11.2 -> 13.85
    n = int(2.65 * SR); tt = T(n); ns = bp(rng.standard_normal(n), 400, 5000) * (tt / 2.65) ** 2.2
    place(M["fx"], st(ns * 0.5, 0), 11.2)
    # 13.9 – 16.9: music drops out (pad tail only), a lone sub drone under "3 JAM"
    place(M["pad"], st(pad([45, 52], 2.8, a=0.2, r=1.2), 0), 15.2, 0.5)
    # 16.9 – 21.0: tired, lone minor pad + one slow note per bar
    section(16.9, 21.0, MIN, padg=0.55, pl=0.0, bs=0.0)
    for k, (tt_, m) in enumerate([(17.5, 69), (19.0, 65)]): place(M["pl"], st(pluck(m, 1.6), -0.2), tt_, 0.34)
    # 21.0 – 23.65: lift. riser, then major
    n = int(2.6 * SR); tt = T(n); ns = bp(rng.standard_normal(n), 300, 6000) * (tt / 2.6) ** 1.6
    place(M["fx"], st(ns * 0.35, 0), 21.0)
    section(21.2, 23.65, MAJ, padg=0.45, pl=0.3, plstep=2, bs=0.5, kk=0.0, hat=0.0)
    section(23.65, 32.5, MAJ, padg=0.5, pl=0.42, plstep=1, bs=0.7, kk=0.5, hat=0.3)
    # 32.5 – 33.5 playful, 33.5 – 34.33 lullaby (music box), 34.33 resolve
    section(32.5, 33.52, MAJ, padg=0.0, pl=0.42, plstep=1, bs=0.0, hat=0.3, off=2)
    for k, m in enumerate([84, 79, 76, 72]): place(M["pl"], st(bell(m, 1.2), 0.15), 33.55 + k * 0.2, 0.34)
    section(34.33, 35.45, MAJ, padg=0.55, pl=0.0, bs=0.6, kk=0.55)
    for m in (72, 76, 79, 84): place(M["pl"], st(bell(m, 1.6), 0.0), 34.36 + (m - 72) * 0.012, 0.28)
    # 35.45 – 46.95: demo, pad only (the proof gets the room)
    section(35.45, 46.95, MAJ, padg=0.4, pl=0.0, bs=0.0)
    for k, tt_ in enumerate([36.4, 38.4, 40.4]): place(M["pl"], st(pluck([76, 72, 79][k], 1.4), 0.2), tt_, 0.2)
    # 46.95 – 55.6: groove returns and climbs
    section(46.95, 51.1, MAJ, padg=0.5, pl=0.44, plstep=1, bs=0.7, kk=0.5, hat=0.3, off=2)
    section(51.1, 55.6, MAJ, padg=0.55, pl=0.5, plstep=1, bs=0.75, kk=0.55, hat=0.35, off=0)
    # step-hops: rising notes (C major pentatonic)
    for tt_, m in [(51.25, 67), (52.2, 72), (52.98, 76), (54.1, 79), (54.28, 84)]: place(M["pl"], st(pluck(m, 1.0), 0.0), tt_, 0.4)
    # 55.6 – end: CTA, then a resolved last chord that rings out
    section(55.6, 59.65, MAJ, padg=0.55, pl=0.46, plstep=1, bs=0.75, kk=0.55, hat=0.35, off=1)
    place(M["pad"], st(pad([48, 55, 60, 64, 67, 72], 4.0, a=0.15, r=2.2), 0), 59.65, 0.65)
    for k, m in enumerate([84, 88, 91]): place(M["pl"], st(bell(m, 2.2), -0.3 + 0.3 * k), 59.7 + k * 0.06, 0.28)
    # bus shaping
    for k in M: M[k] = reverb(M[k], 1.8, 0.28, 3) if k in ("pad", "pl") else M[k]

# ------------------------------------------------------------------ SFX (kept sparse: pops for pieces, slams for punchlines, whoosh only on cuts)
def pop(f=620, d=0.11):
    n = int(d * SR); tt = T(n); fr = f * (1.6 - 0.6 * np.minimum(1, tt / 0.05))
    return np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-tt * 30) * np.minimum(1, tt / 0.002)
def tick(f=3200, d=0.025):
    n = int(d * SR); tt = T(n); return bp(rng.standard_normal(n), f * 0.7, f * 1.5) * np.exp(-tt * 160)
def slam(f=88, d=0.42):
    n = int(d * SR); tt = T(n); fr = f * (1 + 1.3 * np.exp(-tt * 25))
    body = np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-tt * 9)
    out = np.tanh(1.5 * body) * 0.9; k = tick(2400, 0.03); out[: len(k)] += k * 0.35
    return out
def whoosh(d=0.42, up=True):
    n = int(d * SR); tt = T(n); w = rng.standard_normal(n)
    bands = [(400, 900), (900, 2000), (2000, 4200), (4200, 8000)]
    out = np.zeros(n); pos = tt / d
    for k, (lo, hi) in enumerate(bands):
        c = (k + 0.5) / len(bands); c = c if up else 1 - c
        out += bp(w, lo, hi) * np.exp(-((pos - c) ** 2) / (2 * 0.22 ** 2))
    return out * np.sin(np.pi * np.clip(pos, 0, 1)) ** 1.5 * 1.4
def boom():
    n = int(1.6 * SR); tt = T(n); fr = 70 * np.exp(-tt * 1.8) + 28
    return np.tanh(1.7 * np.sin(2 * np.pi * np.cumsum(fr) / SR)) * np.exp(-tt * 2.2) + lp(rng.standard_normal(n), 600) * np.exp(-tt * 5) * 0.4
def snip():
    return np.concatenate([tick(7000, 0.02), np.zeros(int(0.015 * SR)), tick(5200, 0.025)])
def flipc():
    n = int(0.05 * SR); tt = T(n); return bp(rng.standard_normal(n), 900, 3500) * np.exp(-tt * 55)
def buzz():
    n = int(0.3 * SR); tt = T(n); return np.sign(np.sin(2 * np.pi * 110 * tt)) * 0.4 * (0.6 + 0.4 * np.sin(2 * np.pi * 28 * tt)) * np.exp(-tt * 6)
def ding(m=84):
    return bell(m, 1.4) * 0.8
def mclick():
    return np.concatenate([tick(2600, 0.012), np.zeros(int(0.03 * SR)), tick(1500, 0.016)])
def rise(d=1.0):
    n = int(d * SR); tt = T(n); f = 300 + 1500 * (tt / d) ** 2
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * (tt / d) ** 1.4 * 0.4

S = np.zeros((N, 2), np.float32)
def sfx(t, sig, g=0.5, pan=0.0): place(S, st(sig, pan), TM(t), g)

def build_sfx():
    # S1
    sfx(0.02, pop(520), 0.35); sfx(1.22, whoosh(0.3), 0.2); sfx(1.26, pop(700), 0.4)
    for k, tt in enumerate((1.55, 1.7, 1.85, 2.0)): sfx(tt, tick(3600 + 200 * k), 0.4)
    for tt in (2.36, 2.66, 3.05): sfx(tt, pop(480 + (tt - 2.36) * 150), 0.5); sfx(tt, whoosh(0.28), 0.14)
    sfx(3.3, whoosh(0.3, False), 0.14); sfx(3.62, slam(70), 0.55); sfx(3.78, slam(96), 0.7)
    for k in range(5): sfx(4.0 + k * 0.16, flipc(), 0.42, -0.2 + 0.1 * k)
    sfx(4.05, whoosh(0.4, False), 0.16); sfx(4.42, slam(80), 0.8)
    # S2 / S3
    sfx(5.8, whoosh(0.18), 0.22); sfx(6.05, pop(560), 0.5)
    for k in range(4): sfx(6.2 + k * 0.05, tick(3000), 0.3)
    for k in range(7): sfx(6.3 + k * 0.1, tick(2200 + 150 * k, 0.012), 0.2)
    for k in range(3): sfx(7.0 + k * 0.08, snip(), 0.5)
    sfx(7.3, pop(640), 0.5)
    for k in range(3): sfx(7.62 + 0.12 * k, tick(2800 + 300 * k), 0.4)
    sfx(8.4, pop(500), 0.5)
    for k in range(4): sfx(8.6 + 0.08 * k, pop(760 + 70 * k, 0.07), 0.3)
    sfx(8.9, whoosh(0.25), 0.12); sfx(9.46, pop(590), 0.5)
    for k in range(4): sfx(9.85 + 0.07 * k, pop(820 + 60 * k, 0.06), 0.28)
    sfx(10.15, slam(120, 0.25), 0.45); sfx(11.0, slam(150, 0.22), 0.5)
    sfx(11.3, pop(540), 0.5); sfx(12.3, pop(480), 0.5)
    for k in range(6): sfx(13.2 + k * 0.1, tick(900, 0.03), 0.25)
    # S4
    sfx(13.9, boom(), 0.38)
    for k in range(18):                                       # clock spinning: accelerating ticks
        tt = 14.3 + 0.95 * (k / 18) ** 0.8
        sfx(tt, tick(4200 if k % 2 else 3000, 0.018), 0.35)
    sfx(14.24, pop(660), 0.45); sfx(14.3, rise(1.0), 0.22)
    sfx(15.28, boom(), 0.7); sfx(15.28, slam(60, 0.5), 0.5); sfx(15.57, slam(80, 0.4), 0.7)
    sfx(15.76, tick(2400), 0.4); sfx(16.12, pop(440), 0.5)
    # S5
    sfx(17.36, pop(330), 0.4); sfx(18.05, buzz(), 0.35)
    sfx(18.8, pop(300), 0.35); sfx(19.5, slam(55, 0.5), 0.7); sfx(19.5, whoosh(0.4, False), 0.1)
    # S6a
    sfx(20.82, whoosh(0.4), 0.3); sfx(21.12, pop(500), 0.3); sfx(21.46, tick(2600), 0.4)
    for k, tt in enumerate((21.93, 22.33, 22.75)): sfx(tt, slam(80 + 18 * k, 0.4), 0.7)
    sfx(23.3, whoosh(0.3, False), 0.22)
    # S6b
    sfx(23.65, boom(), 0.3); sfx(23.67, ding(88), 0.34); sfx(23.9, bell(95, 1.2), 0.18)
    sfx(24.7, whoosh(0.5, False), 0.18); sfx(25.5, slam(90, 0.4), 0.6)
    for tt in (26.95, 27.86, 28.38): sfx(tt, pop(520 + (tt - 26.95) * 60), 0.5)
    sfx(29.95, pop(780), 0.5); sfx(31.1, pop(880), 0.5)
    sfx(31.22, pop(560), 0.45); sfx(31.4, pop(620), 0.45); sfx(31.55, whoosh(0.3), 0.14)
    # S7
    sfx(32.53, slam(85, 0.35), 0.6); sfx(32.86, slam(100, 0.35), 0.6)
    for i in range(5): sfx(32.6 + i * 0.16, whoosh(0.3), 0.1); sfx(32.94 + i * 0.16, pop(380 + 60 * i, 0.09), 0.4)
    for k in range(3): sfx(33.7 + k * 0.12, pop(300 - 30 * k, 0.16), 0.32)
    sfx(33.74, slam(70, 0.3), 0.4)
    sfx(34.33, whoosh(0.15), 0.15); sfx(34.35, ding(84), 0.4); sfx(34.62, slam(95, 0.4), 0.5)
    sfx(34.5, rise(0.45), 0.18)
    # S8 (the case study keeps its own audio inside the demo gap)
    sfx(35.55, whoosh(0.45), 0.2); sfx(35.8, pop(540, 0.1), 0.35); sfx(36.09, tick(2600), 0.4); sfx(36.79, slam(90, 0.4), 0.6)
    for tt in (38.94, 39.35, 39.65): sfx(tt, slam(75, 0.3), 0.5)
    sfx(40.95, whoosh(0.35, False), 0.15)
    # S9
    sfx(47.3, slam(90, 0.35), 0.5)
    for tt in (47.58, 48.84, 49.55): sfx(tt, slam(80, 0.3), 0.55); sfx(tt + 0.04, whoosh(0.35), 0.12)
    # S10
    sfx(51.1, pop(420), 0.4); sfx(51.2, pop(500), 0.4); sfx(52.14, slam(80, 0.3), 0.6)
    sfx(52.35, pop(460), 0.4); sfx(52.62, whoosh(0.2), 0.1); sfx(52.98, slam(60, 0.3), 0.5)
    sfx(53.17, slam(88, 0.3), 0.6); sfx(53.5, pop(500), 0.4)
    sfx(53.9, whoosh(0.2), 0.1); sfx(54.26, slam(55, 0.35), 0.4); sfx(54.28, slam(100, 0.4), 0.5)
    for k in range(10): sfx(54.3 + 0.02 * k, tick(5000 + 500 * k, 0.02), 0.3, -0.6 + 0.12 * k)
    sfx(54.3, ding(91), 0.5)
    # S11
    sfx(55.86, tick(2600), 0.4); sfx(56.02, slam(88, 0.35), 0.6)
    for k in range(12): sfx(56.34 + 0.08 * k, pop(520 + 55 * k, 0.07), 0.25)
    sfx(56.66, slam(95, 0.35), 0.6); sfx(57.62, whoosh(0.3, False), 0.18)
    sfx(57.78, pop(520), 0.45); sfx(58.1, slam(90, 0.35), 0.6); sfx(58.2, pop(600), 0.45)
    sfx(58.82, mclick(), 0.7)
    sfx(58.89, slam(85, 0.3), 0.4); sfx(59.2, slam(100, 0.4), 0.5)

# ------------------------------------------------------------------ mix
vo = wav.read("audio/VO_Break_Pattern_FAST.wav")[1].astype(np.float64) / 2 ** 31
VO = np.zeros(N); VO[: min(N, len(vo))] = vo[:N]

def env_follow(x, a=0.015, r=0.35, win=0.02):
    hop = int(win * SR); n = len(x) // hop
    e = np.sqrt((x[: n * hop].reshape(n, hop) ** 2).mean(1)); o = np.zeros(n); c = 0.0
    ka, kr = np.exp(-win / a), np.exp(-win / r)
    for i, v in enumerate(e): c = ka * c + (1 - ka) * v if v > c else kr * c + (1 - kr) * v; o[i] = c
    return np.interp(np.arange(len(x)) / SR, np.arange(n) * win + win / 2, o)


GONK_DROP = 38.35                    # the big drop in the track (after the 36.5-38.3 s breakdown) ...
T_DROP = TM(23.65)                   # ... lands on the VGC logo reveal
G0 = GONK_DROP - T_DROP


def peak_eq(x, f0, q, gain_db):
    A = 10 ** (gain_db / 40); w0 = 2 * np.pi * f0 / SR; al = np.sin(w0) / (2 * q)
    b = [1 + al * A, -2 * np.cos(w0), 1 - al * A]; a = [1 + al / A, -2 * np.cos(w0), 1 - al / A]
    return sg.lfilter(np.array(b) / a[0], np.array(a) / a[0], x, axis=0)


def main():
    build_sfx()
    # --- case-study original audio (one sentence) at the start of the compressed demo gap
    CS_SRC0, CS_SRC1 = RM["cs_src"]; CS_T0 = RM["demo_new_start"] + RM["cs_pre"]
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(CS_SRC0), "-t", str(CS_SRC1 - CS_SRC0), "-i", "src/casestudy.mp4", "-vn", "-ar", str(SR), "-ac", "2", "audio/cs_clip.wav"], check=True)
    cs = hp(wav.read("audio/cs_clip.wav")[1].astype(np.float64) / 32768, 70)
    csl = np.zeros((N, 2)); place(csl, fade(cs, 0.03, 0.08), CS_T0, 1.0)
    act = np.abs(cs.mean(1)) > 0.02
    csl *= 10 ** (-14.7 / 20) / np.sqrt((cs.mean(1)[act] ** 2).mean()) * 0.9
    # --- music: the supplied track, cut so its drop hits the VGC reveal
    if not os.path.exists("audio/gonk_full.wav"): subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "src/the_gonk.mp4", "-vn", "-ar", str(SR), "-ac", "2", "audio/gonk_full.wav"], check=True)
    g = wav.read("audio/gonk_full.wav")[1].astype(np.float64) / 32768                 # 48 kHz stereo, L/R correlation +0.99 (in phase)
    seg = g[int(G0 * SR): int(G0 * SR) + N]
    if len(seg) < N: seg = np.vstack([seg, np.zeros((N - len(seg), 2))])
    seg = hp(seg, 60, 2)
    seg = peak_eq(seg, 2200, 0.9, -3.0)                                                # leave room for the voice presence band
    tt = np.arange(N) / SR
    seg *= np.clip(tt / 0.9, 0, 1)[:, None] * np.clip((DUR - tt) / 1.4, 0, 1)[:, None]  # fade in 0.9 s, out 1.4 s
    mus = seg
    vo_env = env_follow(VO)
    duck = 1 - 0.55 * np.clip(vo_env / 0.06, 0, 1)
    cs_env = env_follow(csl.mean(1)); duck *= 1 - 0.6 * np.clip(cs_env / 0.05, 0, 1)
    mus = mus * duck[:, None]
    mus = mus * np.interp(tt, [0, T_DROP - 0.2, T_DROP + 0.05, T_DROP + 4.0, T_DROP + 4.9, DUR], [1, 1, 0.6, 0.6, 1, 1])[:, None]   # the drop is ~5 dB hotter than the groove: keep it subtle under 'VGC / korang akan belajar'
    sf = S * (1 - 0.5 * np.clip(vo_env / 0.06, 0, 1))[:, None]
    vact = vo_env > 0.04
    rms_m = np.sqrt((mus[vact] ** 2).mean()); target = 10 ** ((-14.7 - 21.5) / 20)       # "subtle": ~21 dB under the voice while it speaks
    mus *= target / rms_m
    sf *= 0.42
    mix = np.stack([VO, VO], 1) + mus + sf + csl
    pk = np.abs(mix).max()
    wav.write("audio/_mix_pre.wav", SR, np.int32(np.clip(mix / max(pk, 1), -1, 1) * (2 ** 31 - 1)))
    r = subprocess.run(["ffmpeg", "-nostats", "-i", "audio/_mix_pre.wav", "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True)
    I = float([l for l in r.stderr.splitlines() if l.strip().startswith("I:")][-1].split()[1])
    gain = -14.0 - I
    print(f"gonk offset {G0:.2f}s (drop at {T_DROP:.2f}s)  pre-mix {I:.1f} LUFS -> gain {gain:+.1f} dB   total {DUR:.3f}s")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "audio/_mix_pre.wav", "-af", f"volume={gain}dB,alimiter=limit=0.89:level=false", "-ar", str(SR), "-c:a", "pcm_s24le", "audio/mix_fast.wav"], check=True)
    for nm, arr in (("voice", np.stack([VO, VO], 1)), ("music", mus), ("sfx", sf), ("casestudy", csl)):
        wav.write(f"audio/stem_fast_{nm}.wav", SR, np.int32(np.clip(arr, -1, 1) * (2 ** 31 - 1)))
    print("music vs voice (speaking windows) dB:", 20 * np.log10(np.sqrt((mus[vact] ** 2).mean())) + 14.7)


main()
