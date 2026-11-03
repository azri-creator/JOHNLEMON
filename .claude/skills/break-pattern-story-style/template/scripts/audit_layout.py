"""Layout audit for the composition: samples the (retimed) timeline every 0.1 s in headless Chrome and reports
  - text outside the side margins / vertical safe area
  - text elements overlapping each other (outside the same card)
  - text covering a character's face
Usage: python3 scripts/audit_layout.py   (writes qc/audit_layout.json and prints a summary)"""
import json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROME = [os.path.join(dp, f) for dp, _, fs in os.walk(os.path.expanduser("~/.cache/puppeteer/chrome-headless-shell")) for f in fs if f == "chrome-headless-shell"][0]
PROJ = sys.argv[1] if len(sys.argv) > 1 else "hf"
html = open(os.path.join(ROOT, PROJ, "index.html")).read()
WD, HT = (int(x) for x in re.search(r'data-width="(\d+)" data-height="(\d+)"', html).groups())
PORTRAIT = HT > WD
SIDE, TOP, BOT = (56, 150, HT - 160) if PORTRAIT else (80, 50, HT - 50)
head_add = '''<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Archivo+Black&family=JetBrains+Mono:wght@400;700&display=block" rel="stylesheet"><script>window.__timelines={};</script>'''
html = html.replace("<head>", "<head>" + head_add, 1)
audit = r'''
<pre id="audit-out" style="position:fixed;left:0;top:0;z-index:9999;background:#fff;color:#000;font-size:9px;width:100%;white-space:pre-wrap"></pre>
<script>
(async () => {
  const W = %d, TOPV = %d, BOTV = %d, SIDE = %d;
  await document.fonts.ready; await new Promise(r => setTimeout(r, 800));
  const tl = window.__timelines["main"]; const total = tl.duration();
  const secs = [...document.querySelectorAll("section.scene")].map(s => [s, +s.dataset.start, +s.dataset.start + +s.dataset.duration]);
  const IGN = new Set(["s1-ghost", "s2-ghost", "s10-ghost"]);
  const eff = (el) => { let o = 1; for (let e = el; e && e !== document.body; e = e.parentElement) o *= parseFloat(getComputedStyle(e).opacity); return o; };
  const textEls = (root) => { const out = []; const w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT); let n; while ((n = w.nextNode())) { if (!n.nodeValue.trim()) continue; const el = n.parentElement; if (el.closest(".fcard") || el.closest(".dots")) continue; if (IGN.has(el.id) || el.closest("#s1-ghost,#s2-ghost,#s10-ghost")) continue; if (!out.includes(el)) out.push(el); } return out; };
  const idOf = (el) => el.id || (el.closest("[id]") ? el.closest("[id]").id + ">" + el.tagName.toLowerCase() + ":" + (el.textContent.trim().slice(0, 14)) : el.tagName);
  const card = (el) => el.closest(".card,.tile,.node,.pill,#s1-cal,#s1-folder,#s7-ai,#s5-prog,#s2-p1,#s2-p2,#s2-p3,#s2-p4,#s2-p5,#s2-p6,#vgc-tile");
  const hits = {};
  const note = (key, t, info) => { (hits[key] = hits[key] || { info, times: [] }).times.push(t); };
  for (let t = 0.05; t < total - 0.02; t += 0.1) {
    tl.seek(t, false);
    for (const [sec, a, b] of secs) {
      const vis = t >= a && t < b; sec.style.display = vis ? "" : "none";
    }
    const vis = secs.filter(([s, a, b]) => t >= a && t < b).map(x => x[0]);
    const items = [];
    for (const s of vis) for (const el of textEls(s)) { const o = eff(el); if (o < 0.5) continue; const r = el.getBoundingClientRect(); if (r.width < 4 || r.height < 4) continue; items.push({ el, r, id: idOf(el), txt: el.textContent.trim().slice(0, 20) }); }
    for (const it of items) {
      const { r } = it; const L = Math.round(r.left), R = Math.round(r.right), T = Math.round(r.top), B = Math.round(r.bottom);
      if (L < SIDE || R > W - SIDE) note("MARGIN-SIDE|" + it.id, t, `"${it.txt}" x ${L}..${R}`);
      if (T < TOPV) note("SAFE-TOP|" + it.id, t, `"${it.txt}" y ${T}..${B}`);
      if (B > BOTV) note("SAFE-BOTTOM|" + it.id, t, `"${it.txt}" y ${T}..${B}`);
    }
    for (let i = 0; i < items.length; i++) for (let j = i + 1; j < items.length; j++) {
      const A = items[i], C = items[j]; if (card(A.el) && card(A.el) === card(C.el)) continue; if (A.el.contains(C.el) || C.el.contains(A.el)) continue;
      const x = Math.min(A.r.right, C.r.right) - Math.max(A.r.left, C.r.left), y = Math.min(A.r.bottom, C.r.bottom) - Math.max(A.r.top, C.r.top);
      if (x > 6 && y > 6) { const ar = x * y / Math.min(A.r.width * A.r.height, C.r.width * C.r.height); if (ar > 0.12) note("TEXT-OVERLAP|" + [A.id, C.id].sort().join(" x "), t, `"${A.txt}" vs "${C.txt}" ${(ar * 100) | 0}%`); }
    }
    for (const ch of vis.flatMap(s => [...s.querySelectorAll("img.char")])) {
      if (eff(ch) < 0.5) continue; const cr = ch.getBoundingClientRect();
      const face = { left: cr.left + cr.width * 0.2, right: cr.left + cr.width * 0.8, top: cr.top + cr.height * 0.02, bottom: cr.top + cr.height * 0.2 };
      for (const it of items) { if (it.el.closest(".card,.tile")) continue; const x = Math.min(face.right, it.r.right) - Math.max(face.left, it.r.left), y = Math.min(face.bottom, it.r.bottom) - Math.max(face.top, it.r.top); if (x > 8 && y > 8 && x * y / (it.r.width * it.r.height) > 0.08) note("TEXT-ON-FACE|" + it.id + " / " + ch.id, t, `"${it.txt}"`); }
    }
  }
  const out = Object.entries(hits).map(([k, v]) => { const ts = v.times; const runs = []; let s = ts[0], p = ts[0]; for (const t of ts.slice(1)) { if (t - p > 0.15) { runs.push([s, p]); s = t; } p = t; } runs.push([s, p]); return { key: k, info: v.info, runs: runs.map(r => [+r[0].toFixed(2), +r[1].toFixed(2)]) }; });
  document.getElementById("audit-out").textContent = "@@" + JSON.stringify(out) + "@@";
})();
</script></body>'''
audit = audit.replace("%d, TOPV = %d, BOTV = %d, SIDE = %d", "%d, TOPV = %d, BOTV = %d, SIDE = %d" % (WD, TOP, BOT, SIDE), 1) if False else audit
html = html.replace("</body>", audit.replace("const W = %d, TOPV = %d, BOTV = %d, SIDE = %d;", "const W = %d, TOPV = %d, BOTV = %d, SIDE = %d;" % (WD, TOP, BOT, SIDE)), 1)
tmp = os.path.join(ROOT, PROJ, "_audit.html")
open(tmp, "w").write(html)
try:
    r = subprocess.run([CHROME, "--headless", "--no-sandbox", "--disable-gpu", "--allow-file-access-from-files", "--window-size=%d,%d" % (WD, HT), "--virtual-time-budget=240000", "--dump-dom", "file://" + tmp], capture_output=True, text=True, timeout=600)
finally:
    os.remove(tmp)
m = re.search(r"@@(.*?)@@", r.stdout, re.S)
if not m:
    print("no audit output", r.stderr[-800:]); sys.exit(1)
res = json.loads(m.group(1).replace("&quot;", '"').replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">"))
json.dump(res, open(os.path.join(ROOT, "qc", "audit_layout_%s.json" % PROJ), "w"), indent=1)
print(f"{len(res)} finding groups")
for g in sorted(res, key=lambda g: g["key"]):
    dur = sum(b - a + 0.1 for a, b in g["runs"])
    if dur >= 0.25: print(f"{g['key']:70s} {dur:4.1f}s runs={g['runs'][:4]} {g['info']}")
