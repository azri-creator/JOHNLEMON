"""Write hf/index.html for a Glow Keyword Style video (HyperFrames: HTML + one paused GSAP timeline).

Layout of this file
  1. config      timing.json (T word anchors, CUT shot cuts, L layout windows), palette, layer constants
  2. LIBRARY     the locked text treatments -> HTML + GSAP:  italic(), heavy(), bluebox(), script(), phrase(),
                 cta_keyword(); camera helpers track(), bump_*(), shake(), flash()
  3. EXAMPLE     the worked example (Jago Prompt hook + concept intro + CTA end card). Rewrite this part per video:
                 it is choreography, not identity (see references/variation_playbook.md)
  4. page        the composition: footage stack (shake > blur/dim > rgb > frame > zoom > push > video), text, flashes

Run:  /usr/bin/python3 scripts/build.py            (PALETTE=green rebuilds with the pre-blue Jago Prompt accent, for A/B)
"""
import json, math, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TM = json.load(open(os.path.join(ROOT, "timing.json")))
T, CUT, L = TM["T"], TM["CUT"], TM["L"]
SRC_END, TOTAL = float(TM["SRC_END"]), float(TM["TOTAL"])
W, H, FPS = 1080, 1920, 30
FOCUS_Y = 690  # face height in the source frame (zoom origin)

# ---------------------------------------------------------------- palette (identity: client tutorial brand blue)
PAL = {
    "blue": dict(box="#14B8F0", neon="#3DD8FF", deep="#0A8ED6", text="#F0FBFF", glow="rgba(20,184,240,0.55)",
                 stroke="#06304f", ex1="#0a4d7a", ex2="#073a5c", ex3="#04263d", neonA="rgba(61,216,255,0.55)"),
    # the first Jago Prompt render (Sep 2026) was green; kept only for A/B against that reference
    "green": dict(box="#1FD11B", neon="#48FF55", deep="#12B80F", text="#F2FFF2", glow="rgba(31,209,27,0.55)",
                  stroke="#0b3b0a", ex1="#0e5a0c", ex2="#0a3d08", ex3="#062a05", neonA="rgba(72,255,85,0.55)"),
}[os.environ.get("PALETTE", "blue")]
INK, RED, CYAN = "#060806", "#FF3B3B", "#18E4FF"
NEON_GLOW = f"0 0 3px {PAL['neon']}, 0 0 10px {PAL['neon']}, 0 0 24px {PAL['deep']}, 0 0 48px {PAL['glow']}"
TEXT_SHADOW = "0 2px 12px rgba(0,0,0,0.55), 0 0 2px rgba(0,0,0,0.35)"

HTML, JS = [], []          # markup for the text layer, timeline lines
_ids = {}


def uid(p):
    _ids[p] = _ids.get(p, 0) + 1
    return f"{p}{_ids[p]}"


def r(v):
    return round(v, 3)


def noise(seed):           # same deterministic noise as the Remotion lib
    x = math.sin(seed * 12.9898 + 78.233) * 43758.5453
    return x - math.floor(x)


def anchor(align):
    return {"left": "0%", "right": "-100%"}.get(align, "-50%")


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ================================================================= LIBRARY: locked text treatments
def italic(text, a, b, x, y, size=50, rot=0, align="center", weight=600, ital=True, color="#fff", maxW=960):
    """Small white keyword: Inter italic 600, blur-in + 16 px rise, soft black shadow."""
    i = uid("it")
    HTML.append(f'<div class="anc" style="left:{x}px;top:{y}px;transform:translate({anchor(align)},-50%) rotate({rot}deg)">'
                f'<div id="{i}" class="it" data-fit="{maxW}" style="font-size:{size}px;font-weight:{weight};'
                f'font-style:{"italic" if ital else "normal"};color:{color}">{esc(text)}</div></div>')
    JS.append(f"tl.fromTo('#{i}',{{y:16,scale:.92,filter:'blur(9px)'}},{{y:0,scale:1,filter:'blur(0px)',duration:.22,ease:EO}},{r(a)});"
              f"tl.fromTo('#{i}',{{opacity:0}},{{opacity:1,duration:.022,ease:'sine.out'}},{r(a)});")  # opacity = clamp(2*eased p): full in ~1 frame
    if b < TOTAL:
        JS.append(f"tl.to('#{i}',{{opacity:0,y:-10,filter:'blur(8px)',duration:.16,ease:EI}},{r(b - .16)});")
    return i


def heavy(text, a, b, x, y, size=130, rot=0, align="center", color="#fff", maxW=960, glow=True, split=1.0, stretch=True):
    """Heavy uppercase hero word: Archivo Black + red/cyan RGB split (3 px rest, ~29 px on entry), 1.9->1 smear."""
    i = uid("hv")
    sh = f"0 0 18px rgba(255,255,255,0.35), {TEXT_SHADOW}" if glow else TEXT_SHADOW
    HTML.append(f'<div class="anc" style="left:{x}px;top:{y}px;transform:translate({anchor(align)},-50%) rotate({rot}deg)">'
                f'<div id="{i}"><div id="{i}x"><div class="hvb" data-fit="{maxW}" data-layout-allow-overlap style="font-size:{size}px"><span class="sz">{esc(text)}</span>'
                f'<span id="{i}r" style="color:{RED}" class="sp">{esc(text)}</span>'
                f'<span id="{i}c" style="color:{CYAN}" class="sp">{esc(text)}</span>'
                f'<span style="color:{color};text-shadow:{sh}">{esc(text)}</span></div></div></div></div>')
    d0, d1 = 3 * split, 29 * split
    di = r(min(.26, b - .14 - a)) if b < TOTAL else .26   # entry never overlaps the exit (lint)
    JS.append(f"tl.fromTo('#{i}',{{opacity:0}},{{opacity:1,duration:.02,ease:'sine.out'}},{r(a)});"
              f"tl.fromTo('#{i}',{{scale:1.25,filter:'blur(7px)'}},{{scale:1,filter:'blur(0px)',duration:{di},ease:EO}},{r(a)});"
              f"tl.fromTo('#{i}r',{{x:{-d1}}},{{x:{-d0},duration:{di},ease:EO}},{r(a)});"
              f"tl.fromTo('#{i}c',{{x:{d1}}},{{x:{d0},duration:{di},ease:EO}},{r(a)});")
    if stretch:
        JS.append(f"tl.fromTo('#{i}x',{{scaleX:1.9}},{{scaleX:1,duration:.18,ease:EO}},{r(a)});")
    if b < TOTAL:
        e = 18 * split
        JS.append(f"tl.to('#{i}',{{opacity:0,scale:1.15,filter:'blur(6px)',duration:.14,ease:EI}},{r(b - .14)});"
                  f"tl.to('#{i}r',{{x:{-(d0 + e)},duration:.14,ease:EI}},{r(b - .14)});"
                  f"tl.to('#{i}c',{{x:{d0 + e},duration:.14,ease:EI}},{r(b - .14)});")
    return i


def bluebox(text, a, b, x, y, size=78, rot=0, align="center", maxW=940):
    """Brand-blue highlight box, black Archivo Narrow-style bold italic; box wipes L->R 0.16 s, text slides in."""
    i = uid("bx")
    HTML.append(f'<div class="anc" style="left:{x}px;top:{y}px;transform:translate({anchor(align)},-50%) rotate({rot}deg)">'
                f'<div id="{i}"><div id="{i}b" class="bx" style="padding:{r(size*.02)}px {r(size*.22)}px {r(size*.04)}px">'
                f'<div id="{i}t" class="bt" data-fit="{maxW - 40}" style="font-size:{size}px">{esc(text)}</div></div></div></div>')
    JS.append(f"tl.fromTo('#{i}',{{opacity:0}},{{opacity:1,duration:.01}},{r(a - .01)});"
              f"tl.fromTo('#{i}b',{{clipPath:'inset(0% 100% 0% 0%)'}},{{clipPath:'inset(0% 0% 0% 0%)',duration:.16,ease:EO}},{r(a)});"
              f"tl.fromTo('#{i}',{{scale:1.12}},{{scale:1,duration:.2,ease:EO}},{r(a + .06)});"
              f"tl.fromTo('#{i}t',{{x:-24,opacity:0}},{{x:0,opacity:1,duration:.2,ease:EO}},{r(a + .06)});")
    if b < TOTAL:
        JS.append(f"tl.to('#{i}',{{opacity:0,scale:.9,filter:'blur(6px)',duration:.14,ease:EI}},{r(b - .14)});")
    return i


def script(text, a, b, x, y, size=110, rot=-6, align="center", dur=.55, maxW=980):
    """Neon connected script (Sacramento): write-on clip L->R, flicker for 0.35 s, blue glow."""
    i = uid("sc")
    HTML.append(f'<div class="anc" style="left:{x}px;top:{y}px;transform:translate({anchor(align)},-50%) rotate({rot}deg)">'
                f'<div id="{i}"><div id="{i}c" class="sc" data-fit="{maxW}" data-stroke="70" style="font-size:{size}px">{esc(text)}</div></div></div>')
    JS.append(f"tl.fromTo('#{i}c',{{clipPath:'inset(-40% 100% -40% -10%)'}},{{clipPath:'inset(-40% 0% -40% -10%)',duration:{dur},ease:EIO}},{r(a)});")
    JS.append(f"tl.fromTo('#{i}',{{opacity:0}},{{opacity:{r(.75 + .25 * noise(math.floor(a * FPS)))},duration:.01}},{r(a - .01)});")
    f0 = math.floor(a * FPS) + 1
    while f0 / FPS < a + .35:
        JS.append(f"tl.set('#{i}',{{opacity:{r(.75 + .25 * noise(f0))}}},{r(f0 / FPS)});")
        f0 += 1
    JS.append(f"tl.set('#{i}',{{opacity:1}},{r(f0 / FPS)});")
    if b < TOTAL:
        JS.append(f"tl.to('#{i}',{{opacity:0,filter:'blur(6px)',duration:.16,ease:EI}},{r(b - .16)});")
    return i


def phrase(words, b, x, y, size=54, weight=600, ital=True, align="center", gap=.28):
    """Word-by-word build: each word pops (rise 14 px, scale .85->1, blur 8->0) on its own start time."""
    i = uid("ph")
    spans = "".join(f'<span id="{i}w{k}" class="pw">{esc(w)}</span>' for k, (w, _) in enumerate(words))
    HTML.append(f'<div class="anc" style="left:{x}px;top:{y}px;transform:translate({anchor(align)},-50%)">'
                f'<div id="{i}" class="ph" style="gap:{r(size*gap)}px;font-size:{size}px;font-weight:{weight};'
                f'font-style:{"italic" if ital else "normal"}">{spans}</div></div>')
    for k, (_, at) in enumerate(words):
        JS.append(f"tl.fromTo('#{i}w{k}',{{y:14,scale:.85,filter:'blur(8px)'}},{{y:0,scale:1,filter:'blur(0px)',duration:.2,ease:EO}},{r(at)});"
                  f"tl.fromTo('#{i}w{k}',{{opacity:0}},{{opacity:1,duration:.02,ease:'sine.out'}},{r(at)});")
    if b < TOTAL:
        JS.append(f"tl.to('#{i}',{{opacity:0,filter:'blur(8px)',duration:.16,ease:EI}},{r(b - .16)});")
    return i


def pop_in(sel, a, dur=.3, frm=.55):
    """Pop: scale from .4-.6 with overshoot (bezier .34,1.56,.64,1), blur 10->0."""
    # blur gets its own ease-out tween: an overshooting ease would push blur() negative (invalid -> stays blurred)
    JS.append(f"tl.fromTo('{sel}',{{scale:{frm}}},{{scale:1,duration:{dur},ease:BK}},{r(a)});"
              f"tl.fromTo('{sel}',{{filter:'blur(10px)'}},{{filter:'blur(0px)',duration:{dur},ease:EO}},{r(a)});"
              f"tl.fromTo('{sel}',{{opacity:0}},{{opacity:1,duration:{r(dur/3)},ease:'none'}},{r(a)});")


# ================================================================= LIBRARY: camera
def track(sel, prop, init, keys, fmt=lambda v: v):
    """Sequential keyframe track (port of lib.track): key (t, v, d=.3, ease=EO). Durations are clipped so tweens
    on one property never overlap (lint), which is what the Remotion track did in practice."""
    JS.append(f"tl.set('{sel}',{{{prop}:{fmt(init)}}},0);")
    keys = sorted(keys, key=lambda k: k[0])
    for n, k in enumerate(keys):
        t, v = k[0], k[1]
        d = k[2] if len(k) > 2 else .3
        e = k[3] if len(k) > 3 else "EO"
        if n + 1 < len(keys): d = max(.01, min(d, keys[n + 1][0] - t))
        d = max(.01, min(d, TOTAL - t))
        JS.append(f"tl.to('{sel}',{{{prop}:{fmt(v)},duration:{r(d)},ease:{e}}},{r(t)});")


FX = []    # (a, b, kind, amp) bumps on the footage stack


def bump_blur(a, b, amp): FX.append((a, b, "blur", amp))


def bump_rgb(a, b, amp): FX.append((a, b, "rgb", amp))


def shake(a, dur, ax, ay, sx=1, sy=7):
    """Seeded decaying shake on the whole footage stack (frame-stepped, like the Remotion version)."""
    f = math.floor(a * FPS)
    while f / FPS <= a + dur:
        t = f / FPS
        if t >= a:
            k = 1 - (t - a) / dur
            JS.append(f"tl.set('#shake',{{x:{r((noise(f + sx) - .5) * 2 * ax * k)},y:{r((noise(f * 1.7 + sy) - .5) * 2 * ay * k)}}},{r(t)});")
        f += 1
    JS.append(f"tl.set('#shake',{{x:0,y:0}},{r(a + dur + .01)});")


FLASHES = []


def flash(t, amp, color="#ffffff", up=.05, down=.2):
    """Screen-blended colour flash (white on hard cuts, brand-blue into a new section). <= 6 per video."""
    i = uid("fl")
    FLASHES.append(f'<div id="{i}" class="flash" style="background:{color}"></div>')
    JS.append(f"tl.fromTo('#{i}',{{opacity:0}},{{opacity:{amp},duration:{up},ease:'none',immediateRender:false}},{r(t - up)});"
              f"tl.to('#{i}',{{opacity:0,duration:{down},ease:'none'}},{r(t)});")


def emit_fx():
    """blur / dim on #fx and the RGB-split SVG filter on #rgbw; switched off (filter:none) between bumps."""
    for a, b, kind, amp in sorted(FX):
        m = (a + b) / 2
        if kind == "blur":
            JS.append(f"tl.set('#fx',{{filter:'blur(0px) brightness(1)'}},{r(a)});"
                      f"tl.to('#fx',{{filter:'blur({amp}px) brightness(1)',duration:{r(m - a)},ease:'none'}},{r(a)});"
                      f"tl.to('#fx',{{filter:'blur(0px) brightness(1)',duration:{r(b - m)},ease:'none'}},{r(m)});"
                      f"tl.set('#fx',{{filter:'none'}},{r(b + .005)});")
        else:
            JS.append(f"tl.set('#rgbw',{{filter:'url(#rgbv)'}},{r(a)});"
                      f"tl.to('#rgbR',{{attr:{{dx:{-amp},dy:{r(amp*.15)}}},duration:{r(m - a)},ease:'none'}},{r(a)});"
                      f"tl.to('#rgbB',{{attr:{{dx:{amp},dy:{r(-amp*.15)}}},duration:{r(m - a)},ease:'none'}},{r(a)});"
                      f"tl.to('#rgbR',{{attr:{{dx:0,dy:0}},duration:{r(b - m)},ease:'none'}},{r(m)});"
                      f"tl.to('#rgbB',{{attr:{{dx:0,dy:0}},duration:{r(b - m)},ease:'none'}},{r(m)});"
                      f"tl.set('#rgbw',{{filter:'none'}},{r(b + .005)});")


def shot_push(cuts):
    """Constant slow push +3.5 % across each shot (resets on every cut)."""
    edges = [0.0] + sorted(cuts) + [TOTAL]
    JS.append("tl.set('#push',{scale:1},0);")
    for a, b in zip(edges, edges[1:]):
        if b <= a: continue
        JS.append(f"tl.fromTo('#push',{{scale:1}},{{scale:1.035,duration:{r(b - a - .001)},ease:'none',immediateRender:false}},{r(a)});")


CUTOUTS = {k: tuple(v) for k, v in TM.get("CUTOUTS", {}).items()}   # name -> (start, end) source seconds


def room_fade(a, b, din=.35, dout=.3):
    """Explainer layout: fade the room out (a) and back in (b). The cut-out presenter (CUTOUTS in timing.json,
    made by prep_footage.py cutout) sits UNDER the room layer, so fading the room reveals her on the dark grid
    backdrop with no brightness dip. Pair it with #frame scale/x/y keys that park her in a corner (~0.6 scale)."""
    JS.append(f"tl.to('#room',{{opacity:0,duration:{din},ease:EIO}},{r(a + .05)});"
              f"tl.to('#backdrop',{{opacity:1,duration:{din},ease:EIO}},{r(a + .05)});"
              f"tl.to('#room',{{opacity:1,duration:{dout},ease:EIO}},{r(b + .03)});"
              f"tl.to('#backdrop',{{opacity:0,duration:{dout},ease:EIO}},{r(b + .03)});")


# ================================================================= EXAMPLE (rewrite per video)
AV = [  # flat illustrated faces: "a different AI face every generation"
    dict(bg="#d9d4cf", hijab="#8a6a64", skin="#eac4a6", fw=58, fh=72, glasses="round", brow=0, mouth="smile"),
    dict(bg="#cfd6da", hijab="#2f4858", skin="#c99670", fw=66, fh=68, glasses="", brow=-6, mouth="flat"),
    dict(bg="#dccfd3", hijab="#a8475a", skin="#f1d2bb", fw=52, fh=78, glasses="square", brow=5, mouth="open"),
    dict(bg="#d5d8cc", hijab="#56703d", skin="#b98361", fw=62, fh=74, glasses="", brow=3, mouth="smile"),
    dict(bg="#e0d8c8", hijab="#b8903a", skin="#e2b48f", fw=56, fh=70, glasses="round", brow=-4, mouth="flat"),
    dict(bg="#d6d0e0", hijab="#5b4a8c", skin="#f3d6bf", fw=60, fh=80, glasses="square", brow=6, mouth="open"),
]


def avatar_svg(v):
    cx, cy, fw, fh = 118, 120, v["fw"], v["fh"]; ey = cy - 4
    s = [f'<svg viewBox="0 0 236 236" width="236" height="236"><rect width="236" height="236" fill="{v["bg"]}"/>',
         f'<ellipse cx="{cx}" cy="262" rx="118" ry="82" fill="{v["hijab"]}"/>',
         f'<path d="M {cx-fw-28} {cy} Q {cx-fw-34} {cy+fh+50} {cx-60} 236 L {cx+60} 236 Q {cx+fw+34} {cy+fh+50} {cx+fw+28} {cy} Z" fill="{v["hijab"]}"/>',
         f'<ellipse cx="{cx}" cy="{cy-6}" rx="{fw+28}" ry="{fh+32}" fill="{v["hijab"]}"/>',
         f'<ellipse cx="{cx}" cy="{cy+6}" rx="{fw}" ry="{fh}" fill="{v["skin"]}"/>',
         f'<path d="M {cx-fw-6} {cy-18} Q {cx} {cy-fh-44} {cx+fw+6} {cy-18} Q {cx} {cy-fh+4} {cx-fw-6} {cy-18} Z" fill="{v["hijab"]}"/>',
         f'<path d="M {cx-36} {ey-20+v["brow"]} Q {cx-22} {ey-28} {cx-8} {ey-20}" stroke="#3a2a22" stroke-width="4" fill="none" stroke-linecap="round"/>',
         f'<path d="M {cx+8} {ey-20} Q {cx+22} {ey-28} {cx+36} {ey-20+v["brow"]}" stroke="#3a2a22" stroke-width="4" fill="none" stroke-linecap="round"/>',
         f'<ellipse cx="{cx-22}" cy="{ey}" rx="6" ry="7" fill="#2a1d18"/><ellipse cx="{cx+22}" cy="{ey}" rx="6" ry="7" fill="#2a1d18"/>']
    if v["glasses"] == "round":
        s.append(f'<g stroke="#2b2b2b" stroke-width="3.5" fill="none"><circle cx="{cx-22}" cy="{ey}" r="17"/><circle cx="{cx+22}" cy="{ey}" r="17"/><path d="M {cx-5} {ey} H {cx+5}"/></g>')
    if v["glasses"] == "square":
        s.append(f'<g stroke="#2b2b2b" stroke-width="3.5" fill="none"><rect x="{cx-40}" y="{ey-14}" width="34" height="27" rx="6"/><rect x="{cx+6}" y="{ey-14}" width="34" height="27" rx="6"/><path d="M {cx-6} {ey} H {cx+6}"/></g>')
    s.append(f'<path d="M {cx} {ey+10} Q {cx-6} {ey+26} {cx+3} {ey+28}" stroke="rgba(90,50,40,0.55)" stroke-width="3" fill="none" stroke-linecap="round"/>')
    if v["mouth"] == "smile": s.append(f'<path d="M {cx-18} {cy+40} Q {cx} {cy+54} {cx+18} {cy+40}" stroke="#9c3b3b" stroke-width="5" fill="none" stroke-linecap="round"/>')
    if v["mouth"] == "flat": s.append(f'<path d="M {cx-15} {cy+44} H {cx+15}" stroke="#9c3b3b" stroke-width="5" stroke-linecap="round"/>')
    if v["mouth"] == "open": s.append(f'<ellipse cx="{cx}" cy="{cy+45}" rx="11" ry="8" fill="#8a2f33"/>')
    return "".join(s) + "</svg>"


def hook_cards():
    """Hook: three 'PROMPT n' polaroids pop in, shuffle on 'muka', flip to new faces, '?' marks, shake on 'lari'."""
    slots = [220, 540, 860]; to_slot = [2, 0, 1]
    for i in range(3):
        appear = [T["try_"], T["mm1"], T["mm2"]][i]
        base = [-7, 3, 8][i]; arc = -90 if i == 1 else 70; rk = [10, -8, 6][i]
        HTML.append(f'<div id="card{i}" class="card" style="left:{slots[i]-130}px;top:285px"><div id="cardP{i}" class="cardP">'
                    f'<div id="cardIn{i}" class="cardIn"><div class="av"><div id="avA{i}" class="avl">{avatar_svg(AV[i])}</div>'
                    f'<div id="avB{i}" class="avl">{avatar_svg(AV[i+3])}</div></div><div class="clab">PROMPT {i+1}</div></div>'
                    f'<div id="q{i}" class="qm">?</div></div></div>')
        JS.append(f"tl.set('#cardP{i}',{{rotation:{base}}},0); tl.set('#avB{i}',{{opacity:0}},0); tl.set('#q{i}',{{opacity:0}},0);")
        pop_in(f"#cardP{i}", appear, .32, .4)
        sp0, sd = T["muka1"], .38
        dx = slots[to_slot[i]] - slots[i]
        JS.append(f"tl.to('#card{i}',{{x:{dx},duration:{sd},ease:EIO}},{r(sp0)});"
                  f"tl.to('#card{i}',{{y:{arc},duration:{sd/2},ease:'sine.out'}},{r(sp0)});"
                  f"tl.to('#card{i}',{{y:0,duration:{sd/2},ease:'sine.in'}},{r(sp0+sd/2)});"
                  f"tl.to('#cardP{i}',{{rotation:{base+rk},duration:{sd/2},ease:'sine.out'}},{r(sp0)});"
                  f"tl.to('#cardP{i}',{{rotation:{base},duration:{sd/2},ease:'sine.in'}},{r(sp0+sd/2)});")
        fa = T["muka1"] + .44 + i * .06   # face swap = card flip
        JS.append(f"tl.fromTo('#cardIn{i}',{{rotationY:0,transformPerspective:900}},{{rotationY:90,duration:.11,ease:'none',immediateRender:false}},{r(fa)});"
                  f"tl.set('#avA{i}',{{opacity:0}},{r(fa+.11)}); tl.set('#avB{i}',{{opacity:1}},{r(fa+.11)});"
                  f"tl.fromTo('#cardIn{i}',{{rotationY:-90,transformPerspective:900}},{{rotationY:0,duration:.11,ease:'none',immediateRender:false}},{r(fa+.11)});")
        qa = T["asyik"] + i * .1
        pop_in(f"#q{i}", qa, .3, .2)
        f = math.floor(qa * FPS)
        while f / FPS < T["hookEnd"] + .25:
            t = f / FPS
            if t >= qa: JS.append(f"tl.set('#q{i}',{{rotation:{r(12 + math.sin((t - T['asyik']) * 9 + i) * 8)}}},{r(t)});")
            f += 1
        # jitter on "lari"
        f = math.floor((T["lari"] - .02) * FPS)
        while f / FPS < T["lari"] + .3:
            t = f / FPS; k = 1 - (t - T["lari"]) / .3
            if t >= T["lari"]:
                JS.append(f"tl.set('#cardIn{i}',{{x:{r((noise(f + i*11) - .5) * 28 * k)},y:{r((noise(f*1.7 + i*11) - .5) * 28 * k)}}},{r(t)});")
            f += 1
        JS.append(f"tl.set('#cardIn{i}',{{x:0,y:0}},{r(T['lari'] + .31)});")
        out = T["hookEnd"] - .05
        JS.append(f"tl.to('#card{i}',{{y:-260,duration:.22,ease:EI}},{r(out)});"
                  f"tl.to('#cardP{i}',{{opacity:0,filter:'blur(12px)',duration:.22,ease:EI}},{r(out)});")


def example():
    # ---- 1. hook (frame shrinks in steps on black, cards fill the freed top third) ----
    italic("Macam mana", .04, 2.66, 70, 820, 54, -2, "left")
    italic("nak buat", T["nakBuat"], 2.66, 1000, 820, 54, 2, "right")
    phrase([("AI", T["AI"]), ("nampak", T["nampak"]), ("real", T["real"]), ("macam ni?", T["macamNi"])], 2.66, 540, 1150, 60, 700)
    hook_cards()
    phrase([("Saya", T["saya"]), ("dah", T["dah"]), ("try", T["try_"])], T["tapi1"] - .04, 540, 1340, 50)
    italic("macam-macam", T["mm1"], T["tapi1"] - .04, 540, 1420, 50)
    heavy("PROMPT", T["prompt1"], T["tapi1"] - .02, 540, 1520, 120)
    phrase([("tapi", T["tapi1"]), ("muka", T["muka1"]), ("dia", T["dia"])], T["hookEnd"], 540, 1360, 54)
    bluebox("ASYIK LARI", T["asyik"], T["hookEnd"] + .02, 540, 1460, 96)
    # ---- 2. concept intro: keywords at chest height ----
    italic("Sebenarnya,", T["sebenarnya"], T["sebelum"] - .02, 540, 1060, 58)
    script("sebelum fikir pasal", T["sebelum"], T["korang1"] - .04, 540, 1170, 104, dur=.8)
    heavy("PROMPT", T["prompts"] - .04, T["korang1"] - .04, 540, 1050, 170)
    italic("korang kena ada", T["korang1"], T["character1"] - .03, 540, 1080, 58)
    heavy("CHARACTER", T["character1"] - .03, T["nak2"] - .05, 540, 1070, 150)
    script("Sheet", T["sheet1"], T["nak2"] - .05, 640, 1190, 150, rot=-8, dur=.4)
    italic("dulu.", T["dulu"], T["nak2"] - .05, 860, 1290, 46)
    italic("Nak buat", T["nak2"], T["wajib"] - .04, 70, 880, 52, -2, "left")
    italic("video AI", T["video2"], T["wajib"] - .04, 1000, 880, 52, 2, "right")
    italic("muka", T["muka2"], T["wajib"] - .04, 540, 1090, 60, ital=False, weight=700)
    bluebox("KEKAL SAMA", T["kekal"], T["wajib"] - .04, 540, 1185, 100)
    heavy("WAJIB", T["wajib"] - .02, SRC_END - .02, 540, 1070, 190)
    script("start dari sini", T["start"], SRC_END - .02, 560, 1210, 110, dur=.5)
    # ---- 3. CTA end card on the blurred, darkened freeze (the user's own CTA words) ----
    a = L["cta"]
    HTML.append('<div id="scrim" class="full" style="background:radial-gradient(ellipse at 50% 45%, rgba(0,0,0,0.25), rgba(0,0,0,0.7))"></div>')
    JS.append(f"tl.fromTo('#scrim',{{opacity:0}},{{opacity:1,duration:.4,ease:EO}},{r(a)});")
    italic("Belajar dengan", a + .05, 99, 540, 470, 52)
    heavy("TUTORIAL", a + .1, 99, 540, 600, 150, maxW=900)
    heavy("NAMA", a + .28, 99, 540, 745, 150, maxW=930)
    heavy("BRAND", a + .42, 99, 540, 890, 150, maxW=930)
    HTML.append(f'<div id="uline" style="position:absolute;left:180px;top:975px;width:720px;height:10px;border-radius:5px;background:{PAL["box"]};box-shadow:0 0 20px {PAL["neon"]}"></div>')
    JS.append(f"tl.fromTo('#uline',{{scaleX:0}},{{scaleX:1,duration:.4,ease:EIO}},{r(a + .55)});")
    cta_keyword("KOMEN", "‘INFO’", a + .75, 1135)
    comment_box("INFO", a + 1.15, a + 1.55, a + 2.05)


def cta_keyword(lead, key, a, y):
    """Locked CTA keyword: Archivo Black skewX(-9deg), neon fill, dark stroke, 3-step 3D extrusion, pulse."""
    HTML.append(f'<div class="anc" style="left:540px;top:{y}px;transform:translate(-50%,-50%)"><div id="ctaP"><div id="ctaK" class="ctak">'
                f'<span style="font-family:\'Archivo Black\';font-size:116px;color:#fff;text-shadow:{TEXT_SHADOW}">{esc(lead)}</span>'
                f'<span style="font-family:\'Archivo Black\';font-size:132px;color:{PAL["neon"]};display:inline-block;transform:skewX(-9deg);'
                f'-webkit-text-stroke:3px {PAL["stroke"]};text-shadow:3px 3px 0 {PAL["ex1"]}, 6px 6px 0 {PAL["ex2"]}, 9px 9px 0 {PAL["ex3"]}, 0 0 36px {PAL["neonA"]}">{esc(key)}</span>'
                f'</div></div></div>')
    pop_in("#ctaK", a, .34, .3)
    p0 = a + .65                     # pulse 1 + .035 sin(5 (t - p0)), finite repeats
    reps = max(0, int((TOTAL - p0 - .32) / .628))
    JS.append(f"tl.to('#ctaP',{{scale:1.035,duration:.314,ease:'sine.out'}},{r(p0)});")
    if reps: JS.append(f"tl.fromTo('#ctaP',{{scale:1.035}},{{scale:.965,duration:.628,ease:'sine.inOut',yoyo:true,repeat:{reps - 1},immediateRender:false}},{r(p0 + .314)});")


def comment_box(text, a, ta, send):
    """Comment-box mock typing the CTA word (shows what to type)."""
    chars = "".join(f'<span id="cch{k}" class="cch">{esc(c)}</span>' for k, c in enumerate(text))
    HTML.append(f'<div id="cbox" class="cbox"><div class="cav"></div><div class="ctx"><span id="cph" class="cph">Tambah komen\u2026</span>'
                f'{chars}<span id="caret" class="caret"></span></div>'
                f'<div id="csend" class="csend"><svg width="40" height="40" viewBox="0 0 40 40"><path id="carr" d="M8 20 L32 20 M22 10 L32 20 L22 30" stroke="#fff" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg></div></div>')
    JS.append(f"tl.fromTo('#cbox',{{opacity:0,y:40}},{{opacity:1,y:0,duration:.35,ease:EO}},{r(a)}); tl.set('#caret',{{opacity:0}},0); tl.set('.cch',{{display:'none'}},0);")
    for k in range(len(text)):
        tk = ta + (k + .5) / len(text) * .35          # typewriter: round(len * progress)
        JS.append(f"tl.set('#cch{k}',{{display:'inline'}},{r(tk)});")
    JS.append(f"tl.set('#cph',{{display:'none'}},{r(ta + .5 / len(text) * .35)});")
    f = math.ceil((a + .35) * FPS)
    while f / FPS < send:
        JS.append(f"tl.set('#caret',{{opacity:{1 if math.floor(f / FPS * 3) % 2 == 0 else 0}}},{r(f / FPS)});"); f += 1
    JS.append(f"tl.set('#caret',{{opacity:0}},{r(send)});"
              f"tl.set('#csend',{{backgroundColor:'{PAL['box']}',boxShadow:'0 0 26px {PAL['neonA']}'}},{r(send)}); tl.set('#carr',{{attr:{{stroke:'{INK}'}}}},{r(send)});")
    pop_in("#csend", send, .3, .6)


def camera():
    """Presenter camera for the example (port of Presenter.camera). Frame on black: scale s around its centre,
    position cx/cy, tilt; inner punch-in z at face height; slow push per shot; blur/RGB bumps; shake."""
    BK_, EI_, EIO_, SN = "BK", "EI", "EIO", "SN"
    track("#frame", "scale", 1, [(T["AI"], .9, .22, BK_), (T["real"], .8, .22, BK_), (T["saya"], .6, .3, BK_),
                                 (T["tapi1"], .55, .25, BK_), (T["asyik"], .5, .22, BK_), (T["hookEnd"], 1, .23, EI_)])
    track("#frame", "x", 0, [(T["AI"], 16, .22), (T["real"], -14, .22), (T["saya"], 0, .3), (T["asyik"], 8, .22), (T["hookEnd"], 0, .23, EI_)])
    track("#frame", "y", 0, [(T["real"], 30, .22), (T["saya"], 290, .3, BK_), (T["tapi1"], 310, .25), (T["asyik"], 330, .22), (T["hookEnd"], 0, .23, EI_)])
    track("#frame", "rotation", 0, [(T["AI"], .8, .22), (T["real"], -1.2, .22), (T["saya"], 0, .3), (T["asyik"], 1, .22), (T["hookEnd"], 0, .2)])
    track("#zoom", "scale", 1, [(CUT["B"], 1.14, .01), (CUT["B"] + .01, 1.0, .4), (T["prompts"], 1.1, .12, SN), (T["korang1"], 1.03, .35),
                                (T["character1"], 1.2, .12, SN), (T["nak2"], 1.0, .12), (T["kekal"], 1.1, .12, SN), (T["wajib"], 1.2, .12, SN),
                                (T["sini"] + .2, 1.0, .25), (L["cta"], 1.22, 3.5)])
    shot_push(list(CUT.values()))
    bump_blur(T["hookEnd"], CUT["B"] + .06, 11)
    for a, b, amp in [(T["lari"] - .02, T["lari"] + .2, 14), (CUT["B"] - .08, CUT["B"] + .14, 18),
                      (T["character1"] - .02, T["character1"] + .16, 10), (L["cta"] - .05, L["cta"] + .2, 18)]:
        bump_rgb(a, b, amp)
    shake(T["lari"], .25, 8, 6, 5, 9)
    emit_fx()
    # end card: blur 13 px + brightness x0.44 on the freeze, 0.5 s ease-out from the CTA start
    JS.append(f"tl.set('#fx',{{filter:'blur(0px) brightness(1)'}},{r(L['cta'])});"
              f"tl.to('#fx',{{filter:'blur(13px) brightness(0.44)',duration:.5,ease:EO}},{r(L['cta'])});")
    flash(CUT["B"], .85, "#ffffff", .06, .22)
    flash(T["character1"], .28)
    flash(L["cta"] + .03, .75, "#bfefff" if PAL["box"] == "#14B8F0" else "#d8ffd6", .05, .35)


# ================================================================= page
camera()
example()
CUT_HTML = "".join(f'<video id="{k}" class="cutv" src="assets/{k}.webm" muted playsinline data-start="{a}" data-duration="{r(b - a)}" data-track-index="{2 + n}"></video>'
                   for n, (k, (a, b)) in enumerate(CUTOUTS.items()))
JS.insert(0, "tl.set('#backdrop',{opacity:0},0);")   # black behind the frame unless an explainer fades the room
JS.append(f"tl.fromTo('#grid',{{backgroundPosition:'0px 0px'}},{{backgroundPosition:'0px 60px',duration:5,ease:'none',repeat:{max(0, int(TOTAL / 5))},immediateRender:false}},0);")

FONTS = """
@font-face { font-family: "InterV"; src: url("assets/fonts/inter-latin-wght-normal.woff2") format("woff2"); font-weight: 100 900; }
@font-face { font-family: "ArchivoV"; src: url("assets/fonts/archivo-latin-wdth-normal.woff2") format("woff2"); font-weight: 100 900; font-stretch: 62% 125%; }
@font-face { font-family: "Sacramento"; src: url("assets/fonts/Sacramento-400.woff2") format("woff2"); font-weight: 400; }
"""

page = f"""<!doctype html>
<html lang="ms">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width={W}, height={H}" />
<title>Glow Keyword</title>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/CustomEase.min.js"></script>
<style>
{FONTS}
  body {{ margin:0; background:#000; }}
  #root {{ position:relative; width:100%; height:100%; overflow:hidden; background:#000; color:#fff; font-family:InterV, sans-serif; }}
  .full {{ position:absolute; left:0; top:0; width:{W}px; height:{H}px; }}
  #frame {{ overflow:hidden; box-shadow:0 30px 80px rgba(0,0,0,0.6); }}
  #frame video, #frame img {{ position:absolute; left:0; top:0; width:{W}px; height:{H}px; object-fit:cover; }}
  #backdrop {{ background:radial-gradient(ellipse at 50% 18%, {PAL['glow'].replace('0.55', '0.13')}, rgba(0,0,0,0) 55%), #040504; }}
  #grid {{ opacity:.5; background-image:linear-gradient(rgba(255,255,255,0.035) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.035) 1px, transparent 1px); background-size:60px 60px; }}
  .anc {{ position:absolute; white-space:nowrap; }}
  .it {{ font-family:InterV, sans-serif; letter-spacing:-0.01em; text-shadow:{TEXT_SHADOW}; line-height:1.2; }}
  .ph {{ display:flex; white-space:nowrap; font-family:InterV, sans-serif; color:#fff; line-height:1.2; }}
  .pw {{ display:inline-block; text-shadow:{TEXT_SHADOW}; }}
  .hvb {{ position:relative; white-space:nowrap; font-family:'Archivo Black', sans-serif; line-height:1; letter-spacing:-0.02em; }}
  .hvb span {{ position:absolute; left:0; top:0; white-space:nowrap; }}
  .hvb .sz {{ position:static; visibility:hidden; }}
  .hvb .sp {{ mix-blend-mode:screen; opacity:0.85; }}
  .bx {{ background:{PAL['box']}; border-radius:6px; box-shadow:0 6px 24px rgba(0,0,0,0.35), 0 0 22px {PAL['glow'].replace('0.55', '0.35')}; }}
  .bt {{ font-family:ArchivoV, sans-serif; font-style:italic; font-weight:700; font-stretch:80%; line-height:1.08; color:{INK}; white-space:nowrap; letter-spacing:0.005em; }}
  .sc {{ font-family:Sacramento, cursive; line-height:1.15; color:{PAL['text']}; white-space:nowrap; padding:0 30px; text-shadow:{NEON_GLOW}; }}
  .card {{ position:absolute; width:260px; height:330px; }}
  .cardP {{ position:absolute; inset:0; }}
  .cardIn {{ position:absolute; inset:0; background:#f6f6f2; border-radius:12px; box-shadow:0 18px 40px rgba(0,0,0,0.55); }}
  .av {{ position:absolute; left:12px; top:12px; width:236px; height:236px; overflow:hidden; border-radius:4px; }}
  .avl {{ position:absolute; inset:0; }}
  .clab {{ position:absolute; left:0; right:0; top:256px; text-align:center; font-family:InterV, sans-serif; font-weight:800; font-size:30px; color:#161616; letter-spacing:0.02em; }}
  .qm {{ position:absolute; left:175px; top:-70px; font-family:'Archivo Black', sans-serif; font-size:120px; line-height:1.2; color:{PAL['text']}; text-shadow:{NEON_GLOW}; }}
  .flash {{ position:absolute; left:0; top:0; width:{W}px; height:{H}px; mix-blend-mode:screen; opacity:0; pointer-events:none; }}
  .ctak {{ display:flex; align-items:center; gap:26px; white-space:nowrap; }}
  .cbox {{ position:absolute; left:130px; top:1265px; width:820px; height:104px; border-radius:52px; background:rgba(255,255,255,0.12); border:2px solid rgba(255,255,255,0.3); box-sizing:border-box; }}
  .cav {{ position:absolute; left:18px; top:14px; width:72px; height:72px; border-radius:36px; background:rgba(255,255,255,0.25); }}
  .ctx {{ position:absolute; left:112px; top:0; height:100px; display:flex; align-items:center; font-family:InterV, sans-serif; font-weight:700; font-size:44px; color:#fff; }}
  .cph {{ color:rgba(255,255,255,0.55); }}
  .cch {{ color:#fff; }}
  .caret {{ display:inline-block; width:3px; height:46px; margin-left:3px; background:{PAL['neon']}; }}
  .csend {{ position:absolute; left:722px; top:10px; width:80px; height:80px; border-radius:40px; background:rgba(255,255,255,0.25); display:flex; align-items:center; justify-content:center; }}
</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-width="{W}" data-height="{H}" data-duration="{TOTAL}">

  <audio id="mix" src="assets/mix.wav" data-start="0" data-duration="{TOTAL}" data-track-index="30" data-volume="1"></audio>

  <svg width="0" height="0" style="position:absolute">
    <defs>
      <filter id="rgbv" x="-5%" y="-5%" width="110%" height="110%" color-interpolation-filters="sRGB">
        <feColorMatrix in="SourceGraphic" type="matrix" values="1 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 1 0" result="r" />
        <feOffset id="rgbR" in="r" dx="0" dy="0" result="r2" />
        <feColorMatrix in="SourceGraphic" type="matrix" values="0 0 0 0 0  0 1 0 0 0  0 0 0 0 0  0 0 0 1 0" result="g" />
        <feColorMatrix in="SourceGraphic" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 1 0 0  0 0 0 1 0" result="b" />
        <feOffset id="rgbB" in="b" dx="0" dy="0" result="b2" />
        <feBlend in="r2" in2="g" mode="screen" result="rg" />
        <feBlend in="rg" in2="b2" mode="screen" />
      </filter>
    </defs>
  </svg>

  <!-- explainer backdrop (shows only where the room is faded out): near-black + faint brand radial + drifting 60 px grid -->
  <div id="backdrop" class="full"><div id="grid" class="full"></div></div>

  <!-- footage stack: shake > blur/dim > RGB split > frame (scale/position/tilt on black) > punch-in zoom > shot push -->
  <div id="shake" class="full"><div id="fx" class="full"><div id="rgbw" class="full">
    <div id="frame" class="full"><div id="zoom" class="full" style="transform-origin:540px {FOCUS_Y}px"><div id="push" class="full" style="transform-origin:540px {FOCUS_Y}px">
      {CUT_HTML}
      <div id="room" class="full">
        <img id="lastf" src="assets/lastframe.jpg" alt="" />
        <video id="aroll" src="assets/graded.mp4" muted playsinline data-start="0" data-duration="{SRC_END}" data-track-index="0"></video>
      </div>
    </div></div></div>
  </div></div></div>

  <!-- text + graphics -->
  {chr(10).join('  ' + h for h in HTML)}

  {chr(10).join('  ' + f for f in FLASHES)}
</div>
<script>
gsap.registerPlugin(CustomEase);
const EO = CustomEase.create('eo', 'M0,0 C0.16,1 0.3,1 1,1');      // EASE_OUT
const EI = CustomEase.create('ei', 'M0,0 C0.7,0 0.84,0 1,1');      // EASE_IN
const EIO = CustomEase.create('eio', 'M0,0 C0.65,0 0.35,1 1,1');   // EASE_IO
const BK = CustomEase.create('bk', 'M0,0 C0.34,1.56 0.64,1 1,1');  // overshoot pop
const SN = CustomEase.create('sn', 'M0,0 C0.05,0.9 0.1,1 1,1');    // punch-in snap
// auto-fit every line to its max width (data-fit); only font-size changes, never the timeline
const fitAll = () => document.querySelectorAll('[data-fit]').forEach(el => {{
  if (!el.dataset.fs) el.dataset.fs = parseFloat(el.style.fontSize);
  const fs = +el.dataset.fs, max = +el.dataset.fit;
  el.style.fontSize = fs + 'px';
  const w = el.scrollWidth;
  if (w > max) el.style.fontSize = (fs * max / w).toFixed(2) + 'px';
  if (el.dataset.stroke) el.style.webkitTextStroke = Math.max(1, parseFloat(el.style.fontSize) / +el.dataset.stroke).toFixed(2) + 'px ' + getComputedStyle(el).color;
}});
fitAll();
if (document.fonts) document.fonts.ready.then(fitAll);

const tl = gsap.timeline({{ paused: true }});
{chr(10).join(JS)}
window.__timelines['main'] = tl;
</script>
</body>
</html>
"""
os.makedirs(os.path.join(ROOT, "hf"), exist_ok=True)
open(os.path.join(ROOT, "hf", "index.html"), "w").write(page)
print("wrote hf/index.html", len(JS), "timeline lines")
