---
name: storyteller-edu-style
description: >-
  "Storyteller Edu Style": the user's locked style for talking-head explainer/ads in a calm storyteller rhythm
  (first built for VGC "Kepada Educators", Oct 2026). Numbered chapter cards (small kicker + one huge glowing
  Archivo Black word, blur-in), keyword-only text (no subtitles), white line diagrams built per sentence on a dark
  grain stage, the presenter slides aside (16:9) or drops down (9:16) to open a panel, real slides that turn into
  real videos with a "Sebelum" thumbnail, a light-stage metaphor, cut-out bg swaps, sharp full-screen 3D tilt
  screens from PDF images, a module grid, a persistent claim badge, yellow #FFE600 as the only highlight, lime only
  on the logo, no CTA button unless asked, varied click/ting/pop SFX (swoosh only on chapter cards), song ~20 LU
  under the voice. 16:9 first, then a purpose-built 9:16. Use whenever the user says "Storyteller Edu Style",
  "Storyteller Edu", "style Kepada Educators" or "macam video Kepada Educators tu".
  Built with HyperFrames; renders the real MP4.
---

# Storyteller Edu Style

First built for VGC **"Kepada Educators"** (28 Oct 2026). It is a 47.8 s talking-head ad: 45.4 s of A-roll plus a 2.7 s end card.
- 16:9 v2 was approved.
- 9:16 v2 was built from the RAW take.

The editing behaviour comes from a storyteller-explainer reference. Only the behaviour was taken; no reference footage or branding.

What changes per video and what stays locked:
- **Per video:** the script, the beats and the assets.
- **Locked:** the identity below.

Where everything else lives:
- `references/pipeline.md`: numbers, layer order, the beat catalogue and the SFX/mix recipe. Read it before building.
- `template/scripts/`: the exact working build (`build.py` 16:9, `build9.py` 9:16, `audio.py`, `times.py`, prep and finish scripts). It is a worked example, so edit its config and beat blocks rather than writing from scratch.

## Locked identity

| Layer | Rule |
|---|---|
| Structure | Every section follows the same cycle: **chapter card → idea → proof → step**. Each section ends on a visual payoff, never on talk alone |
| Chapter card | Full dark stage `#0F1419` with grain at 7 % overlay. A kicker in **Inter 600, 30 px, letter-spacing .32 em**, with a yellow bold number ("**01** BAYANGKAN"). Below it, one or two huge **Archivo Black** uppercase words (200 px in 16:9), with the key word in yellow `#FFE600`. Glow comes from `text-shadow` only. The card blurs in (blur 18 → 0, scale 1.06 → 1, 0.35 s) and drifts to scale 1.05 over 1.5 s. Hold it about 1.3 s. It is the **only** place a swoosh/whoosh-impact SFX plays |
| Text | **Keywords only, no subtitles.** Archivo Black uppercase with a soft white glow. One yellow word per beat at most. A drop-shadow filter on the parent. Text always goes on the open side of the presenter, never over the face or the jersey print |
| Highlight | Yellow `#FFE600` is the only highlight colour. Lime appears **only on the logo**. Red `#FF5A4F` is used only for ✕ marks |
| Panels | **16:9:** the presenter slides left (x −560, 0.55 s) and the A-roll's right edge feathers through a `--fe` mask variable. A dark panel opens on the right (`rgba(15,20,25,.95)`, radius 30). **9:16:** the presenter glides **down** (y +450…600, sine) with a feathered **top** edge, and the panel sits on top |
| Line diagrams | White 5 px strokes drawn with `strokeDashoffset`, plus nodes that pop in. They are built as the sentence is spoken (tree, ✕ on the wrong branch, a yellow glow on the right one) |
| Slides → video | Real slides drop in as tilted cards. The front slide flies into a video card and becomes the **real** video. The slide then shrinks into the corner as a "**Sebelum**" thumbnail (dark backing). A checklist ticks with yellow dots, video cards push left/right, and a **triptych** (all three) is held **≥ 2.3 s** so people can scan it |
| Metaphor | **Rare.** One light-stage beat (`#E8E6E1`, charcoal line art drawn on, a yellow marker label, one clean slice) |
| Cut-out bg swaps | An exact cut-out (source pixels plus the matte alpha) over stock backgrounds. The backgrounds push horizontally; scaled ones use xPercent ±115 |
| Full-screen screens | **Sharp 3D tilt planes** from the PDFs' **embedded** images (`scripts/pdf_tilt.py`). `transformPerspective` is 1700–1800, rotY ±7–11°, rotX 3–7°, with a slow drift. Clear `filter` after the blur-in, or the plane stays soft. In 9:16, planes fill the height and glide across the content column |
| Proof | A grid of module thumbnails zooms out from module 1, with a yellow ring on the first and last. Then the grid blurs and **real student results** (cropped chat recordings, names blurred) rise on the keyword |
| Claim badge | A glass badge visible the whole video, from 0.27 s to the end card: "**100%** DIEDIT OLEH CLAUDE / Claude Opus 5.5 · High · Siap NN minit". Bottom-left in 16:9, top-centre (top 96) in 9:16. Only use the user's own claim text |
| End card | The last frame, blurred 24 px, then the real logo pops in and the title blurs in. **No CTA button** unless the user asks |
| Camera | 16:9: slow pushes (1.0 → 1.07 in the hook, 1.15 at the end). 9:16: **calm** (sine only, half the zoom range, no snaps); the presenter steps left/right on headline beats |
| Footage | The grade is never touched. Tag everything BT.709 and render `--sdr`. 9:16 from 1080p source = lanczos ×1.7778 strip (1848×1920), plus light unsharp |
| Audio | Voice untouched. The supplied song at original tempo, **voice LUFS − 20**, a 0.3 s ramp, lifted ×2.2 on the end card. Every SFX is synthesised with its own seed (no repeats): click/double-click, ting (rising pitches), pop, paper, keyboard, riser, thud, sparkle, shutter, blip, tick-roll, plus whoosh-impact on the chapter cards **only**. Mix to −14 LUFS with a limiter |

## Storyboard first (must)

Make storyboard frames with the `storyboard-frames` skill (`.claude/skills/storyboard-frames/`) before any MP4 render, draft or delivery:
1. Build the composition.
2. Snapshot one still per beat onto numbered sheets.
3. Let the student refine frame by frame.
4. Render only after they reply "ok storyboard".

Every render step in the workflow below comes after that approval.

## Workflow

1. **Plan before rendering.** Transcribe the take and refine word starts from the energy envelope (`times.py`; Whisper drifts 0.2–0.3 s). Write `PLAN.md` as a beat table (time | words | visual | SFX) and list the assets needed. Wait for approval ("jangan render apa-apa, bagi plan dulu").
2. **Clean start.** If the user names the first line, count syllable nuclei in the 100–900 Hz band at 10 ms resolution, and cut in the closure **before** the first syllable. Whisper boundaries run early (v1 kept the "-o" of the previous word). Trimming after render (`finish.sh` `TRIM=`) keeps composition times unchanged.
3. **Assets.** Run `prep16.sh` (frame-exact A-roll, `voice.wav`, exact cut-out, last frame). Make tilt planes with `pdf_tilt.py`. Stage slide videos muted, cropped and short. Crop result recordings and blur names.
4. **Build 16:9.** Edit `build.py` (`T` overrides, `CARD`, the beat blocks), then run `audio.py` (`SONG=… python3`, the cue list).
5. **Check.** Run `npx hyperframes check` (0 errors). Snapshot **every beat**. Look for: text over the face or the print, white text on cream cards (give it a dark backing), bg edges peeking in, last grid rows not centred.
6. **Render** with `finish.sh` (delivery, `--sdr`, trim). Verify with ffprobe (bt709), `ebur128` ≈ −14 LUFS, and a Whisper check of the opening words. **Wait for 16:9 approval before 9:16.**
7. **9:16.**
   1. If the user asks for the RAW / un-swapped take, check that it is frame-aligned (audio cross-correlation lag 0). Then run `prep9.sh` with `SRC9=…`; it builds new strips and a fresh matte.
   2. Run `build9.py` (face constants `AX/PX/FACE_*`, `DOWN`, text tops follow the face) and `finish9.sh`.
   3. Snapshot every beat: badge clear of tilt headlines, triptych tags at the card bottom, the pile beat stepping away from the face.

## Known gotchas

- HyperFrames: every `<video>` needs an id. Use `immediateRender:false` on fromTo tweens. Hide late elements with `gsap.set` at t = 0. Duplicate ids silently break tweens.
- Mask on the A-roll: in 9:16 the strip **is** the masked box, so the mask moves with it. Never mask a parent smaller than its video.
- `sips` rasterises PDFs soft; use the embedded image. A tilt plane that keeps a `filter` after its blur-in renders soft.
- A second root HTML with `data-composition-id` in the project makes `check` fail (duplicate audio). Move backups out.
- Presenters drift inside long takes. Re-check face x per beat before side-steps (the 9:16 pile beat needed −300).
- Claims: "Siap NN minit" and "Opus 5.5 · High" are the user's statements. Report the real build time honestly alongside.
- Write with `/usr/bin/python3` (it has cv2, numpy, scipy, pypdf). Homebrew `python3` lacks PIL/cv2.
