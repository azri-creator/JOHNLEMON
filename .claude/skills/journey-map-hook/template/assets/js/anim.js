(function () {
  const A = window.AKG;
  const tl = gsap.timeline({ paused: true });
  const $ = (s) => document.querySelector(s);
  const FACE = "960px 470px";

  /* ============ presenter: mode (full / pip) ============ */
  const FULL = { scale: 1, x: 0, y: 0, "--ol": 0 };
  const PIP = { scale: 0.62, x: -650, y: 0, "--ol": 1 };
  gsap.set("#pres-pip", { transformOrigin: "960px 1080px", ...FULL });
  gsap.set("#pres-cam", { transformOrigin: FACE });
  const mode = (t, from, to, dur, ease) => tl.fromTo("#pres-pip", { ...from }, { ...to, duration: dur, ease, immediateRender: false }, t);
  mode(2.3, FULL, PIP, 0.62, "back.out(1.25)");
  mode(5.26, PIP, FULL, 0.28, "power3.out");
  mode(6.45, FULL, PIP, 0.55, "back.out(1.25)");
  mode(32.4, PIP, FULL, 0.3, "power3.out");
  mode(35.2, FULL, PIP, 0.55, "back.out(1.2)");
  mode(51.62, PIP, FULL, 0.45, "power3.inOut");

  /* ============ presenter camera: scale / dolly poses (alive!) ============ */
  const CAM = [];
  const P = (t, s, e = "sine.inOut", x = 0, y = 0, r = 0) => CAM.push({ t, s, x, y, r, e });
  // A: cold open punch-out then slow push
  P(0, 1.2, "none", 0, 34, 0.0); P(0.55, 1.06, "power3.out"); P(1.62, 1.12, "sine.inOut", 0, 0, -0.5); P(2.3, 1.15, "sine.inOut", 0, 0, 0.2);
  P(2.92, 1.0, "power2.out", 0, 0, 0);
  P(3.9, 1.03, "sine.inOut", 0, 0, 0.3); P(5.2, 1.0, "sine.inOut", 0, 0, 0);
  // B: "Sebenarnya tak guys" — snap punch-in
  P(5.27, 1.0, "none"); P(5.48, 1.24, "power4.out", -14, 16, 0.5); P(6.42, 1.31, "sine.inOut", -22, 22, 0.9);
  P(7.0, 1.0, "power2.out", 0, 0, 0);
  // PiP span 2 (7.0 → 32.3): breathing + word hits
  const hits2 = [[7.55, 0.07], [9.74, 0.07], [12.1, 0.09], [14.87, 0.09], [19.66, 0.09], [25.56, 0.09], [29.51, 0.05], [30.91, 0.05]];
  const pipSpan = (a, b, hits) => {
    for (let k = 1; a + k * 1.75 < b - 0.4; k++) {
      const tt = a + k * 1.75;
      if (hits.some(([h]) => tt > h - 0.45 && tt < h + 0.9)) continue;
      P(+tt.toFixed(2), k % 2 ? 1.035 : 1.0, "sine.inOut", 0, 0, k % 2 ? 0.35 : -0.3);
    }
    for (const [h, amt] of hits) { P(+(h - 0.04).toFixed(2), 1.0 + amt * 0.2, "sine.in"); P(+(h + 0.1).toFixed(2), 1.0 + amt, "power3.out", 0, 0, amt > 0.07 ? -0.5 : 0); P(+(h + 0.7).toFixed(2), 1.015, "power2.out", 0, 0, 0); }
  };
  pipSpan(7.0, 32.3, hits2);
  // C: "Yang tu belah EXTREME" punch then relax
  P(32.34, 1.0, "none"); P(32.62, 1.27, "power4.out", 0, 22, -0.6); P(33.74, 1.29, "sine.inOut", 0, 24, -0.2); P(35.2, 1.04, "sine.inOut", 0, 0, 0.7);
  P(35.78, 1.0, "power2.out", 0, 0, 0);
  const hits3 = [[36.52, 0.05], [37.72, 0.08], [38.84, 0.05], [39.85, 0.06], [41.65, 0.07], [46.76, 0.07], [49.55, 0.05], [50.98, 0.07]];
  pipSpan(35.78, 51.5, hits3);
  // D: CTA — push / pull to the emotion of each phrase
  P(51.6, 1.0, "none"); P(52.4, 1.08, "sine.inOut", 0, 8, 0.2); P(54.4, 1.1, "sine.inOut"); P(54.62, 1.21, "power4.out", 0, 16, 0.5);
  P(56.3, 1.24, "sine.inOut", 0, 20, 0.6); P(56.42, 1.18, "power2.out", 0, 14, 0.2); P(57.74, 1.27, "sine.inOut", 0, 22, 0.9);
  P(58.12, 1.07, "power3.inOut", 0, 0, -0.5); P(59.66, 1.15, "power4.out", 0, 10, 0.4); P(60.5, 1.09, "sine.inOut", 0, 0, 0);
  P(60.76, 1.17, "power4.out", 0, 12, -0.4); P(61.55, 1.1, "sine.inOut", 0, 4, 0); P(63.9, 1.24, "sine.inOut", 0, 18, 0.6); P(68.5, 1.3, "sine.inOut", 0, 22, 0);

  CAM.sort((a, b) => a.t - b.t);
  const dedup = [];
  for (const p of CAM) { if (dedup.length && p.t - dedup[dedup.length - 1].t < 0.03) dedup[dedup.length - 1] = p; else dedup.push(p); }
  gsap.set("#pres-cam", { scale: dedup[0].s, x: dedup[0].x, y: dedup[0].y, rotation: dedup[0].r });
  for (let i = 0; i < dedup.length - 1; i++) {
    const a = dedup[i], b = dedup[i + 1];
    tl.fromTo("#pres-cam", { scale: a.s, x: a.x, y: a.y, rotation: a.r }, { scale: b.s, x: b.x, y: b.y, rotation: b.r, duration: b.t - a.t, ease: b.e, immediateRender: false }, a.t);
  }

  /* ============ background parallax: follows the presenter punches ============ */
  const sAt = (t) => { // linear read of the presenter scale at time t
    for (let i = 0; i < dedup.length - 1; i++) if (t >= dedup[i].t && t <= dedup[i + 1].t) { const u = (t - dedup[i].t) / (dedup[i + 1].t - dedup[i].t); return dedup[i].s + (dedup[i + 1].s - dedup[i].s) * u; }
    return 1;
  };
  const punchTween = (sel, a, b, factor, base = 1) => {
    const poses = [{ t: a, s: sAt(a), e: "none" }];
    dedup.filter((p) => p.t > a + 0.02 && p.t < b - 0.02).forEach((p) => poses.push({ t: p.t, s: p.s, e: p.e }));
    poses.push({ t: b, s: sAt(b), e: "sine.inOut" });
    const sc = (s) => base + (s - 1) * factor;
    gsap.set(sel, { scale: sc(poses[0].s) });
    for (let i = 0; i < poses.length - 1; i++) {
      const p = poses[i], q = poses[i + 1];
      tl.fromTo(sel, { scale: sc(p.s) }, { scale: sc(q.s), duration: q.t - p.t, ease: q.e, immediateRender: false }, p.t);
    }
  };
  gsap.set("#bg", { transformOrigin: "50% 50%" });
  tl.fromTo("#bg", { scale: 1.0, x: -18 }, { scale: 1.1, x: 20, duration: 7, ease: "none" }, 0);
  gsap.set("#bg-punch", { transformOrigin: "50% 42%" });
  punchTween("#bg-punch", 0, 2.4, 0.42);
  punchTween("#bg-punch", 5.2, 6.5, 0.42);

  /* ============ transitions: cinematic slide-left (no shapes) ============ */
  // incoming layer slides in from the right; the layer underneath drifts left slower (parallax) and dims
  const SL = 0.62;
  const slide = (t, inSel, prevSel, dur = SL) => {
    tl.set(inSel, { autoAlpha: 1 }, t);
    tl.fromTo(inSel, { xPercent: 100, filter: "blur(10px)" }, { xPercent: 0, filter: "blur(0px)", duration: dur, ease: "power3.inOut", immediateRender: false }, t);
    if (prevSel) {
      tl.fromTo(prevSel, { xPercent: 0, filter: "blur(0px) brightness(1)" }, { xPercent: -30, filter: "blur(6px) brightness(0.55)", duration: dur, ease: "power3.inOut", immediateRender: false }, t);
      tl.set(prevSel, { autoAlpha: 0 }, t + dur + 0.04);
      tl.set(prevSel, { xPercent: 0, filter: "none" }, t + dur + 0.06);
    }
  };
  gsap.set("#map-wrap", { autoAlpha: 0 });

  /* ---- 1.45: talk -> map ---- */
  slide(1.45, "#map-wrap", "#bg-wrap", 0.7);
  /* ---- 5.28: map -> talk ---- */
  slide(5.26, "#bg-wrap", "#map-wrap", 0.6);
  /* ---- 6.45: talk -> map ---- */
  slide(6.45, "#map-wrap", "#bg-wrap", 0.7);

  /* ============ real footage / stills ============ */
  gsap.set(".bk", { autoAlpha: 0 });
  const KB = (sel, t0, t1, from, to) => tl.fromTo(sel, { scale: from.s, x: from.x, y: from.y }, { scale: to.s, x: to.x, y: to.y, duration: t1 - t0 + 0.7, ease: "none", immediateRender: false }, t0);
  const KBi = (id, t0, t1, from, to) => KB(`#${id} img`, t0, t1, from, to);
  const KBv = (id, t0, t1, from, to) => KB(`#${id} .kbw`, t0, t1, from, to);
  const bk = (t, id, prev, dur = 0.55) => slide(t, "#" + id, "#" + prev, dur);

  /* ---- 10.45: map -> Titlis ---- */
  slide(10.45, "#bk-04", "#map-wrap", 0.7); KBi("bk-04", 10.44, 11.9, { s: 1.0, x: 14, y: 0 }, { s: 1.14, x: -22, y: -8 });
  bk(11.9, "bv-snow", "bk-04", 0.5); KBv("bv-snow", 11.9, 13.5, { s: 1.0, x: 0, y: 0 }, { s: 1.12, x: -16, y: 6 });
  bk(13.5, "bv-matter", "bv-snow", 0.5); KBv("bv-matter", 13.5, 15.7, { s: 1.12, x: 14, y: 0 }, { s: 1.0, x: -14, y: 0 });
  bk(15.7, "bv-dolo", "bv-matter", 0.55); KBv("bv-dolo", 15.7, 18.45, { s: 1.0, x: 22, y: 4 }, { s: 1.13, x: -22, y: -4 });

  /* ---- 18.45: Cliff Walk ---- */
  bk(18.45, "bk-07", "bv-dolo", 0.6); KBi("bk-07", 18.45, 22.5, { s: 1.0, x: 24, y: 0 }, { s: 1.15, x: -24, y: -6 });
  bk(22.5, "bk-08", "bk-07"); KBi("bk-08", 22.5, 27.35, { s: 1.0, x: -20, y: 6 }, { s: 1.16, x: 24, y: -10 });
  bk(27.35, "bk-09", "bk-08"); KBi("bk-09", 27.35, 29.75, { s: 1.12, x: 12, y: 0 }, { s: 1.0, x: -12, y: 4 });
  bk(29.75, "bk-10", "bk-09"); KBi("bk-10", 29.75, 32.45, { s: 1.05, x: 0, y: 0 }, { s: 1.14, x: 0, y: 0 });

  /* ---- 32.3: back to the presenter over real footage ---- */
  bk(32.3, "bv-hills", "bk-10", 0.6);
  punchTween("#bv-hills .kbw", 32.3, 35.3, 0.42, 1.06);

  /* ---- 35.2: small towns ---- */
  bk(35.2, "bv-bern", "bv-hills", 0.55); KBv("bv-bern", 35.2, 37.0, { s: 1.0, x: 0, y: 0 }, { s: 1.12, x: -12, y: -6 });
  bk(37.0, "bv-castle", "bv-bern", 0.5); KBv("bv-castle", 37.0, 38.72, { s: 1.0, x: 14, y: 0 }, { s: 1.1, x: -14, y: 0 });
  bk(38.72, "bk-16", "bv-castle", 0.45); KBi("bk-16", 38.72, 39.85, { s: 1.0, x: 16, y: 0 }, { s: 1.1, x: -16, y: -6 });
  bk(39.85, "bk-12", "bk-16", 0.45); KBi("bk-12", 39.85, 40.96, { s: 1.1, x: -10, y: 0 }, { s: 1.0, x: 14, y: 0 });
  bk(40.96, "bk-13", "bk-12", 0.45); KBi("bk-13", 40.96, 41.65, { s: 1.0, x: 20, y: 6 }, { s: 1.12, x: -20, y: -6 });
  bk(41.65, "bk-21", "bk-13", 0.45); KBi("bk-21", 41.65, 43.0, { s: 1.0, x: -20, y: 0 }, { s: 1.12, x: 20, y: 0 });
  bk(43.0, "bk-20", "bk-21", 0.5); KBi("bk-20", 43.0, 44.8, { s: 1.12, x: 10, y: 0 }, { s: 1.0, x: -10, y: 0 });

  /* ---- 44.8: lakes ---- */
  bk(44.8, "bv-turq", "bk-20", 0.6); KBv("bv-turq", 44.8, 48.5, { s: 1.0, x: 0, y: 0 }, { s: 1.12, x: -20, y: -6 });
  bk(48.5, "bv-reflect", "bv-turq", 0.6); KBv("bv-reflect", 48.5, 51.65, { s: 1.12, x: 14, y: 0 }, { s: 1.0, x: -14, y: 0 });

  /* ---- 51.6: CTA over real footage ---- */
  bk(51.6, "bv-tree", "bv-reflect", 0.65);
  punchTween("#bv-tree .kbw", 51.6, 64.9, 0.42, 1.04);
  // closing dissolve to golden-hour (a soft cross-fade is the only non-slide transition)
  tl.set("#bv-sunset", { autoAlpha: 1 }, 64.9);
  tl.fromTo("#bv-sunset", { opacity: 0 }, { opacity: 1, duration: 1.0, ease: "power1.inOut", immediateRender: false }, 64.9);
  const s649 = sAt(64.9);
  tl.fromTo("#bv-sunset .kbw", { scale: 1.04 + (s649 - 1) * 0.42 }, { scale: 1.04 + (1.3 - 1) * 0.42, duration: 3.6, ease: "sine.inOut", immediateRender: false }, 64.9);
  tl.set("#bv-tree", { autoAlpha: 0 }, 66.0);

  /* ============ cinematic title typography ============ */
  const ttl = (sel, t0, t1) => {
    tl.set(sel, { autoAlpha: 1 }, t0);
    tl.fromTo(`${sel} .big`, { opacity: 0, letterSpacing: "0.26em", filter: "blur(18px)", y: 34 }, { opacity: 1, letterSpacing: "0.02em", filter: "blur(0px)", y: 0, duration: 1.15, ease: "power3.out", immediateRender: false }, t0);
    tl.fromTo(`${sel} .scr`, { clipPath: "inset(-40% 100% -40% -6%)", opacity: 0, x: -30 }, { clipPath: "inset(-40% -6% -40% -6%)", opacity: 1, x: 0, duration: 1.05, ease: "power2.inOut", immediateRender: false }, t0 + 0.5);
    tl.to(sel, { opacity: 0, y: -14, duration: 0.35, ease: "power2.in", immediateRender: false }, t1 - 0.35);
    tl.set(sel, { autoAlpha: 0 }, t1);
  };
  gsap.set(".ttl, .num, #elev", { autoAlpha: 0 });
  ttl("#t-ch", 2.55, 5.3);
  ttl("#t-titlis", 7.5, 13.45);
  ttl("#t-cliff", 18.5, 29.7);
  ttl("#t-spiez", 36.95, 44.7);
  const numIn = (sel, t0, t1) => {
    tl.set(sel, { autoAlpha: 1 }, t0);
    tl.fromTo(sel, { opacity: 0, scale: 0.9, y: 24, filter: "blur(10px)" }, { opacity: 1, scale: 1, y: 0, filter: "blur(0px)", duration: 0.6, ease: "power3.out", immediateRender: false }, t0);
    tl.to(sel, { opacity: 0, scale: 1.06, duration: 0.3, ease: "power2.in", immediateRender: false }, t1 - 0.3);
    tl.set(sel, { autoAlpha: 0 }, t1);
  };
  numIn("#num-cliff", 24.75, 29.7);
  numIn("#num-3000", 11.95, 13.45);
  // dotted elevation route
  tl.set("#elev", { autoAlpha: 1 }, 10.5);
  tl.fromTo("#elev", { opacity: 0, x: -30 }, { opacity: 1, x: 0, duration: 0.5, ease: "power3.out", immediateRender: false }, 10.5);
  tl.to("#elev", { opacity: 0, duration: 0.3, ease: "power2.in", immediateRender: false }, 13.15);
  tl.set("#elev", { autoAlpha: 0 }, 13.45);

  /* ============ floating portrait cards ============ */
  gsap.set(".rc", { autoAlpha: 0, transformPerspective: 1000, transformOrigin: "50% 50%" });
  const rc = (id, t0, t1, rot) => {
    const el = "#" + id;
    tl.set(el, { autoAlpha: 1 }, t0);
    tl.fromTo(el, { y: 70, rotationY: rot * 2.6, scale: 0.82, opacity: 0 }, { y: 0, rotationY: rot, scale: 1, opacity: 1, duration: 0.6, ease: "back.out(1.4)", immediateRender: false }, t0);
    tl.to(el, { y: -10, duration: t1 - t0 - 0.9, ease: "sine.inOut", immediateRender: false }, t0 + 0.6);
    tl.to(el, { opacity: 0, scale: 0.9, y: 30, duration: 0.28, ease: "power2.in", immediateRender: false }, t1 - 0.28);
    tl.set(el, { autoAlpha: 0 }, t1);
  };
  rc("rc-10", 29.85, 32.4, 7);
  rc("rc-11", 30.35, 32.4, -7);

  /* ============ captions ============ */
  const capsIn = $("#caps-in");
  const esc = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;");
  window.AKG_CAPS.forEach(([t0, t1, text, kw], i) => {
    const el = document.createElement("div");
    el.className = "cap"; el.id = "cap-" + i;
    const html = kw && text.includes(kw) ? esc(text).replace(esc(kw), `<span class="kw">${esc(kw)}</span>`) : esc(text);
    el.innerHTML = html; capsIn.appendChild(el);
    gsap.set(el, { autoAlpha: 0, transformOrigin: "50% 60%" });
    tl.set(el, { autoAlpha: 1 }, t0);
    tl.fromTo(el, { scale: 0.84, y: 12 }, { scale: 1, y: 0, duration: 0.16, ease: "back.out(2.2)", immediateRender: false }, t0);
    tl.set(el, { autoAlpha: 0 }, Math.max(t0 + 0.2, t1 - 0.01));
  });
  const capLane = (t, x, dur = 0.45) => tl.fromTo("#caps-in", { x: x === 0 ? 290 : 0 }, { x, duration: dur, ease: "power3.out", immediateRender: false }, t);
  gsap.set("#caps-in", { x: 0 });
  capLane(2.3, 290); capLane(5.26, 0, 0.3); capLane(6.45, 290); capLane(32.4, 0, 0.3); capLane(35.2, 290); capLane(51.62, 0);

  /* ============ CTA ============ */
  gsap.set("#brandbar, #tagline, #url, .cl", { autoAlpha: 0 });
  tl.set("#brandbar", { autoAlpha: 1 }, 52.2);
  tl.fromTo("#brandbar", { x: -60, opacity: 0 }, { x: 0, opacity: 1, duration: 0.6, ease: "power3.out", immediateRender: false }, 52.2);
  tl.set("#tagline", { autoAlpha: 1 }, 52.7);
  tl.fromTo("#tagline", { opacity: 0, letterSpacing: "0.9em" }, { opacity: 1, letterSpacing: "0.42em", duration: 0.9, ease: "power3.out", immediateRender: false }, 52.7);
  const cl = (id, t, fromX) => {
    tl.set("#" + id, { autoAlpha: 1 }, t);
    tl.fromTo("#" + id, { x: fromX, opacity: 0, filter: "blur(8px)" }, { x: 0, opacity: 1, filter: "blur(0px)", duration: 0.55, ease: "power3.out", immediateRender: false }, t);
  };
  cl("cl-1", 58.3, -80); cl("cl-2", 59.9, 80); cl("cl-3", 60.9, -80); cl("cl-4", 62.05, 80);
  tl.set("#url", { autoAlpha: 1 }, 63.6);
  tl.fromTo("#url", { y: 30, opacity: 0, letterSpacing: "0.5em" }, { y: 0, opacity: 1, letterSpacing: "0.28em", duration: 0.8, ease: "power3.out", immediateRender: false }, 63.6);

  /* ============ live HUD (deterministic functions of t) ============ */
  const counts = Array.from(document.querySelectorAll(".count"));
  const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
  const eio = (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);
  const clipR = $("#elev-clip-r"), elevB = $("#elev-b");
  const hud = (t) => {
    for (const c of counts) {
      const f = +c.dataset.from, to = +c.dataset.to, t0 = +c.dataset.t0, t1 = +c.dataset.t1;
      const p = eio(clamp((t - t0) / (t1 - t0)));
      c.textContent = Math.round(f + (to - f) * p).toLocaleString("en-US");
    }
    if (clipR) clipR.setAttribute("width", (560 * eio(clamp((t - 10.6) / 2.2))).toFixed(1));
    if (elevB) elevB.setAttribute("opacity", String(clamp((t - 12.7) / 0.3)));
  };
  window.addEventListener("hf-seek", (e) => hud(e.detail.time));
  hud(0);

  window.AKG_TL = tl;
})();
