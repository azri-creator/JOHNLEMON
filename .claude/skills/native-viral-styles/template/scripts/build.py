# Native Viral Styles — build script (reference: VGC "Control Zoom In/Out").
# Run from the project dir (the one containing scripts/ and hf/):  python3 scripts/build.py
# Per video, edit these blocks: END, SC (scene modules: name, start, duration, in_camera),
# PAIRS (kicker/headline captions, verbatim speech), KEY (big headlines: "B" behind head / "F" front),
# PROMPTS (Claude chip commands), CAM (camera keys), SHAKES (impact shakes).
# Needs hf/assets/src/main.mov, hf/assets/person.webm, hf/assets/fonts/anton-400.woff2, scripts/scenes/*.html.
# Builds the 9:16 composition: hf/compositions/*.html + hf/index.html
import json,re,os,sys
END=45.3
common=open('scripts/common.css').read()
def uniquify(name, html):
    ids=set(re.findall(r'(?<![\w-])id="([A-Za-z][\w-]*)"',html))-{'root'}
    for i in sorted(ids,key=len,reverse=True):
        new=f"{name}__{i}"
        html=re.sub(r'(?<![\w-])id="%s"'%re.escape(i), f'id="{new}"', html)
        html=re.sub(r'#%s(?![\w-])'%re.escape(i), '#'+new, html)
        html=re.sub(r'getElementById\("%s"\)'%re.escape(i), f'getElementById("{new}")', html)
    return html
def scope_css(name, html):
    def fix(m):
        css=re.sub(r'/\*.*?\*/','',m.group(2),flags=re.S)
        out=[]
        for sel,body in re.findall(r'([^{}]+)\{([^{}]*)\}',css):
            parts=[]
            for sp in sel.split(','):
                sp=sp.strip()
                sp=f'[data-composition-id="{name}"]'+sp[5:] if sp.startswith('#root') else f'[data-composition-id="{name}"] '+sp
                parts.append(sp)
            out.append(','.join(parts)+'{'+body+'}')
        return m.group(1)+'\n'.join(out)+m.group(3)
    return re.sub(r'(<style>)(.*?)(</style>)',fix,html,flags=re.S)
# name, start, dur, in_camera
SC=[("hud",3.8,3.6,0),("keyf",8.3,2.2,0),("clock",10.45,4.55,0),("power",15.0,3.84,1),("orbit",18.7,9.0,1),("super",27.5,1.65,1),("laptop",29.05,3.15,0),("slot",32.25,2.3,0),("motion",34.6,3.25,0),("alasan",37.7,4.92,1),("cta",42.6,2.7,0)]
os.makedirs('hf/compositions',exist_ok=True)
for n,a,d,c in SC:
    s=open(f'scripts/scenes/{n}.html').read().replace('/*COMMON*/',common)
    s=scope_css(n,uniquify(n,s))
    s=s.replace('<span class="ln"','<span data-layout-allow-occlusion data-layout-allow-overflow data-layout-allow-overlap class="ln"')
    open(f'hf/compositions/{n}.html','w').write(s)
def host(n,a,d,k): return f'        <div id="host-{n}" class="scene-host" data-composition-id="{n}" data-composition-src="compositions/{n}.html" data-start="{a}" data-duration="{d}" data-track-index="{k+3}" data-width="1080" data-height="1920"></div>'
cam_hosts="\n".join(host(n,a,d,k) for k,(n,a,d,c) in enumerate(SC) if c)
scr_hosts="\n".join(host(n,a,d,k) for k,(n,a,d,c) in enumerate(SC) if not c)
# ---------------- captions (verbatim speech; *key*) ----------------
PAIRS=[(0.00,0.94,2.22,"BILA KORANG DAH *ADAPT*","SKILL EDIT VIDEO"),(2.22,3.40,3.90,"DENGAN *AI* NI, KORANG","SELAMBA JE"),(3.90,4.10,4.76,"*BOLEH*","ZOOM VIDEO"),
(4.76,6.12,6.60,"MACAM NI, DAN BOLEH *MINTA*","ZOOM OUT"),(6.60,7.36,8.48,"VIDEO MACAM NI,","BILA-BILA MASA JE"),(8.48,9.94,10.45,"TANPA PERLU *SENTUH*","KEYFRAME"),
(10.54,11.48,11.84,"BAYANGKAN BERAPA *BANYAK*","MASA"),(11.84,12.32,12.60,"YANG *KITA* DAH","JIMAT"),(12.60,13.22,13.68,"HANYA *DENGAN*","AUTOMATE"),(13.68,14.52,14.95,"BENDA-BENDA *KECIL*","MACAM NI JE"),
(15.04,15.92,16.64,"DAN YANG PALING *BEST*,","AI LEVEL"),(16.64,17.46,18.30,"SEKARANG NI *DAH*","TERSANGAT-SANGAT"),(18.30,18.34,18.84,"","POWER"),
(18.84,19.18,19.46,"*TENGOK* NI,","CLAUDE"),(19.46,20.50,21.44,"TOLONG *LETAKKAN*","VIDEO-VIDEO SAYA"),(21.44,21.74,22.22,"*YANG*","TERBAIK"),(22.22,23.30,24.45,"DEKAT *SEKELILING* SAYA","SECARA 3D"),
(24.52,24.86,25.32,"SEKARANG *NI*","KUMPUL"),(25.32,26.02,26.44,"SEMUA VIDEO TU *DEKAT*","TANGAN SAYA"),(26.44,26.76,27.52,"*DAN*","HILANGKAN DIA"),(27.58,28.40,29.10,"DAH MACAM *ADA*","SUPER POWER"),
(29.10,29.72,30.18,"NAK *BELAJAR*","SKILL NI"),(30.18,30.84,31.22,"KORANG KENA *ADA*","LAPTOP"),(31.22,31.54,32.20,"*DAN*","INTERNET JE"),
(32.32,32.92,33.62,"LEPAS *TU*,","ANY CONTENT"),(33.62,34.00,34.60,"*BOLEH*","AUTOMATE"),(34.66,35.02,35.90,"KALAU TAK *ADA*","FOOTAGE SENDIRI PUN"),(35.90,36.78,37.78,"BOLEH BUAT *VIDEO*","MOTION MACAM NI"),
(37.78,39.20,39.64,"SO, KALAU TANYA SAYA, APA *LAGI*","ALASAN"),(39.64,40.30,41.12,"HARI NI *UNTUK*","TAK ADA CONTENT?"),(41.18,41.18,41.58,"","TAK ADA."),(41.58,42.22,42.60,"*MEMANG* TAK ADA","ALASAN"),
(42.64,43.64,44.42,"NAK BELAJAR *SKILL* NI,","ADAPT HARI NI"),(44.42,44.42,45.30,"","TEKAN LINK YANG ADA")]
KEY={2:"F",3:"F",5:"B",12:"B",16:"F",20:"B",25:"B",28:"B",30:"F",33:"B"}
GLITCH={"SUPER POWER"}
smallH=[];headB=[];headF=[];cap_js=[]
for n,(tk,th,te,k,h) in enumerate(PAIRS):
    kt=re.sub(r"[*](.+?)[*]",r"<b>\1</b>",k)
    nxt=PAIRS[n+1][0]-0.02 if n+1<len(PAIRS) else 1e9
    e=round(min(te+0.06,nxt-0.01,END),3)
    if n in KEY:
        fs=int(min(170 if KEY[n]=="F" else 158,980/(0.47*max(1,len(h)))))
        if k: smallH.append(f'      <div id="k{n}" class="kick">{kt}</div>')
        (headB if KEY[n]=="B" else headF).append(f'      <div id="h{n}" class="head{" hb" if KEY[n]=="B" else ""}" style="font-size:{fs}px" data-layout-allow-occlusion data-layout-allow-overlap>{h}</div>')
        cap_js.append(f'capK({n},{round(max(0,tk-0.03),3)},{round(max(0,th-0.03),3)},{e},{1 if k else 0},{1 if h in GLITCH else 0},{1 if KEY[n]=="B" else 0});')
    else:
        l1=f'<span class="l1">{kt}</span>' if k else ''
        smallH.append(f'      <div id="c{n}" class="cap2">{l1}<span class="l2">{h}</span></div>')
        cap_js.append(f'capS({n},{round(max(0,tk-0.03),3)},{e});')
# ---------------- Claude prompt chip ----------------
PROMPTS=[("pA","zoom in dekat muka",3.95,4.32,"1.6×",4.6,5.9),("pB","zoom out",5.95,6.12,"1.0×",6.62,7.3),
         ("pC","letak video terbaik sekeliling saya, 3D",19.3,23.9,"6 video",24.1,24.5),("pD","kumpul video dekat tangan & hilangkan",24.55,26.9,"selesai",27.36,27.8)]
CW=19.2
chip_lines="\n".join(f'        <div class="pl" id="{i}" style="opacity:0"><span class="pt" id="{i}t">{txt}</span></div>' for i,txt,*_ in PROMPTS)
chip_js=[]
for i,txt,a,b,st,ts,hide in PROMPTS:
    n=len(txt)
    chip_js.append(f'tl.set("#{i}",{{opacity:1}},{a-0.05});')
    chip_js.append(f'tl.fromTo("#{i}t",{{clipPath:"inset(0 100% 0 0)"}},{{clipPath:"inset(0 0% 0 0)",duration:{round(b-a,3)},ease:"steps({n})",immediateRender:false}},{a});')
    chip_js.append(f'tl.set("#cur",{{x:0}},{a-0.05});tl.to("#cur",{{x:{round(n*CW,1)},duration:{round(b-a,3)},ease:"steps({n})"}},{a});')
    chip_js.append(f'tl.set("#cstat",{{textContent:"✓ {st}"}},{ts-0.01});tl.fromTo("#cstat",{{opacity:0,scale:.6}},{{opacity:1,scale:1,duration:.25,ease:"expo.out",immediateRender:false}},{ts});')
    chip_js.append(f'tl.set(["#{i}","#cstat"],{{opacity:0}},{hide});')
# ---------------- camera ----------------
CAM=[(0.0,1.0,440,560,0,"none"),(0.0,1.06,440,560,3.9,"sine.inOut"),
     (4.10,1.6,440,520,0.46,"power3.inOut"),(4.56,1.66,440,520,1.5,"none"),(6.12,1.0,440,520,0.5,"expo.inOut"),
     (6.62,1.05,440,560,1.8,"sine.inOut"),(8.48,1.14,440,560,1.46,"power2.inOut"),(9.94,1.2,440,560,0.12,"power2.out"),(10.06,1.0,440,560,0.45,"expo.inOut"),
     (10.54,1.08,440,560,1.7,"sine.inOut"),(12.32,1.16,440,560,0.1,"power2.out"),(12.42,1.0,440,560,0.5,"expo.out"),
     (13.22,1.1,440,560,0.1,"power2.out"),(13.32,1.0,440,560,0.5,"expo.out"),
     (15.04,1.1,440,560,3.26,"sine.inOut"),(18.34,1.18,440,560,0.1,"power2.out"),(18.44,1.0,440,560,0.4,"expo.out"),
     (23.95,1.07,540,900,0.45,"expo.out"),(24.40,1.0,540,900,0.4,"power2.inOut"),(24.86,1.1,560,1000,1.1,"power2.inOut"),(26.6,1.0,560,1000,0.5,"expo.inOut"),
     (28.40,1.12,540,800,0.1,"power2.out"),(28.50,1.0,540,800,0.6,"expo.out"),
     (29.10,1.07,440,560,1.7,"sine.inOut"),(30.84,1.12,440,560,0.1,"power2.out"),(30.94,1.07,440,560,0.3,"expo.out"),(31.54,1.12,440,560,0.1,"power2.out"),(31.64,1.0,440,560,0.5,"expo.out"),
     (32.92,1.15,440,560,0.08,"power3.out"),(34.0,1.0,440,560,0.35,"expo.out"),(34.66,1.1,440,560,1.2,"sine.inOut"),(37.6,1.0,440,560,0,"none"),
     (37.78,1.15,440,560,3.3,"sine.inOut"),(41.18,1.0,440,560,0,"none"),(41.20,1.22,440,520,0.08,"power3.out"),(41.58,1.05,440,560,0.35,"expo.out"),
     (42.22,1.14,440,560,0.1,"power2.out"),(42.32,1.0,440,560,0.4,"expo.out"),(42.74,1.06,440,560,2.5,"sine.inOut")]
cam_js=[]
for t,S,px,py,d,e in CAM:
    if d==0: cam_js.append(f'tl.set("#cam, #camP",{{scale:{S},x:{round(px*(1-S),2)},y:{round(py*(1-S),2)}}},{t});')
    else: cam_js.append(f'tl.to("#cam, #camP",{{scale:{S},x:{round(px*(1-S),2)},y:{round(py*(1-S),2)},duration:{d},ease:"{e}"}},{t});')
import random
rnd=random.Random(3)
SHAKES=[(18.34,.36,18),(27.36,.32,15),(28.40,.3,13),(28.78,.25,10),(41.18,.3,15)]
for t,d,a in SHAKES:
    n=int(d/0.03)
    for k in range(n):
        f=(1-k/n)**1.5
        cam_js.append(f'tl.to("#shake, #shake2",{{x:{round((rnd.random()-.5)*2*a*f,1)},y:{round((rnd.random()-.5)*2*a*f,1)},duration:0.029,ease:"none"}},{round(t+k*0.03,3)});')
    cam_js.append(f'tl.to("#shake, #shake2",{{x:0,y:0,duration:0.05,ease:"none"}},{round(t+n*0.03,3)});')
audio_tags=open('scripts/audio_tags.html').read() if os.path.exists('scripts/audio_tags.html') else ''
html=f'''<!doctype html>
<html lang="ms">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      @font-face {{ font-family: "Anton"; src: url("assets/fonts/anton-400.woff2") format("woff2"); font-weight: 400; font-style: normal; }}
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: 1080px; height: 1920px; overflow: hidden; background: #06090D; }}
      #root {{ position: relative; width: 1080px; height: 1920px; overflow: hidden; font-family: Inter, sans-serif; color: #F5F7FA; background: #06090D; }}
      #shake, #cam, #shake2, #camP, #headsB, #headsF, #kicks, #pmatw {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; }}
      #cam, #camP {{ transform-origin: 0 0; }}
      #pmat {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; object-fit: cover; }}
      #headsB, #headsF, #kicks, #pmatw {{ pointer-events: none; }}
      .head.hb {{ top: 58px; }}
      .cap2 {{ position: absolute; left: 0; top: 116px; width: 1080px; text-align: center; font-family: Inter, sans-serif; font-weight: 900; text-transform: uppercase; color: #F5F7FA; opacity: 0; text-shadow: 0 2px 6px rgba(0,0,0,.6), 0 0 22px rgba(0,0,0,.35); }}
      .cap2 span {{ display: block; white-space: nowrap; }}
      .cap2 .l1 {{ font-size: 40px; line-height: 1.15; }}
      .cap2 .l2 {{ font-size: 52px; line-height: 1.12; }}
      .cap2 b {{ color: #FFE600; }}
      #base {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; object-fit: cover; }}
      .scene-host {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; }}
      #scrim {{ position: absolute; left: 0; top: 0; width: 1080px; height: 560px; pointer-events: none; background: linear-gradient(to bottom, rgba(6,9,13,0.5) 0%, rgba(6,9,13,0.28) 55%, rgba(6,9,13,0) 100%); }}
      #kicks {{ z-index: 40; }}
      .kick {{ position: absolute; left: 0; top: 116px; width: 1080px; text-align: center; font-family: Inter, sans-serif; font-weight: 900; font-size: 44px; letter-spacing: 0.01em; line-height: 1.1; color: #F5F7FA; opacity: 0; white-space: nowrap; text-shadow: 0 2px 6px rgba(0,0,0,.55), 0 0 22px rgba(0,0,0,.35); }}
      .kick b {{ color: #FFE600; font-weight: 900; }}
      .head {{ position: absolute; left: 0; top: 172px; width: 1080px; text-align: center; font-family: Anton, sans-serif; font-weight: 400; line-height: 1.0; letter-spacing: 0.005em; color: #FFFFFF; opacity: 0; white-space: nowrap; text-shadow: 0 6px 22px rgba(0,0,0,.35), 0 0 24px rgba(200,220,255,.3); }}
      #chip {{ position: absolute; left: 70px; top: 1400px; width: 940px; height: 150px; z-index: 35; opacity: 0; background: rgba(9,13,18,.72); -webkit-backdrop-filter: blur(24px) saturate(1.15); backdrop-filter: blur(24px) saturate(1.15); border: 1.5px solid rgba(255,255,255,.16); border-radius: 30px; box-shadow: 0 28px 70px rgba(0,0,0,.45), inset 0 1px 0 rgba(255,255,255,.10); }}
      #spark {{ position: absolute; left: 30px; top: 46px; width: 58px; height: 58px; }}
      #clab {{ position: absolute; left: 112px; top: 24px; font-weight: 700; font-size: 22px; letter-spacing: .14em; text-transform: uppercase; color: #9AA4B2; }}
      #cstat {{ position: absolute; right: 26px; top: 18px; height: 40px; padding: 0 18px; border-radius: 20px; background: #F5F7FA; color: #06090D; font-weight: 900; font-size: 24px; display: flex; align-items: center; opacity: 0; transform-origin: 100% 50%; }}
      .pl {{ position: absolute; left: 112px; top: 70px; height: 50px; }}
      .pt {{ display: inline-block; font-family: "JetBrains Mono", monospace; font-weight: 700; font-size: 32px; line-height: 50px; color: #F5F7FA; white-space: pre; }}
      #cur {{ position: absolute; left: 112px; top: 78px; width: 4px; height: 36px; background: #D97757; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{END}" data-width="1080" data-height="1920">
      <div id="shake">
        <div id="cam">
          <video id="base" src="assets/src/main.mov" data-start="0" data-duration="{END}" data-media-start="0" data-track-index="0" muted playsinline></video>
{cam_hosts}
        </div>
      </div>
      <div id="scrim" data-layout-ignore></div>
      <div id="headsB">
{chr(10).join(headB)}
      </div>
      <div id="pmatw"><div id="shake2"><div id="camP"><video id="pmat" src="assets/person.webm" data-start="0" data-duration="{END}" data-media-start="0" data-track-index="1" muted playsinline></video></div></div></div>
{scr_hosts}
      <div id="headsF">
{chr(10).join(headF)}
      </div>
      <div id="chip" data-layout-allow-overlap>
        <svg id="spark" viewBox="0 0 48 48"><g stroke="none"><path fill="#D97757" d="M24 3 L28 20 L45 24 L28 28 L24 45 L20 28 L3 24 L20 20 Z"/></g></svg>
        <div id="clab">Claude Code</div>
        <div id="cstat">✓</div>
{chip_lines}
        <div id="cur"></div>
      </div>
      <div id="kicks">
{chr(10).join(smallH)}
      </div>
      <audio id="voice" src="assets/src/main.mov" data-start="0" data-duration="{END}" data-media-start="0" data-track-index="30" data-volume="1"></audio>
{audio_tags}
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      const GL = "-6px 0 rgba(255,40,90,.7), 6px 0 rgba(40,220,255,.7), 0 6px 22px rgba(0,0,0,.35)";
      const NG = "0 6px 22px rgba(0,0,0,.35), 0 0 24px rgba(200,220,255,.3)";
      function capS(n, s, e) {{
        const el = "#c" + n;
        tl.fromTo(el, {{ opacity: 0, y: 10 }}, {{ opacity: 1, y: 0, duration: 0.12, ease: "power2.out" }}, s);
        tl.set(el, {{ opacity: 0 }}, e);
      }}
      function capK(n, tk, th, te, hasK, glitch, behind) {{
        const k = "#k" + n, h = "#h" + n;
        if (hasK) {{ tl.fromTo(k, {{ opacity: 0, y: 12 }}, {{ opacity: 1, y: 0, duration: 0.12, ease: "power2.out" }}, tk); tl.set(k, {{ opacity: 0 }}, behind ? th : te); }}
        tl.fromTo(h, {{ opacity: 0, y: 46 }}, {{ opacity: 1, y: 0, duration: 0.22, ease: "power3.out" }}, th);
        if (glitch) {{ [0.0,0.06,0.12].forEach((d,i) => tl.set(h, {{ textShadow: i%2 ? NG : GL }}, th + d)); tl.set(h, {{ textShadow: NG }}, th + 0.18); }}
        tl.set(h, {{ opacity: 0 }}, te);
      }}
      // person cutout layer is hidden during the 3D orbit (cards must pass in front)
      tl.set("#pmatw", {{ opacity: 0 }}, 18.68);
      tl.set("#pmatw", {{ opacity: 1 }}, 27.72);
      {chr(10).join('      '+j for j in cap_js)}
      // camera + shake + flashes
      {chr(10).join('      '+j for j in cam_js)}
      // Claude chip
      tl.fromTo("#chip", {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: .35, ease: "expo.out" }}, 3.72);
      tl.to("#chip", {{ opacity: 0, y: 20, duration: .25, ease: "power2.in" }}, 7.3);
      tl.fromTo("#chip", {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: .35, ease: "expo.out", immediateRender: false }}, 18.72);
      tl.to("#chip", {{ opacity: 0, y: 20, duration: .25, ease: "power2.in" }}, 27.8);
      tl.to("#cur", {{ opacity: .15, duration: .28, ease: "none", yoyo: true, repeat: 13 }}, 3.75);
      tl.to("#cur", {{ opacity: .15, duration: .28, ease: "none", yoyo: true, repeat: 31 }}, 18.75);
      {chr(10).join('      '+j for j in chip_js)}
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
'''
open('hf/index.html','w').write(html)
print("built",len(SC),"scenes",len(PAIRS),"captions,",len(KEY),"big headlines")
