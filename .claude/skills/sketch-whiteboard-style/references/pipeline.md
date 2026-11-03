# Sketch Whiteboard Style: pipeline and numbers

## Project layout
```
<Project>/
  hf/index.html           the whole composition (const FMT = "9x16"; DUR; BOARDS; per-board blocks)
  hf/assets/              vo_src.wav, song_src.wav, brand_logo.png, mix.wav
  scripts/transcribe.py   Whisper large-v3 -> scripts/words_raw.json  ([start, end, word] list)
  scripts/events.py       pen / pop / push times from index.html -> scripts/events.json
  scripts/make_audio.py   voice + song bed + SFX -> hf/assets/mix.wav (+ stems/)
  scripts/build_fmt.py    hf169/ (16:9) and hf43/ (4:3) copies with FMT switched
```

## Action API (all times in seconds, positions in world coordinates)
- `write(id, t0, dur)`: reveals a `<text>` left to right (clip in the text's own bbox units). The pencil tracks the reveal edge.
- `hl(id, t0, dur, col)`: a marker highlight in the accent tint, swept under a text element.
- `draw(groupId, t0, dur)`: draws every outline in the group in document order, splitting `dur` by path length. The pencil follows the stroke, and fills wash in behind it.
- `pop(id, t0, s0)`: a soft appear (scale `s0` → 1 plus a fade, no overshoot), used for stickers, ticks and the logo.
- `add(boardId, html)`: inserts SVG into the board.
- `T(id, x, y, text, cls, size)`: a text helper. `cls` is `hd` (Archivo Black) or `tt` (Poppins 700).
- Shared shapes: `star()` and the icon snippets inside each board block.

Every action pushes a segment into `SEGS`. `handAt(t)` then places the pencil from the active segment, glides between segments with smootherstep, and returns to `REST` (`[960, 1640]` in 9:16) when idle for more than about 0.8 s. `OFF` is used only before the first and after the last stroke.

## Continuity (`PANS`)
For each board after the first, the pan starts about 0.6 s before the board's start time and lasts about 0.6 s, with a sine in-out camera (`camAt`). A thread path runs from the previous board's last pen point to the next board's first pen point. It is drawn with the same easing during the pan and fades 0.7 s after arrival.

## First build board timings (61.8 s)
b1 0 · b2 3.15 · b3 6.29 · b4 10.12 · b5 16.3 · b6 20.93 · b7 23.4 · b8 25.95 · b9 30.7 · b10 37.45 · b11 40.75 · b12 44.97 · b13 47.9 · b14 51.27 · b15 56.6

The accent order was BL BL RD GR RD PU BL GR BL GR PU BL GR RD RD. Accents rotate, and purple is used at most twice.

## Landscape layout
`LAYOUT[boardId] = { title: [...ids], art: [...ids], copy: [...ids] }`. `wrap()` groups the ids, and `fit(g, x0, y0, x1, y1, smax)` scales and centres them in the box. The title goes across the top, the art in the left 55 % and the copy in the right 45 %. Boards b1 and b4 are centred. `REST` and `OFF` switch with `LAND`.

## Audio numbers (`make_audio.py`)
- Voice: `vo *= db(6.0)`.
- Song: slowed to 0.75× and low-passed at 3.8 kHz beforehand (bake both into `song_src.wav` with ffmpeg `atempo=0.75,lowpass=3800`), with a 1.2 s fade-in. Gain is `db(-22)`, multiplied by `(1 − act·(1 − db(−4)))`, where `act` is the smoothed voice activity (threshold −36 dB, 0.3 s window).
- Scribble: band noise 1.8–6.5 kHz plus 0.5–1.5 kHz, amplitude-modulated at 8–11 Hz for writing and 3–5 Hz for drawing, at −33 or −35 dB.
- Pop: a 90 ms chirp at 480–620 Hz, at −35 dB.
- Swish: band noise at 0.3–2.6 kHz, sin² envelope, 0.6 s, at −38 dB, plus a quiet scribble on every pan.
- Master: tanh soft clip at −1 dBFS and a 1 s fade-out. Stems go to `stems/`.

