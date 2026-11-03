# Storyteller Edu Style: pipeline and numbers

These numbers come from the approved "Kepada Educators" build (`template/scripts/`). Times are on the trimmed timeline: render time minus the 0.267 s trim.

## Project layout

```
<project>/
  PLAN.md                     beat table (approved before any render)
  scripts/  times.py audio.py build.py build9.py prep16.sh prep9.sh pdf_tilt.py finish.sh finish9.sh
  work/     voice.wav times.json song48.wav mix_raw.wav sfx_cues.txt snapshots
  hf/       index.html + assets/ (aroll.mp4 person.webm bg/ clips/ thumb/ tilt/ slide_*.jpg logo.png lastframe.jpg grain.png mix.wav)
  hf9/      the same assets plus aroll9.mp4 person9.webm tilt9/ lastframe9.jpg (copy hf/assets with rsync, then add)
```

## Timeline (16:9, 48.1 s composition, 47.83 s after trim)

| t (s) | Beat | Visual | SFX |
|---|---|---|---|
| 0.27 | Hook title | "PARA PENDIDIK" blurs in at the top; the badge fades in | click |
| ilmu / slide | Hook words | Icon + word pop in to the left and right of the head (ILMU white, SLIDE yellow) | pop, pop |
| 3.86 | Card 01 | "01 BAYANGKAN / SATU SLIDE" | whoosh-impact |
| macam | Panel | The presenter slides left; 3 real slides drop into a stack | paper, pop, paper |
| transform | Slide → video | The front slide flies to the video card and becomes the real clip; the "Sebelum" thumbnail appears | riser → thud |
| motion…animation | Checklist | 4 ticks (yellow dot + check); pushes between 3 slide clips | ting ×3 rising, clicks, pop |
| 12.5–14.85 | Triptych | All 3 clips side by side, labelled, held about 2.3 s | sparkle |
| 14.85 | Point | Medium push; "PELAJAR FAHAM / KONTEKS" on the open side | click, ting |
| sebab | Card 02 | "AI = PISAU" | whoosh-impact |
| pisau…okey | Metaphor | Light stage, knife line-art drawn on; "BETUL CARA GUNA ✓" marker; a "HASIL" box sliced | shing, ting, swoosh (slice) |
| salah…control | Cut-out | Cave → bedroom (pile of chores in boxes) → studio; "SALAH CARA ✕", "CIKGU & LECTURER" | thud, blip, clicks, keyboard, thuds |
| control | Tilt A | Prompt Vault screens 05 → 06 → 07, full-screen 3D tilt | riser, click, pop, click |
| 31.2 | Tree | Presenter left; "BUAT VIDEO" tree, ✕ on SKILL EDITING, glow on KNOWLEDGE WORKFLOW | pop, click, blip, ting |
| sebab2 | Tilt B | Dashboard screen, long drift | shutter |
| 36.78 | Card 03 | "03 PANDUAN / EDIT VIDEO GUNA CODE", word by word on the voice | whoosh-impact, sparkle |
| 38.2 | Proof | Module grid zooms out from R01; rings on R01/R17 | tick-roll |
| expert | Results | Grid blurs; 2 student-result recordings rise | riser, sparkle |
| claude / chat | Pills | "Claude" and "ChatGPT" glass pills either side | pop, pop |
| 45.40 | End card | Last frame blurred 24 px; logo pops in; title blurs in; no button | ting, sparkle |

## Motion helpers (all in `build.py`)

- `blurIn(el, at, d=.45, y)`: opacity 0 → 1, blur 18 → 0, scale 1.06 → 1, `power2.out`.
- `blurOut(el, at, d=.35)`: blur to 14, `power2.in`.
- `popIn`: scale .6 → 1, `back.out(1.6)`, .38 s.
- Video pushes: `xPercent` ±100, `power3.inOut`, .4 s.
- Tilt: `tilt(el, at, d, ry0, ry1, rx0, rx1, y0, y1)` with `transformPerspective` 1700. Planes are 2420×1546 at left −250, top −233 (16:9). In 9:16 the planes are 2312×2050 at top 30, gliding x (−100 → −200).

## 16:9 layout numbers

- `FACE` origin is `1010px 420px`.
- The video card `CARD` is left 620, top 208, 1180×664. The "Sebelum" thumbnail is 300×169 and overhangs the card's bottom-left corner.
- The tree panel is 880×780 at left 950, top 150.
- The pile boxes are 560×100 at x 1380, stacked every 110 px.
- The grid is 5×4, 360×203 thumbnails at a 376 px step, with the last row centred. It starts at scale 2.4 with origin `180px 101px`.
- The badge is at left 36, bottom 30, z 50.

## 9:16 layout numbers (1080×1920)

- The strip `.strip` is 1848×1920.
  - From the RAW take: `AX −402`, `FACE_A 942px 924px`, `PX −384`, `FACE_P 924px 924px`, `DOWN 450`.
  - From the library-bg take: face y 782, `DOWN 600`.
- The top mask is `linear-gradient(180deg, transparent 0, #000 var(--fe))`, and `--fe` is 300 px while the presenter is down.
- The badge is top-centre, top 96, in a full-width flex wrapper, so its animation can use y without breaking the centring.
- Text tops follow the face:
  - Hook / Salah / Cikgu: about 330–360.
  - Konteks: the presenter moves x +260 and the caption goes left at top 770, 76 px.
  - Pills: top 400.
- Chapter-card words are stacked one per line: 220 px, and 190 px for the four-word card.
- Slide → video:
  - The video card is left 40, top 300, 1000×563.
  - The checklist sits below it, at left 250, top 980.
  - The triptych is stacked: three 840×473 cards at tops 250, 763 and 1276, with tags at the bottom-left.
- Knife: the SVG is at top 470, the label at 960 and the box at 1180.
- The pile boxes are 420×90 on the right (x 830), between y 1022 and 1430, while the presenter steps x −300.
- The grid is 3×6, 330×186 thumbnails at a 348/204 step, with the last two centred. The results are two 480 px wide cards side by side.
- Camera:
  - Hook push 1.0 → 1.035.
  - Konteks 1.08.
  - End push 1.075.
  - Every move uses `cam()` (sine.inOut, about 0.6 s).

## Audio

- `times.py`: each Whisper start is refined to the onset after the local envelope minimum (±0.12 s window). The result is clamped to −0.10…+0.15 s from Whisper, because soft s-/f- onsets read late.
- `audio.py`:
  - Each cue is `(time, family, args, gain dB, align start|end|impact)`.
  - Each family has a `TARGET` RMS in dB below the voice RMS: whoosh-impact −9, thud −10, swoosh −11, pop −12, riser −13, shutter −13, click −14, paper −14, shing −14, blip −14, ting −15, tick-roll −15, keyboard −16, sparkle −17.
  - Cue i uses the seed `7000 + i·97`. Never use the same family more than twice in a row.
  - Swoosh / whoosh-impact appear only on chapter cards (plus one slice).
- Song gain = voice LUFS − 20 − song LUFS. It has a 0.3 s ramp in, is lifted ×2.2 from the end card, and fades out at the end.
- Final: `volume` to −14 LUFS, then `alimiter limit .89`. Measured −14.3 LUFS, TP about −1.6.

## Verification checklist

- `npx hyperframes check`: 0 errors. Contrast warnings on white text over a wall are expected; check those by eye.
- Snapshot every beat (`--at` list, `--no-end`) and look at the contact sheets. Zoom in on tilt planes to confirm they are sharp.
- After render:
  - ffprobe: h264 yuv420p bt709 at the right size.
  - `ebur128`: about −14.9 LUFS on the delivered file.
  - Whisper on the first 3 s: the opening line is clean.
  - A frame strip of 6–8 frames.
- Say plainly that the audio was measured, not listened to.

## Companion: 4:3 "resize" comparison (optional, only if asked)

The user later made a 4:3 (1440×1080) piece from the two finals: the landscape at max size → a prompt bar typing "Tolong resize video ni jadi size 9:16" → the bar turns into a progress bar → the landscape shrinks and tilts while the 9:16 (506×900) overlaps its edge, over an original dark light-ribbon background. Recreate it from the description if asked; don't add it by default.
