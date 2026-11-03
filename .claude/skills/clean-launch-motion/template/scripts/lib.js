// ================= Clean Launch Motion: locked building blocks (GSAP, seek-safe) =================
// Inlined into hf/index.html by build.py, after the data block (PLAN, WORDS, SPAN, TOTAL).
// Every helper adds tweens to ONE paused timeline `tl`. Nothing reads the clock; every value is a
// function of timeline time, so any frame can be rendered alone.
const tl = gsap.timeline({ paused: true });
const $ = (id) => document.getElementById(id);
const W = 1080, H = 1920, FPS = 30, OVER = 0.1; // OVER = zoom-through overlap between scenes (s)

// ---------- eases (exact CSS cubic-bezier, same curves as the approved Remotion build) ----------
function cubicBezier(x1, y1, x2, y2) {
  const cx = 3 * x1, bx = 3 * (x2 - x1) - cx, ax = 1 - cx - bx;
  const cy = 3 * y1, by = 3 * (y2 - y1) - cy, ay = 1 - cy - by;
  const sx = (t) => ((ax * t + bx) * t + cx) * t, sy = (t) => ((ay * t + by) * t + cy) * t;
  const dx = (t) => (3 * ax * t + 2 * bx) * t + cx;
  return (x) => {
    if (x <= 0) return 0;
    if (x >= 1) return 1;
    let t = x;
    for (let i = 0; i < 8; i++) { const e = sx(t) - x, d = dx(t); if (Math.abs(e) < 1e-6 || Math.abs(d) < 1e-6) break; t -= e / d; }
    if (Math.abs(sx(t) - x) > 1e-5) { let lo = 0, hi = 1; t = x; for (let i = 0; i < 40; i++) { if (sx(t) < x) lo = t; else hi = t; t = (lo + hi) / 2; } }
    return sy(t);
  };
}
const EASE_OUT = cubicBezier(0.16, 1, 0.3, 1); // expo-like settle (entrances)
const EASE_IN = cubicBezier(0.7, 0, 0.84, 0);  // exits
const EASE_IO = cubicBezier(0.65, 0, 0.35, 1); // camera moves, morphs
const backOut = (x) => 1 + 2.2 * Math.pow(x - 1, 3) + 1.2 * Math.pow(x - 1, 2); // small overshoot (cards, chips, buttons)
const LINEAR = (p) => p;
const clamp01 = (v) => Math.min(1, Math.max(0, v));
const mix = (a, b, p) => a + (b - a) * p;

// ---------- VO word anchors (vo/vo_words.json, injected as WORDS) ----------
const BY_ID = new Map(WORDS.map((w) => [w.id, w]));
function word(id) { const w = BY_ID.get(id); if (!w) throw new Error("VO word not found: " + id); return w; }
const ws = (id, off = 0) => word(id).s + off;  // start of word id ("storyboard.#1") + offset
const we = (id, off = 0) => word(id).e + off;  // end of word id + offset
const sceneWords = (k) => WORDS.filter((w) => w.scene === k);
function nth(k, n) {
  const l = sceneWords(k);
  if (!l.length) throw new Error("no VO words for scene " + k);
  return l[Math.max(0, Math.min(l.length - 1, n < 0 ? l.length + n : n))];
}
const sw = (k, n, off = 0) => nth(k, n).s + off;   // n-th word of scene k (negative counts from the end)
const swe = (k, n, off = 0) => nth(k, n).e + off;
/** Anchor spec -> seconds. 1.2 | "1.2" (absolute) | "video#1" | "hook:5" | any of these + "@-0.04" offset. */
function at(spec, defOff = 0) {
  if (typeof spec === "number") return spec;
  let s = String(spec).trim(), off = defOff, explicit = false;
  const i = s.lastIndexOf("@");
  if (i >= 0) { off = parseFloat(s.slice(i + 1)); s = s.slice(0, i); explicit = true; }
  if (/^-?\d*\.?\d+$/.test(s)) return parseFloat(s) + (explicit ? off : 0);
  if (/^[^#]+:-?\d+$/.test(s)) { const [k, n] = s.split(":"); return sw(k, parseInt(n, 10), off); }
  return ws(s, off);
}

// ---------- generic tween helpers ----------
/** Tween `prop` so that its value IS fn(p), p = 0..1 over [start, start+dur]. Seek-safe way to draw any curve
 *  (sine drift, speed blur, confetti arcs). `tpl` wraps the number, e.g. blurTpl for filter. */
function curve(target, prop, start, dur, fn, o = {}) {
  const tpl = o.tpl || ((v) => v);
  tl.fromTo(target, { [prop]: tpl(0) }, { [prop]: tpl(1), duration: Math.max(0.001, dur), ease: fn, immediateRender: false }, start);
  if (o.ir) gsap.set(target, { [prop]: tpl(fn(0)) }); // ir: hold the curve's own first value until it starts
}
const blurTpl = (v) => `blur(${v}px)`;
/** Speed-based motion blur for a move of `dist` px over `dur` s with ease E: travel per frame x 0.09, capped at 14. */
const mblurFn = (E, dist, dur, k = 0.09, max = 14) => (p) =>
  Math.min(max, Math.abs(E(p) - E(Math.max(0, p - 1 / (FPS * dur)))) * Math.abs(dist) * k);
/** Apply a motion-blur curve to el and clear the filter afterwards (a kept filter makes tilted planes soft). */
function mblur(el, start, dur, E, dist) {
  curve(el, "filter", start, dur, mblurFn(E, dist, dur), { tpl: blurTpl });
  tl.set(el, { filter: "none" }, start + dur);
}
/** Gentle sine float on one property (use a dedicated wrapper so it never fights an entrance tween). */
function float(el, prop, start, end, amp, freq = 1.4, phase = 0) {
  const D = Math.max(0.1, end - start);
  curve(el, prop, start, D, (p) => Math.sin(p * D * freq + phase) * amp);
}
/** Blur-in entrance: opacity 0->1, blur b->0, optional y/scale; filter cleared at the end. */
function blurIn(el, start, dur = 0.45, o = {}) {
  const from = { opacity: 0, filter: `blur(${o.blur ?? 12}px)` }, to = { opacity: 1, filter: "blur(0px)", duration: dur, ease: o.ease || EASE_OUT };
  if (o.y !== undefined) { from.y = o.y; to.y = 0; }
  if (o.scale !== undefined) { from.scale = o.scale; to.scale = 1; }
  if (o.ir === false) to.immediateRender = false;
  tl.fromTo(el, from, to, start);
  tl.set(el, { filter: "none" }, start + dur + 0.01);
}
/** Blur-out exit (headline-style): blur 16, scale 1.05, fade, 0.26 s. */
function blurOut(el, start, dur = 0.26, o = {}) {
  tl.fromTo(el, { opacity: 1, filter: "blur(0px)", scale: 1 },
    { opacity: 0, filter: `blur(${o.blur ?? 16}px)`, scale: o.scale ?? 1.05, duration: dur, ease: EASE_IN, immediateRender: false }, start);
}

// ---------- 3D tilt without preserve-3d ----------
// The look was designed as CSS `rotateX(a) rotateY(b) rotateZ(c) scale(s)` under a parent `perspective` whose vanishing
// point is the FRAME centre. HyperFrames planes use per-element transformPerspective instead (never a preserve-3d stage:
// videos inside those render black). Two corrections keep the same picture:
//  1. GSAP writes `rotate(Z) rotateY rotateX`, so tilt() converts the angles to the same orientation.
//  2. transformPerspective projects from the element's transform-origin. pose() moves the origin to the vanishing point
//     (vp = [dx, dy] px from the plane's centre to the frame centre, e.g. a phone centred at y 1364 -> vp [0, -404])
//     and adds the translation R*s*d - d, which makes the result identical to the parent-perspective version.
const _rot = (rx, ry, rz) => {
  const r = Math.PI / 180, [ca, sa] = [Math.cos(rx * r), Math.sin(rx * r)], [cb, sb] = [Math.cos(ry * r), Math.sin(ry * r)], [cc, sc] = [Math.cos(rz * r), Math.sin(rz * r)];
  const X = [[1, 0, 0], [0, ca, -sa], [0, sa, ca]], Y = [[cb, 0, sb], [0, 1, 0], [-sb, 0, cb]], Z = [[cc, -sc, 0], [sc, cc, 0], [0, 0, 1]];
  const mul = (A, B) => A.map((row, i) => B[0].map((_, j) => row.reduce((acc, _v, k) => acc + A[i][k] * B[k][j], 0)));
  return mul(mul(X, Y), Z); // CSS rotateX rotateY rotateZ
};
function tilt(rx, ry, rz) {
  const M = _rot(rx, ry, rz), r = Math.PI / 180;
  const b = -Math.asin(Math.max(-1, Math.min(1, M[2][0]))), a = Math.atan2(M[2][1], M[2][2]), g = Math.atan2(M[1][0], M[0][0]);
  return { rotationX: a / r, rotationY: b / r, rotation: g / r };
}
/** Pose = {x, y, rx, ry, rz, s, persp, vp:[dx,dy]} -> GSAP vars for element el. */
function pose(el, p) {
  const s = p.s ?? 1, v = { x: p.x ?? 0, y: p.y ?? 0, z: 0, scale: s, transformPerspective: p.persp ?? 2400, ...tilt(p.rx ?? 0, p.ry ?? 0, p.rz ?? 0) };
  if (p.vp) {
    const [dx, dy] = p.vp, M = _rot(p.rx ?? 0, p.ry ?? 0, p.rz ?? 0);
    v.x += s * (M[0][0] * dx + M[0][1] * dy) - dx;
    v.y += s * (M[1][0] * dx + M[1][1] * dy) - dy;
    v.z += s * (M[2][0] * dx + M[2][1] * dy);
    const e = typeof el === "string" ? document.querySelector(el) : el;
    gsap.set(e, { transformOrigin: `${e.offsetWidth / 2 + dx}px ${e.offsetHeight / 2 + dy}px` });
  }
  return v;
}
/** Tween a plane between two poses (give both the same vp and persp). */
function poseTo(el, from, to, start, dur, ease = EASE_OUT, ir = true) {
  tl.fromTo(el, pose(el, from), { ...pose(el, to), duration: dur, ease, immediateRender: ir }, start);
}

// ---------- scenes, camera, transitions ----------
/** Register a scene: zoom-through in/out (0.34 s settle from 0.9 + blur 14; out: push to 1.22 + blur 18 + fade over 0.3 s). */
function scene(key, build) {
  const i = PLAN.scenes.indexOf(key), first = i === 0, last = i === PLAN.scenes.length - 1;
  const [a, b] = SPAN[key], el = $(key);
  if (!el) throw new Error(`scene "${key}" has no <section id="${key}">`);
  const S = { key, a, b, first, last, end: last ? TOTAL : b + OVER, el, cam: $(key + "-cam"), step: $(key + "-step") };
  if (first) gsap.set(el, { opacity: 1 });
  else {
    tl.fromTo(el, { scale: 0.9, filter: "blur(14px)" }, { scale: 1, filter: "blur(0px)", duration: 0.34, ease: EASE_OUT }, a - 0.04);
    curve(el, "opacity", a - 0.04, 0.34, (p) => Math.min(1, EASE_OUT(p) * 1.6));
    tl.set(el, { filter: "none" }, a + 0.31);
  }
  if (!last) {
    tl.fromTo(el, { scale: 1, filter: "blur(0px)" }, { scale: 1.22, filter: "blur(18px)", duration: 0.3, ease: EASE_IN, immediateRender: false }, S.end - 0.26);
    // fade over the push, cut to 0 at b + OVER (the scene is gone there, as in the approved build)
    curve(el, "opacity", S.end - 0.26, 0.26, (p) => (p >= 1 ? 0 : 1 - EASE_IN((p * 0.26) / 0.3)));
  }
  build(S);
}
/** Scene camera: slow push (+push over the scene), roll drift (sin 0.9 rad/s x roll deg) and +3 % step zooms (0.35 s) on beat words. */
function cam(S, o = {}) {
  const push = o.push ?? 0.05, roll = o.roll ?? 0.6, steps = (o.steps || []).slice().sort((x, y) => x - y);
  if (o.origin) gsap.set([S.cam, S.step], { transformOrigin: o.origin });
  tl.fromTo(S.cam, { scale: 1 }, { scale: 1 + push, duration: Math.max(0.1, S.b - S.a), ease: LINEAR }, S.a);
  const D = S.end + 0.4 - S.a;
  curve(S.cam, "rotation", S.a, D, (p) => Math.sin(p * D * 0.9) * roll, { ir: true });
  steps.forEach((st, k) => tl.fromTo(S.step, { scale: 1 + 0.03 * k }, { scale: 1 + 0.03 * (k + 1), duration: 0.35, ease: EASE_OUT, immediateRender: k === 0 }, st));
}
/** Camera keys across an image inside a fixed-size layer (w x h): each key moves to scale s centred on (x, y) in layer px. */
function camKeys(el, w, h, keys) {
  gsap.set(el, { transformOrigin: "0 0" });
  const v = (k) => ({ x: w / 2 - k.x * k.s, y: h / 2 - k.y * k.s, scale: k.s });
  gsap.set(el, v(keys[0]));
  keys.slice(1).forEach((k, i) => tl.fromTo(el, v(keys[i]), { ...v(k), duration: k.d ?? 0.45, ease: EASE_IO, immediateRender: false }, k.t));
  return keys;
}

// ---------- headline: re-centring, word-by-word blur-in ----------
// Markup: <div class="hl" id="x" data-y="900" data-size="124"><span data-at="0.1">Belajar</span><span data-at="video#1" class="blue">Video</span></div>
// span classes: blue (gradient), royal, br (start a new line). data-at default offset is -0.1 s (slot opens before the word).
// Each word's slot opens (grid 0fr -> 1fr, 0.32 s, EASE_IO, from -0.1 s) so the line glides back to centre, then the glyphs
// blur in (+0.06 s, 0.4 s: blur 12 -> 0, rise 26 px, scale 1.08 -> 1). Lines wider than data-max (880) are scaled to fit.
function headline(id, o = {}) {
  const root = $(id), d = root.dataset;
  const size = +(d.size || 92), weight = +(d.weight || 500), gap = +(d.gap || 0.26), lh = +(d.lh || 1.14), maxW = +(d.max || 880), y = +(d.y || 960);
  const parts = [...root.children].map((p) => ({ text: p.textContent, cls: p.className, at: p.dataset.at }));
  const base = d.at !== undefined ? at(d.at, 0) : null;
  const times = parts.map((p, i) => (p.at !== undefined ? at(p.at, -0.1) : (base ?? 0) + i * 0.07));
  root.textContent = "";
  Object.assign(root.style, { fontSize: size + "px", fontWeight: weight, lineHeight: lh });
  const lines = [[]];
  parts.forEach((p, i) => {
    if (/\bbr\b/.test(p.cls) && lines[lines.length - 1].length) lines.push([]);
    lines[lines.length - 1].push({ ...p, t: times[i] });
  });
  const words = [];
  lines.forEach((ln) => {
    const L = document.createElement("div"); L.className = "hl-line"; root.appendChild(L);
    ln.forEach((p, j) => {
      const w = document.createElement("div"); w.className = "hl-w";
      const wi = document.createElement("div"); wi.className = "hl-wi"; if (j) wi.style.paddingLeft = gap + "em";
      const g = document.createElement("span"); g.className = "hl-g " + p.cls.replace(/\bbr\b/, ""); g.textContent = p.text;
      wi.appendChild(g); w.appendChild(wi); L.appendChild(w); words.push({ w, g, t: p.t });
    });
  });
  // fit: measure every line fully open (fonts are loaded before scripts run), then close the slots again
  const fit = () => {
    root.style.fontSize = size + "px";
    words.forEach(({ w }) => (w.style.gridTemplateColumns = "1fr"));
    const full = Math.max(...[...root.children].map((L) => [...L.children].reduce((s, c) => s + c.getBoundingClientRect().width, 0)));
    const fs = full > maxW ? size * (maxW / full) : size;
    root.style.fontSize = fs + "px";
    root.style.top = y - (lines.length * fs * lh) / 2 + "px";
    words.forEach(({ w }) => (w.style.gridTemplateColumns = "0fr"));
    return fs;
  };
  const fs = fit();
  words.forEach(({ w, g, t }) => {
    tl.fromTo(w, { gridTemplateColumns: "0fr" }, { gridTemplateColumns: "1fr", duration: 0.32, ease: EASE_IO }, t - 0.1);
    tl.fromTo(g, { opacity: 0, y: 26, scale: 1.08, filter: "blur(12px)" }, { opacity: 1, y: 0, scale: 1, filter: "blur(0px)", duration: 0.4, ease: EASE_OUT }, t + 0.06);
    tl.set(g, { filter: "none" }, t + 0.47);
  });
  const out = o.out ?? (d.out !== undefined ? at(d.out, 0) : undefined);
  if (out !== undefined) blurOut(root, out);
  return { root, times, fs, first: Math.min(...times) };
}

// ---------- highlight: rounded stroke draws on, 8 % fill, optional label chip ----------
// Markup: <div class="hlt" id="x" data-x data-y data-w data-h data-label="Packaging" data-pos="bottom"></div> (parent px)
function highlight(id, t0, o = {}) {
  const el = $(id), d = el.dataset, x = +d.x, y = +d.y, w = +d.w, h = +d.h, r = +(d.r || 22), perim = 2 * (w + h);
  Object.assign(el.style, { left: x + "px", top: y + "px", width: w + "px", height: h + "px" });
  el.innerHTML = `<svg width="${w + 20}" height="${h + 20}" style="position:absolute;left:-10px;top:-10px;overflow:visible">
    <rect x="10" y="10" width="${w}" height="${h}" rx="${r}" fill="rgba(72,152,248,0.08)" fill-opacity="0" stroke="${d.colour || "#2B7CF5"}" stroke-width="5"
      stroke-dasharray="${perim}" stroke-dashoffset="${perim}" style="filter:drop-shadow(0 0 10px rgba(72,152,248,0.55))"/></svg>` +
    (d.label ? `<div class="hlt-lab" style="${d.pos === "top" ? "bottom" : "top"}:${h + 18}px"><div class="hlt-in"><span class="chip white" style="font-size:30px">${d.label}</span></div></div>` : "");
  const rect = el.querySelector("rect");
  tl.fromTo(rect, { attr: { "stroke-dashoffset": perim, "fill-opacity": 0 } }, { attr: { "stroke-dashoffset": 0, "fill-opacity": 1 }, duration: 0.4, ease: EASE_OUT }, t0);
  const lab = el.querySelector(".hlt-lab");
  if (lab) {
    tl.fromTo(lab, { opacity: 0, y: 12 }, { opacity: 1, y: 0, duration: 0.4, ease: EASE_OUT }, t0);
    if (o.labelOut !== undefined) tl.fromTo(lab.firstChild, { opacity: 1 }, { opacity: 0, duration: 0.4, ease: EASE_OUT, immediateRender: false }, o.labelOut);
  }
}

// ---------- fly-in card (tilted floating card from off-frame) ----------
// Nest: .fly (entrance x/y/rotation/opacity + speed blur) > .flt (sine float). Card centre sits at its CSS left/top.
function flyIn(el, t0, o) {
  const [fx, fy] = o.from, rot = o.rot ?? 0, dur = o.dur ?? 0.5;
  gsap.set(el, { xPercent: -50, yPercent: -50 });
  tl.fromTo(el, { x: fx, y: fy }, { x: 0, y: 0, duration: dur, ease: backOut }, t0);
  curve(el, "rotation", t0, 0.45, (p) => mix(rot * 3.5, rot, EASE_OUT(p)), { ir: true });
  curve(el, "opacity", t0, 0.45, (p) => Math.min(1, EASE_OUT(p) * 2), { ir: true });
  mblur(el, t0, dur, backOut, Math.hypot(fx, fy) * 0.9);
  const flt = el.querySelector(".flt");
  if (flt && o.floatEnd) float(flt, "y", t0, o.floatEnd, 7, 1.3, o.phase ?? 0);
}

// ---------- ring -> check -> confetti ----------
function ringCheck(id, t0) {
  const el = $(id), R = +(el.dataset.r || 150), L = 2 * Math.PI * (R - 12);
  tl.fromTo(el.querySelector(".ring"), { attr: { "stroke-dashoffset": L } }, { attr: { "stroke-dashoffset": 0 }, duration: 0.5, ease: EASE_IO }, t0);
  tl.fromTo(el.querySelector(".tick"), { attr: { "stroke-dashoffset": 170 } }, { attr: { "stroke-dashoffset": 0 }, duration: 0.25, ease: EASE_OUT }, t0 + 0.45);
}
/** Restrained deterministic confetti (20-22 pieces, blue/cyan/indigo + a little pink/lilac), 1.6 s. */
function confetti(containerId, t0, cx, cy, n = 22) {
  const box = $(containerId), cols = ["#4898F8", "#7CC0F9", "#00A9EB", "#4858F8", "#F3A8D8", "#B7A6F8"];
  for (let i = 0; i < n; i++) {
    const r1 = Math.sin(i * 12.9898) * 43758.5453, r = r1 - Math.floor(r1), r2 = Math.sin(i * 78.233) * 12345.678, q = r2 - Math.floor(r2);
    const ang = (i / n) * Math.PI * 2 + r * 0.6, dist = 220 + q * 300;
    const c = document.createElement("div");
    Object.assign(c.style, { position: "absolute", left: cx + "px", top: cy + "px", width: 14 + q * 16 + "px", height: 8 + r * 10 + "px", borderRadius: "3px", background: cols[i % cols.length], opacity: 0 });
    box.appendChild(c);
    const e = (p) => EASE_OUT(clamp01(p * 1.4));
    curve(c, "x", t0, 1.6, (p) => Math.cos(ang) * dist * e(p));
    curve(c, "y", t0, 1.6, (p) => Math.sin(ang) * dist * e(p) + p * p * 260);
    curve(c, "rotation", t0, 1.6, (p) => ang * 57 + p * 540 * (q - 0.5));
    curve(c, "opacity", t0, 1.6, (p) => (p > 0 ? (1 - p) * 0.9 : 0));
    tl.set(c, { opacity: 0 }, t0 + 1.6);
  }
}

// ---------- cursor tap with ripple ----------
/** Cursor moves in (0.4 s), presses (scale 0.88), ripple on `rippleId`, fades out at `outAt`. */
function tap(cursorId, from, to, moveAt, tapAt, outAt, rippleId) {
  const c = $(cursorId);
  gsap.set(c, { transformOrigin: "30% 10%" });
  tl.fromTo(c, { x: from[0], y: from[1] }, { x: to[0], y: to[1], duration: 0.4, ease: EASE_OUT }, moveAt);
  tl.fromTo(c, { opacity: 0 }, { opacity: 1, duration: 0.4, ease: EASE_OUT }, moveAt);
  tl.fromTo(c, { scale: 1 }, { scale: 0.88, duration: 0.08, ease: EASE_OUT }, tapAt);
  tl.fromTo(c, { scale: 0.88 }, { scale: 1, duration: 0.18, ease: EASE_OUT, immediateRender: false }, tapAt + 0.1);
  if (outAt !== undefined) tl.fromTo(c, { opacity: 1 }, { opacity: 0, duration: 0.3, ease: EASE_OUT, immediateRender: false }, outAt);
  if (rippleId) {
    const rp = $(rippleId);
    tl.fromTo(rp, { width: 40, height: 40, opacity: 1 }, { width: 740, height: 740, opacity: 0, duration: 0.6, ease: LINEAR }, tapAt);
  }
}

// ---------- sparkle flight (cubic curve + soft dotted trail), then twinkle ----------
function sparkleFlight(sparkId, trailId, t0, P, size = 70) {
  const bez = (p, i) => { const u = 1 - p; return u * u * u * P[0][i] + 3 * u * u * p * P[1][i] + 3 * u * p * p * P[2][i] + p * p * p * P[3][i]; };
  const sp = $(sparkId), half = size / 2;
  curve(sp, "x", t0, 0.7, (p) => bez(EASE_IO(p), 0) - half, { ir: true });
  curve(sp, "y", t0, 0.7, (p) => bez(EASE_IO(p), 1) - half, { ir: true });
  curve(sp, "rotation", t0, 0.7, (p) => EASE_IO(p) * 180, { ir: true });
  curve(sp, "scale", t0, 0.7, (p) => mix(60, 80, EASE_IO(p)) / size, { ir: true });
  tl.fromTo(sp, { opacity: 0 }, { opacity: 1, duration: 0.15, ease: EASE_OUT }, t0);
  const tf = sp.querySelector(".tf"), tw = sp.querySelector(".tw");
  if (tf) float(tf, "y", t0 + 0.7, TOTAL, 6, 1.2);
  if (tw) curve(tw, "scale", t0 + 0.7, Math.max(0.1, TOTAL - t0 - 0.7), (p) => 1 + Math.sin((t0 + 0.7 + p * (TOTAL - t0 - 0.7)) * 5) * 0.08, { ir: true });
  const trail = $(trailId);
  for (let i = 0; i < 14; i++) {
    const dot = document.createElement("div"); dot.className = "trail-dot"; trail.appendChild(dot);
    const q = (p) => clamp01(EASE_IO(p) - i * 0.03);
    curve(dot, "x", t0, 0.7, (p) => bez(q(p), 0) - 9, { ir: true });
    curve(dot, "y", t0, 0.7, (p) => bez(q(p), 1) - 9, { ir: true });
    tl.set(dot, { opacity: (1 - i / 14) * 0.35 }, t0);
    tl.set(dot, { opacity: 0 }, t0 + 0.7);
  }
}

// ---------- background glows (drift for the whole video) ----------
function background() {
  curve($("glow1"), "x", 0, TOTAL, (p) => Math.sin(p * TOTAL * 0.21) * 60, { ir: true });
  curve($("glow1"), "y", 0, TOTAL, (p) => Math.cos(p * TOTAL * 0.17) * 50, { ir: true });
  curve($("glow2"), "x", 0, TOTAL, (p) => -Math.cos(p * TOTAL * 0.19) * 60, { ir: true });
  curve($("glow2"), "y", 0, TOTAL, (p) => -Math.sin(p * TOTAL * 0.23) * 60, { ir: true });
}
