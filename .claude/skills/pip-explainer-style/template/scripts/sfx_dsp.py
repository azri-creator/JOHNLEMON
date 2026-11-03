"""Synth DSP + SFX building blocks (from the Glow Keyword Style / Jago Prompt pipeline, re-used)."""
import numpy as np
SR = 48000
rng = np.random.default_rng(29)

# ======================= DSP helpers =======================
def lp1(x, fc):
    fc = np.broadcast_to(np.asarray(fc, dtype=np.float64), x.shape)
    a = np.exp(-2 * np.pi * fc / SR)
    y = np.empty_like(x); acc = 0.0
    for i in range(len(x)):
        acc = (1 - a[i]) * x[i] + a[i] * acc; y[i] = acc
    return y


def lp(x, fc, order=2):
    """one-pole low-pass cascaded; static cut-off uses fast lfilter via numpy recursion trick"""
    if np.ndim(fc) == 0:
        from scipy.signal import lfilter  # noqa
        a = np.exp(-2 * np.pi * fc / SR)
        for _ in range(order): x = lfilter([1 - a], [1, -a], x)
        return x
    for _ in range(order): x = lp1(x, fc)
    return x


def hp(x, fc):
    return x - lp(x, fc, 1)


def place(buf, sig, t, gain=1.0, pan=0.0):
    i = int(round(t * SR))
    if i >= buf.shape[1] or i + len(sig) <= 0: return
    j0 = max(0, -i); i = max(0, i); seg = sig[j0:j0 + buf.shape[1] - i] * gain
    l, r = np.cos((pan + 1) * np.pi / 4) * 1.414, np.sin((pan + 1) * np.pi / 4) * 1.414
    buf[0, i:i + len(seg)] += seg * l; buf[1, i:i + len(seg)] += seg * r


midi = lambda m: 440.0 * 2 ** ((m - 69) / 12)
env_exp = lambda n, k: np.exp(-np.arange(n) / SR * k)



# ======================= SFX =======================
def whoosh(dur=0.45, lo=300, hi=5000, up=True):
    n = int(dur * SR); tt = np.arange(n) / SR; x = rng.standard_normal(n)
    sweep = np.exp(np.linspace(np.log(lo), np.log(hi), n)) if up else np.exp(np.linspace(np.log(hi), np.log(lo), n))
    y = lp(x, sweep, 2); y = hp(y, 150)
    e = np.sin(np.pi * np.clip(tt / dur, 0, 1)) ** 1.6
    return y * e * 3.2


def pop(f=900, dur=0.09):
    n = int(dur * SR); tt = np.arange(n) / SR
    return np.sin(2 * np.pi * np.cumsum(f * (1 + 1.2 * np.exp(-tt * 60))) / SR) * np.exp(-tt * 45) * np.minimum(1, tt / 0.002)


def click():
    n = int(0.03 * SR); x = hp(rng.standard_normal(n), 2500) * env_exp(n, 220)
    n2 = int(0.05 * SR); tt = np.arange(n2) / SR
    return np.pad(x, (0, n2 - n)) * 0.8 + np.sin(2 * np.pi * 2200 * tt) * env_exp(n2, 120) * 0.25


def impact(dur=0.9):
    n = int(dur * SR); tt = np.arange(n) / SR
    boom = np.sin(2 * np.pi * np.cumsum(38 + 110 * np.exp(-tt * 18)) / SR) * np.exp(-tt * 4.5)
    crack = lp(rng.standard_normal(n), 2500) * np.exp(-tt * 28)
    return np.tanh(1.6 * (boom + 0.4 * crack))


def riser(dur=0.6):
    n = int(dur * SR); tt = np.arange(n) / SR
    sw = np.exp(np.linspace(np.log(400), np.log(9000), n))
    x = lp(rng.standard_normal(n), sw, 2) * 2.5
    tone = np.sin(2 * np.pi * np.cumsum(np.exp(np.linspace(np.log(220), np.log(880), n))) / SR) * 0.3
    return (x + tone) * (tt / dur) ** 2


def glitch(dur=0.22):
    n = int(dur * SR); out = np.zeros(n); i = 0
    while i < n:
        L_ = int(rng.uniform(0.008, 0.03) * SR); f = rng.uniform(300, 3000)
        seg = np.sign(np.sin(2 * np.pi * f * np.arange(L_) / SR)) * rng.uniform(0.3, 0.8)
        if rng.random() < 0.4: seg = rng.standard_normal(L_) * 0.5
        out[i:i + L_] = seg[: n - i]; i += L_ + int(rng.uniform(0, 0.012) * SR)
    return lp(out, 6000) * np.linspace(1, 0.4, n)


def neon(dur=0.5):
    n = int(dur * SR); tt = np.arange(n) / SR
    buzz = np.sign(np.sin(2 * np.pi * 120 * tt)) * 0.3 + np.sin(2 * np.pi * 240 * tt) * 0.3
    return lp(buzz, 1800) * np.exp(-tt * 5) * (0.6 + 0.4 * (rng.random(n) > 0.02))


def ding(f=1320):
    n = int(0.6 * SR); tt = np.arange(n) / SR
    return (np.sin(2 * np.pi * f * tt) + 0.4 * np.sin(2 * np.pi * f * 2.01 * tt)) * np.exp(-tt * 7) * np.minimum(1, tt / 0.002)


def key():
    n = int(0.035 * SR); tt = np.arange(n) / SR
    return hp(rng.standard_normal(n), 1800) * env_exp(n, 160) * 0.7 + np.sin(2 * np.pi * rng.uniform(1500, 2500) * tt) * env_exp(n, 200) * 0.2



# ======================= MIX =======================
def envelope(x, att=0.02, rel=0.28):
    m = np.abs(x).max(0)
    hop = int(0.01 * SR); n = len(m) // hop
    r = np.sqrt((m[: n * hop].reshape(n, hop) ** 2).mean(1))
    e = np.zeros(n); acc = 0
    for i in range(n):
        c = att if r[i] > acc else rel
        a = np.exp(-0.01 / c); acc = a * acc + (1 - a) * r[i]; e[i] = acc
    return np.interp(np.arange(len(m)) / hop, np.arange(n), e)


