# Journey Map Hook — pipeline reference

## Presenter key (green screen `#06e006`)
```bash
ffmpeg -i cutout.mov -an -vf "chromakey=color=0x06e006:similarity=0.16:blend=0.07,despill=type=green:mix=0.6,format=yuva420p" \
  -c:v libvpx-vp9 -pix_fmt yuva420p -auto-alt-ref 0 -b:v 0 -crf 20 -row-mt 1 -cpu-used 3 assets/presenter.webm
```
Use the `<video>` muted; the VO plays from a separate `<audio>`. Wrap the video in non-timed divs (`#pres-pip` for mode, `#pres-cam` for camera).

## Voice clean (band-limited phone audio, ~4 kHz cliff)
```bash
ffmpeg -i vo.m4a -af "highpass=f=85:poles=2,equalizer=f=240:t=q:w=1.1:g=-2.5,equalizer=f=3100:t=q:w=0.9:g=2.5,\
aexciter=level_in=1:level_out=1:amount=2.4:drive=8:blend=0:freq=4200:ceil=11000,equalizer=f=6500:t=q:w=0.8:g=1,lowpass=f=13000,\
acompressor=threshold=-21dB:ratio=2.6:attack=12:release=140:makeup=3,aecho=1.0:0.88:11|19:0.10|0.06,\
alimiter=limit=0.89:level=disabled,loudnorm=I=-16:TP=-1.5:LRA=7" -t <len> -ar 48000 -c:a aac -b:a 224k vo_clean.m4a
python3 scripts/spectrum-report.py before.wav after.wav   # 4-12 kHz should rise ~14-24 dB relative
```
`aexciter` ceil must be ≥ 9999.

## Music bed (≈20 dB under voice, ducked, full length)
```bash
ffmpeg -ss 0 -t 72 -i bgm_full.m4a -i vo_clean.m4a -filter_complex \
"[0:a]lowpass=f=8500,equalizer=f=1800:t=q:w=0.6:g=-5,equalizer=f=350:t=q:w=0.8:g=-2,loudnorm=I=-34:TP=-9:LRA=6,afade=t=in:st=0:d=2[m];\
[m][1:a]sidechaincompress=threshold=0.16:ratio=2.2:attack=20:release=500:makeup=1,apad=whole_dur=69,afade=t=out:st=64.5:d=4[d]" \
-map "[d]" -t 68.5 -ac 2 -c:a aac -b:a 192k bgm_mix.m4a
```
Composition volumes: `vo` 1, `bgm` 0.7, `sfx` 0.3. `loudnorm` TP range is −9…0.

## Map baking (`scripts/bake-map.mjs <scratch> <out>`)
Needs `sharp` and `@napi-rs/canvas` (npm i in a scratch dir) plus these files in `<scratch>`: `ne.json` (Natural Earth 10m countries), `data/ne_lakes.json`, `data/ne_lakes_eu.json`, `data/ne_rivers.json`, `geo/sb_CH.json`, `geo/sb_LI.json` (official boundary).
- Official CH outline: `https://api3.geo.admin.ch/rest/services/api/MapServer/find?layer=ch.swisstopo.swissboundaries3d-land-flaeche.fill&searchText=CH&searchField=id&returnGeometry=true&sr=4326&geometryFormat=geojson`
- City gazetteer: `https://api3.geo.admin.ch/rest/services/api/SearchServer?searchText=<name>&type=locations&origins=gazetteer&sr=4326`
- Outputs `*_albedo.jpg`, `*_height.bin` (int16 metres×4), `*_sdf.png`, `meta.json` (borders, POIs, rivers) and `geo_check.json` (every city inside the outline + km to border). Fix any `inside=false` before rendering.
- Terrarium 8-bit elevation: always `removeAlpha().toColourspace("srgb")` when mosaicking tiles.
- Patches: `eu` (backdrop), `ch` (country), plus one zoom patch per featured landmark. Fine patches are cut out of coarser ones in the shader (`uCutA/uCutB`).

## Composition notes
- Layers z-order: bg → map → b-roll → scrims → titles → presenter → CTA → captions → vignette. B-roll elements are in chronological DOM order so each incoming layer covers the previous one.
- Slide helper: incoming `xPercent 100→0` with blur, outgoing `xPercent 0→−30` with blur+dim, then hide + reset.
- Presenter modes FULL/PIP and camera poses are GSAP tweens on `#pres-pip` and `#pres-cam`; background punches follow the presenter scale at 0.42× (`punchTween`).
- Map camera keys live in `assets/js/akg-config.js` (`cam`, `mapOn`, `labels`); the map layer is only visible inside `mapOn`.
- Draft render ≈ 1.5 min, delivery ≈ 2.5 min per format on an M3 Pro.

## 9:16
`python3 scripts/make-9x16.py <16x9_project> <new_project> [vertical_bg.png]`, then lint, snapshot (check the wide map shot fits and captions wrap), and render.
