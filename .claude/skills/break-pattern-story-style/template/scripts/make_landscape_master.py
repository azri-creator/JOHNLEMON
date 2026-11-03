"""Re-layout the portrait master (1080x1920) for 16:9 (1920x1080): same ids, same word-synced timeline and tweens,
new positions/sizes per scene (character at the side, content beside it) plus the few absolute numbers inside the JS.
Output: master/index.master16.html  (then: python3 scripts/retime_build.py master/index.master16.html hf16/index.html)"""
import re, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
s = open(os.path.join(ROOT, "master", "index.master.html")).read()


def setstyle(eid, **kw):
    global s
    m = re.search(r'<[a-zA-Z]+\b[^>]*\bid="%s"[^>]*>' % re.escape(eid), s)
    assert m, eid
    tag = m.group(0)
    sm = re.search(r'style="([^"]*)"', tag)
    assert sm, eid
    d = {}
    for part in [x for x in sm.group(1).split(";") if x.strip()]:
        k, v = part.split(":", 1)
        d[k.strip()] = v.strip()
    for k, v in kw.items():
        d[k.replace("_", "-")] = str(v)
    s = s.replace(tag, tag.replace(sm.group(0), 'style="%s"' % ";".join(f"{k}:{v}" for k, v in d.items())), 1)


def rep(a, b, count=1):
    global s
    assert a in s, a[:90]
    s = s.replace(a, b, count)


def px(v): return f"{v:g}px"


def zoomed(eid, z, x, y, **kw):
    """place a zoomed element so its VISUAL top-left is (x,y)"""
    setstyle(eid, zoom=z, left=px(x / z), top=px(y / z), **kw)


# ------------------------------------------------------------------ canvas
rep('content="width=1080, height=1920"', 'content="width=1920, height=1080"')
rep("html, body { width: 1080px; height: 1920px;", "html, body { width: 1920px; height: 1080px;")
rep('data-width="1080" data-height="1920"', 'data-width="1920" data-height="1080"')
setstyle("wipe", width="1920px", height="1080px"); setstyle("flash", width="1920px", height="1080px")
rep("{ x: 1300, opacity: 1, skewX: -12 }, { x: -260,", "{ x: 2100, opacity: 1, skewX: -12 }, { x: -300,")

# ------------------------------------------------------------------ S1  galeri -> footage -> NAK EDIT
setstyle("s1-ghost", left="60px", top="40px", font_size="280px")
setstyle("s1-blob", left="100px", top="330px", width="640px", height="640px")
setstyle("s1-char", left="130px", top="130px", width="580px")
setstyle("s1-gal", left="780px", top="120px", width="760px", height="580px")
setstyle("s1-folder", left="1250px", top="560px")
setstyle("s1-cal", left="940px", top="700px")
setstyle("s1-t1", left="960px", top="105px", font_size="104px"); setstyle("s1-t2", left="960px", top="225px", font_size="190px")
rep('left: 6 + (i % 3) * 178 + "px", top: 6 + Math.floor(i / 3) * 168 + "px", width: "162px", height: "154px"',
    'left: 6 + (i % 4) * 180 + "px", top: 6 + Math.floor(i / 4) * 152 + "px", width: "168px", height: "140px"')
rep("const rest = [[560,170,-6],[700,330,5],[420,430,-9],[640,540,7],[760,730,-4],[470,650,3],[560,880,-8],[700,1000,6],[380,930,-3],[620,1140,-5],[740,1250,8],[460,1190,4],[30,1560,-7],[250,1630,6],[110,1370,-4],[780,1490,-9]];",
    "const rest = [[1000,90,-6],[1260,150,5],[860,250,-9],[1130,330,7],[1470,270,-4],[900,440,3],[1310,460,-8],[1560,410,6],[1030,580,-3],[1170,660,-5],[1480,600,8],[820,640,4],[1640,170,-7],[1640,500,6],[880,810,-4],[1110,780,-9]];")
rep("{ opacity: 0, scale: 0.15, x: -330, y: 340, rotation: -10 }", "{ opacity: 0, scale: 0.15, x: -860, y: -140, rotation: -10 }")
rep("{ x: 575, y: 515, scale: 0.2, rotation: 0, opacity: 0 }", "{ x: 980, y: 285, scale: 0.2, rotation: 0, opacity: 0 }")
rep("{ x: 580, y: 1420, scale: 0.26,", "{ x: 1355, y: 653, scale: 0.26,")

# ------------------------------------------------------------------ S2  dense editing panels (zoom .8)
setstyle("s2-ghost", left="40px", top="690px", font_size="360px")
setstyle("s2-char", left="80px", top="150px", width="640px")
zoomed("s2-p1", 0.8, 740, 70); zoomed("s2-p2", 0.8, 1390, 60); zoomed("s2-p5", 0.8, 760, 400)
zoomed("s2-p3", 0.8, 1390, 340); zoomed("s2-p4", 0.8, 800, 650); zoomed("s2-p6", 0.8, 1330, 700)
setstyle("s2-scr1", left="40px", top="240px"); setstyle("s2-scr2", left="610px", top="330px")

# ------------------------------------------------------------------ S4  3 JAM
setstyle("s4-rays", left="60px", top="80px"); setstyle("s4-clock", left="160px", top="180px")
setstyle("s4-big", left="820px", width="1000px", top="260px", font_size="300px")
setstyle("s4-dep", left="820px", width="1000px", top="610px"); setstyle("s4-lap", left="1100px", top="680px")

# ------------------------------------------------------------------ S5  penat
setstyle("s5-blob", left="1000px", top="200px", width="700px", height="700px")
setstyle("s5-char", left="970px", top="40px", width="700px")
setstyle("s5-prog", left="96px", top="90px")
setstyle("s5-post", left="1570px", top="190px")
setstyle("s5-big", left="96px", top="400px", font_size="200px")

# ------------------------------------------------------------------ S6a  lockup
setstyle("s6a-lbl", left="96px", top="72px")
setstyle("s6a-l1", left="90px", top="165px", font_size="250px"); setstyle("s6a-l2", left="90px", top="379px", font_size="250px"); setstyle("s6a-l3", left="90px", top="593px", font_size="250px")
setstyle("s6a-char", left="1180px", top="140px", width="640px")
rep('{ x: 700, duration: 0.3, ease: "power3.in" }, 23.3);', '{ x: 900, duration: 0.3, ease: "power3.in" }, 23.3);')

# ------------------------------------------------------------------ S6b  VGC + workflow (snake grid)
setstyle("s6b-char", left="10px", top="300px", width="520px")
setstyle("s6b-bel", left="300px", top="90px", font_size="110px")
for t in ("vgc-tile", "vgc-ring1", "vgc-ring2"): setstyle(t, left="700px", top="280px")
rep("{ x: -371, y: -510, scale: 0.32,", "{ x: -781, y: -347, scale: 0.32,")
Z = 0.87
zoomed("n-a", Z, 540, 330); zoomed("n-b", Z, 987, 330); zoomed("n-c", Z, 1434, 330)
zoomed("n-d", Z, 1434, 660); zoomed("n-e", Z, 987, 660)
for nid in ("n-a", "n-b", "n-c", "n-d", "n-e"): setstyle(nid, width="450px")
# directional arrows (horizontal / down / left) in place of the portrait down-arrows; loop arrow removed
A_R = '<svg id="%s" class="abs" style="left:%dpx;top:%dpx" width="50" height="46" viewBox="0 0 50 46"><path d="M4 23 H38 M26 9 L40 23 L26 37" fill="none" stroke="#14171f" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/></svg>'
A_L = '<svg id="%s" class="abs" style="left:%dpx;top:%dpx" width="50" height="46" viewBox="0 0 50 46"><path d="M46 23 H12 M24 9 L10 23 L24 37" fill="none" stroke="#14171f" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/></svg>'
A_D = '<svg id="%s" class="abs" style="left:%dpx;top:%dpx" width="50" height="46" viewBox="0 0 50 46"><path d="M25 2 V34 M10 24 L25 40 L40 24" fill="none" stroke="#14171f" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/></svg>'
for aid, new in (("a-ab", A_R % ("a-ab", 934, 402)), ("a-bc", A_R % ("a-bc", 1381, 402)), ("a-cd", A_D % ("a-cd", 1605, 567)), ("a-de", A_L % ("a-de", 1381, 717))):
    s = re.sub(r'<svg\b[^>]*\bid="%s"[^>]*>.*?</svg>' % aid, new, s, 1, flags=re.S)
s = re.sub(r'<svg\b[^>]*\bid="a-loop"[^>]*>.*?</svg>', "", s, 1, flags=re.S)
rep('tl.fromTo(arrow, { opacity: 0, scaleY: 0, transformOrigin: "50% 0%" }, { opacity: 1, scaleY: 1, duration: 0.2, ease: "power2.out" }, t + 0.12);',
    'tl.fromTo(arrow, { opacity: 0, scale: 0 }, { opacity: 1, scale: 1, duration: 0.2, ease: "back.out(2)" }, t + 0.12);')
s = re.sub(r'\n[^\n]*"#a-loop path:first-child"[^\n]*', "", s, 1)
s = re.sub(r'\n[^\n]*"#a-loophead"[^\n]*', "", s, 1)

# ------------------------------------------------------------------ S7  campak / tidur / siap
setstyle("s7-t1", left="110px", top="170px", font_size="190px"); setstyle("s7-t2", left="110px", top="400px", font_size="150px")
setstyle("s7-ai", left="1280px", top="330px")
rep("{ x: -420, y: 1000 + i * 90, scale: 0.9, rotation: -30, opacity: 1 }, { x: 600 + (i % 2) * 20, y: 960 + (i % 3) * 20,",
    "{ x: -420, y: 560 + i * 70, scale: 0.9, rotation: -30, opacity: 1 }, { x: 1320 + (i % 2) * 20, y: 420 + (i % 3) * 20,")
rep("Math.round(R() * 1040) + \"px\", top: Math.round(R() * 560) + \"px\"", "Math.round(R() * 1840) + \"px\", top: Math.round(R() * 520) + \"px\"")
setstyle("s7-moon", left="150px", top="90px")
setstyle("s7-char", left="1100px", top="70px", width="700px")
setstyle("s7-tidur", left="120px", top="470px", font_size="250px")
setstyle("s7-z1", left="1670px", top="240px"); setstyle("s7-z2", left="1740px", top="180px"); setstyle("s7-z3", left="1790px", top="125px")
setstyle("s7-disc", left="330px", top="250px")
setstyle("s7-siap", left="780px", width="1000px", top="270px", text_align="left")
setstyle("s7-bar", left="780px", top="640px", width="900px")

# ------------------------------------------------------------------ S8  demo (video card right, text left)
setstyle("s8-top1", left="96px", top="110px"); setstyle("s8-top2", left="90px", top="160px", font_size="250px")
setstyle("s8-b1", left="96px", top="500px", font_size="120px"); setstyle("s8-b2", left="96px", top="620px", font_size="120px"); setstyle("s8-b3", left="90px", top="740px", font_size="190px")
setstyle("demo", width="960px", height="960px")
rep('tl.fromTo("#demo", { opacity: 0.2, x: 36, y: 890, scale: 0.94 }, { opacity: 1, x: 36, y: 444, scale: 1,',
    'tl.fromTo("#demo", { opacity: 0.2, x: 1700, y: 60, scale: 0.94 }, { opacity: 1, x: 900, y: 60, scale: 1,')

# ------------------------------------------------------------------ S9  three product cards
setstyle("s9-ada", left="96px", top="150px")
setstyle("s9-w1", left="96px", top="340px", font_size="112px"); setstyle("s9-w2", left="96px", top="340px", font_size="112px"); setstyle("s9-w3", left="96px", top="340px", font_size="100px")
setstyle("s9-k1", left="900px", top="170px", width="380px", height="670px")
setstyle("s9-k2", left="1170px", top="310px", width="380px", height="670px")
setstyle("s9-k3", left="1440px", top="190px", width="380px", height="670px")

# ------------------------------------------------------------------ S10  steps left -> right
setstyle("s10-ghost", left="40px", top="110px")
setstyle("st1", left="0px", top="900px", width="640px", height="260px"); setstyle("st2", left="640px", top="800px", width="640px", height="390px"); setstyle("st3", left="1280px", top="700px", width="700px", height="520px")
setstyle("st1-l", left="90px", font_size="70px"); setstyle("st2-l", left="40px", font_size="70px"); setstyle("st3-l", left="50px", font_size="110px")
setstyle("s10-char", left="120px", top="325px", width="400px")
rep("const base = [-120, 230, 470]; const tops = [1560, 1330, 1100]; const dy = 884; /* feet = top + 884 */", "const base = [120, 760, 1400]; const tops = [900, 800, 700]; const dy = 575; /* feet = top + 575 */")
rep("y: tops[1] - tops[0] - 140", "y: tops[1] - tops[0] - 110"); rep("y: tops[2] - tops[0] - 140", "y: tops[2] - tops[0] - 110")
rep('left: "700px", top: "500px"', 'left: "1560px", top: "260px"')

# ------------------------------------------------------------------ S11  CTA
setstyle("s11-nm", left="96px", top="150px"); setstyle("s11-post", left="90px", top="210px", font_size="170px")
setstyle("s11-hh", left="90px", top="390px", font_size="150px")
s = re.sub(r'(id="s11-hh"[^>]*>)HARI-HARI\?', r"\1HARI-<br />HARI?", s, 1)
setstyle("s11-cal", zoom=0.85, left="1158px", top="270px", width="1080px", height="800px")
setstyle("s11-logo", left="820px", top="60px", width="460px")
setstyle("s11-k", left="816px", top="355px", font_size="150px")
setstyle("s11-d1", left="816px", top="520px"); setstyle("s11-d2", left="816px", top="655px")
setstyle("s11-btn", left="830px", top="838px")
setstyle("s11-cur", left="1060px", top="915px"); setstyle("s11-ring", left="1040px", top="895px")
setstyle("s11-char", left="20px", top="130px", width="640px")
rep('{ opacity: 0, x: -500, y: 100, rotation: -8 }', '{ opacity: 0, x: -500, y: 100, rotation: -8 }')

open(os.path.join(ROOT, "master", "index.master16.html"), "w").write(s)
print("written master/index.master16.html")
