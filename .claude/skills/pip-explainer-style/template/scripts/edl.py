"""Edit decision list (source seconds) + word timeline for the picture and audio.
The user already cut the footage themselves, so the whole clip is used untrimmed (one segment).

  SRC_MOV=<talking-head .mov> SRC_DUR=<seconds> /usr/bin/python3 scripts/edl.py
reads analysis/words.json (from scripts/transcribe.py) and writes data/edl.json."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, ".."))
SRC = os.environ.get("SRC_MOV") or os.path.join(ROOT, "SOURCE_FOOTAGE.mov")  # export SRC_MOV=<path to the talking-head .mov>
SEGS = [  # the user delivers footage already cut: use it whole (set the real duration). Only add cuts if the user asks.
    (0.00, float(os.environ.get("SRC_DUR", "92.42"))),
]
TAIL = 2.0  # end-card hold after the last word
EDL = os.path.join(ROOT, "data", "edl.json")


def starts():
    s, out = 0.0, []
    for a, b in SEGS: out.append(s); s += b - a
    return out, s


def to_tl(t):
    st, _ = starts()
    for (a, b), s in zip(SEGS, st):
        if a - 0.05 <= t <= b + 0.05: return s + (t - a)
    return None


if __name__ == "__main__":
    st, total = starts()
    words = json.load(open(os.path.join(ROOT, "analysis", "words.json")))  # from scripts/transcribe.py
    out = []
    for seg in words:
        for w in seg["words"]:
            m = (w["s"] + w["e"]) / 2
            for (a, b), s in zip(SEGS, st):
                if a <= m <= b:
                    out.append({"w": w["w"].strip(), "s": round(max(a, w["s"]) - a + s, 3), "e": round(min(b, w["e"]) - a + s, 3), "src": w["s"]})
    os.makedirs(os.path.dirname(EDL), exist_ok=True)
    json.dump({"segs": [{"in": a, "out": b, "at": round(s, 3)} for (a, b), s in zip(SEGS, st)], "speechEnd": round(total, 3),
               "total": round(total + TAIL, 3), "words": out}, open(EDL, "w"), ensure_ascii=False, indent=1)
    print("speech", round(total, 3), "total", round(total + TAIL, 3))
    for w in out: print(f'{w["s"]:6.2f} {w["w"]}')
