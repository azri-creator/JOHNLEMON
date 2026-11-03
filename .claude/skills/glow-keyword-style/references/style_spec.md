# Glow Keyword Style: specification

§1–5 and §8–10 are the locked identity. §6–7 record what the first video (Jago Prompt) did; they are examples of
the style, not a structure to repeat. For per-video choices see `variation_playbook.md`.

Values are the ones used in the locked original (client Jago Prompt remake, built in Remotion). They carry over 1:1 to
the HyperFrames build in `template/` (the `scripts/build.py` library, `scripts/grade.py` and `scripts/make_audio.py`).

## Contents
1. Format · 2. Grade · 3. Typography · 4. Colour · 5. Motion vocabulary · 6. Layouts · 7. Section recipe
8. Transitions · 9. Audio · 10. Safe area & composition

## 1. Format
1080×1920, 30 fps CFR. Presenter footage used 1:1 (only trim real dead air > ~0.3 s; never cut a sentence).
End card holds ~3–3.5 s after the last word on a blurred, darkened (brightness ×0.44, blur 13 px) freeze frame with
a slow 1.0→1.22 push.

## 2. Grade (`scripts/grade.py`, baked by `prep_footage.py graded` into `hf/assets/graded.mp4`, tagged BT.709)
1. Per-shot balance first (eq contrast/brightness/saturation + colorbalance) so shots match; keep skin natural.
2. Shared look: curves `0/0 0.10/0.065 0.30/0.27 0.55/0.56 0.85/0.88 1/0.985` (deeper shadows), saturation ×1.06,
   highlight glow (threshold ~0.62, gblur σ38, warm tint, screen @ 0.17), radial chromatic fringe (R ×1.0045,
   G ×1.0022, B ×1.0), vignette angle 0.32.
3. The grade is baked in ffmpeg, never applied as CSS filters on the footage. The only live treatments on the
   footage stack are the transition blur/dim (`#fx`) and the RGB split (an SVG filter on `#rgbw`).

## 3. Typography (HyperFrames: Archivo Black is bundled; Inter, Archivo and Sacramento ship as woff2 files in `template/assets/fonts/`)
| Role | Font | Treatment |
|---|---|---|
| Small keywords (side words, phrases) | Inter 600 italic (variable Inter, synthesised italic), 46–60 px | white, soft black shadow, blur-in + 16 px rise, word-by-word |
| Heavy hero word (PROMPT, CHARACTER, WAJIB, PENING?) | Archivo Black, 120–220 px, tracking −0.02em | white + red/cyan RGB split (3 px rest, ~29 px on entry), horizontal smear 1.9→1 in 0.18 s, soft white glow |
| Highlight box (ASYIK LARI, KEKAL SAMA) | Archivo Narrow Bold Italic look (variable Archivo 700, `font-stretch: 80%`, italic), 64–100 px | black text on `#14B8F0`, box wipes left→right 0.16 s, text slides in |
| Neon script (sebelum fikir pasal, *Sheet*) | Sacramento, 100–170 px, rot −6…−8° | `#F0FBFF` + 1–2 px stroke, glow `0 0 3/10/24/48px` blue, write-on clip 0.35–0.8 s, flicker on entry |
| CTA keyword | Archivo Black skewX(−9°) | neon blue fill, dark-blue stroke, 3-step 3D extrusion, pulse |
Auto-fit every line to ≤ 930–960 px width: `data-fit` on the text node, and `build.py` shrinks the font-size once the fonts have loaded.

## 4. Colour (client tutorial brand blue — sampled from the client's logo & course portal buttons, ~#20C0F0)
blue box `#14B8F0` · neon `#3DD8FF` · deep `#0A8ED6` · neon text `#F0FBFF` · ink `#060806` · cards
`#171b19→#101312`, border `rgba(255,255,255,0.12)` radius 26–34 · muted text `rgba(255,255,255,0.58)` · RGB split
red `#FF3B3B` / cyan `#18E4FF`. Background for explainer layouts: near-black `#040504` + faint blue radial top +
60 px grid lines at 3.5 % white drifting slowly.

## 5. Motion vocabulary
- Punch-in zoom on emphasis words: +10–20 % in 0.10–0.12 s (snap ease), release over 0.25–0.35 s; zoom origin at
  face height. Constant slow push +3.5 % across each shot.
- Pop: scale 0.4–0.6 → 1 with overshoot (bezier .34,1.56,.64,1), 0.28–0.32 s, blur 10→0. The blur has its own ease-out
  tween, never the overshoot ease. All eases are the original beziers via GSAP CustomEase: EO .16,1,.3,1 · EI .7,0,.84,1
  · EIO .65,0,.35,1 · BK .34,1.56,.64,1 · SN .05,.9,.1,1.
- Motion blur on flying objects (blur ∝ speed) + arc paths.
- Shake (±8–14 px, 0.25–0.4 s) on frustration words; RGB split on the video (SVG filter, `bump_rgb()`) at ≤ 6 moments.
- Something new happens every ~0.5–1.5 s; captions appear on the word's start time.

## 6. Layouts (example: Jago Prompt; more options in variation_playbook.md)
- **Hook frame:** video frame shrinks in steps on pure black (1.0 → 0.9 → 0.8 → 0.6 → 0.55 → 0.5) on stressed
  words, slight tilt ±1°, drops lower so the top third holds graphics (cards). Expands back to full with blur + flash
  on the cut.
- **Full frame:** keywords at chest height (y ≈ 1040–1320) or side words at y ≈ 820–880 left/right; above the head
  (y ≈ 320) when the face fills the chest area.
- **Explainer:** presenter cut out (`npx hyperframes remove-background` matte on the graded pixels, VP9 alpha) at 0.6–0.62 scale in a bottom corner, face
  y ≈ 1050–1250; room fades out underneath (cut-out layer sits UNDER the room layer to avoid a brightness dip);
  graphics card y ≈ 196–960 (or header y 262 + chips y 400 + card y 505–1145).
- **Full-screen moment:** concept grid zooms to near full screen with hero text over a dark scrim, then shrinks to
  a thumbnail feeding the next section.

## 7. Section recipe (example: problem→solution tutorial)
1. Hook/problem — shrinking frame + illustrated cards + question marks + blue box on the pain word.
2. Concept — neon script lead-in + heavy hero word + script accent; key promise in a blue box.
3. How-to — numbered step card (badge + title), cursor clicks, photos flying into slots, typing fields, generated
   grid — all labelled "Visual contoh"/"Contoh input"/"Ilustrasi konsep".
4. Reuse/payoff — thumbnail → labelled cards with flying copies and ✓ checks.
5. Offer/USP — clear visual change (blue flash), brand header, COPY → EDIT → PASTE chips, template card with
   neon-blue-highlighted editable [LABELS].
6. CTA — the user's exact CTA text, heavy white lines + blue underline, neon 3D keyword, comment-box mock typing it.

## 8. Transitions
White flash 0.85 on the hook→body cut; blue flash 0.7 into the offer section; tinted flash 0.75 into the CTA;
small flashes (≤ 0.3) on hero words. Zoom-blur (≤ 12 px) during layout changes (0.35–0.45 s, ease-in-out).

## 9. Audio (`scripts/make_audio.py` → `hf/assets/mix.wav`, one `<audio id="mix">` in the composition)
- Voice: original only. Per-shot gain toward −16 dB (75 %; the voiced median is measured per shot), adeclip, HPF 80, afftdn nr 8, −2.5 dB @250 Hz,
  +2.5 dB @3.4 kHz, +1 dB shelf 9 kHz, deesser, compressor 3:1 @ −21 dB, loudnorm −16; compensate chain latency
  (measured ~25 ms).
- Music (tempo/key/groove vary per video — see playbook; the first video used): original synthesised trap-pop, 144 BPM (72 half-time), A minor Am–F–C–G, 808 + kick + clap on 3 + rolling
  hats + FM pluck; filtered intro, downbeat on the first hard cut, breakdown + riser before the offer, hit on the CTA.
  Or a real licensed track (e.g. Flow Music) if the user supplies/approves one.
- Ducking: music −9 dB, SFX −3 dB under speech (voice envelope); music ≈ −16 dB below voice; +7 dB on the CTA hold.
- SFX: whoosh on moves, pop on entries, click on cursor, impact on hero words, riser into big cuts, glitch on
  frustration, key ticks on typing, ding on checks.
- Master: two-pass linear loudnorm −14 LUFS, TP −1.5, limiter; verify with a Whisper re-transcript.

## 10. Safe area & composition
Critical text within y ≈ 250–1500 and x ≈ 60–960; keep the right rail (x > 960, y 1100–1650) and bottom 400 px free
of important text. Never cover the face; hands/mic may be overlapped by cards. Viewer should always know whether to
watch face, text or demo — one focal element at a time.
