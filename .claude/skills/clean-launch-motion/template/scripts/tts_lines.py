"""Clean Launch Motion VO, step 1: generate the voice LINE BY LINE (one ElevenLabs request per script line) with the
neighbouring lines passed as previous_text / next_text, so intonation flows while each chunk starts and ends in
natural silence. Nothing is ever cut inside a chunk (inserting silence inside a continuous take caused audible
"sangkut" hitches in the first Belajar AI version, and speed 1.0 dragged).

Several seeds per line; the smoother candidate is chosen automatically:
  - alignment text must equal the locked line exactly
  - penalise internal pauses > 0.28 s not at punctuation (hesitations)
  - penalise words abnormally long for their length (drawl)
  - penalise pitch far from the median of all candidates (keeps one consistent voice)

The API key is the STUDENT'S OWN, read by the elevenlabs-voiceover skill (env ELEVENLABS_API_KEY or the macOS
Keychain entry made by `python3 .claude/skills/elevenlabs-voiceover/scripts/voiceover.py setup`). It is never
printed, stored here or passed on the command line. Costs ElevenLabs credits (~chars x seeds); existing chunks are reused.

usage: /usr/bin/python3 scripts/tts_lines.py   -> vo/takes/lines/line_XX_seedS.mp3 + .align.json + selection.json
"""
import base64, json, os, subprocess, sys
import numpy as np
from common import PROJ, ffmpeg, load_plan, script_lines


def find_voiceover():
    """voiceover.py from the elevenlabs-voiceover skill: $VOICEOVER_PY, then the nearest .claude/skills up the tree, then ~/.claude/skills."""
    cands = [os.environ.get("VOICEOVER_PY", "")]
    d = PROJ
    while True:
        cands.append(os.path.join(d, ".claude", "skills", "elevenlabs-voiceover", "scripts", "voiceover.py"))
        if os.path.dirname(d) == d:
            break
        d = os.path.dirname(d)
    cands.append(os.path.expanduser("~/.claude/skills/elevenlabs-voiceover/scripts/voiceover.py"))
    for c in cands:
        if c and os.path.isfile(c):
            return c
    raise SystemExit("elevenlabs-voiceover skill not found (needs .claude/skills/elevenlabs-voiceover/scripts/voiceover.py)")


VOPY = find_voiceover()
sys.path.insert(0, os.path.dirname(VOPY))
import voiceover as vo  # noqa: E402

plan = load_plan()
V = plan["voice"]
OUT = os.path.join(PROJ, "vo", "takes", "lines")
FF = ffmpeg()
os.makedirs(OUT, exist_ok=True)

lines = script_lines(plan)
assert len(lines) == len(plan["line_scene"]), f"script has {len(lines)} lines but plan.line_scene has {len(plan['line_scene'])}"
key = vo.get_key()  # exits with setup instructions if the student has no key yet
assert V.get("id") and not V["id"].startswith("PASTE_"), "Set plan.voice.id to a voice on your own ElevenLabs account (run voiceover.py voices to list them)."
meta = vo.request("GET", f"/v1/voices/{V['id']}", key, None)
assert meta.get("name", "").startswith(V.get("name_prefix", "")), (
    f"voice identity check failed: id {V['id']} is '{meta.get('name')}', expected a name starting '{V.get('name_prefix')}'. "
    "Set plan.voice.id / name_prefix to a voice on your own ElevenLabs account; never swap voices silently.")


def words_from(al):
    out, cur = [], None
    for c, s, e in zip(al["characters"], al["character_start_times_seconds"], al["character_end_times_seconds"]):
        if c.isspace():
            if cur: out.append(cur); cur = None
            continue
        if cur is None: cur = {"w": "", "s": s, "e": e}
        cur["w"] += c; cur["e"] = e
    if cur: out.append(cur)
    return out


def analyse(path, words):
    raw = subprocess.run([FF, "-v", "error", "-i", path, "-ac", "1", "-ar", "16000", "-f", "f32le", "-"], capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32).astype(np.float64); sr, hop = 16000, 160
    db = np.array([20 * np.log10(np.sqrt(np.mean(x[i * hop:(i + 1) * hop] ** 2)) + 1e-9) for i in range(len(x) // hop)])
    punct_ends = [w["e"] for w in words if w["w"][-1] in ".,?!…—"]
    s0, e0 = words[0]["s"], words[-1]["e"]
    pauses, run = [], None
    for i, d in enumerate(db):
        t = i * hop / sr
        if s0 + 0.05 < t < e0 - 0.4 and d < -42:   # the last word's alignment often runs into trailing silence
            run = t if run is None else run
        elif run is not None:
            if t - run > 0.28 and not any(abs(run - p) < 0.25 for p in punct_ends):
                pauses.append((round(run, 2), round(t - run, 2)))
            run = None
    long_words = [(w["w"], round(w["e"] - w["s"], 2)) for w in words[:-1]
                  if (w["e"] - w["s"]) > 0.16 + 0.085 * len(w["w"].strip(".,?!…—")) and w["w"][-1] not in "…—"]
    f0 = []
    for i in range(0, len(x) - 640, 320):
        f = x[i:i + 640]
        if np.sqrt(np.mean(f ** 2)) < 0.02: continue
        f = f - f.mean(); ac = np.correlate(f, f, "full")[639:]
        k = sr // 300 + int(np.argmax(ac[sr // 300:sr // 70]))
        if ac[k] / ac[0] > 0.45: f0.append(sr / k)
    return {"pauses": pauses, "long_words": long_words, "f0": float(np.median(f0)) if f0 else 0.0,
            "rate": round(len(words) / max(0.1, e0 - s0), 2)}


results = []
for i, line in enumerate(lines):
    prev_t = " ".join(lines[max(0, i - 2):i]) or None
    next_t = lines[i + 1] if i + 1 < len(lines) else None
    cands = []
    for seed in V.get("seeds", [11, 23]):
        base = os.path.join(OUT, f"line_{i + 1:02d}_seed{seed}")
        cached = os.path.exists(base + ".align.json") and json.load(open(base + ".align.json", encoding="utf-8")).get("text") == line
        if not cached:
            body = {"text": line, "model_id": V["model"], "language_code": V.get("language", "ms"), "voice_settings": V["settings"], "seed": seed}
            if prev_t: body["previous_text"] = prev_t
            if next_t: body["next_text"] = next_t
            res = vo.request("POST", f"/v1/text-to-speech/{V['id']}/with-timestamps?output_format=mp3_44100_128", key, body)
            open(base + ".mp3", "wb").write(base64.b64decode(res["audio_base64"]))
            json.dump({"voice_id": V["id"], "voice_name": meta.get("name"), "model": V["model"], "settings": V["settings"], "seed": seed,
                       "text": line, "previous_text": prev_t, "next_text": next_t, "alignment": res["alignment"]},
                      open(base + ".align.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        d = json.load(open(base + ".align.json", encoding="utf-8"))
        a = analyse(base + ".mp3", words_from(d["alignment"]))
        a.update(seed=seed, base=os.path.basename(base), text_ok="".join(d["alignment"]["characters"]).strip() == line)
        cands.append(a)
    results.append(cands)

med = float(np.median([c["f0"] for cs in results for c in cs if c["f0"]]))
selection = []
for i, cs in enumerate(results):
    for c in cs:
        c["score"] = (0 if c["text_ok"] else 100) + 3 * len(c["pauses"]) + 1.5 * len(c["long_words"]) + abs(12 * np.log2(max(c["f0"], 1) / med)) * 0.5
    best = min(cs, key=lambda c: c["score"])
    selection.append({"line": i + 1, "scene": plan["line_scene"][i], "text": lines[i], "chosen": best["base"], "candidates": cs})
    print(f"L{i + 1:02d} -> {best['base']:<20} " + " | ".join(f"s{c['seed']}: {c['score']:.1f} pauses {c['pauses']} long {c['long_words']}" for c in cs))
json.dump({"median_f0": med, "voice": V, "selection": selection}, open(os.path.join(OUT, "selection.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("selection ->", os.path.join(OUT, "selection.json"))
