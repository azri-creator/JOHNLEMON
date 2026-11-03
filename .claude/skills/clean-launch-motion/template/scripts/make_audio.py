"""Clean Launch Motion: original music + SFX + VO mix, all synthesised here (no samples -> no licence dependency).

Music: bright product-launch bed, D major I-V-vi-IV; tempo is chosen near plan.music.target_bpm so the first scene
cut lands exactly on a beat. Pad + plucked arpeggio with echo + soft kick/bass/hats (claps in the back half);
first scene = intro (no drums), drums drop for one bar when the last (CTA) scene starts, bed resolves and fades.
SFX: a whoosh on every scene cut (automatic) + the cues listed in plan.json "sfx".
Mix: music ~12 dB under VO and ducked -6 dB under speech; master -14 LUFS / -1.5 dBTP.

plan.json "sfx" entries: {"type": whoosh|pop|tick|tap|chime|riser|shimmer, "at": <anchor>, "off": s, "gain": g, "pan": -1..1,
                          optional "dur", "bright" (whoosh), "freq" (pop/tick), "notes" (chime, MIDI list)}
anchor: "scene:n" (n-th word of that scene, negative from the end), a word id like "storyboard.#1", or seconds (number).

Writes hf/assets/music.wav, sfx.wav and mix.wav (48 kHz stereo, -14 LUFS). hf/index.html plays mix.wav as its one <audio>.

usage: /usr/bin/python3 scripts/make_audio.py   (then re-run build.py so the <audio> tag is added)
"""
import json, os, subprocess
from itertools import accumulate
import numpy as np
from common import ASSETS, ffmpeg, load_plan, load_words, timing

AUD = ASSETS
FF = ffmpeg()
SR = 48000
rng = np.random.default_rng(7)

plan = load_plan()
words = load_words()
BY_ID = {w["id"]: w for w in words}
CUT, _SPAN, VO_END, TOTAL = timing(plan, words)
SCENES = plan["scenes"]


def scene_words(k):
    return [w for w in words if w["scene"] == k]


def anchor(a):
    if isinstance(a, (int, float)):
        return float(a)
    if ":" in a:
        k, n = a.split(":")
        lst = scene_words(k); n = int(n)
        return lst[max(0, min(len(lst) - 1, n if n >= 0 else len(lst) + n))]["s"]
    return BY_ID[a]["s"]


N = int(np.ceil(TOTAL * SR))


# ---------------- helpers ----------------
def lp(x, fc):
    a = np.exp(-2 * np.pi * fc / SR)
    for _ in range(2):
        x = np.fromiter(accumulate(x * (1 - a), lambda p, v: v + a * p), dtype=np.float64, count=len(x))
    return x


def hp(x, fc):
    return x - lp(x, fc)


def env_adsr(n, a, d, s, r, sus_len):
    A, D, R = int(a * SR), int(d * SR), int(r * SR)
    S = max(0, sus_len - A - D)
    e = np.concatenate([np.linspace(0, 1, max(A, 1)), np.linspace(1, s, max(D, 1)), np.full(S, s), np.linspace(s, 0, max(R, 1))])
    return e[:n] if len(e) >= n else np.pad(e, (0, n - len(e)))


def place(buf, sig, t, gain=1.0, pan=0.0):
    i = int(t * SR)
    if i >= buf.shape[1] or i + len(sig) <= 0:
        return
    j0 = max(0, -i); i = max(0, i)
    seg = sig[j0:j0 + buf.shape[1] - i]
    l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    buf[0, i:i + len(seg)] += seg * gain * l * 1.414
    buf[1, i:i + len(seg)] += seg * gain * r * 1.414


midi = lambda m: 440.0 * 2 ** ((m - 69) / 12)

# ---------------- music ----------------
first_cut = CUT[SCENES[1]] if len(SCENES) > 1 else 2.0
target = plan.get("music", {}).get("target_bpm", 124)
_k = min(range(2, 24), key=lambda k: abs(60 * k / first_cut - target))
BEAT = first_cut / _k
BAR = BEAT * 4
BPM = 60 / BEAT
CHORDS = [(62, [62, 66, 69]), (57, [57, 61, 64]), (59, [59, 62, 66]), (55, [55, 59, 62])]  # D A Bm G
music = np.zeros((2, N))
last_cut = CUT[SCENES[-1]]
mid_cut = CUT[SCENES[len(SCENES) // 2]]


def section_level(t):
    """(pad, pluck, drums, bass)"""
    if len(SCENES) > 1 and t < first_cut: return 0.8, 0.55, 0.0, 0.0
    if t < mid_cut: return 0.7, 0.7, 0.75, 0.8
    if t < last_cut: return 0.7, 0.8, 0.9, 0.9
    if t < last_cut + BAR: return 0.9, 0.7, 0.0, 0.3
    if t < VO_END + 0.4: return 0.85, 0.75, 0.55, 0.7
    return 0.9, 0.4, 0.0, 0.5


n_bars = int(np.ceil(TOTAL / BAR)) + 1
for b in range(0, n_bars, 2):  # pad, 2 bars per chord
    t0 = b * BAR
    if t0 >= TOTAL: break
    root, triad = CHORDS[(b // 2) % 4]
    last = t0 + 2 * BAR >= VO_END + 0.4
    dur = (TOTAL - t0 + 0.5) if last else 2 * BAR + 0.25
    if last: root, triad = CHORDS[0]
    n = int(dur * SR); tt = np.arange(n) / SR
    sig = np.zeros(n)
    for m in triad + [triad[0] + 12]:
        for det in (-0.07, 0.0, 0.07):
            sig += 2 * ((tt * midi(m) * 2 ** (det / 12) + rng.random()) % 1) - 1
    sig = lp(sig / 12, 1500 + 900 * np.clip((t0 - first_cut) / 20, 0, 1))
    rel = 2.5 if last else 0.6
    e = env_adsr(n, 0.35, 0.3, 0.8, rel, n - int(rel * SR))
    lvl = section_level(t0 + 0.1)[0]
    place(music, sig * e * 0.16 * lvl, t0, pan=-0.25)
    place(music, np.roll(sig, 900) * e * 0.16 * lvl, t0, pan=0.25)

pattern = [0, 2, 1, 2, 3, 2, 1, 2]
for b in range(n_bars):  # pluck arpeggio in 8ths with echo
    for k in range(8):
        t0 = b * BAR + k * BEAT / 2
        if t0 >= min(TOTAL - 0.8, VO_END + 1.2): break
        _, triad = CHORDS[(b // 2) % 4]
        notes = [triad[0] + 12, triad[1] + 12, triad[2] + 12, triad[0] + 24]
        lvl = section_level(t0)[1]
        if lvl <= 0: continue
        n = int(0.5 * SR); tt = np.arange(n) / SR; f0 = midi(notes[pattern[k]])
        tone = np.sin(2 * np.pi * f0 * tt + 1.2 * np.exp(-tt * 18) * np.sin(2 * np.pi * f0 * 2 * tt)) * np.exp(-tt * 7.5) * np.minimum(1, tt / 0.004)
        vel = 0.9 if k % 2 == 0 else 0.65
        place(music, tone * 0.075 * lvl * vel, t0, pan=0.3 if k % 2 else -0.3)
        place(music, tone * 0.03 * lvl * vel, t0 + 3 * BEAT / 4, pan=-0.6 if k % 2 else 0.6)

kick_n = int(0.35 * SR); kt = np.arange(kick_n) / SR
kick = np.sin(2 * np.pi * np.cumsum(45 + 95 * np.exp(-kt * 28)) / SR) * np.exp(-kt * 9)
hat_n = int(0.06 * SR); hat = hp(rng.standard_normal(hat_n), 7000) * np.exp(-np.arange(hat_n) / SR * 70)
clap_n = int(0.18 * SR); clap = hp(lp(rng.standard_normal(clap_n), 3500), 900) * np.exp(-np.arange(clap_n) / SR * 22)
for b in range(n_bars):
    for beat in range(4):
        t0 = b * BAR + beat * BEAT
        if t0 >= TOTAL: break
        _, _, dl, bl = section_level(t0)
        if dl > 0:
            if beat in (0, 2): place(music, kick * 0.42 * dl, t0)
            if beat in (1, 3) and mid_cut <= t0 < last_cut: place(music, clap * 0.10 * dl, t0, pan=0.1)
            place(music, hat * 0.05 * dl, t0 + 0.5 * BEAT, pan=0.35)
        if bl > 0:
            f0 = midi(CHORDS[(b // 2) % 4][0] - 24)
            for h in (0, 0.5):
                n = int(BEAT / 2 * 0.9 * SR); tt = np.arange(n) / SR
                bs = np.tanh(1.6 * np.sin(2 * np.pi * f0 * tt)) * np.minimum(1, tt / 0.01) * np.exp(-tt * 3)
                place(music, bs * 0.16 * bl * (1.0 if h == 0 else 0.7), t0 + h * BEAT)

pump = np.ones(N)
for b in range(n_bars):
    for beat in (0, 2):
        t0 = b * BAR + beat * BEAT
        if section_level(t0)[2] <= 0: continue
        i = int(t0 * SR)
        if i >= N: break
        seg = 1 - 0.28 * np.exp(-np.arange(min(int(0.28 * SR), N - i)) / SR * 12)
        pump[i:i + len(seg)] *= seg
music *= pump
fade_n = int(1.2 * SR)
music[:, -fade_n:] *= np.linspace(1, 0, fade_n) ** 1.5
music[:, :int(0.02 * SR)] *= np.linspace(0, 1, int(0.02 * SR))


# ---------------- SFX ----------------
def whoosh(dur=0.55, bright=2500):
    n = int(dur * SR); tt = np.arange(n) / SR
    noise = rng.standard_normal(n)
    return (lp(noise, bright) - lp(noise, 300)) * np.sin(np.pi * np.clip(tt / dur, 0, 1)) ** 2


def tick(freq=1900, dur=0.09):
    n = int(dur * SR); tt = np.arange(n) / SR
    return np.sin(2 * np.pi * freq * tt) * np.exp(-tt * 55) + 0.3 * np.sin(2 * np.pi * freq * 1.5 * tt) * np.exp(-tt * 80)


def pop(freq=620, dur=0.16):
    n = int(dur * SR); tt = np.arange(n) / SR
    return np.sin(2 * np.pi * np.cumsum(freq * (1 + 0.6 * np.exp(-tt * 40))) / SR) * np.exp(-tt * 24)


def tap():
    n = int(0.05 * SR); tt = np.arange(n) / SR
    return (hp(rng.standard_normal(n), 2500) * 0.5 + np.sin(2 * np.pi * 1400 * tt)) * np.exp(-tt * 120)


def chime(notes=(81, 86, 90, 93), gap=0.07, dur=1.2):
    out = np.zeros(int((dur + gap * len(notes)) * SR))
    for i, m in enumerate(notes):
        n = int(dur * SR); tt = np.arange(n) / SR; f0 = midi(m)
        s = (np.sin(2 * np.pi * f0 * tt) + 0.35 * np.sin(2 * np.pi * f0 * 2.01 * tt) * np.exp(-tt * 6)) * np.exp(-tt * 3.2)
        j = int(i * gap * SR); out[j:j + n] += s
    return out


def shimmer(dur=0.8):
    out = np.zeros(int(dur * SR))
    for i in range(14):
        n = int(0.4 * SR); tt = np.arange(n) / SR
        s = np.sin(2 * np.pi * midi(86 + rng.integers(0, 12)) * tt) * np.exp(-tt * 9)
        j = int(i / 14 * (dur - 0.4) * SR); out[j:j + n] += s * (0.6 + 0.4 * rng.random())
    return out


def riser(dur=0.6):
    n = int(dur * SR); tt = np.arange(n) / SR
    f = 400 + 900 * (tt / dur) ** 2
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * (tt / dur) ** 2 * 0.6 + lp(rng.standard_normal(n), 3000) * (tt / dur) ** 3 * 0.4


sfx = np.zeros((2, N))
for i, k in enumerate(SCENES[1:]):  # automatic: whoosh peaking at each zoom-through cut
    place(sfx, whoosh(0.5), CUT[k] - 0.3, 0.22, pan=-0.2 if i % 2 else 0.2)
for c in plan.get("sfx", []):
    t0 = anchor(c["at"]) + c.get("off", 0.0)
    ty = c["type"]
    sig = {"whoosh": lambda: whoosh(c.get("dur", 0.5), c.get("bright", 2200)),
           "pop": lambda: pop(c.get("freq", 640), c.get("dur", 0.16)),
           "tick": lambda: tick(c.get("freq", 1900)),
           "tap": tap,
           "chime": lambda: chime(tuple(c.get("notes", (81, 86, 90, 93)))),
           "riser": lambda: riser(c.get("dur", 0.6)),
           "shimmer": lambda: shimmer(c.get("dur", 0.8))}[ty]()
    place(sfx, sig, t0, c.get("gain", 0.2), c.get("pan", 0.0))


# ---------------- VO + ducking + master ----------------
def read_mono(path):
    raw = subprocess.run([FF, "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).astype(np.float64)


vo_path = os.path.join(AUD, "vo.wav")
vo = read_mono(vo_path) if os.path.exists(vo_path) else np.zeros(N)
vo = np.pad(vo, (0, max(0, N - len(vo))))[:N]
act = np.abs(vo) > 10 ** (-40 / 20)
act = np.convolve(act.astype(float), np.ones(int(0.02 * SR)) / int(0.02 * SR), mode="same") > 0.05
g = np.where(act, 10 ** (-6 / 20), 1.0)
duck = np.empty(N); prev = 1.0
a_att, a_rel = np.exp(-1 / (0.06 * SR)), np.exp(-1 / (0.35 * SR))
for i in range(0, N, 480):
    a = a_att if g[i] < prev else a_rel
    prev = g[i] + (prev - g[i]) * (a ** 480)
    duck[i:i + 480] = prev

music_gain, sfx_gain = 10 ** (-7.0 / 20), 10 ** (-7 / 20)
mix = music * music_gain * duck + sfx * sfx_gain
mix[0] += vo; mix[1] += vo
os.makedirs(AUD, exist_ok=True)


def write(path, x):
    tmp = path + ".f32"
    x.T.astype(np.float32).tofile(tmp)
    subprocess.run([FF, "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", tmp, "-c:a", "pcm_s24le", path], check=True)
    os.remove(tmp)


write(os.path.join(AUD, "music.wav"), music * music_gain)
write(os.path.join(AUD, "sfx.wav"), sfx * sfx_gain)
raw_mix = os.path.join(AUD, "_mix_raw.wav")
write(raw_mix, mix)
subprocess.run([FF, "-v", "error", "-y", "-i", raw_mix, "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:linear=true", "-ar", str(SR),
                "-c:a", "pcm_s24le", os.path.join(AUD, "mix.wav")], check=True)
os.remove(raw_mix)
print(f"music {BPM:.1f} BPM, {TOTAL:.2f}s, {len(plan.get('sfx', []))} cue SFX + {len(SCENES) - 1} cut whooshes -> hf/assets/mix.wav")
