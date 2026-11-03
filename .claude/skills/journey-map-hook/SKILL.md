---
name: journey-map-hook
description: >-
  "Journey Map Hook": a locked editing style for travel / destination ads with a talking-head presenter on a cut-out
  (first built for a travel client's Switzerland ad, Oct 2026). A short cinematic 3D terrain-map hook (satellite relief,
  country filled in the brand colour with a neon border, labelled cities, fly-in to the featured landmark), then real
  footage and stills behind the presenter, cinematic gradient + script place titles (never boxes), clean slide-left
  transitions, live zoom/dolly on the presenter driven by voice energy, cleaned voice and low ducked music. 16:9 first,
  then a purpose-built 9:16. Use whenever the user says "Journey Map Hook", "map hook", "style peta", "intro peta 3D", or asks for a destination/travel ad that opens on a 3D map, even without naming it. Built
  with HyperFrames (HTML + GSAP + Three.js); renders the real MP4.
---

# Journey Map Hook

First built for "Ramai Ingat Amek Gambar Je" (Switzerland, Oct 2026). Locked identity below; destination, copy and shot
choices change per video. Pipeline details and numbers: `references/pipeline.md`. Read it before building.

## Locked identity

| Layer | Rule |
|---|---|
| Structure | 0–1.5 s presenter full-frame → **map hook only ~5–10 s** (national overview → fly-in to the landmark) → everything after is **real footage/stills** behind the presenter → CTA over real footage with logo + the brand's website |
| Map | Real data only: AWS Terrarium DEM + NASA Blue Marble + Natural Earth lakes + **official national boundary** (swisstopo for Switzerland; use the country's official source elsewhere) + verified city coordinates. Country fill `#ff661f`, neon border per neighbour (FR cyan, DE yellow, IT green, AT pink), dark terrain, white city dots, orange landmark pin. Labels typed by us, never AI text |
| Titles | Gradient (orange→white) Montserrat 900 caps + handwritten script (Mrs Saint Delafield) underneath, over a dark scrim. **No purple boxes / HUD panels / pills** ("murah"). Numbers and checklists are plain typography |
| Transitions | **Slide-left only** (incoming from right, outgoing drifts left slower with blur + dim). No swipe bars, iris, wipes, flashes. Optional soft cross-fade at the very end |
| Presenter | Green-screen cutout keyed to alpha (never re-grade; user already retouched). Full ↔ PiP (bottom-left, white outline + orange glow). Camera alive: slow push, snap punch-ins on emphasis words, pull-outs on pauses, ≤ ~1.3×. Sync to voice energy, not Whisper times |
| Captions | Montserrat 900 caps, 2–3 words, white with `#14091f` stroke, keyword in `#ff661f`. Mark guessed words `?` in `captions.js`; leave unclear parts (prices) uncaptioned until the user confirms |
| Frame | **No vignette / dark edges** anywhere (map, b-roll, talk). Only very light top/bottom scrims (~25%) for text legibility |
| Brand | the brand's website: orange `#ff661f`, purple `#240064/#352540/#23172f`, lilac `#bba9ce`, mist `#e8e3ed`; logo `assets/img/brand-logo.svg` (a placeholder: swap in the student's own logo); tagline "Beyond Tourism" |
| Audio | Voice cleaned (see pipeline), −16 LUFS. Music ~20 dB under voice, sidechain-ducked, lowpassed, fades to full length. SFX soft slide whooshes + pops/ticks, ~−30 LUFS. Supplied soundtracks are loud (−11 LUFS): always attenuate |
| Deliverables | 16:9 1920×1080 30 fps first, then 9:16 1080×1920 (presenter native-res at the bottom, map/footage/titles above). Render `--quality delivery` only after approval |

## Storyboard first (must)

Make storyboard frames with the `storyboard-frames` skill (`.claude/skills/storyboard-frames/`) before any MP4 render, draft or delivery:
1. Build the composition.
2. Snapshot one still per beat onto numbered sheets.
3. Let the student refine frame by frame.
4. Render only after they reply "ok storyboard".

Every render step in the workflow below comes after that approval.

## Workflow

1. Gather: presenter cutout (green screen ok), baked backdrop plate(s), b-roll stills + montage, soundtrack, VO. Probe everything.
2. Transcribe the VO (`npx hyperframes transcribe vo.wav --model small --language ms`), draft captions with `?` marks, compute the VO energy envelope.
3. Key the presenter: `chromakey` + `despill` → VP9 alpha WebM (see pipeline).
4. Bake the map for the destination with `scripts/bake-map.mjs` (edit the PATCHES / POIs / neighbours block at the top of that file for the new country). Run the inside-border check; **geography must pass before any render**.
5. Copy `template/` into a new `npx hyperframes init` project, replace destination data (`akg-config.js` cam/labels, `captions.js`, titles in `index.html`, clip timings in `anim.js`), cut montage clips with ffmpeg.
6. Audio: clean voice, duck/attenuate music, build SFX (`scripts/make-sfx.sh`), then a draft render and review contact sheets.
7. `npx hyperframes lint` → snapshots at transitions → draft render → user approval → delivery render of 16:9, then `scripts/make-9x16.py` and delivery render of 9:16.

## Known gotchas

- `hyperframes check` false-positives `text_not_painted` on gradient text; verify in the render instead.
- Name clash: `VERT` is the vertex shader in `map.js`; use `IS_VERT` for the portrait flag.
- Map labels clip into titles: place neighbour labels with fixed lon/lat (see `map.js`), not run midpoints.
- 1080p montage clips look soft when cover-cropped to 9:16 (~1.8×). Say so; ask for 4K if available.
- Never put a price on screen before the user confirms the script.
