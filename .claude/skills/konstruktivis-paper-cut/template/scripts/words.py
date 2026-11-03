# Whisper word list -> envelope-snapped one-word captions (hf/words.json)
import json, re, wave, numpy as np, sys, os
P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
raw = json.load(open(f"{P}/scripts/words_raw.json"))
w = wave.open(f"{P}/hf/assets/vo_src.wav"); sr = w.getframerate()
x = np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, 2).mean(1) / 32768
hop = sr // 100; n = len(x) // hop
db = 20 * np.log10(np.sqrt((x[:n*hop].reshape(n, hop) ** 2).mean(1)) + 1e-6)

# merge reduplication parts ("tangan" + "-tangan")
words = []
for a, b, t in raw:
    if t.startswith("-") and words:
        words[-1][1] = b; words[-1][2] += t
    else:
        words.append([a, b, t])
# fixes: "sendiri" missed by Whisper; Bayangkan really starts 9.24
fix = {"vault.": "Vault", "ChatGPT": "ChatGPT"}
out = []
for a, b, t in words:
    if t == "Bayangkan" and abs(a - 8.92) < 0.05:
        out.append([8.93, 9.12, "sendiri"]); a = 9.24
    out.append([a, b, fix.get(t, t)])

def snap(t):
    i0, i1 = max(0, int((t - 0.18) * 100)), min(n - 1, int((t + 0.14) * 100))
    seg = db[i0:i1]
    if len(seg) < 3: return t
    k = int(seg.argmin()); dip = seg[k]
    if dip > db[i0:i1+20].max() - 12: return t   # no real gap: keep Whisper time
    for j in range(i0 + k, i1 + 15):
        if db[j] > dip + 9: return round(j / 100, 2)
    return t

caps = []
for i, (a, b, t) in enumerate(out):
    s = min(max(snap(a), a - 0.05), a + 0.10)          # snap, but never far from Whisper
    if caps and s < caps[-1]["t"] + 0.13: s = caps[-1]["t"] + 0.13   # no sub-0.13 s flashes
    s = round(s, 2)
    caps.append({"t": s, "w": re.sub(r"[.,?!]", "", t).upper()})
json.dump(caps, open(f"{P}/hf/words.json", "w"), ensure_ascii=False)
print(len(caps)); print(" ".join(f'{c["t"]:.2f}|{c["w"]}' for c in caps))
