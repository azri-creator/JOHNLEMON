# VGC Repo by Coach Am

This repo is a starter kit from Coach Am (Video Guna Code). Students drop their footage or voice-over into `input/`, name a style, and Claude builds and renders a finished MP4 with HyperFrames. Every style is a skill in `.claude/skills/`, and every style renders with HyperFrames (HTML + GSAP, rendered to MP4).

Talk to the student in Bahasa Melayu (casual, like Coach Am) unless they write in English.

## Style menu

### Footage Sendiri (talking-head footage of the student)
| Skill | Say | Look |
|---|---|---|
| `native-viral-styles` | "Native Viral" | A Claude Code chip types a command, then the effect happens. Two-tier top captions, cut-out words behind the head |
| `astra-styles` | "Astra Style" | Magenta two-tone type that blurs in, rack focus, dark-stage UI scenes |
| `glow-keyword-style` | "Glow Keyword" | White italic keywords, blue highlight box, neon script with glow, RGB split |
| `pip-explainer-style` | "PiP Explainer" | Presenter swaps between a close-up and a small PiP card, with diagrams above |
| `storyteller-edu-style` | "Storyteller Edu" | Calm storyteller rhythm: chapter cards, white line diagrams, 3D tilt screens |
| `journey-map-hook` | "Journey Map Hook" | Travel ad that opens on a cinematic 3D terrain map, then real footage behind a cut-out |
| `epic-style` | "Epic Style" | 9:16 travel ad: flag-colour act then brand act, lift transitions, map trail, 3D itinerary |
| `travel-style` | "Travel Style" | 9:16 travel lifestyle / holiday package: navy + gold, cleaned phone takes, flight-map trail |

### Motion Ad (100 % motion: voice-over, plus at most a few photos)
| Skill | Say | Look |
|---|---|---|
| `clean-launch-motion` | "Clean Launch" | Near-white premium launch look, blue gradient headlines, phone mockups |
| `konstruktivis-paper-cut` | "Konstruktivis" | Red / black / cream paper-cut with no hard cuts. Each scene zooms through a shape |
| `sketch-whiteboard-style` | "Sketch Whiteboard" | Hand-drawn whiteboard: a blue pencil draws in sync with the voice |
| `break-pattern-story-style` | "Break Pattern" | Cut-out photos of the student change pose per beat, beside neo-paper cards (mustard / navy) |

If the student doesn't know which style to pick, ask what they have (footage or only a voice-over), the platform (9:16 or 16:9) and the mood. Then suggest two styles from the matching category.

### Scripts and marketing: `vgc-master-knowledge`
Whenever a student asks for a script, hook, copy, CTA, brief, plan or review, first read `.claude/skills/vgc-master-knowledge/` and use Coach Am's formulas: **HKA** (~8 s), **HIKA** (~20 s) and **SEEIUWTOA** (~40 s), with the exact definitions in the knowledge file. Never invent testimonials, prices or offers. Every video plan starts from an approved script.

### Helper skills (engine, not styles)
- `hyperframes`, `hyperframes-core`, `hyperframes-animation`, `hyperframes-audio`, `hyperframes-cli`, `hyperframes-creative`, `hyperframes-keyframes`, `hyperframes-registry`, `hyperframes-studio`, `media-use`, `general-video` and `faceless-explainer` are the HyperFrames engine. Read `hyperframes` first whenever you build or render.
- `storyboard-frames` turns the built composition into numbered storyboard sheets for review. Every style goes through it before rendering.
- `elevenlabs-voiceover` makes a voice-over from a script. It uses the student's own ElevenLabs key.

## How every job runs
1. **Look at the inputs** in `input/`: duration, resolution, HDR or SDR, and whether there is a song, a logo or a brand kit.
2. **Read the chosen style's SKILL.md and its `references/pipeline.md`** before planning.
3. **Plan first.** Transcribe, then show a short beat table (time | words | visual) and the list of assets needed. Wait for "ok" before building.
4. **Build in `work/<project-name>/`.** Copy the style's `template/` there and edit its data. Never write the template from scratch.
5. **Check.** `npx hyperframes check` must show 0 errors.
6. **Storyboard frames (must).**
   1. Follow `.claude/skills/storyboard-frames/`. Snapshot one still per beat onto numbered sheets, check them yourself, and send them to the student.
   2. Refine frame by frame. Re-snapshot only the frames that changed.
   3. Don't render any MP4 until the student replies "ok storyboard". The only exception is a student who says to skip it.
7. **Render** to `output/<project-name>_<9x16|16x9>.mp4`.
   1. Copy the approved sheet next to the video as `output/<project-name>_storyboard.jpg`.
   2. Verify the video with ffprobe and confirm loudness is about −14 LUFS.

## House rules (from Coach Am's builds)
- **The student's brand only.** Every style was first built for a real brand. The templates ship with neutral placeholders ("LOGO", "Nama Brand", "namabrand.com"); swap in the student's own logo, colours, CTA and handle. Never use another company's logo or name.
- **Footage grade is untouched.** Change only the colours of captions and graphics. Never put a coloured overlay on the face.
- **Sync to the voice energy.** Whisper word times drift 0.2–0.3 s, so snap cuts and captions to the dips in the audio envelope.
- **Voice on top.** Keep the song low and slow, about 18–22 dB under the voice, ducked under speech. Use soft SFX with variety, not swoosh after swoosh.
- **Tight pace.** Squeeze long silences to about 0.2 s, and never cut inside a word.
- **Fresh every video.** Don't reuse the last video's signature effect. Keep the style's identity, but invent new metaphors.
- **Privacy.** Blur API keys, account IDs, card numbers and personal names in screen recordings before rendering.
- Never commit videos, audio or `work/` to git; `.gitignore` already excludes them.

## Environment
- Run `bash setup.sh` once. It installs Node, ffmpeg, the Python packages and the HyperFrames render browser.
- Use a Python that has numpy, scipy, Pillow, opencv and pypdf. On macOS that is often `/usr/bin/python3`, not Homebrew's.
- `npx hyperframes doctor` diagnoses a broken setup.
- If plain `npx hyperframes` fails with ETARGET (a fresh release not yet served), pin a known-good version, for example `npx hyperframes@0.8.212 …`. The ported skills already pin one.
