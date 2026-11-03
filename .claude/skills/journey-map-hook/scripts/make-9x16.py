#!/usr/bin/env python3
"""Derive the 9:16 project from a finished 16:9 Journey Map Hook project.
usage: make-9x16.py <src_16x9_project_dir> <dst_9x16_project_dir> [vertical_bg_png]
Copies the project (without renders/snapshots/raw cutout) and applies the portrait layout patches.
The presenter stays at native resolution at the bottom; map/footage/titles use the top ~60%.
"""
import re, shutil, subprocess, sys, os
src, dst = sys.argv[1], sys.argv[2]
bg = sys.argv[3] if len(sys.argv) > 3 else None
if os.path.exists(dst): shutil.rmtree(dst)
subprocess.check_call(['rsync','-a','--exclude','renders','--exclude','snapshots','--exclude','cutout.mov','--exclude','bgm_full.m4a','--exclude','.hyperframes','--exclude','vo.wav',src.rstrip('/')+'/',dst.rstrip('/')+'/'])
if bg: shutil.copy(bg, os.path.join(dst,'assets','bg-lauterbrunnen-9x16.png'))
def sub(s, a, b, count=1):
    if a not in s: print('WARN: pattern not found:', a[:70])
    return s.replace(a, b)
h = open(f'{dst}/index.html').read()
for a,b in [
 ('width=1920, height=1080','width=1080, height=1920'),
 ('data-width="1920" data-height="1080"','data-width="1080" data-height="1920"'),
 ('html, body { width: 1920px; height: 1080px;','html, body { width: 1080px; height: 1920px;'),
 ('.abs { position: absolute; left: 0; top: 0; width: 1920px; height: 1080px; }','.abs { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; }'),
 ('<script src="assets/js/akg-config.js"></script>','<script>window.AKG_DIM = { W: 1080, H: 1920, vertical: true };</script>\n    <script src="assets/js/akg-config.js"></script>'),
 ('#bg { position: absolute; left: -96px; top: -54px; width: 2112px; height: 1188px;','#bg { position: absolute; left: -54px; top: -96px; width: 1188px; height: 2112px;'),
 ('assets/bg-lauterbrunnen.png','assets/bg-lauterbrunnen-9x16.png'),
 ('#map-canvas { position: absolute; left: 0; top: 0; width: 1920px; height: 1080px;','#map-canvas { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px;'),
 ('<canvas id="map-canvas" width="1920" height="1080"></canvas>','<canvas id="map-canvas" width="1080" height="1920"></canvas>'),
 ('.bk { position: absolute; left: 0; top: 0; width: 1920px; height: 1080px;','.bk { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px;'),
 ('.bk img, .bk .kbw { position: absolute; left: 0; top: 0; width: 1920px; height: 1080px;','.bk img, .bk .kbw { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px;'),
 ('.bk img { left: -80px; top: -45px; width: 2080px; height: 1170px;','.bk img { left: -45px; top: -80px; width: 1170px; height: 2080px;'),
 ('.bk .kbw video { position: absolute; left: 0; top: 0; width: 1920px; height: 1080px;','.bk .kbw video { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px;'),
 ('#pres { position: absolute; left: 0; top: 0; width: 1920px; height: 1080px; object-fit: cover; }','#pres { position: absolute; left: -420px; top: 840px; width: 1920px; height: 1080px; object-fit: cover; }'),
 ('.ttl { position: absolute; top: 40px; left: 0; width: 1920px;','.ttl { position: absolute; top: 250px; left: 0; width: 1080px;'),
 ('.ttl .big { display: inline-block; font: 900 150px/1','.ttl .big { display: inline-block; font: 900 118px/1'),
 ('font: 400 140px/1 Signature, cursive; color: #fff; margin-top: -6px; margin-left: 380px;','font: 400 112px/1 Signature, cursive; color: #fff; margin-top: -4px; margin-left: 250px;'),
 ('.num { position: absolute; left: 0; width: 1920px; top: 318px;','.num { position: absolute; left: 0; width: 1080px; top: 500px;'),
 ('.num .val { display: inline-block; font: 900 200px/1','.num .val { display: inline-block; font: 900 170px/1'),
 ('#elev { position: absolute; left: 96px; top: 330px;','#elev { position: absolute; left: 60px; top: 520px;'),
 ('style="left:560px; top:150px"','style="left:90px; top:560px"'),
 ('style="left:1060px; top:130px"','style="left:600px; top:500px"'),
 ('#brandbar { position: absolute; left: 90px; top: 62px;','#brandbar { position: absolute; left: 60px; top: 130px;'),
 ('#tagline { position: absolute; left: 96px; top: 176px;','#tagline { position: absolute; left: 66px; top: 244px;'),
 ('<div class="cl" id="cl-1" style="left:84px; top:330px">','<div class="cl" id="cl-1" style="left:70px; top:420px">'),
 ('<div class="cl r" id="cl-2" style="right:84px; top:330px">','<div class="cl" id="cl-2" style="left:70px; top:510px">'),
 ('<div class="cl" id="cl-3" style="left:84px; top:440px">','<div class="cl" id="cl-3" style="left:70px; top:600px">'),
 ('<div class="cl r" id="cl-4" style="right:84px; top:440px">','<div class="cl" id="cl-4" style="left:70px; top:690px">'),
 ('.lbl.major .tx { font: 900 30px/1','.lbl.major .tx { font: 900 34px/1'),
 ('#url { position: absolute; left: 0; width: 1920px; bottom: 52px; text-align: center; font: 800 44px/1','#url { position: absolute; left: 0; width: 1080px; bottom: 300px; text-align: center; font: 800 40px/1'),
]: h = sub(h, a, b)
# captions: wrap to two lines above the presenter's chest
i = h.index('      .cap { position: absolute;'); j = h.index('      .cap .kw')
h = h[:i] + '''      .cap { position: absolute; left: 70px; width: 940px; bottom: 330px; text-align: center; visibility: hidden; opacity: 0; font: 900 66px/1.06 Montserrat, sans-serif; color: #fff; letter-spacing: .01em; text-transform: uppercase;
        -webkit-text-stroke: 10px #14091f; paint-order: stroke fill; text-shadow: 0 6px 0 rgba(20,9,31,.9), 0 10px 26px rgba(0,0,0,.55); }
''' + h[j:]
h = re.sub(r'      #t-titlis \{.*?\n      #t-spiez \{?.*?\n', '      #t-titlis .big { font-size: 118px; } #t-titlis .scr { font-size: 100px; margin-left: 180px; }\n      #t-cliff .big { font-size: 112px; } #t-cliff .scr { font-size: 104px; margin-left: 230px; }\n      #t-spiez .big { font-size: 150px; } #t-spiez .scr { font-size: 112px; margin-left: 260px; }\n', h, flags=re.S)
h = re.sub(r'      #num-cliff \{[^\n]*\n      #num-3000 \{[^\n]*\n', '', h)
open(f'{dst}/index.html','w').write(h)
m = open(f'{dst}/assets/js/map.js').read()
m = sub(m,'const W = 1920, H = 1080;','const W = window.AKG_DIM ? window.AKG_DIM.W : 1920, H = window.AKG_DIM ? window.AKG_DIM.H : 1080;\nconst IS_VERT = !!(window.AKG_DIM && window.AKG_DIM.vertical);')
m = sub(m,'const dist = c.d * KM;','const dist = c.d * KM * (IS_VERT ? 1.75 + 0.85 * sstep(60, 420, c.d) : 1);')
m = sub(m,'camera.setViewOffset(W, H, c.sx, 0, W, H);','camera.setViewOffset(W, H, IS_VERT ? 0 : c.sx, IS_VERT ? 330 : 0, W, H);')
open(f'{dst}/assets/js/map.js','w').write(m)
a = open(f'{dst}/assets/js/anim.js').read()
a = sub(a,'const FACE = "960px 470px";','const FACE = "540px 1310px";')
a = sub(a,'const FULL = { scale: 1, x: 0, y: 0, "--ol": 0 };\n  const PIP = { scale: 0.62, x: -650, y: 0, "--ol": 1 };\n  gsap.set("#pres-pip", { transformOrigin: "960px 1080px", ...FULL });','const FULL = { scale: 1.3, x: 0, y: 0, "--ol": 0 };\n  const PIP = { scale: 1.05, x: 0, y: 0, "--ol": 1 };\n  gsap.set("#pres-pip", { transformOrigin: "540px 1920px", ...FULL });')
a = sub(a,'capLane(2.3, 290); capLane(5.26, 0, 0.3); capLane(6.45, 290); capLane(32.4, 0, 0.3); capLane(35.2, 290); capLane(51.62, 0);','')
a = sub(a,'const KB = (sel, t0, t1, from, to) => tl.fromTo(sel, { scale: from.s, x: from.x, y: from.y }, { scale: to.s, x: to.x, y: to.y,','const XK = 5;\n  const KB = (sel, t0, t1, from, to) => tl.fromTo(sel, { scale: from.s, x: from.x * XK, y: from.y }, { scale: to.s, x: to.x * XK, y: to.y,')
open(f'{dst}/assets/js/anim.js','w').write(a)
print('9:16 project written to', dst)
