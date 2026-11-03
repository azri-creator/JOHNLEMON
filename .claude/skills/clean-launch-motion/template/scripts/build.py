"""Assemble hf/index.html from scripts/index.tpl.html + lib.js + the scene files, plan.json and vo/vo_words.json.

Scene files: scripts/scenes/*.html (or a folder given as argv[1]). Each file holds one scene:
    <section class="scene" id="<key>"> ...markup... </section>
    <script> scene("<key>", (S) => { cam(S, {...}); headline("..."); ... }); </script>
Only scenes listed in plan.scenes are used, in plan order. Re-run after every edit (it overwrites hf/index.html).

usage: /usr/bin/python3 scripts/build.py [scenes_dir]
"""
import glob, json, os, re, sys
from common import ASSETS, HERE, HF, load_plan, load_words, timing

plan = load_plan()
words = load_words()
cut, span, vo_end, total = timing(plan, words)
scene_dir = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(HERE, "scenes")

found = {}
for f in sorted(glob.glob(os.path.join(glob.escape(scene_dir), "*.html"))):
    src = open(f, encoding="utf-8").read()
    m = re.search(r'<section[^>]*class="scene"[^>]*id="([^"]+)"', src) or re.search(r'<section[^>]*id="([^"]+)"[^>]*class="scene"', src)
    if not m:
        print("skip (no <section class=\"scene\" id=...>):", os.path.basename(f)); continue
    i = src.find("<script>")
    j = src.rfind("</script>")
    if i < 0 or j < 0:
        raise SystemExit(f"{os.path.basename(f)}: needs one <script> block after the markup")
    found[m.group(1)] = (src[:i].strip(), src[i + len("<script>"):j].strip(), os.path.basename(f))

missing = [k for k in plan["scenes"] if k not in found]
if missing:
    raise SystemExit(f"no scene file for: {missing} (looked in {scene_dir})")
unused = [found[k][2] for k in found if k not in plan["scenes"]]
if unused:
    print("not in plan.scenes, left out:", unused)

markup = "\n".join(found[k][0] for k in plan["scenes"])
code = "\n".join(f"// ---------------- scene: {k} ({found[k][2]}) ----------------\n{found[k][1]}" for k in plan["scenes"])
data = (f"const PLAN = {json.dumps({'name': plan['name'], 'scenes': plan['scenes'], 'lead': plan['lead'], 'end_hold': plan['end_hold']})};\n"
        f"const WORDS = {json.dumps(words, ensure_ascii=False)};\n"
        f"const CUT = {json.dumps(cut)};\nconst SPAN = {json.dumps(span)};\nconst VO_END = {vo_end};\nconst TOTAL = {total};")

audio = ""
if os.path.exists(os.path.join(ASSETS, "mix.wav")):
    audio = f'      <audio id="mix" src="assets/mix.wav" data-start="0" data-duration="{total}" data-track-index="10" data-volume="1"></audio>'
else:
    print("note: hf/assets/mix.wav not found yet (run make_audio.py); building a silent preview")

tpl = open(os.path.join(HERE, "index.tpl.html"), encoding="utf-8").read()
lib = open(os.path.join(HERE, "lib.js"), encoding="utf-8").read()
html = (tpl.replace("/*__TOTAL__*/", f"{total}").replace("<!--__SCENES__-->", markup).replace("<!--__AUDIO__-->", audio)
        .replace("/*__DATA__*/", data).replace("/*__LIB__*/", lib).replace("/*__BUILD__*/", code))
os.makedirs(HF, exist_ok=True)
open(os.path.join(HF, "index.html"), "w", encoding="utf-8").write(html)
print(f"built hf/index.html: {total:.2f}s, scenes " + ", ".join(f"{k} {span[k][0]:.2f}-{span[k][1]:.2f}" for k in plan["scenes"]))
