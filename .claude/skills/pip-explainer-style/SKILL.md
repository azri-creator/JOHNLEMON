---
name: pip-explainer-style
description: >-
  "PiP Explainer Style": the locked editing style for vertical 9:16 talking-head explainers (first built for the
  client "Bisnes Baru Nak AI" reel). The presenter alternates between a full close-up (1.2x crop, snap punch-ins, slam
  words) and a small rounded picture-in-picture card at the bottom, while animated diagrams, cards, UI mocks and
  kinetic type above it explain what is said. Navy dot-grid, brand cyan/blue structure, yellow emphasis, bold sans
  titles with a serif-italic accent, 1-3-word BM captions, punchy cold open, original synth beat and restrained SFX.
  Use it whenever the user says "PiP Explainer", "style Bisnes Baru", "style IG Viral", "macam video bisnes baru
  tu", or asks to edit a talking-head video with motion graphics or a presenter-in-box explainer look, even without
  naming it. Built with HyperFrames; renders the real MP4.
---

# PiP Explainer Style

A saved house style, used as a series. The **identity** (layout system, palette, type, caption rules, motion grammar,
mix) stays the same. **What the graphics show is chosen fresh from what the presenter says** in each video, so two
videos never look like copies. First built in Remotion (Sep 2026), ported to HyperFrames (Oct 2026) with the same look.

Where everything lives:
- `references/style_spec.md`: the identity with every number. Read it first.
- `references/scene_playbook.md`: edit brief, scene menu, honesty rules, video log. Read it before planning.
- `references/pipeline.md`: project layout, layer order, the FULL↔PiP morph numbers, Remotion→GSAP mapping, commands, checks.
- `template/`: the working build (worked example = Bisnes Baru). Copy it; edit `timing.py`, `captions.py`,
  `scenes.py` and the cue lists. `build.py` writes `hf/index.html`; never hand-edit that file.

## Locked identity

| Layer | Rule |
|---|---|
| Layouts | Only two. **FULL**: close-up, 1.2× crop (origin 540, 1500), snap punch-ins pivoting on the face, +3.5 % push per stint, slam word. **PIP**: presenter ×0.6 in a rounded card (x 30, y 1372, 1020×508, r 40, cyan hairline + glow), wall-colour fill, feathered edges; graphics above |
| Switch | **One continuous presenter video** that morphs its frame and transform (0.34 s / 0.24 s expo.out). No crossfades, no second copy. Switch on meaning (question, punchline, new idea), every 2–6 s |
| Panel camera | Each PiP scene pushes in 1.14× + blur 14 → 1.0 sharp in 0.42 s, drifts +3.5 %, snaps out in 0.1 s |
| Palette | Navy `#061329` + drifting cyan dot grid (34 px) + blue glow. Cyan `#00CFF5` / blue `#087BEE` = structure. Yellow `#FFE600` = emphasis only (navy text on yellow boxes). No red |
| Type | Inter 800 titles (58–66 px, y≈205) with ONE serif-italic accent word in yellow (Instrument Serif if the woff2 is present, else Playfair Display). Archivo Black for slams and big numbers, auto-fit ≤ 960 px |
| Captions | BM, 1–3 words (≤ 16 chars), unspoken words at 35 %, keywords yellow, pop 0.86→1. y 1210 FULL / 1296 PiP. Standard spelling; unclear words get "…", never a guess |
| Cold open | Frame 0: flash, 1.22→1 snap punch, shake, impact, beat running, headline slam; question teaser on the next key noun; first PiP scene on the key noun with a 0.3 s counter; music drop on the hook keyword |
| Accents | Screen flashes (0.2–0.55) and 8–14 px shakes only on the big hits |
| End card | 0.1 s after the last word, ≥ 2 s: 2-line takeaway (white Archivo + yellow box) and the brand's logo row |
| Footage | Original colour, tone-curve face lift only, BT.709; HDR is tone-mapped and rendered `--sdr` |
| Audio | Presenter's own voice (cleaned, latency-compensated). Original synth bed (default 140 BPM half-time, drop on the hook, beat-stop before the punchline). Restrained synth SFX, one per visual event. Music −8 dB ducked, SFX ×0.32, master −14 LUFS / −1.5 dBTP |

## The user's standing rules
- **Don't cut or trim the footage.** It arrives already edited: EDL = one segment, even if a pasted brief lists cut timecodes. Only cut when the user asks in chat.
- **The first ~10 s must be punchy** (see Cold open).
- Keep the presenter's **original colour**; never tint the face.
- Earlier projects' assets may be reused as B-roll when relevant; label them honestly.
- Use the student's own brand (logo, colours, CTA), never client's or VGC's.
- Reply in casual Malaysian BM ("aku/kau/bro").

## Storyboard first (must)

Make storyboard frames with the `storyboard-frames` skill (`.claude/skills/storyboard-frames/`) before any MP4 render, draft or delivery:
1. Build the composition.
2. Snapshot one still per beat onto numbered sheets.
3. Let the student refine frame by frame.
4. Render only after they reply "ok storyboard".

Every render step in the workflow below comes after that approval.

## Workflow
1. **Analyse.** Probe the footage (`ffmpeg -i`: fps, HDR or SDR). Make a contact sheet (`fps=0.5,tile`). Transcribe
   word-level (`scripts/transcribe.py`, `ASR_PROMPT` = key terms). Re-transcribe unclear bits; if still unclear, don't caption a guess.
2. **Set up.** Copy `template/` to `work/<project>/`. `export SRC_MOV=<footage> SRC_DUR=<duration>` (and `BROLL_DIR`,
   `LOGO_ICON`, `LOGO_TEXT`). Run `/usr/bin/python3 scripts/edl.py`, which writes `data/edl.json`.
3. **Plan.** Write the edit brief (playbook §1): beat map → FULL/PIP per beat → one scene per idea → slams. Read the
   video log. Show the plan (time | words | layout | visual | SFX) and wait for "ok".
4. **Build.**
   - `timing.py`: anchors (source seconds, refined on the voice envelope), `LAYOUT`, `PANEL_CUTS`, `PUNCH`, `SHAKES`, `FLASHES`.
   - `captions.py`: `FIX` / `JOIN` / `KEY` for this video.
   - `scenes.py`: new scene functions from kit pieces; list them in `panels()`; slams in `full_overlays()`; `END_LINE1/2`.
   - `prep_footage.py`: B-roll `CLIPS` / `STILLS`, `REAL_CONTENT_T`; run it. Resample the wall colour (`#pwall` in build.py) if the room differs.
   - `make_audio.py`: tempo/key/`section()` and the `build_sfx()` cues; run it.
   - `DUR=15 /usr/bin/python3 scripts/build.py` for a first look, then the full build.
5. **Check.** `npx hyperframes lint hf` and `npx hyperframes check hf` (0 errors). Snapshot every beat
   (`snapshot hf --at … --no-end`, add `--against <reference>` when matching an earlier cut) and look at the frames.
   Fix overflow, empty panels, captions over the card.
6. **Render.** Draft first (`render hf --quality draft --sdr`), then `NAME=<Name> zsh scripts/finish.sh` (delivery render + exact audio master).
7. **QC before handing over:** 0.5 s contact sheets (`qc_sheet.py`); audio offset vs the source 0 ms; a Whisper
   re-transcript of the end (nothing masks the last word); −14 LUFS / ≤ −1.5 dBTP; spelling of every on-screen word;
   nothing wider than the frame; end card ≥ 2 s.
8. **Deliver** the MP4 (H.264 High, AAC 48 kHz, 1080×1920, 30 fps) to `output/`, with a short BM note listing assets
   used and every assumption. Append the video to the video log.

## Known gotchas
- HyperFrames: every `<video>` needs an id; time the video, never its wrapper (`video_nested_in_timed_element`).
- A second `fromTo` on the same property needs `immediateRender:false`, or its from-state shows at t = 0. Elements
  that must hold a start pose before their tween (e.g. an icon at scale 0.6) need a `gsap.set` too.
- Never put a CSS `transform` on an element GSAP moves; centre with `kit.anchor()` (zero-size flex box).
- Never blur on an overshooting ease (`back.out`): the blur goes negative and sticks. kit.py blurs on `power2.out`.
- Clear `filter` after a blur-in (`filter:'none'`), or text stays soft.
- Relative tweens (`'+=260'`) while another tween writes the same property fail lint
  (`gsap_relative_value_second_writer`). Put each motion on its own wrapper with absolute values.
- `attr` tweens on one element count as one property for the overlap check: tween dash-march via `strokeDashoffset` (CSS), geometry via `attr`.
- Root-level clips anchor at 0,0: position with GSAP x/y. Videos inside `transform-style: preserve-3d` render black.
- Bundled fonts (Inter, Archivo Black, Playfair Display, JetBrains Mono) need no `@font-face`. Don't build the
  timeline inside `document.fonts.ready`: the first frame renders blank.
- `check` warnings that are expected: `line_unread` on 1–3-word captions, `composition_file_too_large`,
  `text_below_floor` on small "AI" tags. Errors are never expected.
- If `npx hyperframes` fails with `ETARGET` (registry lag on a fresh release), pin the version:
  `npx --yes hyperframes@0.8.212 …` (or `HF="npx --yes hyperframes@0.8.212" zsh scripts/finish.sh`).
- Python: use `/usr/bin/python3` (numpy, scipy, PIL, cv2). Homebrew `python3` lacks them; faster-whisper must be installed for the same python.
- Overshoot entrances clip at 1080 width: keep settled widths ≤ 960 px; side-by-side cards 430 px wide at x 95 / 555.
- Write new files to a fresh folder rather than `rm` on a glob.
