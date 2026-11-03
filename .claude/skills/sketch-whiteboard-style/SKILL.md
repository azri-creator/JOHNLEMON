---
name: sketch-whiteboard-style
description: >-
  "Sketch Whiteboard Style": the user's locked style for faceless hand-drawn whiteboard explainer/ads on a
  voice-over (first built for VGC "Sketch Educators", Oct 2026). Cream paper #f2ede3, charcoal ink, one accent per
  board (blue, red, green, a little purple) with marker-tint highlights. A blue pencil (never a hand) writes and
  draws line-art in sync with the voice. One long sheet: the camera pans while the pencil draws a connecting line
  into the next board. Calm soft fades, song low under the voice, marker-scribble SFX. Renders 9:16, 16:9 and 4:3.
  Use whenever the user says "Sketch Whiteboard", "style whiteboard", "style sketch", "style Sketch
  Educators", "macam video Sketch Educators tu", "lukis tangan", or asks for a hand-drawn / doodle / whiteboard
  explainer, even without naming it. Built with HyperFrames; renders the real MP4.
---

# Sketch Whiteboard Style

First built for VGC **"Sketch Educators"** (22 Oct 2026): 61.8 s, 15 boards, aimed at cikgu and lecturers, on a supplied VO and a kids-story song.
- v1 copied a Threads reference post: white paper, a cartoon hand, gold icons and boards sliding left. The user said it was too cluttered ("terlampau serabut").
- **v2 is the locked style:** pencil only, calm, continuous, cream and charcoal with accents.

What changes per video and what stays locked:
- **Per video:** the VO, the boards (one board per idea), the drawings and the accent per board.
- **Locked:** the identity below.

Where everything else lives:
- `references/pipeline.md`: the action API, the board catalogue, the landscape layout and the audio recipe.
- `template/hf/index.html`: the exact approved v2 composition (one file, 15 boards). It is a worked example, so replace the board blocks rather than writing from scratch.
- `template/scripts/`: the rest of the build: `events.py`, `make_audio.py`, `build_fmt.py` and `transcribe.py`.
- `references/index_v1_hand_gold.html`: the rejected v1, kept as a reference for what **not** to do.

## Locked identity

| Layer | Rule |
|---|---|
| Paper | Cream `#f2ede3`, with cards in `#fbf8f1` and grey `#6b6a70` for secondary lines. No white paper, no gold |
| Ink | Charcoal `#26262b` for all outlines and text. Strokes are round-capped, 5–7 px |
| Accents | **One accent per board**, chosen from blue `#2d5bff`, red `#f0453a` and green `#14a85a`, with purple `#8b5cf6` only rarely. Marker highlights use the light tint (`#a9c0ff`, `#ffa79f`, `#8fe0b2`, `#cdb9ff`) under the key word |
| Type | Archivo Black uppercase for headlines and key words, and Poppins 700 for sentence titles. Write English words in their English spelling, for example "Group" and not "Grup" |
| Tool | A **blue pencil only**, never a hand. It glides on eased paths (smootherstep), follows every `write`/`draw` stroke, rests low-right when idle (`REST`) and never pops in or out mid-video |
| Drawing | Line-art icons (phone, laptop, slides, chat bubble, vault, play button and so on) are drawn stroke by stroke with dash-offset. Fills wash in **behind** the pencil. Text writes left to right through a clip reveal |
| Continuity | One long sheet, with board `i` at `x = i × W`. Between boards the camera pans (sine in-out) while the pencil draws **one connecting line** from the last stroke of the board into the first stroke of the next. The line fades 0.7 s after it arrives. No slide-offs, no cuts |
| Motion | Calm: soft fades and eased glides. **No** bouncy pops, twinkles, sparkles or shakes. `pop()` is a soft scale-fade with no overshoot |
| Sync | Each board starts on its sentence. Stroke times come from the voice envelope, not raw Whisper times (Whisper drifts 0.2–0.3 s). Whisper also invents words: "Bantu" at 22.6 and "Dah." at 50.92 were hallucinations, "cloud" was Claude and "prom" was prompt |
| End | The real VGC logo is drawn or popped onto the last board, with a short tracked CTA line. No button unless asked |
| Audio | Voice with gain only (+6 dB in the first build). The song is slowed to 0.75×, low-passed at 3.8 kHz, about **20–22 dB under the voice** and ducked a further 4 dB. SFX are synthesised and soft: a marker scribble under every pen stroke (quieter for drawings), small pops for stickers and a paper swish on each pan. A soft limiter at −1 dBFS and a 1 s fade-out |

## Storyboard first (must)

Make storyboard frames with the `storyboard-frames` skill (`.claude/skills/storyboard-frames/`) before any MP4 render, draft or delivery:
1. Build the composition.
2. Snapshot one still per beat onto numbered sheets.
3. Let the student refine frame by frame.
4. Render only after they reply "ok storyboard".

Every render step in the workflow below comes after that approval.

## Workflow

1. **Transcribe:** `/usr/bin/python3 scripts/transcribe.py hf/assets/vo_src.wav scripts/words_raw.json`. Fix the Whisper errors by hand.
2. **Plan boards:** one board per sentence or idea. For each, write the time its first stroke starts, its accent, its title and its drawing. Keep the boards sparse: one title, one drawing, at most two short lines of copy.
3. **Build:**
   1. Copy `template/hf` and `template/scripts` into the project.
   2. Put `vo_src.wav`, `song_src.wav` (48 kHz stereo) and `brand_logo.png` in `hf/assets/`.
   3. Edit `BOARDS` (`[id, startTime, accent]`), `DUR`, and each board's `add()` markup and action calls.
4. **Audio:** run `python3 scripts/events.py` (it reads the pen, pop and push times from `index.html`), then `python3 scripts/make_audio.py`.
5. **Check:** run `npx hyperframes lint` and `check`, then snapshot every board and every pan midpoint. Look for:
   - a pencil tip that does not sit on the stroke being drawn;
   - text that runs past the board;
   - a first frame that is blank.
6. **Render 9:16:** `cd hf && npx hyperframes render --quality delivery --fps 30 -o ../<Name>_9x16.mp4`.
7. **Landscape (when asked):** `python3 scripts/build_fmt.py` writes `hf169/` (1920×1080) and `hf43/` (1440×1080) from the 9:16 source. Per board, `LAYOUT` puts the title on top, the art on the left and the copy on the right, with `fit()` sizing by getBBox. Render each one, and edit only `hf/index.html`.

## Break pattern (must)

Don't repeat the previous video's drawings or board order. Keep the identity, and draw new metaphors for every script. See the `feedback-break-pattern-across-videos` memory.

## Known gotchas

- **Build synchronously.** Building inside `document.fonts.ready` left the first frame of each snapshot or render worker blank. Use `clipPathUnits="objectBoundingBox"` for text reveals, and read `getBBox()` lazily per frame.
- Generated ids are `${id}_svg` and `${id}_defs`. Never give an element an id like `b7s` or `b4d`, because it clashes with board-derived ids.
- Round-cap strokes show a dot before the dash-draw starts. Also fade `strokeOpacity` in at the start of the draw.
- The pencil reads positions through `getCTM`, so groups that `LAYOUT` moves stay in sync in the landscape formats.
- Run Python with `/usr/bin/python3`.
