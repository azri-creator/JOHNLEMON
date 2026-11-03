---
name: clean-launch-motion
description: >-
  "Clean Launch Motion" (formerly "Google-Inspired Motion"): the locked clean product-launch motion style for vertical
  9:16 ads and explainers. Cool near-white stage (#FAF6FE), blue-gradient Inter headlines that blur in word by word
  and re-centre, dark-bezel phone mockups in steep perspective cropped by the frame, tilted floating cards, a camera
  that never sits still (drift and step-zooms), 0.3 s zoom-through transitions, ring-to-check moments, a sparkle
  finale with a calm end card, and a smooth line-by-line ElevenLabs VO (the student's own voice) over an original
  synthesised bed. Built on Coach Am's "Belajar AI" ad. Use whenever the user says "Clean Launch Motion",
  "clean launch", "Google-Inspired Motion", "style Google", "motion macam iklan Belajar AI", "motion putih-biru
  clean", or asks for a light, premium, Apple/Google-launch-style motion ad or explainer, even without naming it.
  Built with HyperFrames; renders the real MP4.
---

# Clean Launch Motion

First shipped as Coach Am's **"Belajar AI"** ad (27 Sep 2026, 46 s, 9:16), approved after two rounds ("aku suka motion ni"). It was built in Remotion and ported to HyperFrames in Oct 2026. The port was checked frame by frame against the approved final (see `references/pipeline.md`, "Verified port").

The look is calm Google/Apple product-launch polish: light surfaces, blue gradients, soft depth, confident motion. It uses **no** Google branding, logos, trademark colours or product UI. Never put a Google, LangEase or Zelios mark in a video. Use the student's own brand, logo, CTA and claims.

What changes per video and what stays locked:
- **Per video:** the scene list and beats, which devices to use, metaphors, what the phone and cards show, headline wording, CTA layout details, music tempo (about 120–128 BPM) and cue SFX, number of scenes, runtime.
- **Locked:** the identity below. Every video should feel like the same family without looking like a re-skin of Belajar AI.

Where everything else lives:
- `references/pipeline.md`: project layout, timing model, every `lib.js` helper, scene-code rules, commands, audio recipe and delivery. Read it before building.
- `references/style_spec.md`: exact numbers (palette, type sizes, surfaces, phone geometry, eases, durations, audio levels).
- `references/motion_vocabulary.md`: the menu of 21 devices, with when to use each and which helper builds it.
- `references/lessons_and_qc.md`: the user's feedback history, failure modes already hit, honesty rules and the QC checklist. Read it before the first render.
- `references/reference_breakdown.md`: the analysed LangEase/Zelios launch reference, the benchmark for pace and feel.
- `template/`: a working HyperFrames build.
  - `plan.json` and `vo/vo_script_locked.txt` hold a placeholder script.
  - `scripts/` has `index.tpl.html`, `lib.js` (the locked helpers), `scenes/` (starter hook / phone / cards / check / cta, one file each), `build.py`, `rough_timing.py`, `tts_lines.py`, `build_vo.py`, `make_audio.py`, `verify.py`, `qc_sheet.py` and `common.py`.

## Locked identity

| Layer | Rule |
|---|---|
| Stage | `#FAF6FE` in every scene, with two very faint drifting glows (`rgba(124,192,249,.16)` top-left, `rgba(183,166,248,.12)` bottom-right). Never a dark charcoal stage, neon, yellow/black stomp type or busy collage. Real screenshots keep their own UI; the stage stays light |
| Palette | Ink `#24243A`, soft ink `#5B5B72`. The blue gradient (90°) `#2B7CF5 → #4898F8 → #7CC0F9` goes on emphasis words, buttons, progress and the sparkle. Royal `#0048E0` is rare. Cyan `#00A9EB` and indigo `#4858F8` are small accents; pink `#F3A8D8` and lilac `#B7A6F8` appear only in confetti |
| Type | **Inter** 500 for headlines (84–104 px, hook up to ~124, tagline 64), 600–700 for chips and buttons, tracking −0.025 em. Emphasis comes from colour on 1–2 words, never bold or italic. Phrases are 1–5 words, centred, and change with the VO. Lines auto-fit to 880 px |
| Headline motion | Words arrive one by one on their spoken word. The slot opens first (0.32 s, from −0.1 s), so the line **re-centres**. Then the glyphs **blur in** (+0.06 s, 0.4 s: blur 12 → 0, rise 26 px, scale 1.08 → 1). The exit is blur 16 + scale 1.05 + fade over 0.26 s. Phrases accumulate across sentences |
| Surfaces | White cards (radius 26–36) with soft or deep blue-grey shadows. Pill chips (blue tint, white, or ink "CONTOH"). The button is a 740×136 gradient pill with the user's exact label. Highlights are a 5 px blueDeep stroke that draws on, with a glow and an 8 % fill |
| Phone | Dark bezel (width × 0.028, gradient `#2a2d36 → #0d0f14`), height = width × 2.13, radius = width × 0.14, dynamic-island pill. Steep perspective (2400; rotateX 22°, rotateY 9°, rotateZ −8°) with its bottom **cropped by the frame**. It rises from below in 0.7 s with speed blur and floats gently |
| Cards | 2–4 **tilted floating cards** fly in from different edges (backOut, ±6–7°, speed blur, float) around a centred phrase, one per spoken item. They can gather into a board |
| Camera | Never sits still. A slow push of +2–5 % per scene, a roll drift of ±0.3–0.8°, and **+3 % step zooms** (0.35 s) on the 2–3 strongest words. Pans across an image land on each detail as it is named (0.4–0.5 s, scale 1.2–1.4). Speed blur = travel × 0.09, capped at 14 |
| Transitions | A **zoom-through** at every cut. The incoming scene settles from 0.9 with blur 14 over 0.34 s. The outgoing scene pushes to 1.22 with blur 18 and fades over its last 0.3 s (0.1 s overlap). Cuts fall 0.18 s before the scene's first word, with a whoosh on each. In-scene match moves count as beats |
| Beats | **Ring → check → confetti** for "done / okay" (ring 0.5 s, check 0.25 s, about 20 restrained pieces), always editorial, never a guarantee. A circle can morph into a phone. A cursor taps (press 0.88, ripple) on real UI |
| Pace | A visible change every ~1–1.5 s, scenes of 4.5–7 s, and never a static frame over ~1.5 s except the end card |
| Finale | A four-point blue **sparkle** flies a curve with a dotted trail (0.7 s) onto the logo's top-right corner and twinkles. Then logo → tagline (user's words) → gradient button (user's label) → cursor tap on "klik…". The card is complete ~0.5 s after "klik" and holds **3.5 s** with a slow 1 → 1.02 push. No URL text unless the user asks |
| Voice | ElevenLabs `eleven_multilingual_v2`, `ms`, **line by line** with previous/next context, 2 seeds, auto-picked for smoothness. Never cut inside a take. the student's own ElevenLabs voice (set `voice.id` in `plan.json`). Gaps are 0.30 / 0.26 / 0.45 s. Clarity chain, −16 LUFS. The student's own key and voice; never swap a voice silently |
| Music + mix | An **original synthesised** bed in D major (I–V–vi–IV), first cut on a beat, no drums in the intro, a one-bar drum drop at the CTA, resolving under the end card. About 12 dB under the VO, ducked a further 6 dB. Soft cue SFX: whoosh, pop, tick, tap, chime, riser, shimmer. Master −14 LUFS / −1.5 dBTP |
| Honesty | Real material where possible. Label anything staged ("CONTOH", "Paparan contoh"). No invented results, counts, testimonials, prices or guarantees. No private links. Flag third-party marks in screenshots |

## Storyboard first (must)

Make storyboard frames with the `storyboard-frames` skill (`.claude/skills/storyboard-frames/`) before any MP4 render, draft or delivery:
1. Build the composition.
2. Snapshot one still per beat onto numbered sheets.
3. Let the student refine frame by frame.
4. Render only after they reply "ok storyboard".

Every render step in the workflow below comes after that approval.

## Workflow

1. **Brief and inputs.**
   - Get the locked script and keep the user's wording verbatim; line breaks are delivery cues.
   - Choose the voice. Use the student's own ElevenLabs voice (`voice.id` in `plan.json`); there is no shared default.
   - List the real assets: screenshots, product images, demo videos, logo.
   - Establish what must or must not appear: price, URLs, private links, claims.
   - If a reference video is given, inspect it properly (skip pre-roll, sample frames and colours; see `reference_breakdown.md`).
2. **Project.**
   1. Copy `template/` to `work/<Name>/`.
   2. Run `npx hyperframes init hf --example blank --resolution portrait --non-interactive --skip-transcribe` inside it.
   3. Put assets in `hf/assets/img/` and `hf/assets/video/`.
   4. Fill in `plan.json`: `name`, `scenes`, one `line_scene` entry per script line, voice, gaps, `sfx`.
3. **Plan the beats before building.**
   - Run `/usr/bin/python3 scripts/rough_timing.py`.
   - For each scene, write a beat list in which every VO phrase triggers a visible change. Pick devices from `motion_vocabulary.md`.
   - Show the plan in 3–5 lines (BM) and wait for "ok" unless the user said to just go.
4. **Build scenes.**
   - Use one `scripts/scenes/NN_<key>.html` per plan scene. Edit the starters; don't write from scratch.
   - Anchor every cue to words (`sw()`, `ws()`, `data-at`), never to seconds, so a new VO take re-flows everything.
   - Run `/usr/bin/python3 scripts/build.py`, then `npx hyperframes check hf` (0 errors), and snapshot as you go.
5. **VO.**
   - `/usr/bin/python3 scripts/tts_lines.py` costs credits (about characters × seeds). Confirm before long scripts.
   - `/usr/bin/python3 scripts/build_vo.py` must print `text==script: True`.
   - You cannot listen. Say so, and ask the user to listen.
6. **Audio.** Add cue SFX to `plan.sfx`, run `/usr/bin/python3 scripts/make_audio.py`, then rerun `build.py` so the `<audio id="mix">` is included.
7. **QC loop.** Snapshot the whole ad every 1–1.5 s, every cut ±0.3 s and every headline mid-entrance. For a look check against an approved video, use `qc_sheet.py --ref`. Fix, rebuild, re-check.
8. **Render and verify.**
   - `npx hyperframes render hf --quality draft` for a quick look, then `--quality delivery --fps 30 -o output/<Name>_9x16.mp4`.
   - Run `/usr/bin/python3 scripts/verify.py <mp4>`. Targets: 1080×1920, 30 fps, H.264 + AAC 48 k, −14 LUFS, VO lag 0 ms.
   - Check that every on-screen word is spelled right, every headline is inside the frame under zoom, and the CTA appears only at the end.
   - Report the checks not performed: listening, the in-app preview and licence confirmations.

## Known gotchas

- **3D planes:** never use a `transform-style: preserve-3d` stage (videos inside it render black). Each plane gets its own `transformPerspective` through `poseTo()`. Pass `vp` = frame centre − plane centre, or the phone sits lower and flatter than designed. GSAP applies `rotate rotateY rotateX`; `tilt()` converts the CSS-order angles.
- A tilted plane that keeps any `filter` (even `blur(0px)`) after its blur-in renders soft. The helpers set `filter: none` afterwards; do the same in custom tweens.
- When two `fromTo` tweens touch the same property, the second needs `immediateRender: false`. Use one wrapper per concern (rise > float > tilt).
- `curve(..., {ir: true})` holds `fn(0)` before it starts. Without it, the property keeps its CSS value until the curve begins.
- The scene-out fade must reach 0 inside its own tween at `b + 0.1`. A zero-length `tl.set` at the same moment loses to a still-running fade, and the old scene ghosts through.
- Fonts: Inter is bundled (no `@font-face`) and is loaded before scripts run, so `headline()` measures synchronously. Don't build the timeline inside `document.fonts.ready`, or the first frame renders blank.
- Every `<video>` needs an id, and no ancestor may carry `data-start`. Root-level clips anchor at 0,0, so position them with GSAP x/y. Never `play()`, `pause()` or seek media.
- Mark intentional overlaps (a card over the phone) with `data-layout-allow-overlap` and intentional crops (the phone's bottom) with `data-layout-allow-overflow`, or `check` fails. `composition_file_too_large`, `first_frame_empty` and contrast on the light end of the gradient button are expected warnings.
- `glob` on paths with `[VGC]` treats the brackets as a pattern; `build.py` escapes it. Keep that in mind in your own scripts.
- If `npx hyperframes` fails with `ETARGET` (an unpublished latest), pin a version: `npx hyperframes@<version> …`.
- Run Python with `/usr/bin/python3` (it has numpy, scipy and PIL). Homebrew `python3` lacks them.
- ElevenLabs: the key is the student's own (env `ELEVENLABS_API_KEY` or the Keychain entry from `python3 .claude/skills/elevenlabs-voiceover/scripts/voiceover.py setup`). Never ask for it in chat, print it or write it to a file. `tts_lines.py` refuses a voice whose name doesn't match `plan.voice.name_prefix`.

## Communication

The user writes casual Malaysian BM ("aku/korang"); reply in BM. On-screen copy uses BM santai with the user's exact terms (simple, scene, okay, proceed, step, group…). When the user changes on-screen copy, apply it exactly as typed.
