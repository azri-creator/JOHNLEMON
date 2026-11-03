(function () {
  const tl = gsap.timeline({ paused: true });
  const T_MAIN = 77.067;

  /* ============ transitions: vertical "lift" (scene rises from below, like a cable car climbing) ============ */
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
  // slow camera drift on each place (linear, so it never stops moving while visible)
  const KB = (id, t0, t1, from, to) =>
    tl.fromTo(`#${id} .kb`, { x: from.x || 0, y: from.y || 0, scale: from.s || 1, rotation: from.r || 0 },
      { x: to.x || 0, y: to.y || 0, scale: to.s || 1, rotation: to.r || 0, duration: t1 - t0 + LIFT, ease: "none", immediateRender: false }, t0);

  gsap.set(".bk", { autoAlpha: 0, transformOrigin: "50% 50%" });
  gsap.set(".bk .kb", { transformOrigin: "50% 45%" });

  // [id, start, end, from, to]
  const SC = [
    ["bk10", 0, 3.55, { s: 1.0 }, { s: 1.16, y: 30 }],                       // hook: looking down the bridge, slow vertigo push
    ["bk07", 3.55, 5.35, { x: -600 }, { x: -1250 }],
    ["bk11", 5.35, 11.6, { s: 1.0, y: -40 }, { s: 1.12, y: 40 }],
    ["bk09", 11.6, 14.0, { s: 1.12, x: 30 }, { s: 1.0, x: -30 }],
    ["bk08", 14.0, 15.75, { s: 1.05 }, { s: 1.14, x: -20 }],
    ["bk06", 15.75, 19.6, { x: -1150 }, { x: -2150 }],                         // "kiri kanan": pan across the panorama
    ["bk05", 19.6, 24.35, { s: 1.0, x: 20 }, { s: 1.12, x: -30 }],
    ["bkmap", 24.35, 29.2, { s: 1.12 }, { s: 1.2 }],                         // vector map: Luzern -> Engelberg -> Titlis
    ["bk02", 29.2, 30.15, { s: 1.0 }, { s: 1.08, x: -20 }],
    ["bk17", 30.15, 34.75, { s: 1.2, r: -3 }, { s: 1.2, r: 5 }],              // Rotair: the view slowly turns
    ["bk03", 34.75, 37.85, { s: 1.0, y: 30 }, { s: 1.12, y: -30 }],
    ["bk04", 37.85, 44.55, { s: 1.0, x: 30 }, { s: 1.14, x: -40 }],
    ["bk07b", 44.55, 47.1, { x: -1700 }, { x: -1100 }],
    ["bkg1", 47.1, 49.9, { s: 1.0 }, { s: 1.12 }],
    ["bkg2", 49.9, 52.4, { s: 1.12, y: 30 }, { s: 1.0, y: -20 }],
    ["bkg3", 52.4, 54.1, { s: 1.0, x: 20 }, { s: 1.1, x: -20 }],
    ["bvlake", 54.1, 59.4, { s: 1.0 }, { s: 1.08, y: -20 }],
    ["bvtrain", 67.9, 70.05, { s: 1.06 }, { s: 1.0 }],
    ["bvsnow", 70.05, 74.3, { s: 1.0 }, { s: 1.08 }],
    ["bvsun", 74.3, T_MAIN, { s: 1.0, y: 20 }, { s: 1.08, y: -20 }],
  ];
  tl.set("#bk10", { autoAlpha: 1 }, 0);
  SC.forEach(([id, t0, t1, a, b], i) => {
    if (i > 0) {
      const prev = SC[i - 1];
      // the itinerary page sits between the lake and the train: the lake is hidden by the page, the train rises out from under it
      if (id === "bvtrain") { tl.set("#bvtrain", { autoAlpha: 1 }, t0); tl.set("#bvlake", { autoAlpha: 0 }, 59.4 + LIFT + 0.05); }
      else lift(t0, "#" + id, "#" + prev[0]);
    }
    KB(id, t0, t1, a, b);
  });

  /* ============ presenter: calm shot sizes (sine glides only, no snaps) ============ */
  gsap.set("#pres-cam", { transformOrigin: "540px 1080px" });
  const CAM = [ // [time, scale, x]
    [0, 1.2, 0], [3.4, 1.0, 0], [5.4, 1.1, -10], [10.7, 1.24, 0], [11.75, 1.0, 0], [15.8, 1.0, 12], [19.6, 1.12, 0],
    [24.4, 1.04, 0], [26.85, 1.14, -8], [30.2, 1.0, 0], [32.4, 1.18, 0], [34.8, 1.05, 0], [37.9, 1.12, 8], [42.55, 1.26, 0],
    [44.6, 1.0, 0], [47.15, 1.08, 0], [51.6, 1.2, -6], [54.15, 1.04, 0], [57.85, 1.28, 0], [59.4, 1.28, 0],
    [67.9, 1.06, 0], [70.1, 1.0, 0], [72.55, 1.16, 0], [74.35, 1.05, 0], [75.85, 1.2, 0], [77.9, 1.24, 0],
  ];
  gsap.set("#pres-cam", { scale: CAM[0][1], x: CAM[0][2] });
  for (let i = 0; i < CAM.length - 1; i++) {
    const [ta, sa, xa] = CAM[i], [tb, sb, xb] = CAM[i + 1];
    const glide = Math.min(1.2, tb - ta); // glide into the next size, hold until then
    tl.fromTo("#pres-cam", { scale: sa, x: xa }, { scale: sb, x: xb, duration: glide, ease: "sine.inOut", immediateRender: false }, tb - glide);
  }
  // itinerary is full frame: presenter steps away underneath it and is back when the page lifts off
  tl.set("#pres-wrap", { autoAlpha: 0 }, 59.4 + LIFT + 0.05);
  tl.set("#pres-wrap", { autoAlpha: 1 }, 67.9);

  /* ============ itinerary page: tilted plane, scrolls from the hero to Hari 03 (Titlis) and on to Hari 09 ============ */
  gsap.set("#itin", { autoAlpha: 0 });
  tl.set("#itin", { autoAlpha: 1 }, 59.4);
  tl.fromTo("#itin", { yPercent: 100, filter: "blur(14px)" }, { yPercent: 0, filter: "blur(0px)", duration: 0.8, ease: "power3.inOut", immediateRender: false }, 59.4);
  tl.fromTo("#itin-tilt", { transformPerspective: 1900, rotationX: 20, rotationY: -14, rotationZ: 3, scale: 1.3 },
    { transformPerspective: 1900, rotationX: 11, rotationY: -7, rotationZ: 1.5, scale: 1.42, duration: 8.5, ease: "sine.inOut", immediateRender: false }, 59.4);
  tl.fromTo("#itin-scroll", { y: 30 }, { y: -880, duration: 3.9, ease: "power2.inOut", immediateRender: false }, 59.6);   // hero -> Hari 03
  tl.fromTo("#d3-line", { scaleX: 0 }, { scaleX: 1, duration: 0.7, ease: "power2.out", immediateRender: false }, 63.3);
  tl.fromTo("#itin-scroll", { y: -880 }, { y: -1260, duration: 3.6, ease: "power2.inOut", immediateRender: false }, 64.5);                                           // on to Hari 05-09
  // the page lifts off upward and the train is underneath
  tl.fromTo("#itin", { yPercent: 0, filter: "blur(0px)" }, { yPercent: -100, filter: "blur(10px)", duration: 0.75, ease: "power3.inOut", immediateRender: false }, 67.9);
  tl.set("#itin", { autoAlpha: 0 }, 68.7);
  tl.fromTo("#bvtrain", { yPercent: 18 }, { yPercent: 0, duration: 0.75, ease: "power3.out", immediateRender: false }, 67.9);


  /* ============ vector map: official outline draws, zoom to central Switzerland, trail A (Luzern) -> B (Titlis) ============ */
  gsap.set(["#ch-line", "#trail", "#trail-case"], { attr: { "stroke-dashoffset": 1 } });
  gsap.set(["#ch-fill", "#ch-lakes"], { opacity: 0 });
  gsap.set("#mapcam", { x: 0, y: 0, scale: 1, svgOrigin: "0 0" });
  gsap.set(".pin", { autoAlpha: 0 });
  tl.fromTo("#ch-line", { attr: { "stroke-dashoffset": 1 } }, { attr: { "stroke-dashoffset": 0 }, duration: 0.95, ease: "power1.inOut", immediateRender: false }, 24.45);
  tl.fromTo("#ch-fill", { opacity: 0 }, { opacity: 1, duration: 0.6, ease: "sine.out", immediateRender: false }, 24.75);
  tl.fromTo("#ch-lakes", { opacity: 0 }, { opacity: 1, duration: 0.5, ease: "sine.out", immediateRender: false }, 25.05);
  tl.fromTo("#mapcam", { x: 0, y: 0, scale: 1 }, { x: -2072.59, y: -2154.99, scale: 4.6, duration: 1.15, ease: "sine.inOut", immediateRender: false }, 25.4);
  const pinIn = (sel, t) => {
    tl.set(sel, { autoAlpha: 1 }, t);
    tl.fromTo(`${sel} i`, { scale: 0 }, { scale: 1, duration: 0.4, ease: "back.out(2.2)", immediateRender: false }, t);
    tl.fromTo(`${sel} span`, { opacity: 0, x: 0 }, { opacity: 1, duration: 0.35, ease: "sine.out", immediateRender: false }, t + 0.12);
  };
  pinIn("#pin-a", 26.45);
  tl.fromTo(["#trail-case", "#trail"], { attr: { "stroke-dashoffset": 1 } }, { attr: { "stroke-dashoffset": 0 }, duration: 1.35, ease: "sine.inOut", immediateRender: false }, 26.6);
  pinIn("#pin-e", 27.4);
  pinIn("#pin-b", 27.9);

  /* ============ titles ============ */
  gsap.set(".hero, .place, #url", { autoAlpha: 0 });
  // hero word: script writes on left->right, big word rises with blur and its tracking settles
  const hero = (sel, t0, t1) => {
    tl.set(sel, { autoAlpha: 1 }, t0);
    tl.fromTo(`${sel} .big`, { opacity: 0, y: 60, filter: "blur(16px)", letterSpacing: "0.04em" }, { opacity: 1, y: 0, filter: "blur(0px)", letterSpacing: "-0.035em", duration: 0.9, ease: "power3.out", immediateRender: false }, t0);
    tl.fromTo(`${sel} .scr`, { clipPath: "inset(-30% 100% -30% -5%)" }, { clipPath: "inset(-30% -5% -30% -5%)", duration: 0.9, ease: "sine.inOut", immediateRender: false }, t0 + 0.25);
    tl.fromTo(sel, { scale: 1 }, { scale: 1.04, duration: t1 - t0, ease: "none", immediateRender: false }, t0);
    tl.to(sel, { opacity: 0, y: -20, filter: "blur(10px)", duration: 0.4, ease: "power2.in" }, t1 - 0.4);
    tl.set(sel, { autoAlpha: 0, filter: "none" }, t1);
  };
  // place title: kicker fades up, each serif line rises out of a mask
  const place = (sel, t0, t1) => {
    tl.set(sel, { autoAlpha: 1 }, t0);
    tl.fromTo(`${sel} .kick`, { opacity: 0, y: 24 }, { opacity: 1, y: 0, duration: 0.6, ease: "power3.out", immediateRender: false }, t0);
    tl.fromTo(`${sel} .ln`, { clipPath: "inset(0 0 100% 0)", y: 70 }, { clipPath: "inset(0 0 -10% 0)", y: 0, duration: 0.8, stagger: 0.14, ease: "power3.out", immediateRender: false }, t0 + 0.15);
    tl.fromTo(sel, { scale: 1 }, { scale: 1.03, duration: t1 - t0, ease: "none", immediateRender: false }, t0);
    tl.to(sel, { opacity: 0, y: -16, filter: "blur(8px)", duration: 0.4, ease: "power2.in" }, t1 - 0.4);
    tl.set(sel, { autoAlpha: 0, filter: "none" }, t1);
  };
  hero("#h-gayat", 0.3, 3.45);
  place("#p-cliff", 3.65, 7.1);
  hero("#h-alt", 7.25, 10.75);
  place("#p-titlis", 25.6, 28.8);
  hero("#h-360", 32.9, 35.9);
  place("#p-glacier", 47.8, 50.0);
  hero("#h-exp", 57.95, 59.45);
  place("#p-pakej", 70.1, 72.5);
  hero("#h-price", 72.6, 77.05);
  tl.set("#url", { autoAlpha: 1 }, 75.0);
  tl.fromTo("#url", { opacity: 0, y: 24, letterSpacing: "0.2em" }, { opacity: 1, y: 0, letterSpacing: "0.04em", duration: 0.7, ease: "power3.out", immediateRender: false }, 75.0);
  tl.set("#url", { autoAlpha: 0 }, T_MAIN + 0.7);

  /* ============ captions ============ */
  const caps = document.getElementById("caps");
  const esc = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;");
  window.AKG_CAPS.forEach(([t0, t1, text, kw], i) => {
    const el = document.createElement("div");
    el.className = "cap" + (t0 >= 59.3 ? " ak" : "");
    el.id = "cap-" + i;
    el.innerHTML = kw && text.includes(kw) ? esc(text).replace(esc(kw), `<span class="kw">${esc(kw)}</span>`) : esc(text);
    caps.appendChild(el);
    gsap.set(el, { autoAlpha: 0, transformOrigin: "50% 60%" });
    tl.set(el, { autoAlpha: 1 }, t0);
    tl.fromTo(el, { y: 18, opacity: 0 }, { y: 0, opacity: 1, duration: 0.18, ease: "power2.out", immediateRender: false }, t0);
    tl.set(el, { autoAlpha: 0 }, Math.max(t0 + 0.2, t1 - 0.02));
  });

  /* ============ outro: rises in over the last frame ============ */
  gsap.set("#outro-wrap", { autoAlpha: 0 });
  lift(T_MAIN, "#outro-wrap", null, 0.7);
  tl.set("#broll, #pres-wrap", { autoAlpha: 0 }, T_MAIN + 0.75);

  tl.set({}, {}, 86.167);
  window.AKG_TL = tl;
})();
