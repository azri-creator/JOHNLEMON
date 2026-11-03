# Build hf/index.html for "Kepada Educators" 16:9 (Storyteller-reference editing DNA).
# Timeline = A-roll from source 10.06 s ("Para pendidik kita...") + 2.7 s end card. Times from work/times.json.
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = json.load(open(os.path.join(ROOT, 'work/times.json')))
# manual fixes where adjacent onsets collide
T.update(edit=36.95, video=37.12, guna=37.35, code=37.85, slide=3.42)
DUR, AROLL, END = 48.1, 45.40, 45.40
PERSON0 = 19.80            # cut-out clip = source 29.86 s
YEL = '#FFE600'
FACE = '1010px 420px'      # face centre, used as zoom origin

def t(k, d=0.0):
    return round(T[k] + d, 3)

CARD = dict(left=620, top=208, w=1180, h=664)          # slide -> video card
THUMB = dict(w=300, h=169, cx=CARD['left'] - 40 + 150, cy=CARD['top'] + CARD['h'] - 130 + 84)

html = f'''<!doctype html>
<html lang="ms">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=1920, height=1080" />
<title>Kepada Educators 16x9</title>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>
  body {{ margin:0; background:#0F1419; }}
  #root {{ position:relative; width:100%; height:100%; overflow:hidden; background:#0F1419;
          font-family:Inter, system-ui, sans-serif; color:#fff; }}
  .layer {{ position:absolute; inset:0; }}
  .fill {{ position:absolute; inset:0; width:100%; height:100%; object-fit:cover; }}
  .hide {{ opacity:0; }}
  .stage {{ position:absolute; inset:0; background:#0F1419; overflow:hidden; }}
  .grain {{ position:absolute; inset:0; background:url(assets/grain.png); background-size:960px 540px;
           opacity:.07; mix-blend-mode:overlay; }}
  .big {{ font-family:'Archivo Black', sans-serif; text-transform:uppercase; line-height:.95;
         letter-spacing:.035em; color:#fff; white-space:nowrap;
         text-shadow:0 0 28px rgba(255,255,255,.28), 0 0 70px rgba(255,255,255,.12); }}
  .y {{ color:{YEL}; text-shadow:0 0 30px rgba(255,230,0,.35), 0 0 80px rgba(255,230,0,.15); }}
  .sh {{ filter:drop-shadow(0 2px 6px rgba(0,0,0,.34)) drop-shadow(0 6px 26px rgba(0,0,0,.5)); }}
  .kick {{ font-family:Inter, sans-serif; font-weight:600; font-size:30px; letter-spacing:.32em;
          text-transform:uppercase; color:rgba(255,255,255,.78); white-space:nowrap; }}
  .kick b {{ color:{YEL}; font-weight:800; margin-right:22px; }}
  .center {{ position:absolute; inset:0; display:flex; flex-direction:column; align-items:center;
            justify-content:center; gap:34px; }}
  .abs {{ position:absolute; }}
  .card {{ position:absolute; border-radius:24px; overflow:hidden; background:#000;
          border:2px solid rgba(255,255,255,.16);
          box-shadow:0 0 0 1px rgba(255,255,255,.04), 0 0 60px rgba(255,255,255,.10), 0 30px 80px rgba(0,0,0,.55); }}
  .card video, .card img {{ position:absolute; inset:0; width:100%; height:100%; object-fit:cover; }}
  .check {{ display:flex; align-items:center; gap:26px; height:96px; }}
  .dot {{ width:56px; height:56px; border-radius:50%; border:3px solid rgba(255,255,255,.55);
         position:relative; flex:none; }}
  .dot i {{ position:absolute; inset:-3px; border-radius:50%; background:{YEL}; opacity:0; }}
  .dot svg {{ position:absolute; inset:10px; opacity:0; }}
  .lbl {{ font-family:Inter, sans-serif; font-weight:700; font-size:42px; white-space:nowrap; }}
  .pill {{ position:absolute; padding:18px 42px; border-radius:999px; border:3px solid rgba(255,255,255,.9);
          background:rgba(15,20,25,.62); font-family:Inter, sans-serif; font-weight:800; font-size:54px;
          white-space:nowrap; }}
  .box {{ position:absolute; width:560px; height:100px; margin-left:-280px; margin-top:-50px; border-radius:18px;
         background:rgba(15,20,25,.95); border:2px solid rgba(255,255,255,.18);
         box-shadow:0 18px 40px rgba(0,0,0,.45); display:flex; align-items:center; justify-content:center;
         font-family:Inter, sans-serif; font-weight:700; font-size:42px; white-space:nowrap; }}
  .tnode {{ position:absolute; border-radius:20px; border:3px solid rgba(255,255,255,.85); padding:22px 34px;
           font-family:'Archivo Black', sans-serif; font-size:40px; letter-spacing:.03em; white-space:nowrap;
           text-transform:uppercase; transform-origin:50% 50%; }}
  .thumb {{ position:absolute; border-radius:12px; overflow:hidden; box-shadow:0 10px 30px rgba(0,0,0,.5); }}
  .thumb img {{ width:100%; height:100%; object-fit:cover; display:block; }}
  .ring {{ position:absolute; inset:-8px; border-radius:18px; border:6px solid {YEL}; opacity:0;
          box-shadow:0 0 30px rgba(255,230,0,.5); }}
</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-width="1920" data-height="1080" data-duration="{DUR}">

  <audio id="mix" src="assets/mix.wav" data-start="0" data-duration="{DUR}" data-track-index="30" data-volume="1"></audio>

  <!-- A-roll (library) -->
  <div id="camA" class="layer" style="--fe:0px;-webkit-mask-image:linear-gradient(90deg,#000 0,#000 calc(100% - var(--fe)),transparent 100%);mask-image:linear-gradient(90deg,#000 0,#000 calc(100% - var(--fe)),transparent 100%)">
    <video id="aroll" class="fill" src="assets/aroll.mp4" muted playsinline data-start="0" data-duration="{AROLL}" data-track-index="0"></video>
  </div>

  <!-- hook words -->
  <div id="tPara" class="abs sh hide" style="left:0;right:0;top:92px;text-align:center"><div class="big" style="font-size:104px">Para Pendidik</div></div>
  <div id="wIlmu" class="abs sh hide" style="left:120px;top:300px;width:440px;text-align:center">
    <svg width="150" height="120" viewBox="0 0 150 120" fill="none" stroke="#fff" stroke-width="6" stroke-linejoin="round" stroke-linecap="round">
      <path d="M75 26 C55 12 28 12 10 18 V104 C28 98 55 98 75 112 C95 98 122 98 140 104 V18 C122 12 95 12 75 26 Z"/><path d="M75 26 V112"/></svg>
    <div class="big" style="font-size:150px;margin-top:10px">Ilmu</div></div>
  <div id="wSlide" class="abs sh hide" style="left:1360px;top:300px;width:470px;text-align:center">
    <svg width="160" height="120" viewBox="0 0 160 120" fill="none" stroke="{YEL}" stroke-width="6" stroke-linejoin="round" stroke-linecap="round">
      <rect x="8" y="8" width="144" height="88" rx="8"/><path d="M80 96 V114 M56 114 H104 M30 32 H96 M30 52 H120 M30 72 H84"/></svg>
    <div class="big y" style="font-size:150px;margin-top:10px">Slide</div></div>

  <!-- konteks caption -->
  <div id="capK" class="abs sh" style="left:40px;top:300px;width:560px;text-align:center">
    <div id="capK1" class="big hide" style="font-size:92px;line-height:1.08"><span style="display:block">Pelajar</span><span style="display:block">Faham</span></div>
    <div id="capK2" class="big y hide" style="font-size:92px;line-height:1.08">Konteks</div></div>

  <!-- presenter-side labels for later beats -->
  <div id="pCl" class="pill sh hide" style="left:250px;top:390px">Claude</div>
  <div id="pGp" class="pill sh hide" style="left:1370px;top:390px">ChatGPT</div>

  <!-- tree panel (presenter slid left) -->
  <div id="tree" class="hide" style="position:absolute;left:950px;top:150px;width:880px;height:780px;border-radius:30px;background:rgba(15,20,25,.95);border:2px solid rgba(255,255,255,.14);box-shadow:0 30px 80px rgba(0,0,0,.5)">
    <svg class="abs" style="left:0;top:0" width="880" height="780" fill="none" stroke="rgba(255,255,255,.75)" stroke-width="5" stroke-linecap="round">
      <path id="trL" d="M440 250 V330 Q440 360 410 360 H250 Q220 360 220 390 V470"/>
      <path id="trR" d="M440 330 Q440 360 470 360 H630 Q660 360 660 390 V470"/></svg>
    <div id="tRoot" class="tnode" style="left:440px;top:170px;margin-left:-170px;width:340px;text-align:center;box-sizing:border-box">Buat Video</div>
    <div id="tSkill" data-layout-ignore class="tnode" style="left:220px;top:520px;margin-left:-190px;width:380px;text-align:center;box-sizing:border-box;line-height:1.1">Skill<span style="display:block">Editing</span></div>
    <div id="tKnow" class="tnode" style="left:660px;top:520px;margin-left:-190px;width:380px;text-align:center;box-sizing:border-box;line-height:1.1">Knowledge<span style="display:block">Workflow</span></div>
    <svg id="tX" class="abs" style="left:150px;top:500px;opacity:0" width="140" height="140" viewBox="0 0 140 140" stroke="#FF5A4F" stroke-width="16" stroke-linecap="round"><path d="M22 22 L118 118 M118 22 L22 118"/></svg>
  </div>

  <!-- cut-out presenter over stock backgrounds -->
  <div id="cut" class="layer hide">
    <div id="bgCave" class="layer"><img class="fill" src="assets/bg/cave.jpg" alt=""></div>
    <div id="bgBed" class="layer"><img class="fill" src="assets/bg/bedroom.jpg" alt=""></div>
    <div id="bgStudio" class="layer"><img class="fill" src="assets/bg/studio.jpg" alt=""></div>
    <div id="camP" class="layer">
      <video id="person" class="fill" src="assets/person.webm" muted playsinline data-start="{PERSON0}" data-duration="10.76" data-track-index="1"></video>
    </div>
    <div id="lSalah" class="abs sh hide" style="left:60px;top:300px;width:560px;text-align:center">
      <div class="big" style="font-size:110px;line-height:1.05"><span style="display:block">Salah</span><span style="display:block">Cara</span></div>
      <svg width="120" height="120" viewBox="0 0 140 140" stroke="#FF5A4F" stroke-width="18" stroke-linecap="round" style="margin-top:18px"><path d="M22 22 L118 118 M118 22 L22 118"/></svg></div>
    <div id="lCikgu" class="abs sh hide" style="left:0;right:0;top:96px;text-align:center"><div class="big" style="font-size:84px">Cikgu &amp; Lecturer</div></div>
  </div>

  <!-- bedroom pile panel -->
  <div id="pile" class="layer" style="pointer-events:none">
    <div id="b1" class="box hide" style="left:1380px;top:800px">Cari bahan</div>
    <div id="b2" class="box hide" style="left:1380px;top:690px">Susun slide</div>
    <div id="b3" class="box hide" style="left:1380px;top:580px">Cari video</div>
    <div id="b4" class="box hide" style="left:1380px;top:470px">Edit sendiri</div>
    <div id="b5" class="box hide" style="left:1380px;top:360px;color:{YEL}">Chapter seterusnya…</div>
  </div>

  <!-- chapter cards -->
  <div id="card1" class="stage hide"><div class="grain"></div>
    <div class="center"><div class="kick"><b>01</b>Bayangkan</div><div id="c1w" class="big" style="font-size:200px">Satu <span class="y">Slide</span></div></div></div>
  <div id="card2" class="stage hide"><div class="grain"></div>
    <div class="center"><div class="kick"><b>02</b>Sebab itulah</div><div id="c2w" class="big" style="font-size:200px">AI = <span class="y">Pisau</span></div></div></div>
  <div id="card3" class="stage hide"><div class="grain"></div>
    <div class="center" style="gap:26px"><div class="kick"><b>03</b>Panduan</div>
      <div class="big" style="font-size:176px"><span id="c3a">Edit</span> <span id="c3b">Video</span></div>
      <div class="big" style="font-size:176px"><span id="c3c">Guna</span> <span id="c3d" class="y">Code</span></div></div></div>

  <!-- slide -> video stage -->
  <div id="stgV" class="stage hide"><div class="grain"></div>
    <div id="chk" class="abs" style="left:110px;top:300px">
      <div class="check" id="k1"><div class="dot"><i></i><svg viewBox="0 0 36 36" fill="none" stroke="#0F1419" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"><path d="M7 19 L15 27 L30 10"/></svg></div><div class="lbl">Video motion</div></div>
      <div class="check" id="k2"><div class="dot"><i></i><svg viewBox="0 0 36 36" fill="none" stroke="#0F1419" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"><path d="M7 19 L15 27 L30 10"/></svg></div><div class="lbl">Education</div></div>
      <div class="check" id="k3"><div class="dot"><i></i><svg viewBox="0 0 36 36" fill="none" stroke="#0F1419" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"><path d="M7 19 L15 27 L30 10"/></svg></div><div class="lbl">Voice over</div></div>
      <div class="check" id="k4"><div class="dot"><i></i><svg viewBox="0 0 36 36" fill="none" stroke="#0F1419" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"><path d="M7 19 L15 27 L30 10"/></svg></div><div class="lbl">Animation</div></div>
    </div>
    <div id="vcard" class="card" style="left:{CARD['left']}px;top:{CARD['top']}px;width:{CARD['w']}px;height:{CARD['h']}px">
      <div id="vc1" class="layer"><video id="v1" src="assets/clips/sv1.mp4" muted playsinline data-start="6.95" data-duration="2.7" data-track-index="2"></video></div>
      <div id="vc2" class="layer"><video id="v2" src="assets/clips/sv2.mp4" muted playsinline data-start="8.95" data-duration="2.3" data-track-index="3"></video></div>
      <div id="vc3" class="layer"><video id="v3" src="assets/clips/sv3.mp4" muted playsinline data-start="10.95" data-duration="1.5" data-track-index="4"></video></div>
    </div>
    <div id="th2" class="thumb hide" style="left:{THUMB['cx']-150}px;top:{THUMB['cy']-84}px;width:300px;height:169px;background:#fff"><img src="assets/slide_fractions.jpg" alt="" style="object-fit:contain"></div>
    <div id="th3" class="thumb hide" style="left:{THUMB['cx']-150}px;top:{THUMB['cy']-84}px;width:300px;height:169px;background:#fff"><img src="assets/slide_energy.jpg" alt="" style="object-fit:contain"></div>
    <div id="tri" class="layer">
      <div id="tr1" class="card hide" style="left:80px;top:362px;width:560px;height:315px"><video id="v4" src="assets/clips/tv1.mp4" muted playsinline data-start="12.45" data-duration="2.8" data-track-index="5"></video></div>
      <div id="tr2" class="card hide" style="left:680px;top:362px;width:560px;height:315px"><video id="v5" src="assets/clips/tv2.mp4" muted playsinline data-start="12.45" data-duration="2.8" data-track-index="6"></video></div>
      <div id="tr3" class="card hide" style="left:1280px;top:362px;width:560px;height:315px"><video id="v6" src="assets/clips/tv3.mp4" muted playsinline data-start="12.45" data-duration="2.8" data-track-index="7"></video></div>
      <div id="triL" class="layer hide">
        <div class="kick abs" style="left:80px;width:560px;top:712px;text-align:center">Sejarah</div>
        <div class="kick abs" style="left:680px;width:560px;top:712px;text-align:center">Matematik</div>
        <div class="kick abs" style="left:1280px;width:560px;top:712px;text-align:center">Fizik</div></div>
    </div>
  </div>

  <!-- slide cards (panel, then the front one becomes the video card) -->
  <div id="slides" class="layer" style="pointer-events:none">
    <div id="sEn" class="card hide" style="left:1110px;top:300px;width:560px;height:420px;background:#fff"><img src="assets/slide_energy.jpg" alt=""></div>
    <div id="sFr" class="card hide" style="left:1430px;top:300px;width:300px;height:424px;background:#fff"><img src="assets/slide_fractions.jpg" alt=""></div>
    <div id="sSj" class="card hide" style="left:{CARD['left']}px;top:{CARD['top']}px;width:{CARD['w']}px;height:{CARD['h']}px;background:#fff"><img src="assets/slide_sejarah.jpg" alt=""></div>
    <div id="thLbl" class="kick hide" style="position:absolute;z-index:5;background:#0F1419;padding:8px 16px 6px;border-radius:8px;left:{THUMB['cx']-150}px;top:{THUMB['cy']-84-66}px;font-size:28px;letter-spacing:.28em">Sebelum</div>
  </div>

  <!-- knife metaphor (light stage) -->
  <div id="knife" class="stage hide" style="background:#E8E6E1">
    <svg class="abs" style="left:110px;top:380px;transform:rotate(-14deg)" width="920" height="300" viewBox="0 0 920 300" fill="none" stroke="#14181D" stroke-width="8" stroke-linecap="round" stroke-linejoin="round">
      <path id="kBlade" d="M590 110 L150 110 Q70 112 30 150 Q120 200 300 205 L590 205"/>
      <path id="kHandle" d="M590 96 L626 96 L626 219 L590 219 Z M626 118 L870 118 Q900 118 900 148 L900 168 Q900 198 870 198 L626 198"/>
      <path id="kEdge" d="M70 160 Q170 190 320 192 L560 192 M700 158 h1 M800 158 h1" stroke-width="5"/></svg>
    <div id="kLbl" class="abs hide" style="left:1110px;top:300px">
      <div style="display:inline-block;background:{YEL};padding:6px 18px 2px;border-radius:6px"><div class="big" style="font-size:60px;color:#14181D;text-shadow:none">Betul cara guna</div></div>
      <svg width="86" height="86" viewBox="0 0 36 36" fill="none" stroke="#14181D" stroke-width="5" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle;margin-left:16px"><path d="M7 19 L15 27 L30 10"/></svg></div>
    <div id="kBox" class="abs hide" style="left:1150px;top:500px;width:520px;height:220px">
      <div id="kTop" class="abs" style="inset:0;border:6px solid #14181D;border-radius:22px;clip-path:polygon(0 0,100% 0,100% 38%,0 62%);display:flex;align-items:center;justify-content:center"><div class="big" style="font-size:80px;color:#14181D;text-shadow:none">Hasil</div></div>
      <div id="kBot" class="abs" style="inset:0;border:6px solid #14181D;border-radius:22px;clip-path:polygon(0 62%,100% 38%,100% 100%,0 100%);display:flex;align-items:center;justify-content:center"><div class="big" style="font-size:80px;color:#14181D;text-shadow:none">Hasil</div></div>
      <svg id="kCut" class="abs" style="left:-60px;top:0" width="640" height="220" fill="none" stroke="#14181D" stroke-width="5" stroke-linecap="round"><path id="kCutP" d="M0 170 L640 50"/></svg>
    </div>
  </div>

  <!-- full-screen 3D tilt screens -->
  <div id="tiltA" class="stage hide" style="background:#06090D">
    <img id="tp05" src="assets/tilt/c05.jpg" alt="" style="position:absolute;left:-250px;top:-233px;width:2420px;height:1546px">
    <img id="tp06" src="assets/tilt/c06.jpg" alt="" style="position:absolute;left:-250px;top:-233px;width:2420px;height:1546px;opacity:0">
    <img id="tp07" src="assets/tilt/c07.jpg" alt="" style="position:absolute;left:-250px;top:-233px;width:2420px;height:1546px;opacity:0"></div>
  <div id="tiltB" class="stage hide" style="background:#06090D">
    <img id="tp01" src="assets/tilt/c01.jpg" alt="" style="position:absolute;left:-250px;top:-233px;width:2420px;height:1546px"></div>

  <!-- module montage + student results -->
  <div id="mont" class="stage hide"><div class="grain"></div>
    <div id="grid" class="abs" style="left:28px;top:110px;width:1864px;height:860px">
'''
# 17 thumbnails, 5 x 4 grid
for i in range(17):
    r, c = divmod(i, 5)
    x = c * 376 + (int(1.5 * 376) if r == 3 else 0)
    html += (f'      <div id="g{i+1}" class="thumb hide" style="left:{x}px;top:{r*219}px;width:360px;height:203px">'
             f'<img src="assets/thumb/R{i+1:02d}.jpg" alt="">{"<div class=ring></div>" if i in (0, 16) else ""}</div>\n')
html += f'''    </div>
    <div id="res" class="layer">
      <div id="resL" class="kick abs hide" style="left:0;right:0;top:96px;text-align:center">Hasil student</div>
      <div id="rc1" class="card hide" style="left:530px;top:170px;width:420px;height:706px"><video id="v7" src="assets/clips/res2.mp4" muted playsinline data-start="40.62" data-duration="1.5" data-track-index="8"></video></div>
      <div id="rc2" class="card hide" style="left:990px;top:170px;width:420px;height:729px"><video id="v8" src="assets/clips/res4.mp4" muted playsinline data-start="40.62" data-duration="1.5" data-track-index="9"></video></div>
    </div>
  </div>

  <!-- end card -->
  <div id="endc" class="stage hide">
    <img id="endBg" class="fill" src="assets/lastframe.jpg" alt="">
    <div class="center" style="gap:40px">
      <img id="endLogo" src="assets/logo.png" alt="" style="width:250px;height:250px">
      <div id="endT" class="big sh" style="font-size:100px">Nama Brand</div></div>
  </div>
  <!-- claim badge, whole video -->
  <div id="badge" style="position:absolute;left:36px;bottom:30px;z-index:50;display:flex;align-items:center;gap:16px;padding:12px 24px 12px 18px;border-radius:16px;background:rgba(15,20,25,.74);border:1.5px solid rgba(255,255,255,.18);box-shadow:0 8px 24px rgba(0,0,0,.35)">
    <svg width="38" height="38" viewBox="0 0 24 24" fill="{YEL}"><path d="M12 1.5 L14.2 9.8 L22.5 12 L14.2 14.2 L12 22.5 L9.8 14.2 L1.5 12 L9.8 9.8 Z"/></svg>
    <div style="font-family:Inter, sans-serif;white-space:nowrap;line-height:1.18">
      <div style="font-weight:800;font-size:28px;letter-spacing:.02em"><span style="color:{YEL}">100%</span> DIEDIT OLEH CLAUDE</div>
      <div style="font-weight:500;font-size:28px;color:rgba(255,255,255,.78)">Claude Opus 5.5 · High · Siap 20 minit</div></div>
  </div>
</div>

<script>
const tl = gsap.timeline({{ paused: true }});
const S = 'sine.inOut', P3 = 'power3.inOut', BO = 'back.out(1.6)';
const blurIn = (el, at, d = .45, y = 0) => tl.fromTo(el, {{ opacity: 0, filter: 'blur(18px)', scale: 1.06, y }}, {{ opacity: 1, filter: 'blur(0px)', scale: 1, y: 0, duration: d, ease: 'power2.out', immediateRender: false }}, at);
const blurOut = (el, at, d = .35) => tl.to(el, {{ opacity: 0, filter: 'blur(14px)', duration: d, ease: 'power2.in' }}, at);
const show = (el, at, d = .3) => tl.to(el, {{ opacity: 1, duration: d, ease: 'power1.out' }}, at);
const hide = (el, at, d = .3) => tl.to(el, {{ opacity: 0, duration: d, ease: 'power1.in' }}, at);
const popIn = (el, at) => tl.fromTo(el, {{ opacity: 0, scale: .6 }}, {{ opacity: 1, scale: 1, duration: .38, ease: BO, immediateRender: false }}, at);
gsap.set('#camA', {{ transformOrigin: '{FACE}' }});
gsap.set('#camP', {{ transformOrigin: '{FACE}' }});
['#bgBed', '#bgStudio'].forEach(s => gsap.set(s, {{ xPercent: 100 }}));
gsap.set('#bgBed', {{ scale: 1.12, xPercent: 115 }});
gsap.set('#cut', {{ xPercent: 100 }});
gsap.set(['#c3a', '#c3b', '#c3c', '#c3d', '#tRoot', '#tSkill', '#tKnow', '#vc1', '#chk'], {{ opacity: 0 }});
gsap.set('#grid', {{ scale: 2.4 }});
gsap.set(['#vc2', '#vc3'], {{ xPercent: 100 }});

// ---- 1. hook: para pendidik / ilmu / slide ----
tl.fromTo('#camA', {{ scale: 1.0 }}, {{ scale: 1.07, duration: 3.9, ease: S }}, 0);
blurIn('#tPara', 0.27, .3, -20);
tl.fromTo('#badge', {{ opacity: 0, x: -20 }}, {{ opacity: 1, x: 0, duration: .35, ease: 'power2.out', immediateRender: false }}, 0.27);
blurOut('#tPara', {t('ilmu', -0.25)});
popIn('#wIlmu', {t('ilmu', -0.04)});
popIn('#wSlide', {t('slide', -0.04)});
tl.to(['#wIlmu', '#wSlide'], {{ y: -10, duration: 1.2, ease: S }}, {t('slide')});

// ---- 2. chapter card 1 ----
blurIn('#card1', 3.86, .35);
tl.fromTo('#c1w', {{ scale: 1.0 }}, {{ scale: 1.05, duration: 1.5, ease: S }}, 3.9);
tl.set(['#wIlmu', '#wSlide'], {{ opacity: 0 }}, 4.2);
tl.set('#camA', {{ scale: 1.0 }}, 4.2);
blurOut('#card1', 5.18, .3);

// ---- 3. "macam ni": presenter slides left, three real slides stack on the right ----
tl.to('#camA', {{ x: -560, '--fe': '360px', duration: .55, ease: P3 }}, {t('macam', -0.12)});
gsap.set('#sSj', {{ x: 1380 - {CARD['left'] + CARD['w']/2}, y: 520 - {CARD['top'] + CARD['h']/2}, scale: 760 / {CARD['w']}, rotation: -2 }});
gsap.set('#sEn', {{ rotation: 7 }}); gsap.set('#sFr', {{ rotation: -6 }});
tl.fromTo('#sEn', {{ opacity: 0, y: 80 }}, {{ opacity: 1, y: 0, duration: .35, ease: 'power3.out', immediateRender: false }}, {t('macam', 0.02)});
tl.fromTo('#sFr', {{ opacity: 0, y: 80 }}, {{ opacity: 1, y: 0, duration: .35, ease: 'power3.out', immediateRender: false }}, {t('macam', 0.2)});
tl.fromTo('#sSj', {{ opacity: 0, y: 520 - {CARD['top'] + CARD['h']/2} + 80 }}, {{ opacity: 1, y: 520 - {CARD['top'] + CARD['h']/2}, duration: .26, ease: 'power3.out', immediateRender: false }}, {t('macam', 0.38)});

// ---- 4. "transform": front slide flies into the video card, becomes the real video ----
show('#stgV', {t('transform', -0.05)}, .3);
tl.to(['#sEn', '#sFr'], {{ opacity: 0, x: '+=260', duration: .3, ease: 'power2.in' }}, {t('transform', -0.05)});
tl.to('#sSj', {{ x: 0, y: 0, scale: 1, rotation: 0, duration: .42, ease: P3 }}, {t('transform')});
tl.set('#camA', {{ x: 0, scale: 1.12, '--fe': '0px' }}, 7.6);
tl.fromTo('#vc1', {{ opacity: 0 }}, {{ opacity: 1, duration: .25, immediateRender: false }}, 7.08);
// the slide shrinks into the corner as the "before" thumbnail
tl.to('#sSj', {{ x: {THUMB['cx']} - {CARD['left'] + CARD['w']/2}, y: {THUMB['cy']} - {CARD['top'] + CARD['h']/2}, scale: 300 / {CARD['w']}, duration: .5, ease: P3 }}, 7.25);
show('#thLbl', 7.6, .25);
tl.fromTo('#chk', {{ opacity: 0, x: -30 }}, {{ opacity: 1, x: 0, duration: .4, ease: 'power2.out', immediateRender: false }}, 7.3);
gsap.set('.check', {{ opacity: .38 }});
const tick = (k, at) => {{
  tl.to(`#${{k}}`, {{ opacity: 1, duration: .15 }}, at);
  tl.fromTo(`#${{k}} .dot i`, {{ opacity: 0, scale: .4 }}, {{ opacity: 1, scale: 1, duration: .28, ease: BO, immediateRender: false }}, at);
  tl.to(`#${{k}} .dot svg`, {{ opacity: 1, duration: .12 }}, at + .08);
  tl.fromTo(`#${{k}} .lbl`, {{ x: 0 }}, {{ x: 10, duration: .15, yoyo: true, repeat: 1, immediateRender: false }}, at);
}};
tick('k1', {t('motion')});
tick('k2', {t('education', -0.04)});
tick('k3', {t('over')});
tick('k4', {t('animation')});
// pushes between slide videos
tl.to('#vc1', {{ xPercent: -100, duration: .4, ease: P3 }}, {t('education', -0.16)});
tl.to('#vc2', {{ xPercent: 0, duration: .4, ease: P3 }}, {t('education', -0.16)});
tl.to('#sSj', {{ opacity: 0, duration: .2 }}, {t('education', -0.05)});
show('#th2', {t('education', -0.05)}, .2);
tl.to('#vc2', {{ xPercent: -100, duration: .4, ease: P3 }}, {t('over', -0.18)});
tl.to('#vc3', {{ xPercent: 0, duration: .4, ease: P3 }}, {t('over', -0.18)});
hide('#th2', {t('over', -0.05)}, .2);
show('#th3', {t('over', -0.05)}, .2);
// "animation": all three play side by side
tl.to(['#vcard', '#chk', '#th3', '#thLbl'], {{ opacity: 0, scale: .94, duration: .3, ease: 'power2.in' }}, 12.50);
['#tr1', '#tr2', '#tr3'].forEach((s, i) => tl.fromTo(s, {{ opacity: 0, y: 50, scale: .9 }}, {{ opacity: 1, y: 0, scale: 1, duration: .4, ease: 'power3.out', immediateRender: false }}, 12.58 + i * .08));
show('#triL', 12.8, .3);
blurOut('#stgV', 14.85, .4);

// ---- 5. pelajar faham konteks (medium framing) ----
tl.to('#camA', {{ scale: 1.16, duration: 1.4, ease: S }}, 14.85);
blurIn('#capK1', 14.95, .35, 20);
blurIn('#capK2', 15.50, .35, 20);
tl.set('#capK', {{ opacity: 0 }}, 16.5);

// ---- 6. chapter card 2 + knife metaphor ----
blurIn('#card2', {t('sebab', -0.04)}, .35);
tl.fromTo('#c2w', {{ scale: 1.0 }}, {{ scale: 1.05, duration: 1.5, ease: S }}, {t('sebab')});
tl.set('#camA', {{ scale: 1.0 }}, 16.6);
tl.fromTo('#knife', {{ xPercent: 100 }}, {{ xPercent: 0, duration: .45, ease: P3, immediateRender: false }}, {t('pisau', -0.16)});
tl.set('#knife', {{ opacity: 1 }}, {t('pisau', -0.16)});
tl.to('#card2', {{ xPercent: -100, duration: .45, ease: P3 }}, {t('pisau', -0.16)});
['#kBlade', '#kHandle', '#kEdge'].forEach((s, i) => {{
  const L = document.querySelector(s).getTotalLength();
  gsap.set(s, {{ strokeDasharray: L, strokeDashoffset: L }});
  tl.to(s, {{ strokeDashoffset: 0, duration: .55, ease: 'power2.inOut' }}, {t('pisau', -0.1)} + i * .12);
}});
popIn('#kLbl', {t('betul', 0.05)});
show('#kBox', {t('betul', 0.5)}, .3);
{{ const L = document.querySelector('#kCutP').getTotalLength();
  gsap.set('#kCutP', {{ strokeDasharray: L, strokeDashoffset: L }});
  tl.to('#kCutP', {{ strokeDashoffset: 0, duration: .16, ease: 'power2.in' }}, {t('okey', 0.0)});
  tl.to('#kCut', {{ opacity: 0, duration: .2 }}, {t('okey', 0.25)}); }}
tl.to('#kTop', {{ x: -16, y: -18, rotation: -2, duration: .35, ease: 'power3.out' }}, {t('okey', 0.14)});
tl.to('#kBot', {{ x: 16, y: 18, rotation: 2, duration: .35, ease: 'power3.out' }}, {t('okey', 0.14)});

// ---- 7. cave -> bedroom -> studio (cut-out presenter, horizontal pushes) ----
tl.set('#cut', {{ opacity: 1 }}, 19.80);
tl.fromTo('#cut', {{ xPercent: 100 }}, {{ xPercent: 0, duration: .45, ease: P3, immediateRender: false }}, {t('salah', -0.2)});
tl.to('#knife', {{ xPercent: -100, duration: .45, ease: P3 }}, {t('salah', -0.2)});
tl.fromTo('#bgCave', {{ scale: 1.0 }}, {{ scale: 1.05, duration: 2.2, ease: S }}, {t('salah')});
popIn('#lSalah', {t('salah', 0.42)});
blurOut('#lSalah', {t('kalau', -0.3)}, .25);
tl.to('#bgCave', {{ xPercent: -100, duration: .5, ease: P3 }}, {t('kalau', -0.12)});
tl.to('#bgBed', {{ xPercent: 0, duration: .5, ease: P3 }}, {t('kalau', -0.12)});
// slide left + pile of chores
tl.to('#camP', {{ x: -560, duration: .55, ease: P3 }}, {t('cari', -0.2)});
tl.to('#bgBed', {{ x: -150, duration: .55, ease: P3 }}, {t('cari', -0.2)});
const drop = (s, at, rot) => tl.fromTo(s, {{ opacity: 0, y: -60, rotation: 0 }}, {{ opacity: 1, y: 0, rotation: rot, duration: .32, ease: 'back.out(1.3)', immediateRender: false }}, at);
drop('#b1', {t('cari')}, -1.5); drop('#b2', 24.42, 1.8); drop('#b3', 25.02, -1.2); drop('#b4', 25.62, 2.2); drop('#b5', {t('chapter')}, -1.8);
tl.to(['#b1', '#b2', '#b3', '#b4', '#b5'], {{ opacity: 0, y: 40, duration: .3, stagger: .03, ease: 'power2.in' }}, {t('sekarang', -0.32)});
tl.to('#camP', {{ x: 0, duration: .5, ease: P3 }}, {t('sekarang', -0.15)});
tl.to('#bgBed', {{ xPercent: -115, duration: .5, ease: P3 }}, {t('sekarang', -0.15)});
tl.to('#bgStudio', {{ xPercent: 0, duration: .5, ease: P3 }}, {t('sekarang', -0.15)});
tl.fromTo('#camP', {{ scale: 1.0 }}, {{ scale: 1.06, duration: 2.6, ease: S, immediateRender: false }}, {t('sekarang', 0.3)});
blurIn('#lCikgu', {t('cikgu2', -0.05)}, .35, -20);
blurOut('#lCikgu', {t('control', -0.25)}, .25);

// ---- 8. "control sendiri": Prompt Vault, full-screen 3D tilt ----
const tilt = (el, at, d, ry0, ry1, rx0, rx1, y0, y1) => tl.fromTo(el, {{ transformPerspective: 1700, rotationY: ry0, rotationX: rx0, y: y0, scale: 1.0 }}, {{ rotationY: ry1, rotationX: rx1, y: y1, scale: 1.03, duration: d, ease: 'power2.out', immediateRender: false }}, at);
tl.fromTo('#tiltA', {{ opacity: 0, scale: 1.12, filter: 'blur(16px)' }}, {{ opacity: 1, scale: 1, filter: 'blur(0px)', duration: .4, ease: 'power3.out', immediateRender: false }}, {t('control', -0.04)});
tl.set('#tiltA', {{ filter: 'none' }}, {t('control', 0.4)});
tilt('#tp05', {t('control', -0.04)}, 0.8, -11, -6, 7, 4, 120, 60);
tl.set('#cut', {{ opacity: 0 }}, 30.45);
const swap = (el, at) => {{ tl.fromTo(el, {{ opacity: 0, filter: 'blur(14px)' }}, {{ opacity: 1, filter: 'blur(0px)', duration: .22, immediateRender: false }}, at); tl.set(el, {{ filter: 'none' }}, at + .24); }};
swap('#tp06', 30.03); tilt('#tp06', 30.03, 0.6, 9, 5, 6, 4, 60, 0);
swap('#tp07', 30.56); tilt('#tp07', 30.56, 0.6, -8, -4, 6, 3, 80, 20);
blurOut('#tiltA', 31.12, .3);

// ---- 9. tree: skill editing x / knowledge workflow ----
tl.set('#camA', {{ x: 0, scale: 1.0 }}, 30.0);
tl.to('#camA', {{ x: -560, '--fe': '360px', duration: .55, ease: P3 }}, 31.22);
tl.fromTo('#tree', {{ opacity: 0, x: 80 }}, {{ opacity: 1, x: 0, duration: .45, ease: 'power3.out', immediateRender: false }}, 31.28);
popIn('#tRoot', 31.40);
['#trL', '#trR'].forEach(s => {{ const L = document.querySelector(s).getTotalLength();
  gsap.set(s, {{ strokeDasharray: L, strokeDashoffset: L }}); tl.to(s, {{ strokeDashoffset: 0, duration: .45, ease: 'power2.out' }}, 31.62); }});
popIn('#tSkill', {t('skill', -0.04)});
tl.fromTo('#tX', {{ opacity: 0, scale: 1.6 }}, {{ opacity: 1, scale: 1, duration: .25, ease: 'power3.out', immediateRender: false }}, {t('editing', 0.12)});
tl.to('#tSkill', {{ opacity: .35, duration: .3 }}, {t('editing', 0.2)});
popIn('#tKnow', {t('knowledge', -0.04)});
tl.to('#tKnow', {{ borderColor: '{YEL}', color: '{YEL}', boxShadow: '0 0 40px rgba(255,230,0,.45)', scale: 1.06, duration: .3, ease: 'power2.out' }}, {t('workflow', -0.02)});

// ---- 10. dashboard tilt, chapter card 3 (words on the beat) ----
tl.fromTo('#tiltB', {{ opacity: 0, scale: 1.1, filter: 'blur(16px)' }}, {{ opacity: 1, scale: 1, filter: 'blur(0px)', duration: .38, ease: 'power3.out', immediateRender: false }}, {t('sebab2', -0.04)});
tilt('#tp01', {t('sebab2', -0.04)}, 1.7, 10, 4, 7, 3, 140, -40);
tl.set('#tree', {{ opacity: 0 }}, 35.6);
tl.set('#camA', {{ x: 0, scale: 1.04, '--fe': '0px' }}, 35.6);
blurIn('#card3', 36.78, .3);
tl.set('#tiltB', {{ opacity: 0 }}, 37.1);
gsap.set(['#c3a', '#c3b', '#c3c', '#c3d'], {{ display: 'inline-block' }});
blurIn('#c3a', {t('edit', -0.05)}, .3, 16); blurIn('#c3b', {t('video', -0.03)}, .3, 16);
blurIn('#c3c', {t('guna', -0.03)}, .3, 16); blurIn('#c3d', {t('code', -0.03)}, .3, 16);

// ---- 11. module montage -> student results on "expert" ----
show('#mont', 38.22, .2);
tl.set('#card3', {{ opacity: 0 }}, 38.45);
gsap.set('#grid', {{ transformOrigin: '180px 101px' }});
tl.to('#grid', {{ scale: 1.0, duration: 1.45, ease: 'power3.inOut' }}, 38.4);
tl.to('#grid', {{ scale: 1.03, duration: 1.0, ease: S }}, 39.9);
for (let i = 1; i <= 17; i++) tl.fromTo(`#g${{i}}`, {{ opacity: 0, scale: .82 }}, {{ opacity: 1, scale: 1, duration: .22, ease: 'power2.out', immediateRender: false }}, 38.30 + (i - 1) * 0.055);
tl.fromTo('#g1 .ring', {{ opacity: 0 }}, {{ opacity: 1, duration: .2, immediateRender: false }}, {t('newbie', -0.03)});
tl.fromTo('#g17 .ring', {{ opacity: 0 }}, {{ opacity: 1, duration: .2, immediateRender: false }}, 40.15);
tl.to('#grid', {{ opacity: .28, filter: 'blur(10px)', duration: .35, ease: 'power2.out' }}, {t('expert', -0.12)});
show('#resL', {t('expert', -0.05)}, .25);
tl.fromTo('#rc1', {{ opacity: 0, y: 90 }}, {{ opacity: 1, y: 0, duration: .4, ease: 'power3.out', immediateRender: false }}, {t('expert', -0.1)});
tl.fromTo('#rc2', {{ opacity: 0, y: 90 }}, {{ opacity: 1, y: 0, duration: .4, ease: 'power3.out', immediateRender: false }}, {t('expert', -0.02)});
blurOut('#mont', 41.92, .3);

// ---- 12. Claude / ChatGPT, then tight push to the end ----
popIn('#pCl', {t('claude', -0.04)});
popIn('#pGp', {t('chat', -0.04)});
tl.to(['#pCl', '#pGp'], {{ opacity: 0, y: -16, duration: .25 }}, {t('nak', -0.2)});
tl.to('#camA', {{ scale: 1.15, duration: 1.75, ease: S }}, {t('nak', -0.1)});

// ---- 13. end card: blurred last frame, real logo, no CTA button ----
tl.set('#endc', {{ opacity: 1 }}, {END});
tl.fromTo('#endBg', {{ filter: 'blur(0px)', scale: 1.15 }}, {{ filter: 'blur(24px)', scale: 1.2, duration: .7, ease: 'power2.out', immediateRender: false }}, {END});
gsap.set('#endBg', {{ transformOrigin: '{FACE}' }});
popIn('#endLogo', {END + 0.15});
blurIn('#endT', {END + 0.35}, .45, 20);
tl.to('#endT', {{ scale: 1.03, duration: 2.0, ease: S }}, {END + 0.8});

window.__timelines['main'] = tl;
</script>
</body>
</html>
'''
open(os.path.join(ROOT, 'hf/index.html'), 'w').write(html)
print('wrote hf/index.html')
