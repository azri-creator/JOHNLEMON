# Glow Keyword Style: variation playbook

Glow Keyword Style is a *look*, not a fixed edit. Only the identity layer is locked: palette, fonts, text treatments, grade,
glow, mix levels and quality/honesty rules. Motion, layout and structure come from each video's content. If
someone watched three Glow Keyword videos back to back, they should recognise the brand but never be able to predict
the next cut.

## Contents
1. Read the content first · 2. Decision menus · 3. Content → choice mapping · 4. Anti-repetition rules ·
5. Video log · 6. Worked contrast

## 1. Read the content first (before choosing any motion)
Write a short "edit brief" for yourself, 5–8 lines, after transcribing:
- **Topic type:** problem→solution tutorial, listicle/tips, story/testimony-style narration, comparison/before-after,
  myth-busting, announcement/offer, reaction/opinion.
- **Presenter energy per section:** frustrated, explaining, excited, calm, pointing, holding a prop. Big gestures
  need space, so don't cover the hands. A static presenter needs more graphic motion.
- **Where the value is:** the moments where showing beats telling. Those get the big layouts. Chatty parts stay on
  the face.
- **Rhythm of speech:** fast talkers → fewer, bolder captions. Slow/deliberate → word-by-word builds.
- **Footage:** number of shots, framing (close/wide/low-angle), room colour, how much empty space and where.
- **Real assets available:** screenshots, product shots, the user's own images. These change what can be shown
  honestly.
Then choose from the menus below to fit that brief.

## 2. Decision menus (pick per video; none is the default)

**Hook mechanic (first 2–4 s)**
- A. Frame shrinks in steps on black, graphics fill the freed space (used: Jago Prompt).
- B. Whip-zoom punch into the face + one giant heavy word slammed over it, then snap back.
- C. Split screen: top half the problem visual (cards, screenshot, "before"), bottom half the presenter; merge on
  the answer.
- D. Freeze-frame on the first frame + question text, then play/unfreeze on the first stressed word.
- E. Hard-cut montage of 3–4 fast graphic cards (0.3 s each) before the presenter appears.
- F. Letterbox/tilt: frame rotated −4°, pushes to 0° on the key word, blue light-leak sweep.

**Explainer layout (how the talking head coexists with graphics)**
- A. Cut-out presenter in a bottom corner + card on top (used).
- B. Presenter in a rounded "phone/window" frame that slides aside; graphic occupies the rest.
- C. Full-screen graphic with presenter picture-in-picture circle (top-left or bottom-left).
- D. Presenter stays full frame, blurred 12 px + darkened; graphic floats over the middle; unblur when back to face.
- E. Horizontal split (graphic top 55 %, presenter bottom 45 %, soft blue divider).
- F. Presenter keeps talking full-frame; small graphic chips orbit/stack beside the head (low-density info).
Use at most 2 different explainer layouts per video, and give each a clear job (e.g. steps vs results).

**Transitions (choose 2–3 families per video, don't use all)**
- white/blue flash · zoom-blur push · whip pan with motion blur · RGB glitch cut · shape wipe (rounded rectangle or
  circle iris in brand blue) · light-leak sweep · card flip · "screen crack" split · match-cut on a gesture
  (hand swipe → graphic slides the same way).

**Caption placement pattern**
- Chest-level centre build (used) · side words left/right at eye line (used) · stacked top-left column ·
  words attached to the gesture (appear where the hand points) · lower-third bar in brand blue for long lists.

**Graphic metaphors**: choose the ones that make *this* explanation clearest.
- Cards: photo/polaroid cards, step card, template/prompt card, stats card.
- UI mock-ups: chat bubbles, checklist ticking, progress bar/meter, timeline/roadmap.
- Comparisons: before/after slider, split compare with ✓/✗, counter/number roll-up.
- Other: flowchart arrows, zoom-into-screenshot with highlight ring, stamp/badge, map pins, calendar.

**CTA end-card layout**
- Stacked heavy lines + comment-box mock (used) · presenter stays live with the CTA as a lower-third card ·
  big 3D keyword centre with a pointer/arrow to the comment icon · countdown-free "save & comment" pair.

**Music variation** (keep the mix numbers): tempo 120–150 BPM, key and progression change per video. Choose drums
by mood: trap-pop (default), lo-fi house for calm tutorials, phonk-lite for bold claims. Place the drop on the
section that carries the value, not always the offer.

## 3. Content → choice mapping (starting points, not rules)
| Content | Good fits |
|---|---|
| Step-by-step how-to | explainer A/B/E, numbered step cards, cursor/typing, checklist |
| Listicle / "3 tips" | hook E, full-screen number reveals (heavy numerals), layout F chips, counter |
| Problem → solution | hook A/C, before/after slider, ✗→✓ flip |
| Story / personal experience | hook D, mostly face (layout F/D), timeline graphic, softer transitions (light-leak, zoom-blur) |
| Comparison (tool vs tool, old vs new) | split screen (hook C / layout E), ✓/✗ table cards |
| Offer / product (client course portal, tutorial) | real screenshots with highlight rings, template card, chips, stamp |
| Myth-busting | glitch transitions, big ✗ stamp, "SEBENARNYA…" reveal on blue box |
| Energetic presenter, big gestures | fewer overlays, match-cuts on gestures, captions follow the hands |
| Calm presenter, static | more graphic motion, layouts B/C, slow push + parallax cards |

## 4. Anti-repetition rules
- Before choosing, read the video log (§5). Do not reuse the previous video's hook mechanic, explainer layout or CTA
  layout unless the content clearly calls for it. If you do reuse one, change its choreography (direction, timing,
  graphic).
- Within one video, avoid the same entrance on consecutive captions. Rotate blur-in, pop, slide, smear and write-on,
  so the rhythm feels designed.
- Keep hero-word slams (heavy RGB) to 3–5 per video and flashes to ≤ 6. Scarcity keeps them punchy.
- Vary box/script placement, rotation (−8…+6°) and size between sections.
- Signature elements that should appear in every video (brand continuity) are only these: the brand blue highlight
  box, at least one neon-blue script accent, one heavy RGB word, the glow grade and the CTA keyword style.

## 5. Video log
Append one entry per finished video to `work/glow-keyword-video-log.md` at the repo root (create it if missing;
`work/` never goes to git). If an older log exists, read that too. The entry format:
```
## <date> · <video name> · <topic type>
hook: … · explainer: … · transitions: … · captions: … · metaphors: … · CTA: … · music: <BPM/key/mood>
```

Entries so far (do not repeat their hooks, layouts or CTAs):
- 2026-09-27 · client Jago Prompt remake · problem→solution tutorial. hook A (frame shrinks on black + swapping
  polaroid face cards + "?") · explainer A (cut-out bottom-left + step card; offer: cut-out bottom-right + chips +
  template card) · transitions: flash, zoom-blur, RGB glitch · captions: chest-centre builds + eye-line side words ·
  CTA: stacked heavy lines + comment-box mock on the blurred freeze · music 144 BPM trap-pop, Am–F–C–G.
- 2026-09-27 · B04 Workflow demo · step-by-step workflow tutorial. hook B (whip-zoom punch + IKLAN slam) ·
  explainer E (horizontal split, b-roll top / presenter bottom) + D (blurred presenter + roadmap) · transitions:
  vertical whip-push, horizontal whip, blue iris, light-leak into the end card · CTA: end card "Tutorial SENI VIDEO
  CONVERT" with CONVERT in the CTA-keyword style · music 132 BPM house, Em–C–G–D.

## 6. Worked contrast (same identity, different edits)
- *Jago Prompt* (problem→solution tutorial): hook A, explainer A + E-style hub layout, flash/zoom-blur/RGB,
  polaroid/step/grid/template cards, stacked CTA, 144 BPM trap-pop Am.
- A hypothetical *"3 kesilapan buat video AI"* (listicle): hook E (3 fast cards), big heavy numerals 1/2/3
  full-screen with a blue box under each, layout F chips beside the head, whip-pan transitions, ✗→✓ stamps,
  CTA as a lower-third with the presenter live, 128 BPM lo-fi house.
