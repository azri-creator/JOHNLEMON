# Native Viral Styles — pipeline and numbers

Reference build: Coach Am's original Control Zoom project (not shipped).
Everything below is what that build used and what the user approved after two rounds of feedback.

## 1. Canvas and layer order (root `index.html`, 1080×1920)

From bottom to top:

1. `#shake > #cam` — camera wrappers (transform-origin 0 0). Inside: the base `<video id="base">` (muted) and the
   **in-camera scene hosts** (effects that must move with the footage: power aura, 3D orbit, super-power bolts,
   vignette push).
2. `#scrim` — top gradient for caption legibility (0 → 560 px, rgba(6,9,13,.5→0)). It must sit **below** the headlines.
3. `#headsB` — big headlines that go **behind the presenter** (cutout).
4. `#pmatw > #shake2 > #camP > #pmat` — person matte video, mirroring every camera/shake tween (`"#cam, #camP"`,
   `"#shake, #shake2"`). It covers `headsB`. Hide it (`opacity 0`) while the 3D orbit runs, so front cards are not covered.
5. **Screen-space scene hosts** (UI that should not zoom: HUD, keyframe panel, clock, icon cards, slot, motion takeover, CTA).
6. `#headsF` — big headlines in front.
7. `#chip` — the Claude Code prompt chip (bottom, top 1400 px).
8. `#kicks` — kickers and small captions (z 40).
9. `<audio>` tracks: voice (from the footage file), `music.wav`, `sfx.wav`.

## 2. Captions

- `PAIRS = (t_kicker, t_headline, t_end, "KICKER WITH *ONE* KEY", "HEADLINE")`. Every spoken word appears in order in
  one of the two strings. Keep the user's wording verbatim (only uppercase it).
- `KEY = {index: "B" | "F"}` — about 8–10 pairs get the big Anton headline. The rest render as a small two-line
  caption (`.cap2`: line 1 = kicker 40 px, line 2 = headline words 52 px, Inter 900 uppercase).
- Headline font size: `min(170 front | 158 behind, 980 / (0.47 × chars))`. Front top 172 px; behind top 58 px.
- Animation: kicker fade-up 0.12 s; headline rise 46 px → 0 in 0.22 s (`power3.out`). No blur, no scale pop, no
  heavy glow (the user found it dizzying). Optional RGB-split glitch for one "power" word only.
- Behind-head headlines hide the kicker at headline time, so the top never shows three lines at once.
- Text shadow: kicker `0 2px 6px rgba(0,0,0,.55)`; headline `0 6px 22px rgba(0,0,0,.35), 0 0 24px rgba(200,220,255,.3)`.

## 3. Claude Code chip

Glass bar 940×150 at (70, 1400). Coral 8-ray spark (`#D97757`), label "CLAUDE CODE" (22 px, tracking .14em, muted),
prompt in JetBrains Mono 32 px (19.2 px per character), revealed with `clipPath inset(0 X% 0 0)` using
`ease: steps(n)`; the coral cursor moves `n × 19.2` px with the same steps and blinks with a finite yoyo. A white
status pill (`✓ 1.6×`, `✓ 6 video`, `✓ selesai`) pops when the effect lands. Keep commands ≤ 40 characters and in BM,
paraphrasing what the presenter asks for. Show the chip only around the command beats.

## 4. Camera recipe (CAM list: time, scale, pivotX, pivotY, duration, ease)

- Translate = pivot × (1 − scale) with transform-origin 0 0. Pivot on the face (≈440, 520–560 for a centred presenter),
  or toward the hand for hand beats.
- Build-up lines: `sine.inOut` pushes of 1.5–3.3 s to 1.06–1.15.
- Keywords: snap `power2/power3.out` in 0.08–0.12 s, +0.08–0.2, then `expo.out` back in 0.3–0.5 s.
- The demo zoom ("zoom video macam ni"): 1.0 → 1.6 in 0.46 s, drift to 1.66, then zoom-out 0.5 s `expo.inOut`.
- The punchline ("Tak ada."): hard set to 1.0 and snap to 1.22 in 0.08 s.
- Tweens must not overlap in time (lint warns). Shakes: 0.03 s steps with decaying random offsets (seeded),
  amplitude 10–18 px, 0.25–0.36 s.
- Start at exactly 1.0 with no wake zoom (the user rejected an opening scale/flash).

## 5. Matte and tracking

- `npx hyperframes remove-background` (u2net_human_seg, CoreML) takes ~170 s for 45 s of 1080×1920. If it says the
  weights aren't cached, copy `~/.u2net/u2net_human_seg.onnx` into
  `~/.cache/hyperframes/background-removal/models/`. Re-encode:
  `ffmpeg -c:v libvpx-vp9 -i matte.webm -c:v libvpx-vp9 -pix_fmt yuva420p -crf 26 -b:v 0 -deadline realtime -cpu-used 6 -row-mt 1 -an person.webm`.
- No hand-landmark model is installed. Read hand/face positions by eye from `scripts/grid_sheet.sh` (a 10×10 grid;
  each cell is 108×192 px of the frame) at 4 fps and key them in the scene (`HK=[[t,x,y],…]`, interpolated).

## 6. Audio (`scripts/audio.py`)

- Voice from the footage (check L/R correlation ≈ 1; fold to mono). Measure the speech RMS.
- Music: pick the most stable 1 s-RMS window ≥ 60 s into the track, `atempo=0.75,lowpass=3800,highpass=40`, gain to
  ~20 dB under the voice RMS, sidechain duck (±2 dB, attack 30 ms, release 280 ms), fade 0.8 s in and 1.8 s out, and a
  hard drop on the punchline that comes back for the CTA. Verify 0.5 s windows: music never within 12 dB of the voice.
- SFX: `S(kind, rng)` synthesizes each event from scratch with its own seed (`1000 + idx*7919`) and randomized
  pitch/filter, so no two events are identical. Families used: boot, tink, swish up/down, keyboard ticks (one per typed
  character group), servo zoom in/out, pings, slide, pops, slam, tape rewind, bell, checks, long riser, boom, portal
  whooshes (panned L/R), whoomp, suction, hum, wub, throw, implode, zap, thunder, knock, blip, data chirp, chord,
  ratchet ticks, clunk, synth stab, error buzz, doppler whoosh, shimmer, reverse whoosh, drone, low boom, shing, stamp,
  pad, confetti. Levels: −8 to −15 dB for impacts, −20 to −28 dB for UI, −31 dB for typing.
- The render lowers ~1.5 dB to keep TP ≤ −1 dBTP. Result: −18.3 LUFS, TP −1.5.

## 7. Verification checklist

1. `npx hyperframes check` with 0 errors (warnings about nested media start or tween tails are fine; fix ✗ overlaps by
   marking intentional ones with `data-layout-allow-overlap` / `data-layout-allow-occlusion` on the text nodes).
2. Snapshot every beat (`npx hyperframes snapshot --at … --no-end -o build/sN`) and read the contact sheets. Look for
   captions over faces, clipped UI at the edges after zoom, unreadable cutouts, and colliding layers.
3. Draft render (~90 s), then voice lag via cross-correlation (must be 0 ms) and `ebur128`.
4. Delivery render (~2–2.5 min), then spot-check 6–9 frames, then send the MP4.
5. Tell the user what you could not verify (you cannot hear the mix; music licence; doubtful words).
