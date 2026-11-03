---
name: epic-style
description: >-
  "Epic Style": a locked 9:16 style for travel / destination ads (first built for a travel client's "Kalau Jenis Gayat",
  Mount Titlis). A cut-out presenter over real destination photos. Two colour acts: the destination's flag colours,
  then the brand colour with a readable glow from the brand line. Condensed serif place titles, a big Poppins word plus
  script behind the head, captions with royal-yellow keywords, vertical "lift" transitions, an accurate vector map with
  an A to B trail, the itinerary PDF as a full-frame 3D-tilted scrolling page, a price CTA, then a team outro. Use
  whenever the user says "Epic Style", "style epic", "style Kalau Gayat", or asks for a 9:16
  destination ad from a talking head and destination photos, even without naming it. Prefer it over Journey Map Hook
  unless they want the 3D terrain-map intro. Built with HyperFrames; renders the real MP4.
---

# Epic Style

The first build was the travel client **"Kalau Jenis Gayat"**: Mount Titlis, 77 s of talk plus a 9 s outro, 9:16. The
user approved it over three drafts. `template/` is that exact working build (`index.html`, `assets/js/anim.js`,
`captions.js`, fonts, wordmark). Treat it as a worked example and edit its data: scene list, captions, titles, map
points. Do not rewrite it from scratch. Commands and numbers are in `references/pipeline.md`; read it before building.

**Fresh every video.** The user does not want an brand video to look like the previous one ("benda yang kita pernah
buat jangan guna, nak fresh"). Keep the identity below. Give each new video at least one signature moment of its own
that fits its story, instead of copying the last one's. For Titlis these were the vertigo push on the bridge, the
360° Rotair turn, and the glacier chimes. Never reuse the old Journey Map Hook signatures unless the user asks:
3D terrain map, count-up altitude, PiP with an orange glow, slide-left.

## Locked identity

| Layer | Rule |
|---|---|
| Inputs | The **TouchUp** video: already cut and graded by the user, 9:16, presenter keyed onto a still. B-roll stills plus a montage of the destination. The soundtrack. The itinerary PDF. The team **outro** clip, which is iPhone HLG. The VO is the TouchUp's own audio. |
| Format | 1080×1920, 30 fps, SDR BT.709, rendered with `--sdr`. 9:16 first. |
| Two colour acts | **Destination act**: the destination's flag colours. For Switzerland, place titles are red `#b3121e` and hero words are white. **Brand act**: starts on the exact word "the brand's team" with a lift. Text is white with a deep-purple `#1d0050` stroke and a dark halo, and accents are lilac `#bba9ce`. brand orange is used **only** on the logo in the outro. Never mix the two acts. |
| Captions | Poppins 800, 2–4 words, at y ≈ 1500. White with a 9 px dark stroke (`#1b232b`) and a hard drop shadow. **Keywords are royal yellow `#fada5e` in both acts.** The user found red keywords unreadable. Leave out words that a big title is already showing, and fix Whisper spellings. |
| Place titles (front) | Noto Serif Display, condensed (`wdth` 62.5, `wght` 800), caps, 150–210 px, in the flag colour, with a soft shadow. An italic Poppins 700 kicker above it, plus a small flag chip on the first place title only. Lines rise out of a mask with a stagger. Sits at y ≈ 120–190, clear of the head. |
| Hero words (behind the head) | Poppins 800 white at ~200–250 px, letter-spacing −0.035em, with a soft dark glow. A Sacramento script (128 px, −7°) overlaps the top-left and writes on left→right. Placed so the cap overlaps only the bottom ~15% of the letters. Check that descenders (y, g, p) stay readable. Use these for the hook word, numbers (3,041 m, 360°), the message word, and the price. |
| Transitions | **Lift**: the incoming scene rises from below (yPercent 100→0, blur 14→0, 0.7 s `power3.inOut`). The outgoing scene drifts up 24% with blur 8 px. No dims, wipes or flashes. The outro also rises in. |
| Camera | Calm. Shot sizes 1.0 (wide), 1.1 (medium) and 1.2–1.28 (close, for punchlines). Every change is a `sine.inOut` glide of ≤ 1.2 s at a sentence start. Origin is near the face. Background drift is linear, at a fixed speed. |
| Presenter | A pixel-exact cut-out: an ML matte alphamerged with the source YUV, tagged BT.709. **Pushed down 76 px** so the script iPad at the bottom of the TouchUp never shows. Hold the last frame 0.9 s for the outro rise. Never tint, dim or re-grade it. |
| Vector map (A→B trail) | Built from the official boundary (swisstopo for Switzerland) and official lakes, with gazetteer-verified points, all checked to be inside the boundary. Sequence: the outline draws, the fill and lakes fade in, the camera zooms ~4.6× to the route, pin A pops, a red trail with a white casing draws through the real via-points, then the small mid pin and the big pin B pop. Labels are in ink or red on the white country. Place it on the line that names the place. |
| Itinerary page | The PDF is rendered at 5× and its bands are stacked into a strip. Paint over anything that contradicts the VO, such as "harga akan diumumkan". It runs **full frame** on an brand-purple gradient, tilted (`transformPerspective` 1900, rotX 20→11, rotY −14→−7, scale 1.3→1.42, origin at the left). It scrolls from the hero to the relevant day, where a lilac underline draws, then on to the last day. The presenter steps away underneath it, and the page lifts off upward to reveal the next scene. |
| CTA | Over real footage in the brand act: kicker "Pakej bersama the travel client", the destination in serif, the price as a hero word with the script "bermula", and the brand's website with a royal-yellow ".com". Then the outro. **Confirm the price with the user before it goes on screen.** |
| Outro | The team's clip, unchanged and full length. Convert HLG to SDR with **Apple `avconvert`**: the hand-made formula looked overexposed. The outro's own audio is levelled to the VO. No extra logo, because the outro already carries it. |
| Audio | VO at ~−16 LUFS, with no heavy processing; the TouchUp audio is already clean. The soundtrack is slowed to 0.75×, uses the quiet sections only (no drops), is low-passed at 3.8 kHz, and sits ~20 dB under the voice with sidechain ducking. Cross-fade to the next section on a scene change. Fade out into the outro. SFX are soft and synthesised: a lift whoosh, wind, cable hum, ice chimes and title pops, mixed at about −12 dB. |
| Footage | Never grade, scrim, vignette or dim. Blur is the only treatment. Montage shots are cover-cropped to 9:16 (~1.78× upscale), so keep them short. Prefer portrait or 3–4K stills. |

## Storyboard first (must)

Make storyboard frames with the `storyboard-frames` skill (`.claude/skills/storyboard-frames/`) before any MP4 render, draft or delivery:
1. Build the composition.
2. Snapshot one still per beat onto numbered sheets.
3. Let the student refine frame by frame.
4. Render only after they reply "ok storyboard".

Every render step in the workflow below comes after that approval.

## Workflow

1. **Probe and plan.** Probe everything: duration, HDR, loudness, L/R correlation. Transcribe with `npx hyperframes transcribe … --model small --language ms`. Contact-sheet the TouchUp, the stills and the montage, scene-detecting the montage. Flag wrong-place assets: a Matterhorn still in a Titlis story, a Dolomites shot in a Swiss montage, AI-made "location" photos. Send the user a beat table (time, VO, background, graphic) and the open questions: the price, missing assets, and anything in the itinerary that contradicts the VO.
2. **Prepare the project.** Copy `template/` to `work/<slug>-9x16/`, then run `scripts/prep_media.sh`:
   - `presenter`: the cut-out.
   - `outro`: the Apple tone map.
   - `clip`: montage shots.
   - `stills`: b-roll.
3. **Itinerary**: `swift scripts/pdf2png.swift itinerary.pdf work/itin 5`, then `scripts/itin_strip.py` with a segments file. Look at the preview and tell the user what you painted out.
4. **Map**: `scripts/geo_map.py fetch-ch`, then `gazetteer`, then `build`, then `inject`. Every point must print `inside=True`. For another country, use that country's official boundary and gazetteer. Never use hand-drawn outlines.
5. **Audio**: `scripts/make_sfx.sh`, set the VO gain so the VO measures −16 LUFS, then run `scripts/mix.py audio.json --check`. The median voice-over-music gap should be at least 20 dB.
6. **Composition**: edit the `SC` scene list, `CAM` poses, titles, map timing, itinerary scroll targets and outro time in `anim.js`. Edit the `.bk` layers and title markup in `index.html`, and the captions in `captions.js`.
7. **Check**: `npx hyperframes@0.8.149 lint`. Take snapshots at every title, the map, the itinerary and the CTA. Check that nothing overflows 1080 px, descenders stay readable, the brand-act text is readable over white and over bright sky, and no iPad shows at the bottom.
8. **Render**: `render --quality looks --fps 30 --sdr` for drafts. Verify with ffprobe (yuv420p, bt709) and ebur128 (≈ −16 LUFS). Crop a face from the render and compare it with the TouchUp. Send the draft, and do the delivery render only after the user approves it.
