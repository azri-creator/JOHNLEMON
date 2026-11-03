# PiP Explainer Style: scene playbook (varies per video)

The identity is locked (style_spec.md). **What the graphics show is chosen fresh from what the presenter says.**
Visualise the sentence being spoken, not a generic topic. The Bisnes Baru scenes in `template/scripts/scenes.py`
are examples of the *grammar*. Reuse the kit pieces (`kit.py`: panel, title, chip, card, slam, tick, icons, shakes),
not the choreography.

## 1. Edit brief (write this before building)
1. **Beat map:** list each sentence with its timeline start (from `data/edl.json` words), then tag it Q (question),
   P (punchline), L (list/steps), E (example), C (contrast), R (reflection) or T (takeaway).
2. **Layout per beat:** Q/P/R go FULL (plus a slam on the key word). L/E/C go PIP (plus a scene). The hook starts FULL and
   goes PIP on the first key noun.
3. **One scene per idea** (3–8 s). A long explanation becomes 2–3 scenes with FULL breaks between them.
4. Pick metaphors from §2 that fit the words; avoid repeating the last video's (see the video log).
5. Honesty check (§4).

## 2. Scene menu (✓ = used in Bisnes Baru Nak AI, function name in scenes.py)
| Content said | Scene ideas |
|---|---|
| Big claim / number ("100% AI") | ✓ `hook`: fast counter + shake + word slam · stamp over a grid · meter filling |
| Several examples ("video, gambar, poster") | ✓ `hook`: fanned cards that land one per word, the last one zooms · carousel · stack |
| N mechanisms / stages | ✓ `mekanisme` / `funnel()`: layers filled per word (last one yellow = most important) · ladder · stairs · pyramid · timeline |
| Sources / channels | ✓ `sumber`: platform chips → dashed flow lines with moving dots → centre object · map pins · pipes |
| "X has many parts" | ✓ `pecahan`: a block that shatters into tiles, then merges into the 2 biggest · pie that splits · tree |
| A vs B | ✓ `pecahan`: two tall cards side by side, each highlighted on its word · split screen · scale/balance |
| "Why people buy / trust" | ✓ `percaya`: shield + checklist rows · handshake · rating stars (no invented numbers) |
| Social proof on FYP | ✓ `fyp`: phone mock with a clip + context label + ↑ badges (no numbers) · feed scroll |
| "X only boosts Y" | ✓ `boost`: foundation block + booster block + meter · rocket · amplifier |
| Action steps | ✓ `tindakan`: 3 numbered row cards with ticks (thumbnail/icon) · checklist · roadmap |
| Tech/UI ("chatbot") | ✓ `chatbot`: chat window + typing dots + notification toast (pattern interrupt: cyan flash) · app mock |
| Missing plan / gap | ✓ `blueprint`: sheet with an incomplete flow (dashed "?" nodes) + "TAK ADA" stamp · puzzle missing a piece |
| Metaphor ("buih di lautan") | ✓ `buih`: sea waves + content cards turning into bubbles that pop · the literal metaphor, abstracted |
| Question to the viewer | ✓ `full_overlays`: FULL + yellow-box slam ("DAH CLEAR?", "TRAFIK = ?") |
| Story / mentor | ✓ `full_overlays`: FULL + quote-glyph slam ("PESAN MENTOR") and a music dip |

## 3. Assets
- B-roll from the student's own earlier work or files in `input/` (set `BROLL_DIR`, edit `CLIPS` / `STILLS` in
  `prep_footage.py`). Preview it first and use only what fits. Skip anything showing a real third-party brand.
- The presenter's own frames can stand for "real content" (label: "rakaman sendiri").
- Icons: `kit.py` `ICONS` has line icons (eye, cart, shield, box, cam, chart, quote, bot, up, rocket). Add new ones there.
- Platform names are text chips with a coloured dot, not trademark logos.

## 4. Honesty rules
- AI examples are labelled "Contoh visual AI" and illustrative UI "Visual contoh". Never present old products or testimonials as proof.
- Never invent numbers (views, conversion, prices). Use arrows or "banyak" instead.
- Keep claims in the speaker's context (e.g. FYP example = "jenama yang **dah ada** trust").
- Never reuse another project's voice-over.

## 5. Video log
Keep a log next to the projects (for example `work/PiP Explainer - video log.md`) and append an entry after each video:
topic, hook mechanic, scenes used, slams, music tempo/key, anything the user changed. Read it before planning the next
video so hooks and metaphors don't repeat.

Log so far:
- **Bisnes Baru Nak AI** (client, Sep 2026, 94 s): hook = "BISNES BARU" slam → "100% AI?" box → 0→100 % counter + fanned AI
  cards. Scenes: funnel ×3, platform flow, shattering tiles, 6-grid + stamp, shield checklist, phone FYP, rocket +
  meter, 3 action rows, chatbot UI, blueprint, sea/bubbles. Music 140 BPM half-time trap-pop, D minor.
