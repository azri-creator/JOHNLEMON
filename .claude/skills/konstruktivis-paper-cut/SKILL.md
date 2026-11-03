---
name: konstruktivis-paper-cut
description: >-
  "Konstruktivis Paper-Cut": the user's locked style for faceless 100 % motion videos on a voice-over (first built
  for VGC "Boleh Buat Motion", Oct 2026). Constructivist paper-cut look: red #c3191f, ink #171412 and cream
  #ece2c9 only, flat SVG figures, sunburst rays and diagonal bands with paper grain. Zero hard cuts: each scene
  zooms through a shared shape into the next. One-word Montserrat 900 captions at 58 % height, a hero "machine"
  beat, a red-flood end card, the song drop aligned to a reveal. 9:16. Use whenever the user says
  "Konstruktivis", "Konstruktivis Paper-Cut", "style paper-cut merah hitam", "style Boleh Buat Motion",
  "macam video Boleh Buat Motion tu", or asks for a faceless red/black/cream constructivist motion video,
  even without naming it. Built with HyperFrames; renders the real MP4.
---

# Konstruktivis Paper-Cut

First built for VGC **"Boleh Buat Motion"** (22 Oct 2026): a 57 s, 9:16, faceless motion video on the user's own VO, with 13 scenes and no cuts. The look copies the DNA of a Facebook reference (video 28374302292250233). Only the behaviour was taken; no footage or branding.

What changes per video and what stays locked:
- **Per video:** the VO, the scene chain (one visual metaphor per spoken idea) and the CTA text.
- **Locked:** the identity below.

Where everything else lives:
- `references/pipeline.md`: the scene catalogue with handoffs, the numbers, the audio recipe and the variants. Read it before building.
- `template/`: the exact working build, recovered and re-verified frame-for-frame against the final. It has `scripts/index.tpl.html` (root, S1, captions, end card), `scripts/scenes/*.js` (S2–S13), `build.py`, `words.py`, `make_audio.py`, `make_grain.py` and `transcribe.py`. It is a worked example, so rewrite the scene blocks for the new script rather than starting from scratch.

## Locked identity

| Layer | Rule |
|---|---|
| Palette | Only `--red #c3191f`, `--red2 #8f1217`, `--blk #171412`, `--cr #ece2c9` and `--cr2 #d6c8a6`. No gradients, no other hues. White appears only in the captions |
| Texture | `assets/grain.png` (from `make_grain.py`) over everything, multiply at 20 % plus screen at 7 % |
| Shapes | Flat SVG only. Use the helpers: `fig()` (a geometric figure with its origin at the feet and the head at y −262; arms down or `"hold"`), `rays()` (sunburst wedges), `phone()` (a black hand silhouette holding a phone from the lower right) and `thumb()`. Use big diagonal bands, circles, triangles and a shadow ellipse under figures. No outlines thinner than 10 px |
| Continuity | **Zero hard cuts.** Each scene ends by zooming (`#zN` scale 15–26, `power3.in`, 0.45–0.8 s) into a shape that becomes the first shape of the next scene. Examples: camera lens → mic → disc → red dot → teacher's head → card → lecture hall → door → book → page lines → stairs. When no shape fits, use a 0.3 s rotate + blur whip. Scenes overlap by about 0.05 s with `tl.set` opacity swaps |
| Camera | Every scene is alive. A `#cN` wrapper drifts (scale 1.1 → 1.0, rotation −2 → 1, sine) while the rays rotate slowly. No still frame longer than 0.5 s |
| Captions | One word at a time, uppercase. **Montserrat 900, 76 px**, white, `-webkit-text-stroke: 13px #0f0d0c` with `paint-order: stroke fill` and a hard shadow `0 8px 0`. Fixed box at **y 1050–1180 (58 %)**. Words come from Whisper and are snapped to envelope dips (`words.py`: ±0.05/+0.10 s clamp, minimum 0.13 s per word) |
| 3D beat | At most one. The lecture hall is a hand-drawn canvas projector driven by one clock tween's `onUpdate`, so it is seek-safe. No WebGL |
| Hero beat | A "machine" transformation: a hand drops a flat slide in, and a film frame comes out with the slide's shapes animated. Give every new video its own hero beat (see Break pattern below) |
| End card | A red flood (a circle from the last play button or tap point, scaled to cover the frame). Then "EDIT VIDEO / GUNA CODE" in Montserrat 900 at 118 px cream, plus a 40 px tracked line "TEKAN LINK SEKARANG" in ink |
| Audio | The voice is untouched apart from gain and a soft limiter. Use the user's song: align its drop to a mid-video reveal (here the song drop at 40.08 s lands on the door opening at 18.33 s, so the song ends on the CTA). The bed sits around −31 LUFS and ducks another 5 dB under speech. SFX are synthesised and soft: whooshes on handoffs, thocks on stamps, ticks. Mix to −14 LUFS, peak −1 dBFS |

## Storyboard first (must)

Make storyboard frames with the `storyboard-frames` skill (`.claude/skills/storyboard-frames/`) before any MP4 render, draft or delivery:
1. Build the composition.
2. Snapshot one still per beat onto numbered sheets.
3. Let the student refine frame by frame.
4. Render only after they reply "ok storyboard".

Every render step in the workflow below comes after that approval.

## Workflow

1. **Transcribe** the VO: `/usr/bin/python3 scripts/transcribe.py hf/assets/vo_src.wav scripts/words_raw.json`. Fix Whisper mis-hearings by hand (in the first build, "Ferry" was "sendiri", "prompt vote" was "Prompt Vault" and "CXPT" was "ChatGPT").
2. **Plan the chain.** Write a table: time | VO | visual | handoff shape. Each spoken idea gets one metaphor, and each scene's last shape must be the next scene's first. Show the plan before building if the user asks for it.
3. **Scaffold:**
   1. Run `npx hyperframes init hf --example blank --resolution portrait --non-interactive --skip-transcribe`.
   2. Copy `template/scripts` to `scripts/`.
   3. Run `make_grain.py`.
   4. Convert the VO to `hf/assets/vo_src.wav` and the song to `hf/assets/song_src.wav` (48 kHz stereo).
4. **Build:** run `words.py`, then `make_audio.py` (set `DUR` and `OFF` = song drop − visual reveal), then `build.py`. Edit `scripts/` only; `build.py` overwrites `hf/index.html`.
5. **Check:** run `npx hyperframes lint` and `check`. Snapshot every handoff (`snapshot --at …`) and look for empty frames between scenes, captions over a key shape and figures cut off.
6. **Render:** `npx hyperframes render --quality delivery --fps 30 -o ../<Name>_9x16.mp4`. Then verify with `ffprobe`, check `ebur128` ≈ −14 LUFS, and count scene changes (`select='gt(scene,0.35)'`). A zoom-through should register as at most one or two.

## Break pattern (must)

The audience sees every VGC ad. Do **not** reuse the previous video's hero beat (slide → film machine), the lecture-hall canvas or the stairs-hop as-is. Keep the identity, but invent new metaphors and a new hero transformation for every script. See the `feedback-break-pattern-across-videos` memory.

## Known gotchas

- GSAP `x`/`y` on an SVG `<g>` that already has `transform="translate(…)"` **replaces** that translate. Wrap the element (`<g id="s1figw">${fig(...)}</g>`) and animate the wrapper.
- For a second `fromTo` on the same property, use `immediateRender: false`. Hide late elements with `tl.set` at their start rather than leaving them at opacity 0 in the markup.
- When rings or strokes fade in, split the scale and opacity tweens. Combining keyframed opacity with scale made the rings flash.
- Run Python with `/usr/bin/python3` (it has numpy, PIL and scipy). Homebrew `python3` lacks them.
- The builder cannot hear the mix. Ask the user to listen once on a phone, especially at the song drop.
