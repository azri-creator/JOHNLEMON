      // ================= S2 · inside the lens: voice rings → radial disc → dot =================
      {
        let bars = "";
        for (let i = 0; i < 56; i++) {
          const a = (i / 56) * 360;
          bars += `<rect x="535" y="${700 - 262}" width="11" height="96" fill="${RED}" transform="rotate(${a} 540 700)"/>`;
        }
        let dots = "";
        for (let i = 0; i < 40; i++) {
          const a = (i / 40) * Math.PI * 2;
          dots += `<circle cx="${540 + 300 * Math.cos(a)}" cy="${700 + 300 * Math.sin(a)}" r="12" fill="${RED}"/>`;
        }
        let rings = "";
        for (let i = 0; i < 5; i++) rings += `<circle class="s2ring" cx="540" cy="700" r="120" fill="none" stroke="${i % 2 ? CR : RED}" stroke-width="16"/>`;
        $("v2").innerHTML = `
          <rect width="1080" height="1920" fill="#0b0908"/>
          <g id="s2rings">${rings}</g>
          <g id="s2mic">
            <rect x="480" y="520" width="120" height="230" rx="60" fill="${CR}"/>
            <rect x="480" y="585" width="120" height="12" fill="${BLK}"/><rect x="480" y="620" width="120" height="12" fill="${BLK}"/><rect x="480" y="655" width="120" height="12" fill="${BLK}"/>
            <path d="M 440 680 Q 440 820 540 820 Q 640 820 640 680" fill="none" stroke="${CR}" stroke-width="16"/>
            <rect x="532" y="820" width="16" height="80" fill="${CR}"/><rect x="470" y="895" width="140" height="18" fill="${RED}"/>
          </g>
          <circle id="s2iris" cx="540" cy="700" r="1300" fill="${CR}"/>
          <g id="s2discS"><g id="s2disc">
            ${dots}${bars}
            <circle cx="540" cy="700" r="150" fill="${RED2}"/>
            <circle cx="540" cy="700" r="124" fill="none" stroke="${RED}" stroke-width="14"/>
            <circle cx="540" cy="700" r="92" fill="none" stroke="${BLK}" stroke-width="10"/>
            <circle cx="540" cy="700" r="62" fill="none" stroke="${RED}" stroke-width="12"/>
            <circle cx="540" cy="700" r="30" fill="${BLK}"/><circle cx="540" cy="700" r="16" fill="${CR}"/>
          </g></g>
          <circle id="s2dot" cx="540" cy="700" r="46" fill="${RED}"/>`;
      }
      tl.set("#s2", { opacity: 1 }, 6.43).set("#s2", { opacity: 0 }, 9.2);
      tl.fromTo("#c2", { scale: 1.06, transformOrigin: "540px 700px" }, { scale: 1, duration: 2.8, ease: "sine.out" }, 6.43);
      tl.fromTo("#s2mic", { scale: 0.4, opacity: 0, svgOrigin: "540 700" }, { scale: 1, opacity: 1, duration: 0.45, ease: "back.out(1.8)" }, 6.45);
      tl.fromTo(".s2ring", { scale: 0.5, svgOrigin: "540 700" }, { scale: 3.2, duration: 1.0, ease: "sine.out", stagger: 0.17 }, 6.59);
      tl.fromTo(".s2ring", { opacity: 0 }, { opacity: 1, duration: 0.08, ease: "none", stagger: 0.17 }, 6.59);
      tl.to(".s2ring", { opacity: 0, duration: 0.8, ease: "power2.in", stagger: 0.17 }, 6.75);
      tl.to("#s2mic", { scale: 0, rotation: 40, svgOrigin: "540 700", duration: 0.3, ease: "back.in(1.6)" }, 7.58);
      tl.fromTo("#s2disc", { scale: 0, rotation: -120, svgOrigin: "540 700" }, { scale: 1, rotation: 0, duration: 0.55, ease: "back.out(1.4)" }, 7.66);
      tl.to("#s2disc", { rotation: 140, svgOrigin: "540 700", duration: 1.0, ease: "sine.inOut" }, 8.22);
      tl.to("#s2discS", { scale: 0.16, svgOrigin: "540 700", duration: 0.55, ease: "power2.inOut" }, 8.42);
      tl.fromTo("#s2iris", { scale: 0, svgOrigin: "540 700" }, { scale: 1, duration: 0.5, ease: "power2.inOut" }, 8.65);
      tl.fromTo("#s2dot", { opacity: 0 }, { opacity: 1, duration: 0.15, ease: "none" }, 8.82);
      tl.to("#s2disc", { opacity: 0, duration: 0.12, ease: "none" }, 8.9);

      // ================= S3 · the dot becomes a teacher's head; educator / cikgu / lecturer =================
      $("v3").innerHTML = `
        <rect width="1080" height="1920" fill="${CR}"/>
        <g id="s3rays">${rays(540, 700, 12, 1700, BLK)}</g>
        <polygon id="s3floor" points="0,1040 1080,1000 1080,1920 0,1920" fill="${BLK}"/>
        <polygon id="s3floor2" points="0,1040 1080,1000 1080,1022 0,1062" fill="${RED}"/>
        <polygon id="s3aisle" points="505,1030 575,1028 860,1920 220,1920" fill="${CR}"/>
        <g id="s3Lw">${fig("s3L", 230, 1050, 1.0, RED, "hold")}<g id="s3Lc"><rect x="168" y="862" width="124" height="88" fill="${CR}" stroke="${BLK}" stroke-width="8"/><rect id="s3Lf" x="182" y="876" width="96" height="60" fill="${RED}" opacity="0"/></g></g>
        <g id="s3Rw">${fig("s3R", 850, 1030, 1.0, RED, "hold")}<g id="s3Rc"><rect x="788" y="842" width="124" height="88" fill="${CR}" stroke="${BLK}" stroke-width="8"/><rect id="s3Rf" x="802" y="856" width="96" height="60" fill="${RED}" opacity="0"/></g></g>
        <g id="s3tb">
          <polygon points="465,756 615,756 596,881 484,881" fill="${RED}"/>
          <rect x="487" y="879" width="46" height="138" fill="${RED}"/><rect x="547" y="879" width="46" height="138" fill="${RED}"/>
        </g>
        <circle id="s3head" cx="540" cy="700" r="46" fill="${RED}"/>
        <g id="s3card">
          <rect x="440" y="760" width="200" height="140" fill="${CR}" stroke="${BLK}" stroke-width="10"/>
          <polygon id="s3tri" points="518,800 518,860 570,830" fill="${RED}"/>
        </g>
        <g id="s3arms"><polygon points="465,760 446,775 500,840 516,826" fill="${RED}"/><polygon points="615,760 634,775 580,840 564,826" fill="${RED}"/></g>`;
      tl.set("#s3", { opacity: 1 }, 9.15).set("#s3", { opacity: 0 }, 14.28);
      tl.fromTo("#s3tb", { scaleY: 0, svgOrigin: "540 746" }, { scaleY: 1, duration: 0.45, ease: "back.out(1.6)" }, 9.2);
      tl.fromTo("#s3arms", { scale: 0, svgOrigin: "540 760" }, { scale: 1, duration: 0.35, ease: "back.out(1.6)" }, 9.4);
      tl.fromTo("#s3floor, #s3floor2, #s3aisle", { y: 900 }, { y: 0, duration: 0.6, ease: "power3.out" }, 9.2);
      tl.fromTo("#s3rays", { scale: 0, rotation: -20, svgOrigin: "540 700" }, { scale: 1, rotation: 0, duration: 0.8, ease: "power3.out" }, 9.5);
      tl.to("#s3rays", { rotation: 24, svgOrigin: "540 700", duration: 4.0, ease: "none" }, 10.3);
      tl.fromTo("#s3card", { y: -1000, rotation: 25, svgOrigin: "540 830" }, { y: 0, rotation: 0, duration: 0.55, ease: "back.out(1.3)" }, 10.62);
      tl.fromTo("#s3Lw", { scale: 0, svgOrigin: "230 1050" }, { scale: 1, duration: 0.45, ease: "back.out(1.8)" }, 11.27);
      tl.fromTo("#s3Rw", { scale: 0, svgOrigin: "850 1030" }, { scale: 1, duration: 0.45, ease: "back.out(1.8)" }, 12.5);
      tl.fromTo("#c3", { scale: 1.08, rotation: 0 }, { scale: 1.0, rotation: -1.5, duration: 1.8, ease: "sine.inOut" }, 9.15);
      tl.to("#c3", { scale: 0.92, rotation: 1, duration: 2.2, ease: "sine.inOut" }, 11.0);
      tl.to("#s3Lf, #s3Rf", { opacity: 1, duration: 0.2, ease: "none" }, 13.46);
      tl.to("#s3tri", { scale: 0, svgOrigin: "540 830", duration: 0.22, ease: "back.in(2)" }, 13.4);
      tl.to("#z3", { scale: 26, duration: 0.6, ease: "power3.in" }, 13.6);

      // ================= S4 · the endless lecture hall (canvas 3D) =================
      {
        const cv = $("hall"), g = cv.getContext("2d");
        const CX = 810, CY = 1440, F = 1050, NEAR = 0.04;
        const clamp = (x) => Math.max(0, Math.min(1, x));
        const E = (a, b, t) => 0.5 - 0.5 * Math.cos(Math.PI * clamp((t - a) / (b - a)));
        const Ein = (a, b, t) => Math.pow(clamp((t - a) / (b - a)), 2.2);
        const hash = (i, j) => { const s = Math.sin(i * 127.1 + j * 311.7) * 43758.5453; return s - Math.floor(s); };
        let C = { h: 0, s: 1, c: 0, z: 0 };
        const cam = (X, Y, Z) => { const ry = Y - C.h, rz = Z - C.z; return [X, -ry * C.s + rz * C.c, ry * C.c + rz * C.s]; };
        const prj = (p) => [CX + (F * p[0]) / p[1], CY - (F * p[2]) / p[1]];
        function poly(pts, fill, stroke, lw) {
          let P = pts.map((p) => cam(p[0], p[1], p[2])), out = [];
          for (let i = 0; i < P.length; i++) {
            const a = P[i], b = P[(i + 1) % P.length], ia = a[1] >= NEAR, ib = b[1] >= NEAR;
            if (ia) out.push(a);
            if (ia !== ib) { const k = (NEAR - a[1]) / (b[1] - a[1]); out.push([a[0] + (b[0] - a[0]) * k, NEAR, a[2] + (b[2] - a[2]) * k]); }
          }
          if (out.length < 3) return;
          g.beginPath();
          out.forEach((p, i) => { const s = prj(p); i ? g.lineTo(s[0], s[1]) : g.moveTo(s[0], s[1]); });
          g.closePath(); g.fillStyle = fill; g.fill();
          if (stroke) { g.strokeStyle = stroke; g.lineWidth = lw; g.stroke(); }
        }
        const ROWS = 18, COLS = 7;
        function draw(t) {
          const h = 0.22 + 2.78 * E(14.27, 15.6, t) - 0.9 * E(16.8, 18.3, t);
          const a = ((90 - 78 * E(14.35, 15.9, t) - 10 * E(16.4, 18.2, t)) * Math.PI) / 180;
          C = { h, s: Math.sin(a), c: Math.cos(a), z: -0.5 + 3.5 * E(14.3, 15.9, t) + 25.6 * Ein(15.9, 18.35, t) };
          const wave = 28 * E(14.4, 17.4, t);
          g.fillStyle = RED; g.fillRect(0, 0, 1620, 2880);
          if (a < (80 * Math.PI) / 180) {
            const vx = CX, vy = CY - (F * C.s) / C.c;
            for (let k = 0; k < 16; k++) {
              if (k % 2) continue;
              const a0 = Math.PI + (k / 16) * Math.PI, a1 = Math.PI + ((k + 1) / 16) * Math.PI;
              g.beginPath(); g.moveTo(vx, vy); g.lineTo(vx + 5000 * Math.cos(a0), vy + 5000 * Math.sin(a0)); g.lineTo(vx + 5000 * Math.cos(a1), vy + 5000 * Math.sin(a1)); g.closePath();
              g.fillStyle = k % 4 ? CR : BLK; g.fill();
            }
          }
          poly([[-16, 0, 31], [16, 0, 31], [16, 14, 31], [-16, 14, 31]], CR);
          poly([[-1.55, 0, 30.98], [1.55, 0, 30.98], [1.55, 4.8, 30.98], [-1.55, 4.8, 30.98]], RED);
          poly([[-1.25, 0, 30.96], [1.25, 0, 30.96], [1.25, 4.4, 30.96], [-1.25, 4.4, 30.96]], BLK);
          poly([[-40, 0, -3], [40, 0, -3], [40, 0, 30.9], [-40, 0, 30.9]], BLK);
          poly([[-0.6, 0.001, -3], [0.6, 0.001, -3], [0.6, 0.001, 30.9], [-0.6, 0.001, 30.9]], CR);
          for (let i = ROWS - 1; i >= 0; i--) {
            const zr = 2 + i * 1.35, zs = zr + 0.75;
            const tc = 14.4 + (3.0 * Math.acos(1 - 2 * clamp(zs / 28))) / Math.PI;
            for (let side = -1; side <= 1; side += 2)
              for (let j = COLS - 1; j >= 0; j--) {
                const X = side * (1.15 + j * 1.15);
                const red = hash(i, j * side) < 0.16 || zs < wave;
                const pop = t > tc && zs < 28 ? 1 + 0.4 * Math.exp(-(t - tc) / 0.12) : 1;
                const col = red ? RED : BLK;
                poly([[X - 0.3, 0.7, zs], [X + 0.3, 0.7, zs], [X + 0.22, 1.28, zs], [X - 0.22, 1.28, zs]], col);
                const hp = cam(X, 1.5, zs);
                if (hp[1] > NEAR) { const s = prj(hp); g.beginPath(); g.arc(s[0], s[1], (F * 0.19 * pop) / hp[1], 0, Math.PI * 2); g.fillStyle = col; g.fill(); }
                const d0 = cam(X, 0.78, zr)[1], lw = d0 > NEAR ? Math.max(1, (F * 0.025) / d0) : 1;
                poly([[X - 0.46, 0, zr], [X + 0.46, 0, zr], [X + 0.46, 0.78, zr], [X - 0.46, 0.78, zr]], CR2, BLK, lw);
                poly([[X - 0.46, 0.78, zr], [X + 0.46, 0.78, zr], [X + 0.46, 0.78, zr + 0.6], [X - 0.46, 0.78, zr + 0.6]], CR, BLK, lw);
                if (red) poly([[X - 0.16, 0.781, zr + 0.14], [X + 0.12, 0.781, zr + 0.12], [X + 0.14, 0.781, zr + 0.42], [X - 0.14, 0.781, zr + 0.44]], BLK);
              }
          }
        }
        const clk = { t: 14.2 };
        tl.fromTo(clk, { t: 14.2 }, { t: 18.45, duration: 4.25, ease: "none", onUpdate: () => draw(clk.t) }, 14.2);
        draw(14.21);
      }
      tl.set("#s4", { opacity: 1 }, 14.21).set("#s4", { opacity: 0 }, 18.4);
      tl.fromTo("#c4", { rotation: -32 }, { rotation: 0, duration: 1.5, ease: "sine.inOut" }, 14.27);
