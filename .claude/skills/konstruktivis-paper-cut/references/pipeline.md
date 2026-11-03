# Konstruktivis Paper-Cut: pipeline and numbers

## Project layout
```
<Project>/
  scripts/index.tpl.html   root + CSS + helpers + S1 + captions + end card  (/*__WORDS__*/ and /*__SCENES__*/ placeholders)
  scripts/scenes/s02_04.js S2 mic/disc, S3 teachers, S4 canvas lecture hall
  scripts/scenes/s05_08.js S5 doors/book, S6 stairs, S7 platforms, S8 machine
  scripts/scenes/s09_13.js S9 phone feed, S10 table, S11 book wall, S12 style tiles, S13 CTA
  scripts/build.py         assembles hf/index.html
  scripts/words.py         words_raw.json + vo envelope -> hf/words.json
  scripts/make_audio.py    voice + song + SFX -> hf/assets/mix.wav
  scripts/make_grain.py    hf/assets/grain.png
  hf/                      HyperFrames project (assets/vo_src.wav, song_src.wav, grain.png, mix.wav)
```
The root has `data-duration` equal to `DUR` in `make_audio.py`. Change both, together with the caption end (55.0 in the caption loop).

## Scene catalogue (first build, 57 s)
| Time | VO | Visual → handoff |
|---|---|---|
| 0–6.45 | senang… tak pandai cakap depan kamera… video motion | Shy figure next to a giant camera, crossed-out speech bubble, shapes start moving → dolly into the lens |
| 6.45–9.2 | voiceover dengan animation macam ni sendiri | Mic in the lens with sound rings → radial disc → red dot on a cream iris |
| 9.15–14.3 | educator, cikgu-cikgu, lecturer | The dot becomes a teacher's head, a skill card drops into their hands, two more teachers appear → zoom into the card |
| 14.2–18.4 | ilmu sampai ke pelajar-pelajar | Canvas 3D lecture hall: the camera rises off the cream aisle and tilts up, a red wave turns every student red, fly to the door |
| 18.33–23.1 | panduan edit video guna code; tak payah prompt/coding | Doors open on the PANDUAN book, PROMPT and CODING chips are struck out and dropped, the book opens → zoom into the page |
| 23.04–31.6 | step by step… install… ChatGPT / Claude | Page lines become stairs, a figure hops step by step (download, terminal, gear, { }, ▶), two platform monoliths, pick ring, ✓✓ → whip |
| 31.3–36.2 | masuk satu slide… video edutainment | **Hero:** a hand drops a slide into the machine and a film frame comes out with the slide's shapes animated → zoom |
| 35.95–40.5 | awareness, promotion, hujung jari | Hand-held phone feed swipes, tap ripple → whip |
| 40.25–45.3 | group support, terus tanya | Top-down table with jointed figures, network lines, ? → ✓ and ! → zoom into the phone |
| 45.22–50.1 | Prompt Vault, pilih strategi | Wall of book boxes, the red PROMPT VAULT book flies out and opens, 5 strategy cards fan out, pick ring → card fills the frame |
| 50.05–53.1 | styling dah ada; follow, buat, dapat video | Style tiles flip, three stamps → red flood from the play button |
| 53.04–57 | Nak belajar? Tekan link sekarang | Phone CTA, thumb press, red laser sweep, red flood, end card |

## Motion numbers
- Zoom-through: `#zN` transform-origin is set on the shape that carries over; scale 15–26 in 0.45–0.8 s with `power3.in`. The next scene starts already scaled (`#cN` from 7 → 1, `power3.out`).
- Pops: `back.out(1.6)` over 0.35–0.45 s. Stamps: scale 1.8 → 1 with `power4.out` over 0.25 s plus a thock.
- Rays rotate about 20° across a scene with `ease: "none"`. Bands and figures drift 20–60 px with sine.
- Caption box: top 1050, height 130, Montserrat 900 at 76 px, stroke 13 px, shadow `0 8px 0 #0f0d0c, 0 10px 18px rgba(0,0,0,.45)`.

## Audio recipe (`make_audio.py`)
- VO: gain only, with a soft limiter.
- Song: starts at `OFF = songDrop − visualReveal` (40.08 − 18.33), fades in over about 1 s and ends at its natural end. Gain `db(-18.5)` gives about −31 LUFS, ducked by a further −5 dB while the voice envelope is active.
- SFX: synthesised whoosh (band noise sweep 400 → 2400 Hz) on every handoff, a thock (150 Hz) on stamps and soft ticks on UI. No repeated sample, because every call has its own random seed.
- Master: −14 LUFS integrated, −1.0 dBFS peak.

## Variants already made (do not repeat them as-is)
- **Editorial v2:** ivory/charcoal/cobalt with the same scenes.
- **16:9:** the same scene scripts with `FMT=16x9`. A per-scene VIEW framing in portrait units, plus `OFF()` group offsets and `P()` value switches.
- **Dark 16:9:** `THEME=dark`, with the accent rotating green → amber → violet → coral → sky at the handoffs nearest each 10 s.

