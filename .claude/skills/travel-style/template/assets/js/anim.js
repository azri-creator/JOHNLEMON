(function () {
  const tl = gsap.timeline({ paused: true });
  const T_MAIN = 42.36;
  const T_END = 45.6;

  /* ============ transitions: vertical "lift" (incoming rises from below; a covering layer lifts off upward) ============ */
  const LIFT = 0.7;
  const lift = (t, inSel, outSel, dur = LIFT) => {
    tl.set(inSel, { autoAlpha: 1 }, t);
    tl.fromTo(inSel, { yPercent: 100, filter: "blur(14px)" }, { yPercent: 0, filter: "blur(0px)", duration: dur, ease: "power3.inOut", immediateRender: false }, t);
    if (outSel) {
      tl.fromTo(outSel, { yPercent: 0, filter: "blur(0px)" }, { yPercent: -24, filter: "blur(8px)", duration: dur, ease: "power3.inOut", immediateRender: false }, t);
      tl.set(outSel, { autoAlpha: 0 }, t + dur + 0.03);
      tl.set(outSel, { yPercent: 0, filter: "none" }, t + dur + 0.05);
    }
  };
  const liftOff = (t, sel) => {
    tl.fromTo(sel, { yPercent: 0, filter: "blur(0px)" }, { yPercent: -100, filter: "blur(10px)", duration: 0.75, ease: "power3.inOut", immediateRender: false }, t);
    tl.set(sel, { autoAlpha: 0 }, t + 0.78);
    tl.set(sel, { yPercent: 0, filter: "none" }, t + 0.8);
  };
  // slow linear drift on each real place
  const KB = (id, t0, t1, from, to) =>
    tl.fromTo(`#${id} .kb`, { x: from.x || 0, y: from.y || 0, scale: from.s || 1 },
      { x: to.x || 0, y: to.y || 0, scale: to.s || 1, duration: t1 - t0 + LIFT, ease: "none", immediateRender: false }, t0);

  gsap.set(".bk", { autoAlpha: 0, transformOrigin: "50% 50%" });
  gsap.set(".bk .kb", { transformOrigin: "50% 45%" });

  /* backgrounds under the presenter */
  tl.set("#bkown1", { autoAlpha: 1 }, 0);
  tl.set("#bklobby", { autoAlpha: 1 }, 14.7);          // swapped in while the destination cutaway covers the frame
  tl.set("#bkown1", { autoAlpha: 0 }, 15.0);
  KB("bklobby", 14.7, 19.98, { s: 1.0, x: 20 }, { s: 1.09, x: -20 });
  lift(19.98, "#bkmap", "#bklobby");                    // "Menariknya": the map rises behind the presenter
  KB("bkmap", 19.98, 28.15, { s: 1.06 }, { s: 1.14 });
  lift(28.15, "#bkstreet", "#bkmap");
  KB("bkstreet", 28.15, 31.0, { s: 1.0, x: 20 }, { s: 1.08, x: -24 });
  tl.set("#bkcta", { autoAlpha: 1 }, 37.1);             // waiting under the seated shot
  KB("bkcta", 37.1, T_END, { s: 1.0, y: 24 }, { s: 1.12, y: -34 });

  /* full-frame layers over the presenter: cutaways and the seated L5 shots */
  lift(5.6, "#ccamel", null);   KB("ccamel", 5.6, 8.9, { s: 1.0 }, { s: 1.08, y: -16 });   liftOff(8.9, "#ccamel");
  lift(12.5, "#cview", null); KB("cview", 12.5, 15.4, { s: 1.08 }, { s: 1.0, y: -20 }); liftOff(15.4, "#cview");
  lift(31.0, "#cown5a", "#bkstreet");
  lift(33.3, "#ccouple", "#cown5a"); KB("ccouple", 33.3, 35.9, { s: 1.0 }, { s: 1.08 });
  lift(35.9, "#cown5b", "#ccouple");
  lift(37.84, "#cown6", "#cown5b");                     // CTA shot (own backdrop; its matte kept part of the background)

  /* ============ presenter: calm glides (sine only), own background follows the same camera ============ */
  const BOTH = ["#pres-cam", "#own-cam"];
  gsap.set(BOTH, { transformOrigin: "540px 1080px", scale: 1, x: 0, y: 0 });
  let cur = { s: 1, x: 0, y: 0 };
  const glide = (t, dur, s, x, y, targets = "#pres-cam") => {
    tl.fromTo(targets, { scale: cur.s, x: cur.x, y: cur.y }, { scale: s, x, y, duration: dur, ease: "sine.inOut", immediateRender: false }, t);
    cur = { s, x, y };
  };
  glide(3.0, 1.2, 1.08, 0, 0, BOTH);     // "inilah masanya"
  glide(7.7, 1.2, 1.0, 0, 0, BOTH);      // under the camel cutaway
  glide(9.9, 1.2, 1.08, 0, 0, BOTH);     // "nikmati impian"
  glide(14.0, 1.2, 1.0, 0, 0, BOTH);     // under the destination cutaway
  glide(16.6, 1.2, 1.06, 0, 0);          // "mulakan perancangan"
  glide(20.0, 1.0, 1.0, 0, 210);         // map: presenter steps down so the route sits above the head
  glide(28.15, 0.9, 1.06, 0, 0);         // second hero word behind the head
  glide(31.2, 0.5, 1.0, 0, 0);           // hidden under the seated shots
  tl.set("#pres-wrap", { autoAlpha: 0 }, 31.0);
  // end: presenter drifts up and away, the footage softens, the logo rises
  tl.fromTo("#cown6", { yPercent: 0, filter: "blur(0px)", opacity: 1 }, { yPercent: -24, filter: "blur(8px)", opacity: 0, duration: 0.7, ease: "power3.inOut", immediateRender: false }, 42.3);
  tl.fromTo("#bkcta .kb video", { filter: "blur(0px)" }, { filter: "blur(16px)", duration: 0.8, ease: "sine.inOut", immediateRender: false }, 42.3);

  /* ============ vector map: flight origin -> pin A, zoom in, trail A -> via -> B (data: assets/js/routemap.js) ============ */
  const M = window.ROUTEMAP;
  document.getElementById("mapwrap").innerHTML = M.svg;
  const svgEl = document.getElementById("routemap");
  const A = M.arc.a, C = M.arc.c, B = M.arc.b;
  const arcD = `M${A[0]},${A[1]} Q${C[0]},${C[1]} ${B[0]},${B[1]}`;
  ["arc", "arc-case"].forEach((id) => document.getElementById(id).setAttribute("d", arcD));
  ["trail", "trail-case"].forEach((id) => document.getElementById(id).setAttribute("d", M.trail));
  const place2 = (id, p, dx = 0, dy = 0) => gsap.set(id, { left: p[0] + dx, top: p[1] + dy });
  place2("#lab-dest", M.labels0.dest, 0, 70);
  place2("#lab-origin", M.labels0.origin, -80, 100);
  place2("#pin-a", M.pins.a);
  place2("#pin-b", M.pins.b);
  gsap.set(".pin, .mlab, #plane", { autoAlpha: 0 });
  gsap.set(["#map-dest", "#map-origin"], { attr: { "fill-opacity": 0.2 } });

  tl.fromTo(["#map-dest", "#map-origin"], { attr: { "fill-opacity": 0.2 } }, { attr: { "fill-opacity": 1 }, duration: 0.6, ease: "sine.out", immediateRender: false }, 20.45);
  const labIn = (sel, t) => {
    tl.set(sel, { autoAlpha: 1 }, t);
    tl.fromTo(`${sel} span`, { opacity: 0, y: 16 }, { opacity: 1, y: 0, duration: 0.4, ease: "power3.out", immediateRender: false }, t);
  };
  labIn("#lab-dest", 20.7);
  labIn("#lab-origin", 20.9);

  // flight: one proxy drives the plane and the arc reveal so they stay together on any seek
  const qb = (p, a, c, b) => (1 - p) * (1 - p) * a + 2 * (1 - p) * p * c + p * p * b;
  const fly = { p: 0 };
  const setFlight = () => {
    const p = fly.p;
    const x = qb(p, A[0], C[0], B[0]), y = qb(p, A[1], C[1], B[1]);
    const dx = 2 * (1 - p) * (C[0] - A[0]) + 2 * p * (B[0] - C[0]);
    const dy = 2 * (1 - p) * (C[1] - A[1]) + 2 * p * (B[1] - C[1]);
    gsap.set("#plane", { x, y, rotation: (Math.atan2(dy, dx) * 180) / Math.PI });
    document.getElementById("arc").setAttribute("stroke-dashoffset", 1 - p);
    document.getElementById("arc-case").setAttribute("stroke-dashoffset", 1 - p);
  };
  setFlight();
  tl.set("#plane", { autoAlpha: 1 }, 21.3);
  tl.fromTo(fly, { p: 0 }, { p: 1, duration: 2.2, ease: "sine.inOut", immediateRender: false, onUpdate: setFlight }, 21.3);
  tl.to(["#plane", "#arcsvg", "#lab-dest", "#lab-origin"], { opacity: 0, duration: 0.3, ease: "sine.in" }, 23.55);

  // zoom: log-interpolated viewBox so the fly-in speed feels even from 7452 down to 144 units
  const c0 = M.cam0, c1 = M.cam1;
  const zoom = { z: 0 };
  const setZoom = () => {
    const w = c0[2] * Math.pow(c1[2] / c0[2], zoom.z);
    const f = (c0[2] - w) / (c0[2] - c1[2]);
    const h = (w * 1920) / 1080;
    const cx = c0[0] + c0[2] / 2 + f * (c1[0] + c1[2] / 2 - (c0[0] + c0[2] / 2));
    const cy = c0[1] + c0[3] * (420 / 1920) + f * (c1[1] + c1[3] * (420 / 1920) - (c0[1] + c0[3] * (420 / 1920)));
    svgEl.setAttribute("viewBox", `${(cx - w / 2).toFixed(3)} ${(cy - h * (420 / 1920)).toFixed(3)} ${w.toFixed(3)} ${h.toFixed(3)}`);
  };
  setZoom();
  tl.fromTo(zoom, { z: 0 }, { z: 1, duration: 1.2, ease: "sine.inOut", immediateRender: false, onUpdate: setZoom }, 23.65);

  const pinIn = (sel, t) => {
    tl.set(sel, { autoAlpha: 1 }, t);
    tl.fromTo(`${sel} i`, { scale: 0 }, { scale: 1, duration: 0.4, ease: "back.out(2.2)", immediateRender: false }, t);
    tl.fromTo(`${sel} span`, { opacity: 0, y: 14 }, { opacity: 1, y: 0, duration: 0.35, ease: "sine.out", immediateRender: false }, t + 0.12);
    tl.fromTo(`${sel} em`, { clipPath: "inset(-30% 100% -30% -5%)" }, { clipPath: "inset(-30% -5% -30% -5%)", duration: 0.7, ease: "sine.inOut", immediateRender: false }, t + 0.25);
  };
  pinIn("#pin-a", 24.95);
  tl.fromTo(["#trail-case", "#trail"], { attr: { "stroke-dashoffset": 1 } }, { attr: { "stroke-dashoffset": 0 }, duration: 1.3, ease: "sine.inOut", immediateRender: false }, 26.25);
  pinIn("#pin-b", 27.5);

  /* ============ titles ============ */
  gsap.set(".hero, .place", { autoAlpha: 0 });
  const hero = (sel, t0, t1) => {
    tl.set(sel, { autoAlpha: 1 }, t0);
    tl.fromTo(`${sel} .big`, { opacity: 0, y: 60, filter: "blur(16px)", letterSpacing: "0.04em" }, { opacity: 1, y: 0, filter: "blur(0px)", letterSpacing: "-0.035em", duration: 0.9, ease: "power3.out", immediateRender: false }, t0);
    tl.fromTo(`${sel} .scr`, { clipPath: "inset(-30% 100% -30% -5%)" }, { clipPath: "inset(-30% -5% -30% -5%)", duration: 0.9, ease: "sine.inOut", immediateRender: false }, t0 + 0.25);
    tl.fromTo(sel, { scale: 1 }, { scale: 1.04, duration: t1 - t0, ease: "none", immediateRender: false }, t0);
    tl.to(sel, { opacity: 0, y: -20, filter: "blur(10px)", duration: 0.4, ease: "power2.in" }, t1 - 0.4);
    tl.set(sel, { autoAlpha: 0, filter: "none" }, t1);
  };
  const place = (sel, t0, t1) => {
    tl.set(sel, { autoAlpha: 1 }, t0);
    tl.fromTo(`${sel} .kick`, { opacity: 0, y: 24 }, { opacity: 1, y: 0, duration: 0.6, ease: "power3.out", immediateRender: false }, t0);
    tl.fromTo(`${sel} .ln`, { clipPath: "inset(0 0 100% 0)", y: 70 }, { clipPath: "inset(0 0 -10% 0)", y: 0, duration: 0.8, stagger: 0.14, ease: "power3.out", immediateRender: false }, t0 + 0.15);
    tl.fromTo(sel, { scale: 1 }, { scale: 1.03, duration: t1 - t0, ease: "none", immediateRender: false }, t0);
    tl.to(sel, { opacity: 0, y: -16, filter: "blur(8px)", duration: 0.4, ease: "power2.in" }, t1 - 0.4);
    tl.set(sel, { autoAlpha: 0, filter: "none" }, t1);
  };
  hero("#h-years", 0.3, 3.2);
  place("#p-impian", 5.95, 8.85);
  hero("#h-syukur", 9.05, 10.45);
  place("#p-dest", 12.9, 15.35);
  place("#p-mk", 15.65, 17.9);
  hero("#h-yakin", 18.95, 19.95);
  hero("#h-risau", 28.4, 30.95);
  place("#p-couple", 33.7, 35.85);
  place("#p-wa", 38.2, 41.0);

  /* ============ captions ============ */
  const caps = document.getElementById("caps");
  const esc = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;");
  window.AKG_CAPS.forEach(([t0, t1, text, kw], i) => {
    const el = document.createElement("div");
    el.className = "cap" + (t0 >= 15.4 ? " mk" : "");
    el.id = "cap-" + i;
    el.innerHTML = kw && text.includes(kw) ? esc(text).replace(esc(kw), `<span class="kw">${esc(kw)}</span>`) : esc(text);
    caps.appendChild(el);
    gsap.set(el, { autoAlpha: 0, transformOrigin: "50% 60%" });
    tl.set(el, { autoAlpha: 1 }, t0);
    tl.fromTo(el, { y: 18, opacity: 0 }, { y: 0, opacity: 1, duration: 0.18, ease: "power2.out", immediateRender: false }, t0);
    tl.set(el, { autoAlpha: 0 }, Math.max(t0 + 0.2, t1 - 0.02));
  });

  /* ============ end: logo rises over the softened CTA footage ============ */
  gsap.set("#end", { autoAlpha: 0 });
  lift(T_MAIN - 0.06, "#end", null, 0.8);
  tl.fromTo("#end-sweep", { backgroundPosition: "100% 0" }, { backgroundPosition: "0% 0", duration: 1.3, ease: "sine.inOut", immediateRender: false }, 43.2);
  tl.fromTo("#end-scr", { clipPath: "inset(-30% 100% -30% -5%)" }, { clipPath: "inset(-30% -5% -30% -5%)", duration: 1.0, ease: "sine.inOut", immediateRender: false }, 42.95);
  tl.fromTo("#end-wa", { opacity: 0, y: 24 }, { opacity: 1, y: 0, duration: 0.6, ease: "power3.out", immediateRender: false }, 43.5);

  tl.set({}, {}, T_END);
  window.AKG_TL = tl;
})();
