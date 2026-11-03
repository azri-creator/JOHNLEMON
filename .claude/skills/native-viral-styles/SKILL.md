---
name: native-viral-styles
description: >-
  "Native Viral Styles" — the user's locked style for vertical 9:16 talking-head ads where the presenter commands the
  edit and it obeys: a Claude Code chip types each command, then the effect happens (AI zoom in/out HUD, keyframes
  deleted, power aura, 3D orbit of video cards behind and in front of the presenter, palm orb implode, lightning,
  slot reel, PiP takeover). Two-tier top captions: kicker with one #FFE600 keyword plus a big Anton headline on ~10
  key words, some behind the head (cutout). Camera always alive (pushes, punch-ins). Neutral palette, never
  hacker-green; no white flashes or fades; every SFX synthesized unique. Use whenever the user says "Native Viral
  Styles", "Native Viral", "style Control Zoom", "macam video zoom in zoom out tu", or asks for a viral/native 9:16
  talking-head ad with AI or Claude-interaction effects, cutout captions or "paling ekstrim" HyperFrames motion, even
  without naming the style. Renders the real MP4 with HyperFrames.
---

# Native Viral Styles

First built for VGC "Control Zoom In/Out" (Oct 2026, 45 s, 9:16). The identity below is locked; the script, beats,
assets and which effect modules appear change per video. Numbers, layer order and code recipes are in
`references/pipeline.md`; the effect modules are in `references/scenes.md`. Read both before building. A working
project lives at `template/` (build script, 11 scene modules, audio generator, Anton font).

## Locked identity

| Layer | Rule |
|---|---|
| Concept | Every effect is "asked for". Where the presenter says a command or describes a capability, a **Claude Code chip** (bottom, y≈1400) types a short BM command in JetBrains Mono, a coral cursor follows, a white status pill shows `✓ …`, then the effect happens on screen. Use it on the 2–4 strongest beats, not everywhere |
| Captions | **Top, two-tier.** Kicker: Inter 900 uppercase ~44 px, white, one keyword `#FFE600`. **Big headline only on ~8–10 key words** (Anton, white, soft shadow, no heavy glow), timed to the spoken word. Other lines are a small 2-line uppercase caption (40/52 px). Captions must follow the speaker's words verbatim |
| Cutout | Some big headlines sit **behind the head** (person matte layer above them). Place them high (top ≈58 px, ≤158 px) so the cap covers only the bottom of the letters, and hide the kicker when they appear. Headlines that land during a big zoom go in front (the face would cover them) |
| Camera | Alive all the time: slow pushes (1.0→1.06–1.15) under build-up lines, snap punch-ins (+0.08–0.2 in 0.08–0.12 s) on keywords, zoom-out punches on "release" words, shake (≤18 px) on impacts. Pivot on the face. Never sit static >2 s |
| Palette | **Not hacker green.** Neutral base: white type, dark frosted glass (`rgba(9,13,18,.68)` + blur 24). Accents: coral `#D97757` (Claude spark/cursor), yellow `#FFE600` (keywords, clocks), blue-white `#6FB1FF` (aura, orb, lightning, rings), red `#FF4D4D` only for ✕/strikes. Brand lime only on the logo and CTA button. Footage grade untouched |
| No fades | The first frame is clean footage: no white flash, no fade-in, no "wake" zoom. No full-screen white/colour flashes anywhere; impacts use shake, rings and particles instead |
| Effects | Pick modules from `references/scenes.md` to match what is said (zoom HUD, keyframe panel, clock, power aura, 3D orbit + palm orb implode, super-power lightning, icon cards, slot reel, motion takeover + PiP, vignette push, CTA with confetti). Any card/panel lives mid or low (y 860–1300), away from the top captions and the face |
| Audio | Voice untouched (−16 to −18 LUFS integrated, TP ≤ −1.5). Supplied music: slowed 0.75×, low-pass 3.8 kHz, ~20–22 dB under the voice, sidechain duck, **drops out on the punchline** and returns for the CTA. SFX: one designed sound per event, every instance synthesized with its own seed/params, **no sample reused** |
| Deliverable | 9:16 1080×1920 30 fps first (`render -q delivery`), then 3:4 / 16:9 re-layouts on request (never a raw crop) |

## Storyboard first (must)

Make storyboard frames with the `storyboard-frames` skill (`.claude/skills/storyboard-frames/`) before any MP4 render, draft or delivery:
1. Build the composition.
2. Snapshot one still per beat onto numbered sheets.
3. Let the student refine frame by frame.
4. Render only after they reply "ok storyboard".

Every render step in the workflow below comes after that approval.

## Workflow

1. **Analyse**: probe the footage (fps, LUFS, jump cuts), transcribe with `scripts/transcribe_words.py` (large-v3), and make face/hand grids with `scripts/grid_sheet.sh`. Present a beat-by-beat plan table (time | words | visual | technique | SFX) and wait for approval. Ask at most 3 questions (assets for orbit/takeover, output formats, any rhetorical beat to keep plain).
2. **Set up**: `npx hyperframes init <dir>/hf --non-interactive --example=blank --skill=general-video`, copy `template/scripts` → `<dir>/scripts`, copy footage and assets into `hf/assets/`, and copy `template/assets/fonts/anton-400.woff2` → `hf/assets/fonts/`.
3. **Matte** the presenter in the background as early as possible (`npx hyperframes remove-background main.mov -o build/matte.webm --quality best`; copy the weights from `~/.u2net/` if they're not cached), then re-encode to `hf/assets/person.webm` (VP9 alpha, crf 26). Check alpha stills at 4–5 times.
4. **Edit the config blocks** in `scripts/build.py`: `SC` (which scene modules, start, duration, in-camera or not), `PAIRS` (kicker / headline / times), `KEY` (which pairs get a big headline, `B` behind head or `F` front), `PROMPTS` (chip commands), `CAM` (camera keys), `SHAKES`. Edit the module HTML (coordinates, hand-track keys, words). Edit `EV` in `scripts/audio.py`.
5. Run `python3 scripts/build.py && python3 scripts/audio.py`, then `npx hyperframes check` (fix every ✗), snapshots at each beat, a draft render, and check voice lag (0 ms) and loudness. Then the delivery render, spot-check frames, and send the MP4.

## Known gotchas

- Sub-compositions are concatenated: `build.py` prefixes ids (`scene__id`) and scopes CSS. Dynamic ids built in JS (`"#x"+i`) are **not** rewritten, so keep element arrays instead of ids, or write the prefixed form (`"#keyf__x"+i`).
- A `fromTo` placed later in a timeline renders its from-state at t=0. Use `immediateRender:false` for elements that must be visible earlier.
- Never give an element both a CSS `transform` and a GSAP transform tween; `gsap.set` the initial rotate instead.
- The person matte layer above the headlines must be hidden while 3D orbit cards pass in front of the presenter.
- The top scrim must sit *below* the headline layers, or the headlines look grey.
- `hf-seek` time is global: analytic scenes (orbit, orb, particles) compute from `e.detail.time`.
- Anton needs a local `@font-face`, or `check` fails. Whisper drifts 0.2–0.3 s and mishears slang ("selamba" → "selama"), so flag doubtful words to the user.
