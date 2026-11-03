# Synthesise unique SFX (one seed per cue, never reused), mix voice + song + SFX -> hf/assets/mix.wav
# Voice untouched apart from gain/limiting; song at original tempo ~20 LU under the voice.
import json, os, re, subprocess, wave
import numpy as np
from scipy import signal

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 48000
TOTAL = 48.1
END_CARD = 45.40
SONG = os.environ.get('SONG', os.path.join(ROOT, 'src/song.mp3'))   # the user's supplied track
T = json.load(open(os.path.join(ROOT, 'work/times.json')))


def rd(path):
    w = wave.open(path); n = w.getnchannels()
    x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32).reshape(-1, n) / 32768
    return x if n == 2 else np.repeat(x, 2, 1)


def wr(path, x):
    x = np.clip(x, -1, 1)
    w = wave.open(path, 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((x * 32767).astype(np.int16).tobytes()); w.close()


def lufs(path):
    o = subprocess.run(['ffmpeg', '-hide_banner', '-i', path, '-af', 'ebur128', '-f', 'null', '-'],
                       capture_output=True, text=True).stderr
    return float(re.findall(r'I:\s+(-?[\d.]+) LUFS', o)[-1])


# ---------- synth helpers ----------
def env_ad(n, a, d, curve=4.0):
    t = np.arange(n) / SR
    e = np.minimum(t / max(a, 1e-4), 1.0) * np.exp(-np.maximum(t - a, 0) * curve / max(d, 1e-4))
    return e


def bp(x, lo, hi, order=2):
    lo, hi = max(lo, 20), min(hi, SR / 2 - 100)
    return signal.sosfilt(signal.butter(order, [lo, hi], 'bandpass', fs=SR, output='sos'), x)


def lp(x, f, order=2):
    return signal.sosfilt(signal.butter(order, min(f, SR / 2 - 100), 'lowpass', fs=SR, output='sos'), x)


def hp(x, f, order=2):
    return signal.sosfilt(signal.butter(order, f, 'highpass', fs=SR, output='sos'), x)


def sweep_noise(r, dur, f0, f1, q=0.5, blocks=48):
    """Noise through a band that moves from f0 to f1 (block-wise, crossfaded)."""
    n = int(dur * SR); x = r.standard_normal(n); out = np.zeros(n)
    edges = np.linspace(0, n, blocks + 1).astype(int)
    for i in range(blocks):
        f = f0 * (f1 / f0) ** (i / (blocks - 1))
        a, b = max(edges[i] - 512, 0), min(edges[i + 1] + 512, n)
        seg = bp(x[a:b], f * (1 - q / 2), f * (1 + q / 2))
        win = np.ones(b - a)
        out[a:b] += seg * win
    return out / (np.abs(out).max() + 1e-9)


def stereo(m, pan=0.0, width=0.0, r=None):
    l, rr = m * np.sqrt((1 - pan) / 2), m * np.sqrt((1 + pan) / 2)
    if width and r is not None:
        d = int(SR * 0.004 * width)
        rr = np.concatenate([np.zeros(d), rr[:-d]]) if d else rr
    return np.stack([l, rr], 1)


def pan_sweep(m, p0, p1):
    p = np.linspace(p0, p1, len(m))
    return np.stack([m * np.sqrt((1 - p) / 2), m * np.sqrt((1 + p) / 2)], 1)


# ---------- families (each call = a new, unique sound) ----------
def riser(r, dur):
    n = int(dur * SR); t = np.arange(n) / SR
    nz = sweep_noise(r, dur, r.uniform(250, 450), r.uniform(5000, 8000), 0.6)
    f = r.uniform(180, 260) * (r.uniform(5, 8)) ** (t / dur)
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.35 + np.sin(2 * np.pi * np.cumsum(f * 1.5) / SR) * 0.15
    e = (t / dur) ** r.uniform(1.8, 2.6)
    m = (nz * 0.8 + tone) * e
    m[-int(0.012 * SR):] *= np.linspace(1, 0, int(0.012 * SR))
    return pan_sweep(m, r.uniform(-.4, -.1), r.uniform(.1, .4))


def pop(r):
    dur = r.uniform(0.07, 0.12); n = int(dur * SR); t = np.arange(n) / SR
    f0, f1 = r.uniform(500, 1100), r.uniform(150, 300)
    f = f1 + (f0 - f1) * np.exp(-t * r.uniform(35, 60))
    m = np.sin(2 * np.pi * np.cumsum(f) / SR) * env_ad(n, 0.002, dur, 5)
    m += hp(r.standard_normal(n), 2000) * env_ad(n, 0.0005, 0.01, 6) * 0.25
    return stereo(m, r.uniform(-.3, .3))


def swoosh(r, dur=None):
    dur = dur or r.uniform(0.28, 0.5)
    m = sweep_noise(r, dur, r.uniform(600, 1200), r.uniform(2500, 5000), 0.9)
    n = len(m); t = np.arange(n) / n
    pk = r.uniform(0.45, 0.65)
    e = np.where(t < pk, (t / pk) ** 2, np.exp(-(t - pk) * r.uniform(6, 10)))
    a, b = r.uniform(-.7, -.3), r.uniform(.3, .7)
    if r.random() < .5: a, b = b, a
    return pan_sweep(m * e, a, b)


def thud(r, dur=None):
    dur = dur or r.uniform(0.25, 0.4); n = int(dur * SR); t = np.arange(n) / SR
    f = r.uniform(42, 55) + r.uniform(40, 70) * np.exp(-t * 25)
    m = np.sin(2 * np.pi * np.cumsum(f) / SR) * env_ad(n, 0.002, dur, 5)
    m += lp(r.standard_normal(n), 900) * env_ad(n, 0.001, 0.05, 6) * 0.4
    return stereo(m, r.uniform(-.1, .1))


def whoosh_impact(r):
    s = swoosh(r, r.uniform(0.35, 0.55)); h = thud(r) * 0.9
    out = np.zeros((len(s) + len(h), 2)); k = int(len(s) * 0.62)
    out[:len(s)] += s; out[k:k + len(h)] += h
    return out[:k + len(h)], k / SR  # impact offset


def click(r, double=True):
    def one():
        n = int(r.uniform(0.006, 0.012) * SR)
        m = bp(r.standard_normal(n), r.uniform(1800, 3000), r.uniform(5000, 7000)) * env_ad(n, 0.0003, 0.004, 6)
        t = np.arange(n) / SR
        m += np.sin(2 * np.pi * r.uniform(2500, 4200) * t) * env_ad(n, 0.0002, 0.003, 6) * 0.6
        return m
    a = one()
    if not double: return stereo(a, r.uniform(-.2, .2))
    gap = int(r.uniform(0.06, 0.09) * SR); b = one() * 0.6
    m = np.zeros(gap + len(b)); m[:len(a)] += a; m[gap:gap + len(b)] += b
    return stereo(m, r.uniform(-.2, .2))


def keyboard(r, dur):
    n = int(dur * SR); m = np.zeros(n + SR // 10); t = 0.0
    while t < dur:
        k = int(t * SR); ln = int(r.uniform(0.01, 0.02) * SR)
        s = bp(r.standard_normal(ln), r.uniform(900, 1800), r.uniform(4000, 6500)) * env_ad(ln, 0.0004, 0.008, 6)
        s += lp(r.standard_normal(ln), 400) * env_ad(ln, 0.0005, 0.01, 6) * 0.5
        m[k:k + ln] += s * r.uniform(0.6, 1.0)
        t += r.uniform(0.055, 0.13) if r.random() > .1 else r.uniform(0.2, 0.3)
    return stereo(m, r.uniform(-.15, .15))


def ting(r, base=None):
    f = base or r.uniform(1300, 2200); dur = r.uniform(0.6, 0.9); n = int(dur * SR); t = np.arange(n) / SR
    m = sum(a * np.sin(2 * np.pi * f * k * t) * np.exp(-t * dcy) for k, a, dcy in
            [(1, 1, 5), (2.76, .35, 9), (5.4, .15, 14), (r.uniform(3.9, 4.3), .1, 12)])
    m *= env_ad(n, 0.001, dur, 0.1)
    return stereo(m, r.uniform(-.25, .25))


def sparkle(r):
    dur = r.uniform(0.7, 1.0); n = int(dur * SR); m = np.zeros((n, 2))
    for _ in range(r.integers(10, 16)):
        k = int(r.uniform(0, dur * 0.7) * SR); ln = int(0.18 * SR); t = np.arange(ln) / SR
        s = np.sin(2 * np.pi * r.uniform(3000, 7500) * t) * np.exp(-t * r.uniform(18, 30)) * r.uniform(.3, 1)
        p = r.uniform(-.8, .8); m[k:k + ln] += stereo(s, p)[:max(0, min(ln, n - k))]
    return m * np.linspace(1, .4, n)[:, None]


def paper(r):
    dur = r.uniform(0.2, 0.32); n = int(dur * SR); t = np.arange(n) / n
    m = bp(r.standard_normal(n), r.uniform(700, 1100), r.uniform(4000, 6000)) * np.sin(np.pi * t) ** 1.5
    m *= 1 + 0.5 * (r.random(n) > .97)
    return pan_sweep(m, r.uniform(.2, .5), r.uniform(-.2, 0))


def shutter(r):
    a = click(r, False); gap = int(r.uniform(0.05, 0.08) * SR); b = click(r, False)
    n = int(0.06 * SR); nz = stereo(bp(r.standard_normal(n), 1500, 7000) * env_ad(n, 0.002, 0.05, 5) * 0.4)
    out = np.zeros((gap + len(b) + n, 2)); out[:len(a)] += a; out[:n] += nz; out[gap:gap + len(b)] += b * 1.2
    return out


def shing(r):
    dur = r.uniform(0.9, 1.2); n = int(dur * SR); t = np.arange(n) / SR
    f = r.uniform(2400, 3000) * (1 + 0.08 * t / dur)
    m = sum(a * np.sin(2 * np.pi * np.cumsum(f * k) / SR) * np.exp(-t * d) for k, a, d in
            [(1, 1, 3.5), (1.53, .5, 5), (2.11, .3, 7), (2.94, .2, 9)])
    m += hp(sweep_noise(r, dur, 3000, 9000, 0.8), 3000) * np.exp(-t * 12) * 0.8
    m *= env_ad(n, 0.004, dur, 0.1)
    return pan_sweep(m, -.4, .4)


def blip(r):
    out = []
    for f in (r.uniform(520, 600), r.uniform(330, 380)):
        n = int(0.09 * SR); t = np.arange(n) / SR
        s = signal.square(2 * np.pi * f * t, 0.5) * 0.4 + np.sin(2 * np.pi * f * t)
        out.append(lp(s, 2500) * env_ad(n, 0.003, 0.09, 3)); out.append(np.zeros(int(0.03 * SR)))
    return stereo(np.concatenate(out), r.uniform(-.1, .1))


def tick_roll(r, times):
    span = times[-1] + 0.05; n = int(span * SR); m = np.zeros((n, 2))
    for i, tt in enumerate(times):
        c = click(r, False) * (0.7 + 0.3 * i / len(times)); k = int(tt * SR)
        m[k:k + len(c)] += c[:n - k]
    return m


# ---------- cue sheet (time, family, level dB rel. family target) ----------
def cues():
    t = T; C = []
    def add(at, fam, *a, gain=0.0, align='start'):
        C.append((at, fam, a, gain, align))
    # swooshes only on the three chapter cards + the knife slice; everything else is click / ting / pop / paper
    add(0.29, 'click', gain=-2)                        # title in (video starts at 0.267 after the trim)
    add(t['ilmu'] - 0.02, 'pop')
    add(t['slide'] - 0.02, 'pop', gain=1)
    add(t['bayangkan'] - 0.02, 'whoosh_impact', align='impact')   # chapter card 1
    add(t['macam'] + 0.02, 'paper')                    # slide cards drop in
    add(t['macam'] + 0.20, 'pop', gain=-3)
    add(t['macam'] + 0.38, 'paper', gain=-1)
    add(t['transform'], 'riser', 0.55, align='end', gain=-2)
    add(t['transform'] + 0.02, 'thud', gain=-3)
    add(t['motion'] + 0.05, 'ting', 1500)
    add(t['education'] - 0.12, 'click', gain=-3)       # push to next slide video
    add(t['education'] + 0.05, 'ting', 1680)
    add(t['over'] - 0.14, 'click', gain=-3)
    add(t['over'] + 0.02, 'ting', 1880)
    add(t['animation'] + 0.02, 'pop', gain=-2)
    add(12.58, 'sparkle', gain=-3)                     # triptych
    add(14.95, 'click', gain=-3)                       # pelajar faham
    add(15.50, 'ting', 1600)                           # konteks
    add(t['sebab'] - 0.02, 'whoosh_impact', align='impact')        # chapter card 2
    add(t['pisau'] - 0.08, 'shing', gain=-2)
    add(t['betul'] + 0.25, 'ting', 1750)
    add(t['okey'], 'swoosh', 0.22, gain=-2)            # clean slice
    add(t['salah'] - 0.08, 'thud', gain=0)             # cave
    add(t['salah'] + 0.45, 'blip', gain=-3)
    add(t['kalau'] - 0.12, 'click', gain=-1)           # bg swap to bedroom
    add(t['cari'], 'keyboard', 1.25, gain=-2)
    add(24.42, 'thud', 0.22, gain=-6)
    add(25.02, 'thud', 0.22, gain=-6)
    add(25.62, 'click', gain=-4)
    add(t['chapter'], 'thud', 0.3, gain=-5)
    add(t['sekarang'] - 0.15, 'click', gain=-1)        # bg swap to studio
    add(t['control'], 'riser', 0.65, align='end', gain=-3)
    add(t['control'], 'click', gain=-1)                # Prompt Vault in
    add(30.05, 'pop', gain=-4)
    add(30.58, 'click', gain=-3)
    add(31.22, 'pop', gain=-4)                         # tree panel
    add(31.40, 'click', False, gain=-5)
    add(t['editing'] + 0.12, 'blip', gain=-3)
    add(t['workflow'], 'ting', 2300)
    add(t['sebab2'] - 0.04, 'shutter', gain=-2)        # dashboard
    add(36.82, 'whoosh_impact', align='impact', gain=-1)          # chapter card 3
    add(t['code'] + 0.05, 'sparkle', gain=-2)
    add(38.30, 'tick_roll', [i * 0.11 for i in range(9)], gain=-3)  # module montage
    add(t['expert'], 'riser', 0.8, align='end', gain=-3)
    add(t['expert'] + 0.02, 'sparkle', gain=-1)
    add(t['claude'] - 0.02, 'pop', gain=-2)
    add(t['chat'] - 0.02, 'pop', gain=-1)
    add(END_CARD + 0.05, 'ting', 1150, gain=-1)
    add(END_CARD + 0.40, 'sparkle', gain=-3)
    return C


TARGET = {  # RMS target per family, dB below voice RMS
    'swoosh': -11, 'pop': -12, 'whoosh_impact': -9, 'paper': -14, 'riser': -13, 'ting': -15, 'sparkle': -17,
    'click': -14, 'shing': -14, 'thud': -10, 'blip': -14, 'keyboard': -16, 'shutter': -13, 'tick_roll': -15}


def rms_db(x):
    x = x[np.abs(x).max(1) > np.abs(x).max() * 0.05] if len(x) else x
    return 20 * np.log10(np.sqrt((x ** 2).mean()) + 1e-9)


def main():
    os.makedirs(os.path.join(ROOT, 'work'), exist_ok=True)
    voice = rd(os.path.join(ROOT, 'work/voice.wav'))
    n = int(TOTAL * SR); mix = np.zeros((n, 2)); vo = np.zeros((n, 2)); vo[:min(n, len(voice))] = voice[:n]
    vr = rms_db(vo)

    # song: original tempo, from 0 s; level set by measured loudness
    song_path = os.path.join(ROOT, 'work/song48.wav')
    if not os.path.exists(song_path):
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', SONG, '-ac', '2', '-ar', str(SR), song_path], check=True)
    song = rd(song_path)[:n]; song = np.pad(song, ((0, n - len(song)), (0, 0)))
    wr(os.path.join(ROOT, 'work/_s.wav'), song); wr(os.path.join(ROOT, 'work/_v.wav'), vo)
    lv, ls = lufs(os.path.join(ROOT, 'work/_v.wav')), lufs(os.path.join(ROOT, 'work/_s.wav'))
    g = 10 ** ((lv - 20 - ls) / 20)
    t = np.arange(n) / SR
    ramp = np.clip(t / 0.3, 0, 1)
    lift = np.interp(t, [0, END_CARD - 0.1, END_CARD + 0.4, TOTAL - 1.3, TOTAL], [1, 1, 2.2, 2.2, 0])
    mix += song * (g * ramp * lift)[:, None]

    used = set(); log = []
    for i, (at, fam, args, gain, align) in enumerate(cues()):
        r = np.random.default_rng(7000 + i * 97)
        res = FAM[fam](r, *args)
        s, imp = (res if isinstance(res, tuple) else (res, 0.0))
        key = (fam, i); assert key not in used; used.add(key)
        s = s * 10 ** ((vr + TARGET[fam] + gain - rms_db(s)) / 20)
        start = at - (imp if align == 'impact' else (len(s) / SR if align == 'end' else 0))
        k = int(max(start, 0) * SR); e = min(n, k + len(s))
        mix[k:e] += s[:e - k]; log.append(f'{start:6.2f} {fam}')

    mix += vo
    wr(os.path.join(ROOT, 'work/mix_raw.wav'), mix * 0.5)
    out = os.path.join(ROOT, 'hf/assets/mix.wav')
    # +6 dB back (from the 0.5 headroom) then lift to about -14 LUFS with a true-peak limiter
    lm = lufs(os.path.join(ROOT, 'work/mix_raw.wav'))
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', os.path.join(ROOT, 'work/mix_raw.wav'), '-af',
                    f'volume={-14.0 - lm:.2f}dB,alimiter=limit=0.89:attack=2:release=60:level=false',
                    '-ar', str(SR), '-c:a', 'pcm_s16le', out], check=True)
    open(os.path.join(ROOT, 'work/sfx_cues.txt'), 'w').write('\n'.join(log))
    print(f'voice {lv:.1f} LUFS, song {ls:.1f} -> gain {20*np.log10(g):.1f} dB; {len(log)} unique SFX; final {lufs(out):.1f} LUFS')


FAM = dict(riser=riser, pop=pop, swoosh=swoosh, thud=thud, whoosh_impact=whoosh_impact, click=click,
           keyboard=keyboard, ting=ting, sparkle=sparkle, paper=paper, shutter=shutter, shing=shing, blip=blip,
           tick_roll=tick_roll)

if __name__ == '__main__':
    main()
