---
name: break-pattern-story-style
description: >-
  "Break Pattern Story Style": the user's locked style for 100 % motion ads built from a voice-over plus a few
  full-body cut-out photos of the presenter (no talking-head footage), first built for VGC "Break Pattern
  Story" (Oct 2026). Flat neo-paper collage: off-white dot-grid paper, navy/charcoal and one mustard accent from
  the presenter's outfit. The cut-out changes pose per beat beside ink-bordered paper UI cards with hard offset
  shadows, slammed Archivo Black words in strips, JetBrains Mono chips, dense → empty → bright rhythm, a real
  before/after demo and a navy CTA. Silences squeezed to ~0.2 s via one time-map. 9:16, rebuilt for 16:9.
  Use whenever the user says "Break Pattern", "Break Pattern Story",
  "style Break Story", "macam video Break Pattern tu", or asks for a motion ad from cut-out character photos and
  a VO, even without naming it. Built with HyperFrames; renders the real MP4.
---

# Break Pattern Story Style

First built for VGC **"Break Pattern Story"** (11 Oct 2026). The final is 48.5 s at 9:16 (`1FA VGC Break Story.mp4`), plus a 16:9 rebuild ("Contoh Motion Video Claude Edit 100%").
- **Inputs:** the user's VO, 4 cut-out PNGs of the presenter, the brand's own logo and product screenshots, stills from the user's raw clips, a before/after case-study clip and a supplied song ("the gonk").
- **Feedback that shaped it:** v1 (62 s) was "too slow, long gaps between lines". v2 and v3 squeezed the silences and added camera punches.

What changes per video and what stays locked:
- **Per video:** the VO, the beats, the poses and the product proof.
- **Locked:** the identity below.

Where everything else lives:
- `references/pipeline.md`: the scene catalogue, the VO-squeeze and retime pipeline, the audio recipe and the 16:9 rebuild.
- `template/master/index.master.html`: the exact working master (62.26 s, synced to the un-squeezed VO), recovered and re-verified against the final.
- `template/scripts/`: the rest of the build (`prep_assets.sh`, `edit_vo.py`, `edit_vo_fast.py`, `make_audio_fast.py`, `retime_build.py`, `make_landscape_master.py`, `audit_layout.py`, `sync_plot_fast.py`, `check_levels.py`, `transcribe.py`, `align_edited.py`).
- `template/hf/BRIEF.md` and `template/hf/design.md`: the brief and design spec.

## Locked identity

| Layer | Rule |
|---|---|
| Palette | Paper `#f2eee6` / `#e6e0d2`, ink `#14171f`, navy `#1b2236` / `#252f4a`, charcoal `#171a21`, mustard `#e09827` / `#f0b64a`. **One accent only**, taken from the presenter's outfit, and no neon. Footage and product screenshots keep their true colour |
| Stage | Full-bleed flat backgrounds with a 46 px dot grid (`.bg-paper`, `.bg-navy`, `.bg-char`, `.bg-must`). The background colour flips per beat: navy/charcoal when the work piles up, mustard when the idea lands, paper for explanations |
| Character | Full-body cut-out PNGs with original alpha and a soft drop shadow. **Change the pose per emotion**: shoot (phone selfie), serabut (hands on head), penat (slumped in a chair), presenter (open-palm point). There is often a mustard blob or circle behind them. The character sits at the side, and the content sits on the open side |
| Cards | Neo-paper: 4 px ink border, radius 24, hard `10px 10px 0` ink shadow, and a header bar with chips (`GALERI` / `VIDEO`, `POTONG`, `SUBTITLE CC`, `B-ROLL MP4`, `VISUAL PNG`, `SFX`). Footage cards show real stills from the user's clips with fake `MVI_###.MP4` labels |
| Type | **Archivo Black** uppercase (−0.03 em, line-height .92) for punchlines at ≥ 110 px, in a `.strip` (mustard or ink block with an 8 px offset shadow). **JetBrains Mono 700** uppercase for chips and labels at ≥ 44 px. Ghost words (7 % opacity) sit behind the scene. **No subtitles**: text appears only on punchlines, key points and the CTA |
| Rhythm | Alternate the density: dense (cards piling up) → empty (one clock "3 JAM") → quiet (tired pose, dark) → bright reveal (mustard lockup "VIDEO GUNA CODE", logo on the song drop). No still frame longer than 0.5 s: small "camera punches" on beats, plus ambient drift |
| Motion | Pops use `back.out(1.6–2)` over 0.35–0.45 s, about 20 % faster in the fast cut. Slams use `power4.out` from scale 1.6–2.2. Wipes are a mustard block over 0.35 s. Cards stack with slight random rotations |
| Proof | The real before/after case-study video in a paper card (`SEBELUM` / `SELEPAS · AI`). Keep its original text visible, and play its own sentence inside the demo gap |
| Product | The student's own product screenshots (3 cards) and their own logo files, supplied by them. Never recolour them, and never use another company's logo |
| Ladder | Stair blocks BASIC → ADVANCE → EXPERT on a mustard stage, with the presenter climbing |
| CTA | Navy stage, the VGC wordmark ("edit VIDEO GUNA CODE_"), "KLIK LINK. / DAFTAR / SEKARANG." strips, and a mustard pill "KLIK LINK →" with a cursor tap |
| Audio | VO: silences only are squeezed (between lines 0.20–0.26 s, inside sentences 0.14 s); speech and breaths are untouched. Song: subtle, about 21 dB under the voice, ducked, with a −3 dB dip at 2.2 kHz. Its **drop lands on the logo reveal**. SFX are sparse and synthesised: small pops, slams on punchlines and whooshes only on cuts or wipes. Mix to −14 LUFS, with a true peak of about −1.4 dBFS |

## Storyboard first (must)

Make storyboard frames with the `storyboard-frames` skill (`.claude/skills/storyboard-frames/`) before any MP4 render, draft or delivery:
1. Build the composition.
2. Snapshot one still per beat onto numbered sheets.
3. Let the student refine frame by frame.
4. Render only after they reply "ok storyboard".

Every render step in the workflow below comes after that approval.

## Workflow

1. **Assets:** run `zsh scripts/prep_assets.sh`, setting `CHAR`, `FOOT`, `CS`, `LOGO_ICON`, `LOGO_WORDMARK` and `CARDS`. Missing logos or cards become neutral placeholders; ask the student for theirs.
2. **VO:**
   1. Run `transcribe.py`, then `edit_vo.py` (a tidy pass: `audio/VO_…_EDITED.wav` and `vo_cues.json`, with the demo gap reserved).
   2. Then run `edit_vo_fast.py`. It squeezes the silences and writes `audio/retime_map.json`, which maps master time to fast time.
   3. Sync visuals to **energy dips**, not Whisper word times.
3. **Master:** edit `master/index.master.html` on the *un-squeezed* timeline. It has scene `<section>`s with data-start/duration, the `T` constants and one GSAP timeline. Rewrite the scenes for the new script, but keep the classes and helpers.
4. **Retime:** `python3 scripts/retime_build.py` writes `hf/index.html`. It remaps every scene, video and tween through the map, so speech stays 1:1 and the gaps shrink.
5. **Audio:** run `make_audio_fast.py` (VO, song with the drop on the logo, SFX through the same map, the case-study sentence), then copy `audio/mix_fast.wav` to `hf/assets/audio/mix.wav`.
6. **Check:**
   1. Run `npx hyperframes check` (contrast must pass; use `data-layout-ignore` on ghost words and `data-layout-allow-overlap` on intended overlaps).
   2. Run `python3 scripts/audit_layout.py`: side margins ≥ 70, key text y 190–1760, no text over the face.
   3. Run `sync_plot_fast.py` and `check_levels.py`.
7. **Render:** `cd hf && npx hyperframes render --quality delivery --fps 30`. Check for black frames, still frames longer than 0.5 s and −14 LUFS.
8. **16:9 (when asked):** run `make_landscape_master.py`, then `retime_build.py master/index.master16.html hf16/index.html`, then `audit_layout.py hf16`. This is a rebuild, not a crop: the character goes at the side, the workflow becomes a 3 + 2 grid, the stairs run left to right, and the demo card sits on the right.

## Break pattern (must)

Don't reuse the last video's beats as-is (gallery → pile → "3 JAM" clock → tired chair → pipeline → stairs). Keep the identity, but pick a new concept angle and a new signature moment per script. See the `feedback-break-pattern-across-videos` memory.

## Known gotchas

- Stop `hyperframes preview --background` before scripted edits, because Studio stamps `data-hf-id` into `index.html`.
- Root-level clips are anchored at 0,0. Position a `<video>` with GSAP x/y, not left/top.
- A second `fromTo` on the same property needs `immediateRender: false`.
- If you edit `hf/index.html` directly (for example in Studio), **don't** run `retime_build.py` afterwards, because it overwrites the file. Make the edit in the master instead.
- Bundled fonts (Archivo Black, JetBrains Mono) need no `@font-face`.
- Run Python with `/usr/bin/python3` (it has numpy, scipy, PIL and pypdf).
- The builder cannot hear the mix. Ask the user to listen once on a phone, especially at the song drop.
