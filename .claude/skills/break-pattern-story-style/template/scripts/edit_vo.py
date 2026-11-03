"""Tidy the raw VO: cut long silences, keep breaths + short phrase pauses, never touch speech.
Raw timings come from the energy map + large-v3 transcript (audio/transcript_raw.json).
Units are phrases that stay untouched internally (inner pauses kept as recorded); only the gaps *between* units are re-timed.
Output: audio/VO_Break_Pattern_EDITED.wav (48 kHz mono 24-bit) + audio/vo_cues.json (output-timeline cues)."""
import json, subprocess
import numpy as np, scipy.io.wavfile as wav, scipy.signal as sg

SR = 48000
raw = wav.read("audio/vo_raw.wav")[1].astype(np.float64) / 32768

# --- speech envelope (10 ms) --------------------------------------------------
hop = SR // 100
n = len(raw) // hop
env = 20 * np.log10(np.sqrt((raw[:n * hop].reshape(n, hop) ** 2).mean(1)) + 1e-9)
THR = -33.0


def bounds(approx_a, approx_b, slack=0.35):
    """refine unit start/end to the true speech edges inside +-slack of the approximations"""
    i0, i1 = int((approx_a - slack) * 100), int((approx_b + slack) * 100)
    act = np.where(env[i0:i1] > THR)[0]
    return (i0 + act[0]) / 100, (i0 + act[-1] + 1) / 100


# unit: (label, approx start, approx end, text, gap_before_target [s of silence between previous speech end and this speech start])
UNITS = [
    ("galeri",   1.20,  5.70, "Cuba tengok balik dekat galeri tu, berapa banyak footage yang tak sempat nak edit.", 0.0),
    ("potong",  15.80, 20.50, "Nak potong video, nak letak subtitle, nak cari b-roll, cari visual.", 0.95),
    ("music",   21.50, 23.90, "Belum masuk music dan juga sound effect lagi.", 0.60),
    ("tigajam", 25.00, 27.30, "Sedar-sedar dah 3 jam depan laptop.", 0.85),
    ("larat",   28.35, 30.95, "Video tak siap. Nak post pun dah tak larat.", 0.85),
    ("panduan", 33.30, 35.60, "Dalam panduan Video Guna Kod", 1.20),
    ("belajar", 37.90, 45.95, "VGC. Korang akan belajar macam mana nak automate editing guna ChatGPT ataupun Claude.", 0.75),
    ("campak",  49.00, 51.45, "Campak footage, tidur, dah siap.", 1.00),
    ("demo",    53.25, 58.05, "Daripada rakaman yang raw macam ni, terus jadi video macam ni.", 0.85),
    ("ada",     60.40, 63.35, "Ada tutorial. Ada template. Ada group support.", None),   # gap set by DEMO_GAP below
    ("basic",   68.90, 72.45, "Belajar dari basic sampai advance. Jadi expert.", 1.00),
    ("posting", 77.90, 79.40, "Nak mula posting hari-hari?", 1.15),
    ("klik",    81.20, 82.80, "Klik link, daftar sekarang.", 0.85),
]
DEMO_GAP = 6.2      # silence reserved after "terus jadi video macam ni" for the before/after demo (case-study audio sits in it)
LEAD_IN = 0.35      # video starts this long before the first word
TAIL = 2.4          # CTA hold after the last word
PRE, POST = 0.45, 0.22   # raw margin kept around each unit (carries breath / natural decay)
XF = 0.012          # crossfade for every join (inside silence, so it is click-free)

# room tone from a genuinely silent stretch of the take
room = raw[int(7.0 * SR):int(10.0 * SR)].copy()


def tone(dur):
    n_ = int(round(dur * SR))
    if n_ <= 0:
        return np.zeros(0)
    reps = int(np.ceil(n_ / len(room))) + 1
    # tile with 50 ms crossfades
    out = room.copy(); xf = int(0.05 * SR); ramp = np.linspace(0, 1, xf)
    for _ in range(reps - 1):
        out = np.concatenate([out[:-xf], out[-xf:] * (1 - ramp) + room[:xf] * ramp, room[xf:]])
    return out[:n_]


out = tone(LEAD_IN - 0.0)
cues = []
prev_end_out = None
for k, (lab, a, b, text, gap) in enumerate(UNITS):
    s, e = bounds(a, b)
    # margin kept from raw: bounded so we never run into the neighbouring unit's speech
    pre = min(PRE, 0.60)
    post = POST
    seg = raw[int((s - pre) * SR):int((e + post) * SR)].copy()
    if gap is None:
        gap = DEMO_GAP
    if k == 0:
        # first unit: lead-in already placed; skip pre-roll (raw has nothing before 1.1 s except room noise)
        seg = raw[int((s - 0.20) * SR):int((e + post) * SR)].copy()
        out = np.concatenate([tone(LEAD_IN - 0.20), seg])
        start_out = LEAD_IN
    else:
        # silence already contributed by previous unit's post margin + this unit's pre margin
        have = POST + pre
        extra = max(0.0, gap - have)
        # trim if the margins alone exceed the target gap
        trim = max(0.0, have - gap)
        if trim > 0:
            cut_pre = min(trim, pre - 0.10)
            seg = seg[int(cut_pre * SR):]
            pre -= cut_pre
        fill = tone(extra + 2 * XF)
        # equal-power crossfades at both joins
        def xfade(a_, b_):
            m = int(XF * SR); r = np.linspace(0, 1, m)
            return np.concatenate([a_[:-m], a_[-m:] * np.sqrt(1 - r) + b_[:m] * np.sqrt(r), b_[m:]])
        out = xfade(out, fill) if extra > 0 else out
        out = xfade(out, seg) if extra > 0 else xfade(out, seg)
        start_out = (len(out) - len(seg)) / SR + pre
    end_out = start_out + (e - s)
    cues.append({"id": lab, "text": text, "raw_start": s, "raw_end": e, "start": round(start_out, 3), "end": round(end_out, 3)})

out = np.concatenate([out, tone(TAIL)])

# --- word cues: whisper end-times are reliable; start = previous end (or unit start) ------------------
words = []
for seg in json.load(open("audio/transcript_raw.json")):
    for w_ in seg["words"]:
        words.append((w_["w"].strip(), w_["s"], w_["e"]))
for c in cues:
    ws = [(t, ee) for (t, s_, ee) in words if c["raw_start"] - 0.35 <= ee <= c["raw_end"] + 0.35 and t.lower() not in ("terima", "kasih", "kerana", "menonton!")]
    c["words"] = [{"w": t, "end": round(c["start"] + (ee - c["raw_start"]), 3)} for t, ee in ws]

# --- processing: HPF, gentle denoise (ffmpeg afftdn), level --------------------------------------------
sos = sg.butter(2, 75 / (SR / 2), "high", output="sos")
out = sg.sosfilt(sos, out)
tmp = "audio/_vo_pre.wav"
wav.write(tmp, SR, np.int16(np.clip(out, -1, 1) * 32767))
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-af", "afftdn=nr=5:nf=-45:nt=w", "-ar", str(SR), "audio/_vo_dn.wav"], check=True)
y = wav.read("audio/_vo_dn.wav")[1].astype(np.float64) / 32768
peak = np.abs(y).max()
y *= 10 ** (-2.0 / 20) / peak          # peak -2 dBFS, no compression, no speed change
wav.write("audio/VO_Break_Pattern_EDITED.wav", SR, np.int32(np.clip(y, -1, 1) * (2 ** 31 - 1)))
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "audio/VO_Break_Pattern_EDITED.wav", "-c:a", "aac", "-b:a", "256k", "audio/VO_Break_Pattern_EDITED.m4a"], check=True)
json.dump({"duration": len(y) / SR, "demo_gap": DEMO_GAP, "units": cues}, open("audio/vo_cues.json", "w"), ensure_ascii=False, indent=1)
print(f"edited VO {len(y)/SR:.2f}s  (raw {len(raw)/SR:.2f}s)")
for c in cues:
    print(f"{c['start']:7.2f}-{c['end']:7.2f}  {c['id']:8s} {c['text']}")
