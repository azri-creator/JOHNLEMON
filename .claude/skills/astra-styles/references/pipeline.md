# Astra Styles — pipeline and numbers

Reference build (Coach Am's original project, not shipped) (`scripts/build.py`, `scripts/audio.py`, `hf/` 16:9, `hf9/` 9:16). Final renders:
`hf/renders/AI_Edit_Merapu_Astra_16x9_v2.mp4` and `hf9/renders/AI_Edit_Merapu_Astra_9x16_v2.mp4`. Everything below is what
that build used. `template/scripts/build.py` and `audio.py` are copies of those two files: read them as the recipe, then edit
the config blocks.

## 1. Assets contract (paths the template expects, relative to `hf/`)

| Path | What |
|---|---|
| `assets/src/main.mov` | the footage (muted in the HTML; voice is a separate track) |
| `assets/person.webm` | presenter matte, VP9 alpha, same size and fps as the footage |
| `assets/res/res1..4.mp4` | result videos (screen recordings cropped to the chat bubble); `CARD_H` holds each height at a 578 px width |
| `assets/fb/fb1.png`, `fb2.png` | feedback screenshots (names/avatars blurred); `FB_AR` holds height/width |
| `assets/thumb/*.jpg` | thumbnails for the fan (`FAN` picks 3) |
| `assets/fonts/*.woff2` | Archivo (variable wdth), Outfit, Inter (variable wght) — copy from `template/assets/fonts/` |
| `assets/audio/voice.wav`, `music.wav`, `sfx.wav` | written by `audio.py` |
| `build/headtrack.json` | `[[t, head_top_y, head_cx], …]` from `scripts/headtrack.py` (4 fps) |
| `build/voice48.wav` | mono 48 kHz voice (`ffmpeg -vn -ac 1 -ar 48000`) |

## 2. Canvas and layer order (root `index.html`)

Size: 1920×1080 (`FMT=16x9`) or 1080×1920 (`FMT=9x16`). Page background `#050304`. From bottom to top:

1. `#foot > #wob > #cam > <video id=base>` — footage. `#cam` is the camera (transform-origin 0 0); `#wob` is the
   chaos-beat shake (transform-origin 50 % 50 %). In 9:16 the 16:9 footage is scaled by K = 1920/1080 and shifted
   `BL = 540 − 1000·K` so the presenter (x ≈ 1000 of 1920) is centred.
2. `#scrL` (16:9) / `#scrT` (9:16) — scrims for type legibility; below the type.
3. `#headsB` — the kicker and the **hero word** (behind the head).
4. `#backCards` — result cards that must pass behind the presenter.
5. `#pmatw > #wob2 > #camP > <video id=pmat>` — presenter matte, mirroring every `#cam` tween. It is `opacity:0`
   except in the windows where something sits behind the head (hero word, back cards): `tl.set("#pmatw",{opacity:1},a)`.
6. `#front` — front cards, comment card, chaos stickers, two-tone blocks, pill, native subtitles, feedback screenshots + rims,
   CTA, sparkles.
7. `#stage` — the dark stage (vignette, labels, prompt bar `#ui`, thumbnail fan, closing type). Fades in over the blurred footage.
8. `<audio>` voice / music / sfx (tracks 20–22).

Mark intentional overlaps with `data-layout-allow-overlap` / `data-layout-allow-occlusion` (and `data-layout-ignore` on
decorative/scrim nodes) so `check` stays clean.

## 3. Camera

`face(t)` averages the head track within ±0.6 s and returns the pivot (cx, top + 140), scaled by K and shifted by BL.
`clamp(S, tx, ty)` keeps the scaled footage covering the frame: `tx ∈ [W − (BL+BW)·S, −BL·S]`, `ty ∈ [H − BH·S, 0]`.

- `C(t, S)` — zoom pivoting on the face: `tx = px(1−S)`, `ty = py(1−S)`.
- `R(t, S=1.32)` — "type moment" framing. 16:9: `ty = 430 − py·S`, `tx = 0` (presenter lands in the right third, type on the
  left). 9:16: scale `S·.94`, `ty = 1060 − py·S·.94` (face low, type above).
- `CAM = [(time, (S,tx,ty), duration, ease), …]`; an assert forbids overlapping tweens.
- Recipe: open at exactly 1.0 (no wake zoom) then push to 1.07 over 4 s `sine.inOut`; on key words `back.out(3)` in
  0.1–0.12 s to 1.16–1.34, then `power2.out` back 0.15–0.3 s; at each two-tone block hard-set `R()` and push to 1.35–1.36
  over 2.2–3.2 s `sine.inOut`; between them `C()` pushes 1.02–1.07 over 2.3–9.4 s; "release" words zoom out
  (`expo.inOut`, 0.35 s). Hard-set 1.0 on the stop word of the chaos beat.
- Chaos shake (`WOB`, seeded `Random(7)`): every 0.11–0.2 s `rotation ±1.6°, x ±10, y ±8` on `#wob, #wob2`, then reset.

## 4. Motion primitives (copy these)

```js
const B0="blur(0px)", BL=p=>"blur("+p+"px)";
function bin(el,t,o){o=o||{};tl.fromTo(el,{opacity:0,filter:BL(o.b||18),x:o.x||0,y:o.y||0,scale:o.s||.96},
  {opacity:1,filter:B0,x:0,y:0,scale:1,duration:o.d||.5,ease:"expo.out",immediateRender:false},t);}
function bout(el,t,o){o=o||{};tl.to(el,{opacity:0,filter:BL(o.b||16),scale:o.s||1.02,duration:o.d||.3,ease:"power2.in"},t);}
```
Always follow a `bout` with `tl.set(el,{opacity:0}, t_end+.01)` and never let a `bin` and `bout` on the same element overlap.

## 5. Scrims

`.scrimL`: `linear-gradient(90deg, rgba(10,5,8,.72) 0%, rgba(10,5,8,.5) 28%, rgba(10,5,8,0) 58%)` (16:9 only, behind left-aligned
type). `.scrimT`: `linear-gradient(180deg, rgba(10,5,8,.66) 0%, rgba(10,5,8,.34) 22–26%, rgba(10,5,8,0) 38–46%)`. Spans come from
`SCRIM_L` / `SCRIM_T` (merged when they touch within 0.05 s); fade in 0.35 s `power2.out`, out 0.3 s `power2.in`.

## 6. Two-tone type (`TT`)

`(id, start_l1, start_l2, end, line1, line2, (x,y,size,align) for 16:9, (y,size) for 9:16)`.
Archivo weight 820, `font-stretch:86%`, uppercase, line-height .98. `.l1` `#F6F4F5` with a soft shadow; `.l2` the accent gradient clipped
to text with a faint drop-shadow. 16:9: left at x=150, y 330–360, size 112–128, slides in from x −40; a centred top variant
(`align 'c'`, y 70, size 104) for a closing line. 9:16: centred, y 330, size 108–124 (y 1330 when the face is up). Rules: line 2
lands ≥ 0.8 s after line 1; `end − .3 ≥ start_l2 + .5` (asserted). Type is verbatim from the transcript, uppercased.

## 7. Dark stage + virtual camera

`#stage`: `#050304` with `.vg` (edge vignette `rgba(92,8,36,.55)` plus two corner glows `rgba(120,10,44,.35/.28)`). Enter: footage
`blur(16px)` 0.28 s, stage fade 0.25 s, label and bar blur-in. Prompt bar: radius 40, `#1A191C`, border 1.5 px `rgba(255,255,255,.08)`,
text Inter 450 46 px, caret 3×50 px `#FF3D8E`, "+" and "Claude ▾" hints, send button 70 px circle. The bar is **wider than the frame**
(1460–1500 px) so the virtual camera (`#ui` scale/x/y keys) can pan along the typed text:

- 16:9 keys: `(14.7, 1.32, −60, −230, .9, expo.inOut)`, `(15.6, 1.32, −560, −230, 1.6, sine.inOut)`, `(17.25, 1.5, −1300, −470, .7, expo.inOut)`.
- 9:16 keys: scale 1.15 → 1.3 (see `UI` in the template).
Typing: `chars()` wraps each character in a `display:none` span, switched with `tl.set` evenly across the spoken time. Cursor arrow
appears 0.55 s before the send, send scales .86→1 and turns `#FF3D8E`, stage blurs out 0.1 s after. Stage exit `blur(20px)` 0.22 s.

## 8. Cards and rack focus

Cards: radius 26, `box-shadow: 0 40px 80px rgba(10,4,8,.45), 0 0 0 1px rgba(255,255,255,.14)`. Enter
`fromTo({opacity:0,filter:blur(24px),x:dx,rotationY:ry·1.6,rotation:rz,transformPerspective:1500,scale:.9},{…,rotationY:ry,scale:1,duration:.7,ease:"expo.out"})`,
then a slow bob (`y −14` front / `+12` back, `sine.inOut`, ≤ 3.2 s). 16:9 widths 290–300 at y 250–300; rotationY ±16–24.
Rack focus: `RACK = "#foot, #pmatw, #backCards, #cd"` → `filter: blur(12px) brightness(.62)` 0.5 s `power2.inOut`, while the hero card flies to
`CA_FWD` (16:9: x 950, y −100, scale 1.733) 0.75 s `expo.inOut` and the other front card fades. Recede the hero card
(`blur(10px) brightness(.6)`, scale 1.63) before screenshots come in; refocus with a 0.01 s set.

## 9. Proof screenshots

White cards radius 26 with a soft shadow, blur-in with `rotationY` 6–9° → 3–5° (right) and −5–−7° → −2–−4° (left). The pink
rim: `border 4px #FF3D8E`, radius 30, glow `0 0 22px rgba(255,45,120,.55)`, box given in % (`RIM`), scales 1.08 → 1 in 0.35 s on the
spoken word, with a soft blip (880 / 988 / 1175 Hz).

## 10. Audio (`scripts/audio.py`, needs numpy + scipy)

- Voice: `voice48.wav` at −1.5 dB (fold to mono).
- Calm bed: pads on D – Bm – A – C(add9), two detuned sines (.997/1.003) per note, low-passed 1.4 kHz, sub root, soft plucks, 68 BPM; whole bed low-passed
  3.8 kHz, normalised to **21 dB under the voice RMS**, 1.5 s fades, dropped during the chaos beat and swelled back over 1.2 s after the stop word.
- Chaos loop (only if the beat exists): 150 BPM kick + cowbell + square lead, 12 dB under the voice RMS, ends hard on the stop word.
- Duck: `1 − .45·clip((env(voice,.12) − (−36 dB))/((−22 dB) − (−36 dB)), 0, 1)` on the music; SFX duck `.35`.
- SFX, all synthesised per event (seeded `default_rng(2026)`): airy whoosh on every blur-in (band-pass noise, random corner ×0.8–1.25, `sin²`
  envelope, level .07, placed 0.55 × its length before the event), keyboard ticks per typed character (hp noise, 0.03 s), click on send,
  ring blips, sparkle on the CTA (9 sines 2.4–5.2 kHz). Chaos: boing, pop, whistle up/down, horn chord, boom, record scratch at the stop word.
- Print voice RMS, music RMS, SFX peak and mix peak. Verify 0.5 s windows: nothing louder than the voice.

## 11. Run and verify

```
FMT=16x9 python3 scripts/build.py && python3 scripts/audio.py
cd hf && npx hyperframes check && npx hyperframes snapshot --at <beat times>
npx hyperframes render --quality delivery --fps 30 --video-frame-format png
cp -R hf/assets hf9/ && FMT=9x16 python3 scripts/build.py      # portrait story, then render in hf9
```
1. `check` with 0 errors. 2. Snapshots at every beat: look for type over faces, clipped UI after zoom, hero word fully readable,
colliding layers. 3. Draft render, voice lag by cross-correlation (0 ms), loudness. 4. Delivery render, spot-check 6–9 frames.
5. Say what could not be verified (the mix was never heard, doubtful transcript words, licence of any supplied music).
