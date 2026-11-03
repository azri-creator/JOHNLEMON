---
workflow: general-video
flow: automation
storyboard: no
message: "Footage banyak tapi tak sempat edit; VGC ajar automate editing guna ChatGPT/Claude, bermula dari basic sampai expert."
destination: "Meta/TikTok vertical ad"
aspect: "9:16 (1080x1920, 30fps)"
language: "Bahasa Melayu"
audience: "Creator/usahawan yang ada footage tapi tak sempat edit"
length: "follows edited VO (~62 s)"
---

## Intent
VGC ad in the editing/motion style of "Break Pattern Story" (collage of cutout character + screenshots + footage cards + big kinetic words + motion, alternating dense and empty scenes). Built on the user's own recorded VO ("VO Break Pattern Story.m4a"), tidied (silences shortened, speech untouched).

## Assets
- Edited VO: `assets/audio/vo.wav` (from `../audio/VO_Break_Pattern_EDITED.wav`)
- Proof: `assets/video/casestudy.mp4` (VGC_CaseStudy_BeforeAfter_1080x1080.mp4, before top / after bottom, original text kept, never covered)
- Characters: 4 PNG cutouts (shoot, serabut, penat, presenter), original transparency
- Product: the brand's own product screenshots and logo files (supplied by the student)
- Footage cards: stills taken from the user's own raw talking-head clips

## Customizations
- Palette (graphics/text only, footage untouched): off-white, navy/charcoal, mustard (matches outfit).
- Fonts: Archivo Black (impact) + JetBrains Mono (UI labels).
- No full subtitles; text only on punchlines / key points / CTA.
- No prices, testimonials, stats or guarantees added.

## Notes
- Sync table lives in `index.html` (`T` constants) and was derived from the edited VO energy dips + syllable timing (Whisper word times drift ~0.2 s).
- Audio is a single pre-mixed track (`assets/audio/mix.wav`): VO + low/slow music + sparse SFX + case-study original audio inside the demo gap only.
