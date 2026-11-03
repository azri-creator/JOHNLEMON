# PiP Explainer Style: identity spec (locked)

Everything here is the same in every video. The numbers come from the approved "Bisnes Baru Nak AI" edit
(Sep 2026). The template already encodes them in `template/scripts/kit.py` (palette, type, geometry, helpers) and
`template/scripts/build.py` (presenter, captions, flashes). Do not change them per video.

## 1. Frame and layout (1080×1920, 30 fps)
Only two layouts. The presenter is **one** `<video>`; switching is a fast morph of its wrappers (no crossfade, no
second copy of the footage): FULL → PIP 0.34 s, PIP → FULL 0.24 s, both `expo.out` (about 90 % there in the first
third, so it reads like the original snap cut).

| Layout | What is on screen |
|---|---|
| **FULL** | Presenter close-up. Base crop **1.2×** with origin (540, 1500), so the crop comes off the empty head-room and the hands stay. Punch-ins multiply on top of it, around the face (≈ 530, 830). A slow push of +3.5% runs inside every FULL stint (4 s). Soft navy vignette top and bottom. |
| **PIP** | Presenter in a rounded card at the bottom: x 30, y 1372, 1020×508, radius 40, cyan hairline plus a glow. The presenter is scaled **0.6** (growing to 0.618 over 5 s), centred, and the source rows from ~430 px (cap) down are shown. The card fill is a wall-colour gradient (`#c9c8c4 → #8f8e8b`), and the footage edges are feathered with a horizontal mask (11 %) so the plain wall blends. Resample the wall colour for a new room. The card nudges (scale 1.03 → 1, 0.25 s) on PiP→PiP scene changes. |

- The **graphic panel** sits above the card, roughly y 150–1250:
  - **Title** at y≈205 (Inter 800, 58–66 px, white), with one **serif-italic accent word** (×1.18, yellow). Written as `"Sumber *trafik*"`.
  - Content sits between y≈300 and 1180.
- Panel "camera": each scene pushes in from **1.14× + blur 14 px → 1.0× sharp** in 0.42 s, drifts +3.5%, and snaps out in 0.1 s. This is the main motion of the style (`panel()` in kit.py).
- Rhythm: switch layout on meaning (question, punchline or new idea), about every 2–6 s. FULL is for punchlines, questions, emotion and "wajah penuh" moments. PIP is for explanations, lists and examples.

## 2. Palette (client, estimated from the logo)
- Base: navy `#061329` with a dot grid (cyan 16% dots, 34 px pitch, drifting slowly), plus a drifting blue glow and a vignette.
- Cards: `#0C2147 → #0A1D3D` gradient, border `rgba(0,207,245,0.35)`, radius 22–30, heavy drop shadow.
- **Cyan `#00CFF5` / blue `#087BEE`** = structure (lines, icons, borders, first layers).
- **Yellow `#FFE600`** = emphasis only: keywords, the "paling penting" item, stamps and boxes. Yellow boxes get navy text.
- **No red** as a main colour.
- For a student's own brand, swap the cyan/blue for their brand colours in `kit.py` `C`; keep navy + yellow roles.

## 3. Type
- Inter 800–900 for titles, labels and captions (bundled).
- Archivo Black for slams, big numbers and funnel labels (bundled).
- Serif italic for one accent word per title and small asides ("dulu.", "banyak", "atau"). The original face is
  **Instrument Serif** italic: drop `InstrumentSerif-Italic.woff2` (OFL, Google Fonts) into `hf/assets/fonts/` and
  kit.py uses it automatically (×1.18). Without it the bundled **Playfair Display** italic is used (×1.06, slightly wider).
- Slam words are auto-fit (`fit()`, measured Archivo Black widths) to ≤ 960 px. Captions stay at 64 px.

## 4. Captions (BM, Reels/TikTok safe)
- Chunks of 1–3 words (≤ 16 characters), broken at punctuation or pauses > 0.35 s. One chunk on screen at a time.
- Words not yet spoken show at 35% opacity. Keywords are yellow.
- Pop entrance: 0.86 → 1 with a slight overshoot (0.16 s).
- Position: y 1210 in FULL (chest) and y 1296 in PIP (just above the card); the caption layer glides with the morph.
- Keep inside x 60–1020 and above y≈1480 (platform UI).
- Spell terms the standard way on screen: "mekanisme", not Whisper's "mekanism". Hyphenated reduplication stays joined ("buih-buih", "Baru-baru").
- If a word is genuinely unclear, don't guess. End the chunk with "…" and tell the user.

## 5. FULL-mode "Slam" words
- Archivo Black 96–170 px at y≈1440 (below the caption line, above the platform UI).
- Either white with a shadow, or a **yellow box with navy text**. An optional icon sits on the left.
- Entrance: scale 1.6 → 1 with BACK easing, blur-in and a short shake. Exit 0.14 s.
- Use one per FULL beat at most, on the punchline word (TAK BOLEH, BRAND TRUST, DAH CLEAR?).

## 6. Flashes and shakes
- A screen-blend flash only on big accents, amplitude 0.2–0.55, 0.04 s up and 0.22 s down: frame 0, the hook number, the punchline, the pattern interrupt and the end card.
- Shake (8–14 px, ≤ 0.3 s, seeded per frame) on hits: the counter landing, a slam, the poster/"jangan cakap" moment.

## 7. Cold open (first ~10 s must be punchy; the user asked for "+10%")
- Frame 0: white flash 0.5, punch 1.22 → 1.0 (SNAP), shake, impact SFX, and the beat already running.
- Headline slam from frame 0 (the topic in 2 words), then swap to the question teaser (e.g. "100% AI?") on the next key noun.
- Snap-zoom on 2 early keywords.
- The first PIP scene lands on the key noun. A big number or keyword counts up fast (0.3 s) with ticks, then shakes on landing.
- The music **drops** on the hook keyword.

## 8. End card
- Starts ~0.1 s **after** the last word; never cover the last word. Hold ≥ 2 s.
- Navy + dot grid. Takeaway in 2 lines: white Archivo Black plus a yellow box (e.g. "FUNDAMENTAL" / "DULU").
- Small logo row: the brand's app icon + wordmark (`LOGO_ICON` / `LOGO_TEXT` in prep_footage.py). In this repo that is
  the **student's** logo, never client's or VGC's.
- For tutorial content use the channel's tutorial line; for opinion/education talking heads, use the video's own takeaway.

## 9. Footage treatment
- Keep original colour. Lift the face gently with a tone curve only (`curves=master='0/0 0.25/0.30 0.5/0.56 0.75/0.79 1/1',eq=saturation=1.03`); no creative grade, no coloured overlay on the face.
- iPhone HLG/PQ footage is tone-mapped to SDR BT.709 in `prep_footage.py` first; always render `--sdr`.

## 10. Audio
- **Voice:** the presenter's own voice, never regenerated. HPF 85, light afftdn, −2 dB at 240 Hz, +2.5 dB at 3.2 kHz, de-ess, 3:1 compression, loudnorm −16. Compensate the chain latency (~25 ms) so lips stay in sync.
- **Music:** original bed synthesised in `make_audio.py`. Default 140 BPM half-time trap-pop (Dm–Bb–F–C), with a downbeat aligned to the hook keyword (drop).
  - Sections follow meaning: punchy cold open, then the drop, a story dip, the groove, a **beat-stop before the punchline** and re-entry on the next key phrase, a tighter groove for UI/tech scenes, a breakdown under the reflective question, a light build, and the end hit plus a ringing chord.
  - Change tempo, key or groove per video.
- **SFX:** synthesised whoosh (card in), pop, tick = click + ding (list items), impact (punchlines), glitch (small), soft UI dings (chat/notifications) and bubble pops. Use at most one SFX per visual event; nothing on every word.
- **Mix:** music ducked −8 dB under the voice (≈ −14.5 dB relative), SFX ×0.32 with −3 dB ducking, master **−14 LUFS / −1.5 dBTP**. `finish.sh` muxes this master into the render unchanged.
- Never put a riser or impact under the last spoken word; it masks it. Check by re-transcribing the ending.
