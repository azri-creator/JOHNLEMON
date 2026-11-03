# Astra Styles — module catalogue

Pick modules to match what the presenter says; do not use all of them. Each module names the config block / DOM ids in
`template/scripts/build.py` (the Merapu build) so you can lift it. Times quoted are from the Merapu script, for scale only.

## Built and approved (Merapu)

### 1. Comment card (hook) — `#cmt`
White card (`rgba(255,255,255,.96)`, radius 30, big soft shadow) with a grey avatar, "Netizen / komen pada video anda" and the
quoted line at 38 px (46 px in 9:16). The key word gets a gradient underline bar that sweeps in (`scaleX 0→1`, 0.35 s). Blur-in from
x −60 with a gentle 3D turn (`rotationY` 16→10) for 3.8 s, blur-out. Use it when the script opens with something somebody said.

### 2. Chaos beat ("merapu") — `CH`, `#burst`, `WOB`, `#chaos`
Comic stickers pop in on every stressed word (spring `back.out(3.2)`, 0.32 s, random start rotation −40°) and wobble until the stop
word. Style: Archivo 900 width 112 %, 5 px `#111` stroke with `paint-order: stroke fill`, hard `7px 7px 0 #111` shadow, colours `#FFE600 #00E5FF
#A6FF00 #FF8A00 #FF2BD6` and a rainbow-gradient word, emoji in Apple Color Emoji, a red "SUBSCRIBE 🔔" button, a 24-point yellow
starburst rotating behind. The footage shakes (`WOB`) and the audio swaps to the tacky 150 BPM loop. On the stop word: record scratch,
camera hard-set to 1.0, `#chaos` goes `grayscale(1)`, then blur 14 px / opacity .45 / scale .94 (0.25 s), then out (0.18 s) while the calm
bed swells back. Only use it when the script literally describes overload; otherwise cut it and its audio.

### 3. Two-tone type — `TT`, `SCRIM_L/T`
White setup line, then the magenta punch line 0.8–1.8 s later. Left-aligned on the left third in 16:9 with the presenter pushed right
(`R()` camera); centred above the face in 9:16. A scrim sits under the type. See pipeline §6 for the numbers. About 6 blocks in 45 s.

### 4. Hero word behind the head — `#kick1`, `#hero`, matte window
A small kicker (Archivo 700, 36 px, tracking .22 em, e.g. "Konsep AI edit video") then one big Outfit word (360 px 16:9 / 300 px 9:16,
gradient). Letters blur up with a 0.045 s stagger, the gradient sweeps across once (`background-position 0%→100%`, 0.9 s), then out.
It sits in `#headsB`, so the matte layer (visible only in this window) puts the head in front of it. Use for the one word the
whole script hangs on.

### 5. Dark stage + prompt bar + virtual camera — `#stage`, `#bar`, `UI`, `P1`
"I tell the AI to do X" beat. Footage blurs into the plum stage, a label with a gradient keyword ("Nak editing **heavy?**"), the prompt bar types
the command, the camera pans along the line and zooms onto the send button, a white cursor clicks, the stage blurs away. Pipeline §7.

### 6. Glass pill prompt over footage + native subtitles — `#pill`, `P2`, `SUBS`
For the quiet "do it simple" beat: a glass pill (spark icon, typed text, gradient send button) over the footage, then the result appears as
plain white subtitles (`.nsub`, Inter 700 54–60 px with a strong shadow) — the "AI did it" proof without a stage.

### 7. Floating cards + rack focus — `CARDS`, `RACK`, `CA_FWD`
Four result videos enter one by one from the sides (two behind the presenter, two in front). One card flies forward while everything else blurs
and dims; it recedes when screenshots appear. Pipeline §8.

### 8. Proof screenshots with pink ring — `FB`, `RIM`, `#nlab`
A small gradient label ("Feedback student"), two real screenshots blur in with a slight 3D turn, the pink rim lands on the bubble when the
presenter says the matching word. Blur names and avatars first.

### 9. Thumbnail fan + closing two-tone — `TH`, `FAN`, `#t7`
Back on the stage: a label ("17 modul panduan"), three thumbnails fan out (centre one scales up and lifts), the group floats up 40 px, then a
two-tone closing word pair ("AUTOMATKAN / EDITING"). Use for "what you get" / module lists.

### 10. Glass CTA + sparkles — `#cta`, `#sp0..4`
Glass pill "TEKAN LINK DI BAWAH" with a pink spark, blur-in 0.5 s, five pink sparkles pop around it (`back.out(3)`, 0.07 s apart) with a sparkle SFX.
Keep the CTA wording the user gave; the Learn More button belongs to the platform.

## Seen in the reference (`Astra Style.mov`) but NOT built yet

These are ideas to offer, not tested recipes. Build them as new modules when the script calls for them, then add them above.

- A huge lower-case magenta hero word on the **left** of the frame ("e-com") with the presenter on the right.
- Dark plum stage with locked/blurred glass cards and a pink lock icon (paywall or "coming soon" beat).
- Callout diagram: a product on a pale gradient with thin leader lines and small labelled circles, headline above.
- Light UI screen recordings (white app UI) sliding in with a blur transition, and a red/pink "Subscribe" pill at the top-left.
- Soft focus-pull intros (the clip opens on a blurred shape that resolves).
