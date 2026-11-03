# Epic Style: pipeline reference

## Contents
1. [Worked example: the Kalau Jenis Gayat beat map](#1-worked-example)
2. [Media prep](#2-media-prep)
3. [Itinerary strip and 3D tilt](#3-itinerary)
4. [Vector map and trail](#4-vector-map)
5. [Audio](#5-audio)
6. [Composition anatomy (`template/`)](#6-composition)
7. [Render and verification](#7-render)
8. [Gotchas](#8-gotchas)

## 1. Worked example
The talk runs 77.067 s and the outro 9.1 s, 86.167 s in total. Times are from the TouchUp; sync cuts on voice-energy dips.

| t (s) | VO | Background | Graphic |
|---|---|---|---|
| 0–3.55 | "Kalau jenis gayat…" | Cliff Walk portrait (looking down the bridge) | Hero "Gayat?" + script "kalau jenis", vertigo push (bg 1.0→1.16, presenter 1.2→1.0) |
| 3.55–5.35 | "Titlis Cliff Walk" | Wide bridge, pan | Place: kicker "Engelberg, Switzerland" + flag, "TITLIS / CLIFF WALK" |
| 5.35–11.6 | "3,041 meter… memang tinggi" | Portrait alt | Hero "3,041 m" + "ketinggian"; close shot on "memang tinggi" |
| 11.6–19.6 | "Bayangkan… angin… kiri kanan" | Fog side shot → bridge → panorama pan | Wind bed, wide shot |
| 19.6–24.35 | "pengalaman menarik" | Alps view | captions |
| 24.35–29.2 | "Mount Titlis… naik cable car" | **Vector map** on a blurred photo | Place "MOUNT TITLIS" (one line, 150 px, ink kicker); trail Luzern → Stans → Engelberg → Trübsee → Klein Titlis |
| 29.2–37.85 | cable car, "berpusing 360°" | Cable car → Rotair (bg rotates −3→5°) → gondola | Hero "360°" + "boleh berpusing", hum bed |
| 37.85–47.1 | family, "tak berebut tingkap", "view epic" | Gondola over mountain → bridge again | captions |
| 47.1–54.1 | Glacier cave, "vibe Frozen" | 3 glacier stills | Place "GLACIER CAVE", ice chimes |
| 54.1–59.4 | "pengalaman tu yang penting" | Turquoise lake clip | Hero "Pengalaman" + "yang penting," |
| **59.4**–67.9 | "Dengan the brand's team… harga tiket… musim" | **Itinerary page, full frame, tilted** (brand act starts) | Scroll hero → Hari 03 (lilac underline) → Hari 09 |
| 67.9–70.05 | "Hujung tahun… berebut" | Red train clip (the page lifts off) | captions |
| 70.05–74.3 | "Switzerland dengan the travel client" | Snowboarder clip | Place (brand act) "SWITZERLAND" |
| 72.6–77.05 | "bermula [harga]… contact team" | Snowboarder → sunset lake | Hero price + "bermula", brand URL at 75.0 |
| 77.067–86.167 | outro | Outro clip rises in | none |

Captions run continuously. They pause where a title shows the same words.

## 2. Media prep
- **Presenter** (`prep_media.sh presenter TouchUp.mov`): the CoreML matte takes about 5 min for 77 s. The alphamerge keeps the source pixels. A face crop compared against the TouchUp must match.
- **Outro** (`prep_media.sh outro Outro.mov`): uses `avconvert -p Preset1920x1080`, which is Apple's HDR→SDR, then `fps=30`, tagged bt709. One iPhone HLG asset left in makes HyperFrames render the whole video as HDR.
- **Montage** (`prep_media.sh clip <mov> <name> <ss> <dur> <crop_x>`): detect scenes with `select='gt(scene,0.3)',showinfo`, then grab the mid frame of each shot. Pick `crop_x` so the subject stays inside the 608-px window. Cut 0.7 s longer than the scene, because a clip starts at lift time − 0.7. Use `TPAD=1` for the last clip before the outro.
- **Stills**: 3–4K or portrait files are best. 1920×1075 stills look soft full-frame, so show them ≤ 1.5 s.
- In zsh, pass ffmpeg option lists as arrays (`"${enc[@]}"`). A plain `$enc` is passed as one word.

## 3. Itinerary
- `swift scripts/pdf2png.swift Itinerary.pdf work/itin 5` gives 3060×3960 per Letter page, and the vector text stays sharp.
- Find the band edges by printing row means: white rows (~255) are the gaps. Keep the readable content column, which was x 660–2400 for the brand web page.
- `itin_strip.py` stacks the hero, stats row, stops band and day list (pages 1–2). It paints over any sidebar that contradicts the VO; for Titlis that was "Tarikh & harga: Akan diumumkan".
- In the composition the strip is 1180 px wide (2391 tall for 1740×3523). Scroll targets are in plane px (strip px × 1180 / strip width): `#itin-scroll` y 30 → −880 (Hari 03 in view) → −1260 (Hari 09). The underline `#d3-line` sits under the day title at plane coordinates. Recompute it from the strip offsets for each new itinerary.

## 4. Vector map
- Switzerland: `geo_map.py fetch-ch geo` downloads the swisstopo swissBOUNDARIES3D outline and BAFU VECTOR25 lakes (171 lakes, ponds dropped).
- Points: use `geo_map.py gazetteer "<name>"`. Take the municipality (gg25) or "Ort" hit. For a cable car or summit, use the named station or peak (for example "Hauptgipfel Kleintitlis"). Via-points (Stans, Trübsee) make the trail follow the real route.
- `build` simplifies the outline and lakes, tests that every point is inside the boundary, and computes the zoom camera and screen pins. `inject` writes the SVG, the pins and the `#mapcam` numbers into the project.
- Timing in `anim.js`: line draw 0.95 s → fill 0.6 s → lakes 0.5 s → zoom 1.15 s `sine.inOut` → pin A → trail 1.35 s → mid pin → pin B. Pins are HTML at their final screen positions, so they appear **after** the zoom lands.
- Other countries: save the official national boundary as GeoJSON with verified city coordinates from that country's gazetteer. Lakes are optional. Never use an approximate outline. The user rejected one before, when a Lugano pin fell outside Ticino.

## 5. Audio
- The TouchUp audio is already clean (corr 1.0, broadband). A light chain is enough: highpass 80, −2 dB at 250 Hz, +1.5 dB at 3.2 kHz and 8 kHz, compressor 2.4:1, loudnorm. Then set `vo_gain_db` in `audio.json` so the VO measures −16 LUFS; single-pass loudnorm only reached −19.9.
- Soundtrack: check the section energies (2 s RMS). Use the quiet intro, then cross-fade to the quiet breakdown, so the drops are never used. With `tempo` 0.75, the cross-fade lands at source_len / 0.75. Choose the parts so it falls on a scene change; for Titlis it fell on the glacier cave.
- `music_db` −10 gave a bed of −36.4 LUFS against VO at −16.4, a median gap of 24 dB.
- The outro is about −10.7 LUFS raw, so set `outro_gain_db` −5.3.
- MBB tracks are free with credit. Suggest putting "Music: MBB – Feel Good" in the post caption for paid ads.

## 6. Composition
- `index.html` layer order (z): `#broll` 10, the `.bk` scenes in chronological DOM order (the map lives in `#bkmap`) → `.hero` 25, behind the presenter → `#pres-wrap` 30 → `.place` / `#url` 40 → `#itin` 45 → `#caps` 50 → `#outro-wrap` 60.
- `anim.js` blocks:
  - `SC`: the scene list `[id, start, end, kbFrom, kbTo]`. Each scene lifts over the previous one. The scene right after the itinerary is set visible without a lift.
  - `CAM`: the shot sizes.
  - The itinerary block.
  - The map block.
  - `hero()` / `place()`: title builders.
  - Captions.
  - The outro lift at `T_MAIN`.
- Video clips: `data-start` = the scene start − 0.7 and `data-duration` ≥ the scene length + 0.7. The presenter's `data-duration` = its length + 0.9 held frame.
- Fonts are in `assets/fonts`. Noto Serif Display is a variable font, so use `font-variation-settings: "wdth" 62.5, "wght" 800`.

## 7. Render
```bash
npx --yes hyperframes@0.8.149 lint
npx --yes hyperframes@0.8.149 snapshot --at 1.5,4.9,8.6,26.9,28.4,33.6,48.6,58.9,60.8,63.9,71.4,74.0,76.3,79
npx --yes hyperframes@0.8.149 render --quality looks --fps 30 --sdr -o renders/<name>-draft1.mp4 --quiet
ffprobe -v error -show_entries stream=pix_fmt,color_transfer,color_primaries -select_streams v renders/<name>-draft1.mp4
ffmpeg -nostats -i renders/<name>-draft1.mp4 -af ebur128 -f null - 2>&1 | grep "I:"
```
An 86 s render takes about 6 min on this Mac, because blur filters force screenshot capture. Snapshots save `frame-NN-at-T.png` plus a `contact-sheet*.jpg`. Tile them yourself with ffmpeg if the sheet name changes.

## 8. Gotchas
- GSAP on an SVG `<g>` must use `svgOrigin: "0 0"`. `transformOrigin` resolves to the bbox, which shifts the zoomed map away from the pins.
- Use `fromTo` with `immediateRender:false` for every tween on a property that is tweened more than once (camera, scroll), so the timeline is seek-safe.
- The same image used twice triggers lint `duplicate_media_discovery_risk`. Copy the file under a new name (e.g. `07b-…jpg`).
- Do not use `transform-style: preserve-3d` with videos, because they render black. Per-element `transformPerspective` is fine.
- Hero words that are too long (e.g. "Pengalaman") overflow at 250 px. Size them per word (150–200 px) and check the snapshots.
- A white map fill hides white kickers, so give the map's kicker ink colour and a white halo.
- Whisper Malay fixes seen: kantong→gantung, arah selahut→aras laut, tingkat→tingkap, gula→gua, Bujong→Hujung, sema→semak, promong→promo. Do not caption uncertain words (e.g. "Vacation/Pakej"); put them in a title instead.
- The itinerary web page may say the price is not announced. Remove that from the strip and tell the user.
