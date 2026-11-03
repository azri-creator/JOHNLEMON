# Motion vocabulary: devices and when to use them

Pick devices that *visualise what the VO says at that moment*. A scene usually combines one headline device, one
object device (phone, sheet, cards, UI) and one or two beat devices (step zoom, highlight, tap). Code references
point to `template/scripts/lib.js` (helpers), the starter scenes in `template/scripts/scenes/`.

## Type
1. **Re-centring blur headline** (`headline(id)` on a `<div class="hl">` of `<span>` words)
   - Each word's slot widens as it arrives, so the line glides back to centre (the reference's "Turn" → "Turn Books").
   - Anchor each word to its spoken word: `<span data-at="hook:0">` or `data-at="video#1"` (default offset −0.1 s; `@-0.04` overrides).
   - Use `class="br"` to start a new line. Colour 1–2 key words `class="blue"` (or `royal`).
2. **Accumulating phrase:** swap the headline on sentence changes ("Mula yang simple dulu." → "1 produk." → "1 produk. 1 mesej."). Give the old phrase `data-out` about 0.26 s before the new one lands.
3. **Hook lift:** line 1 scales to 0.8 and lifts 110 px as line 2 lands (starter `10_hook.html`). Pair it with a thin **progress bar that fills slowly and stalls** for "slow/stuck" feelings.

## Camera
4. **Cam drift + step zoom** (`cam(S, …)` on the scene's `#key-cam` / `#key-step` wrappers): every scene. Put steps on the 2–3 strongest words.
5. **Pan across an image** (`camKeys(el, w, h, keys)` on a fixed-size layer): the camera travels to the detail being named. In the example, the product sheet pans to packaging → label → silhouette with highlights (example `30_ref.html`). Add `mblur` for each pan move.
6. **Zoom into a panel:** a full storyboard/grid scales until one panel fills a card window, then that panel crop cross-fades in (Remotion-era Belajar AI S5; not in the HyperFrames example yet). Use it for "take this one and look closer".
7. **Push-to-detail inside a card:** an inner `camKeys` scale of ~1.2 onto the object being checked, then a pull back.

## Objects
8. **Angled phone rise** (`.phone` with `--pw`, tilted by `poseTo` + `vp`): the phone rises from below the frame over 0.7 s, gets motion blur from `mblur`, floats gently, and its bottom stays cropped. Punch it in (scale +8%, glow ring on the content) on the keyword.
9. **Whip-in phone** (Remotion-era Belajar AI S6): the phone enters from the side with rotateY −40°→−15°. It can later straighten and zoom to 1.2 around a UI detail. Scroll the screen content with `mblur`.
10. **Perspective sheet:** a big landscape image arrives in steep perspective (rotateX 50°→16°, scale 1.5→1) and flattens when details matter.
11. **Tilted floating cards** (`flyIn` on `.gat > .fly > .flt`, starter `30_cards.html`): 2–4 cards fly in from different edges with backOut, ±6–7° tilt and a gentle float, arranged around a centred phrase (the reference's 19 s look). One card per spoken item.
12. **Gather into one:** cards converge to their places in a board, grid or storyboard (0.5 s) as the board rises in. Use it for "susun / combine / system".
13. **Ring → check → confetti** (`ringCheck`, `confetti`): the ring draws 0.5 s, the check draws 0.25 s, then 20 restrained confetti pieces. Use it for "done / okay / verified". Keep it editorial: never imply an automated guarantee.
14. **Circle → rounded square → phone morph:** width, height and radius interpolate over 0.5 s, and video fades in inside. Use it for "now turn it into…".
15. **UI interaction:** the cursor (`tap(...)`) moves in (0.3–0.4 s), presses (scale 0.88 for 0.1 s) with a ripple, and the real app feedback appears (toast, state change). Use real captures of local copies; stage only what is labelled.
16. **Staged control overlay:** for example a replay ↺ button with a scrubber over a real tutorial card. Label it "Paparan contoh".
17. **List reveal with scroll** (Remotion-era Belajar AI CTA teaser): rows of a real list slide in one by one on "satu-satu". A window then scrolls slowly with a bottom fade and a count chip (e.g. "15+ video tutorial") when the list continues beyond what's shown. Never invent the missing rows.

## Finale
18. **Sparkle flight** (`sparkleFlight`): a four-point blue sparkle flies a cubic curve with a soft dotted trail (0.7 s) and lands on the top-right corner of the logo, then twinkles. Soft blurred background trails draw across the stage.
19. **Minimal end card:** logo → tagline (user's words) → gradient button (user's label) → cursor tap on "klik…" → hold for 3.5 s. An optional teaser element (list or card) can sit between tagline and button if the user asks. Show no URL text unless the user explicitly wants it; the user removed a URL block once.

## Transitions
20. **Zoom-through** (built into `scene()`, automatic between scenes): the outgoing scene pushes past camera while the incoming one settles. A whoosh fires automatically at every cut.
21. **Match moves inside a scene:** the phone slides aside while a card swings in; cards fly back while a new card swoops up. These count as beats and keep the pace without hard cuts.
