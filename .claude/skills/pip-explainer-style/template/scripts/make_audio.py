"""Audio (48 kHz stereo) -> hf/assets/audio/{voice,music,sfx,mix_master}.wav   Run: /usr/bin/python3 scripts/make_audio.py

VOICE : the presenter's own voice from the source .mov (used whole, untrimmed: the user already cut it): high-pass, light
        denoise, mud cut / presence lift, de-ess, gentle compression, loudness-normalised, chain latency compensated.
MUSIC : original instrumental bed synthesised here (no third-party audio, no audio taken from any reference).
        Worked example: 140 BPM half-time trap-pop in D minor (Dm-Bb-F-C): filtered intro, drop on "100% AI", beat-stop
        before "tak boleh", re-entry on "brand trust", lighter groove for chatbot/blueprint, breakdown under the
        no-blueprint question (voice room), build into the end card, final hit and a ringing tail.
        PER VIDEO: change BPM / PROG / T0 and section(); keep the levels and the mix.
SFX   : synthesised whoosh / pop / click / impact / riser / glitch / ding, placed on the same word anchors the picture
        uses (scripts/timing.py), so a timing edit moves the sound too. PER VIDEO: rewrite build_sfx().
"""
import json, os, subprocess, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from sfx_dsp import SR, rng, lp, hp, place, whoosh, pop, click, impact, riser, glitch, ding, envelope
from edl import SEGS, SRC
from timing import T, TOTAL, SPEECH_END, END_CARD

ROOT = os.path.abspath(os.path.join(HERE, ".."))
AUD = os.path.join(ROOT, "hf", "assets", "audio"); os.makedirs(AUD, exist_ok=True)
END = END_CARD
N = int(TOTAL * SR)


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
    def env(x):
        n = len(x) // hop; e = np.log(np.sqrt((x[: n * hop].reshape(n, hop) ** 2).mean(1)) + 1e-4); return e - e.mean()
    ea, eb = env(a), env(b); L = min(len(ea), len(eb)) - 2 * search - 10
    best = max(range(-search, search + 1), key=lambda k: np.dot(ea[search + k: search + k + L], eb[search: search + L]))
    return best * hop


# ======================= VOICE =======================
def build_voice():
    raw = os.path.join(AUD, "_voice_raw.wav")
    ff("-i", SRC, "-vn", "-ac", "1", "-ar", str(SR), raw)
    v = read_wav(raw)[0]
    xf = int(0.010 * SR)
    out = np.zeros(0)
    for a, b in SEGS:
        seg = v[int(round(a * SR)): int(round(b * SR))].copy()
        seg[:xf] *= np.linspace(0, 1, xf); seg[-xf:] *= np.linspace(1, 0, xf)
        out = np.concatenate([out, seg])
    cat = os.path.join(AUD, "_voice_cat.wav"); write_wav(cat, out[None, :])
    chain = ("highpass=f=85,afftdn=nr=6:nf=-44,equalizer=f=240:t=q:w=1.1:g=-2,equalizer=f=3200:t=q:w=0.9:g=2.5,"
             "equalizer=f=9500:t=h:w=1:g=1.5,deesser=i=0.3,acompressor=threshold=-20dB:ratio=3:attack=6:release=90:makeup=2,"
             "loudnorm=I=-16:TP=-2:LRA=7")
    dst = os.path.join(AUD, "voice.wav")
    ff("-i", cat, "-af", chain + ",aresample=48000", "-ac", "2", dst)
    x = read_wav(dst)
    lag = envelope_lag(x[0], out)
    if lag > 0: x = np.pad(x[:, lag:], ((0, 0), (0, lag)))
    print("voice chain latency compensated:", round(lag / SR * 1000, 1), "ms")
    if x.shape[1] < N: x = np.pad(x, ((0, 0), (0, N - x.shape[1])))
    x = x[:, :N]
    for f_ in (raw, cat): os.remove(f_)
    write_wav(dst, x)
    return x


# ======================= MUSIC =======================
midi = lambda m: 440.0 * 2 ** ((m - 69) / 12)
BPM = 140.0
BEAT = 60 / BPM; BAR = 4 * BEAT; S16 = BEAT / 4
T0 = T["ai100"] - 2 * BAR  # a downbeat lands exactly on "100%" (the drop)
PROG = [(50, [62, 65, 69]), (46, [58, 62, 65]), (53, [60, 65, 69]), (48, [60, 64, 67])]  # Dm Bb F C

def section(t):
    """levels: pad, drums, bass, pluck, hats, pad cutoff"""
    if t < T["ai100"]: return 0.7, 0.65, 0.5, 0.5, 0.9, 1200               # punchy cold open: beat from frame 0, filtered
    if t < T["sebelum"] - 0.05: return 0.6, 1.0, 1.0, 0.8, 1.0, 2600       # drop on "100%"
    if t < T["dalam"] - 0.05: return 0.8, 0.0, 0.5, 0.4, 0.6, 1400         # mentor: story dip
    if t < T["takBoleh"] - 0.22: return 0.6, 1.0, 1.0, 0.75, 1.0, 2600
    if t < T["brand1"] - 0.02: return 0.0, 0.0, 0.0, 0.0, 0.0, 900          # beat stop -> "tak boleh" hit
    if t < T["baruBaru"] - 0.05: return 0.6, 1.0, 1.0, 0.75, 1.0, 2600
    if t < T["macamMana"] - 0.05: return 0.55, 0.85, 1.0, 0.0, 1.0, 2000    # chatbot / blueprint: tighter, no pluck
    if t < T["samaKontenAI"] - 0.05: return 0.85, 0.0, 0.35, 0.35, 0.35, 1100  # breakdown: space for the voice
    if t < END: return 0.8, 0.0, 0.4, 0.3, 0.25, 1300                       # light build, kept under the last line
    return 0.0, 0.0, 0.0, 0.0, 0.0, 900

def build_music():
    mus = np.zeros((2, N))
    nb = int((TOTAL - T0) / BAR) + 2
    b0 = int(np.floor(-T0 / BAR)) if T0 < 0 else 0
    for b in range(-2, nb):
        t0 = T0 + b * BAR
        if t0 > TOTAL or t0 + BAR < 0: continue
        root, tri = PROG[b % 4]
        dur = BAR + 0.08; n = int(dur * SR); tt = np.arange(n) / SR
        sig = np.zeros(n)
        for m in tri + [tri[0] - 12]:
            for det in (-0.08, 0.0, 0.08):
                sig += 2 * ((tt * midi(m) * 2 ** (det / 12) + rng.random()) % 1) - 1
        lv = section(t0 + 0.05)
        sig = lp(sig / 12, lv[5])
        e = np.minimum(1, tt / 0.05) * np.minimum(1, (dur - tt) / 0.08)
        # gate the pad per 16th when the drums are on (sidechain pump)
        if lv[1] > 0:
            ph = (tt % BEAT) / BEAT; e = e * (0.45 + 0.55 * np.minimum(1, ph / 0.35))
        place(mus, sig * e * 0.12 * lv[0], t0, pan=-0.35); place(mus, np.roll(sig, 900) * e * 0.12 * lv[0], t0, pan=0.35)
    kick_n = int(0.32 * SR); kt = np.arange(kick_n) / SR
    kick = np.sin(2 * np.pi * np.cumsum(48 + 140 * np.exp(-kt * 36)) / SR) * np.exp(-kt * 10)
    kick[: int(0.004 * SR)] += rng.standard_normal(int(0.004 * SR)) * 0.5
    clap_n = int(0.24 * SR)
    clap = hp(lp(rng.standard_normal(clap_n), 4500), 900) * np.exp(-np.arange(clap_n) / SR * 17)
    for d in (0.010, 0.021): clap[int(d * SR):] += hp(rng.standard_normal(clap_n - int(d * SR)), 1200) * np.exp(-np.arange(clap_n - int(d * SR)) / SR * 60) * 0.5
    hat_n = int(0.05 * SR); hat = hp(rng.standard_normal(hat_n), 7800) * np.exp(-np.arange(hat_n) / SR * 90)
    oh_n = int(0.22 * SR); ohat = hp(rng.standard_normal(oh_n), 6500) * np.exp(-np.arange(oh_n) / SR * 14)
    kick_pat = [0, 7, 10]
    bass_pat = [(0, 6), (7, 3), (10, 5)]
    for b in range(-2, nb):
        bt = T0 + b * BAR
        root, tri = PROG[b % 4]
        for s in range(16):
            t0 = bt + s * S16
            if t0 < 0 or t0 >= TOTAL: continue
            pad_l, dr, bl, pl, hl, _ = section(t0)
            if dr > 0:
                if s in kick_pat: place(mus, kick * 0.6 * dr, t0)
                if s == 8: place(mus, clap * 0.26 * dr, t0, pan=0.05)
                if s == 14 and b % 2 == 1: place(mus, ohat * 0.05 * dr, t0, pan=-0.3)
            if hl > 0 and s % 2 == 0:
                place(mus, hat * 0.07 * hl * (0.9 if s % 4 == 0 else 0.6), t0, pan=0.3)
            if hl > 0 and dr > 0 and b % 2 == 1 and s >= 12:
                for r in range(2): place(mus, hat * 0.045 * hl, t0 + r * S16 / 2, pan=0.35)
            if bl > 0:
                for (ps, ln) in bass_pat:
                    if s == ps:
                        n = int(ln * S16 * SR); tt = np.arange(n) / SR
                        f0 = midi(root - 12)
                        glide = f0 * (1 + 0.45 * np.exp(-tt * 40))
                        sig = np.tanh(2.4 * np.sin(2 * np.pi * np.cumsum(glide) / SR)) * np.minimum(1, (n / SR - tt) / 0.03)
                        place(mus, sig * 0.2 * bl, t0)
            if pl > 0 and s % 2 == 0:
                seq = [tri[0] + 12, tri[2], tri[1], tri[2], tri[0] + 12, tri[1] + 12, tri[2], tri[1]]
                m = seq[(s // 2) % 8]
                n = int(0.32 * SR); tt = np.arange(n) / SR
                tone = np.sin(2 * np.pi * midi(m) * tt + 0.9 * np.exp(-tt * 22) * np.sin(2 * np.pi * midi(m) * 3 * tt))
                tone *= np.exp(-tt * 10) * np.minimum(1, tt / 0.003)
                place(mus, tone * 0.05 * pl, t0, pan=-0.4 if s % 4 else 0.4)
                place(mus, tone * 0.02 * pl, t0 + 3 * S16, pan=0.5 if s % 4 else -0.5)
    # snare roll in the last 2 beats before the end card
    k = 0
    while True:
        t0 = END - 2 * BEAT + k * S16 / (1 + (k > 4))
        if t0 >= END - 0.02: break
        place(mus, clap * 0.08 * (0.4 + 0.6 * (t0 - (END - 2 * BEAT)) / (2 * BEAT)), t0, pan=0.1); k += 1
    # end card: ringing Dm chord + sub drop
    n = int((TOTAL - END + 0.2) * SR); tt = np.arange(n) / SR
    ch = sum(np.sin(2 * np.pi * midi(m) * tt) * (0.5 if m < 60 else 0.3) for m in (38, 50, 62, 65, 69, 74))
    place(mus, lp(ch, 3000) * np.exp(-tt * 1.3) * 0.12, END)
    sub = np.sin(2 * np.pi * np.cumsum(36 + 80 * np.exp(-tt * 14)) / SR) * np.exp(-tt * 2.0)
    place(mus, sub * 0.5, END)
    fade = np.ones(N); a = int((TOTAL - 0.9) * SR); fade[a:] = np.linspace(1, 0, N - a) ** 1.5
    mus *= fade
    return np.tanh(mus * 1.4) / 1.4


# ======================= SFX =======================
def build_sfx():
    fx = np.zeros((2, N))
    P = lambda sig, t, g, pan=0.0: place(fx, sig, t, g, pan)
    tick = lambda t, f=1568, g=0.5: (P(click(), t, g), P(ding(f), t + 0.02, g * 0.22))
    # 1 hook (punchy cold open)
    P(impact(0.9), 0.0, 0.55); P(whoosh(0.3, 3000, 400, up=False), 0.0, 0.2)
    P(pop(900, 0.1), T["jual"], 0.22); P(impact(0.6), T["produk"] - 0.02, 0.4); P(glitch(0.1), T["produk"] - 0.02, 0.1)
    P(whoosh(0.35, 400, 5000), T["bisnesBaru"] - 0.15, 0.28)
    for i in range(6): P(click(), T["ai100"] + i * 0.05, 0.25)  # counter ticks 0 -> 100
    P(impact(0.5), T["pakaiAI"] - 0.02, 0.35); P(glitch(0.1), T["pakaiAI"], 0.1)
    P(riser(0.55), T["ai100"] - 0.55, 0.22); P(impact(0.9), T["ai100"], 0.5)
    for i, k in enumerate(("video", "gambar", "poster")):
        P(whoosh(0.3, 500, 4500), T[k] - 0.2, 0.2, (-0.4, 0, 0.4)[i]); P(pop(700 + 120 * i, 0.1), T[k] - 0.02, 0.3, (-0.4, 0, 0.4)[i])
    P(impact(0.7), T["poster"], 0.3)
    P(whoosh(0.25, 900, 6000), T["sebelum"] - 0.15, 0.2); P(pop(600, 0.12), T["mentor"] - 0.1, 0.25)
    P(whoosh(0.3, 600, 6000), T["dalam"] - 0.12, 0.2)
    # 2 mekanisme
    P(pop(520, 0.13), T["tiga"], 0.38); P(impact(0.5), T["wajib"], 0.22)
    P(whoosh(0.7, 300, 3000), T["corong"], 0.18)
    tick(T["trafik"], 1175); tick(T["konten"], 1397)
    P(whoosh(0.25, 900, 6000), T["paling"] - 0.2, 0.2)
    tick(T["closing"], 1760, 0.6); P(impact(0.6), T["closing"], 0.3)
    P(pop(900, 0.1), T["conversion"], 0.25)
    # 2b sumber trafik / pecahan konten
    P(whoosh(0.25, 900, 6000), T["trafikQ"] - 0.1, 0.18); P(impact(0.45), T["trafikQ"], 0.25)
    P(whoosh(0.35, 400, 5000), T["sumber"] - 0.15, 0.22)
    for i, k in enumerate(("tiktok", "facebook", "instagram")): P(pop(760 + 140 * i, 0.1), T[k] - 0.05, 0.3, (-0.5, 0, 0.5)[i])
    P(whoosh(0.25, 900, 6000), T["untukMenarik"] - 0.1, 0.16); P(impact(0.6), T["kenaAda"] - 0.05, 0.35)
    P(whoosh(0.35, 400, 5000), T["dalamKonten"] - 0.15, 0.22)
    for i in range(12): P(pop(1100 + 60 * (i % 4), 0.05), T["pecahan"] - 0.1 + i * 0.03, 0.1, ((i % 3) - 1) * 0.5)
    P(whoosh(0.3, 5000, 500, up=False), T["pecahanBesar"] - 0.05, 0.16)
    tick(T["pecahanBesar"] + 0.15, 1175, 0.4); P(ding(1568), T["videoSebenar"], 0.1)
    tick(T["keduaVideo"], 1397, 0.4); P(ding(1760), T["videoAI2"], 0.1)
    # 3 produk baru / 100% AI
    P(whoosh(0.35, 400, 5000), T["soDekat"] - 0.15, 0.22); P(pop(650, 0.12), T["launch"] - 0.2, 0.3)
    for i in range(6): P(pop(1000 + 70 * i, 0.07), T["semua"] - 0.08 + i * 0.07, 0.16, ((i % 3) - 1) * 0.4)
    P(impact(0.5), T["semua"] + 0.47, 0.28)
    # 4 tak boleh / brand trust
    P(impact(1.2), T["takBoleh"] - 0.04, 0.75); P(glitch(0.12), T["takBoleh"] - 0.04, 0.12)
    P(impact(0.8), T["brand1"] - 0.04, 0.42); P(ding(2093), T["brand1"], 0.1)
    P(whoosh(0.35, 400, 5000), T["orangDah"] - 0.2, 0.22)
    tick(T["percayaBrand"] + 0.15, 1568, 0.45); tick(T["percayaProduk"] + 0.15, 1760, 0.45)
    # 5 FYP
    P(whoosh(0.45, 300, 5000), T["sebabTu"] - 0.1, 0.26)
    P(pop(800, 0.1), T["gunaAI"], 0.18)
    for k, f_ in (("view", 1568), ("conv2", 1760)):
        P(pop(760, 0.12), T[k] - 0.05, 0.3); P(ding(f_), T[k] + 0.1, 0.12)
    P(whoosh(0.25, 900, 6000), T["brandSendiri"] - 0.2, 0.16)
    P(pop(560, 0.12), T["orangPercaya"] - 0.04, 0.3)
    # 6 boost
    P(whoosh(0.35, 400, 5000), T["videoAI"] - 0.2, 0.22); P(impact(0.45), T["videoAI"] + 0.6, 0.22)
    P(riser(0.7), T["boost"] - 0.1, 0.22)
    P(whoosh(0.25, 900, 6000), T["soKalau"] - 0.2, 0.16)
    P(impact(0.8), T["brandDulu"] - 0.06, 0.45)
    # 7 tiga tindakan
    P(whoosh(0.3, 500, 5000), T["buatKonten"] - 0.25, 0.2)
    for k, f_ in (("buatKonten", 1175), ("result", 1397), ("testimoni", 1760)): tick(T[k] + 0.12, f_, 0.55)
    # 7b sama juga closing
    P(whoosh(0.3, 400, 5000), T["samaClosing"] - 0.15, 0.2); P(click(), T["samaClosing"] + 0.8, 0.4)
    # 8 chatbot (soft UI)
    A8 = T["baruBaru"] - 0.05
    P(glitch(0.1), A8 - 0.02, 0.1); P(whoosh(0.3, 800, 6000), A8 - 0.12, 0.2)
    P(ding(1760), A8 + 0.25, 0.1); P(ding(1319), A8 + 0.9, 0.09)
    P(ding(2349), T["chatbot"] - 0.1, 0.13); P(ding(3136), T["chatbot"] - 0.02, 0.1); P(pop(1200, 0.06), T["chatbot"] - 0.1, 0.15)
    P(pop(820, 0.1), T["service"] - 0.05, 0.22, -0.3); P(pop(920, 0.1), T["produk2"] - 0.05, 0.22, 0.3)
    # 9 blueprint
    A9 = T["awakSendiri"] - 0.05
    P(whoosh(0.35, 400, 5000), A9 - 0.15, 0.22)
    for i in range(4): P(pop(600 + 90 * i, 0.08), A9 + 0.1 + i * 0.35, 0.16)
    P(glitch(0.18), T["takAda"], 0.14); P(impact(0.55), T["takAda"], 0.32)
    # 10 no-blueprint question: almost nothing (voice room)
    P(pop(900, 0.08), T["chatbot2"] - 0.1, 0.12)
    P(impact(0.5), T["soClear"] + 0.05, 0.28)
    # 11 fundamental / buih / end
    P(whoosh(0.35, 400, 5000), T["samaKontenAI"] - 0.2, 0.2); P(impact(0.5), T["fundamental"] - 0.1, 0.25)
    for i in range(3): P(pop(700 + 110 * i, 0.09), T["samaKontenAI"] + 0.2 + i * 0.12, 0.2, (-0.4, 0, 0.4)[i])
    for i in range(7): P(pop(1300 + 180 * (i % 3), 0.05), T["buih"] + 0.8 + i * 0.2 + rng.uniform(-0.05, 0.05), 0.05, rng.uniform(-0.5, 0.5))
    P(whoosh(0.25, 600, 8000), END - 0.04, 0.2)  # no riser under the last word
    P(impact(1.8), END, 0.8)
    return fx


if __name__ == "__main__":
    voice = build_voice()
    music = build_music()
    sfx = build_sfx()
    env = envelope(voice)
    act = np.clip(env / (np.percentile(env[env > 1e-4], 60) + 1e-9), 0, 1)
    duck_m = 10 ** (-8 * act / 20)
    duck_s = 10 ** (-3 * act / 20)
    music_n = music / (np.abs(music).max() + 1e-9)
    sfx_n = sfx / (np.abs(sfx).max() + 1e-9)
    write_wav(os.path.join(AUD, "music.wav"), music_n * 0.9)
    write_wav(os.path.join(AUD, "sfx.wav"), sfx_n * 0.9)
    tt = np.arange(N) / SR
    hold = 1 + 1.0 * np.clip((tt - SPEECH_END) / 0.3, 0, 1)
    mix = voice + music_n * duck_m * hold * 0.18 + sfx_n * duck_s * 0.32
    sp = act > 0.5
    print("music under speech vs voice (dB):", round(20 * np.log10(np.sqrt(((music_n * duck_m * 0.18)[:, sp] ** 2).mean()) / np.sqrt((voice[:, sp] ** 2).mean())), 1))
    pre = os.path.join(AUD, "_mix_pre.wav"); write_wav(pre, mix)
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", pre, "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    js = json.loads(r[r.rindex("{"): r.rindex("}") + 1])
    af = (f"loudnorm=I=-14:TP=-1.5:LRA=11:linear=true:measured_I={js['input_i']}:measured_TP={js['input_tp']}:"
          f"measured_LRA={js['input_lra']}:measured_thresh={js['input_thresh']}:offset={js['target_offset']},alimiter=limit=0.84:level=false,aresample=48000")
    ff("-i", pre, "-af", af, "-ar", "48000", os.path.join(AUD, "mix_master.wav"))
    os.remove(pre)
    print("ok", {k: js[k] for k in ("input_i", "input_tp")})
