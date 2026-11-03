# Clean Launch Motion: HyperFrames pipeline

## Project layout
```
work/<Name>/                     copy of template/ (plan.json, vo/, scripts/), plus hf/ from `hyperframes init`
  plan.json                      name, script path, voice, scenes, line_scene, gaps, lead, end_hold, music, sfx
  vo/vo_script_locked.txt        the user's script, verbatim, one delivery line per line
  vo/takes/lines/                ElevenLabs line takes + selection.json          (tts_lines.py)
  vo/vo_words.json               word timings: the timing source for picture AND sound (rough_timing.py / build_vo.py)
  scripts/index.tpl.html         root, CSS tokens, surfaces (phone, card, chip, button, sparkle...)
  scripts/lib.js                 locked GSAP helpers (below)
  scripts/scenes/NN_<key>.html   one scene per file: <section class="scene" id="<key>"> markup + one <script>
  scripts/build.py               writes hf/index.html (never edit hf/index.html by hand)
  hf/                            HyperFrames project; hf/assets/{img,video}/ real assets, vo.wav, music.wav, sfx.wav, mix.wav
  <Name>_VO.wav                  VO master (-16 LUFS)
```
One root composition (no sub-compositions): scenes are plain `<section>` layers whose opacity/scale the timeline drives, exactly like the original single Remotion `<Ad>`. `lint` warns `composition_file_too_large`; that warning is expected for this style. The only timed clips are `<audio id="mix">` and any `<video>`.

## Timing model
- `build_vo.py` (or `rough_timing.py` before any credits) writes `vo/vo_words.json`: every word has `id` ("storyboard.#1" = lower-cased word with its punctuation, `#n` = n-th occurrence), `s`, `e`, `line`, `scene` (from `plan.line_scene`).
- Scene cuts: scene 1 starts at 0; every other scene starts `plan.lead` (0.18 s) before its first VO word. Total = last word end + `plan.end_hold` (3.5 s). `build.py` and `make_audio.py` share this formula (`common.timing`), so whooshes and the drum drop land on the cuts.
- In scene code, anchor everything to words, never hard-coded seconds: `sw("cards", 2, -0.1)` (3rd word of the scene, −0.1 s), `sw("cta", -1)` (last word), `ws("rujukan.#1")`, `we(...)` for word ends. In headline markup: `data-at="cards:2"`, `data-at="rujukan.#1"`, `data-at="cards:2@-0.04"`, or seconds `data-at="0.1"`.
- Inside each scene builder `S = {key, a, b, end, first, last, el, cam, step}`; `S.end` = `b + 0.1` (the zoom-through overlap), or the video end for the last scene.

## lib.js helpers (all add tweens to one paused `tl`)
| Helper | Device |
|---|---|
| `scene(key, S => …)` | registers a scene and its zoom-through in/out (0.9→1 + blur 14→0 over 0.34 s; out 1→1.22 + blur 18 + fade, gone at `b + 0.1`) |
| `cam(S, {push, roll, steps, origin})` | slow push, roll drift (sin 0.9 rad/s), +3 % step zooms (0.35 s) on `#key-cam` / `#key-step` |
| `headline(id, {out})` | re-centring word-by-word blur-in from `<div class="hl" data-y data-size [data-max data-gap data-lh data-out]>` + `<span data-at class="blue|royal|br">` |
| `poseTo(el, from, to, t, dur, ease, ir)` | 3D plane between poses `{x, y, rx, ry, rz, s, persp, vp}` (CSS rotateX→Y→Z order, vanishing point `vp`) |
| `mblur(el, t, dur, ease, dist)` | speed blur (travel/frame × 0.09, cap 14), then `filter: none` |
| `float(el, prop, t0, t1, amp, freq, phase)` | sine float on a dedicated wrapper |
| `curve(el, prop, t, dur, p => value, {tpl, ir})` | any seek-safe function of time (fills, arcs, opacity rules). `ir:true` holds `fn(0)` before it starts |
| `camKeys(el, w, h, keys)` | camera travel across an image inside a fixed layer: keys `{t, s, x, y, d}` in layer px |
| `highlight(id, t, {labelOut})` | rounded stroke draw-on + 8 % fill + label chip from `<div class="hlt" data-x data-y data-w data-h data-label data-pos>` |
| `flyIn(el, t, {from, rot, floatEnd, phase})` | tilted card fly-in (backOut, rot×3.5 → rot, speed blur, float on `.flt`) |
| `ringCheck(id, t)`, `confetti(fxId, t, cx, cy, n)` | ring 0.5 s → check 0.25 s → restrained confetti 1.6 s |
| `tap(cursorId, from, to, moveAt, tapAt, outAt, rippleId)` | cursor move-in, press 0.88, ripple |
| `sparkleFlight(sparkId, trailId, t, [P0..P3])` | sparkle on a cubic curve with a 14-dot trail, then twinkle + float |
| `blurIn`, `blurOut`, `backOut`, `EASE_OUT/IN/IO`, `mix`, `clamp01` | entrance/exit and the exact cubic-bezier eases |

### Rules for scene code
- Each animated property of an element has one owner. If two tweens touch the same property, the later one gets `immediateRender: false`. Split concerns into wrappers: `rise` (y + speed blur) > `float` (sine + punch scale) > `tilt` (3D pose).
- Never put a CSS `transform` on an element GSAP transforms (lint `gsap_css_transform_conflict`). Position with `left/top`; centre cards with `xPercent/yPercent` (flyIn does it).
- Planes in perspective: `poseTo` with `vp` = (frame centre − plane centre). Phone at left 200 / top 640 / 680×1448 → centre (540, 1364) → `vp [0, -404]`. Never `transform-style: preserve-3d`.
- Clear filters after blur-ins (helpers do). Hide late elements with CSS `opacity: 0` in the markup or `tl.set` at their start.
- Ids are unique across the whole page: prefix with the scene key (`cards-f1`).
- Real media: `<img src="assets/img/x.png">`; `<video id="x" src="assets/video/x.mp4" muted playsinline data-start=".." data-duration="..">` (an id on every video, no `data-start` on any ancestor; its time window is absolute seconds).
- Intentional overlaps (a card over the phone) need `data-layout-allow-overlap` on the overlapping element; intentional frame crops (the phone's bottom) `data-layout-allow-overflow`.

## Commands
```bash
cd work/<Name>
npx hyperframes init hf --example blank --resolution portrait --non-interactive --skip-transcribe   # once
/usr/bin/python3 scripts/rough_timing.py      # preview timings, no credits
/usr/bin/python3 scripts/build.py             # -> hf/index.html (re-run after every edit)
npx hyperframes check hf                       # 0 errors (lint + runtime + layout + contrast)
npx hyperframes snapshot hf --at 1.2,3.4,...  # look at every beat and cut +-0.3 s
/usr/bin/python3 scripts/tts_lines.py         # VO lines (student's own ElevenLabs key; costs credits)
/usr/bin/python3 scripts/build_vo.py          # VO master + vo/vo_words.json (prints text==script: True)
/usr/bin/python3 scripts/make_audio.py        # music + SFX + duck + -14 LUFS -> hf/assets/mix.wav
/usr/bin/python3 scripts/build.py             # again, so the <audio id="mix"> is included
npx hyperframes render hf --quality draft -o ../<Name>_draft.mp4        # quick look
npx hyperframes render hf --quality delivery --fps 30 -o <out>/<Name>_9x16.mp4
/usr/bin/python3 scripts/verify.py <out>/<Name>_9x16.mp4                # specs, LUFS, VO sync lag, silences
/usr/bin/python3 scripts/qc_sheet.py <mp4> qc.jpg 4 --ref <approved.mp4> 1.2 4.4 7.5   # side-by-side look check
```
If `npx hyperframes` tries to install an unpublished version (`ETARGET`), pin the one in `hf/package.json` or the last working one: `npx hyperframes@<version> …`.

## Audio recipe (unchanged from the approved build)
- VO: ElevenLabs `eleven_multilingual_v2`, `ms`, line by line with previous/next text, 2 seeds, auto-pick (no hesitations, no drawl, consistent pitch). Coach Am: stability 0.5, similarity 0.8, style 0, speaker boost, speed 1.10. Gaps 0.30 lead-in / 0.26 in scene / 0.45 at scene change. Clarity chain, −16 LUFS / −1.5 dBTP.
- Music: original synthesis, D major I–V–vi–IV, tempo near `plan.music.target_bpm` so the first cut lands on a beat; intro without drums, one-bar drum drop at the CTA, resolves under the end card. About 12 dB under the VO, ducked a further 6 dB (60 ms / 350 ms).
- SFX: whoosh on every cut (automatic) plus `plan.sfx` cues (whoosh, pop, tick, tap, chime, riser, shimmer).
- Master −14 LUFS, −1.5 dBTP. HyperFrames plays `mix.wav` as the single `<audio id="mix">`.

## Delivery
`render --quality delivery` writes H.264 + AAC 48 kHz, 1080×1920, 30 fps, BT.709. Run `verify.py`. If a platform needs the exact old encode (H.264 High, CRF 16, tv-range VUI tags, AAC 256 k), re-encode once:
```bash
ffmpeg -i in.mp4 -c:v libx264 -profile:v high -preset slow -crf 16 -pix_fmt yuv420p \
  -x264-params colorprim=bt709:transfer=bt709:colormatrix=bt709:range=tv -color_primaries bt709 -color_trc bt709 -colorspace bt709 \
  -c:a aac -b:a 256k -ar 48000 -movflags +faststart out.mp4
```

## Verified port (Oct 2026)
The port was verified against the approved original ad (scenes 1–3 rebuilt with its VO and word timings, compared frame by frame).
