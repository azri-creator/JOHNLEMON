# Assemble hf/index.html from the template, the scene parts and the caption words.
import json, os, glob
P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
tpl = open(f"{P}/scripts/index.tpl.html").read()
words = json.load(open(f"{P}/hf/words.json"))
parts = "\n".join(open(f).read() for f in sorted(glob.glob(f"{P}/scripts/scenes/*.js")))
html = tpl.replace("/*__WORDS__*/", "const WORDS = " + json.dumps(words, ensure_ascii=False) + ";")
html = html.replace("/*__SCENES__*/", parts)
open(f"{P}/hf/index.html", "w").write(html)
print("built", len(html), "bytes,", len(words), "words")
