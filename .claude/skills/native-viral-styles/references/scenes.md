# Effect modules (`template/scripts/scenes/*.html`)

Each module is a HyperFrames sub-composition (1080×1920, transparent root) with `/*COMMON*/` replaced by
`common.css`. Times inside a module are **local** (0 = host start). The comment `// local 0 = …` records the global
offset used in the reference build. Change coordinates and word-synced times per video. Use a module only when the
words call for it.

| Module | Layer | Use when the presenter says… | What it does | Edit per video |
|---|---|---|---|---|
| `hud.html` | screen | "zoom in / zoom out" | Four white viewfinder brackets tighten onto the face, a centre crosshair, readout `ZOOM 1.0×→1.6×` in JetBrains Mono with the value in `#FFE600` (set by stepped `textContent`) | R0/R1 rectangles, step times matching the CAM zoom |
| `keyf.html` | screen | "tanpa sentuh keyframe" / "no editing" | Glass timeline panel with 6 white diamonds, a playhead sweep, red ✕ on each, a counter 6→0, then a white pill "0 keyframe ✓" | diamond times on the words |
| `clock.html` | screen | "jimat masa" / time saved | Glass dial with hands spinning backwards, a yellow arc filling, "Jimat masa" text, then the dial slides left and three task chips get yellow checks | labels of the 3 chips |
| `power.html` | in-camera | "power" / "level" / hype build | Matte duplicate with a blue drop-shadow aura under a clean matte top layer, rising particles, a vertical "AI LEVEL" meter stepping to MAX on the words, a double shockwave ring on the punch word | meter step times, label |
| `orbit.html` | in-camera | "letakkan video … sekeliling saya secara 3D", then "kumpul … dekat tangan … hilangkan" | CSS-3D stage with a person plane at z=0 and six video cards orbiting (ω 0.95 rad/s, rx 470, rz 420), so they pass behind and in front of the presenter. Spawn glows; orbit tilt 16° on "3D". The gather spirals the cards into the palm track `HK`, then a blue-white orb rides the hand, is thrown up on a Bezier and implodes with 40 particles and a ring. Fully analytic in `hf-seek` | card sources/sizes, `YO` heights, `HK` hand keys, throw end point, spawn/gather times |
| `super.html` | in-camera | "super power" / climax | Blue-white aura, two seeded lightning strikes with branches, radial speed lines. The headline itself comes from the caption system (glitch flag) | strike times |
| `laptop.html` | screen | "kena ada X dan Y je" | Two glass cards with outline icons (laptop, wifi), a "+" between, white check badges | icons/labels |
| `slot.html` | screen | "any content / apa-apa" | Glass window with a reel of content types decelerating (`power4.out`) onto the last item, then flipping to "✓ Automate" | reel words, final word |
| `motion.html` | screen | "boleh buat video motion macam ni" / show an example | Chip "Tanpa footage sendiri" with a camera-off icon, then the example video zooms through from a card to full screen, with a PiP of the presenter (bottom-left, white border) | example clip + media start, PiP crop |
| `alasan.html` | in-camera | rhetorical question build | A radial vignette slowly tightens during the camera push, then is set to 0 on the hard-cut punchline | timing only |
| `cta.html` | screen | final call to action | Bottom dark gradient, brand logo, lime CTA button with a pulse and an arrow bob, seeded confetti on "tekan" | logo, button text |

## Adding a module

Write it with element arrays instead of JS-built ids, use `fromTo` with `immediateRender:false` for anything that
appears later, use `gsap.set` for initial rotations, and put cards and panels between y 860 and 1300. For a 3D effect
that must interleave with the presenter, follow `orbit.html`: one `preserve-3d` stage holding a person plane at z=0,
positions computed from global time in an `hf-seek` listener, and the root `#pmatw` hidden for that window.
