---
name: glow-keyword-style
description: >-
  "Glow Keyword Style" (formerly "Indo Glow Style"): locked style for vertical 9:16 talking-head + motion ads
  (Indo/Malay TikTok-Reels look). White italic keywords, brand blue highlight box, neon-blue connected script with
  glow, heavy RGB-split words, warm glow grade, punchy motion graphics and whoosh/pop SFX over a produced beat, with
  motion, layout and structure chosen fresh for each video's content. Use whenever the user says "Glow Keyword
  Style", "Glow Keyword", "Indo Glow Style", "Indo Glow", "style macam Jago Prompt", "style yang aku lock tu", or
  asks to edit a talking-head or motion ad "in the same style as before", even without
  naming it. Built with HyperFrames (HTML + GSAP); renders the real MP4.
---

# Glow Keyword Style

*Formerly named "Indo Glow Style". First built in Remotion for the "Jago Prompt" remake (Sep 2026, 50 s), then ported to HyperFrames (Oct 2026) with the same look.*

Every Glow Keyword video should feel like part of the same series, but it must **not** look like a copy of the last one. The style therefore has two layers:

| Locked (identity: same in every video) | Varies (chosen from the content) |
|---|---|
| brand blue palette, fonts, the 4 text treatments (italic keyword, heavy RGB word, blue box, neon script), glow grade, CTA keyword style, mix levels, safe area, QC and honesty rules | hook mechanic, explainer layout, transitions, caption placement, graphic metaphors, section structure, pacing, CTA layout, music tempo/mood |

The Jago Prompt edit is one *example* of the style, not a template to clone. Reusing its hook, layouts and choreography on a different topic is the failure the user explicitly warned about.

Where everything lives:
- `references/style_spec.md`: identity numbers (format, grade, type, colour, motion, transitions, audio, safe area). Its §6–7 describe what the Jago Prompt edit did; treat them as examples.
- **`references/variation_playbook.md`: read it before planning any motion.** It covers the edit brief, menus of hooks, layouts, transitions and metaphors, the content→choice mapping, anti-repetition rules and the video log.
- `references/pipeline.md`: project layout, commands, the `build.py` library API, layer order and the verification checklist.
- `template/`: a working HyperFrames build (`timing.json`, `scripts/`, fonts). Its worked example is the Jago Prompt hook + concept intro + CTA end card. Copy it for the plumbing, not the choreography.

## Locked identity

| Layer | Rule |
|---|---|
| Format | 1080×1920, 30 fps CFR, H.264 High + AAC 48 k, BT.709. The presenter footage is used 1:1: trim only real dead air over ~0.3 s and never cut a sentence |
| Grade | `scripts/grade.py`: a per-shot balance first (eq + colorbalance, natural skin), then the shared look: deeper-shadow curve, saturation ×1.06, warm highlight glow (threshold 0.62, σ38, screen @ 0.17), radial chromatic fringe, vignette 0.32. It is baked into `graded.mp4` by ffmpeg, never applied as CSS |
| Italic keyword | Inter Italic 600, 46–60 px, white with a soft black shadow. Blur-in 9→0 plus a 16 px rise, word by word |
| Heavy hero word | Archivo Black 120–220 px, tracking −0.02em. White over red `#FF3B3B` / cyan `#18E4FF` copies screen-blended: 3 px apart at rest, ~29 px on entry. Horizontal smear 1.9→1 in 0.18 s, soft white glow. 3–5 per video |
| Highlight box | Black bold-italic narrow type (Archivo at 80 % width) on `#14B8F0`. The box wipes left→right in 0.16 s and the text slides in 24 px |
| Neon script | Sacramento 100–170 px, rotated −6…−8°. Fill `#F0FBFF` with a 1–2 px stroke and a `0 0 3/10/24/48px` blue glow. Writes on left→right in 0.35–0.8 s, with a flicker on entry |
| CTA keyword | Archivo Black skewX(−9°), neon `#3DD8FF` fill, dark-blue stroke, 3-step 3D extrusion, a slow pulse. The CTA text is the user's own |
| Palette | Box `#14B8F0` · neon `#3DD8FF` · deep `#0A8ED6` · neon text `#F0FBFF` · ink `#060806`. For a student's own brand, swap the `PAL` entry in `build.py` (box/neon/deep/text) and keep every other rule |
| Motion | Punch-ins +10–20 % in 0.10–0.12 s (snap ease) at face height; a slow +3.5 % push across every shot; pops with overshoot (`.34,1.56,.64,1`); shakes of ±8–14 px on frustration words; RGB split on the video at ≤ 6 moments; something new every ~0.5–1.5 s; captions land on the word's start |
| Transitions | White flash 0.85 on the hook→body cut, a blue flash into the offer, a tinted flash into the CTA, small flashes (≤ 0.3) on hero words, zoom-blur ≤ 12 px on layout changes. No more than 6 flashes per video |
| Audio | The presenter's own voice only: cleaned, latency-compensated, −16 LUFS. An original synthesised beat (or a track the user supplies) about 16 dB under the voice, ducked −9 dB under speech, +7 dB on the CTA hold. Whoosh/pop/impact/riser/glitch/neon/typing/ding SFX on the word anchors. Master at −14 LUFS, TP −1.5 |
| End card | Hold ~3–3.5 s after the last word on the freeze frame, blurred 13 px and darkened ×0.44, with a slow 1.0→1.22 push |
| Safe area | Critical text inside y ≈ 250–1500 and x ≈ 60–960. Keep the right rail (x > 960, y 1100–1650) and the bottom 400 px free. Never cover the face. One focal element at a time |

## Storyboard first (must)

Make storyboard frames with the `storyboard-frames` skill (`.claude/skills/storyboard-frames/`) before any MP4 render, draft or delivery:
1. Build the composition.
2. Snapshot one still per beat onto numbered sheets.
3. Let the student refine frame by frame.
4. Render only after they reply "ok storyboard".

Every render step in the workflow below comes after that approval.

## Workflow

1. **Watch and analyse everything first.**
   - Make contact sheets of the footage and of any new reference.
   - Find shot cuts (`ffmpeg select=gt(scene,0.25)`) and the voice level per shot.
   - Make a word-level transcript: `scripts/transcribe_words.py` (faster-whisper large-v3, `ms`, with key terms in the prompt).
   - Keep the narrative order. Never regenerate the presenter's voice.
2. **Copy the template** to `work/<project>/` and put the source path in `SRC_MOV`. Probe the source: if it is HDR (HLG/PQ), render with `SDR=1`.
3. **Timing.** Put the word anchors in `work/anchors.json`, run `make_audio.py` once to get `work/audio/voice.wav`, then run `refine_times.py`. It snaps each anchor to the voice envelope (Whisper drifts 0.2–0.3 s) and writes `T` in `timing.json`. Also set `CUT`, `L`, `SRC_END` and `TOTAL` there. Captions, camera and SFX all read this one file.
4. **Footage.**
   - Tune the per-shot balance in `grade.py` (`SHOTS`), then run `prep_footage.py graded`. It writes `graded.mp4` and `lastframe.jpg`.
   - For explainer layouts, add `CUTOUTS` to `timing.json` and run `prep_footage.py cutout`. It uses the HyperFrames matte on the graded pixels.
5. **Plan, then build.**
   1. Write the edit brief (playbook §1) and read the video log.
   2. Choose the hook, the explainer layout(s), the transition families, the caption pattern, the metaphors, the CTA layout and the music mood. They must fit *this* content and differ from recent videos.
   3. Tell the user the plan in 3–4 lines and wait for an ok.
   4. Rewrite `example()`, `camera()` and the scene helpers in `build.py`; the library functions stay as they are. Visualise what is said. Captions are short keywords, never paragraphs.
6. **Audio.** Rewrite `cues()` and `SECTIONS` in `make_audio.py`. Change the tempo, key and groove for the video, but keep the mix numbers. Run it to get `hf/assets/mix.wav`.
7. **Check.** Run `build.py`, then `npx hyperframes lint` and `npx hyperframes check`; both need 0 errors. Snapshot every beat with `snapshot --at …`, and use `--against <reference.mp4>` when rebuilding an edit. Look at every frame yourself.
8. **Render.** Run `QUALITY=draft scripts/finish.sh` for a preview. After approval, run `scripts/finish.sh` for delivery. It re-tags BT.709, adds faststart and prints the ffprobe result and the loudness.
9. **QC before handing over.**
   - Make 0.5 s contact sheets of the export (`qc_sheet.py`).
   - Check the audio sync (envelope cross-correlation lag 0 ms) and run a Whisper re-transcript of the final mix.
   - Confirm −14 LUFS / ≤ −1.5 dBTP.
   - Check the spelling of every on-screen word, the safe area, and that the CTA is readable for ≥ 3 s.
10. **Deliver.** Hand over the final MP4 and a short README in BM listing what matched and every difference or assumption. Add this video's choices to the video log (playbook §5).

## Honesty rules the user cares about

- Screens of tools that weren't actually recorded are drawn as clean explanatory cards labelled "Visual contoh". Example values are labelled "Contoh", and grids built from the presenter's own frames are labelled "Ilustrasi konsep".
- Don't add features, bonuses, testimonials, links or promises the user didn't give. The CTA text comes from the user or the recording.
- If an exact asset (font, music) isn't available, use the closest match and say so in the summary.
- Never overwrite the source video.

## Known gotchas

From the Remotion original (still true):
- Cut-outs sit **under** the room layer. Fading the room reveals the presenter with no brightness dip. Use the `room_fade()` helper.
- The voice chain (afftdn, adeclip) adds about 25 ms of latency. `make_audio.py` measures it and shifts the voice back; keep that step.
- Shots from different AI clips can be 13–19 dB apart. The per-shot gain is measured automatically (75 % of the way to −16 dB).

HyperFrames:
- Every `<video>` needs an id. A second `fromTo` on the same property needs `immediateRender:false`. Hide late elements at t = 0 (each helper's first `fromTo` does this).
- **Never let an overshooting ease drive `blur()`.** A negative blur is invalid CSS, so the element stays blurred. `pop_in()` gives the blur its own ease-out tween.
- Remotion's `opacity = clamp(k × eased p)` reaches full opacity in about one frame. The helpers use 0.02 s opacity ramps for that reason; a 0.1 s linear ramp makes hero words look ghosty.
- Tweens on one property must not overlap (lint). `track()` clips each key's duration to the next key, and `heavy()` shortens its entry when the exit comes early.
- The RGB layers of a heavy word overlap on purpose. They carry `data-layout-allow-overlap`, and a hidden sizer span gives them their size (a transparent-fill node fails `check` as `text_not_painted`).
- Don't build the timeline inside `document.fonts.ready`, or the first frame renders blank. Only the auto-fit (font-size) runs again after the fonts load.
- Videos inside a `transform-style: preserve-3d` stage render black. The card flip uses a per-element `transformPerspective` instead.
- Root-level elements anchor at 0,0. The camera moves `#frame` with GSAP `x/y/scale/rotation` around its centre; never put a CSS transform on a GSAP-animated node (text anchors are separate parent divs).
- Pin the CLI version (`HFV` in `finish.sh`, `npx --yes hyperframes@<version>`). A bare `npx hyperframes` sometimes picks up a version that was published minutes ago and doesn't resolve yet.
- Bundled fonts (Archivo Black, Inter, Montserrat, Poppins, JetBrains Mono …) need no `@font-face`. Sacramento and the variable Archivo/Inter files ship in `template/assets/fonts/`.
- Use `/usr/bin/python3`, which has numpy, scipy, PIL and cv2; Homebrew `python3` lacks them.

## Communication

The user writes casual Malaysian BM ("aku/korang"). Reply in BM. On-screen text uses BM santai with the correct spelling of terms (character sheet, custom GPT, client course portal, taip).
