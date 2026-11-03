# Glow Keyword Style: HyperFrames pipeline

`template/` is a tested build. Its worked example is the first 14.5 s of the client's Jago Prompt remake (hook + concept intro) plus the 3 s CTA end card: 17.5 s in total. It was snapshot-compared against the approved Remotion final, frame for frame, with the palette switched to the old green (`PALETTE=green`) for the A/B: PSNR 25–34 dB, audio lag 0 ms. Edit the config and the `example()` / `camera()` / `cues()` blocks; don't rewrite the library.

## Project layout

```
work/<project>/
  timing.json            T (word anchors), CUT (shot cuts), L (layout windows, cta), SRC_END, TOTAL, CUTOUTS
  scripts/               build.py prep_footage.py grade.py make_audio.py refine_times.py transcribe_words.py qc_sheet.py finish.sh
  assets/fonts/          Sacramento-400, archivo-latin-wdth-normal (100–900, stretch 62–125 %), inter-latin-wght-normal
  work/                  words.json anchors.json audio/{voice,music,sfx}.wav cutout segments + mattes
  hf/                    hyperframes.json, index.html (written by build.py), assets/{graded.mp4, lastframe.jpg, cutout_*.webm, mix.wav, fonts/}
```

## Commands (in order)

```bash
cp -R .claude/skills/glow-keyword-style/template work/<project> && cd work/<project>
export SRC_MOV="$PWD/../../input/<footage>.mov"
/usr/bin/python3 scripts/transcribe_words.py <audio.wav> work/words.json "key terms"   # text + rough word times
/usr/bin/python3 scripts/prep_footage.py graded          # grade -> hf/assets/graded.mp4 + lastframe.jpg + fonts
/usr/bin/python3 scripts/make_audio.py                   # voice/music/sfx -> hf/assets/mix.wav
/usr/bin/python3 scripts/refine_times.py                 # work/anchors.json -> timing.json T (envelope onsets)
/usr/bin/python3 scripts/prep_footage.py cutout          # only if timing.json has CUTOUTS
/usr/bin/python3 scripts/make_audio.py                   # again, after the timing changed
/usr/bin/python3 scripts/build.py                        # -> hf/index.html
(cd hf && npx --yes hyperframes@0.8.213 lint && npx --yes hyperframes@0.8.213 check)
(cd hf && npx --yes hyperframes@0.8.213 snapshot --at 0.6,2.3,4.25,… --no-end [--against ref.mp4])
QUALITY=draft scripts/finish.sh                          # preview MP4 in hf/renders/
scripts/finish.sh                                        # delivery (SDR=1 when a source is HDR)
```

## Layer order (root `index.html`, 1080×1920, bottom to top)

1. `#backdrop` > `#grid`: near-black `#040504`, a faint brand radial at the top and a 60 px grid at 3.5 % white drifting 12 px/s. Its opacity is 0 except while `room_fade()` runs, so the hook frame shrinks on pure black.
2. The footage stack: `#shake` (seeded frame shake) > `#fx` (transition blur and the end-card dim, `filter: blur() brightness()`, set to `none` between bumps) > `#rgbw` (`filter:url(#rgbv)` only during RGB bumps; the GSAP `attr` tweens drive the `feOffset` dx on `#rgbR`/`#rgbB`) > `#frame` (the camera: `scale`, `x`, `y`, `rotation` around the centre, `overflow:hidden`, drop shadow) > `#zoom` (punch-ins, origin `540px 690px`) > `#push` (+3.5 % per shot).
   - Inside: the cut-out videos `.cutv` **under** `#room`, then `#room` = `lastframe.jpg` (the end-card freeze) under `<video id="aroll">` (`data-duration = SRC_END`).
3. Text and graphics, in source order. Each text node has an anchor parent with the static CSS `translate()/rotate()`; GSAP animates only the child.
4. Flashes `.flash` (screen blend).
5. `<audio id="mix">`: the only sound. The video is muted.

## `build.py` library (identity: keep as is)

| Call | What it does |
|---|---|
| `italic(text, a, b, x, y, size=50, rot=0, align, weight=600, ital=True)` | Inter italic keyword: blur 9→0, y 16→0, scale .92→1 over 0.22 s EO; exit 0.16 s EI with a −10 px lift and blur 8 |
| `heavy(text, a, b, x, y, size=130, rot, align, maxW=960, split=1, stretch=True)` | Archivo Black + RGB copies: offset 29→3 px, scale 1.25→1, blur 7→0 over 0.26 s, scaleX 1.9→1 over 0.18 s; exit 0.14 s (scale 1.15, offset +18) |
| `bluebox(text, a, b, x, y, size=78, rot, align)` | Box clip-wipe 0.16 s; text x −24→0 and scale 1.12→1 at +0.06 s; exit scale .9 + blur 6 |
| `script(text, a, b, x, y, size=110, rot=-6, dur=.55)` | Sacramento write-on (clip-path), 0.35 s frame-stepped flicker (seeded noise), neon glow, stroke = size/70 |
| `phrase([(word, t), …], b, x, y, size=54, weight=600)` | Word-by-word build: y 14→0, scale .85→1, blur 8→0 over 0.2 s |
| `pop_in(sel, a, dur=.3, frm=.55)` | Overshoot pop (BK) with a separate ease-out blur |
| `cta_keyword(lead, key, a, y)` | Locked CTA keyword (skew −9°, neon fill, stroke, 3-step extrusion) with a finite sine pulse |
| `track(sel, prop, init, [(t, v, d, ease), …])` | Port of Remotion's `track()`. Durations are clipped to the next key and to `TOTAL` |
| `bump_blur(a, b, amp)` / `bump_rgb(a, b, amp)` | Triangle bumps on the footage blur / RGB split (linear up to the midpoint and back) |
| `shake(a, dur, ax, ay, sx, sy)` | The original seeded shake, set per frame on `#shake` |
| `flash(t, amp, color, up=.05, down=.2)` | Screen-blended flash |
| `room_fade(a, b)` | Explainer layout: fades the room out and the grid backdrop in, then back |
| `shot_push(cuts)` | The constant +3.5 % push per shot |

The eases are the original beziers through GSAP CustomEase: `EO` (.16,1,.3,1), `EI` (.7,0,.84,1), `EIO` (.65,0,.35,1), `BK` (.34,1.56,.64,1) and `SN` (.05,.9,.1,1).

Fit: each text node has `data-fit=<max px>`. `fitAll()` shrinks the font-size so the line fits, and runs again on `document.fonts.ready`; the timeline itself is built synchronously.

## Example numbers (Jago Prompt; choreography, not identity)

- **Hook frame:** scale 1 → .9 (AI) → .8 (real) → .6 (saya) → .55 (tapi) → .5 (asyik), each a 0.22–0.3 s BK. Then y +290…+330, tilt ±1°, and back to 1 on `hookEnd` (0.23 s EI), with blur 11 and the white flash .85 on the cut.
- **Cards:** three 260×330 polaroids at x 220/540/860 and y 285. They shuffle on "muka" (0.38 s EIO with an arc), flip at +0.44 s (+0.06 s stagger), get "?" marks that wobble 12 ± 8°, jitter on "lari", and leave upward 260 px.
- **Intro:** keywords at chest height (y 1050–1290), side words at y 880 (x 70 / 1000). Punch-ins: PROMPT 1.1, CHARACTER 1.2, KEKAL 1.1, WAJIB 1.2.
- **CTA:** scrim, "Belajar dengan" at y 470, heavy lines at 600 / 745 / 890, a 720 px underline at 975, "KOMEN 'client'" at 1135, the comment box at 1265 (it types the word, then send).
- **Explainer (cut-out):** frame scale .62 with x −235 / y +435 (bottom-left) plus `room_fade()`; graphics card at y 196–960. This was tested with a 1.8 s cut-out.

## Audio numbers (`make_audio.py`)

- Voice:
  - The per-shot voiced median is measured automatically; on the Jago clips it gave −13.5 / −16.6 dB, the same as the hand-measured original.
  - Gain is 75 % of the way to −16 dB, with a 30 ms gain crossfade at cuts. Then the chain, loudnorm −16, and the measured latency shift (25 ms).
  - The room tone fades over 0.12 s at `SRC_END`.
- Music: `BPM`, `PROG`, `T0` (the downbeat on the first hard cut) and `SECTIONS` (pad / drums / bass / pluck / hats levels and the pad cutoff per section) are the per-video knobs. The CTA hit is at `L.cta`.
- Mix:
  - Music is ×0.2, ducked −9 dB under speech (it measured −16.6 dB vs the voice). SFX are ×0.3, ducked −3 dB. The CTA hold is ×2.25 from `cta + 0.1`.
  - Then a two-pass linear loudnorm to −14 LUFS / TP −1.5 and `alimiter 0.84`.
- SFX: `cues(P, typing)` places `whoosh / pop / click / impact / riser / glitch / neon / ding / key` at `T[...]` anchors.

## Verification checklist

- `lint` and `check`: 0 errors.
  - Expected warnings: `composition_file_too_large` (one generated file), `line_unread` on fast hook words and on the typed comment-box letters.
  - Expected info: container overflow of ~2 px on scaled boxes.
- `snapshot --at` every beat. When rebuilding an edit, add `--against <final.mp4>` and look at the `pair-*.jpg` files.
- Render the draft, then run ffprobe (h264, yuv420p, bt709, 1080×1920, 30 fps), `ebur128` (≈ −14 LUFS, peak ≤ −1.5), an audio-envelope cross-correlation against the voice (lag 0 ms), 0.5 s contact sheets (`qc_sheet.py`), and a Whisper re-transcript of the mix.
- Say plainly that the audio was measured, not listened to.
