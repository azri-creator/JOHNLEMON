"""Build hf/index.html (fast cut) from hf/index.master.html (the 62.26 s master timeline).
The master timeline keeps the original word-synced times; this script
  1. rewrites every scene/video/audio data-start / data-duration through the VO time-map (audio/retime_map.json),
  2. injects a retime block that remaps every GSAP tween the same way (speech stays 1:1, silences are compressed).
Run: python3 scripts/retime_build.py   (re-run edit_vo_fast.py first if the VO changes)."""
import json, math, re, shutil, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
master = os.path.join(ROOT, sys.argv[1] if len(sys.argv) > 1 else "master/index.master.html")
target = os.path.join(ROOT, sys.argv[2] if len(sys.argv) > 2 else "hf/index.html")
if not os.path.exists(master):
    shutil.copy(target, master)
s = open(master).read()
m = json.load(open(os.path.join(ROOT, "audio", "retime_map.json")))
XS, YS = m["xs"], m["ys"]


def M(t):
    if t <= XS[0]: return YS[0] + (t - XS[0])
    for i in range(1, len(XS)):
        if t <= XS[i]:
            d = XS[i] - XS[i - 1]
            return YS[i] if d <= 1e-9 else YS[i - 1] + (t - XS[i - 1]) * (YS[i] - YS[i - 1]) / d
    return YS[-1] + (t - XS[-1])


def f(x): return f"{x:.3f}".rstrip("0").rstrip(".")


total = math.ceil(m["new_total"] * 30) / 30


def retag(tag_id, ns, nd, media_start=None):
    global s
    pat = re.compile(r'<(?:section|video|audio)\b[^>]*\bid="%s"[^>]*>' % re.escape(tag_id))
    mt = pat.search(s)
    assert mt, tag_id
    tag = mt.group(0)
    new = re.sub(r'data-start="[^"]*"', f'data-start="{f(ns)}"', tag)
    new = re.sub(r'data-duration="[^"]*"', f'data-duration="{f(nd)}"', new)
    if media_start is not None: new = re.sub(r'data-media-start="[^"]*"', f'data-media-start="{f(media_start)}"', new)
    s = s.replace(tag, new, 1)


scenes = {"s1": (0, 5.8), "s2": (5.8, 13.9), "s4": (13.9, 16.9), "s5": (16.9, 21.0), "s6a": (21.0, 23.65), "s6b": (23.65, 32.5),
          "s7": (32.5, 35.45), "s8": (35.45, 47.25), "s9": (47.25, 51.1), "s10": (51.1, 55.6), "s11": (55.6, 62.26)}
for k, (a, b) in scenes.items():
    last = k == "s11"
    ns, ne = M(a), (total if last else M(b))
    retag(k, ns, ne - ns)
    print(f"{k:4s} {a:6.2f}-{b:6.2f} -> {ns:6.2f}-{ne:6.2f}  ({ne-ns:4.2f}s)")

# demo clip: plays 1:1 from the start of S8; the case-study sentence must be at (demo gap start + pre) on the new timeline
s8_ns, s8_ne = M(35.45), M(47.25)
t_cs = m["demo_new_start"] + m["cs_pre"]
media_start = m["cs_src"][0] - (t_cs - s8_ns)
assert media_start >= 0, media_start
retag("demo", s8_ns, s8_ne - s8_ns, media_start)
retag("mix", 0, total)
s = re.sub(r'(data-composition-id="main"[^>]*?)data-duration="[^"]*"', lambda mm: f'{mm.group(1)}data-duration="{f(total)}"', s, 1)
print(f"demo media-start {media_start:.3f}  case audio at {t_cs:.3f}  total {total:.3f}")

block = f"""
      /* ---- retime: the master timeline above is authored on the 62.26 s VO. This map tightens it to the fast VO
              (speech stays 1:1, every silent gap is compressed). Anchors come from audio/retime_map.json. ---- */
      (() => {{
        const XS = {json.dumps([round(v, 4) for v in XS])};
        const YS = {json.dumps([round(v, 4) for v in YS])};
        const M = (t) => {{
          if (t <= XS[0]) return YS[0] + (t - XS[0]);
          for (let i = 1; i < XS.length; i++) if (t <= XS[i]) {{ const d = XS[i] - XS[i - 1]; return d <= 1e-9 ? YS[i] : YS[i - 1] + ((t - XS[i - 1]) * (YS[i] - YS[i - 1])) / d; }}
          return YS[YS.length - 1] + (t - XS[XS.length - 1]);
        }};
        tl.getChildren(false, true, false).forEach((ch) => {{
          const s0 = ch.startTime(), reps = Math.max(0, ch.repeat()), rd = ch.repeatDelay ? ch.repeatDelay() : 0;
          const e0 = s0 + ch.duration() * (reps + 1) + rd * reps;
          const ns = M(s0), ne = M(e0);
          let nd = Math.max(0.001, (ne - ns - rd * reps) / (reps + 1));
          const ez = ch.vars && ch.vars.ease;
          if (reps === 0 && typeof ez === "string" && /^(power|back|bounce|expo|elastic)/.test(ez) && nd <= 0.7 && nd > 0.05) nd *= 0.8;   // snappier pops/slams (fast-pace)
          ch.startTime(ns); ch.duration(nd);
        }});
      }})();
"""
marker = '      window.__timelines["main"] = tl;'
assert marker in s
s = s.replace(marker, block + "\n" + marker, 1)
open(target, "w").write(s)
