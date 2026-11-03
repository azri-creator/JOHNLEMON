"""Audio for a Glow Keyword build (48 kHz stereo). Writes work/audio/{voice,music,sfx}.wav and hf/assets/mix.wav.
Mix logic is unchanged from the Remotion version; only the timing source (timing.json) and the per-video config moved.

VOICE  : the presenter's own voice from the source video (never re-generated). Per-shot gain toward -16 dB (75 %),
         de-clip, HPF 80, light FFT denoise, -2.5 dB @250 Hz, +2.5 dB @3.4 kHz, +1 dB shelf 9 kHz, de-ess,
         compressor 3:1 @ -21 dB, loudnorm -16; chain latency measured and compensated (lip sync).
MUSIC  : original bed synthesised here (no third-party audio). Default = the Jago Prompt bed: 144 BPM (72 half-time)
         trap-pop, A minor Am-F-C-G, 808 + kick + clap on 3 + rolling hats + FM pluck, filtered intro, downbeat on the
         first hard cut, hit on the CTA. CHANGE tempo/key/groove/SECTIONS per video (variation_playbook.md); keep the mix.
SFX    : synthesised whoosh / pop / click / impact / riser / glitch / neon / typing / ding on the same word anchors the
         picture uses (timing.json), so a timing edit moves the sound too. Rewrite cues() per video.
MIX    : music -9 dB and SFX -3 dB under speech (voice envelope), music ~16 dB below the voice, +7 dB on the CTA hold,
         two-pass linear loudnorm to -14 LUFS / -1.5 dBTP + limiter.

Usage:  SRC_MOV=/path/to/source.mov /usr/bin/python3 scripts/make_audio.py
"""
import json, os, subprocess, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
AUD = os.path.join(ROOT, "work", "audio"); os.makedirs(AUD, exist_ok=True)
OUT = os.path.join(ROOT, "hf", "assets", "mix.wav"); os.makedirs(os.path.dirname(OUT), exist_ok=True)
SRC = os.environ.get("SRC_MOV") or sys.exit("set SRC_MOV to the presenter source video")
SR = 48000
rng = np.random.default_rng(11)

# ---------- timing shared with the picture ----------
TM = json.load(open(os.path.join(ROOT, "timing.json")))
T, CUT, L = TM["T"], TM["CUT"], TM["L"]
TOTAL, SRC_END, CTA = float(TM["TOTAL"]), float(TM["SRC_END"]), float(TM["L"]["cta"])
N = int(TOTAL * SR)
EDGES = [0.0] + sorted(v for v in CUT.values() if v < SRC_END) + [999.0]   # shots, for the per-shot voice gain


def ff(*args):
    subprocess.run(["ffmpeg", "-v", "error", "-y", *args], check=True)


def read_wav(p):
    import wave
    w = wave.open(p); n = w.getnframes(); ch = w.getnchannels()
    x = np.frombuffer(w.readframes(n), np.int16).astype(np.float64) / 32768
    return x.reshape(-1, ch).T


def write_wav(p, x):
    import wave
    x = np.clip(x, -1, 1)
    w = wave.open(p, "wb"); w.setnchannels(x.shape[0]); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((x.T * 32767).astype(np.int16).tobytes()); w.close()


def envelope_lag(a, b, hop=48, search=200):
    """samples by which `a` lags `b` (log-RMS envelope cross-correlation, 1 ms resolution)"""
    def env(x):
        n = len(x) // hop; e = np.log(np.sqrt((x[: n * hop].reshape(n, hop) ** 2).mean(1)) + 1e-4); return e - e.mean()
    ea, eb = env(a), env(b); L_ = min(len(ea), len(eb)) - 2 * search - 10
    best = max(range(-search, search + 1), key=lambda k: np.dot(ea[search + k: search + k + L_], eb[search: search + L_]))
    return best * hop


def voiced_median_db(x):
    """median level (dB) of the voiced 50 ms frames of one shot (frames within 25 dB of its loudest)"""
    h = int(0.05 * SR); n = len(x) // h
    if n < 4: return -16.0
    db = 20 * np.log10(np.sqrt((x[: n * h].reshape(n, h) ** 2).mean(1)) + 1e-9)
    return float(np.median(db[db > db.max() - 25]))


# ======================= VOICE =======================
def build_voice():
    raw = os.path.join(AUD, "_voice_raw.wav")
    ff("-i", SRC, "-vn", "-ac", "1", "-ar", str(SR), "-t", f"{SRC_END + 0.5:.3f}", "-af", "adeclip", raw)
    v = read_wav(raw)[0]
    # per-shot gain: measured voiced medians -> 75 % of the way to -16 dB (Jago Prompt clips were 13.5..18.8 dB apart)
    g = np.ones_like(v); tt = np.arange(len(v)) / SR
    for a, b in zip(EDGES, EDGES[1:]):
        m = (tt >= a) & (tt < b)
        if not m.any(): continue
        med = voiced_median_db(v[m]); db = 0.75 * (-16 - med)
        g[m] = 10 ** (db / 20); print(f"shot {a:6.2f}-{min(b, SRC_END):6.2f}: voiced median {med:6.1f} dB -> {db:+.1f} dB")
    k = int(0.03 * SR); g = np.convolve(g, np.ones(k) / k, mode="same")  # 30 ms crossfade of gain at cuts
    bal = os.path.join(AUD, "_voice_bal.wav"); write_wav(bal, (v * g)[None, :])
    chain = ("highpass=f=80,afftdn=nr=8:nf=-42,equalizer=f=250:t=q:w=1.1:g=-2.5,equalizer=f=3400:t=q:w=0.9:g=2.5,"
             "equalizer=f=9000:t=h:w=1:g=1,deesser=i=0.35,acompressor=threshold=-21dB:ratio=3:attack=6:release=90:makeup=2,"
             "loudnorm=I=-16:TP=-2:LRA=7")
    out = os.path.join(AUD, "voice.wav")
    ff("-i", bal, "-af", chain + ",aresample=48000", "-ac", "2", out)
    x = read_wav(out)
    # the FFT denoiser / de-clipper add a few ms of latency: measure it against the input and shift back (lip sync)
    lag = envelope_lag(x[0], v * g)
    if lag > 0: x = np.pad(x[:, lag:], ((0, 0), (0, lag)))
    print("voice chain latency compensated:", round(lag / SR * 1000, 1), "ms")
    if x.shape[1] < N: x = np.pad(x, ((0, 0), (0, N - x.shape[1])))
    x = x[:, :N]
    # fade the room tone under the frozen end-card frame
    fo = int(0.12 * SR); end = int(SRC_END * SR)
    x[:, end:end + fo] *= np.linspace(1, 0, len(x[0, end:end + fo])); x[:, end + fo:] = 0
    for f in (raw, bal): os.remove(f)
    write_wav(out, x)
    return x


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


# ======================= MUSIC (per-video: tempo, key, groove, sections) =======================
BPM = 144.0
BEAT = 60 / BPM; BAR = 4 * BEAT
T0 = CUT["B"] - 3 * BAR   # downbeat lands exactly on the first hard cut
PROG = [(57, [57, 60, 64]), (53, [53, 57, 60]), (48, [48, 52, 55]), (55, [55, 59, 62])]  # Am F C G
# (from_time, pad, drums, bass, pluck, hats, pad_cutoff_hz): the arrangement. Jago Prompt full version also had a
# pluck-led how-to, a drum-less grid moment and a breakdown (pad cut 900 Hz) + riser before the offer.
SECTIONS = [
    (-99, 0.8, 0.0, 0.35, 0.0, 0.55, 700),    # hook: filtered, no drums
    (CUT["B"], 0.7, 1.0, 1.0, 0.0, 1.0, 2400),  # drop on the first hard cut
    (CTA, 0.9, 0.0, 0.55, 0.55, 0.0, 2400),     # CTA hold: drums out, hit + tail
]


def section(t):
    lv = SECTIONS[0]
    for s in SECTIONS:
        if t >= s[0]: lv = s
    return lv[1:]


def build_music():
    mus = np.zeros((2, N))
    nbars = int((TOTAL - T0) / BAR) + 2
    # pad (detuned saws, filtered; opens up after the hook)
    for b in range(nbars):
        t0 = T0 + b * BAR
        if t0 > TOTAL: break
        root, tri = PROG[b % 4]
        dur = BAR + 0.08; n = int(dur * SR); tt = np.arange(n) / SR
        sig = np.zeros(n)
        for m in tri + [tri[0] + 12]:
            for det in (-0.09, 0.0, 0.09):
                sig += 2 * ((tt * midi(m) * 2 ** (det / 12) + rng.random()) % 1) - 1
        lv = section(t0 + 0.05)
        sig = lp(sig / 12, lv[5])
        e = np.minimum(1, tt / 0.06) * np.minimum(1, (dur - tt) / 0.08)
        place(mus, sig * e * 0.11 * lv[0], t0, pan=-0.35); place(mus, np.roll(sig, 700) * e * 0.11 * lv[0], t0, pan=0.35)
    # drums / 808 / hats / pluck on a 16th grid
    kick_n = int(0.3 * SR); kt = np.arange(kick_n) / SR
    kick = np.sin(2 * np.pi * np.cumsum(50 + 130 * np.exp(-kt * 38)) / SR) * np.exp(-kt * 11)
    kick[: int(0.004 * SR)] += rng.standard_normal(int(0.004 * SR)) * 0.5
    clap_n = int(0.22 * SR)
    clap = hp(lp(rng.standard_normal(clap_n), 4200), 900) * env_exp(clap_n, 18)
    for d in (0.011, 0.022): clap[int(d * SR):] += hp(rng.standard_normal(clap_n - int(d * SR)), 1200) * env_exp(clap_n - int(d * SR), 60) * 0.5
    hat_n = int(0.05 * SR); hat = hp(rng.standard_normal(hat_n), 7500) * env_exp(hat_n, 90)
    s16 = BEAT / 4
    kick_pat = [0, 6, 10]            # 16th positions in a bar (trap half-time feel)
    bass_pat = [(0, 5), (6, 3), (10, 5)]
    for b in range(nbars):
        bt = T0 + b * BAR
        root, tri = PROG[b % 4]
        for s in range(16):
            t0 = bt + s * s16
            if t0 < 0 or t0 >= TOTAL: continue
            pad_l, dr, bl, pl, hl, _ = section(t0)
            if dr > 0:
                if s in kick_pat: place(mus, kick * 0.55 * dr, t0)
                if s == 8: place(mus, clap * 0.22 * dr, t0, pan=0.05)
            if hl > 0 and s % 2 == 0:
                vel = 0.9 if s % 4 == 0 else 0.6
                place(mus, hat * 0.07 * hl * vel, t0, pan=0.3)
            if hl > 0 and dr > 0 and b % 2 == 1 and s >= 12:  # rolls
                for r_ in range(2): place(mus, hat * 0.045 * hl, t0 + r_ * s16 / 2, pan=0.35)
            if bl > 0:
                for (ps, ln) in bass_pat:
                    if s == ps:
                        n = int(ln * s16 * SR); tt = np.arange(n) / SR
                        f0 = midi(root - 24)
                        glide = f0 * (1 + 0.5 * np.exp(-tt * 40))
                        sig = np.tanh(2.2 * np.sin(2 * np.pi * np.cumsum(glide) / SR)) * np.minimum(1, (n / SR - tt) / 0.03)
                        place(mus, sig * 0.2 * bl, t0)
            if pl > 0 and s % 2 == 0:
                seq = [tri[0] + 24, tri[2] + 12, tri[1] + 12, tri[2] + 12, tri[0] + 24, tri[1] + 24, tri[2] + 12, tri[1] + 12]
                m = seq[(s // 2) % 8]
                n = int(0.35 * SR); tt = np.arange(n) / SR
                tone = np.sin(2 * np.pi * midi(m) * tt + 0.9 * np.exp(-tt * 20) * np.sin(2 * np.pi * midi(m) * 3 * tt))
                tone *= np.exp(-tt * 9) * np.minimum(1, tt / 0.003)
                place(mus, tone * 0.05 * pl, t0, pan=-0.4 if s % 4 else 0.4)
                place(mus, tone * 0.02 * pl, t0 + 3 * s16, pan=0.5 if s % 4 else -0.5)
    # CTA hit + tail chord
    n = int(3.6 * SR); tt = np.arange(n) / SR
    hit = np.sin(2 * np.pi * np.cumsum(40 + 90 * np.exp(-tt * 20)) / SR) * np.exp(-tt * 2.2)
    place(mus, hit * 0.5, CTA)
    fade = np.ones(N); a = int((TOTAL - 1.6) * SR); fade[a:] = np.linspace(1, 0, N - a) ** 1.5
    mus *= fade
    mus = np.tanh(mus * 1.4) / 1.4
    return mus


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



def cues(P, typing):
    """SFX cue list for the worked example (Jago Prompt hook + intro + CTA). Rewrite per video."""
    # 1 hook
    P(pop(1100), 0.04, 0.18); P(pop(1250), T["nakBuat"], 0.16)
    for t in (T["AI"], T["real"]): P(whoosh(0.28, 500, 4000), t - 0.1, 0.18)
    P(whoosh(0.4, 300, 5000), T["saya"] - 0.12, 0.28)
    for i, t in enumerate((T["try_"], T["mm1"], T["mm2"])): P(pop(700 + i * 150), t, 0.35, (-0.5, 0, 0.5)[i])
    P(impact(0.6), T["prompt1"] - 0.02, 0.35)
    P(whoosh(0.4, 400, 3500), T["muka1"], 0.3)
    for i in range(3): P(whoosh(0.18, 1500, 6000), T["muka1"] + 0.44 + i * 0.06, 0.12, (-0.5, 0, 0.5)[i])
    P(pop(600), T["asyik"], 0.35)
    for i in range(3): P(pop(1400 + 200 * i, 0.07), T["asyik"] + i * 0.1, 0.2, (-0.5, 0, 0.5)[i])
    P(glitch(0.25), T["lari"], 0.25)
    P(riser(0.75), CUT["B"] - 0.75, 0.3); P(whoosh(0.35, 800, 7000), CUT["B"] - 0.2, 0.35); P(impact(0.8), CUT["B"], 0.45)
    # 2 intro
    P(neon(0.6), T["sebelum"], 0.14); P(impact(0.7), T["prompts"] - 0.04, 0.42)
    P(riser(0.5), T["character1"] - 0.5, 0.25); P(impact(0.9), T["character1"] - 0.03, 0.5); P(neon(0.5), T["sheet1"], 0.14)
    P(pop(1300), T["nak2"], 0.15); P(pop(1450), T["video2"], 0.15); P(pop(650), T["kekal"], 0.35)
    P(impact(0.6), T["wajib"] - 0.02, 0.42); P(neon(0.5), T["start"], 0.14)
    # 3 CTA end card
    P(riser(0.6), CTA - 0.6, 0.35); P(impact(1.2), CTA + 0.03, 0.6); P(whoosh(0.5, 600, 8000), CTA - 0.1, 0.3)
    for i, dt in enumerate((0.1, 0.28, 0.42)): P(pop(600 + 80 * i, 0.12), CTA + dt, 0.3)
    P(impact(0.8), CTA + 0.75, 0.48); P(ding(1760), CTA + 0.78, 0.12)
    P(whoosh(0.3, 600, 5000), CTA + 1.15, 0.15)
    typing(CTA + 1.55, CTA + 1.9, 0.35)
    P(click(), CTA + 2.05, 0.5); P(ding(2093), CTA + 2.08, 0.16)


def build_sfx():
    fx = np.zeros((2, N))
    P = lambda sig, t, g, pan=0.0: place(fx, sig, t, g, pan)
    typing = lambda a, b, g=0.35: [P(key(), a + k * 0.055 + rng.uniform(-0.01, 0.01), g * rng.uniform(0.7, 1), rng.uniform(-0.3, 0.3)) for k in range(int((b - a) / 0.055))]
    cues(P, typing)
    return fx


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


if __name__ == "__main__":
    voice = build_voice()
    music = build_music()
    sfx = build_sfx()
    env = envelope(voice)
    act = np.clip(env / (np.percentile(env[env > 1e-4], 60) + 1e-9), 0, 1)
    duck_m = 10 ** (-9 * act / 20)   # music -9 dB under speech
    duck_s = 10 ** (-3 * act / 20)   # sfx -3 dB under speech
    music_n = music / (np.abs(music).max() + 1e-9)
    sfx_n = sfx / (np.abs(sfx).max() + 1e-9)
    write_wav(os.path.join(AUD, "music.wav"), music_n * 0.9)
    write_wav(os.path.join(AUD, "sfx.wav"), sfx_n * 0.9)
    # after the last word the bed carries the CTA hold: bring it up ~7 dB
    tt = np.arange(N) / SR
    hold = 1 + 1.25 * np.clip((tt - (CTA + 0.1)) / 0.4, 0, 1)
    mix = voice + music_n * duck_m * hold * 0.2 + sfx_n * duck_s * 0.3
    sp = act > 0.5
    print("music under speech vs voice (dB):", round(20 * np.log10(np.sqrt(((music_n * duck_m * 0.2)[:, sp] ** 2).mean()) / np.sqrt((voice[:, sp] ** 2).mean())), 1))
    pre = os.path.join(AUD, "_mix_pre.wav"); write_wav(pre, mix)
    # two-pass linear loudness normalisation to -14 LUFS / -1.5 dBTP (social delivery)
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", pre, "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    js = json.loads(r[r.rindex("{"): r.rindex("}") + 1])
    af = (f"loudnorm=I=-14:TP=-1.5:LRA=11:linear=true:measured_I={js['input_i']}:measured_TP={js['input_tp']}:"
          f"measured_LRA={js['input_lra']}:measured_thresh={js['input_thresh']}:offset={js['target_offset']},alimiter=limit=0.84:level=false,aresample=48000")
    ff("-i", pre, "-af", af, "-ar", "48000", OUT)
    os.remove(pre)
    print("wrote", OUT, {k: js[k] for k in ("input_i", "input_tp")})
