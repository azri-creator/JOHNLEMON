"""Rough word timings from the script alone (no TTS): ~0.30 s per word + plan gaps. Writes vo/vo_words.json so scenes
can be planned, built and snapshotted before any ElevenLabs credits are spent. build_vo.py overwrites it with real timings.

usage: /usr/bin/python3 scripts/rough_timing.py [seconds_per_word=0.30]
"""
import json, os, re, sys
from common import WORDS_JSON, load_plan, script_lines

plan = load_plan()
spw = float(sys.argv[1]) if len(sys.argv) > 1 else 0.30
lines = script_lines(plan)
assert len(lines) == len(plan["line_scene"]), f"script has {len(lines)} lines but plan.line_scene has {len(plan['line_scene'])}"
t, words, count = plan["gaps"]["lead_in"], [], {}
for i, line in enumerate(lines):
    for w in line.split():
        dur = spw * (1.6 if w[-1] in ".?!…" else 1.0)
        k = re.sub(r"[^a-z0-9?.!…]", "", w.lower()); count[k] = count.get(k, 0) + 1
        words.append({"w": w, "s": round(t, 3), "e": round(t + dur * 0.9, 3), "line": i + 1, "scene": plan["line_scene"][i], "id": f"{k}#{count[k]}"})
        t += dur
    if i + 1 < len(lines):
        t += plan["gaps"]["scene_change"] if plan["line_scene"][i + 1] != plan["line_scene"][i] else plan["gaps"]["in_scene"]
os.makedirs(os.path.dirname(WORDS_JSON), exist_ok=True)
json.dump({"source": "rough (no VO yet)", "duration": round(t, 3), "words": words}, open(WORDS_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"rough timing: {len(words)} words, {t:.1f}s speech (+{plan['end_hold']}s end hold) -> vo/vo_words.json")
