"""BM captions: 1-3 words (<= 16 characters) per chunk, broken at punctuation or pauses > 0.35 s.
Not-yet-spoken words sit at 35 % opacity, keywords are yellow. PER VIDEO: edit FIX / JOIN / KEY / is_key()."""
import re
from timing import T, WORDS

# On-screen spelling fixes (Whisper writes the spoken form; captions use standard BM / the terms as said).
FIX = {"mekanism": "mekanisme", "100": "100%", "%": "", "-baru": "", "-buih": "", "-satu": "", "bayarkan": "bayangkan", "-kick": ""}
JOIN = {"Baru": "Baru-baru", "buih": "buih-buih", "satu": "satu-satu"}  # hyphenated reduplication stays joined
DROP = set()  # word start times (f"{s:.2f}") to drop, e.g. cut-edge artefacts. The footage is used untrimmed here.
KEY = re.compile(r"^(100%|ai|trafik|konten|closing|conversion|brand|trust|fyp|percaya|sebenar|result|testimoni|chatbot|"
                 r"blueprint|fundamental|buih-buih|corong|wajib|3)$", re.I)
UNCLEAR = {"pre"}  # a genuinely unclear word: not guessed, the chunk ends with an ellipsis instead


def is_key(text, s):
    return bool(KEY.match(text)) or (T["takBoleh"] - 0.1 <= s < T["takBoleh"] + 0.5) or \
        (text.lower() == "tak" and abs(s - T["takAda"]) < 0.1)


def tokens():
    out = []
    for i, w in enumerate(WORDS):
        if f'{w["s"]:.2f}' in DROP: continue
        raw = re.sub(r"[,.?]", "", w["w"])
        text = FIX.get(raw.lower(), FIX.get(raw, raw))
        if raw in JOIN and i + 1 < len(WORDS) and WORDS[i + 1]["w"].startswith("-"): text = JOIN[raw]
        if raw in UNCLEAR and out:
            out[-1]["text"] += "…"; out[-1]["e"] = w["e"]; out[-1]["brk"] = True; continue
        if not text:
            if out: out[-1]["e"] = w["e"]
            continue
        punct = w["w"][-1] if re.search(r"[,.?]$", w["w"]) else ""
        out.append({"text": text + ("?" if punct == "?" else ""), "s": w["s"], "e": w["e"], "key": is_key(text, w["s"]), "brk": bool(punct)})
    return out


def chunks():
    res, cur = [], []
    for tk in tokens():
        ln = len(" ".join(c["text"] for c in cur)) + len(tk["text"])
        if cur and (len(cur) >= 3 or ln > 16 or tk["s"] - cur[-1]["e"] > 0.35):
            res.append(cur); cur = []
        cur.append(tk)
        if tk["brk"]: res.append(cur); cur = []
    if cur: res.append(cur)
    out = []
    for k, c in enumerate(res):
        s = c[0]["s"]; nxt = res[k + 1][0]["s"] if k + 1 < len(res) else 1e9
        end = min(nxt, c[-1]["e"] + 0.45) - 0.02  # hold until the next chunk or 0.45 s after the last word
        out.append({"toks": c, "s": s - 0.04, "end": end})
    return out
