"""PER VIDEO: the PiP graphic panels, the FULL slams and the end card.
These are the "Bisnes Baru Nak AI" scenes: examples of the GRAMMAR (counter + fanned cards, funnel, flow lines,
shattering tiles, checklists, phone mock, meter, chat UI, blueprint, metaphor). For a new video write new scenes from
what the presenter says (references/scene_playbook.md); reuse the kit pieces, not this choreography.

Each scene returns dict(a=start, html=..., js=...). Ids are prefixed per scene and must be unique in the page.
Panel content area: title at y~205, content between y~300 and 1180 (the PiP card starts at 1372, captions at 1296)."""
import os
from kit import C, GLOW_C, GLOW_Y, HF, SHADOW, W, Y, anchor, card, chip, icon, label, noise, shake_js, slam, tick_svg, title
from timing import END_CARD, T, TOTAL


def t(k, d=0.0): return f"{T[k] + d:.4f}"
def n(x): return f"{x:.4f}"


def panel_open(pid): return f'<div id="{pid}" class="layer panel hide"><div id="{pid}_d" class="layer panel">'
PANEL_CLOSE = "</div></div>"
FAINT = dict(color="rgba(255,255,255,0.08)", ink="rgba(255,255,255,0.7)")
YFAINT = dict(color="rgba(255,230,0,0.14)", ink=C["yellow"])


def vid(id_, src, a, dur, b=None, extra=""):
    """muted B-roll clip; starts from its first frame when the card appears (time the video, not its wrapper)"""
    d = min(dur, (b - a) if b else dur)
    return f'<video id="{id_}" class="media" src="assets/{src}" muted playsinline data-start="{a:.3f}" data-duration="{d:.3f}" style="{extra}"></video>'


def img(src, pos="50% 50%"): return f'<img class="media" src="assets/{src}" alt="" style="object-position:{pos}">'


def yoyo(sel, a, b, prop, v0, v1, half, ease="sine.inOut"):
    """finite back-and-forth motion between a and b (seek-safe replacement for sin(t) wobble)"""
    reps = max(0, int((b - a) / half) - 1)
    return (f"tl.fromTo('{sel}', {{ {prop}: {v0} }}, {{ {prop}: {v1}, duration: {half:.3f}, ease: '{ease}', repeat: {reps}, yoyo: true, "
            f"immediateRender: false }}, {a:.4f});")


# =====================================================================================================
# 1 · HOOK: bisnes baru, 100% AI? video / gambar / poster
def hook():
    a, b = T["bisnesBaru"] - 0.05, T["sebelum"] - 0.05
    cards = [("video", 222, -7, "VIDEO", vid("h_v0", "video/ai_xray.mp4", T["video"], 6, b)),
             ("gambar", 540, 0, "GAMBAR", img("img/ai_img_kitchen.jpg")),
             ("poster", 858, 7, "POSTER", img("img/ai_poster_sofa.jpg"))]
    h = [panel_open("hook"), '<div id="h_sh" class="layer">',
         title("h_t1", "Bisnes *baru*"), title("h_t2", "100% *AI* ?"),
         '<div id="h_box" class="layer" style="transform-origin:540px 640px">',
         card("h_card", "left:330px;top:430px;width:420px;height:420px;display:flex;align-items:center;justify-content:center", f'<div id="h_icw"><div id="h_ic">{icon("box", 230, C["cyan"], 3.5)}</div></div>', glow=GLOW_C, cls=""),
         chip("h_chip", 540, 930, "PRODUK BARU", color=C["yellow"], ink=C["navy"], size=40), "</div>",
         '<div id="h_cnt" class="layer hide" style="transform-origin:540px 600px">',
         anchor(540, 640, '<div style="width:760px;height:760px;border-radius:50%;background:radial-gradient(circle, rgba(255,230,0,0.22), rgba(255,230,0,0) 62%)"></div>'),
         anchor(540, 600, f'<div id="h_num" class="heavy" style="font-size:290px;color:{C["yellow"]};text-shadow:{GLOW_Y};white-space:nowrap;letter-spacing:-0.03em">0%</div>'),
         anchor(540, 880, f'<div id="h_ai" class="heavy hide" style="font-size:210px;color:#fff;text-shadow:{SHADOW}">AI?</div>'), "</div>"]
    for i, (k, x, rot, lab, el) in enumerate(cards):
        bc = C["yellow"] if i == 2 else "rgba(255,255,255,0.85)"
        h.append(f'<div id="h_c{i}" class="hide" style="position:absolute;left:{x - 140}px;top:390px;width:280px;height:498px">'
                 f'<div id="h_c{i}i" style="position:absolute;inset:0;border-radius:26px;overflow:hidden;border:3px solid rgba(255,255,255,0.85);box-shadow:0 30px 60px rgba(0,0,0,0.6)">'
                 f'{el}<div class="aitag">AI</div></div></div>')
        h.append(label(f"h_l{i}", x, 955, f"{lab} {Y('AI')}"))
    h += [chip("h_note", 540, 1060, "Contoh visual AI", size=26, **FAINT), "</div>", PANEL_CLOSE]
    j = [f"panel('hook', {n(a)}, {n(b)});",
         f"title('h_t1', {n(a + 0.05)}); tl.set('#h_t1', {{ opacity: 0 }}, {t('video', -0.02)}); title('h_t2', {t('video')});",
         f"gsap.set('#h_ic', {{ scale: 0.6 }}); tl.fromTo('#h_ic', {{ scale: 0.6 }}, {{ scale: 1, duration: 0.4, ease: E.back, immediateRender: false }}, {n(a + 0.1)});",
         yoyo("#h_icw", a, T["ai100"], "rotation", -3, 3, 1.571),
         f"pop('h_chip', {n(a + 0.3)});",
         f"tl.to('#h_box', {{ opacity: 0, scale: 0.6, duration: 0.2, ease: E.in }}, {t('ai100', -0.05)});",
         # counter 0 -> 100 % fast, lands with a shake
         f"tl.set('#h_cnt', {{ opacity: 1 }}, {t('ai100')});",
         f"tl.fromTo('#h_num', {{ scale: 1.5 }}, {{ scale: 1, duration: 0.25, ease: E.back, immediateRender: false }}, {t('ai100')});",
         f"counter('h_num', {t('ai100')}, 0.3, 100, '%');",
         f"tl.fromTo('#h_ai', {{ scale: 2.2, rotation: -8 }}, {{ scale: 1, duration: 0.16, ease: E.back, immediateRender: false }}, {t('pakaiAI')});",
         f"tl.to('#h_ai', {{ rotation: -3, duration: 0.2, ease: E.out }}, {t('pakaiAI')});",
         f"tl.fromTo('#h_ai', {{ opacity: 0 }}, {{ opacity: 1, duration: 0.08, ease: 'none', immediateRender: false }}, {t('pakaiAI')});",
         f"tl.to('#h_cnt', {{ opacity: 0, scale: 0.7, y: -200, duration: 0.2, ease: E.in }}, {t('video', -0.08)});",
         shake_js("#h_sh", T["ai100"] + 0.28, 0.3, 14, 2), shake_js("#h_sh", T["pakaiAI"], 0.2, 9, 4), shake_js("#h_sh", T["poster"], 0.25, 10, 6)]
    for i, (k, x, rot, lab, el) in enumerate(cards):
        j += [f"tl.fromTo('#h_c{i}', {{ y: 420, rotation: 0, scale: 0.7 }}, {{ y: 0, rotation: {rot}, scale: 1, duration: 0.28, ease: E.back, immediateRender: false }}, {t(k, -0.05)});",
              f"tl.fromTo('#h_c{i}', {{ opacity: 0 }}, {{ opacity: 1, duration: 0.09, ease: 'none', immediateRender: false }}, {t(k, -0.05)});",
              f"tl.fromTo('#h_l{i}', {{ opacity: 0 }}, {{ opacity: 1, duration: 0.14, ease: 'none', immediateRender: false }}, {t(k, -0.05)});",
              f"tl.to('#h_c{i}i', {{ scale: {1.16 if i == 2 else 0.9}, duration: 0.3, ease: E.out }}, {t('poster')});"]
        if i == 2: j.append(f"tl.set('#h_c2i', {{ borderColor: '{C['yellow']}' }}, {t('poster')});")
        else: j.append(f"tl.set('#h_c{i}i', {{ filter: 'brightness(0.6)' }}, {t('poster')});")
    j.append(f"fadeIn('h_note', {t('video', 0.4)});")
    return dict(a=a, html="\n".join(h), js="\n".join(j))


# =====================================================================================================
# 2 · 3 MEKANISME: corong trafik -> konten -> closing (= conversion). The funnel is reused in 3 panels.
LAYERS = [(330, 520, 900, 760, "TRAFIK", "trafik", C["cyan"]), (545, 735, 740, 600, "KONTEN", "konten", C["blue"]),
          (760, 950, 580, 440, "CLOSING", "closing", C["yellow"])]


def funnel(p, dy=0):
    h = [f'<div class="layer" style="top:{dy}px">', f'<svg width="{W}" height="1100" style="position:absolute;left:0;top:0;overflow:visible">']
    for i, (y0, y1, w0, w1, *_r) in enumerate(LAYERS):
        d = f"M{540 - w0 / 2} {y0} L{540 + w0 / 2} {y0} L{540 + w1 / 2} {y1} L{540 - w1 / 2} {y1} Z"
        h.append(f'<g id="{p}g{i}"><path id="{p}L{i}" d="{d}" fill="{LAYERS[i][6]}" fill-opacity="0" stroke="{C["cyan"]}" stroke-width="4" '
                 f'stroke-dasharray="2600" stroke-dashoffset="2600"/></g>')
    h.append("</svg>")
    for i, (y0, y1, w0, w1, name, k, fill) in enumerate(LAYERS):
        ink = "#fff" if i == 1 else C["navy"]
        badge = "rgba(255,255,255,0.2)" if i == 1 else "rgba(6,19,41,0.2)"
        h.append(anchor(540, (y0 + y1) / 2, f'<div id="{p}n{i}" class="heavy hide" style="font-size:{76 if i == 2 else 70}px;color:{ink};white-space:nowrap;display:flex;align-items:center;gap:18px">'
                 f'<span style="font-family:Inter;font-weight:900;font-size:34px;background:{badge};border-radius:999px;width:54px;height:54px;display:inline-flex;align-items:center;justify-content:center">{i + 1}</span>{name}</div>'))
    for i in (0, 1):
        y0, y1, w0, w1, *_r = LAYERS[i]
        h.append(f'<div id="{p}ar{i}" class="hide" style="position:absolute;left:{540 + w1 / 2 + 40}px;top:{y1 - 30}px"><svg width="60" height="80">'
                 f'<path d="M10 10 C40 20 40 50 20 70 M20 70 L14 52 M20 70 L36 62" stroke="{C["cyan"]}" stroke-width="4" fill="none" stroke-linecap="round"/></svg></div>')
    h.append(chip(f"{p}pp", 540, 1035, "PALING PENTING", size=32, **YFAINT))
    h.append(anchor(540, 1130, f'<div id="{p}cv" class="lbl hide" style="font-size:48px">CLOSING <span class="serif" style="font-size:58px;color:{C["cyan"]}">atau</span> {Y("CONVERSION")}</div>'))
    h.append("</div>")
    j = []
    for i in range(3):
        j.append(f"draw('{p}L{i}', {t('corong')}, 0.7, 2600);")
        at = T[LAYERS[i][5]]
        j.append(f"tl.fromTo('#{p}L{i}', {{ attr: {{ 'fill-opacity': 0 }} }}, {{ attr: {{ 'fill-opacity': 0.9 }}, duration: {0.25 if i == 2 else 0.35}, ease: E.out, immediateRender: false }}, {n(at)});")
        j.append(f"pop('{p}n{i}', {n(at - 0.02)}, 0.3, 0.5);")
    for i in (0, 1):
        j.append(f"fadeIn('{p}ar{i}', {n(T[LAYERS[i + 1][5]])});")
    # 3rd layer pulses (yellow stroke) from "ketiga" until "closing"; then the others dim and closing glows
    j.append(f"tl.set('#{p}L2', {{ attr: {{ stroke: '{C['yellow']}' }} }}, {t('ketiga')});")
    j.append(yoyo(f"#{p}L2", T["ketiga"], T["closing"], "attr", "{ 'stroke-width': 4 }", "{ 'stroke-width': 7 }", 0.224))
    j.append(f"tl.set('#{p}L2', {{ attr: {{ 'stroke-width': 4 }}, filter: 'drop-shadow(0 0 22px rgba(255,230,0,0.7))' }}, {t('closing')});")
    j.append(f"tl.to(['#{p}g0', '#{p}g1'], {{ opacity: 0.4, duration: 0.15 }}, {t('closing')});")
    j.append(f"tl.to(['#{p}n0', '#{p}n1'], {{ opacity: 0.45, duration: 0.15 }}, {t('closing', 0.3)});")
    j.append(f"tl.to(['#{p}ar0', '#{p}ar1'], {{ opacity: 0.4, duration: 0.15 }}, {t('closing', 0.35)});")
    j.append(f"pop('{p}pp', {t('closing', 0.15)});")
    j.append(f"pop('{p}cv', {t('conversion')}, 0.3, 0.5);")
    return "\n".join(h), "\n".join(j)


def mekanisme():
    a, b = T["tiga"] - 0.05, T["paling"] - 0.1
    a2, b2 = T["closing"] + 0.02, T["trafikQ"] - 0.05
    f1h, f1j = funnel("f1_"); f2h, f2j = funnel("f2_")
    h = [panel_open("mek"),
         '<div id="m_intro" class="layer" style="transform-origin:540px 600px">',
         anchor(540, 560, f'<div id="m_3" class="heavy" style="font-size:400px;color:{C["yellow"]};text-shadow:{GLOW_Y};line-height:1">3</div>'),
         anchor(540, 830, f'<div id="m_mek" class="heavy hide" style="font-size:104px;color:#fff;text-shadow:{SHADOW}">MEKANISME</div>'),
         anchor(540, 975, f'<div id="m_waj" class="heavy hide" style="font-size:96px;background:{C["yellow"]};color:{C["navy"]};padding:6px 34px 12px;border-radius:16px;box-shadow:{GLOW_Y}">WAJIB</div>'),
         "</div>", title("m_t", "3 Mekanisme *Wajib*"), f'<div id="m_fun" class="layer hide">{f1h}</div>', PANEL_CLOSE,
         panel_open("mek2"), title("m2_t", "Ibarat *corong*"), f2h, PANEL_CLOSE]
    j = [f"panel('mek', {n(a)}, {n(b)});",
         f"tl.fromTo('#m_3', {{ scale: 1.8 }}, {{ scale: 1, duration: 0.3, ease: E.back, immediateRender: false }}, {n(a)});",
         f"pop('m_mek', {t('tiga', 0.2)}, 0.3, 0.7);", f"pop('m_waj', {t('wajib')}, 0.22, 1.5);",
         f"tl.to('#m_intro', {{ opacity: 0, scale: 0.65, y: -260, duration: 0.25, ease: E.in }}, {t('corong', -0.12)});",
         f"title('m_t', {t('corong', -0.1)});", f"tl.set('#m_fun', {{ opacity: 1 }}, {t('corong')});", f1j,
         f"panel('mek2', {n(a2)}, {n(b2)}, 1.08);", f"title('m2_t', {n(a2)});", f2j]
    return dict(a=a, html="\n".join(h), js="\n".join(j))


# =====================================================================================================
# 2b · SUMBER TRAFIK: TikTok / Facebook / Instagram -> produk (platform names as text chips, no logos)
PLATFORMS = [("TikTok", "tiktok", 200, "#25F4EE"), ("Facebook", "facebook", 540, "#1877F2"), ("Instagram", "instagram", 880, "#E1306C")]


def sumber():
    a, b = T["sumber"] - 0.05, T["untukMenarik"] - 0.05
    h = [panel_open("sum"), title("s_t", "Sumber *trafik*"), label("s_q", 540, 440, f"Orang tengok dari {Y('mana?')}", 50),
         f'<svg width="{W}" height="1200" style="position:absolute;left:0;top:0">']
    for i, (nm, k, x, dot) in enumerate(PLATFORMS):
        h.append(f'<line id="s_ln{i}" x1="{x}" y1="520" x2="{x}" y2="520" stroke="{C["cyan"]}" stroke-width="4" stroke-dasharray="12 12" opacity="0"/>')
    h.append("</svg>")
    for i, (nm, k, x, dot) in enumerate(PLATFORMS):
        h.append(card(f"s_p{i}", f"left:{x - 150}px;top:400px;width:300px;height:120px;display:flex;align-items:center;justify-content:center;gap:14px",
                      f'<div style="width:22px;height:22px;border-radius:50%;background:{dot};box-shadow:0 0 14px {dot}"></div><span style="font-weight:800;font-size:42px">{nm}</span>',
                      border="rgba(255,255,255,0.3)"))
        h.append(f'<div id="s_dw{i}" class="layer hide">' + "".join(
            f'<div id="s_d{i}_{q}" style="position:absolute;left:{x - 9}px;top:511px;width:18px;height:18px;border-radius:50%;background:{C["yellow"]};box-shadow:{GLOW_Y};opacity:0"></div>'
            for q in range(4)) + "</div>")
    h.append(f'<div id="s_prw" style="position:absolute;left:390px;top:740px;width:300px;height:300px">'
             + card("s_pr", "left:0;top:0;width:300px;height:300px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:10px",
                    icon("box", 150, C["cyan"], 3.5) + '<span style="font-weight:800;font-size:34px">Produk awak</span>', border=C["cyan"], glow=GLOW_C) + "</div>")
    h += [chip("s_eq", 540, 1120, "= TRAFIK", size=36), PANEL_CLOSE]
    j = [f"panel('sum', {n(a)}, {n(b)});", f"title('s_t', {n(a)});",
         f"fadeIn('s_q', {t('orangTengok', -0.1)}); tl.set('#s_q', {{ opacity: 0 }}, {t('tiktok')});",
         f"popBlur('s_pr', {n(a + 0.1)}, 0.4, 0.5);", yoyo("#s_prw", T["tiktok"], b, "scale", 0.96, 1.04, 0.5236)]
    for i, (nm, k, x, dot) in enumerate(PLATFORMS):
        at = T[k]; P = 1 / 0.9
        j += [f"pop('s_p{i}', {n(at - 0.05)}, 0.3, 0.4);",
              f"tl.set('#s_ln{i}', {{ opacity: 0.8 }}, {n(at + 0.1)});",
              f"tl.fromTo('#s_ln{i}', {{ attr: {{ x2: {x}, y2: 520 }} }}, {{ attr: {{ x2: 540, y2: 790 }}, duration: 0.35, ease: E.io, immediateRender: false }}, {n(at + 0.1)});",
              f"tl.fromTo('#s_ln{i}', {{ strokeDashoffset: 0 }}, {{ strokeDashoffset: {-60 * (b - at):.0f}, duration: {b - at - 0.1:.3f}, ease: 'none', immediateRender: false }}, {n(at + 0.1)});",
              f"tl.set('#s_dw{i}', {{ opacity: 1 }}, {n(at + 0.45)});"]
        for q in range(4):  # traffic dots flowing to the product, phase-shifted by a quarter
            ph = (0.45 * 0.9 + q / 4) % 1
            reps = int((b - at) / P) + 1
            j.append(f"{{ const d = gsap.timeline({{ repeat: {reps} }}); const el = '#s_d{i}_{q}';"
                     f" d.fromTo(el, {{ x: 0, y: 0 }}, {{ x: {540 - x}, y: 270, duration: {P:.4f}, ease: 'none' }}, 0)"
                     f".fromTo(el, {{ opacity: 0 }}, {{ opacity: 1, duration: {P / 2:.4f}, ease: 'sine.out' }}, 0)"
                     f".to(el, {{ opacity: 0, duration: {P / 2:.4f}, ease: 'sine.in' }}, {P / 2:.4f}); tl.add(d, {n(at + 0.45 - ph * P)}); }}")
    j.append(f"pop('s_eq', {t('tiktok', 0.6)});")
    return dict(a=a, html="\n".join(h), js="\n".join(j))


# =====================================================================================================
# 2c · KONTEN: banyak pecahan -> 2 paling besar: video sebenar & video AI
def pecahan():
    a, b = T["dalamKonten"] - 0.05, T["soDekat"]
    ic = [icon("cam", 70, C["yellow"], 4), icon("chart", 64, C["cyan"], 4), icon("quote", 64, C["cyan"], 4)]
    h = [panel_open("pec"), title("p_t1", "Konten ada banyak *pecahan*", size=58), title("p_t2", "Pecahan *paling besar*"),
         '<div id="p_grp" class="layer">',
         card("p_k", "left:240px;top:520px;width:600px;height:240px;display:flex;align-items:center;justify-content:center",
              '<span class="heavy" style="font-size:110px">KONTEN</span>', border=C["cyan"], glow=GLOW_C)]
    for i in range(12):
        col, row = i % 4, i // 4
        x1, y1 = 150 + col * 260, 390 + row * 240
        yel = i % 3 == 0
        h.append(f'<div id="p_tl{i}" class="hide" style="position:absolute;left:{x1 - 100}px;top:{y1 - 85}px;width:200px;height:170px">'
                 f'<div id="p_ti{i}" style="position:absolute;inset:0;border-radius:20px;background:{"rgba(255,230,0,0.18)" if yel else "rgba(0,207,245,0.14)"};'
                 f'border:2px solid {"rgba(255,230,0,0.6)" if yel else C["line"]};display:flex;align-items:center;justify-content:center">{ic[i % 3]}</div></div>')
    h.append("</div>")
    cards = [("pecahanBesar", 0.15, "videoSebenar", 95, img("img/real_content.jpg", "50% 25%"), "rakaman sendiri", f"Video {Y('sebenar')}"),
             ("keduaVideo", 0.0, "videoAI2", 555, vid("p_v1", "video/ai_dispenser.mp4", T["keduaVideo"], 6, b), "contoh visual AI", f"Video {Y('AI')}")]
    for i, (k, dk, hi, x, el, tag, lab) in enumerate(cards):
        h.append(f'<div id="p_c{i}" class="hide" style="position:absolute;left:{x}px;top:340px;width:430px;height:620px">'
                 f'<div id="p_c{i}i" style="position:absolute;inset:0;border-radius:30px;overflow:hidden;border:4px solid rgba(255,255,255,0.6);box-shadow:0 30px 60px rgba(0,0,0,0.6)">{el}'
                 f'<div style="position:absolute;left:16px;top:16px;background:{C["navy"]};color:{C["cyan"]};font-weight:900;font-size:30px;padding:4px 14px;border-radius:10px">0{i + 1}</div>'
                 f'<div style="position:absolute;left:12px;right:12px;bottom:12px;text-align:center;font-weight:700;font-size:20px;background:rgba(6,19,41,0.75);border-radius:8px;padding:3px 0">{tag}</div></div></div>')
        h.append(label(f"p_l{i}", x + 215, 1045, lab, 48))
    h.append(PANEL_CLOSE)
    sp = T["pecahan"] - 0.1
    j = [f"panel('pec', {n(a)}, {n(b)});", f"title('p_t1', {n(a)}); tl.set('#p_t1', {{ opacity: 0 }}, {t('pecahanBesar', -0.05)}); title('p_t2', {t('pecahanBesar', -0.05)});",
         f"popBlur('p_k', {n(a + 0.05)}, 0.35, 0.5); tl.set('#p_k', {{ opacity: 0 }}, {n(sp + 0.01)});"]
    for i in range(12):
        col, row = i % 4, i // 4
        x0, y0 = 240 + (col + 0.5) * 150, 520 + (row + 0.5) * 80
        x1, y1 = 150 + col * 260, 390 + row * 240
        r = (noise(i + 7) - 0.5) * 16
        j += [f"tl.set('#p_tl{i}', {{ opacity: 1, x: {x0 - x1:.1f}, y: {y0 - y1:.1f}, scale: 0.6 }}, {n(sp + 0.01)});",
              f"tl.to('#p_tl{i}', {{ x: 0, y: 0, rotation: {r:.2f}, scale: 1, duration: 0.4, ease: E.back }}, {n(sp + i * 0.03 + 0.012)});"]
    j += [f"tl.to('#p_grp', {{ opacity: 0, duration: 0.3, ease: E.in }}, {t('pecahanBesar', -0.05)});",
          f"tl.to('[id^=p_ti]', {{ scale: 0.5, duration: 0.3, ease: E.in }}, {t('pecahanBesar', -0.05)});"]
    for i, (k, dk, hi, x, el, tag, lab) in enumerate(cards):
        at = T[k] + dk - 0.08
        j += [f"tl.fromTo('#p_c{i}', {{ y: 300, scale: 0.7, rotation: 0 }}, {{ y: 0, scale: 1, rotation: {3 if i else -3}, duration: 0.3, ease: E.back, immediateRender: false }}, {n(at)});",
              f"tl.fromTo(['#p_c{i}', '#p_l{i}'], {{ opacity: 0 }}, {{ opacity: 1, duration: 0.1, ease: 'none', immediateRender: false }}, {n(at)});",
              f"tl.set('#p_c{i}i', {{ borderColor: '{C['yellow']}', boxShadow: '{GLOW_Y}, 0 30px 60px rgba(0,0,0,0.6)' }}, {t(hi, -0.05)});",
              f"tl.to('#p_c{i}i', {{ scale: 1.03, duration: 0.2, ease: E.out }}, {t(hi, -0.05)});"]
    return dict(a=a, html="\n".join(h), js="\n".join(j))


# =====================================================================================================
# 3 · PRODUK BARU, SEMUA KONTEN AI?
GRID = ["video/ai_dispenser.mp4", "img/ai_img_drink.jpg", "img/ai_img_sofa.jpg", "video/ai_fashion.mp4", "img/ai_img_dark.jpg", "img/ai_poster_sofa.jpg"]


def produk_baru():
    a, b = T["soDekat"], T["takBoleh"] - 0.04
    gi = T["semua"] - 0.08
    h = [panel_open("prb"), title("pb_t1", "Produk *baru* launch?"), title("pb_t2", "Semua *konten AI*?"),
         '<div id="pb_box" class="layer" style="transform-origin:540px 650px">',
         card("pb_card", "left:340px;top:440px;width:400px;height:400px;display:flex;align-items:center;justify-content:center", icon("box", 220, C["cyan"], 3.5), glow=GLOW_C, cls=""),
         f'<div id="pb_new" class="heavy hide" style="position:absolute;left:680px;top:420px;background:{C["yellow"]};color:{C["navy"]};font-size:50px;padding:6px 22px 10px;border-radius:12px;box-shadow:{GLOW_Y}">BARU!</div>',
         chip("pb_c", 540, 930, "Belum ada siapa kenal", size=32, color="rgba(255,255,255,0.08)", ink="rgba(255,255,255,0.75)"), "</div>"]
    for i, src in enumerate(GRID):
        col, row = i % 3, i // 3
        x, y = 222 + col * 318, 530 + row * 420
        at = gi + i * 0.07
        el = vid(f"pb_v{i}", src, at, 4, b) if src.endswith(".mp4") else img(src)
        h.append(f'<div id="pb_g{i}" class="hide" style="position:absolute;left:{x - 140}px;top:{y - 190}px;width:280px;height:380px;border-radius:22px;overflow:hidden;'
                 f'border:2px solid rgba(255,255,255,0.7);box-shadow:0 20px 40px rgba(0,0,0,0.5)">{el}<div class="aitag" style="left:10px;top:10px;font-size:24px;padding:3px 10px">AI</div></div>')
    h += [anchor(540, 740, f'<div id="pb_st" class="heavy hide" style="background:{C["yellow"]};color:{C["navy"]};font-size:92px;padding:8px 36px 14px;border-radius:16px;box-shadow:{GLOW_Y}, 0 20px 50px rgba(0,0,0,0.6);white-space:nowrap">100% AI</div>'),
          PANEL_CLOSE]
    j = [f"panel('prb', {n(a)}, {n(b)});", f"title('pb_t1', {n(a)}); tl.set('#pb_t1', {{ opacity: 0 }}, {n(gi)}); title('pb_t2', {n(gi)});",
         f"gsap.set('#pb_new', {{ rotation: 12 }}); pop('pb_new', {t('launch', -0.2)}, 0.3, 0.3);", f"pop('pb_c', {n(a + 0.4)});",
         f"tl.to('#pb_box', {{ opacity: 0, scale: 0.7, duration: 0.2, ease: E.in }}, {n(gi - 0.05)});"]
    for i in range(6):
        j += [f"gsap.set('#pb_g{i}', {{ rotation: {(noise(i + 3) - 0.5) * 6:.2f} }});", f"pop('pb_g{i}', {n(gi + i * 0.07)}, 0.3, 0.4);"]
    j += [f"gsap.set('#pb_st', {{ rotation: -8 }}); pop('pb_st', {n(gi + 0.55)}, 0.22, 2.2);"]
    return dict(a=a, html="\n".join(h), js="\n".join(j))


# =====================================================================================================
# 4 · ORANG DAH PERCAYA (brand + produk)
def percaya():
    a, b = T["orangDah"] - 0.05, T["sebabTu"]
    rows = [("percayaBrand", "Percaya pada brand", 820), ("percayaProduk", "Percaya pada produk", 990)]
    h = [panel_open("pcy"), title("pc_t", "Orang beli sebab *trust*"),
         anchor(540, 530, f'<div id="pc_sh" class="hide" style="filter:drop-shadow(0 0 30px rgba(0,207,245,0.6))">{icon("shield", 300, C["cyan"], 3.2)}</div>'),
         label("pc_l", 540, 715, f"BRAND {Y('TRUST')}", 46)]
    for i, (k, txt, y) in enumerate(rows):
        h.append(card(f"pc_r{i}", f"left:150px;top:{y - 70}px;width:780px;height:140px;display:flex;align-items:center;gap:28px;padding:0 36px",
                      tick_svg(f"pc_k{i}", 76) + f'<span style="font-weight:800;font-size:52px">{txt}</span>'))
    h.append(PANEL_CLOSE)
    j = [f"panel('pcy', {n(a)}, {n(b)});", f"title('pc_t', {n(a)});", f"pop('pc_sh', {n(a + 0.05)}, 0.4, 0.4);", f"fadeIn('pc_l', {n(a + 0.25)});"]
    for i, (k, txt, y) in enumerate(rows):
        j += [f"slideIn('pc_r{i}', {t(k, -0.05)}, {{ x: 600 }});", f"tick('pc_k{i}', {t(k, 0.15)});"]
    return dict(a=a, html="\n".join(h), js="\n".join(j))


# =====================================================================================================
# 5 · FYP: jenama yang DAH ADA trust, konten AI -> view & conversion (no numbers invented)
def fyp():
    a, b = T["sebabTu"], T["brandSendiri"] - 0.05
    phone = (f'<div id="fy_ph" style="position:absolute;left:315px;top:300px;width:450px;height:800px;border-radius:56px;background:#000;padding:14px;'
             f'box-shadow:0 40px 90px rgba(0,0,0,0.7), 0 0 0 3px rgba(255,255,255,0.12)">'
             f'<div style="position:relative;width:100%;height:100%;border-radius:44px;overflow:hidden;background:{C["navy2"]}">{vid("fy_v", "video/ai_drink.mp4", a, 6, b)}'
             f'<div class="layer" style="width:100%;height:100%;background:linear-gradient(180deg, rgba(0,0,0,0.35) 0%, rgba(0,0,0,0) 18%, rgba(0,0,0,0) 65%, rgba(0,0,0,0.6) 100%)"></div>'
             f'<div style="position:absolute;top:30px;width:100%;text-align:center;font-weight:700;font-size:22px;color:rgba(255,255,255,0.75)">Following&nbsp;&nbsp;|&nbsp;&nbsp;'
             f'<span style="color:#fff;border-bottom:3px solid #fff;padding-bottom:4px">For You</span></div>'
             + "".join(f'<div style="position:absolute;right:16px;top:{360 + k * 90}px;width:58px;height:58px;border-radius:50%;background:rgba(255,255,255,0.22)"></div>' for k in range(3))
             + f'<div style="position:absolute;left:20px;bottom:70px;font-weight:800;font-size:24px;display:flex;align-items:center;gap:8px">@jenama_dipercayai'
             f'<span style="width:24px;height:24px;border-radius:50%;background:{C["cyan"]};color:{C["navy"]};font-size:16px;display:inline-flex;align-items:center;justify-content:center">✓</span></div>'
             f'<div style="position:absolute;left:20px;bottom:36px;font-weight:600;font-size:20px;color:rgba(255,255,255,0.85)">#fyp #kontenAI</div>'
             f'<div id="fy_tag" class="hide" style="position:absolute;left:18px;top:72px;background:{C["yellow"]};color:{C["navy"]};font-weight:900;font-size:22px;padding:4px 12px;border-radius:8px">Konten AI</div>'
             f'</div></div>')
    h = [panel_open("fyp"), title("fy_t", "Jenama yang *DAH ADA* trust", size=58), phone]
    badges = [("view", 24, 430, "eye", "View"), ("conv2", 706, 760, "cart", "Conversion")]
    for i, (k, x, y, ic, lab) in enumerate(badges):
        arrows = "".join(f'<div id="fy_b{i}a{q}" class="hide">{icon("up", 40, C["yellow"], 7)}</div>' for q in range(3))
        h.append(f'<div id="fy_bw{i}" style="position:absolute;left:{x}px;top:{y}px;width:350px;height:190px">' + card(
            f"fy_b{i}", "left:0;top:0;width:350px;height:190px;padding:22px;display:flex;flex-direction:column;justify-content:space-between",
            f'<div style="display:flex;align-items:center;gap:14px">{icon(ic, 54, C["yellow"])}<span style="font-weight:800;font-size:36px">{lab}</span></div>'
            f'<div style="display:flex;align-items:center;gap:6px">{arrows}<span class="serif" style="font-size:50px;color:{C["yellow"]};margin-left:8px">banyak</span></div>',
            border=C["yellow"], glow=GLOW_Y) + "</div>")
    h += [chip("fy_c", 540, 1160, "Visual contoh · brand yang sudah dipercayai", size=24, **FAINT), PANEL_CLOSE]
    j = [f"panel('fyp', {n(a)}, {n(b)}, 1.1);", f"title('fy_t', {n(a)});",
         f"tl.fromTo('#fy_ph', {{ y: 500, rotation: 8 }}, {{ y: 0, rotation: 0, duration: 0.45, ease: E.out, immediateRender: false }}, {n(a)});",
         f"fadeIn('fy_tag', {t('gunaAI', -0.05)}, 0.2);", f"fadeIn('fy_c', {n(a + 0.5)});"]
    for i, (k, x, y, ic, lab) in enumerate(badges):
        j += [f"pop('fy_b{i}', {t(k, -0.05)}, 0.3, 0.4);", yoyo(f"#fy_bw{i}", T[k], b, "y", -6, 6, 0.628)]
        for q in range(3):
            j.append(f"tl.fromTo('#fy_b{i}a{q}', {{ y: 30, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.3, ease: E.back, immediateRender: false }}, {t(k, 0.1 + q * 0.08)});")
    return dict(a=a, html="\n".join(h), js="\n".join(j))


# =====================================================================================================
# 6 · VIDEO AI = BOOST keinginan (atas trust yang sedia ada)
def boost():
    a, b = T["videoAI"] - 0.05, T["soKalau"] - 0.05
    h = [panel_open("bst"), title("bo_t", "Video AI = *boost*"),
         card("bo_base", "left:60px;top:820px;width:560px;height:190px;display:flex;align-items:center;gap:22px;padding:0 30px",
              icon("shield", 96, C["cyan"], 4) + f'<div><div class="heavy" style="font-size:56px">BRAND TRUST</div><div class="serif" style="font-size:40px;color:{C["cyan"]}">dah sedia ada</div></div>',
              border=C["cyan"], glow=GLOW_C),
         f'<div id="bo_rk" class="hide" style="position:absolute;left:110px;top:560px;width:460px;height:230px;border-radius:30px;background:linear-gradient(160deg, {C["blue"]}, #0654b0);'
         f'box-shadow:0 24px 50px rgba(0,0,0,0.5);display:flex;align-items:center;gap:20px;padding:0 32px"><div id="bo_ri">{icon("rocket", 120, "#fff", 3.5)}</div>'
         f'<div class="heavy" style="font-size:64px">VIDEO AI</div></div>',
         f'<div id="bo_m" class="hide"><div style="position:absolute;left:745px;top:330px;width:260px;text-align:center;font-weight:800;font-size:38px">Keinginan</div>'
         f'<div style="position:absolute;left:815px;top:390px;width:120px;height:620px;border-radius:60px;border:3px solid {C["line"]};background:rgba(255,255,255,0.05);overflow:hidden">'
         f'<div id="bo_lv" style="position:absolute;left:0;bottom:0;width:100%;height:100%;transform-origin:50% 100%;background:linear-gradient(0deg, {C["blue"]}, {C["yellow"]});box-shadow:{GLOW_Y}"></div></div></div>',
         f'<div id="bo_ar" class="hide" style="position:absolute;left:830px;top:0">{icon("up", 90, C["yellow"], 8)}</div>',
         chip("bo_c", 540, 1120, "boost keinginan je", size=34, **YFAINT), PANEL_CLOSE]
    j = [f"panel('bst', {n(a)}, {n(b)});", f"title('bo_t', {n(a)});",
         f"tl.fromTo('#bo_base', {{ y: 300 }}, {{ y: 0, duration: 0.35, ease: E.back, immediateRender: false }}, {n(a + 0.05)}); fadeIn('bo_base', {n(a + 0.05)}, 0.15);",
         f"fadeIn('bo_m', {n(a + 0.05)}, 0.3);",
         f"tl.fromTo('#bo_rk', {{ y: -520 }}, {{ y: 0, duration: 0.35, ease: E.back, immediateRender: false }}, {n(a + 0.35)}); fadeIn('bo_rk', {n(a + 0.35)}, 0.1);",
         yoyo("#bo_ri", a + 0.35, b, "y", -4, 4, 0.349),
         f"gsap.set('#bo_lv', {{ scaleY: 0.3 }}); tl.to('#bo_lv', {{ scaleY: 0.92, duration: 0.7, ease: E.out }}, {t('boost')});",
         f"tl.set('#bo_ar', {{ y: {1040 - 620 * 0.3 - 110:.0f} }}, {t('boost')}); fadeIn('bo_ar', {t('boost')}, 0.2);",
         f"tl.to('#bo_ar', {{ y: {1040 - 620 * 0.92 - 110:.0f}, duration: 0.7, ease: E.out }}, {t('boost')});",
         f"pop('bo_c', {t('keinginan', 0.3)});"]
    return dict(a=a, html="\n".join(h), js="\n".join(j))


# =====================================================================================================
# 7 · TIGA TINDAKAN: konten sebenar -> result -> testimoni
def tindakan():
    a, b = T["buatKonten"] - 0.06, T["samaClosing"] - 0.05
    rows = [("buatKonten", "Konten sebenar", img("img/real_content.jpg", "50% 30%"), "rakaman sendiri"),
            ("result", "Result", icon("chart", 110, C["cyan"], 4), ""), ("testimoni", "Testimoni", icon("quote", 110, C["cyan"], 4), "")]
    h = [panel_open("tdk"), title("ti_t", "Bina trust *dulu*")]
    for i, (k, nm, ic, tag) in enumerate(rows):
        tg = (f'<div style="position:absolute;bottom:8px;left:8px;right:8px;text-align:center;font-weight:700;font-size:17px;background:rgba(6,19,41,0.75);'
              f'border-radius:6px;padding:2px 0">{tag}</div>') if tag else ""
        h.append(card(f"ti_r{i}", f"left:70px;top:{330 + i * 265}px;width:940px;height:230px;display:flex;align-items:center;gap:32px;padding:0 26px",
                      f'<div style="width:180px;height:180px;border-radius:22px;overflow:hidden;background:rgba(0,207,245,0.1);display:flex;align-items:center;justify-content:center;flex-shrink:0;position:relative">{ic}{tg}</div>'
                      f'<div style="flex:1"><div style="font-weight:700;font-size:30px;color:{C["cyan"]}">0{i + 1}</div><div style="font-weight:900;font-size:62px;letter-spacing:-0.02em">{nm}</div></div>'
                      + tick_svg(f"ti_k{i}", 84)))
    h.append(PANEL_CLOSE)
    j = [f"panel('tdk', {n(a)}, {n(b)});", f"title('ti_t', {n(a)});"]
    for i, (k, *_r) in enumerate(rows):
        j += [f"slideIn('ti_r{i}', {t(k, -0.08)}, {{ x: 700 }});", f"tl.set('#ti_r{i}', {{ borderColor: 'rgba(255,230,0,0.6)' }}, {t(k)});",
              f"tick('ti_k{i}', {t(k, 0.12)});"]
    return dict(a=a, html="\n".join(h), js="\n".join(j))


# 7b · SAMA JUGA MACAM CLOSING (the funnel again, final state)
def sama_closing():
    a, b = T["samaClosing"] - 0.05, T["baruBaru"] - 0.05
    fh, fj = funnel("f3_", 40)
    h = [panel_open("smc"), title("sc_t", "Sama juga macam *closing*", size=60), fh, PANEL_CLOSE]
    return dict(a=a, html="\n".join(h), js="\n".join([f"panel('smc', {n(a)}, {n(b)}, 1.1);", f"title('sc_t', {n(a)});", fj]))


# =====================================================================================================
# 8 · CHATBOT (pattern interrupt): chat window + typing dots + notification toast
def chatbot():
    a, b = T["baruBaru"] - 0.05, T["awakSendiri"] - 0.05
    bot = lambda s: f'<div style="width:{s}px;height:{s}px;border-radius:{"50%" if s == 70 else "16px"};background:{C["blue"]};display:flex;align-items:center;justify-content:center">{icon("bot", int(s * .68), "#fff", 5)}</div>'
    bubbles = [(a + 0.25, False, "Hai! Ada apa boleh saya bantu? 👋"), (a + 0.9, True, "Berapa harga? Ada stok?")]
    body = (f'<div style="height:110px;background:rgba(255,255,255,0.06);display:flex;align-items:center;gap:20px;padding:0 30px;border-bottom:1px solid rgba(255,255,255,0.1)">{bot(70)}'
            f'<div><div style="font-weight:800;font-size:34px">Chatbot AI</div><div style="font-weight:600;font-size:22px;color:{C["cyan"]}">● online 24 jam</div></div></div>')
    for i, (at, me, txt) in enumerate(bubbles):
        side = "right:30px" if me else "left:30px"
        body += (f'<div id="cb_b{i}" class="hide" style="position:absolute;top:{160 + i * 130}px;{side};max-width:620px;background:{C["blue"] if me else "rgba(255,255,255,0.12)"};'
                 f'font-weight:600;font-size:32px;padding:20px 28px;border-radius:28px;transform-origin:{"100% 50%" if me else "0 50%"}">{txt}</div>')
    body += ('<div id="cb_ty" class="hide" style="position:absolute;top:420px;left:30px;background:rgba(255,255,255,0.12);border-radius:28px;padding:24px 30px;display:flex;gap:12px">'
             + "".join(f'<div id="cb_d{k}" style="width:16px;height:16px;border-radius:50%;background:#fff;opacity:0.35"></div>' for k in range(3)) + "</div>")
    body += ('<div style="position:absolute;bottom:26px;left:30px;right:30px;height:80px;border-radius:40px;background:rgba(255,255,255,0.08);font-size:26px;'
             'color:rgba(255,255,255,0.4);display:flex;align-items:center;padding:0 30px">Taip mesej…</div>')
    h = [panel_open("cbt"), title("cb_t", "Baru start, dah *chatbot*?", size=60),
         card("cb_win", "left:110px;top:330px;width:860px;height:780px", body, border="rgba(255,255,255,0.18)", cls=""),
         f'<div id="cb_toast" class="hide" style="position:absolute;left:120px;top:290px;width:840px;height:104px;border-radius:26px;background:rgba(255,255,255,0.96);'
         f'box-shadow:0 20px 50px rgba(0,0,0,0.5);display:flex;align-items:center;gap:20px;padding:0 26px">{bot(64)}'
         f'<div><div style="font-weight:800;font-size:30px;color:{C["navy"]}">Chatbot diaktifkan ✓</div><div style="font-weight:500;font-size:22px;color:#4a5870">baru sahaja</div></div></div>',
         chip("cb_s", 330, 1175, "Jual service", size=34, **YFAINT), chip("cb_p", 750, 1175, "Jual produk", size=34, **YFAINT),
         f'<div id="cb_vc" class="hide" style="position:absolute;right:130px;top:360px;font-weight:600;font-size:20px;color:rgba(255,255,255,0.5)">Visual contoh</div>',
         PANEL_CLOSE]
    ta = T["chatbot"] - 0.1
    j = [f"panel('cbt', {n(a)}, {n(b)}, 0.9);", f"title('cb_t', {n(a)});", f"fadeIn('cb_vc', {n(a + 0.4)});"]
    for i, (at, me, txt) in enumerate(bubbles): j.append(f"pop('cb_b{i}', {n(at)}, 0.3, 0.5);")
    j.append(f"tl.set('#cb_ty', {{ opacity: 1 }}, {n(a + 1.5)});")
    for k in range(3): j.append(yoyo(f"#cb_d{k}", a + 1.5 + k * 0.1, b, "opacity", 0.35, 1, 0.349))
    j += [f"tl.fromTo('#cb_toast', {{ y: -200, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.35, ease: E.back, immediateRender: false }}, {n(ta)});",
          f"tl.to('#cb_toast', {{ y: -200, opacity: 0, duration: 0.3, ease: E.in }}, {n(ta + 1.8)});",
          f"pop('cb_s', {t('service', -0.05)});", f"pop('cb_p', {t('produk2', -0.05)});"]
    return dict(a=a, html="\n".join(h), js="\n".join(j))


# =====================================================================================================
# 9 · TAK ADA BLUEPRINT closing: a flow that never completes
def blueprint():
    a, b = T["awakSendiri"] - 0.05, T["macamMana"] - 0.05
    nodes = [(190, 560, "1", True), (400, 740, "?", False), (640, 560, "?", False), (860, 780, "CLOSE", False)]
    grid = (f"repeating-linear-gradient(0deg, rgba(0,207,245,0.09) 0 2px, transparent 2px 50px), "
            f"repeating-linear-gradient(90deg, rgba(0,207,245,0.09) 0 2px, transparent 2px 50px), {C['navy2']}")
    h = [panel_open("blp"), title("bp_t", "Blueprint *closing* ?"),
         f'<div style="position:absolute;left:70px;top:320px;width:940px;height:800px;border-radius:26px;border:2px solid {C["line"]};overflow:hidden;background:{grid}">'
         f'<div style="position:absolute;left:28px;top:22px;font-family:\'JetBrains Mono\', monospace;font-size:24px;color:{C["cyan"]};letter-spacing:0.15em">BLUEPRINT · CLOSING</div></div>',
         f'<svg width="{W}" height="1200" style="position:absolute;left:0;top:0">']
    for i in range(3):
        (x0, y0, *_r), (x1, y1, *_q) = nodes[i], nodes[i + 1]
        dash = "" if i == 0 else 'stroke-dasharray="14 14"'
        h.append(f'<line id="bp_ln{i}" x1="{x0}" y1="{y0}" x2="{x0}" y2="{y0}" stroke="{C["cyan"]}" stroke-width="5" {dash} opacity="{1 if i == 0 else 0.7}"/>')
    h.append("</svg>")
    for i, (x, y, lab, solid) in enumerate(nodes):
        end = i == 3
        st = (f"width:{220 if end else 140}px;height:140px;border-radius:{'30px' if end else '50%'};border:5px {'solid' if solid else 'dashed'} "
              f"{C['cyan'] if solid else 'rgba(255,255,255,0.6)'};background:{'rgba(0,207,245,0.2)' if solid else 'rgba(255,255,255,0.04)'};display:flex;align-items:center;"
              f"justify-content:center;font-family:{'Archivo Black' if end else 'Inter'};font-weight:900;font-size:{48 if end else 70}px;color:{'#fff' if solid else 'rgba(255,255,255,0.75)'}")
        h.append(anchor(x, y, f'<div id="bp_n{i}" class="hide"><div id="bp_f{i}" style="{st}">{lab}</div></div>'))
    h += [anchor(540, 980, f'<div id="bp_st" class="heavy hide" style="border:8px solid {C["yellow"]};color:{C["yellow"]};font-size:96px;padding:4px 34px 10px;border-radius:18px;'
                           f'white-space:nowrap;text-shadow:{GLOW_Y};background:rgba(6,19,41,0.6)">TAK ADA</div>'), PANEL_CLOSE]
    j = [f"panel('blp', {n(a)}, {n(b)});", f"title('bp_t', {n(a)});"]
    for i in range(3):
        (x0, y0, *_r), (x1, y1, *_q) = nodes[i], nodes[i + 1]
        r = 1 if i == 0 else 0.55
        j.append(f"tl.fromTo('#bp_ln{i}', {{ attr: {{ x2: {x0}, y2: {y0} }} }}, {{ attr: {{ x2: {x0 + (x1 - x0) * r:.1f}, y2: {y0 + (y1 - y0) * r:.1f} }}, duration: 0.4, ease: E.io, immediateRender: false }}, {n(a + 0.25 + i * 0.35)});")
    for i in range(4): j.append(f"pop('bp_n{i}', {n(a + 0.1 + i * 0.35)}, 0.3, 0.3);")
    # flicker of the unfinished parts (12 Hz, seeded)
    f0, f1 = int(a * 12) + 1, int(b * 12)
    for fr in range(f0, f1, 1):
        tt = fr / 12
        for i in (1, 2):
            j.append(f"tl.set('#bp_ln{i}', {{ opacity: {0.7 if noise(fr + i * 7) > 0.25 else 0.245} }}, {tt:.4f});")
        for i in (1, 2, 3):
            j.append(f"tl.set('#bp_f{i}', {{ opacity: {1 if noise(fr + (i + 3) * 7) > 0.25 else 0.71} }}, {tt:.4f});")
    j += [f"gsap.set('#bp_st', {{ rotation: -7 }}); pop('bp_st', {t('takAda')}, 0.2, 2.2);"]
    return dict(a=a, html="\n".join(h), js="\n".join(j))


# =====================================================================================================
# 10 · TANPA FUNDAMENTAL, KONTEN = BUIH DI LAUTAN (the literal metaphor, abstracted)
FLOAT = ["img/ai_img_drink.jpg", "img/ai_poster_sofa.jpg", "img/ai_img_kitchen.jpg"]


def buih():
    import math
    a, b = T["samaKontenAI"] - 0.05, END_CARD + 0.05
    SPEEDS = (2.0, 2.6, 3.2)  # wave phase speeds (rad/s), as in the original sin(x/110 + t*speed)

    def wave(k, amp, y0):  # long enough to slide left for the whole panel (x shift = 110 * speed * time)
        x1 = int(W + 110 * SPEEDS[k] * (b - a) + 200)
        d = f"M-100 {y0}"
        for x in range(-100, x1 + 1, 20): d += f" L{x} {y0 + math.sin(x / 110 + k) * amp:.1f}"
        return d + f" L{x1} 1300 L-100 1300 Z"
    h = [panel_open("buh"), title("bu_t1", "Sama juga *konten AI*"), title("bu_t2", "Kalau tak ada…"), title("bu_t3", "Tanpa *fundamental*"),
         anchor(540, 360, '<div id="bu_fq" class="heavy hide" style="border:5px dashed rgba(255,255,255,0.55);border-radius:24px;padding:20px 40px;font-size:70px;color:rgba(255,255,255,0.8);white-space:nowrap">FUNDAMENTAL = ?</div>'),
         f'<svg width="{W}" height="1300" style="position:absolute;left:0;top:0;overflow:hidden">',
         f'<path id="bu_w0" d="{wave(0, 18, 960)}" fill="rgba(8,123,238,0.35)"/>', f'<path id="bu_w1" d="{wave(1, 14, 1000)}" fill="rgba(0,207,245,0.25)"/>',
         f'<path id="bu_w2" d="{wave(2, 10, 1050)}" fill="rgba(6,19,41,0.85)" stroke="{C["cyan"]}" stroke-width="3"/>', "</svg>"]
    for i, src in enumerate(FLOAT):
        x = 250 + i * 290
        h.append(f'<div id="bu_fw{i}" style="position:absolute;left:{x - 100}px;top:{930 - 390}px;width:200px;height:260px">'
                 f'<div id="bu_fd{i}" style="position:absolute;inset:0"><div id="bu_f{i}" class="hide" style="position:absolute;inset:0;border-radius:18px;overflow:hidden;border:3px solid rgba(255,255,255,0.8)">{img(src)}</div></div></div>')
    bubbles = [(120 + noise(i * 3.1) * 840, 30 + noise(i * 5.7) * 60, noise(i * 1.3) * 0.9, 0.8 + noise(i * 9.1) * 0.7, 1.1 + noise(i * 2.2) * 0.8) for i in range(14)]
    for i, (x, r, d, sp, pa) in enumerate(bubbles):
        h.append(f'<div id="bu_b{i}" class="hide" style="position:absolute;left:{x - r:.1f}px;top:{980 - r:.1f}px;width:{2 * r:.1f}px;height:{2 * r:.1f}px;border-radius:50%;'
                 f'border:3px solid rgba(160,240,255,0.85);background:radial-gradient(circle at 32% 30%, rgba(255,255,255,0.6) 0 12%, rgba(0,207,245,0.12) 40%, transparent 70%)"></div>')
    h.append(PANEL_CLOSE)
    j = [f"panel('buh', {n(a)}, {n(b)}, 1.1);", f"title('bu_t1', {n(a)}); tl.set('#bu_t1', {{ opacity: 0 }}, {t('kalauTak', -0.05)});",
         f"title('bu_t2', {t('kalauTak', -0.05)}); tl.set('#bu_t2', {{ opacity: 0 }}, {t('fundamental', -0.2)}); title('bu_t3', {t('fundamental', -0.2)});",
         f"pop('bu_fq', {t('fundamental', -0.1)}, 0.3, 0.5); tl.to('#bu_fq', {{ opacity: 0, duration: 0.2, ease: E.out }}, {t('kontenTu')});"]
    for k, sp in enumerate(SPEEDS):  # waves drift at their own speeds
        j.append(f"tl.fromTo('#bu_w{k}', {{ x: 0 }}, {{ x: {-110 * sp * (b - a):.0f}, duration: {b - a:.3f}, ease: 'none', immediateRender: false }}, {n(a)});")
    tb = T["buih"] - 0.1
    for i in range(3):
        at = T["samaKontenAI"] + 0.2 + i * 0.12
        j += [f"pop('bu_f{i}', {n(at)}, 0.35, 0.4);", yoyo(f"#bu_fw{i}", at, b, "y", -16, 16, 1.309), yoyo(f"#bu_f{i}", at, b, "rotation", -5, 5, 1.571),
              f"tl.to('#bu_fd{i}', {{ y: 260, scale: 0.6, duration: 0.35, ease: E.in }}, {n(tb)});",  # drop onto the sea (own wrapper: the bob keeps running)
              f"tl.to('#bu_f{i}', {{ borderRadius: 130, duration: 0.35, ease: E.in }}, {n(tb)});",
              f"tl.to('#bu_f{i}', {{ opacity: 0, duration: 0.12, ease: 'none' }}, {t('buih', 0.2 + i * 0.12)});"]
    for i, (x, r, d, sp, pa) in enumerate(bubbles):  # rise, wobble, pop
        st = T["buih"] + d
        if st >= b: continue
        life = pa / sp
        j += [f"tl.set('#bu_b{i}', {{ opacity: 1 }}, {n(st)});",
              f"tl.fromTo('#bu_b{i}', {{ y: 0 }}, {{ y: {-420 * pa:.0f}, duration: {life:.3f}, ease: 'none', immediateRender: false }}, {n(st)});",
              f"tl.to('#bu_b{i}', {{ scale: 1.6, opacity: 0, duration: {0.12 / sp:.3f}, ease: 'none' }}, {n(st + life)});"]
    return dict(a=a, html="\n".join(h), js="\n".join(j))


def panels():
    return [hook(), mekanisme(), sumber(), pecahan(), produk_baru(), percaya(), fyp(), boost(), tindakan(), sama_closing(), chatbot(), blueprint(), buih()]


# =====================================================================================================
# FULL close-up overlays: one slam per FULL beat at most, on the punchline word
def full_overlays():
    q = f'<span class="serif" style="font-size:190px;color:{C["yellow"]};line-height:0.6;margin-top:50px">“</span>'
    S = [  # id, text, a, b, size, box, icon, sub
        ("sl0", "BISNES BARU", 0, T["produk"] - 0.04, 150, False, "", ""),
        ("sl1", "100% AI?", T["produk"] - 0.02, T["bisnesBaru"] - 0.06, 170, True, "", ""),
        ("sl2", "PESAN MENTOR", T["mentor"] - 0.1, T["dalam"] - 0.05, 96, False, q, ""),
        ("sl3", "PALING PENTING", T["paling"] - 0.08, T["closing"], 104, True, "", ""),
        ("sl4", "TRAFIK = ?", T["trafikQ"] - 0.02, T["sumber"] - 0.07, 140, True, "", ""),
        ("sl5", "KENA ADA KONTEN", T["kenaAda"] - 0.05, T["dalamKonten"] - 0.07, 110, True, "", ""),
        ("sl6", "TAK BOLEH", T["takBoleh"] - 0.02, T["brand1"] - 0.08, 170, False, "", ""),
        ("sl7", "BRAND TRUST", T["brand1"] - 0.04, T["orangDah"] - 0.07, 112, True, icon("shield", 96, C["navy"], 6), ""),
        ("sl8", "DAH PERCAYA", T["orangPercaya"] - 0.04, T["videoAI"] - 0.07, 110, False, icon("shield", 96, C["yellow"], 6), ""),
        ("sl9", "BRAND TRUST", T["brandDulu"] - 0.06, T["buatKonten"] - 0.08, 118, True, "", "dulu."),
        ("sl10", "DAH CLEAR?", T["soClear"] + 0.05, T["samaKontenAI"] - 0.07, 140, True, "", ""),
    ]
    out = []
    for id_, txt, a, b, size, box, ic, sub in S:
        js = f"slam('{id_}', {n(a)}, {n(b)}, {'true' if sub else 'false'});"
        out.append(dict(a=a, html=slam(id_, txt, size, box, sub, ic), js=js))
    # chatbot with no blueprint: minimal graphic, give the voice room
    a, b = T["chatbot2"] - 0.1, T["kalauAwak"]
    out.append(dict(a=a, html=(
        f'<div id="fo_bot" class="hide" style="position:absolute;left:90px;top:250px;display:flex;align-items:center;gap:14px">'
        f'<div style="width:110px;height:110px;border-radius:28px;background:{C["blue"]};box-shadow:{GLOW_C};display:flex;align-items:center;justify-content:center">{icon("bot", 78, "#fff", 4.5)}</div>'
        f'<div class="heavy" style="font-size:90px;color:{C["yellow"]};text-shadow:{GLOW_Y}">?</div></div>'),
        js=(f"fadeIn('fo_bot', {n(a)}, 0.25); tl.to('#fo_bot', {{ opacity: 0, duration: 0.25, ease: E.in }}, {n(b - 0.25)});\n"
            + yoyo("#fo_bot", a, b, "y", -6, 6, 1.047))))
    return out


# =====================================================================================================
# END CARD: takeaway in 2 lines + the brand's logo row. Starts just after the last word, holds >= 2 s.
END_LINE1, END_LINE2 = "FUNDAMENTAL", "DULU"


def end_card():
    a = END_CARD
    logos = ""
    if os.path.exists(os.path.join(HF, "assets", "img", "logo_icon.png")):
        logos += '<img src="assets/img/logo_icon.png" alt="" style="width:130px;height:130px;border-radius:30px">'
    if os.path.exists(os.path.join(HF, "assets", "img", "logo_text.png")):
        logos += '<img src="assets/img/logo_text.png" alt="" style="width:330px">'
    h = (f'<div id="endc" class="layer hide" style="background:radial-gradient(ellipse at 50% 40%, #0d2a57 0%, {C["navy"]} 65%)">'
         f'<div class="layer" style="background-image:radial-gradient(rgba(0,207,245,0.18) 1.6px, transparent 1.8px);background-size:36px 36px;opacity:0.6"></div>'
         f'<div id="endk" class="layer">'
         + anchor(540, 760, f'<div id="end1w"><div id="end1" class="heavy hide" style="font-size:112px;text-shadow:{SHADOW};white-space:nowrap;letter-spacing:-0.02em">{END_LINE1}</div></div>')
         + anchor(540, 945, f'<div id="end2" class="heavy hide" style="background:{C["yellow"]};color:{C["navy"]};font-size:150px;padding:4px 48px 16px;border-radius:22px;box-shadow:{GLOW_Y}">{END_LINE2}</div>')
         + (anchor(540, 1290, f'<div id="endlg" class="hide" style="display:flex;align-items:center;gap:26px">{logos}</div>') if logos else "")
         + "</div></div>")
    j = [f"tl.fromTo('#endc', {{ opacity: 0 }}, {{ opacity: 1, duration: 0.35, ease: E.out, immediateRender: false }}, {n(a)});",
         f"tl.fromTo('#end1', {{ scale: 1.5 }}, {{ scale: 1, duration: 0.3, ease: E.back, immediateRender: false }}, {n(a + 0.05)}); fadeIn('end1', {n(a + 0.05)}, 0.15);",
         f"tl.fromTo('#end1w', {{ scale: 1 }}, {{ scale: 1.03, duration: 2, ease: 'none', immediateRender: false }}, {n(a)});",
         f"tl.fromTo('#end2', {{ scale: 1.8 }}, {{ scale: 1, duration: 0.3, ease: E.back, immediateRender: false }}, {n(a + 0.22)}); fadeIn('end2', {n(a + 0.22)}, 0.15);"]
    if logos:
        j.append(f"tl.fromTo('#endlg', {{ y: 40, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.4, ease: E.out, immediateRender: false }}, {n(a + 0.45)});")
    j.append(f"tl.to('#endk', {{ opacity: 0, duration: 0.25, ease: E.in }}, {n(TOTAL - 0.25)});")
    return dict(html=h, js="\n".join(j))
