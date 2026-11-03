      // ================= S5 · through the door: the guide book; prompt / coding struck out =================
      {
        let lines = "";
        for (let k = 0; k < 8; k++) lines += `<rect x="370" y="${560 + k * 60}" width="340" height="14" fill="${BLK}"/>`;
        $("v5").innerHTML = `
          <rect width="1080" height="1920" fill="${CR}"/>
          <g id="s5rays">${rays(540, 760, 18, 1800, RED)}</g>
          <polygon points="0,1500 1080,1380 1080,1920 0,1920" fill="${BLK}"/>
          <rect x="470" y="1060" width="140" height="900" fill="${BLK}"/>
          <rect x="390" y="1050" width="300" height="28" fill="${BLK}"/>
          <g id="s5book">
            <rect x="314" y="454" width="452" height="612" rx="8" fill="${BLK}"/>
            <rect x="330" y="470" width="420" height="580" fill="${CR}"/>
            <g id="s5lines">${lines}</g>
            <g id="s5left"><rect x="-100" y="470" width="420" height="580" fill="${CR2}"/><rect x="-60" y="560" width="300" height="14" fill="${BLK}" opacity="0.5"/><rect x="-60" y="620" width="300" height="14" fill="${BLK}" opacity="0.5"/><rect x="-60" y="680" width="220" height="14" fill="${BLK}" opacity="0.5"/></g>
            <g id="s5cover">
              <rect x="320" y="460" width="440" height="600" fill="${BLK}"/>
              <rect x="345" y="485" width="390" height="550" fill="none" stroke="${CR}" stroke-width="4"/>
              <circle cx="540" cy="590" r="46" fill="${RED}"/><polygon points="526,568 526,612 564,590" fill="${CR}"/>
              <text x="540" y="728" text-anchor="middle" font-family="Montserrat" font-weight="900" font-size="70" fill="${CR}">PANDUAN</text>
              <rect x="320" y="770" width="440" height="64" fill="${RED}"/>
              <text x="540" y="815" text-anchor="middle" font-family="Montserrat" font-weight="900" font-size="34" letter-spacing="3" fill="${CR}">NAMA</text>
              <text x="540" y="900" text-anchor="middle" font-family="Montserrat" font-weight="900" font-size="34" letter-spacing="3" fill="${CR}">BRAND</text>
            </g>
          </g>
          <g id="s5p">
            <rect x="110" y="1290" width="380" height="120" rx="18" fill="${BLK}"/>
            <text x="300" y="1370" text-anchor="middle" font-family="Montserrat" font-weight="900" font-size="50" fill="${CR}">&gt;_ PROMPT</text>
            <rect id="s5ps" x="90" y="1338" width="420" height="26" fill="${RED}" transform="rotate(-10 300 1350)"/>
          </g>
          <g id="s5c">
            <rect x="590" y="1290" width="380" height="120" rx="18" fill="${BLK}"/>
            <text x="780" y="1370" text-anchor="middle" font-family="Montserrat" font-weight="900" font-size="48" fill="${CR}">&lt;/&gt; CODING</text>
            <rect id="s5cs" x="570" y="1338" width="420" height="26" fill="${RED}" transform="rotate(-10 780 1350)"/>
          </g>
          <rect id="s5dl" x="0" y="0" width="541" height="1920" fill="${BLK}"/>
          <rect id="s5dr" x="539" y="0" width="541" height="1920" fill="${BLK}"/>`;
      }
      tl.set("#s5", { opacity: 1 }, 18.33).set("#s5", { opacity: 0 }, 23.08);
      tl.to("#s5dl", { x: -600, duration: 0.7, ease: "power2.inOut" }, 18.4);
      tl.to("#s5dr", { x: 600, duration: 0.7, ease: "power2.inOut" }, 18.4);
      tl.fromTo("#s5book", { y: 160, scale: 0.86, svgOrigin: "540 760" }, { y: 0, scale: 1, duration: 0.9, ease: "power3.out" }, 18.45);
      tl.fromTo("#s5rays", { rotation: -10, svgOrigin: "540 760" }, { rotation: 20, duration: 4.6, ease: "none" }, 18.4);
      tl.fromTo("#c5", { scale: 1.0 }, { scale: 1.08, duration: 3.9, ease: "sine.inOut" }, 18.6);
      tl.fromTo("#s5left", { scaleX: 0, svgOrigin: "320 760" }, { scaleX: 1, duration: 0.22, ease: "power2.out" }, 22.5);
      tl.fromTo("#s5p", { scale: 0, svgOrigin: "300 1350" }, { scale: 1, duration: 0.35, ease: "back.out(2)" }, 20.43);
      tl.fromTo("#s5ps", { scaleX: 0, svgOrigin: "90 1350" }, { scaleX: 1, duration: 0.2, ease: "power2.out" }, 21.36);
      tl.to("#s5p", { y: 760, rotation: -35, svgOrigin: "300 1350", duration: 0.55, ease: "power2.in" }, 21.62);
      tl.fromTo("#s5c", { scale: 0, svgOrigin: "780 1350" }, { scale: 1, duration: 0.35, ease: "back.out(2)" }, 21.68);
      tl.fromTo("#s5cs", { scaleX: 0, svgOrigin: "570 1350" }, { scaleX: 1, duration: 0.2, ease: "power2.out" }, 22.24);
      tl.to("#s5c", { y: 760, rotation: 35, svgOrigin: "780 1350", duration: 0.5, ease: "power2.in" }, 22.46);
      tl.to("#s5cover", { scaleX: 0, svgOrigin: "320 760", duration: 0.22, ease: "power2.in" }, 22.28);
      tl.to("#c5", { scale: 6, duration: 0.55, ease: "power2.in" }, 22.52);

      // ================= S6 + S7 · page lines become stairs; two platforms at the top =================
      {
        const ST = [0, 1, 2, 3, 4].map((i) => ({ x: 60 + i * 190, y: 1560 - i * 210 }));
        let bars = "", pil = "";
        for (let k = 1; k <= 6; k++) bars += `<rect id="s6b${k}" x="-480" y="${-440 + 360 * k}" width="2040" height="84" fill="${BLK}"/>`;
        ST.forEach((p, i) => (pil += `<rect class="s6pil" x="${p.x}" y="${p.y + 56}" width="250" height="1500" fill="${BLK}"/>`));
        const ic = [
          `<polygon points="-26,-50 26,-50 26,0 56,0 0,56 -56,0 -26,0" fill="${CR}"/>`,
          `<text x="0" y="22" text-anchor="middle" font-family="JetBrains Mono" font-weight="700" font-size="66" fill="${CR}">&gt;_</text>`,
          `<circle cx="0" cy="0" r="40" fill="none" stroke="${CR}" stroke-width="20" stroke-dasharray="16 10"/><circle cx="0" cy="0" r="14" fill="${CR}"/>`,
          `<text x="0" y="22" text-anchor="middle" font-family="JetBrains Mono" font-weight="700" font-size="66" fill="${CR}">{ }</text>`,
          `<polygon points="-34,-46 -34,46 48,0" fill="${RED}"/>`,
        ];
        let icons = "";
        ST.forEach((p, i) => (icons += `<g class="s6ic" id="s6ic${i}" transform="translate(${p.x + 125} ${p.y + 170})">${ic[i]}</g>`));
        $("v6").innerHTML = `
          <rect x="-2000" y="-2000" width="6000" height="6000" fill="${CR}"/>
          <g id="s6w">
            <g id="s7raysL">${rays(1000, 330, 10, 1500, BLK, Math.PI / 10 / 2.6)}</g>
            <g id="s7raysR">${rays(1440, 330, 10, 1500, RED, Math.PI / 10 / 2.6)}</g>
            <rect id="s6plat" x="820" y="720" width="1700" height="60" fill="${BLK}"/>
            <rect id="s6platp" x="820" y="776" width="1700" height="1500" fill="${BLK}"/>
            ${pil}${bars}${icons}
            <g id="s7L"><rect x="870" y="80" width="260" height="642" fill="${BLK}"/><rect x="870" y="80" width="260" height="30" fill="${RED}"/>
              <text x="1000" y="300" text-anchor="middle" font-family="Montserrat" font-weight="900" font-size="48" fill="${CR}">CHATGPT</text>
              <rect x="940" y="160" width="120" height="76" rx="22" fill="none" stroke="${CR}" stroke-width="10"/><polygon points="960,232 990,232 966,262" fill="${CR}"/></g>
            <g id="s7R"><rect x="1310" y="80" width="260" height="642" fill="${RED}"/><rect x="1310" y="80" width="260" height="30" fill="${BLK}"/>
              <text x="1440" y="300" text-anchor="middle" font-family="Montserrat" font-weight="900" font-size="48" fill="${CR}">CLAUDE</text>
              <rect x="1380" y="160" width="120" height="76" rx="22" fill="none" stroke="${CR}" stroke-width="10"/><polygon points="1480,232 1450,232 1474,262" fill="${CR}"/></g>
            <g id="s7chkL"><circle cx="1000" cy="40" r="58" fill="${CR}" stroke="${BLK}" stroke-width="8"/><polyline points="972,40 994,64 1032,18" fill="none" stroke="${BLK}" stroke-width="14"/></g>
            <g id="s7chkR"><circle cx="1440" cy="40" r="58" fill="${CR}" stroke="${BLK}" stroke-width="8"/><polyline points="1412,40 1434,64 1472,18" fill="none" stroke="${BLK}" stroke-width="14"/></g>
            <g id="s7ring"><circle cx="1000" cy="230" r="190" fill="none" stroke="${BLK}" stroke-width="26"/><circle cx="1000" cy="230" r="190" fill="none" stroke="${CR}" stroke-width="12"/></g>
            <g id="s6fx"><g id="s6fy">${fig("s6fig", 0, 0, 0.55, RED)}</g></g>
          </g>`;
        tl.set("#s6", { opacity: 1 }, 23.04).set("#s6", { opacity: 0 }, 31.6);
        // bars → step slabs
        const map = { 6: 0, 5: 1, 4: 2, 3: 3, 2: 4 };
        Object.entries(map).forEach(([k, i], n) =>
          tl.to(`#s6b${k}`, { attr: { x: ST[i].x, y: ST[i].y, width: 250, height: 60 }, duration: 0.55, ease: "power3.inOut" }, 23.08 + n * 0.05));
        tl.to("#s6b1", { attr: { y: -900 }, duration: 0.5, ease: "power2.in" }, 23.08);
        tl.fromTo(".s6pil", { scaleY: 0, transformOrigin: "50% 0%" }, { scaleY: 1, duration: 0.45, ease: "power2.out", stagger: 0.05 }, 23.45);
        tl.fromTo(".s6ic", { scale: 0, transformOrigin: "50% 50%" }, { scale: 1, duration: 0.3, ease: "back.out(2)", stagger: 0.06 }, 23.7);
        tl.fromTo("#s6plat, #s6platp", { scaleX: 0, transformOrigin: "0% 50%" }, { scaleX: 1, duration: 0.6, ease: "power2.out" }, 25.9);
        // figure hops step by step
        const hops = [23.36, 23.73, 24.61, 25.33, 26.19];
        tl.fromTo("#s6fx", { x: -120 }, { x: -120, duration: 0.01 }, 23.0);
        tl.fromTo("#s6fy", { y: 1760 }, { y: 1760, duration: 0.01 }, 23.0);
        hops.forEach((t, i) => {
          const P = { x: ST[i].x + 125, y: ST[i].y };
          const y0 = i ? ST[i - 1].y : 1760;
          tl.to("#s6fx", { x: P.x, duration: 0.34, ease: "power1.inOut" }, t);
          tl.to("#s6fy", { y: Math.min(y0, P.y) - 120, duration: 0.17, ease: "power2.out" }, t);
          tl.to("#s6fy", { y: P.y, duration: 0.17, ease: "power2.in" }, t + 0.17);
          tl.fromTo(`#s6ic${i}`, { scale: 1 }, { scale: 1.35, duration: 0.14, yoyo: true, repeat: 1, ease: "sine.out", immediateRender: false }, t + 0.32);
        });
        // world camera follows the climb
        hops.forEach((t, i) => {
          const P = { x: ST[i].x + 125, y: ST[i].y };
          tl.to("#s6w", { x: -(P.x - 420) * 0.7, y: (1500 - P.y) * 0.7, duration: 0.7, ease: "sine.inOut" }, t + 0.05);
        });
        // top: walk between the monoliths, pan up
        tl.to("#s6fx", { x: 1220, duration: 0.8, ease: "sine.inOut" }, 26.75);
        tl.to("#s6w", { x: -680, y: 760, duration: 1.0, ease: "sine.inOut" }, 26.6);
        tl.fromTo("#s7L", { scaleY: 0, svgOrigin: "1000 722" }, { scaleY: 1, duration: 0.5, ease: "back.out(1.4)" }, 26.86);
        tl.fromTo("#s7R", { scaleY: 0, svgOrigin: "1440 722" }, { scaleY: 1, duration: 0.5, ease: "back.out(1.4)" }, 27.27);
        tl.fromTo("#s7raysL", { scale: 0, svgOrigin: "1000 330" }, { scale: 1, duration: 0.6, ease: "power3.out" }, 27.73);
        tl.fromTo("#s7raysR", { scale: 0, svgOrigin: "1440 330" }, { scale: 1, duration: 0.6, ease: "power3.out" }, 28.72);
        tl.to("#s7raysL", { rotation: 30, svgOrigin: "1000 330", duration: 3.4, ease: "none" }, 28.33);
        tl.to("#s7raysR", { rotation: -30, svgOrigin: "1440 330", duration: 2.4, ease: "none" }, 29.32);
        tl.fromTo("#s7ring", { scale: 0, opacity: 1, svgOrigin: "1000 230" }, { scale: 1, duration: 0.3, ease: "back.out(2)" }, 29.3);
        tl.to("#s7ring", { x: 440, duration: 0.45, ease: "power2.inOut" }, 29.94);
        tl.to("#s7ring", { x: 0, duration: 0.45, ease: "power2.inOut" }, 30.42);
        tl.to("#s7ring", { opacity: 0, duration: 0.2, ease: "none" }, 30.9);
        tl.fromTo("#s7chkL", { scale: 0, svgOrigin: "1000 40" }, { scale: 1, duration: 0.35, ease: "back.out(2.4)" }, 30.71);
        tl.fromTo("#s7chkR", { scale: 0, svgOrigin: "1440 40" }, { scale: 1, duration: 0.35, ease: "back.out(2.4)" }, 30.96);
        // whip out
        tl.to("#c6", { rotation: 24, scale: 1.5, filter: "blur(16px)", transformOrigin: "540px 960px", duration: 0.35, ease: "power2.in" }, 31.22);
        tl.to("#s6", { opacity: 0, duration: 0.16, ease: "none" }, 31.42);
      }

      // ================= S8 · a slide goes into the machine, edutainment comes out =================
      {
        let ticks = "";
        for (let i = 0; i < 24; i++) ticks += `<rect x="536" y="1262" width="8" height="30" fill="${CR}" transform="rotate(${i * 15} 540 1480)"/>`;
        let holes = "";
        for (let i = 0; i < 11; i++) holes += `<rect x="${232 + i * 58}" y="440" width="30" height="20" rx="4" fill="${CR}"/><rect x="${232 + i * 58}" y="840" width="30" height="20" rx="4" fill="${CR}"/>`;
        $("v8").innerHTML = `
          <rect width="1080" height="1920" fill="${CR}"/>
          <polygon points="0,260 1080,0 1080,250 0,520" fill="${BLK}"/>
          <polygon id="s8redb" points="1080,1000 1080,1920 600,1920" fill="${RED}"/>
          <polygon points="0,1300 0,1920 380,1920" fill="${BLK}"/>
          <clipPath id="s8clip"><rect x="-200" y="-400" width="1480" height="1582"/></clipPath>
          <g clip-path="url(#s8clip)">
            <g id="s8card">
              <rect x="330" y="470" width="420" height="290" rx="6" fill="${CR}" stroke="${BLK}" stroke-width="8"/>
              <rect x="330" y="470" width="420" height="56" fill="${BLK}"/>
              <text x="356" y="509" font-family="Montserrat" font-weight="900" font-size="28" letter-spacing="3" fill="${CR}">SLIDE</text>
              <rect x="368" y="562" width="190" height="14" fill="${BLK}"/><rect x="368" y="604" width="160" height="14" fill="${BLK}"/><rect x="368" y="646" width="180" height="14" fill="${BLK}"/>
              <circle cx="660" cy="606" r="46" fill="${RED}"/>
              <rect x="600" y="690" width="26" height="40" fill="${BLK}"/><rect x="640" y="666" width="26" height="64" fill="${RED}"/><rect x="680" y="646" width="26" height="84" fill="${BLK}"/>
            </g>
            <g id="s8hand"><polygon points="590,-460 730,-460 690,420 570,420" fill="${BLK}"/><rect x="520" y="400" width="200" height="110" rx="40" fill="${BLK}"/></g>
          </g>
          <rect x="230" y="1180" width="620" height="620" rx="12" fill="${BLK}"/>
          <rect x="320" y="1166" width="440" height="26" fill="#0b0908" stroke="${CR}" stroke-width="5"/>
          <circle id="s8l1" cx="290" cy="1232" r="12" fill="${CR}"/><circle id="s8l2" cx="330" cy="1232" r="12" fill="${RED}"/><circle id="s8l3" cx="370" cy="1232" r="12" fill="${CR}"/>
          <g id="s8disc">
            <circle cx="540" cy="1480" r="232" fill="${RED}"/>${ticks}
            <circle cx="540" cy="1480" r="190" fill="none" stroke="${CR}" stroke-width="12"/>
            <circle cx="540" cy="1480" r="150" fill="none" stroke="${BLK}" stroke-width="18" stroke-dasharray="40 20"/>
            <circle cx="540" cy="1480" r="104" fill="none" stroke="${CR}" stroke-width="10"/>
            <circle cx="540" cy="1480" r="70" fill="${RED2}"/><circle cx="540" cy="1480" r="28" fill="${BLK}"/><rect x="532" y="1410" width="16" height="70" fill="${CR}"/>
          </g>
          <g id="s8frame">
            <rect x="210" y="426" width="660" height="448" rx="14" fill="${BLK}"/>${holes}
            <clipPath id="s8scr"><rect x="240" y="470" width="600" height="360"/></clipPath>
            <g clip-path="url(#s8scr)">
              <rect x="240" y="470" width="600" height="360" fill="${CR}"/>
              <polygon points="240,830 840,640 840,830" fill="${CR2}"/>
              <circle id="s8sun" cx="420" cy="720" r="58" fill="${RED}"/>
              <rect id="s8b1" x="640" y="700" width="34" height="100" fill="${BLK}"/><rect id="s8b2" x="690" y="660" width="34" height="140" fill="${RED}"/><rect id="s8b3" x="740" y="610" width="34" height="190" fill="${BLK}"/>
              <g id="s8walk">${fig("s8w", 0, 800, 0.36, BLK)}</g>
              <rect x="262" y="808" width="556" height="10" fill="${CR2}"/><rect id="s8prog" x="262" y="808" width="556" height="10" fill="${RED}"/>
            </g>
          </g>`;
      }
      tl.set("#s8", { opacity: 1 }, 31.3).set("#s8", { opacity: 0 }, 36.2);
      tl.fromTo("#c8", { rotation: -24, scale: 0.7, filter: "blur(16px)" }, { rotation: 0, scale: 1, filter: "blur(0px)", duration: 0.55, ease: "power2.out" }, 31.3);
      tl.to("#c8", { scale: 1.05, duration: 4, ease: "sine.inOut" }, 31.86);
      tl.fromTo("#s8hand, #s8card", { y: -500 }, { y: 0, duration: 0.6, ease: "power3.out" }, 31.48);
      tl.to("#s8card", { y: 760, duration: 0.7, ease: "power2.inOut" }, 32.43);
      tl.to("#s8hand", { y: 280, duration: 0.45, ease: "power2.inOut" }, 32.43);
      tl.to("#s8hand", { y: -900, duration: 0.6, ease: "power2.in" }, 32.95);
      tl.to("#s8disc", { rotation: 540, svgOrigin: "540 1480", duration: 3.0, ease: "sine.inOut" }, 32.9);
      tl.fromTo("#s8l1, #s8l2, #s8l3", { opacity: 1 }, { opacity: 0.2, duration: 0.14, yoyo: true, repeat: 9, stagger: 0.07, ease: "none" }, 33.0);
      tl.fromTo("#s8frame", { x: 0, y: 830, scale: 0.12, svgOrigin: "540 650" }, { y: 0, scale: 1, duration: 0.7, ease: "back.out(1.2)" }, 34.05);
      tl.fromTo("#s8sun", { y: 140 }, { y: 0, duration: 1.0, ease: "power2.out" }, 34.5);
      tl.fromTo("#s8b1, #s8b2, #s8b3", { scaleY: 0, transformOrigin: "50% 100%" }, { scaleY: 1, duration: 0.5, ease: "back.out(1.6)", stagger: 0.12 }, 34.7);
      tl.fromTo("#s8walk", { x: 230 }, { x: 560, duration: 1.4, ease: "none" }, 34.5);
      tl.fromTo("#s8prog", { scaleX: 0, svgOrigin: "262 813" }, { scaleX: 1, duration: 1.5, ease: "none" }, 34.5);
      tl.to("#z8", { scale: 6.2, duration: 0.6, ease: "power2.in" }, 35.5);
