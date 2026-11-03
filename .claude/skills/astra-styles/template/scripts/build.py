# ===== TEMPLATE NOTE (Astra Styles skill) =====
# This is the exact build of VGC "AI Edit Merapu" (45.3 s). It is a WORKED EXAMPLE, not a generic generator:
# - Config blocks to replace per video: CAM, WOB/CH (chaos beat, optional), TT, SCRIM_L/SCRIM_T, P1/P2/SUBS, CARDS/CARD_H/CA_FWD,
#   FB/FB_AR/RIM, TH/FAN, LY, UI.
# - The timeline list J (further down) has beat times hard-coded for the Merapu script: re-time or delete beats you do not use.
# - Needs hf/build/headtrack.json (scripts/headtrack.py) and the assets listed in references/pipeline.md section 1.
# ==============================================
# VGC "AI Edit Merapu" — Astra Style build, one script for both sizes.
# Run from the project dir (the one holding scripts/ and hf/):
#   FMT=16x9 python3 scripts/build.py   -> hf/index.html   (landscape, default)
#   FMT=9x16 python3 scripts/build.py   -> hf9/index.html  (portrait story; copy hf/assets into hf9 first)
# Astra DNA: one accent (magenta→red gradient) + white, two-tone type (white setup / magenta punch),
# blur-in / blur-out motion, 2D rack focus, floating perspective cards, dark stage UI scenes,
# hero word behind the head. Beat 2 is deliberately "merapu" (chaos) until "kejap kejap kejap".
import json, math, os, random, html as H_

FMT = os.environ.get('FMT', '16x9')
P = FMT == '9x16'
END = 45.3
W, H = (1080, 1920) if P else (1920, 1080)
OUT = 'hf9' if P else 'hf'
# footage geometry inside the frame (portrait: fill height, centre the presenter)
K = 1920 / 1080 if P else 1.0
BW, BH = round(1920 * K), round(1080 * K)
BL = round(540 - 1000 * K) if P else 0
HT = json.load(open('hf/build/headtrack.json'))

def face(t):
    w = [(cx, top) for tt, top, cx in HT if abs(tt - t) <= 0.6] or [(1000, 360)]
    cx = sum(c for c, _ in w) / len(w); cy = sum(tp for _, tp in w) / len(w) + 140
    return cx * K + BL, cy * K

def clamp(S, tx, ty):
    lo_x, hi_x = W - (BL + BW) * S, -BL * S
    return S, round(min(hi_x, max(lo_x, tx)), 1), round(min(0, max(H - BH * S, ty)), 1)

def C(t, S):            # zoom pivoting on the face
    px, py = face(t)
    return clamp(S, px * (1 - S), py * (1 - S))

def R(t, S=1.32):       # landscape: presenter to the right third (type on the left); portrait: face lower (type above)
    px, py = face(t)
    if P: return clamp(S * .94, px * (1 - S * .94), 1060 - py * S * .94)
    return clamp(S, 0, 430 - py * S)

# ---------------- camera keys: (time, (S,tx,ty), duration, ease) ----------------
CAM = [
    (0.0, C(0, 1.0), 0, ''), (0.05, C(2, 1.07), 4.0, 'sine.inOut'),
    (4.14, C(4.2, 1.16), .12, 'back.out(3)'), (4.5, C(4.6, 1.08), .3, 'power2.out'),
    (5.31, C(5.4, 1.22), .12, 'back.out(3)'), (5.7, C(5.8, 1.12), .25, 'power2.out'),
    (6.46, C(6.5, 1.26), .1, 'back.out(3)'), (6.82, C(6.9, 1.14), .2, 'power2.out'),
    (7.4, C(7.5, 1.3), .1, 'back.out(3)'), (7.86, C(7.9, 1.18), .15, 'power2.out'), (8.05, C(8.1, 1.34), .1, 'back.out(3)'),
    (8.42, C(8.5, 1.0), 0, ''), (9.12, R(9.6), 0, ''), (9.14, R(10, 1.36), 2.9, 'sine.inOut'),
    (12.1, C(12.5, 1.0), 0, ''), (12.15, C(13, 1.04), 2.3, 'sine.inOut'),
    (18.1, R(18.6), 0, ''), (18.15, R(19.5, 1.35), 3.2, 'sine.inOut'),
    (21.46, C(22, 1.02), 0, ''), (21.5, C(23, 1.06), 2.85, 'sine.inOut'),
    (24.44, C(24.6, 1.32), .22, 'expo.out'), (24.8, C(25, 1.0), .35, 'expo.inOut'),
    (25.3, R(25.8), 0, ''), (25.35, R(26.5, 1.36), 2.2, 'sine.inOut'),
    (27.66, C(28, 1.0), 0, ''), (27.7, C(31, 1.04), 9.4, 'sine.inOut'),
    (40.14, R(40.6), 0, ''), (40.18, R(41.5, 1.36), 2.2, 'sine.inOut'),
    (42.46, C(43, 1.0), 0, ''), (42.5, C(44, 1.07), 2.8, 'sine.inOut'),
]
for (t0, _, d0, _), (t1, *_) in zip(CAM, CAM[1:]):
    assert t0 + d0 <= t1 + 1e-6, (t0, t1)

rnd = random.Random(7)
WOB = []
t = 4.14
while t < 8.3:
    WOB.append((round(t, 3), round(rnd.uniform(-1.6, 1.6), 2), round(rnd.uniform(-10, 10), 1), round(rnd.uniform(-8, 8), 1)))
    t += rnd.uniform(.11, .2)
WOB.append((8.42, 0, 0, 0))

# ---------------- chaos stickers (beat 2) — positions per format ----------------
CH = [  # (time, text, (x,y) 16:9, (x,y) 9:16, size, color, rot, kind)
    (4.14, 'PENING KEPALA!!', (110, 120), (40, 230), 96, '#FFE600', -9, 'txt'),
    (4.47, '😵‍💫', (1450, 120), (820, 420), 170, '', 12, 'emo'),
    (5.31, 'BANYAK SANGAT', (1080, 760), (120, 1380), 92, '#00E5FF', 6, 'txt'),
    (5.64, '💥', (260, 560), (40, 900), 190, '', -14, 'emo'),
    (5.97, 'EFEK!!!', (140, 820), (520, 1560), 130, '#A6FF00', -6, 'txt'),
    (6.46, 'KELUAR 🔥', (1290, 330), (560, 1120), 100, '#FF8A00', 10, 'txt'),
    (6.82, 'ANIMATION', (520, 40), (90, 90), 140, 'rainbow', -4, 'txt'),
    (7.1, '⭐', (90, 380), (60, 520), 150, '', 0, 'emo'),
    (7.4, 'WOW!!', (1500, 600), (700, 760), 120, '#FF2BD6', -12, 'txt'),
    (7.55, '👉', (380, 330), (70, 1180), 160, '', 8, 'emo'),
    (7.7, 'SUBSCRIBE 🔔', (760, 900), (300, 1740), 70, 'btn', 0, 'txt'),
    (7.86, '🤯', (1640, 860), (860, 1500), 150, '', -10, 'emo'),
    (8.05, 'KELUAR!!!', (560, 470), (150, 880), 150, '#FFE600', 5, 'txt'),
]
CH_SZ = .78 if P else 1.0

# ---------------- two-tone type blocks (Astra signature) ----------------
# (id, start_l1, start_l2, end, l1, l2, (x, y, size, align) 16:9, (y, size) 9:16 centred)
TT = [
    ('t1', 9.14, 10.32, 12.0, 'SALAH AI?', 'ATAU AWAK?', (150, 330, 128, 'l'), (330, 124)),
    ('t2', 18.65, 20.45, 21.4, 'EDITING SIMPLE', 'NAMPAK NATIVE', (150, 340, 112, 'l'), (330, 112)),
    ('t3', 25.3, 26.24, 27.6, 'JANGAN SALAHKAN', 'AI.', (150, 330, 118, 'l'), (330, 110)),
    ('t4', 32.0, 33.56, 34.4, 'HASIL', 'POWERFUL', (150, 360, 128, 'l'), (1330, 128)),
    ('t5', 40.4, 41.48, 42.42, 'FOKUS PADA', 'KUALITI KONTEN', (150, 340, 112, 'l'), (330, 112)),
    ('t6', 42.84, 43.73, END + 1, 'RIGHT MESSAGE', 'RIGHT EDITING', (0, 70, 104, 'c'), (300, 108)),
]
SCRIM_L = [] if P else [(9.05, 12.05), (18.55, 21.42), (25.25, 27.62), (31.7, 37.25), (40.3, 42.45)]
SCRIM_T = [(9.05, 12.05), (12.05, 14.4), (18.55, 21.42), (25.25, 27.62), (40.3, 42.45), (42.7, END + 1)] if P else [(12.05, 14.4), (42.7, END + 1)]
SCRIM_T = sorted(SCRIM_T)

# ---------------- prompt typing ----------------
P1 = 'Buat editing heavy, masuk segala tulisan & efek'
P1_T = (14.62, 17.2); P1_SEND = 17.9
P2 = 'Buat simple subtitle je'
P2_T = (21.6, 23.3); P2_SEND = 23.45
def chars(txt, cls):
    return ''.join(f'<span class="{cls}" style="display:none">{H_.escape(c) if c != " " else "&nbsp;"}</span>' for c in txt)
SUBS = [(23.62, 24.42, 'Habis kot, ada'), (24.44, 24.78, 'zoom in'), (24.8, 25.28, 'zoom out')]

# ---------------- result cards (beat 8) ----------------
# id, src, layer, x, y, w, rotY, rotZ, enter, enter dx
CARDS = ([('ca', 'res1', 'front', 20, 330, 250, 20, -2, 28.09, -200),
          ('cb', 'res2', 'back', 285, 390, 235, 10, 1, 28.79, -160),
          ('cc', 'res3', 'back', 560, 390, 235, -10, -1, 29.78, 160),
          ('cd', 'res4', 'front', 810, 330, 250, -20, 2, 30.68, 200)] if P else
         [('ca', 'res1', 'front', 70, 250, 300, 24, -2, 28.09, -260),
          ('cb', 'res2', 'back', 400, 300, 290, 16, 1, 28.79, -220),
          ('cc', 'res3', 'back', 1230, 300, 290, -16, -1, 29.78, 220),
          ('cd', 'res4', 'front', 1550, 250, 300, -24, 2, 30.68, 260)])
CARD_H = {'res1': 772, 'res2': 870, 'res3': 870, 'res4': 846}
CA_FWD = (170, -40, 2.8, 2.66) if P else (950, -100, 1.733, 1.63)   # x, y, scale, recede scale
# ---------------- feedback screenshots (beat 8b) ----------------
FB = ({'lab': (90, 300), 'fb1': (190, 370, 700), 'fb2': (40, 1010, 1000)} if P else
      {'lab': (150, 150), 'fb1': (150, 205, 640), 'fb2': (430, 790, 1010)})
FB_AR = {'fb1': 570 / 656, 'fb2': 254 / 1256}
RIM = {'fb1': (13.4, 39.3, 58.5, 31.2), 'fb2': (8.9, 9.4, 89.8, 45.7)}   # % box of the highlighted bubble

# ---------------- module thumbnails (beat 9) ----------------
TH = (240, 680, 600, 338) if P else (600, 200, 720, 405)
FAN_DX = 225 if P else 340
FAN = [('fl', 'R07', -FAN_DX, -9, 14), ('fr', 'R16', FAN_DX, 9, -14), ('fc', 'Aku_Arah_Ai_Edit', 0, 0, 0)]

# ---------------- other per-format layout ----------------
LY = dict(
    cmt=(90, 250, 900) if P else (120, 300, 560),
    burst=(190, 550) if P else (610, 190),
    hero=(400, 300) if P else (135, 360),          # top, font-size
    kick1=320 if P else 92,
    bar=(60, 820, 1500, 230) if P else (230, 420, 1460, 210),
    slab1=640 if P else 250,
    pill=(90, 1500, 900) if P else (510, 880, 900),
    cta=(140, 1560, 800) if P else (560, 880, 800),
    nsub=1480 if P else 860,
    rlab=230 if P else 120,
    slab2=470 if P else 92,
    t7=1130 if P else 700,
    spark=[(150, 1540), (900, 1530), (210, 1670), (850, 1680), (540, 1525)] if P else [(530, 860), (1400, 850), (600, 990), (1340, 1000), (960, 845)],
)
# virtual camera on the prompt bar: keys (time, scale, x, y, duration, ease)
bx, by, bw, bh = LY['bar']
SEND = (bx + bw - 38 - 35, by + bh // 2 + 38)
if P:
    UI = [(14.7, 1.15, -40, -150, .9, 'expo.inOut'), (15.6, 1.15, -470, -150, 1.6, 'sine.inOut'),
          (17.25, 1.3, round(700 - SEND[0] * 1.3), round(1000 - SEND[1] * 1.3), .7, 'expo.inOut')]
else:
    UI = [(14.7, 1.32, -60, -230, .9, 'expo.inOut'), (15.6, 1.32, -560, -230, 1.6, 'sine.inOut'),
          (17.25, 1.5, -1300, -470, .7, 'expo.inOut')]

GRAD = 'linear-gradient(92deg,#FF3FA4 0%,#FF2D6F 45%,#FF2448 75%,#FF5A3A 100%)'

# ================= HTML =================
o = []
A = o.append
cx_, cy_, cw_ = LY['cmt']
A(f'''<!doctype html>
<html lang="ms">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      @font-face {{ font-family: "Archivo"; src: url("assets/fonts/archivo-latin-wdth-normal.woff2") format("woff2"); font-weight: 100 900; font-stretch: 62% 125%; }}
      @font-face {{ font-family: "Outfit"; src: url("assets/fonts/outfit-latin-wght-normal.woff2") format("woff2"); font-weight: 100 900; }}
      @font-face {{ font-family: "Apple Color Emoji"; src: local("Apple Color Emoji"); }}
      @font-face {{ font-family: "InterV"; src: url("assets/fonts/inter-latin-wght-normal.woff2") format("woff2"); font-weight: 100 900; }}
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: {W}px; height: {H}px; overflow: hidden; background: #050304; }}
      #root {{ position: relative; width: 100%; height: 100%; overflow: hidden; background: #050304; font-family: InterV, sans-serif; color: #F6F4F5; }}
      .full {{ position: absolute; left: 0; top: 0; width: {W}px; height: {H}px; }}
      #cam, #camP {{ transform-origin: 0 0; }}
      #wob, #wob2 {{ transform-origin: 50% 50%; }}
      #base, #pmat {{ position: absolute; left: {BL}px; top: 0; width: {BW}px; height: {BH}px; object-fit: fill; }}
      #pmatw {{ opacity: 0; }}
      .scrimL {{ background: linear-gradient(90deg, rgba(10,5,8,.72) 0%, rgba(10,5,8,.5) 28%, rgba(10,5,8,0) 58%); opacity: 0; }}
      .scrimT {{ background: linear-gradient(180deg, rgba(10,5,8,.66) 0%, rgba(10,5,8,.34) {22 if P else 26}%, rgba(10,5,8,0) {38 if P else 46}%); opacity: 0; }}
      .tt {{ position: absolute; font-family: Archivo, sans-serif; font-weight: 820; font-stretch: 86%; text-transform: uppercase; line-height: .98; letter-spacing: -.005em; white-space: nowrap; }}
      .tt.c {{ left: 0; width: {W}px; text-align: center; }}
      .tt span {{ display: block; opacity: 0; }}
      .l1 {{ color: #F6F4F5; text-shadow: 0 4px 24px rgba(0,0,0,.35); }}
      .l2, .grad {{ background: {GRAD}; -webkit-background-clip: text; background-clip: text; color: transparent; }}
      .l2 {{ padding-bottom: .06em; filter: drop-shadow(0 4px 18px rgba(0,0,0,.3)); }}
      .ch {{ position: absolute; opacity: 0; white-space: nowrap; font-family: Archivo, sans-serif; font-weight: 900; font-stretch: 112%; -webkit-text-stroke: 5px #111; paint-order: stroke fill; text-shadow: 7px 7px 0 #111; }}
      .ch.emo {{ -webkit-text-stroke: 0; text-shadow: 0 10px 20px rgba(0,0,0,.35); font-family: "Apple Color Emoji", sans-serif; font-weight: 400; }}
      .ch.rainbow {{ background: linear-gradient(90deg,#ff004c,#ffb800,#3dff00,#00d0ff,#a100ff); -webkit-background-clip: text; background-clip: text; color: transparent; -webkit-text-stroke: 0; text-shadow: none; filter: drop-shadow(6px 6px 0 #111); }}
      .ch.btn {{ background: #FF0033; color: #fff; padding: 14px 34px; border-radius: 14px; -webkit-text-stroke: 0; text-shadow: none; box-shadow: 6px 6px 0 #111; }}
      #burst {{ position: absolute; left: {LY["burst"][0]}px; top: {LY["burst"][1]}px; width: 700px; height: 700px; opacity: 0; }}
      #cmt {{ position: absolute; left: {cx_}px; top: {cy_}px; width: {cw_}px; padding: 30px 34px 32px; border-radius: 30px; background: rgba(255,255,255,.96); color: #141214; box-shadow: 0 40px 80px rgba(20,8,14,.35), 0 0 0 1px rgba(255,255,255,.6); opacity: 0; }}
      #cmt .hd {{ display: flex; align-items: center; gap: 16px; margin-bottom: 18px; }}
      #cmt .av {{ width: 58px; height: 58px; border-radius: 50%; background: linear-gradient(135deg,#c9c3c8,#8e868c); }}
      #cmt .nm {{ font-weight: 700; font-size: 26px; }}
      #cmt .sb {{ font-size: 21px; color: #797377; font-weight: 500; }}
      #cmt .tx {{ font-size: {46 if P else 38}px; line-height: 1.22; font-weight: 600; letter-spacing: -.01em; }}
      #cmt .hl {{ position: relative; display: inline-block; }}
      #cmt .hl i {{ font-style: normal; position: relative; z-index: 1; }}
      #cmt .hl b {{ position: absolute; left: -4px; right: -4px; bottom: 2px; height: 16px; border-radius: 4px; background: {GRAD}; opacity: .85; transform-origin: 0 50%; }}
      #hero {{ position: absolute; left: 0; top: {LY["hero"][0]}px; width: {W}px; text-align: center; font-family: Outfit, sans-serif; font-weight: 700; font-size: {LY["hero"][1]}px; line-height: 1; letter-spacing: -.035em; white-space: nowrap; }}
      #hero span {{ display: inline-block; opacity: 0; background: linear-gradient(92deg,#FF3FA4 0%,#FF2D6F 40%,#FF2448 60%,#FF2D6F 80%,#FF3FA4 100%); background-size: 300% 100%; background-position: 0% 0; -webkit-background-clip: text; background-clip: text; color: transparent; }}
      #kick1 {{ position: absolute; left: 0; top: {LY["kick1"]}px; width: {W}px; text-align: center; font-family: Archivo, sans-serif; font-weight: 700; font-stretch: 100%; font-size: 36px; letter-spacing: .22em; color: #F6F4F5; opacity: 0; text-transform: uppercase; }}
      #stage {{ opacity: 0; background: #050304; overflow: hidden; }}
      #stage .vg {{ position: absolute; inset: 0; background: radial-gradient(120% 90% at 50% 50%, rgba(5,3,4,0) 45%, rgba(92,8,36,.55) 100%), radial-gradient(50% 60% at 0% 100%, rgba(120,10,44,.35), rgba(0,0,0,0) 70%), radial-gradient(50% 60% at 100% 0%, rgba(120,10,44,.28), rgba(0,0,0,0) 70%); }}
      .lab {{ position: absolute; font-family: Archivo, sans-serif; font-weight: 800; font-stretch: 90%; text-transform: uppercase; letter-spacing: .02em; opacity: 0; white-space: nowrap; }}
      #ui {{ position: absolute; left: 0; top: 0; width: {W}px; height: {H}px; transform-origin: 0 0; }}
      #bar {{ position: absolute; left: {bx}px; top: {by}px; width: {bw}px; height: {bh}px; border-radius: 40px; background: #1A191C; border: 1.5px solid rgba(255,255,255,.08); box-shadow: 0 40px 90px rgba(0,0,0,.55); opacity: 0; }}
      #bar .tx {{ position: absolute; left: 52px; top: 40px; font-size: 46px; font-weight: 450; color: #F2F0F2; white-space: nowrap; letter-spacing: -.005em; }}
      .caret {{ display: inline-block; width: 3px; height: 50px; background: #FF3D8E; vertical-align: -8px; margin-left: 3px; }}
      #bar .plus {{ position: absolute; left: 48px; bottom: 32px; font-size: 48px; font-weight: 300; color: #BDB8BC; line-height: 1; }}
      #bar .mdl {{ position: absolute; right: 150px; bottom: 40px; font-size: 30px; color: #BDB8BC; font-weight: 500; }}
      #send {{ position: absolute; right: 38px; bottom: 22px; width: 70px; height: 70px; border-radius: 50%; background: #F2F0F2; }}
      #send svg {{ position: absolute; left: 17px; top: 16px; width: 36px; height: 38px; }}
      #cur {{ position: absolute; left: 0; top: 0; width: 40px; height: 52px; opacity: 0; }}
      .glass {{ position: absolute; border-radius: 999px; background: rgba(28,22,26,.42); -webkit-backdrop-filter: blur(26px) saturate(1.2); backdrop-filter: blur(26px) saturate(1.2); border: 1.5px solid rgba(255,90,160,.55); box-shadow: 0 0 0 1px rgba(255,255,255,.06) inset, 0 24px 60px rgba(20,4,12,.35), 0 0 34px rgba(255,45,120,.18); opacity: 0; white-space: nowrap; }}
      #pill {{ left: {LY["pill"][0]}px; top: {LY["pill"][1]}px; width: {LY["pill"][2]}px; height: 104px; }}
      #pill .tx {{ position: absolute; left: 92px; top: 26px; font-size: 40px; font-weight: 500; color: #F6F4F5; }}
      #pill .spk, #cta .spk {{ position: absolute; width: 36px; height: 36px; }}
      #pill .spk {{ left: 36px; top: 34px; }}
      #pill .snd {{ position: absolute; right: 18px; top: 17px; width: 70px; height: 70px; border-radius: 50%; background: {GRAD}; }}
      #pill .snd svg {{ position: absolute; left: 17px; top: 16px; width: 36px; height: 38px; }}
      #cta {{ left: {LY["cta"][0]}px; top: {LY["cta"][1]}px; width: {LY["cta"][2]}px; height: 110px; }}
      #cta .tx {{ position: absolute; left: 0; top: 0; width: {LY["cta"][2]}px; height: 110px; display: flex; align-items: center; justify-content: center; gap: 22px; font-family: Archivo, sans-serif; font-weight: 800; font-stretch: 92%; font-size: 44px; letter-spacing: .06em; color: #F6F4F5; }}
      .sp {{ position: absolute; width: 30px; height: 30px; opacity: 0; }}
      .nsub {{ position: absolute; left: 0; top: {LY["nsub"]}px; width: {W}px; text-align: center; font-family: InterV, sans-serif; font-weight: 700; font-size: {60 if P else 54}px; color: #fff; opacity: 0; text-shadow: 0 2px 4px rgba(0,0,0,.65), 0 0 18px rgba(0,0,0,.35); }}
      .card {{ position: absolute; border-radius: 26px; overflow: hidden; opacity: 0; background: #0d0b0c; box-shadow: 0 40px 80px rgba(10,4,8,.45), 0 0 0 1px rgba(255,255,255,.14); }}
      #ca {{ transform-origin: 0 0; }}
      .card video {{ position: absolute; left: 0; top: 0; width: 100%; height: 100%; object-fit: cover; }}
      .fb {{ position: absolute; border-radius: 26px; overflow: hidden; opacity: 0; background: #fff; box-shadow: 0 40px 90px rgba(10,4,8,.5), 0 0 0 1px rgba(255,255,255,.4); }}
      .fb img {{ display: block; width: 100%; height: 100%; }}
      .rim {{ position: absolute; border-radius: 30px; border: 4px solid #FF3D8E; box-shadow: 0 0 22px rgba(255,45,120,.55), inset 0 0 14px rgba(255,45,120,.25); opacity: 0; }}
      .th {{ position: absolute; left: {TH[0]}px; top: {TH[1]}px; width: {TH[2]}px; height: {TH[3]}px; border-radius: 24px; overflow: hidden; opacity: 0; box-shadow: 0 50px 90px rgba(0,0,0,.6), 0 0 0 1px rgba(255,255,255,.12); }}
      .th img {{ width: 100%; height: 100%; display: block; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{END}" data-width="{W}" data-height="{H}">
      <div id="foot" class="full">
        <div id="wob" class="full"><div id="cam" class="full">
          <video id="base" src="assets/src/main.mov" data-start="0" data-duration="{END}" data-media-start="0" data-track-index="0" muted playsinline></video>
        </div></div>
      </div>
      <div id="scrL" class="full scrimL" data-layout-ignore></div>
      <div id="scrT" class="full scrimT" data-layout-ignore></div>
      <div id="headsB" class="full">
        <div id="kick1" data-layout-allow-overlap>Konsep AI edit video</div>
        <div id="hero" data-layout-allow-occlusion data-layout-allow-overlap>{"".join(f"<span>{c}</span>" for c in "senang")}</div>
      </div>
      <div id="backCards" class="full">''')

CARDS_START = {c[0]: c[8] - .15 for c in CARDS}
TRK = {'ca': 3, 'cb': 4, 'cc': 5, 'cd': 6}
def card(cid, src, x, y, w):
    h = round(w * CARD_H[src] / 578); st = round(CARDS_START[cid], 3)
    return (f'        <div id="{cid}" class="card" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px" data-layout-allow-occlusion data-layout-allow-overlap>'
            f'<video id="{cid}v" src="assets/res/{src}.mp4" data-start="{st}" data-duration="{round(37.4 - st, 3)}" data-media-start="0.5" data-track-index="{TRK[cid]}" muted playsinline></video></div>')
for c in CARDS:
    if c[2] == 'back': A(card(c[0], c[1], c[3], c[4], c[5]))
A(f'''      </div>
      <div id="pmatw" class="full"><div id="wob2" class="full"><div id="camP" class="full">
        <video id="pmat" src="assets/person.webm" data-start="0" data-duration="{END}" data-media-start="0" data-track-index="1" muted playsinline></video>
      </div></div></div>
      <div id="front" class="full">''')
for c in CARDS:
    if c[2] == 'front': A(card(c[0], c[1], c[3], c[4], c[5]))
A('''        <div id="cmt" data-layout-allow-overlap>
          <div class="hd"><div class="av"></div><div><div class="nm">Netizen</div><div class="sb">komen pada video anda</div></div></div>
          <div class="tx">"Video AI edit ni <span class="hl"><b></b><i>merapu</i></span> sangat lah"</div>
        </div>''')
A('        <div id="chaos" class="full">')
A('          <svg id="burst" viewBox="-100 -100 200 200" data-layout-ignore><g fill="#FFE600" stroke="#111" stroke-width="3"><polygon points="' +
  ' '.join(f"{round((95 if i % 2 == 0 else 55) * math.cos(i * math.pi / 12), 1)},{round((95 if i % 2 == 0 else 55) * math.sin(i * math.pi / 12), 1)}" for i in range(24)) + '"/></g></svg>')
for i, (t0, txt, p16, p9, sz, col, rot, kind) in enumerate(CH):
    x, y = p9 if P else p16
    cls = 'ch' + (' emo' if kind == 'emo' else '') + (' rainbow' if col == 'rainbow' else '') + (' btn' if col == 'btn' else '')
    style = f'left:{x}px;top:{y}px;font-size:{round(sz * CH_SZ)}px;' + (f'color:{col};' if col.startswith('#') else '')
    A(f'          <div id="ch{i}" class="{cls}" style="{style}" data-layout-allow-occlusion data-layout-allow-overlap data-layout-ignore>{txt}</div>')
A('        </div>')
for tid, a, b, e, l1, l2, g16, g9 in TT:
    if P: pos, al = f'top:{g9[0]}px;font-size:{g9[1]}px;', 'c'
    else:
        x, y, sz, al = g16
        pos = f'top:{y}px;font-size:{sz}px;' + ('' if al == 'c' else f'left:{x}px;')
    A(f'        <div id="{tid}" class="tt{" c" if al == "c" else ""}" style="{pos}" data-layout-allow-overlap><span class="l1" data-layout-allow-overlap>{l1}</span><span class="l2" data-layout-allow-overlap>{l2}</span></div>')
SPARK = '<svg viewBox="0 0 40 40"><path d="M20 2 L23.5 16.5 L38 20 L23.5 23.5 L20 38 L16.5 23.5 L2 20 L16.5 16.5 Z" fill="#FF4FA0"/></svg>'
ARROW = '<svg viewBox="0 0 36 38"><path d="M18 34V5M5 17L18 4l13 13" fill="none" stroke="#111" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/></svg>'
ARROWW = ARROW.replace('#111', '#fff')
A(f'''        <div id="pill" class="glass" data-layout-allow-overlap><div class="spk">{SPARK}</div><div class="tx">{chars(P2, "c2")}<span class="caret" id="caret2"></span></div><div class="snd" id="snd2">{ARROWW}</div></div>''')
for i, (a, b, txt) in enumerate(SUBS):
    A(f'        <div id="ns{i}" class="nsub" data-layout-allow-overlap>{txt}</div>')
A(f'        <div id="nlab" class="lab grad" style="left:{FB["lab"][0]}px;top:{FB["lab"][1]}px;font-size:34px;letter-spacing:.12em" data-layout-allow-overlap>Feedback student</div>')
for k in ('fb1', 'fb2'):
    x, y, w = FB[k]; h = round(w * FB_AR[k]); rl, rt, rw, rh = RIM[k]
    A(f'        <div id="{k}" class="fb" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px" data-layout-allow-overlap><img src="assets/fb/{k}.png" alt="">'
      f'<div id="{k}r" class="rim" style="left:{rl}%;top:{rt}%;width:{rw}%;height:{rh}%" data-layout-ignore></div></div>')
A(f'        <div id="rlab" class="lab" style="left:0;width:{W}px;text-align:center;top:{LY["rlab"]}px;font-size:34px;letter-spacing:.2em;color:#F6F4F5" data-layout-allow-overlap>Hasil student</div>')
A(f'''        <div id="cta" class="glass" data-layout-allow-overlap><div class="tx"><span class="spk" style="position:relative;display:inline-block">{SPARK}</span>TEKAN LINK DI BAWAH</div></div>''')
for i, (x, y) in enumerate(LY['spark']):
    A(f'        <div id="sp{i}" class="sp" style="left:{x}px;top:{y}px" data-layout-ignore>{SPARK}</div>')
A('      </div>')
A(f'''      <div id="stage" class="full">
        <div class="vg"></div>
        <div id="slab1" class="lab" style="left:0;width:{W}px;text-align:center;top:{LY["slab1"]}px;font-size:38px;letter-spacing:.16em;color:#F6F4F5" data-layout-allow-overlap>Nak editing <span class="grad">heavy?</span></div>
        <div id="ui">
          <div id="bar"><div class="tx">{chars(P1, "c1")}<span class="caret" id="caret1"></span></div><div class="plus">+</div><div class="mdl">Claude ▾</div><div id="send">{ARROW}</div></div>
          <svg id="cur" viewBox="0 0 40 52" data-layout-ignore><path d="M4 3 L4 42 L14 32 L21 48 L28 45 L21 29 L35 29 Z" fill="#fff" stroke="#111" stroke-width="3" stroke-linejoin="round"/></svg>
        </div>
        <div id="slab2" class="lab" style="left:0;width:{W}px;text-align:center;top:{LY["slab2"]}px;font-size:34px;letter-spacing:.2em;color:#F6F4F5" data-layout-allow-overlap>17 modul panduan</div>''')
for fid, img, dx, rz, ry in FAN:
    A(f'        <div id="{fid}" class="th" data-layout-allow-occlusion data-layout-allow-overlap><img src="assets/thumb/{img}.jpg" alt=""></div>')
A(f'''        <div id="t7" class="tt c" style="top:{LY["t7"]}px;font-size:104px" data-layout-allow-overlap><span class="l1" data-layout-allow-overlap>AUTOMATKAN</span><span class="l2" data-layout-allow-overlap>EDITING</span></div>
      </div>
      <audio id="voice" src="assets/audio/voice.wav" data-start="0" data-duration="{END}" data-media-start="0" data-track-index="20" data-volume="1"></audio>
      <audio id="music" src="assets/audio/music.wav" data-start="0" data-duration="{END}" data-media-start="0" data-track-index="21" data-volume="1"></audio>
      <audio id="sfx" src="assets/audio/sfx.wav" data-start="0" data-duration="{END}" data-media-start="0" data-track-index="22" data-volume="1"></audio>
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      const B0 = "blur(0px)", BL = (p) => "blur(" + p + "px)";
      function bin(el, t, o) {{ o = o || {{}}; tl.fromTo(el, {{ opacity: 0, filter: BL(o.b || 18), x: o.x || 0, y: o.y || 0, scale: o.s || .96 }}, {{ opacity: 1, filter: B0, x: 0, y: 0, scale: 1, duration: o.d || .5, ease: "expo.out", immediateRender: false }}, t); }}
      function bout(el, t, o) {{ o = o || {{}}; tl.to(el, {{ opacity: 0, filter: BL(o.b || 16), scale: o.s || 1.02, duration: o.d || .3, ease: "power2.in" }}, t); }}
''')
J = []
for t0, (S, tx, ty), d, e in CAM:
    if d == 0: J.append(f'tl.set("#cam, #camP", {{scale:{S},x:{tx},y:{ty}}}, {t0});')
    else: J.append(f'tl.to("#cam, #camP", {{scale:{S},x:{tx},y:{ty},duration:{d},ease:"{e}"}}, {t0});')
for t0, r, x, y in WOB:
    if t0 < 8.42: J.append(f'tl.to("#wob, #wob2", {{rotation:{r},x:{x},y:{y},duration:.1,ease:"power2.out"}}, {t0});')
    else: J.append(f'tl.set("#wob, #wob2", {{rotation:0,x:0,y:0}}, {t0});')
for a, b in [(12.0, 14.5), (27.6, 37.3)]:
    J.append(f'tl.set("#pmatw", {{opacity:1}}, {a}); tl.set("#pmatw", {{opacity:0}}, {b});')
def scrim(sel, spans):
    # merge touching spans so the scrim does not dip between back-to-back beats
    m = []
    for a, b in spans:
        if m and a <= m[-1][1] + .05: m[-1][1] = max(m[-1][1], b)
        else: m.append([a, b])
    for a, b in m:
        J.append(f'tl.fromTo("{sel}", {{opacity:0}}, {{opacity:1,duration:.35,ease:"power2.out",immediateRender:false}}, {a});' +
                 (f' tl.to("{sel}", {{opacity:0,duration:.3,ease:"power2.in"}}, {round(b - .3, 3)});' if b < END else ''))
scrim('#scrL', SCRIM_L); scrim('#scrT', SCRIM_T)
J += ['bin("#cmt", .18, {x:-60, b:22, d:.6});',
      f'tl.fromTo("#cmt", {{rotationY:{10 if P else 16}, transformPerspective:1400}}, {{rotationY:{6 if P else 10}, duration:3.8, ease:"sine.inOut", immediateRender:false}}, .18);',
      'tl.fromTo("#cmt .hl b", {scaleX:0}, {scaleX:1, duration:.35, ease:"expo.out"}, 3.0);',
      'bout("#cmt", 3.85, {d:.28});']
J.append('tl.fromTo("#burst", {opacity:0, scale:.2, rotation:0}, {opacity:.9, scale:1, rotation:30, duration:.3, ease:"back.out(2)"}, 6.46); tl.to("#burst", {rotation:200, duration:1.9, ease:"none"}, 6.76);')
crnd = random.Random(11)
for i, (t0, txt, p16, p9, sz, col, rot, kind) in enumerate(CH):
    J.append(f'tl.fromTo("#ch{i}", {{opacity:0, scale:0, rotation:{rot - 40}}}, {{opacity:1, scale:1, rotation:{rot}, duration:.32, ease:"back.out(3.2)"}}, {t0});')
    t = t0 + .32; k = 0
    while t < 8.32:
        d = crnd.uniform(.14, .26)
        J.append(f'tl.to("#ch{i}", {{rotation:{rot + (6 if k % 2 == 0 else -6)}, scale:{1.08 if k % 2 == 0 else .96}, duration:{round(d, 3)}, ease:"sine.inOut"}}, {round(t, 3)});')
        t += d; k += 1
J += ['tl.to("#chaos", {filter:"grayscale(1) blur(0px)", duration:.08}, 8.42);',
      'tl.to("#chaos", {filter:"grayscale(1) blur(14px)", opacity:.45, scale:.94, duration:.25, ease:"power2.out"}, 8.79);',
      'tl.to("#chaos", {opacity:0, filter:"grayscale(1) blur(30px)", duration:.18, ease:"power2.in"}, 9.02);']
for tid, a, b, e, l1, l2, g16, g9 in TT:
    dx = -40 if (not P and g16[3] == 'l') else 0
    dy = 0 if dx else 18
    J.append(f'bin("#{tid} .l1", {a}, {{x:{dx}, y:{dy}, b:20}}); bin("#{tid} .l2", {b}, {{x:{dx}, y:{dy}, b:24, s:.94}});')
    assert e - .3 >= b + .5, tid
    if e < END: J.append(f'bout("#{tid} span", {round(e - .3, 3)}); tl.set("#{tid} span", {{opacity:0}}, {round(e + .01, 3)});')
J += ['bin("#kick1", 12.12, {y:-10, b:12, d:.45});',
      'tl.fromTo("#hero span", {opacity:0, filter:BL(30), y:40, scale:.9}, {opacity:1, filter:B0, y:0, scale:1, duration:.55, ease:"expo.out", stagger:.045, immediateRender:false}, 13.62);',
      'tl.fromTo("#hero span", {backgroundPosition:"0% 0"}, {backgroundPosition:"100% 0", duration:.9, ease:"power2.inOut", immediateRender:false}, 13.95);',
      'bout("#kick1", 14.2); bout("#hero span", 14.42, {b:24, d:.25}); tl.set("#hero span, #kick1", {opacity:0}, 14.75);']
J += ['tl.to("#foot", {filter:"blur(16px)", duration:.28, ease:"power2.in"}, 14.3);',
      'tl.fromTo("#stage", {opacity:0}, {opacity:1, duration:.25, ease:"power2.out", immediateRender:false}, 14.4);',
      'tl.set("#foot", {filter:"blur(0px)"}, 14.7);',
      'bin("#slab1", 14.5, {y:-10, b:14});',
      'bin("#bar", 14.45, {y:40, b:24, d:.5});']
for t0, S, x, y, d, e in UI:
    J.append(f'tl.to("#ui", {{scale:{S}, x:{x}, y:{y}, duration:{d}, ease:"{e}"}}, {t0});')
sx, sy = SEND
J += [f'tl.fromTo("#cur", {{opacity:0, x:{sx - 117}, y:{sy + 67}}}, {{opacity:1, x:{sx - 17}, y:{sy + 2}, duration:.45, ease:"power3.out", immediateRender:false}}, 17.35);',
      f'tl.to("#send", {{scale:.86, duration:.08, ease:"power2.in"}}, {P1_SEND}); tl.to("#send", {{scale:1, background:"#FF3D8E", duration:.25, ease:"back.out(3)"}}, {P1_SEND + .08});',
      f'tl.to("#cur", {{scale:.88, duration:.08}}, {P1_SEND}); tl.to("#cur", {{scale:1, duration:.15}}, {P1_SEND + .08});',
      'tl.to("#stage", {opacity:0, filter:BL(20), duration:.22, ease:"power2.in"}, 18.0);',
      'tl.set("#stage", {filter:"blur(0px)"}, 18.3);']
n1 = len(P1); a, b = P1_T
for i in range(n1):
    J.append(f'tl.set("#bar .c1:nth-child({i + 1})", {{display:"inline"}}, {round(a + (b - a) * i / n1, 3)});')
J.append('tl.fromTo("#caret1", {opacity:1}, {opacity:.1, duration:.3, ease:"none", yoyo:true, repeat:5, immediateRender:false}, 17.2);')
J += ['bin("#pill", 21.5, {y:30, b:20, d:.45});']
n2 = len(P2); a, b = P2_T
for i in range(n2):
    J.append(f'tl.set("#pill .c2:nth-child({i + 1})", {{display:"inline"}}, {round(a + (b - a) * i / n2, 3)});')
J += [f'tl.to("#snd2", {{scale:.85, duration:.08}}, {P2_SEND}); tl.to("#snd2", {{scale:1, duration:.2, ease:"back.out(3)"}}, {P2_SEND + .08});',
      'bout("#pill", 23.52, {d:.25});']
for i, (a, b, txt) in enumerate(SUBS):
    J.append(f'tl.fromTo("#ns{i}", {{opacity:0}}, {{opacity:1, duration:.06, immediateRender:false}}, {a}); tl.set("#ns{i}", {{opacity:0}}, {b});')
for cid, src, layer, x, y, w, ry, rz, t0, dx in CARDS:
    J.append(f'tl.fromTo("#{cid}", {{opacity:0, filter:BL(24), x:{dx}, rotationY:{ry * 1.6}, rotation:{rz}, transformPerspective:1500, scale:.9}}, {{opacity:1, filter:B0, x:0, rotationY:{ry}, scale:1, duration:.7, ease:"expo.out", immediateRender:false}}, {t0});')
    J.append(f'tl.to("#{cid}", {{y:{-14 if layer == "front" else 12}, duration:{round(min(3.2, 31.6 - (t0 + .7)), 3)}, ease:"sine.inOut"}}, {t0 + .7});')
J.append('bin("#rlab", 28.2, {y:-10, b:12});  bout("#rlab", 31.4);')
RACK = '"#foot, #pmatw, #backCards, #cd"'
fx, fy, fs, fr = CA_FWD
J += [f'tl.to({RACK}, {{filter:"blur(12px) brightness(.62)", duration:.5, ease:"power2.inOut"}}, 31.66);',
      f'tl.to("#ca", {{x:{fx}, y:{fy}, scale:{fs}, rotationY:-6, rotation:0, duration:.75, ease:"expo.inOut"}}, 31.66);',
      'tl.to("#cd", {opacity:0, duration:.4}, 31.9);',
      f'tl.to("#ca", {{filter:"blur(10px) brightness(.6)", scale:{fr}, duration:.45, ease:"power2.inOut"}}, 34.02);',
      # real student feedback (names blurred), bubbles ringed on "message" / "target"
      'bin("#nlab", 34.3, {x:-30, b:14});',
      f'tl.fromTo("#fb1", {{opacity:0, filter:BL(24), y:50, scale:.92, rotationY:{6 if P else 9}, transformPerspective:1600}}, {{opacity:1, filter:B0, y:0, scale:1, rotationY:{3 if P else 5}, duration:.55, ease:"expo.out", immediateRender:false}}, 34.45);',
      'tl.fromTo("#fb1r", {opacity:0, scale:1.08}, {opacity:1, scale:1, duration:.35, ease:"expo.out", immediateRender:false}, 35.08);',
      f'tl.fromTo("#fb2", {{opacity:0, filter:BL(24), y:50, scale:.92, rotationY:{-5 if P else -7}, transformPerspective:1800}}, {{opacity:1, filter:B0, y:0, scale:1, rotationY:{-2 if P else -4}, duration:.55, ease:"expo.out", immediateRender:false}}, 35.63);',
      'tl.to("#fb1", {filter:"brightness(.88)", duration:.3, ease:"power2.out"}, 35.63);',
      'tl.fromTo("#fb2r", {opacity:0, scale:1.06}, {opacity:1, scale:1, duration:.35, ease:"expo.out", immediateRender:false}, 36.09);',
      'bout("#nlab, #fb1, #fb2", 36.95, {d:.3}); tl.to("#ca, #cb, #cc", {opacity:0, duration:.3, ease:"power2.in"}, 36.95);',
      'tl.set("#nlab, #fb1, #fb2", {opacity:0}, 37.27);',
      f'tl.to({RACK}, {{filter:"blur(0px) brightness(1)", duration:.01}}, 37.6);']
J += ['tl.set("#bar, #slab1, #cur", {opacity:0}, 37.0);',
      'tl.fromTo("#stage", {opacity:0}, {opacity:1, duration:.3, ease:"power2.out", immediateRender:false}, 37.12);',
      'bin("#slab2", 37.3, {y:-10, b:12});']
for k, (fid, img, dx, rz, ry) in enumerate(FAN):
    J.append(f'tl.fromTo("#{fid}", {{opacity:0, filter:BL(26), y:60, scale:.86, transformPerspective:1600}}, {{opacity:1, filter:B0, y:0, scale:.9, duration:.6, ease:"expo.out", immediateRender:false}}, {37.3 + k * .08});')
    if dx: J.append(f'tl.to("#{fid}", {{x:{dx}, rotation:{rz}, rotationY:{ry}, y:30, duration:.7, ease:"expo.out"}}, 38.03);')
J += ['tl.to("#fc", {scale:1, y:-10, duration:.65, ease:"expo.out"}, 38.1);',
      'tl.to("#fl, #fr, #fc", {y:"-=40", duration:2.0, ease:"sine.inOut"}, 38.75);',
      'bin("#t7 .l1", 39.03, {y:20, b:20}); bin("#t7 .l2", 39.68, {y:20, b:24, s:.94});',
      'tl.to("#stage", {opacity:0, filter:BL(20), duration:.25, ease:"power2.in"}, 40.0);']
J += ['bin("#cta", 44.5, {y:30, b:20, d:.5});']
for i in range(5):
    t0 = 44.55 + i * .07
    J.append(f'tl.fromTo("#sp{i}", {{opacity:0, scale:0, rotation:-60}}, {{opacity:1, scale:1.1, rotation:0, duration:.25, ease:"back.out(3)", immediateRender:false}}, {round(t0, 3)}); tl.to("#sp{i}", {{opacity:0, scale:.3, duration:.35, ease:"power2.in"}}, {round(t0 + .45, 3)});')
A('\n'.join('      ' + j for j in J))
A('''      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
''')
os.makedirs(OUT, exist_ok=True)
open(f'{OUT}/index.html', 'w').write('\n'.join(o))
print(FMT, '->', OUT, len(J), 'timeline lines')
