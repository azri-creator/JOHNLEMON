---
name: astra-styles
description: >-
  "Astra Styles" — the user's locked style for talking-head explainer/ad videos built in the "Astra" look: one hot
  magenta→red accent on a near-black plum stage, two-tone type (white setup line, magenta punch line) that blurs in and
  out, a big hero word BEHIND the presenter's head (cutout matte), dark "stage" UI scenes with a Claude-style prompt bar
  and a virtual camera that follows the caret, floating perspective cards with 2D rack focus (blur + dim the rest),
  real screenshots with a pink ring, glass pills, sparkle CTA. Camera is alive (face-pivot pushes, snap punch-ins). Optional "merapu" chaos beat (tacky stickers) that freezes, desaturates and blurs away when the
  presenter says stop. Built in HyperFrames, one script renders 16:9 and 9:16. Use whenever the user says "Astra Style",
  "Astra Styles", "style Astra", "style Merapu", "macam video Merapu / AI Edit Merapu tu", or asks for a magenta/pink
  two-tone, blur-in, rack-focus, dark-stage-UI explainer, even without naming it. Renders the real MP4.
---

# Astra Styles

First built for VGC **"AI Edit Merapu"** (Oct 2026, 45.3 s, 16:9 first then 9:16), after the user's reference
a reference video (a long-form explainer: plum-black UI stages, white + hot-pink two-tone
type, a magenta hero word behind the head, glass cards, callout diagrams, blur transitions). The identity below is
locked. The script, beats, assets and which modules appear change per video. Numbers and code recipes are in
`references/pipeline.md`; the module catalogue is in `references/modules.md`. Read both before building. A working
example lives in `template/` (the exact Merapu build script + audio generator + fonts).

## Locked identity

| Layer | Rule |
|---|---|
| Accent | **One** accent only: magenta→red gradient `linear-gradient(92deg,#FF3FA4 0%,#FF2D6F 45%,#FF2448 75%,#FF5A3A 100%)`, plus off-white `#F6F4F5`. Keep it even when the presenter wears red (user decision). Secondary pinks: caret/ring `#FF3D8E`, spark `#FF4FA0`. No other brand colours; the footage grade is untouched |
| Base | Near-black with a plum tint `#050304`. Scrims `rgba(10,5,8,…)`. Dark stage scenes add a deep-magenta edge vignette `rgba(92,8,36,.55)` |
| Type | **Two-tone blocks**: line 1 white (setup), line 2 gradient magenta (punch), Archivo (variable) weight 820, width 86 %, uppercase, tight leading .98. Hero word: Outfit 700, lower-case, gradient, huge. Labels: Archivo 700–800 uppercase tracking .12–.22 em. UI text: Inter |
| Motion | Everything **blurs in** (blur 18–24 px → 0, offset + scale .94–.96 → 1, 0.5 s `expo.out`) and **blurs out** (blur 16 px, scale 1.02, 0.3 s `power2.in`). Two-tone: line 2 lands 0.8–1.8 s after line 1. No bouncy overshoot except the deliberate chaos beat |
| Camera | Alive: slow `sine.inOut` pushes to 1.04–1.07 under talking, snap punch-ins (`back.out(3)` in 0.1 s to 1.2–1.36) on key words, always **pivoting on the face** (head track). In 16:9 the presenter slides to the right third while type sits on the left; in 9:16 the face drops low and type sits above |
| Hero word | One big word (e.g. "senang") **behind the head**: it lives under the person-matte layer, letters stagger in (0.045 s), a gradient sweeps across once, then it blurs out |
| Dark stage | The footage blurs away into a plum-black stage with a Claude-style prompt bar (typed text, pink caret, cursor arrow, send button), a **virtual camera** (scale/x/y keys) that follows the caret then the send button, then the stage blurs back. Use for "I tell the AI…" beats |
| Cards | Result videos/screenshots/thumbnails float as perspective cards (rotationY ±10–24°, `transformPerspective` 1500, slow bob). Some sit **behind** the person, some **in front**. **Rack focus**: when one card comes forward, the rest (`foot`, matte, back cards) go `blur(12px) brightness(.62)` for 0.5 s, then refocus |
| Proof | Real student screenshots/chats in white cards, names and avatars blurred, the key bubble ringed with a pink 4 px rim (`#FF3D8E`) at the spoken word. Never invent UI |
| Glass | Pills/CTA: `rgba(28,22,26,.42)` + blur 26 + saturate 1.2, border 1.5 px `rgba(255,90,160,.55)`, soft pink glow, pink 4-point spark icon |
| Chaos beat (optional) | When the script says the output is messy ("merapu"), stack tacky comic stickers (stroke 5 px black, hard drop shadow, rainbow/yellow/cyan/lime colours, emoji, a "SUBSCRIBE" button) with wobble and a 150 BPM bouncy loop. On the stop word ("kejap kejap kejap") it freezes, goes grayscale, blurs out, the camera resets and the calm bed returns. Skip this beat if the script has no "too much" moment |
| Audio | Voice untouched. Calm original bed (slow pads, 68 BPM) ≈ 21 dB under the voice, ducked under speech. One airy whoosh per blur-in, typing ticks, a click on send, soft ring blips, a sparkle on the CTA. Every SFX synthesised, none reused. Never louder than the voice |
| Formats | 16:9 1920×1080 first, then 9:16 1080×1920 from the **same** script (`FMT=16x9|9x16`), never a raw crop. 3:4 / 4:3 only on request |

## Storyboard first (must)

Make storyboard frames with the `storyboard-frames` skill (`.claude/skills/storyboard-frames/`) before any MP4 render, draft or delivery:
1. Build the composition.
2. Snapshot one still per beat onto numbered sheets.
3. Let the student refine frame by frame.
4. Render only after they reply "ok storyboard".

Every render step in the workflow below comes after that approval.

## Workflow

1. **Analyse**: probe the footage, transcribe words with `scripts/transcribe_words.py` (text only; take sync from the
   voice-energy valleys), make face/hand grids with `scripts/grid_sheet.sh`. Present a beat table (time | words | module |
   SFX) and wait for approval. Ask at most 3 questions: assets for cards/screenshots, which formats, whether a chaos beat
   fits.
2. **Set up** a project dir with `scripts/`, `hf/`. `npx hyperframes init hf --non-interactive --example=blank
   --skill=general-video`; copy `template/scripts/*` to `scripts/`, `template/assets/fonts/*` to `hf/assets/fonts/`,
   footage to `hf/assets/src/main.mov`, result videos to `hf/assets/res/`, screenshots to `hf/assets/fb/`, thumbnails to
   `hf/assets/thumb/`.
3. **Matte** the presenter early: `npx hyperframes remove-background hf/assets/src/main.mov -o hf/build/matte.webm
   --quality best` (u2net_human_seg, cached locally, CoreML, about 3 min for 45 s of 1080p). Re-encode to
   `hf/assets/person.webm` (VP9 alpha, crf 26). Then `python3 scripts/headtrack.py hf/assets/person.webm
   hf/build/headtrack.json`. Check alpha stills at 4–5 times.
4. **Voice**: `ffmpeg -i hf/assets/src/main.mov -vn -ac 1 -ar 48000 hf/build/voice48.wav` (audio.py reads it).
5. **Edit the config blocks** in `scripts/build.py`: `CAM`, `CH` (chaos stickers), `TT` (two-tone blocks), `SCRIM_L/T`,
   prompts (`P1`, `P2`, `SUBS`), `CARDS`, `FB`/`RIM`, `TH`/`FAN`, `LY` (per-format layout), `UI` (virtual camera). The timeline
   section (`J` list) has beat times hard-coded for the Merapu script: re-time or delete the beats you do not use.
   Edit the event lists in `scripts/audio.py` to match.
6. `FMT=16x9 python3 scripts/build.py && python3 scripts/audio.py`, then `cd hf && npx hyperframes check` (fix every ✗),
   snapshot every beat, a draft render, check voice lag (0 ms) and loudness, then the delivery render
   (`npx hyperframes render --quality delivery --fps 30 --video-frame-format png`). For 9:16 copy `hf/assets` into `hf9/`
   and run `FMT=9x16 python3 scripts/build.py`.

## Known gotchas

- Light walls: white type needs a left (16:9) or top (9:16) scrim (`SCRIM_L/T`) or it vanishes.
- A blur-in and blur-out on the **same element must not overlap**, or the text sticks in the render even though
  snapshots look fine. The script hard-sets `opacity:0` just after each exit. Keep that.
- A `fromTo` placed later in a timeline renders its from-state at t=0 unless `immediateRender:false`.
- `hf9` needs its own copy of `hf/assets`.
- Emoji need `@font-face { font-family:"Apple Color Emoji"; src:local("Apple Color Emoji") }`.
- Variable fonts: Archivo uses `font-stretch` (62–125 %), so the woff2 must be declared with `font-stretch: 62% 125%`.
- `python3 -I` hides numpy/scipy; run `audio.py` with plain `python3`.
- Whisper mishears Malay slang and English tech words ("selamba", "arahan", "native"): list the doubtful words for the user.
- Blur names, avatars and phone numbers in screenshots before they go on screen; keep the content bubbles.
- Cloud-synced folders can go TCC-blocked mid-session ("Operation not permitted"): a full app restart fixes it. Copy sources to the
  scratchpad first.
- Do not carry another style's elements in (timelines, headlines, glitch) unless the user asks.
