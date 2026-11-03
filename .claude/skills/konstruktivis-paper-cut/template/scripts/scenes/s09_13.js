      // ================= S9 · phone in hand: awareness, promotion, at your fingertip =================
      {
        const feed = `
          <g id="s9feed">
            <g><rect x="-214" y="-440" width="428" height="600" fill="${CR2}"/><rect x="-200" y="-420" width="400" height="300" fill="${BLK}"/>
              <rect x="-188" y="-406" width="376" height="272" fill="${CR}"/><circle cx="-90" cy="-260" r="44" fill="${RED}"/>
              <rect x="40" y="-250" width="28" height="90" fill="${BLK}"/><rect x="80" y="-280" width="28" height="120" fill="${RED}"/><rect x="120" y="-310" width="28" height="150" fill="${BLK}"/>
              <rect x="-188" y="-150" width="376" height="10" fill="${RED}"/>
              <rect x="-200" y="-90" width="300" height="22" fill="${BLK}"/><rect x="-200" y="-50" width="220" height="22" fill="${BLK}" opacity="0.5"/></g>
            <g transform="translate(0 640)"><rect x="-214" y="-440" width="428" height="600" fill="${CR}"/>
              <path d="M -170 -250 Q 0 -420 170 -250 Q 0 -80 -170 -250 Z" fill="${CR}" stroke="${BLK}" stroke-width="20"/>
              <circle cx="0" cy="-250" r="70" fill="${RED}"/><circle cx="0" cy="-250" r="30" fill="${BLK}"/>
              <text x="0" y="-20" text-anchor="middle" font-family="Montserrat" font-weight="900" font-size="50" fill="${BLK}">AWARENESS</text>
              <rect x="-150" y="20" width="300" height="18" fill="${BLK}" opacity="0.4"/><rect x="-110" y="56" width="220" height="18" fill="${BLK}" opacity="0.4"/></g>
            <g transform="translate(0 1280)"><rect x="-214" y="-440" width="428" height="600" fill="${CR}"/>
              <polygon points="-150,-360 80,-360 170,-250 80,-140 -150,-140" fill="${RED}"/><circle cx="-110" cy="-250" r="18" fill="${CR}"/>
              <text x="10" y="-212" text-anchor="middle" font-family="Montserrat" font-weight="900" font-size="110" fill="${CR}">%</text>
              <text x="0" y="-20" text-anchor="middle" font-family="Montserrat" font-weight="900" font-size="50" fill="${BLK}">PROMOTION</text>
              <rect x="-150" y="20" width="300" height="18" fill="${BLK}" opacity="0.4"/><rect x="-110" y="56" width="220" height="18" fill="${BLK}" opacity="0.4"/></g>
          </g>
          <g id="s9rip"><circle class="s9r" cx="40" cy="60" r="60" fill="none" stroke="${RED}" stroke-width="12"/><circle class="s9r" cx="40" cy="60" r="60" fill="none" stroke="${RED}" stroke-width="12"/><circle class="s9r" cx="40" cy="60" r="60" fill="none" stroke="${RED}" stroke-width="12"/></g>`;
        $("v9").innerHTML = `
          <rect width="1080" height="1920" fill="${RED}"/>
          <circle cx="90" cy="360" r="340" fill="${BLK}"/>
          <polygon points="0,1500 1080,1180 1080,1920 0,1920" fill="${RED2}"/>
          <g transform="translate(560 860) rotate(6)">${phone("s9ph", feed, "s9clip")}<g id="s9thw">${thumb("s9th")}</g></g>`;
      }
      tl.set("#s9", { opacity: 0 }, 40.5);
      tl.fromTo("#s9", { opacity: 0 }, { opacity: 1, duration: 0.22, ease: "none", immediateRender: false }, 35.95);
      tl.fromTo("#c9", { scale: 2.5, y: 340 }, { scale: 1, y: 0, duration: 0.9, ease: "power3.out" }, 35.95);
      tl.to("#c9", { scale: 1.08, duration: 2.6, ease: "sine.inOut" }, 36.9);
      tl.fromTo("#s9thw", { x: 260, y: 420 }, { x: 150, y: 280, duration: 0.35, ease: "power2.out" }, 36.1);
      [36.55, 37.83].forEach((t, i) => {
        tl.to("#s9thw", { y: 80, duration: 0.3, ease: "power2.in" }, t - 0.08);
        tl.to("#s9feed", { y: -640 * (i + 1), duration: 0.5, ease: "power3.inOut" }, t);
        tl.to("#s9thw", { y: 280, duration: 0.35, ease: "sine.out" }, t + 0.3);
      });
      tl.to("#s9thw", { x: 40, y: 60, duration: 0.4, ease: "power2.inOut" }, 38.6);
      tl.to("#s9th", { scale: 0.92, transformOrigin: "50% 0%", duration: 0.1, yoyo: true, repeat: 1, ease: "sine.inOut" }, 39.0);
      tl.fromTo(".s9r", { scale: 0.3, opacity: 1, svgOrigin: "40 60" }, { scale: 3.4, opacity: 0, duration: 0.8, ease: "sine.out", stagger: 0.16 }, 39.05);
      tl.to("#c9", { rotation: -22, scale: 1.7, filter: "blur(16px)", duration: 0.38, ease: "power2.in" }, 40.0);
      tl.to("#s9", { opacity: 0, duration: 0.15, ease: "none" }, 40.25);

      // ================= S10 · top-down table: group support, ask anything =================
      {
        const top = (id, x, y, r, col) => `<g id="${id}" transform="translate(${x} ${y}) rotate(${r})"><g class="s10f">
          <polyline points="-92,-10 -78,-150 -30,-232" fill="none" stroke="${col}" stroke-width="36" stroke-linejoin="round"/>
          <polyline points="92,-10 78,-150 30,-232" fill="none" stroke="${col}" stroke-width="36" stroke-linejoin="round"/>
          <circle cx="-78" cy="-150" r="15" fill="${CR}" stroke="${BLK}" stroke-width="6"/><circle cx="78" cy="-150" r="15" fill="${CR}" stroke="${BLK}" stroke-width="6"/>
          <circle cx="-92" cy="-10" r="15" fill="${CR}" stroke="${BLK}" stroke-width="6"/><circle cx="92" cy="-10" r="15" fill="${CR}" stroke="${BLK}" stroke-width="6"/>
          <rect x="-118" y="-46" width="236" height="92" rx="46" fill="${col}"/>
          <circle cx="0" cy="0" r="60" fill="${BLK}"/><rect x="-60" y="-14" width="120" height="16" fill="${col === RED ? CR : RED}"/></g></g>`;
        $("v10").innerHTML = `
          <rect x="-600" y="-600" width="2280" height="3120" fill="${BLK}"/>
          <polygon points="-600,-600 900,-600 -600,1300" fill="${RED}"/>
          <polygon points="1680,800 1680,2520 300,2520" fill="${RED2}"/>
          <g transform="rotate(12 540 900)">
            <rect x="220" y="410" width="640" height="980" fill="${CR}"/>
            <rect x="240" y="430" width="600" height="940" fill="none" stroke="${BLK}" stroke-width="6"/>
            <g id="s10net">
              <line class="s10l" x1="540" y1="900" x2="540" y2="320" stroke="${RED}" stroke-width="10" stroke-dasharray="26 16"/>
              <line class="s10l" x1="540" y1="900" x2="540" y2="1480" stroke="${RED}" stroke-width="10" stroke-dasharray="26 16"/>
              <line class="s10l" x1="540" y1="900" x2="160" y2="900" stroke="${RED}" stroke-width="10" stroke-dasharray="26 16"/>
              <line class="s10l" x1="540" y1="900" x2="920" y2="900" stroke="${RED}" stroke-width="10" stroke-dasharray="26 16"/>
            </g>
            <rect x="445" y="720" width="190" height="360" rx="28" fill="#0c0a09"/><circle cx="600" cy="760" r="14" fill="#2a2421"/>
            ${top("s10a", 540, 270, 180, RED)}${top("s10b", 540, 1530, 0, CR)}${top("s10c", 110, 900, 90, CR)}${top("s10d", 970, 900, -90, RED)}
          </g>
          <g id="s10q"><circle cx="300" cy="560" r="80" fill="${CR}" stroke="${BLK}" stroke-width="10"/>
            <text id="s10qm" x="300" y="598" text-anchor="middle" font-family="Montserrat" font-weight="900" font-size="104" fill="${BLK}">?</text>
            <polyline id="s10ok" points="262,560 292,592 342,532" fill="none" stroke="${RED}" stroke-width="18" stroke-linecap="round"/></g>
          <g id="s10a2"><circle cx="820" cy="1350" r="80" fill="${RED}" stroke="${BLK}" stroke-width="10"/>
            <text x="820" y="1386" text-anchor="middle" font-family="Montserrat" font-weight="900" font-size="104" fill="${CR}">!</text></g>`;
      }
      tl.set("#s10", { opacity: 1 }, 40.25).set("#s10", { opacity: 0 }, 45.3);
      tl.fromTo("#c10", { rotation: 22, scale: 1.5, filter: "blur(16px)" }, { rotation: 0, scale: 1, filter: "blur(0px)", duration: 0.55, ease: "power2.out" }, 40.25);
      tl.to("#c10", { rotation: -6, scale: 1.06, duration: 4.0, ease: "sine.inOut" }, 40.8);
      tl.fromTo("#s10a, #s10b, #s10c, #s10d", { scale: 0.4, opacity: 0, transformOrigin: "50% 50%" }, { scale: 1, opacity: 1, duration: 0.45, ease: "back.out(1.6)", stagger: 0.12 }, 40.4);
      tl.fromTo(".s10f", { rotation: -5, transformOrigin: "50% 50%" }, { rotation: 5, duration: 0.9, yoyo: true, repeat: 4, ease: "sine.inOut", stagger: 0.2 }, 40.9);
      tl.fromTo(".s10l", { attr: { x2: 540, y2: 900 } }, { attr: { x2: (i) => [540, 540, 160, 920][i], y2: (i) => [320, 1480, 900, 900][i] }, duration: 0.45, ease: "power2.out", stagger: 0.08 }, 41.94);
      tl.fromTo("#s10q", { scale: 0, svgOrigin: "300 560" }, { scale: 1, duration: 0.35, ease: "back.out(2.4)" }, 43.18);
      tl.fromTo("#s10ok", { opacity: 0 }, { opacity: 1, duration: 0.15, ease: "none" }, 44.62);
      tl.to("#s10qm", { opacity: 0, duration: 0.12, ease: "none" }, 44.55);
      tl.fromTo("#s10a2", { scale: 0, svgOrigin: "820 1350" }, { scale: 1, duration: 0.35, ease: "back.out(2.4)" }, 44.22);
      tl.to("#s10q, #s10a2", { opacity: 0, duration: 0.2, ease: "none" }, 44.85);
      tl.to("#z10", { scale: 15, duration: 0.45, ease: "power3.in" }, 44.76);

      // ================= S11 · the wall of books: Prompt Vault, pick a strategy =================
      {
        const hash = (i, j) => { const s = Math.sin(i * 91.7 + j * 17.3) * 43758.5453; return s - Math.floor(s); };
        let cells = "";
        for (let r = 0; r < 10; r++)
          for (let c = 0; c < 7; c++) {
            const x = 540 - 85 + (c - 3) * 184, y = -100 + r * 214, h = hash(r, c);
            if (r === 4 && c === 3) { cells += `<rect x="${x}" y="${y}" width="170" height="200" fill="#100e0c" stroke="#3a322c" stroke-width="4"/>`; continue; }
            cells += `<rect x="${x}" y="${y}" width="170" height="200" fill="${BLK}" stroke="#3a322c" stroke-width="4"/>`;
            if (h < 0.35) cells += `<circle cx="${x + 85}" cy="${y + 80}" r="34" fill="${CR}"/><rect x="${x + 51}" y="${y + 124}" width="68" height="44" fill="${CR}"/>`;
            else if (h < 0.55) cells += `<rect x="${x + 30}" y="${y + 50}" width="110" height="12" fill="${CR2}"/><rect x="${x + 30}" y="${y + 80}" width="80" height="12" fill="${CR2}"/><rect x="${x + 30}" y="${y + 110}" width="96" height="12" fill="${CR2}"/>`;
            else if (h < 0.65) cells += `<rect x="${x + 60}" y="${y + 40}" width="50" height="130" fill="${RED}"/>`;
          }
        const icons = [
          `<circle cx="0" cy="-20" r="46" fill="none" stroke="${RED}" stroke-width="14"/><circle cx="0" cy="-20" r="18" fill="${BLK}"/>`,
          `<polygon points="-46,-40 -10,-40 40,-70 40,30 -10,0 -46,0" fill="${BLK}"/><rect x="-36" y="0" width="22" height="40" fill="${BLK}"/>`,
          `<polygon points="0,-74 18,-34 62,-30 28,-2 38,42 0,20 -38,42 -28,-2 -62,-30 -18,-34" fill="${RED}"/>`,
          `<rect x="-50" y="-10" width="24" height="50" fill="${BLK}"/><rect x="-12" y="-40" width="24" height="80" fill="${RED}"/><rect x="26" y="-70" width="24" height="110" fill="${BLK}"/>`,
          `<rect x="-56" y="-66" width="112" height="76" rx="22" fill="${BLK}"/><polygon points="-30,8 0,8 -26,40" fill="${BLK}"/>`,
        ];
        let cards = "";
        icons.forEach((ic, i) => (cards += `<g class="s11card" id="s11k${i}"><g id="s11kz${i}"><rect x="-80" y="-112" width="160" height="224" rx="10" fill="${CR}" stroke="${BLK}" stroke-width="8"/><g class="s11ico">${ic}</g><rect x="-50" y="66" width="100" height="12" fill="${BLK}" opacity="0.4"/></g></g>`));
        $("v11").innerHTML = `
          <rect x="-1200" y="-1200" width="3480" height="4320" fill="${BLK}"/>
          <g id="s11wall">${cells}</g>
          <g id="s11cards">${cards}</g>
          <g id="s11book">
            <rect x="-62" y="-82" width="124" height="164" rx="6" fill="${RED2}"/>
            <g id="s11pages"><rect x="-58" y="-78" width="116" height="156" fill="${CR}"/><rect x="-44" y="-50" width="88" height="6" fill="${BLK}"/><rect x="-44" y="-34" width="70" height="6" fill="${BLK}"/></g>
            <g id="s11cov"><rect x="-62" y="-82" width="124" height="164" rx="6" fill="${RED}"/><rect x="-52" y="-72" width="104" height="144" fill="none" stroke="${CR}" stroke-width="2"/>
              <text x="0" y="-8" text-anchor="middle" font-family="Montserrat" font-weight="900" font-size="20" fill="${CR}">PROMPT</text>
              <text x="0" y="20" text-anchor="middle" font-family="Montserrat" font-weight="900" font-size="20" fill="${CR}">VAULT</text>
              <rect x="-34" y="40" width="68" height="6" fill="${BLK}"/></g>
          </g>
          <g id="s11ring"><circle cx="0" cy="0" r="140" fill="none" stroke="${RED}" stroke-width="14"/></g>`;
        // card fan positions above the open book
        const fan = [-2, -1, 0, 1, 2].map((k) => ({ x: 540 + k * 186, y: 330 + Math.abs(k) * 46, r: k * 9 }));
        tl.set("#s11", { opacity: 1 }, 45.22).set("#s11", { opacity: 0 }, 50.1);
        tl.fromTo("#s11book", { opacity: 0 }, { opacity: 1, duration: 0.2, ease: "none" }, 45.7);
        tl.fromTo("#c11", { scale: 7 }, { scale: 1, duration: 0.95, ease: "power3.out" }, 45.22);
        tl.to("#c11", { scale: 1.05, duration: 3.6, ease: "sine.inOut" }, 46.2);
        tl.fromTo("#s11book", { x: 540, y: 856, scale: 1 }, { x: 540, y: 836, scale: 1.12, duration: 0.4, ease: "back.out(2)" }, 46.06);
        tl.to("#s11book", { y: 760, scale: 3, duration: 0.6, ease: "power3.inOut" }, 47.0);
        tl.fromTo("#s11book", { rotation: 0 }, { rotation: -8, duration: 0.3, yoyo: true, repeat: 1, ease: "sine.inOut", immediateRender: false }, 47.0);
        tl.to("#s11wall", { opacity: 0.45, duration: 0.6, ease: "none" }, 47.0);
        tl.to("#s11cov", { scaleX: 0, svgOrigin: "-62 0", duration: 0.25, ease: "power2.in" }, 47.84);
        fan.forEach((p, i) => {
          tl.fromTo(`#s11k${i}`, { x: 540, y: 760, scale: 0.2, rotation: 0, opacity: 0 }, { x: p.x, y: p.y, scale: 1, rotation: p.r, opacity: 1, duration: 0.5, ease: "back.out(1.4)" }, 48.0 + i * 0.06);
        });
        tl.fromTo("#s11ring", { x: fan[0].x, y: fan[0].y, scale: 0, opacity: 1 }, { scale: 1, duration: 0.25, ease: "back.out(2)" }, 48.57);
        tl.to("#s11ring", { x: fan[2].x, y: fan[2].y, duration: 0.35, ease: "power2.inOut" }, 48.82);
        tl.to("#s11k0, #s11k1, #s11k3, #s11k4", { opacity: 0.3, duration: 0.3, ease: "none" }, 49.07);
        tl.to("#s11ring", { opacity: 0, duration: 0.2, ease: "none" }, 49.2);
        tl.to("#s11k2", { y: fan[2].y - 40, scale: 1.25, duration: 0.35, ease: "back.out(2)" }, 49.07);
        tl.to("#s11k2 .s11ico", { opacity: 0, duration: 0.15, ease: "none" }, 49.6);
        tl.to("#s11k2", { x: 540, y: 960, scale: 14, rotation: 0, duration: 0.5, ease: "power3.in" }, 49.6);
      }

      // ================= S12 · styling ready; follow, buat, dapat video =================
      $("v12").innerHTML = `
        <rect width="1080" height="1920" fill="${CR}"/>
        <polygon points="0,1240 1080,1180 1080,1920 0,1920" fill="${CR2}"/>
        <g id="s12t0"><rect x="260" y="390" width="260" height="260" fill="${RED}"/><text x="390" y="565" text-anchor="middle" font-family="Montserrat" font-weight="900" font-size="130" fill="${CR}">Aa</text></g>
        <g id="s12t1"><rect x="560" y="390" width="260" height="260" fill="${BLK}"/><circle cx="690" cy="520" r="80" fill="${RED}"/></g>
        <g id="s12t2"><rect x="260" y="690" width="260" height="260" fill="${CR}" stroke="${BLK}" stroke-width="12"/><polygon points="390,750 470,890 310,890" fill="${BLK}"/></g>
        <g id="s12t3"><rect x="560" y="690" width="260" height="260" fill="${BLK}"/><polygon points="560,950 820,690 820,950" fill="${RED}"/></g>
        <g id="s12s1"><circle cx="220" cy="1468" r="125" fill="${BLK}"/>
          <rect x="160" y="1418" width="120" height="16" fill="${CR}"/><rect x="160" y="1460" width="120" height="16" fill="${CR}"/><rect x="160" y="1502" width="80" height="16" fill="${CR}"/>
          <circle cx="148" cy="1426" r="9" fill="${RED}"/><circle cx="148" cy="1468" r="9" fill="${RED}"/><circle cx="148" cy="1510" r="9" fill="${RED}"/></g>
        <g id="s12s2"><circle cx="540" cy="1468" r="125" fill="${RED}"/><polygon points="500,1400 500,1530 534,1498 558,1550 582,1538 558,1488 602,1484" fill="${CR}"/></g>
        <g id="s12s3"><circle cx="860" cy="1468" r="125" fill="${BLK}"/><polygon points="836,1420 836,1516 918,1468" fill="${RED}"/></g>
        <circle id="s12flood" cx="863" cy="1468" r="2300" fill="${RED}"/>`;
      tl.set("#s12", { opacity: 1 }, 50.05).set("#s12", { opacity: 0 }, 53.1);
      tl.fromTo("#c12", { scale: 1.08 }, { scale: 1, duration: 2.6, ease: "sine.out" }, 50.05);
      ["#s12t0", "#s12t1", "#s12t2", "#s12t3"].forEach((id, i) =>
        tl.fromTo(id, { scale: 0, rotation: -30, transformOrigin: "50% 50%" }, { scale: 1, rotation: 0, duration: 0.45, ease: "back.out(1.8)" }, 50.08 + i * 0.1));
      tl.to("#s12t0, #s12t1, #s12t2, #s12t3", { rotation: 90, transformOrigin: "50% 50%", duration: 0.5, ease: "back.inOut(1.4)", stagger: 0.08 }, 50.77);
      [["#s12s1", 51.2, "220 1468"], ["#s12s2", 51.87, "540 1468"], ["#s12s3", 52.31, "860 1468"]].forEach(([id, t, o]) =>
        tl.fromTo(id, { scale: 2.3, opacity: 0, rotation: -14, svgOrigin: o }, { scale: 1, opacity: 1, rotation: 0, duration: 0.22, ease: "power3.in" }, t - 0.14));
      tl.fromTo("#s12flood", { scale: 0, svgOrigin: "863 1468" }, { scale: 1, duration: 0.5, ease: "power2.in" }, 52.58);
      tl.to("#z12", { scale: 2.2, duration: 0.5, ease: "power2.in" }, 52.58);

      // ================= S13 · press the link; laser; red flood; end card =================
      {
        const scr = `
          <circle cx="-180" cy="-404" r="26" fill="${RED}"/>
          <text x="-140" y="-392" font-family="Montserrat" font-weight="900" font-size="30" fill="${BLK}">NAMA BRAND</text>
          <rect x="-210" y="-350" width="420" height="400" fill="${BLK}"/><polygon points="-210,50 210,-350 210,50" fill="${CR2}"/>
          <circle cx="-60" cy="-180" r="90" fill="${RED}"/>
          <rect x="-210" y="72" width="300" height="20" fill="${BLK}"/><rect x="-210" y="106" width="220" height="20" fill="${BLK}" opacity="0.45"/>
          <g id="s13btn"><rect x="-190" y="160" width="380" height="120" rx="60" fill="${RED}"/>
            <text x="0" y="236" text-anchor="middle" font-family="Montserrat" font-weight="900" font-size="46" fill="${CR}">TEKAN LINK</text></g>
          <polygon points="-22,320 22,320 0,350" fill="${BLK}"/>`;
        $("v13").innerHTML = `
          <rect width="1080" height="1920" fill="${RED}"/>
          <circle cx="960" cy="300" r="320" fill="${BLK}"/>
          <polygon points="0,1560 1080,1300 1080,1920 0,1920" fill="${RED2}"/>
          <g transform="translate(540 740) rotate(-6) scale(0.95)">${phone("s13ph", scr, "s13clip")}<g id="s13thw">${thumb("s13th")}</g>
            <g id="s13rip"><circle class="s13r" cx="0" cy="220" r="70" fill="none" stroke="${BLK}" stroke-width="10"/><circle class="s13r" cx="0" cy="220" r="70" fill="none" stroke="${BLK}" stroke-width="10"/></g></g>
          <g id="s13las" transform="rotate(-32 540 960)">
            <rect x="-1400" y="930" width="2400" height="60" fill="#ff3b30" opacity="0.35"/>
            <rect x="-1400" y="952" width="2400" height="16" fill="#ff5a4f"/>
            <rect x="-1400" y="957" width="2400" height="6" fill="#ffe1dc"/>
          </g>
          <circle id="s13flood" cx="562" cy="948" r="2300" fill="${RED}"/>`;
      }
      tl.set("#s13", { opacity: 1 }, 53.04);
      tl.fromTo("#c13", { scale: 1.12, rotation: 3 }, { scale: 1.0, rotation: 0, duration: 1.4, ease: "sine.out" }, 53.04);
      tl.fromTo("#s13thw", { x: 300, y: 700 }, { x: 40, y: 230, duration: 0.42, ease: "power3.out" }, 53.3);
      tl.to("#s13btn", { scale: 0.92, svgOrigin: "0 220", duration: 0.1, yoyo: true, repeat: 1, ease: "sine.inOut" }, 53.74);
      tl.to("#s13th", { scale: 0.93, transformOrigin: "50% 0%", duration: 0.1, yoyo: true, repeat: 1, ease: "sine.inOut" }, 53.74);
      tl.fromTo(".s13r", { scale: 0.4, opacity: 1, svgOrigin: "0 220" }, { scale: 3, opacity: 0, duration: 0.7, ease: "sine.out", stagger: 0.18 }, 53.8);
      tl.fromTo("#s13las", { x: -1500, y: 0 }, { x: 1700, duration: 0.6, ease: "power1.inOut" }, 53.95);
      tl.fromTo("#s13flood", { scale: 0, svgOrigin: "562 948" }, { scale: 1, duration: 0.55, ease: "power2.in" }, 54.45);
      tl.fromTo("#endcard", { opacity: 0 }, { opacity: 1, duration: 0.3, ease: "none" }, 55.0);
      tl.fromTo("#end1, #end2", { y: 60 }, { y: 0, duration: 0.6, ease: "power3.out", stagger: 0.08 }, 55.0);
      tl.fromTo("#end3", { y: 30, opacity: 0 }, { y: 0, opacity: 1, duration: 0.5, ease: "power3.out" }, 55.25);
