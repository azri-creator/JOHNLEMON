# Clean Launch Motion: style spec (locked numbers)

All values are from the approved client "Belajar AI (Coach Am)" ad (first built in Remotion, now ported 1:1 to HyperFrames). They live in `template/scripts/index.tpl.html` (CSS tokens on `:root`, surfaces) and `template/scripts/lib.js` (eases, timings, helpers).

## Canvas and safe area
- The canvas is 1080×1920 at 30 fps.
- Keep all important text between y≈250 and y≈1600. The bottom ~320 px sits under platform UI (TikTok/Reels captions and buttons), and the right ~120 px sits under the action rail.
- Headlines auto-fit to **880 px** wide (default `data-max`), so camera step-zooms (up to ~1.12×) never push text off frame.

## Palette (sampled from the reference, compressed-stream ±3)
| Token | Hex | Use |
|---|---|---|
| bg | `#FAF6FE` | Stage, every scene. It carries two very faint drifting glows (`rgba(124,192,249,.16)` top-left, `rgba(183,166,248,.12)` bottom-right). |
| ink | `#24243A` | Main dark type. |
| inkSoft | `#5B5B72` | Secondary labels. |
| blueDeep → blue → blueLight | `#2B7CF5` → `#4898F8` → `#7CC0F9` | The **blue gradient** (90°), used for emphasis words, buttons, progress, the sparkle. |
| royal | `#0048E0` | Rare, saturated emphasis. |
| cyan / indigo | `#00A9EB` / `#4858F8` | Small accents and confetti. |
| confetti extras | `#F3A8D8`, `#B7A6F8` | Only in restrained confetti. |

Never drift into dark charcoal stages, neon/cyberpunk, yellow/black stomp type or busy collage. Real screenshots may keep their own (even dark) UI; the stage around them stays light.

## Typography
- **Inter** (SIL OFL) at weight 500 for headlines, 600–700 for chips and buttons. Tracking is −0.025 em.
- Headline sizes are 84–104 px (a hook can go to ~124 px), with the tagline at 64 px. Chips are 22–32 px, button labels 48–50 px, card body text 42–50 px. Nothing that must be read goes below ~26 px.
- Emphasis comes from colour alone (the blue gradient on 1–2 words), never from bold or italic.
- Phrases are short, 1–5 words, centred, and change with the VO.

## Surfaces
- **Cards:** white, radius 26–36, padding 30–42. Shadows:
  - soft: `0 30px 80px rgba(46,72,140,.16), 0 8px 24px rgba(46,72,140,.10)`
  - deep: `0 60px 140px rgba(40,60,120,.24), 0 18px 40px rgba(40,60,120,.14)`
- **Phone:** width 600–760; height = width × 2.13; radius = width × 0.14; bezel = width × 0.028 with a dark gradient `#2a2d36→#0d0f14`; dynamic-island pill.
  - Typical perspective: 2400, rotateX 22°, rotateY 9°, rotateZ −8°, vanishing point at the frame centre. In HyperFrames: `poseTo(el, {rx, ry, rz, vp}, …)` with per-element `transformPerspective` (never a preserve-3d stage). `vp` = frame centre minus plane centre, e.g. `[0, -404]` for a phone centred at y 1364.
  - Place the phone so its bottom is cropped by the frame edge.
- **Chips:** pill shape. Blue tint `rgba(72,152,248,.12)` with blueDeep text, or white with a soft shadow, or ink with white text (used for "CONTOH").
- **Highlight:** a rounded stroke of 5 px in blueDeep that draws on (dash offset), with a glow `drop-shadow(0 0 10px rgba(72,152,248,.55))`, 8% blue fill and an optional white label chip.
- **Button:** 740×136, pill, blue gradient, `0 26px 60px rgba(43,124,245,.35)`, white Inter 700 at ~50 px. Use the user's exact label.

## Easing and durations
- `EASE_OUT = bezier(0.16,1,0.3,1)` for expo-like settles (entrances). `EASE_IN = bezier(0.7,0,0.84,0)` for exits. `EASE_IO = bezier(0.65,0,0.35,1)` for camera moves and morphs.
- `backOut` is a small overshoot for cards, chips and buttons landing.
- Headline word:
  - the slot opens over 0.32 s (EASE_IO, starting 0.1 s before the anchor)
  - the glyphs blur in over 0.40 s (blur 12→0 px, rise 26 px, scale 1.08→1), starting 0.06 s after the anchor
  - exit is blur 16 + scale 1.05 + fade over 0.26 s
- Entrances (phone, sheet, cards) take 0.45–0.7 s. Card fly-ins take 0.5 s with backOut and start from off-frame.
- Scene transition (`scene()`, automatic): the incoming scene goes scale 0.9→1 with blur 14→0 over 0.34 s. The outgoing scene goes scale →1.22 with blur →18 and a fade over its last 0.3 s, overlapping by 0.1 s (`OVER`). The outgoing scene is gone at its end + 0.1 s.
- Camera (`cam(S, {push, roll, steps})`): a slow push of +2–5% across the scene, a roll drift of ±0.3–0.8° (sin at 0.9 rad/s), and a **step zoom of +3% over 0.35 s** on each beat word (at most 2–3 per scene).
- Pans across an image (`camKeys`): 0.4–0.5 s per move to scale 1.2–1.4 on the detail being talked about.
- Motion blur (`mblur(el, start, dur, ease, dist)`): frame-to-frame travel × 0.09 px, capped at 14, then the filter is cleared.
- Scene cuts fall `lead` = 0.18 s before the scene's first VO word.
- The end card is complete about 0.5 s after "klik…" and holds for **3.5 s** after the last word, with a slow 1→1.02 push and a twinkling sparkle.

## Pace benchmark
The reference changes something every ~0.5–1.5 s over 33 s. For Malay VO of 40–50 s:
- make a visible change (word, card, camera move, highlight, morph) every **~1–1.5 s**
- keep scenes at 4.5–7 s
- never hold a static frame for more than ~1.5 s, except the final end-card hold

## Audio
- **VO:** ElevenLabs `eleven_multilingual_v2`, language `ms`.
  - Coach Am settings: stability 0.5, similarity 0.8, style 0, speaker boost on, **speed 1.10** (1.0 drags; the earlier approved work used 1.13).
  - Gaps: lead-in 0.30 s, 0.26 s within a scene, 0.45 s at scene changes.
  - Clarity chain as in `build_vo.py`. Master at −16 LUFS / −1.5 dBTP.
- **Music:** original synthesis, D major I–V–vi–IV, ≈120–128 BPM with the first cut on a beat. The intro has no drums; drums drop for one bar at the CTA, and the bed resolves under the end card. Level about −30 LUFS (≈12 dB under VO) plus a further −6 dB duck under speech (60 ms attack / 350 ms release).
- **SFX:** a whoosh on every cut (automatic) plus cue SFX (gains ~0.12–0.24, taps ~0.55).
- **Final mix:** −14 LUFS integrated, −1.5 dBTP.
- **Delivery:** H.264 High yuv420p, BT.709 tv-range with VUI tags, CRF 16, AAC-LC 256 k 48 kHz, faststart.
