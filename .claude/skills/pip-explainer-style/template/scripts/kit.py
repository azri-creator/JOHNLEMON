"""PiP Explainer kit: the locked identity as reusable HTML + GSAP pieces (palette, type, Panel camera, Title, Chip,
Slam, Card, Tick, icons, shakes). Scenes in scenes.py are built from these. Do not change the numbers per video;
they are the style (see references/style_spec.md)."""
import math, os

W, H, FPS = 1080, 1920, 30
HF = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "hf"))

# ---- client palette (estimated from the logo, not an official brand guide). Swap for the student's brand if asked. ----
C = dict(navy="#061329", navy2="#0A1D3D", card="#0C2147", cyan="#00CFF5", blue="#087BEE", yellow="#FFE600",
         white="#FFFFFF", mute="rgba(255,255,255,0.62)", line="rgba(0,207,245,0.35)")
SHADOW = "0 3px 14px rgba(0,0,0,0.55), 0 0 2px rgba(0,0,0,0.4)"
GLOW_C = "0 0 18px rgba(0,207,245,0.55), 0 0 40px rgba(8,123,238,0.35)"
GLOW_Y = "0 0 18px rgba(255,230,0,0.55), 0 0 42px rgba(255,190,0,0.3)"

# ---- type: bold sans titles + ONE serif-italic accent word ----
INTER, HEAVY = "Inter", "Archivo Black"  # bundled in HyperFrames, no @font-face needed
_IS = os.path.join(HF, "assets", "fonts", "InstrumentSerif-Italic.woff2")
if os.path.exists(_IS):  # the original accent face; drop the OFL file in hf/assets/fonts/ to use it
    SERIF, SERIF_K = "Instrument Serif", 1.18
    FONT_FACE = "@font-face { font-family: 'Instrument Serif'; font-style: italic; font-weight: 400; src: url('assets/fonts/InstrumentSerif-Italic.woff2') format('woff2'); }"
else:  # bundled fallback with the same high-contrast display-italic feel (a little wider, so a smaller factor)
    SERIF, SERIF_K, FONT_FACE = "Playfair Display", 1.06, ""

# ---- geometry (reference layout) ----
PIP = dict(x=30, y=1372, w=1020, h=508, r=40, k=0.6, src_top=430)  # presenter card at the bottom
FULL = dict(z=1.2, ox=540, oy=1500, face_x=530, face_y=830)        # 1.2x crop off the head-room, punch pivot = face
CAP_Y = dict(full=1210, pip=1296)                                  # caption centre line per layout
SLAM_Y = 1440

# Archivo Black advance widths (em), measured in the render browser. Used by fit() so slams stay <= 960 px.
_AB = {" ": .333, "%": 1.0, "?": .611, "!": .333, "=": .66, ".": .333, ",": .333, "-": .333, "“": .444, "”": .444, '"': .5, "'": .18,
       **{d: .667 for d in "0123456789"}, "A": .778, "B": .778, "C": .778, "D": .778, "E": .722, "F": .667, "G": .833, "H": .833,
       "I": .389, "J": .667, "K": .833, "L": .667, "M": .944, "N": .833, "O": .833, "P": .722, "Q": .833, "R": .778, "S": .722,
       "T": .722, "U": .833, "V": .778, "W": 1.0, "X": .778, "Y": .778, "Z": .722}


def fit(text, size, max_w=960):
    w = sum(_AB.get(ch.upper(), .75) for ch in text) * size - 0.01 * size * len(text)
    return round(size * max_w / w, 1) if w > max_w else size


# ---- deterministic noise + shakes (same maths as the Remotion original) ----
def noise(seed):
    x = math.sin(seed * 12.9898 + 78.233) * 43758.5453
    return x - math.floor(x)


def shake_js(sel, a, dur, amp, seed=1):
    """per-frame seeded jitter on a wrapper (x/y only), decaying to 0"""
    out, f0, f1 = [], int(math.ceil(a * FPS)), int(math.floor((a + dur) * FPS))
    for f in range(f0, f1 + 1):
        t = f / FPS; k = 1 - (t - a) / dur
        x = (noise(f + seed) - 0.5) * 2 * amp * k; y = (noise(f * 1.7 + seed) - 0.5) * 2 * amp * k
        out.append(f"tl.set('{sel}', {{ x: {x:.2f}, y: {y:.2f} }}, {t:.4f});")
    out.append(f"tl.set('{sel}', {{ x: 0, y: 0 }}, {(f1 + 1) / FPS:.4f});")
    return "\n".join(out)


# ---- HTML pieces ----
def anchor(x, y, inner, id_="", extra=""):
    """zero-size box at (x, y) whose child is centred on that point (no CSS transform, so GSAP can scale the child)"""
    i = f' id="{id_}"' if id_ else ""
    return (f'<div{i} class="anc" style="left:{x}px;top:{y}px;{extra}">{inner}</div>')


def title(id_, text, y=205, size=66, accent=None):
    """bold sans title with ONE serif-italic accent word, written as 'Sumber *trafik*'"""
    accent = accent or C["yellow"]
    parts = []
    for p in [s for s in __import__("re").split(r"(\*[^*]+\*)", text) if s]:
        if p.startswith("*"):
            parts.append(f'<span class="acc" style="font-size:{size * SERIF_K:.0f}px;color:{accent}"> {p[1:-1]} </span>')
        else:
            parts.append(f"<span>{p}</span>")
    return f'<div id="{id_}" class="title hide" style="top:{y}px;font-size:{size}px">{"".join(parts)}</div>'


def chip(id_, x, y, text, color="rgba(0,207,245,0.16)", ink=None, size=30, icon=""):
    ink = ink or C["cyan"]
    inner = (f'<div id="{id_}" class="chip hide" style="background:{color};color:{ink};border:2px solid {ink};'
             f'padding:{size * .32:.0f}px {size * .8:.0f}px;font-size:{size}px;gap:{size * .35:.0f}px">{icon}{text}</div>')
    return anchor(x, y, inner)


def label(id_, x, y, html, size=36):
    return anchor(x, y, f'<div id="{id_}" class="lbl hide" style="font-size:{size}px">{html}</div>')


def Y(s):
    return f'<span style="color:{C["yellow"]}">{s}</span>'


def card(id_, style, inner="", border=None, glow=None, cls="hide"):
    b = border or C["line"]
    g = f", {glow}" if glow else ""
    return (f'<div id="{id_}" class="card {cls}" style="border-color:{b};box-shadow:0 24px 60px rgba(0,0,0,0.55){g};{style}">{inner}</div>')


def slam(id_, text, size=150, box=False, sub="", icon="", y=SLAM_Y):
    """big kinetic word for FULL close-ups (below the caption line, above the platform UI)"""
    fs = fit(text, size, 960 - (130 if icon else 0) - (68 if box else 0))
    style = (f"font-size:{fs}px;color:{C['navy'] if box else '#fff'};background:{C['yellow'] if box else 'transparent'};"
             f"padding:{'14px 34px 18px' if box else '0'};box-shadow:{GLOW_Y if box else 'none'};"
             f"text-shadow:{'none' if box else SHADOW + ', 0 0 30px rgba(0,0,0,0.5)'}")
    s = (f'<div id="{id_}_s" class="slamsub" style="font-size:{size * .62:.0f}px">{sub}</div>') if sub else ""
    inner = f'<div id="{id_}" class="slam hide"><div id="{id_}_k" class="slamrow" style="{style}">{icon}{text}</div>{s}</div>'
    return anchor(540, y, inner)


def tick_svg(id_, size=70):
    return (f'<svg id="{id_}" width="{size}" height="{size}" viewBox="0 0 70 70" style="flex:none">'
            f'<circle id="{id_}_c" cx="35" cy="35" r="31" fill="none" stroke="rgba(255,255,255,0.35)" stroke-width="4" opacity="0.25"/>'
            f'<path id="{id_}_p" d="M21 36 L31 46 L50 25" fill="none" stroke="{C["navy"]}" stroke-width="7" stroke-linecap="round" '
            f'stroke-linejoin="round" stroke-dasharray="45" stroke-dashoffset="45"/></svg>')


# ---- line icons (currentColor style) ----
def _ic(body, size=64, color="#fff", sw=5):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 64 64" fill="none" stroke="{color}" stroke-width="{sw}" '
            f'stroke-linecap="round" stroke-linejoin="round" style="flex:none">{body}</svg>')


ICONS = {
    "eye": '<path d="M4 32 C14 16 50 16 60 32 C50 48 14 48 4 32Z"/><circle cx="32" cy="32" r="8"/>',
    "cart": '<path d="M6 10h8l7 30h30l6-20H18"/><circle cx="25" cy="52" r="4"/><circle cx="47" cy="52" r="4"/>',
    "shield": '<path d="M32 5 L54 13 V30 C54 44 44 54 32 59 C20 54 10 44 10 30 V13Z"/><path d="M22 32 L29 39 L43 24"/>',
    "box": '<path d="M32 6 L56 18 V46 L32 58 L8 46 V18Z"/><path d="M8 18 L32 30 L56 18 M32 30 V58"/>',
    "cam": '<rect x="6" y="18" width="36" height="30" rx="6"/><path d="M42 28 L58 20 V46 L42 38"/>',
    "chart": '<path d="M8 56 H58"/><rect x="12" y="36" width="9" height="16"/><rect x="28" y="26" width="9" height="26"/><rect x="44" y="12" width="9" height="40"/>',
    "quote": '<path d="M8 12 H56 V44 H30 L18 56 V44 H8Z"/><path d="M20 26 h24 M20 34 h16"/>',
    "bot": '<rect x="10" y="20" width="44" height="34" rx="10"/><path d="M32 8 V20"/><circle cx="32" cy="7" r="3"/><circle cx="24" cy="36" r="3"/><circle cx="40" cy="36" r="3"/><path d="M25 46 h14"/>',
    "up": '<path d="M32 56 V10 M14 28 L32 10 L50 28"/>',
    "rocket": '<path d="M32 4 C44 14 46 30 40 44 H24 C18 30 20 14 32 4Z"/><circle cx="32" cy="22" r="5"/><path d="M24 44 L16 54 L26 50 M40 44 L48 54 L38 50 M28 50 L32 60 L36 50"/>',
}


def icon(name, size=64, color="#fff", sw=5):
    return _ic(ICONS[name], size, color, sw)


# ---- CSS for the whole kit ----
CSS = f"""
{FONT_FACE}
* {{ margin:0; padding:0; box-sizing:border-box; }}
html, body {{ margin:0; width:{W}px; height:{H}px; overflow:hidden; background:{C['navy']}; }}
#root {{ position:relative; width:100%; height:100%; overflow:hidden; background:{C['navy']}; font-family:'{INTER}', sans-serif; color:#fff; }}
.layer {{ position:absolute; left:0; top:0; width:{W}px; height:{H}px; }}
.hide {{ opacity:0; }}
.anc {{ position:absolute; width:0; height:0; display:flex; align-items:center; justify-content:center; }}
.anc > * {{ flex:none; }}
.panel {{ transform-origin:540px 700px; }}
.title {{ position:absolute; left:0; width:{W}px; text-align:center; font-weight:800; color:#fff; letter-spacing:-0.02em;
         text-shadow:{SHADOW}; white-space:nowrap; line-height:1.15; }}
.acc {{ font-family:'{SERIF}', serif; font-style:italic; font-weight:400; letter-spacing:0; }}
.serif {{ font-family:'{SERIF}', serif; font-style:italic; font-weight:400; }}
.heavy {{ font-family:'{HEAVY}', sans-serif; font-weight:400; }}
.chip {{ border-radius:999px; font-weight:700; white-space:nowrap; display:flex; align-items:center; }}
.lbl {{ font-weight:800; color:#fff; white-space:nowrap; text-shadow:{SHADOW}; }}
.card {{ position:absolute; background:linear-gradient(180deg, {C['card']}, {C['navy2']}); border:2px solid {C['line']};
        border-radius:30px; overflow:hidden; }}
.slam {{ display:flex; flex-direction:column; align-items:center; }}
.slamrow {{ display:flex; align-items:center; gap:24px; font-family:'{HEAVY}', sans-serif; line-height:1; white-space:nowrap;
           border-radius:18px; letter-spacing:-0.01em; }}
.slamsub {{ font-family:'{SERIF}', serif; font-style:italic; color:{C['yellow']}; margin-top:6px; text-shadow:{SHADOW}; }}
.cap {{ position:absolute; left:60px; width:{W - 120}px; top:0; height:0; display:flex; align-items:center; justify-content:center; }}
.capin {{ font-weight:800; font-size:64px; line-height:1.1; letter-spacing:-0.015em; white-space:nowrap; text-align:center; }}
.capin span {{ text-shadow:{SHADOW}, 0 0 3px rgba(0,0,0,0.6); }}
.media {{ position:absolute; left:0; top:0; width:100%; height:100%; object-fit:cover; }}
.aitag {{ position:absolute; left:14px; top:14px; background:{C['yellow']}; color:{C['navy']}; font-weight:900; font-size:26px;
         padding:4px 12px; border-radius:8px; }}
"""

# ---- GSAP helpers (inserted before the scene code; every helper adds tweens to the one paused timeline `tl`) ----
JS = """
const E = { out: 'expo.out', snap: 'expo.out', back: 'back.out(1.8)', in: 'expo.in', io: 'power3.inOut', lin: 'none', sine: 'sine.inOut' };
// Panel camera: push in from 1.14x + blur 14 px -> 1.0 sharp in 0.42 s, drift +3.5 %, snap out in 0.1 s. Main motion of the style.
function panel(id, a, b, from = 1.14, drift = 0.035) {
  tl.set('#' + id, { opacity: 1 }, a);
  tl.fromTo('#' + id, { scale: from, filter: 'blur(14px)' }, { scale: 1, filter: 'blur(0px)', duration: 0.42, ease: E.out, immediateRender: false }, a);
  tl.set('#' + id, { filter: 'none' }, a + 0.43);
  tl.fromTo('#' + id + '_d', { scale: 1 }, { scale: 1 + drift, duration: Math.max(0.2, b - a - 0.12), ease: E.lin, immediateRender: false }, a);
  tl.fromTo('#' + id, { filter: 'blur(0px)' }, { scale: 1.06, filter: 'blur(8px)', opacity: 0, duration: 0.1, ease: E.in, immediateRender: false }, b - 0.1);
  tl.set('#' + id, { opacity: 0, filter: 'none' }, b);
}
function title(id, a) {
  tl.fromTo('#' + id, { opacity: 0, y: 24, filter: 'blur(8px)' }, { opacity: 1, y: 0, filter: 'blur(0px)', duration: 0.35, ease: E.out, immediateRender: false }, a);
  tl.set('#' + id, { filter: 'none' }, a + 0.36);
}
function swapOut(id, a, d = 0.06) { tl.to('#' + id, { opacity: 0, duration: d, ease: E.lin }, a); }
// pop: scale from `from` with overshoot + fast fade (chips, labels, stamps)
function pop(id, a, d = 0.3, from = 0.6, ease = E.back) {
  tl.fromTo('#' + id, { scale: from }, { scale: 1, duration: d, ease: ease, immediateRender: false }, a);
  tl.fromTo('#' + id, { opacity: 0 }, { opacity: 1, duration: d * 0.4, ease: E.lin, immediateRender: false }, a);
}
// pop with blur-in (cards, big words)
function popBlur(id, a, d = 0.3, from = 0.55) {
  tl.fromTo('#' + id, { scale: from }, { scale: 1, duration: d, ease: E.back, immediateRender: false }, a);
  tl.fromTo('#' + id, { filter: 'blur(10px)' }, { filter: 'blur(0px)', duration: d * 0.6, ease: 'power2.out', immediateRender: false }, a);
  tl.fromTo('#' + id, { opacity: 0 }, { opacity: 1, duration: d / 3, ease: E.lin, immediateRender: false }, a);
  tl.set('#' + id, { filter: 'none' }, a + d + 0.01);
}
function fadeIn(id, a, d = 0.3) { tl.fromTo('#' + id, { opacity: 0 }, { opacity: 1, duration: d, ease: E.out, immediateRender: false }, a); }
function slideIn(id, a, from, d = 0.35, ease = E.out) {
  tl.fromTo('#' + id, Object.assign({}, from), Object.assign({ x: 0, y: 0, rotation: 0, duration: d, ease: ease, immediateRender: false }, ), a);
  tl.fromTo('#' + id, { opacity: 0 }, { opacity: 1, duration: d * 0.5, ease: E.lin, immediateRender: false }, a);
}
// tick: yellow disc + drawn check
function tick(id, a, d = 0.3) {
  tl.set('#' + id + '_c', { attr: { fill: '#FFE600', stroke: '#FFE600' } }, a + 0.02);
  tl.fromTo('#' + id + '_c', { opacity: 0.25 }, { opacity: 1, duration: d * 0.5, ease: E.out, immediateRender: false }, a);
  tl.fromTo('#' + id + '_p', { attr: { 'stroke-dashoffset': 45 } }, { attr: { 'stroke-dashoffset': 0 }, duration: d, ease: E.out, immediateRender: false }, a);
}
// slam word (FULL): scale 1.6 -> 1 BACK + blur-in + short shake, exit 0.14 s. Blur never rides an overshooting ease.
function slam(id, a, b, sub = false) {
  tl.set('#' + id, { opacity: 1 }, a);
  tl.fromTo('#' + id, { scale: 1.6 }, { scale: 1, duration: 0.22, ease: E.back, immediateRender: false }, a);
  tl.fromTo('#' + id, { filter: 'blur(10px)' }, { filter: 'blur(0px)', duration: 0.15, ease: 'power2.out', immediateRender: false }, a);
  tl.set('#' + id, { filter: 'none' }, a + 0.23);
  for (let i = 0; i <= 8; i++) { const t = i / 30; tl.set('#' + id, { x: i < 8 ? Math.sin(t * 90) * 10 * (1 - t / 0.25) : 0 }, a + t); }
  if (sub) tl.fromTo('#' + id + '_s', { opacity: 0 }, { opacity: 1, duration: 0.25, ease: E.out, immediateRender: false }, a + 0.15);
  tl.fromTo('#' + id, { filter: 'blur(0px)' }, { scale: 0.8, opacity: 0, filter: 'blur(8px)', duration: 0.14, ease: E.in, immediateRender: false }, b - 0.14);
  tl.set('#' + id, { filter: 'none' }, b);
}
// fast counter (text via a proxy, seek-safe)
function counter(id, a, d, to, suffix = '') {
  const el = document.getElementById(id), o = { v: 0 };
  tl.fromTo(o, { v: 0 }, { v: to, duration: d, ease: E.out, immediateRender: false, onUpdate: () => { el.textContent = Math.round(o.v) + suffix; } }, a);
}
// dash-draw an SVG path / shape
function draw(id, a, d, len, ease = E.io) {
  tl.fromTo('#' + id, { attr: { 'stroke-dasharray': len, 'stroke-dashoffset': len } }, { attr: { 'stroke-dashoffset': 0 }, duration: d, ease: ease, immediateRender: false }, a);
}
"""
