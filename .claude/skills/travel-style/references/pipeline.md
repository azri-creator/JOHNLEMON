# Travel Style: pipeline reference

## Contents
1. [Worked example: the first build's beat map](#1-worked-example)
2. [A-roll cleaning](#2-a-roll-cleaning)
3. [Media prep](#3-media-prep)
4. [Vector map](#4-vector-map)
5. [Audio](#5-audio)
6. [Composition anatomy (`template/`)](#6-composition)
7. [Render and verification](#7-render)
8. [Gotchas](#8-gotchas)

## 1. Worked example
Six WhatsApp takes of the presenter, 576×1024 portrait (stored 1024×576 with ±90° rotation), ~64 s raw →
42.36 s of clean talk + 3.2 s logo end = 45.6 s. Five iPhone B-roll clips, 1584×2816, ambient audio only.

| t (s) | VO (worked example, travel lifestyle) | Background | Graphic |
|---|---|---|---|
| 0–5.6 | "Setelah bertahun-tahun anda bekerja dan membesarkan keluarga, inilah masanya…" | seated take, own background | hero "Bertahun-tahun" (122 px) + script "setelah"; glide 1.0→1.08 at "inilah masanya" |
| 5.6–8.9 | "…capai impian anda yang telah lama anda impikan." | desert / scenic B-roll, full frame (lifts in, lifts off) | place: kicker "Inilah masanya untuk" / "CAPAI / IMPIAN" (gold) |
| 8.9–12.5 | "Dan bersyukur, inilah masanya untuk anda nikmati impian untuk menjelajah" | seated take with brochure, own background | hero "Bersyukur" (168 px) + script "dan" |
| 12.5–15.4 | "destinasi impian anda." | city skyline at sunset, full frame | place: "Destinasi impian" / "JOM / BERCUTI" |
| **15.4**–19.98 | "Bersama [brand], mulakan perancangan percutian anda dengan lebih yakin." | cut-out over a group in a hotel lobby (**brand act starts**) | place (brand act): "Bersama" / "NAMA BRAND" (first word gold); hero "Yakin" + "lebih" |
| 19.98–28.15 | "Menariknya… pada hari pertama kita akan singgah di Abu Dhabi dahulu, baru akan masuk ke Kota Dubai." | **vector map** on a blurred destination frame; presenter steps down 210 px | labels UAE / MALAYSIA → plane KLIA→Abu Dhabi 21.3–23.5 → zoom 23.65–24.85 → pin Abu Dhabi 24.95 → trail 26.25 → pin Dubai 27.5 |
| 28.15–31.0 | "Jadi anda tak perlu risau [tentang perjalanan] daripada Malaysia." | cut-out over a street scene | hero "Risau" + script "tak perlu" |
| 31.0–33.3 | "Jika anda merancang untuk pergi bercuti" | seated take, full-frame layer (lifts in) | captions |
| 33.3–35.9 | "bersama dengan pasangan atau keluarga," | couple B-roll, full frame | place (brand act): "Bercuti bersama" / "PASANGAN / & KELUARGA" |
| 35.9–37.84 | "boleh hubungi [brand] sekarang." | seated take, full-frame layer | captions |
| 37.84–42.36 | "Klik WhatsApp sekarang, menemani perjalanan terindah anda." | standing take, original backdrop | place (brand act): "Klik sekarang" / "WHATSAPP KAMI" |
| 42.36–45.6 | (pad swell, bell) | destination footage blurred to 16 px | logo rises + gold sweep, script tagline, contact line |

## 2. A-roll cleaning
- WhatsApp takes carry rotation metadata; ffmpeg auto-rotates. Two of the six were 31.58 fps, so `render_aroll.py` forces `fps=30`.
- The prompter cue sits in the first 0.3–2.8 s of each take, often at the same level as the talent (−32…−38 dBFS), so a threshold alone can't separate them. Find it by: 0.1 s loudness envelope per take, a Whisper pass on the first 2.2 s boosted +12 dB, and a Whisper pass from the suspected talent start. Set each take's `from` just after the cue and `to` before the stop-tap (a −12…−19 dB click in the last 0.2 s).
- `cutlist.py` thresholds: −37.5 dBFS, silences > 0.24 s squeezed to 0.14 s, pre-roll 0.06 s, tail 0.12 s. Natural line gaps end up ~0.18 s.
- `render_aroll.py` per segment: trim → fps 30 → lanczos to 1080×1920 → `unsharp=5:5:0.35`; audio: mono fold, 12–15 ms fades at every cut, then `highpass=80, afftdn=nr=10:nf=-45, acompressor 2.5:1, loudnorm I=-16`. It also writes `line_times.json` (where each take starts in the cut).
- Re-transcribe `voice.wav` with `whisper-cli -ml 1 -sow -oj` and an initial prompt listing the brand name, the place names and other key words (e.g. "Abu Dhabi, Dubai, bersyukur, WhatsApp").

## 3. Media prep
- `media.sh cutout`: `remove-background --quality best` took ~2 min for 42 s on an M3 Pro. Inspect the matte by compositing it over flat green at 5–6 times. Standing takes keyed cleanly; seated takes kept bits of the chair (harmless, because those shots sit on their own background); a take shot in front of a printed photo backdrop kept part of the print around the head → that shot used its original frame instead.
- Own-background slices: cut them from `aroll_cut.mp4` at the same timeline time they play (e.g. `media.sh clip aroll_cut.mp4 own5a 30.3 3.8`, then `data-start="30.3"`), so the picture stays in sync with `voice.wav`. Use a separate file for each element: the same file twice triggers lint `duplicate_media_discovery_risk`.
- B-roll clips start 0.7 s before their lift and run ≥ 0.7 s past it (scene length + 0.7). The end-card footage must run to the end of the video.

## 4. Vector map
- Data: `curl -L -o ne_countries.geojson https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_10m_admin_0_countries.geojson` (13 MB). Official national boundaries are not always available in machine-readable form; Natural Earth is the accepted fallback. Say so if asked.
- Points in the worked example: KLIA 2.7448, 101.7074; Abu Dhabi 24.4539, 54.3773; via point 24.7600, 54.9400 (inland, so it passes the inside check); Dubai 25.1972, 55.2744. Look every point up again before use. Query: `curl -s -G https://nominatim.openstreetmap.org/search --data-urlencode "q=<place>" --data-urlencode format=json --data-urlencode limit=1 -A "<project>/1.0"`.
- `route_map.py` keys are roles: `origin` = flight origin, `a` = pin A, `via` = trail midpoint, `b` = pin B. For another route change the coordinates (and ISO A3 country from Natural Earth's `ADM0_A3`), the pin label text and the country labels in `index.html`. Camera 0 fits lon 30–106 with lat 32 at y = 150 (move `X0`/`Y0`/`U0` for destinations outside that window); camera 1 puts pin A and pin B 470 px apart around (540, 420). The script fails if a point falls outside its country. Output: `assets/js/routemap.js` (`window.ROUTEMAP`).
- In `anim.js` the overview is a static viewBox; the plane and the arc share one proxy tween (seek-safe); the zoom is a proxy that sets the viewBox with log interpolation of the width (`w = w0·(w1/w0)^z`) so the fly-in speed feels even. Borders use `vector-effect="non-scaling-stroke"`. Pins and labels are HTML at their final screen positions and appear after the zoom lands.

## 5. Audio
- `music.py <out> <dur> <bell_at>`: five slow chords in D (Dmaj9-ish → Bm → Gmaj7 → A → D), detuned sine pairs, 3 s cross-fades, slow breathing LFO, bell (D5 with inharmonic partials) at the logo. ~8 s to synthesise 46 s.
- `media.sh bed`: pad → lowpass 3.2 kHz, small echo room, loudnorm −36 LUFS; +7 dB swell over 0.7 s after the voice ends; fade in 1.2 s, out 1.3 s; limiter 0.89. Measured: voice −16.1, pad −35.9 under the talk, mix −15.1 LUFS, peak −3.1 dBFS.
- First build's SFX events: lift 0.55 at every lift (5.6, 8.9, 12.5, 15.4, 19.98, 28.15, 31.0, 33.3, 35.9, 37.84, 42.25); pop 0.35 at every title and pin; jet 0.32 at 21.3; zoom 0.45 at 23.65.

## 6. Composition
- Layer order (z): `#broll` 10 (scenes under the presenter, chronological: own background → lobby → map → street → CTA footage) → `.hero` 25 (behind the presenter) → `#pres-wrap` 30 (cut-out) → `#cut` 35 (full-frame cutaways and seated full-frame layers, chronological) → `.place` 40 → `#caps` 50 → `#end` 60.
- `anim.js` blocks: `lift()` / `liftOff()` / `KB()` helpers → background schedule → cutaway schedule → camera `glide()` list (targets `#pres-cam`, plus `#own-cam` while a seated own-background shot is on screen) → map → `hero()` / `place()` list → captions → end card.
- The presenter `<video>` is muted; all sound comes from one `<audio id="mix">`. Video clips sit inside untimed `.kb` / `.own` wrappers; never time both a wrapper and its video.
- Fonts are local woff2 with `@font-face` (no network at render). Noto Serif Display is variable: `font-variation-settings: "wdth" 62.5, "wght" 800`.

## 7. Render
```bash
npx --yes hyperframes@0.8.149 lint
npx --yes hyperframes@0.8.149 snapshot --at 1.6,4.5,6.6,9.6,13.8,16.6,19.4,20.9,22.4,24.4,25.6,27.9,29.6,32.2,34.6,36.8,39.4,41.6,44.6
npx --yes hyperframes@0.8.149 render --quality looks --fps 30 --sdr -o renders/<name>-draft1.mp4 --quiet
ffprobe -v error -show_entries stream=pix_fmt,color_transfer,color_primaries -select_streams v renders/<name>-draft1.mp4
ffmpeg -nostats -i renders/<name>-draft1.mp4 -af ebur128 -f null - 2>&1 | grep "I:"
```
A 45.6 s render takes ~2–3 min on an M3 Pro (blur filters force screenshot capture).

## 8. Gotchas
- Hero words overflow at 250 px when long ("Bertahun-tahun" needed 122 px, "Bersyukur" 168 px). The script line clips at x < 0 unless its `left` is nudged in.
- A hero word too low gets swallowed by the head ("WhatsApp" lost its middle letters). Keep ≥ 85 % of the letters above the hair.
- Seated cut-outs over B-roll look like floating people: cover seated shots with full-frame layers instead.
- Mattes keep printed or photographic backdrops that touch the head (towers, pillars). A clip-path around the head did not hide it; use the original frame.
- Transitions between two different seated/standing takes can expose the wrong take for a few frames: hide the cut-out (`#pres-wrap`) while a full-frame layer is rising.
- GSAP on clip elements: never tween `autoAlpha`/`visibility` on a `.clip`; animate the wrapper `.bk`.
- `fromTo` with `immediateRender:false` for every property tweened more than once (camera, pins), so seeking is safe.
- Whisper hallucinates "Terima kasih kerana menonton" on ambient-only B-roll: it means the clip has no speech.
