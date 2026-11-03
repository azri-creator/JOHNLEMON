# PiP Explainer Style: HyperFrames pipeline and numbers

Reference build: "Bisnes Baru Nak AI" (client, 94.4 s, 9:16). The Remotion original was ported 1:1 to HyperFrames; the
template rebuilds the approved cut frame for frame (same EDL, same anchors, same audio master: 0 ms lag,
correlation 0.9998 against the approved final).

## 1. Project layout (copy `template/` to `work/<project>/`)
```
<project>/
  scripts/        python pipeline + the composition generator (edit these)
  analysis/       foot16k.wav, words.json (transcribe.py)
  data/edl.json   EDL + word timeline (edl.py). The shipped one is the Bisnes Baru example.
  hf/             HyperFrames project: index.html (written by build.py), hyperframes.json, assets/{video,img,audio,fonts}
  renders/        finish.sh output
  qc/             contact sheets, compare sheets
```
Never hand-edit `hf/index.html`: it is regenerated. Edit the python files and rebuild.

| File | Per video? | What it holds |
|---|---|---|
| `edl.py` | rarely | segments (whole clip by default; the user delivers footage already cut), 2 s end-card tail |
| `transcribe.py` | no | faster-whisper large-v3, `language="ms"`, `ASR_PROMPT` = key terms |
| `timing.py` | **yes** | word anchors in SOURCE seconds, `LAYOUT`, `PANEL_CUTS`, `PUNCH`, `SHAKES`, `FLASHES`, `END_CARD` |
| `captions.py` | **yes** | `FIX` spellings, `JOIN`, `KEY` regex, `UNCLEAR`; the 1–3-word chunker |
| `scenes.py` | **yes** | the PiP panels, the FULL slams, the end-card text |
| `kit.py` | no (locked) | palette, type, geometry, `fit()`, icons, HTML pieces, CSS, GSAP helpers |
| `build.py` | no (engine) | assembles index.html: backdrop, panels, presenter morph, slams, captions, end card, flashes |
| `prep_footage.py` | B-roll list | main.mp4 (tone curve, HDR→SDR if needed, BT.709, `-g 10`), B-roll, logos |
| `make_audio.py` | music sections + SFX cues | voice chain, synth bed, synth SFX, ducked mix, −14 LUFS master |
| `sfx_dsp.py` | no | DSP + SFX building blocks |
| `finish.sh` | no | delivery render `--sdr`, mux the exact audio master |
| `qc_sheet.py`, `compare_sheet.py` | no | contact sheet; side-by-side against a reference video |

## 2. Layer order (root `index.html`, 1080×1920, one paused timeline `window.__timelines['main']`)
1. `#bg` navy + `#dots` (34 px cyan dot grid, drifts −6 px/s) + `#glow` (sine drift) + vignette.
2. `#panels`: one `.panel` per PiP scene (`<id>` push-in/out camera, `<id>_d` drift layer inside).
3. `#presenter` (the ONE video):
   `#pbump` (PiP→PiP nudge, origin card bottom) > `#pclip` (clip-path frame) >
   `#pwall` (wall gradient) + `#pmove` (layout transform, origin 0 0) > `#ppush` (stint push, origin face) >
   `#ppunch` (punch-ins, origin face) > `#pshake` (seeded jitter) > `#pmask` (`--fe` edge feather) > `<video id="pres">`;
   `#fullvig` (FULL vignette) inside the clip; `#pring` (card hairline + glow) outside the clip.
4. `#slams` (FULL kinetic words).
5. `#caps` (caption chunks; the layer glides +86 px in PiP).
6. `#endc` end card.
7. `#flash` (screen-blend flash).
8. `<audio id="mix" src="assets/audio/mix_master.wav">` (the main video is `muted`).

## 3. The FULL ↔ PiP morph (numbers)
| | FULL | PiP (k = 0.6 → 0.618 over 5 s) |
|---|---|---|
| `#pclip` clipPath | `inset(0 0 0 0 round 0)` | `inset(1372px 30px 40px 30px round 40px)` |
| `#pmove` x / y / scale | −108 / −300 / 1.2 | 540(1−k) / 1372 − 430k / k |
| `#pmask --fe` | 0 % | 11 % |
| `#fullvig`, `#pring` | 1, 0 | 0, 1 (ring fades in over the last 65 % of the morph) |
| `#caps` y | 0 (caption at 1210) | +86 (caption at 1296) |
| duration / ease | 0.24 s expo.out | 0.34 s expo.out |

`#ppunch` and `#ppush` return to 1 during the FULL→PiP morph; `#ppush` then runs 1 → 1.035 over 4 s in each FULL
stint. Punch keys are evaluated with the original `track()` semantics in Python and written as `fromTo` tweens
truncated at the next key / layout switch, so no two tweens on `#ppunch` overlap.

## 4. Remotion → GSAP mapping (used by kit.py)
| Remotion original | HyperFrames |
|---|---|
| `EASE_OUT` bezier(0.16,1,0.3,1) / `SNAP` | `expo.out` |
| `BACK` bezier(0.34,1.56,0.64,1) | `back.out(1.8)` |
| `EASE_IN` / `EASE_IO` | `expo.in` / `power3.inOut` |
| `<Panel a b from drift>` | `panel(id, a, b, from, drift)` |
| `<Title>`, `<Chip>`, `<Slam>`, `<Tick>`, `pop()` | `title()`, `pop()`, `slam()`, `tick()`, `popBlur()` (+ `kit.title/chip/slam/tick_svg` for the HTML) |
| `shake(t, a, dur, amp, seed)` | `shake_js(sel, a, dur, amp, seed)`: per-frame `tl.set` with the same seeded noise |
| `Math.sin(t*k)` wobble | `yoyo(sel, a, b, prop, v0, v1, half)` (finite repeat) |
| `<OffthreadVideo>` in a `<Loop>` | `vid()`: `<video data-start data-duration muted>`; time the video, never its wrapper |
| `translate(-50%,-50%)` centring | `anchor(x, y, inner)`: a zero-size flex box, so GSAP can scale the child |
| counter text | `counter(id, a, d, to, suffix)`: proxy tween with `onUpdate` (seek-safe) |

## 5. Commands
```
export SRC_MOV="<footage.mov>" SRC_DUR=<seconds> BROLL_DIR="<folder>" LOGO_ICON=<png> LOGO_TEXT=<png>
ffmpeg -i "$SRC_MOV" -vn -ac 1 -ar 16000 analysis/foot16k.wav
ASR_PROMPT="<key terms>" /usr/bin/python3 scripts/transcribe.py analysis/foot16k.wav analysis/words.json
/usr/bin/python3 scripts/edl.py
/usr/bin/python3 scripts/prep_footage.py          # ~35 s for 92 s of 1080x1920
/usr/bin/python3 scripts/make_audio.py            # ~10 s
DUR=15 /usr/bin/python3 scripts/build.py          # quick cut for review; omit DUR for the full video
npx hyperframes lint hf && npx hyperframes check hf
npx hyperframes snapshot hf --at 0.3,3.2,... --no-end -o qc/snap [--against <reference.mp4>]
npx hyperframes render hf --quality draft --sdr -o renders/draft.mp4
NAME=<Name> zsh scripts/finish.sh                 # delivery render + exact audio master
```
Render speed on an M-series Mac: 15 s draft in ~14 s.

## 6. Verification checklist
1. `lint` and `check`: 0 errors. Expected warnings: `composition_file_too_large` (one generated file by design),
   `line_unread` on captions (1–3-word kinetic captions are the style), `text_below_floor` on the small "AI" tags,
   `duplicate_media_discovery_risk` (the same still in two scenes).
2. Snapshot every beat; read the sheets. Look for empty panels, overflow past 960 px, captions over the card, a
   title clipped by the push-in.
3. Audio: cross-correlate the render's audio with the source voice (lag 0 ms), `ebur128` ≈ −14 LUFS, TP ≤ −1.5.
4. A Whisper re-transcript of the ending: nothing masks the last word; the end card starts after it and holds ≥ 2 s.
5. The spelling of every on-screen word.
