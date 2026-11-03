---
name: travel-style
description: >-
  "Travel Style": a locked 9:16 editing style for travel-lifestyle and holiday-package ads (first built for a travel
  agency). Raw phone takes are cleaned (the off-camera prompter voice and every silent gap cut out, lines in
  script order), then the presenter is cut out pixel-exact over real travel footage. Pop-out palette: navy + gold. Two
  colour acts (gold destination titles, then a white-on-navy brand act). Condensed serif place titles, a big Poppins
  hero word plus a Sacramento script behind the head, captions with royal-yellow keywords, vertical "lift"
  transitions, a real-data vector map with a flight and a ground trail, and the logo only at the end over blurred
  real footage. Use whenever someone says "Travel Style", "style travel", "travel lifestyle", "iklan pakej
  percutian", or asks for a 9:16 travel or holiday-package ad from talking-head takes and B-roll, even without naming
  the style. Built with HyperFrames; renders the real MP4.
compatibility: >-
  Claude Code (shell access). Needs ffmpeg/ffprobe, Python 3, Node 18+ (npx hyperframes@0.8.149), and whisper-cli or
  `npx hyperframes transcribe` for Malay transcription. The cut-out uses `hyperframes remove-background` (CoreML on
  Apple silicon, CPU elsewhere, slower).
---

# Travel Style

`template/` holds a finished, approved build. Its files:
- `index.html`;
- `assets/js/anim.js` (all timing);
- `captions.js`;
- `routemap.js` (the baked map);
- the fonts and a placeholder logo.

Its worked example is a holiday-package ad: KLIA → Abu Dhabi flight, then an Abu Dhabi → Dubai trail. Treat it as a worked example. Copy it, swap the media, and edit its data (scene times, titles, captions, map points); don't rewrite it from scratch. Commands, the beat map and the gotchas are in `references/pipeline.md`. Read it before building.

Each new video keeps the identity below and adds **one signature moment of its own** that fits its story. In the example, that moment is the flight map. Repeating the same hero moment in every ad makes the series feel templated.

## Locked identity

| Layer | Rule |
|---|---|
| Inputs | Phone talking-head takes of the presenter. These are often several short WhatsApp or iPhone clips, sometimes one long take, and each starts with an **off-camera voice reading the line first** ("suara campak skrip"). Portrait travel B-roll (iPhone, usually 1584×2816). The brand's own logo, which replaces `template/assets/img/brand-logo.png`. Probe everything: rotation metadata, HDR (iPhone HLG must be tone-mapped to SDR with Apple `avconvert -p Preset1920x1080`), loudness and L/R polarity. |
| Edit | Keep only the talent's delivery. Cut the prompter cue at the head of each take, squeeze inner silences to ~0.14 s and line gaps to ~0.2 s, and never speed speech up. Order lines by **the script's logic**, not by file names. Cut on loudness-envelope dips, because Whisper word times drift 0.2–0.3 s. |
| Format | 1080×1920, 30 fps, SDR BT.709, rendered with `--sdr`. |
| Palette | Navy `#0a1a4f` / deep `#071238`, brand gold `#ffc72c` (highlight `#ffe07a`), white, and royal yellow `#fada5e` for caption keywords. Bright, high-contrast and premium: gold never sits on gold without a navy edge. Swap the gold for the student's brand colour if asked. |
| Two colour acts | **Destination act** (the emotional opening, up to the line that names the brand): place titles in brand gold with an 8 px navy stroke and a 7 px navy drop, hero words white with a soft navy glow, script in pale gold. **Brand act** (from the exact words that name the brand): text white with a 10 px navy stroke, a hard navy drop and a navy halo, with accents (e.g. "&", "WhatsApp") in brand gold. Captions switch to the navy stroke in the brand act. |
| Captions | Poppins 800, 66 px, 2–4 words, at y ≈ 1500, white with a 9 px dark stroke and a hard drop shadow. One keyword per chunk in royal yellow. Leave out words a big title already shows. Fix Whisper's Malay spellings before they go on screen. |
| Place titles (front) | Noto Serif Display condensed (`wdth` 62.5, `wght` 800), caps, 170–210 px, at y ≈ 150–190. One or two lines rise out of a mask with a stagger, under an italic Poppins 700 kicker. Use them on full-frame B-roll and for the brand line. |
| Hero words (behind the head) | Poppins 800 at 120–250 px (size each word so it fits inside 1080 px), letter-spacing −0.035em. A Sacramento script (128 px, −7°) writes on left→right over its top-left. Place it so the presenter's hair overlaps only the bottom ~15 % of the letters. At most one per sentence: the hook word, the emotion word or the key benefit. |
| Transitions | **Lift** only. The incoming layer rises from below (yPercent 100→0, blur 14→0, 0.7 s `power3.inOut`) while the outgoing one drifts up 24 % with an 8 px blur. A full-frame cutaway leaves by lifting off upward (yPercent 0→−100) to reveal the next scene. No wipes, flashes, dims or shape transitions. |
| Presenter | A pixel-exact cut-out: the ML matte alphamerged with the source YUV, BT.709. **Standing** shots go over real footage or the map. **Seated** shots keep their own background, because the cut-out sits on its own frame and chairs never float; full-frame cutaways cover them. Check every matte for leaks from printed backdrops behind the head. If a shot leaks, use its original frame for that shot. Never tint, dim or re-grade the presenter. |
| Camera | Calm: sine glides of ≤ 1.2 s between 1.0 and 1.08. The takes are often 576p, so don't push further. Seated own-background shots move the cut-out and its background together. During the map the presenter steps down ~210 px so the route sits above the head. |
| Footage | Never grade, scrim, vignette or dim B-roll. Blur is the only treatment (map background, end card). Add a slow linear drift (scale 1.0→1.08) while a clip is visible. Don't label footage with a place name unless the location is confirmed. |
| Map (signature) | Real data only: Natural Earth 10m countries and OpenStreetMap-verified coordinates. `scripts/route_map.py` checks that every point sits inside its country. Navy sea and land, with the origin and destination countries in brand gold and a white edge. The sequence: overview → the plane flies origin → pin A along a gold arc → log zoom in → pin A (script "hari pertama") → navy trail via a midpoint → pin B (script "seterusnya"). Place it on the line that names the places, for 5–8 s. |
| End | The logo appears **only at the end**. The last shot lifts off, the real footage behind it blurs to 16 px, the logo rises with a gold light sweep, then the script tagline and the contact line appear ("WhatsApp" in royal yellow). |
| Audio | Voice cleaned (highpass, light denoise, 2.5:1 compression, loudnorm) to −16 LUFS. An original soft ambient pad (no vocals) sits ~20 dB under the voice, swells after the last word, and has one soft bell on the logo. SFX are soft and synthesised: lift whoosh, title pops, a jet under the flight and air on the zoom. |

## Storyboard first (must)

Make storyboard frames with the `storyboard-frames` skill (`.claude/skills/storyboard-frames/`) before any MP4 render, draft or delivery:
1. Build the composition.
2. Snapshot one still per beat onto numbered sheets.
3. Let the student refine frame by frame.
4. Render only after they reply "ok storyboard".

Every render step in the workflow below comes after that approval.

## Workflow

1. **Probe and plan.**
   1. Probe every file.
   2. Transcribe each take in Malay. Transcribe the first 2–3 s of each take separately (boosted) to hear the prompter cue.
   3. Make contact sheets of the takes and the B-roll.
   4. Send the student a beat table (time, VO line, background, graphic) with the open questions: line order, any place names in the B-roll, music preference, anything unclear in the VO.
   5. Don't put prices or claims on screen that the VO doesn't say.
2. **Clean the A-roll.**
   1. Run `scripts/cutlist.py` (`clips.json` in script order), then `scripts/render_aroll.py`. This gives `aroll_cut.mp4` (1080×1920, 30 fps) and `voice.wav` (−16 LUFS).
   2. Re-transcribe `voice.wav` with word times. It must contain no prompter words, and these word times drive caption and title timing.
3. **Project.**
   1. Copy `template/` to a new project folder.
   2. Run `bash scripts/media.sh cutout aroll_cut.mp4`.
   3. Cut backgrounds with `media.sh clip`: the B-roll, plus slices of `aroll_cut.mp4` for seated own-background shots.
   4. Use `media.sh still` for the map background.
4. **Map** (if the story names the route).
   1. Download Natural Earth 10m countries.
   2. Edit `PTS` in `scripts/route_map.py` (origin, pin A, via, pin B, each with its ISO A3 code). Run it into `assets/js/routemap.js`; every point must print `inside=True`.
   3. Change the pin and country labels in `index.html`.
5. **Audio.**
   1. Run `scripts/music.py` (pad, plus the bell at the logo time).
   2. Run `media.sh bed`, then `media.sh sfx`.
   3. Run `scripts/mix_sfx.py` with an events list that matches your lifts, titles, pins and map.
   4. Keep the voice at least 20 dB above the music.
6. **Composition.** Edit `index.html` (layers, titles, media `data-start` / `data-duration`), `assets/js/anim.js` (backgrounds, cutaways, camera glides, map times, titles, end) and `captions.js`. Keep the layer order described in the pipeline reference.
7. **Check.**
   1. Run `npx --yes hyperframes@0.8.149 lint`.
   2. Snapshot every title, cutaway and map beat, and the end.
   3. Look for: text overflowing 1080 px, hero words hidden by the head, matte leaks, captions colliding with titles, and seated cut-outs floating.
8. **Render.**
   1. Use `render --quality looks --fps 30 --sdr` for the draft.
   2. Verify with ffprobe (yuv420p, bt709) and ebur128 (≈ −15 / −16 LUFS).
   3. Crop a face from the render and compare it with `aroll_cut.mp4`.
   4. Do the delivery render after the student approves.
