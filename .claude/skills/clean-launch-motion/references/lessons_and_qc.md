# Lessons, honesty rules and QC

## User feedback history (Belajar AI, 27 Sep 2026)
- **v1 → rejected points:**
  - "Tak perlu ada link website sampai macam ni." Remove large URL blocks; the button plus the VO "klik link website" is enough.
  - The VO was "tak smooth, clarity kurang, ada part sangkut". The cause was one long take at speed 1.0 with silence inserted inside speech.
  - "Pace motion ni tak sama standard reference." v1 had slow 0.5–1.2 s entrances, long static holds and blur-dissolve transitions.
- **v2 → approved direction:** VO regenerated line by line at speed 1.10 with a clarity chain. The camera always moves, with step zooms, 0.3 s zoom-through transitions, fast entrances, motion blur and a visual beat every ~1–1.5 s. The runtime dropped from 56 s to 46 s.
- **v2b / v2c:** the user edited on-screen copy ("ikut step je", button "Panduan Zero to Expert") and asked for a real playlist screenshot as a "belajar dengan client" teaser. The playlist has 15+ videos, so it scrolls with a fade and a count chip.
- **Final:** "Aku suka motion ni."

## Failure modes already hit (and the fix)
| Symptom | Fix |
|---|---|
| Headline cut off at the frame edges when the camera zooms | Default `data-max` 880 (auto-fit); fewer step zooms in scenes with long lines |
| Incoming word overlaps the previous one ("jTak", "gambarrujukan") | Slot opens first (−0.1 s), glyphs blur in after (+0.06 s), left-anchored in the slot (built into `headline()`) |
| Word spacing wrong ("buatscene") | Slots are CSS grid `0fr → 1fr` around the real glyphs, so spacing is the browser's own (built in) |
| Lines overlap when a long line wraps | Force breaks with `class="br"`; keep each line ≤ 880 px |
| Labels of successive highlights collide | Fade earlier labels (`labelOpacity`) when the next highlight lands |
| Zoomed image slides under the headline or chip | Keep zoom keys where the image's top stays below ~y 430; place chips under the headline, not over the image |
| Toast or feedback rendered off-screen inside a tilted phone | Place feedback relative to the pressed control, inside the visible part of the screen |
| Silence inserted inside a word ("storyboar-d", "s|usun") | Never edit inside a take: generate per line and join chunks at their natural silences (`build_vo.py`) |
| Sticky app header covering a captured card | Hide or make the sticky element static in the throwaway capture copy only |
| Outgoing scene ghosting through the next one | The fade must reach 0 inside the same tween at end + 0.1 s (`scene()` does it); a zero-length `set` loses to a still-running fade |
| Phone sits lower / flatter than designed | `transformPerspective` projects from the element's own origin; pass `vp` to `poseTo` so the vanishing point is the frame centre |
| A tilted plane looks soft after its entrance | A `filter` left on it (even `blur(0px)`); every helper clears it with `filter: none` |
| Phone or video renders black | A `transform-style: preserve-3d` stage; use per-element `transformPerspective` only |
| Element invisible until its tween starts, or flashes | Two `fromTo` on one property both rendering at build: give the later one `immediateRender: false` |

## Honesty and content rules
- Use real material wherever possible. Screenshots come from **local copies** captured headlessly. Never mutate live apps, submit forms, join groups or change account state.
- Label anything staged or illustrative on screen: "CONTOH", "Contoh edit", "Paparan contoh", "Contoh video · dari gambar tadi". Don't fabricate conversations, testimonials, member details, results, counts or UI states that the app can't produce.
- No price, discount or income claims unless the user supplies them for that video. No guaranteed speed, income, sales or zero-effort claims.
- Show no private or access links (invite links, course portals, private URLs). Check screenshots for affiliate commission amounts, prices and "student only" text before using them.
- Keep the CTA and brand invitation in the final scene unless the brief says otherwise.
- Don't embed reference-ad footage, VO, music or branding. Don't use Google, LangEase or Zelios marks.
- Third-party brand marks visible inside authentic screenshots (e.g. a Maggi pack) should be flagged to the user.
- Never claim "100% identical" to a reference. Say what was matched and what differs.

## QC checklist (before handing over)
1. Run `npx hyperframes snapshot hf --at …` or `qc_sheet.py` on: the whole ad at a 1–1.5 s step, every cut ±0.3 s, and every headline mid-entrance. Look for overlaps, clipping at the frame edge under zoom, unreadable text (<26 px), placeholder text left in, and wrong assets.
2. VO: `build_vo.py` prints `text==script: True`. Check the chunk selection scores (no internal pauses except scripted ones).
3. Sync: cross-correlate the VO master against the final mix; lag should be 0 ms.
4. Levels: final −14 LUFS ±0.5, peak ≤ −1.3 dBFS. The longest near-silence (< −50 dB, 10 ms windows) should be under ~0.35 s.
5. Specs: 1080×1920, 30 fps CFR, H.264 High yuv420p BT.709 (tagged), AAC-LC 48 kHz stereo.
6. Copy: every on-screen word matches the user's wording and spelling. The CTA label is exact. There is no URL text unless requested.
7. State the checks not performed: human listening (you can't hear audio), in-app platform preview, and licence confirmations (ElevenLabs plan commercial rights for the student's own account).
