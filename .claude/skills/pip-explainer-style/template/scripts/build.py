"""Build hf/index.html: the whole PiP Explainer composition (one paused GSAP timeline).

  /usr/bin/python3 scripts/build.py            full video
  DUR=15 /usr/bin/python3 scripts/build.py     first 15 s only (quick test / review cut)

Layer order (bottom -> top): backdrop (navy dot grid) | PiP graphic panels | presenter | FULL slams | captions |
end card | flash. The presenter is ONE <video>: FULL <-> PiP is a morph of its wrappers (clip-path frame, layout
transform, edge feather), never a second copy of the footage.
Engine only: per-video content lives in timing.py (anchors, layout, punches), captions.py and scenes.py."""
import math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from kit import C, CSS, FULL, H, JS, PIP, CAP_Y, W, shake_js
from timing import END_CARD, FLASHES, LAYOUT, PANEL_CUTS, PUNCH, SHAKES, SPEECH_END, TOTAL, T
import captions, scenes

ROOT = os.path.abspath(os.path.join(HERE, ".."))
DUR = float(os.environ.get("DUR") or TOTAL)
MORPH_IN, MORPH_OUT = 0.34, 0.24  # FULL -> PiP / PiP -> FULL (expo.out: ~90 % there in a third of the time)


def f(x): return f"{x:.4f}"


# ---------------- presenter geometry ----------------
def full_state():
    z = FULL["z"]
    return dict(x=FULL["ox"] * (1 - z), y=FULL["oy"] * (1 - z), scale=z)


def pip_state(k):  # card pivot: source (540, src_top) sits at the card's top centre
    return dict(x=540 * (1 - k), y=PIP["y"] - PIP["src_top"] * k, scale=k)


CLIP_FULL = "inset(0px 0px 0px 0px round 0px)"
CLIP_PIP = f"inset({PIP['y']}px {W - PIP['x'] - PIP['w']}px {H - PIP['y'] - PIP['h']}px {PIP['x']}px round {PIP['r']}px)"


def js_obj(d): return "{ " + ", ".join(f"{k}: {v:.3f}" if isinstance(v, float) else f"{k}: {v}" for k, v in d.items()) + " }"


# ---------------- punch track (same semantics as the Remotion track(): each key eases toward v from t over d) ----------------
def ease(name, x):
    x = min(1.0, max(0.0, x))
    return 1.0 if x >= 1 else 1 - 2 ** (-10 * x)  # 'out' and 'snap' both map to expo.out


KEYS = sorted([dict(t=k[0], v=k[1], d=k[2], e=(k[3] if len(k) > 3 else "out")) for k in PUNCH], key=lambda k: k["t"])


def track(t):
    v = 1.0
    for k in KEYS:
        if t < k["t"]: break
        v = v + (k["v"] - v) * ease(k["e"], (t - k["t"]) / max(k["d"], 1e-6))
    return v


def build_presenter_js():
    js = []
    sw = [(a, m) for a, m in LAYOUT if a < DUR]
    nxt = lambda a: min([b for b, _ in LAYOUT if b > a + 1e-6] + [DUR])
    fs = full_state()
    js.append(f"gsap.set('#pmove', {js_obj(fs)}); gsap.set('#pclip', {{ clipPath: '{CLIP_FULL}' }}); gsap.set('#pmask', {{ '--fe': '0%' }});")
    for i, (a, m) in enumerate(sw):
        b = nxt(a)
        if m == 1:  # -> PiP: frame closes into the card, presenter scales to 0.6, edges feather into the wall colour
            d = MORPH_IN if i else 0.001
            k0 = PIP["k"] * (1 + 0.03 * min(1, d / 5))
            js.append(f"tl.to('#pclip', {{ clipPath: '{CLIP_PIP}', duration: {d}, ease: 'expo.out' }}, {f(a)});")
            js.append(f"tl.to('#pmove', {{ ...{js_obj(pip_state(k0))}, duration: {d}, ease: 'expo.out' }}, {f(a)});")
            js.append(f"tl.to('#pmask', {{ '--fe': '11%', duration: {d}, ease: 'expo.out' }}, {f(a)});")
            js.append(f"tl.to(['#ppunch', '#ppush'], {{ scale: 1, duration: {d}, ease: 'expo.out' }}, {f(a)});")
            js.append(f"tl.to('#fullvig', {{ opacity: 0, duration: {d}, ease: 'expo.out' }}, {f(a)});")
            js.append(f"tl.to('#caps', {{ y: {CAP_Y['pip'] - CAP_Y['full']}, duration: {d}, ease: 'expo.out' }}, {f(a)});")
            js.append(f"tl.fromTo('#pring', {{ opacity: 0 }}, {{ opacity: 1, duration: 0.2, ease: 'none', immediateRender: false }}, {f(a + d * 0.35)});")
            # slow growth inside the stint (0.6 -> 0.618 over 5 s)
            g1 = min(a + 5, b) - 0.001
            if g1 > a + d + 0.05:
                k1 = PIP["k"] * (1 + 0.03 * min(1, (g1 - a) / 5))
                js.append(f"tl.to('#pmove', {{ ...{js_obj(pip_state(k1))}, duration: {g1 - a - d:.3f}, ease: 'none' }}, {f(a + d)});")
        else:  # -> FULL: frame opens to full screen, 1.2x crop, then a slow +3.5 % push inside the stint
            if i:
                d = MORPH_OUT
                js.append(f"tl.set('#pring', {{ opacity: 0 }}, {f(a)});")
                js.append(f"tl.to('#pclip', {{ clipPath: '{CLIP_FULL}', duration: {d}, ease: 'expo.out' }}, {f(a)});")
                js.append(f"tl.to('#pmove', {{ ...{js_obj(fs)}, duration: {d}, ease: 'expo.out' }}, {f(a)});")
                js.append(f"tl.to('#pmask', {{ '--fe': '0%', duration: {d}, ease: 'expo.out' }}, {f(a)});")
                js.append(f"tl.to('#fullvig', {{ opacity: 1, duration: {d}, ease: 'expo.out' }}, {f(a)});")
                js.append(f"tl.to('#caps', {{ y: 0, duration: {d}, ease: 'expo.out' }}, {f(a)});")
            p1 = min(a + 4, b) - 0.002
            js.append(f"tl.fromTo('#ppush', {{ scale: 1 }}, {{ scale: {1 + 0.035 * min(1, (p1 - a) / 4):.4f}, duration: {p1 - a:.3f}, ease: 'none', immediateRender: false }}, {f(a)});")
            # punch-ins of this stint (truncated at the next key / layout switch so tweens never overlap)
            ks = [k for k in KEYS if a - 1e-6 <= k["t"] < b]
            for j, k in enumerate(ks):
                t0 = k["t"]; t1 = min(t0 + k["d"], ks[j + 1]["t"] if j + 1 < len(ks) else b, b)
                if t1 - t0 < 0.005:
                    js.append(f"tl.set('#ppunch', {{ scale: {track(t1):.4f} }}, {f(t0)});"); continue
                js.append(f"tl.fromTo('#ppunch', {{ scale: {track(t0):.4f} }}, {{ scale: {track(t1 - 1e-4):.4f}, duration: {t1 - t0:.3f}, "
                          f"ease: 'expo.out', immediateRender: false }}, {f(t0)});")
    for c in PANEL_CUTS:  # PiP -> PiP scene change: the card nudges
        if c < DUR:
            js.append(f"tl.fromTo('#pbump', {{ scale: 1.03 }}, {{ scale: 1, duration: 0.25, ease: 'expo.out', immediateRender: false }}, {f(c)});")
    for a, d, amp, seed in SHAKES:
        if a < DUR: js.append(shake_js("#pshake", a, d, amp, seed))
    js.append(f"tl.set('#presenter', {{ opacity: 0 }}, {f(END_CARD + 0.3)});")
    return "\n".join(js)


PRESENTER = f"""
<div id="presenter" class="layer">
  <div id="pbump" class="layer" style="transform-origin:540px {PIP['y'] + PIP['h']}px">
    <div id="pclip" class="layer">
      <div id="pwall" class="layer" style="background:linear-gradient(180deg,#c9c8c4 0px,#c9c8c4 {PIP['y']}px,#bdbcb8 {PIP['y'] + int(PIP['h'] * .55)}px,#8f8e8b {PIP['y'] + PIP['h']}px)"></div>
      <div id="pmove" class="layer" style="transform-origin:0 0">
        <div id="ppush" class="layer" style="transform-origin:{FULL['face_x']}px {FULL['face_y']}px">
          <div id="ppunch" class="layer" style="transform-origin:{FULL['face_x']}px {FULL['face_y']}px">
            <div id="pshake" class="layer">
              <div id="pmask" class="layer" style="--fe:0%;-webkit-mask-image:linear-gradient(90deg,transparent 0%,#000 var(--fe),#000 calc(100% - var(--fe)),transparent 100%);mask-image:linear-gradient(90deg,transparent 0%,#000 var(--fe),#000 calc(100% - var(--fe)),transparent 100%)">
                <video id="pres" class="media" src="assets/video/main.mp4" muted playsinline data-start="0" data-duration="{min(SPEECH_END, DUR):.3f}" data-track-index="0"></video>
              </div>
            </div>
          </div>
        </div>
      </div>
      <!-- soft navy vignette top + bottom in FULL, so a slam reads over the wall -->
      <div id="fullvig" class="layer" style="background:linear-gradient(180deg, rgba(6,19,41,0.18) 0%, rgba(6,19,41,0) 22%, rgba(6,19,41,0) 58%, rgba(6,19,41,0.42) 100%)"></div>
    </div>
    <div id="pring" class="hide" style="position:absolute;left:{PIP['x']}px;top:{PIP['y']}px;width:{PIP['w']}px;height:{PIP['h']}px;border-radius:{PIP['r']}px;box-shadow:0 -10px 60px rgba(0,0,0,0.5), 0 0 0 2px {C['line']}, 0 0 30px rgba(0,207,245,0.18)"></div>
  </div>
</div>"""

BACKDROP = f"""
<div id="bg" class="layer" style="background:{C['navy']}">
  <div id="dots" class="layer" style="background-image:radial-gradient(rgba(0,207,245,0.16) 1.5px, transparent 1.7px);background-size:34px 34px"></div>
  <div class="anc" style="left:540px;top:560px"><div id="glow" style="width:1100px;height:1100px;border-radius:50%;background:radial-gradient(circle, rgba(8,123,238,0.28), rgba(8,123,238,0) 65%)"></div></div>
  <div class="layer" style="background:radial-gradient(ellipse at 50% 45%, rgba(0,0,0,0) 55%, rgba(0,0,0,0.5) 100%)"></div>
</div>"""


def backdrop_js():
    n1, n2 = math.ceil(DUR / 7.854) + 1, math.ceil(DUR / 10.472) + 1
    return "\n".join([
        f"tl.fromTo('#dots', {{ backgroundPositionY: '0px' }}, {{ backgroundPositionY: '{-6 * DUR:.0f}px', duration: {DUR}, ease: 'none', immediateRender: false }}, 0);",
        f"tl.fromTo('#glow', {{ x: -160 }}, {{ x: 160, duration: 7.854, ease: 'sine.inOut', repeat: {n1}, yoyo: true, immediateRender: false }}, -3.927);",
        f"tl.fromTo('#glow', {{ y: 90 }}, {{ y: -90, duration: 10.472, ease: 'sine.inOut', repeat: {n2}, yoyo: true, immediateRender: false }}, 0);",
    ])


def captions_html_js():
    html, js, prev = ['<div id="caps" class="layer" style="pointer-events:none">'], [], 0.0
    for i, c in enumerate(captions.chunks()):
        if c["s"] >= min(DUR, END_CARD): continue
        c = dict(c, s=max(c["s"], prev)); prev = c["end"]  # one chunk on screen at a time
        spans = []
        for k, tk in enumerate(c["toks"]):
            on = tk["s"] - 0.04 <= c["s"] + 1e-6
            col = C["yellow"] if tk["key"] else "#fff"
            mr = "margin-right:18px;" if k < len(c["toks"]) - 1 else ""
            spans.append(f'<span id="cw{i}_{k}" style="color:{col};opacity:{1 if on else 0.35};{mr}">{tk["text"]}</span>')
            if not on: js.append(f"tl.set('#cw{i}_{k}', {{ opacity: 1 }}, {f(tk['s'] - 0.04)});")
        html.append(f'<div id="cap{i}" class="cap hide" style="top:{CAP_Y["full"]}px"><div id="cap{i}i" class="capin">{"".join(spans)}</div></div>')
        js.append(f"tl.set('#cap{i}', {{ opacity: 1 }}, {f(c['s'])});")
        js.append(f"tl.fromTo('#cap{i}i', {{ scale: 0.86, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.16, ease: 'back.out(1.8)', immediateRender: false }}, {f(c['s'])});")
        js.append(f"tl.set('#cap{i}', {{ opacity: 0 }}, {f(min(c['end'], END_CARD))});")
    html.append("</div>")
    return "\n".join(html), "\n".join(js)


def flash_js():
    js = []
    for t, amp, col in sorted(FLASHES):
        if t >= DUR: continue
        a = max(0.0, t - 0.04)
        js.append(f"tl.set('#flash', {{ backgroundColor: '{col}' }}, {f(a)});")
        if t > 0.04:
            js.append(f"tl.fromTo('#flash', {{ opacity: 0 }}, {{ opacity: {amp}, duration: 0.04, ease: 'none', immediateRender: false }}, {f(a)});")
        else:
            js.append(f"tl.set('#flash', {{ opacity: {amp} }}, 0);")
        js.append(f"tl.to('#flash', {{ opacity: 0, duration: 0.22, ease: 'none' }}, {f(t)});")
    return "\n".join(js)


def main():
    sc = [s for s in scenes.panels() if s["a"] < DUR]
    sl = [s for s in scenes.full_overlays() if s["a"] < DUR]
    end = scenes.end_card() if END_CARD < DUR else dict(html="", js="")
    cap_html, cap_js = captions_html_js()
    media = "\n".join(s.get("media", "") for s in sc)
    html = f"""<!doctype html>
<html lang="ms">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width={W}, height={H}" />
<title>PiP Explainer</title>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>{CSS}</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{DUR:.3f}" data-width="{W}" data-height="{H}">
<audio id="mix" src="assets/audio/mix_master.wav" data-start="0" data-duration="{DUR:.3f}" data-track-index="30" data-volume="1"></audio>
{BACKDROP}
<div id="panels" class="layer">
{chr(10).join(s['html'] for s in sc)}
</div>
{PRESENTER}
<div id="slams" class="layer">
{chr(10).join(s['html'] for s in sl)}
</div>
{cap_html}
{end['html']}
<div id="flash" class="layer" style="opacity:0;mix-blend-mode:screen;background:#fff;pointer-events:none"></div>
</div>
<script>
const tl = gsap.timeline({{ paused: true }});
{JS}
// ---- backdrop ----
{backdrop_js()}
// ---- presenter: one video, FULL <-> PiP morph, punch-ins, pushes, shakes ----
{build_presenter_js()}
// ---- PiP graphic panels ----
{chr(10).join(s['js'] for s in sc)}
// ---- FULL slams ----
{chr(10).join(s['js'] for s in sl)}
// ---- captions ----
{cap_js}
// ---- end card ----
{end['js']}
// ---- flashes ----
{flash_js()}
window.__timelines['main'] = tl;
tl.seek(0);
</script>
</body>
</html>
"""
    out = os.path.join(ROOT, "hf", "index.html")
    open(out, "w", encoding="utf-8").write(html)
    print(f"wrote {out}  ({DUR:.2f} s, {len(sc)} panels, {len(sl)} slams)")


if __name__ == "__main__":
    main()
