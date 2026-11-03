import * as THREE from "three";
import { Line2 } from "three-addons/lines/Line2.js";
import { LineGeometry } from "three-addons/lines/LineGeometry.js";
import { LineMaterial } from "three-addons/lines/LineMaterial.js";

const A = window.AKG;
const W = 1920, H = 1080;
const R = 6378137;
const mx = (lon) => (lon * Math.PI * R) / 180;
const my = (lat) => R * Math.log(Math.tan(Math.PI / 4 + (lat * Math.PI) / 360));
const OX = mx(8.2), OY = my(46.85);
const KM = 1000 * 1.4663; // merc metres per "real" km at lat 47
const EXAG = 1.9;
const HS = 1.4663 * EXAG; // elevation (m) -> world units

const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
const lerp = (a, b, t) => a + (b - a) * t;
const sstep = (a, b, x) => { const t = clamp((x - a) / (b - a)); return t * t * (3 - 2 * t); };
const easeIO = (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);
const easeOut = (t) => 1 - Math.pow(1 - t, 3);
const easeOutBack = (t) => { const c1 = 1.70158, c3 = c1 + 1; return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2); };

const canvas = document.getElementById("map-canvas");
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: false, powerPreference: "high-performance" });
renderer.setPixelRatio(1);
renderer.setSize(W, H, false);
const FOG = new THREE.Color("#0b1c33");
renderer.setClearColor(FOG, 1);
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(30, W / H, 100, 1e7);

let ready = false;
let META = null;
const patches = {};
const U = {
  uTime: { value: 0 }, uFill: { value: 0 }, uFillR: { value: 0 }, uFillC: { value: new THREE.Vector2(0, 0) }, uGlow: { value: 0 },
  uDim: { value: 0 }, uFillMix: { value: 0.78 }, uGrid: { value: 0 }, uScan: { value: -1e9 }, uScanOn: { value: 0 }, uLakeGlow: { value: 0 },
  uPing: { value: new THREE.Vector2(0, 0) }, uPingOn: { value: 0 }, uCam: { value: new THREE.Vector3() }, uHScale: { value: HS },
  uFogColor: { value: FOG }, uFogDen: { value: 1 / 3.2e6 }, uClouds: { value: 1 }, uLight: { value: new THREE.Vector3(-0.5, 0.72, -0.48).normalize() },
};

const VERT = /* glsl */ `
uniform sampler2D uHeight; uniform float uHScale; uniform float uLift;
varying vec2 vUv; varying vec3 vW; varying float vH;
void main(){
  vUv = uv;
  float h = texture2D(uHeight, vec2(uv.x, 1.0 - uv.y)).r;
  vH = h;
  vec3 p = position;
  p.y = max(h, 0.0) * uHScale + uLift;
  vec4 w = modelMatrix * vec4(p, 1.0);
  vW = w.xyz;
  gl_Position = projectionMatrix * viewMatrix * w;
}`;

const FRAG = /* glsl */ `
precision highp float;
uniform sampler2D uAlbedo, uHeight, uSdf;
uniform vec2 uTexel; uniform float uWorldPerTexel, uHScale, uSdfRange;
uniform float uFillMix, uTime, uFill, uFillR, uGlow, uDim, uGrid, uScan, uScanOn, uLakeGlow, uPingOn, uClouds, uEdge, uIsBase, uSea, uFogDen;
uniform vec2 uFillC, uPing; uniform vec3 uCam, uFogColor, uLight; uniform vec4 uCutA, uCutB;
varying vec2 vUv; varying vec3 vW; varying float vH;

float hash(vec2 p){ return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
float vnoise(vec2 p){ vec2 i = floor(p), f = fract(p); f = f*f*(3.0-2.0*f);
  return mix(mix(hash(i), hash(i+vec2(1,0)), f.x), mix(hash(i+vec2(0,1)), hash(i+vec2(1,1)), f.x), f.y); }
float fbm(vec2 p){ return vnoise(p)*0.5 + vnoise(p*2.03)*0.25 + vnoise(p*4.1)*0.125; }

void main(){
  if (vW.x > uCutA.x && vW.x < uCutA.y && vW.z > uCutA.z && vW.z < uCutA.w) discard;
  if (vW.x > uCutB.x && vW.x < uCutB.y && vW.z > uCutB.z && vW.z < uCutB.w) discard;
  vec2 tuv = vec2(vUv.x, 1.0 - vUv.y);
  vec3 albedo = texture2D(uAlbedo, vUv).rgb;
  vec3 sdfT = texture2D(uSdf, vUv).rgb;
  float dist = (sdfT.r * 2.0 - 1.0) * uSdfRange; // ground metres, negative inside CH
  float lake = smoothstep(0.35, 0.65, sdfT.g);
  float hC = vH;
  float hR = texture2D(uHeight, tuv + vec2(uTexel.x, 0.0)).r;
  float hL = texture2D(uHeight, tuv - vec2(uTexel.x, 0.0)).r;
  float hS = texture2D(uHeight, tuv + vec2(0.0, uTexel.y)).r;
  float hN = texture2D(uHeight, tuv - vec2(0.0, uTexel.y)).r;
  vec3 n = normalize(vec3(-(hR - hL) * uHScale / (2.0 * uWorldPerTexel), 1.0, -(hS - hN) * uHScale / (2.0 * uWorldPerTexel)));
  float sea = uSea * (1.0 - smoothstep(0.0, 6.0, hC)) * (1.0 - lake);
  float water = max(lake, sea);
  if (water > 0.5) n = vec3(0.0, 1.0, 0.0);
  vec3 V = normalize(uCam - vW);
  float lamb = clamp(dot(n, uLight), 0.0, 1.0);

  vec3 col = albedo * (0.80 + 0.42 * lamb);

  // cloud shadows drifting over the land
  float cs = fbm(vW.xz * 0.000012 + vec2(uTime * 0.0035, uTime * 0.0012));
  col *= 1.0 - 0.20 * smoothstep(0.52, 0.80, cs) * uClouds * (1.0 - water);

  // water ripples + sun glint
  if (water > 0.01) {
    float sp1 = vnoise(vW.xz * 0.0009 + vec2(uTime * 0.25, -uTime * 0.18));
    float sp2 = vnoise(vW.xz * 0.0031 - vec2(uTime * 0.40, uTime * 0.30));
    float sparkle = smoothstep(0.60, 0.90, sp1 * 0.6 + sp2 * 0.5) * 0.65;
    vec3 nw = normalize(vec3((sp1 - 0.5) * 0.10, 1.0, (sp2 - 0.5) * 0.10));
    vec3 Hh = normalize(uLight + V);
    float spec = pow(clamp(dot(nw, Hh), 0.0, 1.0), 140.0);
    float fres = pow(1.0 - clamp(V.y, 0.0, 1.0), 3.0);
    col += water * (sparkle * 0.30 + spec * 0.8) * vec3(0.85, 0.96, 1.0);
    col = mix(col, col * vec3(0.9, 1.08, 1.12) + vec3(0.02, 0.07, 0.10), water * fres * 0.55);
    col = mix(col, vec3(0.10, 0.78, 0.86), lake * uLakeGlow * 0.38);
  }

  // Switzerland highlight: orange fill (swept in as a ripple from the centre) + neon rim
  float inside = smoothstep(60.0, -60.0, dist);
  float dC = distance(vW.xz, uFillC);
  float sweep = smoothstep(uFillR, uFillR - 40000.0, dC);
  float fillM = inside * sweep * uFill;
  vec3 orange = vec3(1.0, 0.40, 0.12);
  float lum = dot(albedo, vec3(0.3, 0.59, 0.11));
  vec3 oc = orange * (0.52 + 0.95 * lum) * (0.82 + 0.40 * lamb);
  col = mix(col, oc, fillM * uFillMix);
  float rim = exp(-abs(dist) / 260.0) * sweep * uGlow;
  float halo = exp(-abs(dist) / 1500.0) * sweep * uGlow * (0.5 + 0.5 * step(0.0, dist));
  col += vec3(1.0, 0.36, 0.14) * rim * 1.6 + vec3(1.0, 0.45, 0.2) * halo * 0.22;
  // wavefront ring while sweeping
  float ring = exp(-pow((dC - uFillR + 12000.0) / 9000.0, 2.0)) * step(0.0, uFillR) * (1.0 - smoothstep(0.0, 1.0, uFill * 1.0001 - 0.98)) ;
  col += vec3(1.0, 0.7, 0.4) * ring * inside * 0.35;
  // dim everything outside the country
  col *= 1.0 - uDim * 0.20 * smoothstep(0.0, 2500.0, dist);
  float g2 = dot(col, vec3(0.3, 0.59, 0.11));
  col = mix(col, vec3(g2), uDim * 0.14 * smoothstep(0.0, 4000.0, dist));

  // lake ping rings (Spiez / Lake Thun)
  float pd = distance(vW.xz, uPing);
  float pr = sin(pd * 0.00045 - uTime * 3.2) * 0.5 + 0.5;
  col += vec3(0.4, 1.0, 1.0) * lake * uPingOn * smoothstep(0.82, 1.0, pr) * exp(-pd / 22000.0) * 0.9;

  // analytical grid
  vec2 gp = vW.xz / 36000.0;
  vec2 gl = abs(fract(gp) - 0.5);
  float gridLine = (1.0 - smoothstep(0.0, 0.006, 0.5 - max(gl.x, gl.y) + 0.0)) ;
  float gx = smoothstep(0.494, 0.5, gl.x) + smoothstep(0.494, 0.5, gl.y);
  col += vec3(0.4, 0.85, 1.0) * clamp(gx, 0.0, 1.0) * uGrid * 0.22;

  // satellite scan band
  float sb = exp(-pow((vW.z - uScan) / 14000.0, 2.0)) * uScanOn;
  col += vec3(0.5, 0.95, 1.0) * sb * 0.55;

  // distance fog
  float dd = distance(uCam, vW);
  float fogF = 1.0 - exp(-pow(dd * uFogDen, 1.35));
  col = mix(col, uFogColor, clamp(fogF, 0.0, 0.92));

  float edge = min(min(vUv.x, 1.0 - vUv.x), min(vUv.y, 1.0 - vUv.y));
  float a = smoothstep(0.0, uEdge, edge);
  if (uIsBase > 0.5) gl_FragColor = vec4(mix(uFogColor, col, a), 1.0);
  else gl_FragColor = vec4(col, a);
}`;

function makeHalfTex(int16, w, h) {
  const out = new Uint16Array(w * h);
  for (let i = 0; i < out.length; i++) out[i] = THREE.DataUtils.toHalfFloat(int16[i] / 4);
  const t = new THREE.DataTexture(out, w, h, THREE.RedFormat, THREE.HalfFloatType);
  t.minFilter = THREE.LinearFilter; t.magFilter = THREE.LinearFilter; t.wrapS = t.wrapT = THREE.ClampToEdgeWrapping;
  t.generateMipmaps = false; t.needsUpdate = true;
  return t;
}

function loadTex(url) {
  return new Promise((res, rej) => {
    new THREE.TextureLoader().load(url, (t) => {
      t.colorSpace = THREE.NoColorSpace; t.minFilter = THREE.LinearMipmapLinearFilter; t.magFilter = THREE.LinearFilter;
      t.anisotropy = 8; t.wrapS = t.wrapT = THREE.ClampToEdgeWrapping; res(t);
    }, undefined, rej);
  });
}

const sampleData = {};
function sampleElev(lon, lat) {
  for (const id of ["titlis", "thun", "ch", "eu"]) {
    const m = META.patches[id];
    const x = mx(lon), y = my(lat);
    if (x < m.x0 || x > m.x1 || y < m.y0 || y > m.y1) continue;
    const px = ((x - m.x0) / (m.x1 - m.x0)) * (m.w - 1), py = ((m.y1 - y) / (m.y1 - m.y0)) * (m.h - 1);
    const xi = Math.floor(px), yi = Math.floor(py), tx = px - xi, ty = py - yi;
    const d = sampleData[id];
    const g = (a, b) => d[Math.min(m.h - 1, b) * m.w + Math.min(m.w - 1, a)] / 4;
    return (g(xi, yi) * (1 - tx) + g(xi + 1, yi) * tx) * (1 - ty) + (g(xi, yi + 1) * (1 - tx) + g(xi + 1, yi + 1) * tx) * ty;
  }
  return 0;
}
const W3 = (lon, lat, lift = 0) => new THREE.Vector3(mx(lon) - OX, Math.max(0, sampleElev(lon, lat)) * HS + lift, -(my(lat) - OY));

const lines = { borders: [], extra: [] };
const dom = { labels: [], nbr: [] };
let cableCurve = null, boatCurve = null, gondolas = [], boat = null, riverLines = [];
const lineMats = [];

async function build() {
  META = await (await fetch("assets/map/meta.json")).json();
  const defs = [
    { id: "eu", seg: [520, 370], edge: 0.05, base: true, sea: 1, lift: -30 },
    { id: "ch", seg: [1000, 635], edge: 0.05, lift: 6 },
    { id: "titlis", seg: [700, 575], edge: 0.06, lift: 14 },
    { id: "thun", seg: [700, 520], edge: 0.06, lift: 14 },
  ];
  const innerRect = (id, e) => {
    const m = META.patches[id];
    const dx = (m.x1 - m.x0) * e, dy = (m.y1 - m.y0) * e;
    return new THREE.Vector4(m.x0 + dx - OX, m.x1 - dx - OX, -(m.y1 - dy - OY), -(m.y0 + dy - OY));
  };
  const cuts = {
    eu: [innerRect("ch", 0.05), new THREE.Vector4(0, 0, 0, 0)],
    ch: [innerRect("titlis", 0.06), innerRect("thun", 0.06)],
    titlis: [new THREE.Vector4(0, 0, 0, 0), new THREE.Vector4(0, 0, 0, 0)],
    thun: [new THREE.Vector4(0, 0, 0, 0), new THREE.Vector4(0, 0, 0, 0)],
  };
  await Promise.all(
    defs.map(async (d) => {
      const m = META.patches[d.id];
      const [alb, sdf, buf] = await Promise.all([
        loadTex(`assets/map/${d.id}_albedo.jpg`),
        loadTex(`assets/map/${d.id}_sdf.png`),
        fetch(`assets/map/${d.id}_height.bin`).then((r) => r.arrayBuffer()),
      ]);
      const i16 = new Int16Array(buf);
      sampleData[d.id] = i16;
      const hTex = makeHalfTex(i16, m.w, m.h);
      sdf.minFilter = THREE.LinearFilter; sdf.generateMipmaps = false;
      const wMerc = m.x1 - m.x0, hMerc = m.y1 - m.y0;
      const geo = new THREE.PlaneGeometry(wMerc, hMerc, d.seg[0], d.seg[1]);
      geo.rotateX(-Math.PI / 2);
      const mat = new THREE.ShaderMaterial({
        uniforms: {
          ...U,
          uAlbedo: { value: alb }, uHeight: { value: hTex }, uSdf: { value: sdf }, uTexel: { value: new THREE.Vector2(1 / m.w, 1 / m.h) },
          uWorldPerTexel: { value: wMerc / m.w }, uSdfRange: { value: m.sdfRange * 1.0 }, uEdge: { value: d.edge }, uIsBase: { value: d.base ? 1 : 0 },
          uSea: { value: d.sea ? 1 : 0 }, uLift: { value: d.lift }, uCutA: { value: cuts[d.id][0] }, uCutB: { value: cuts[d.id][1] },
        },
        vertexShader: VERT, fragmentShader: FRAG, transparent: !d.base, depthWrite: true, depthTest: true,
        polygonOffset: !d.base, polygonOffsetFactor: -2, polygonOffsetUnits: -2,
      });
      const mesh = new THREE.Mesh(geo, mat);
      mesh.position.set((m.x0 + m.x1) / 2 - OX, 0, -((m.y0 + m.y1) / 2 - OY));
      mesh.frustumCulled = false;
      mesh.renderOrder = d.base ? 0 : d.id === "ch" ? 1 : 2;
      scene.add(mesh);
      patches[d.id] = mesh;
    }),
  );

  // ---- borders (colour-coded per neighbour) ----
  const res = new THREE.Vector2(W, H);
  const mkLine = (pts, color, width, opacity, additive) => {
    const g = new LineGeometry();
    g.setPositions(pts.flatMap((p) => [p.x, p.y, p.z]));
    const mat = new LineMaterial({ color, linewidth: width, transparent: true, opacity, depthWrite: false, depthTest: true, worldUnits: false });
    if (additive) mat.blending = THREE.AdditiveBlending;
    mat.resolution.copy(res);
    lineMats.push(mat);
    const l = new Line2(g, mat);
    l.frustumCulled = false; l.renderOrder = 10;
    scene.add(l);
    return l;
  };
  META.borders.forEach((b, i) => {
    const pts = b.pts.map(([x, y, h]) => new THREE.Vector3(x - OX, Math.max(0, h) * HS + 160, -(y - OY)));
    const col = new THREE.Color(A.borderColor[b.code]);
    const glow = mkLine(pts, col, 16, 0.22, true);
    const mid = mkLine(pts, col, 6, 0.55, true);
    const core = mkLine(pts, new THREE.Color("#ffffff").lerp(col, 0.35), 2.6, 1, false);
    lines.borders.push({ code: b.code, parts: [glow, mid, core], n: pts.length - 1, mid: pts[Math.floor(pts.length / 2)], idx: i });
  });

  // ---- cable car route Engelberg -> Titlis ----
  const cabPts = [
    [8.4085, 46.8175], [8.4115, 46.8010], [8.4060, 46.7870], [8.4190, 46.7790], [8.4310, 46.7745], [8.4375, 46.7722],
  ].map(([lo, la]) => W3(lo, la, 420));
  cableCurve = new THREE.CatmullRomCurve3(cabPts, false, "catmullrom", 0.2);
  const cp = cableCurve.getPoints(80);
  lines.cable = mkLine(cp, new THREE.Color("#ffffff"), 2.4, 0.9, false);
  const gMat = new THREE.MeshBasicMaterial({ color: 0xe8261c });
  const gMat2 = new THREE.MeshBasicMaterial({ color: 0xffffff });
  for (let i = 0; i < 2; i++) {
    const grp = new THREE.Group();
    const body = new THREE.Mesh(new THREE.BoxGeometry(1.6, 1.0, 1.0), gMat);
    const roof = new THREE.Mesh(new THREE.BoxGeometry(1.8, 0.28, 1.15), gMat2); roof.position.y = 0.65;
    grp.add(body, roof); grp.renderOrder = 12;
    body.frustumCulled = roof.frustumCulled = false;
    scene.add(grp); gondolas.push(grp);
  }

  // ---- boat on Lake Thun ----
  const boatPts = [[7.633, 46.752], [7.672, 46.737], [7.713, 46.722], [7.758, 46.711], [7.80, 46.700], [7.84, 46.692]].map(([lo, la]) => W3(lo, la, 20));
  boatCurve = new THREE.CatmullRomCurve3(boatPts, false, "catmullrom", 0.3);
  boat = new THREE.Group();
  const hull = new THREE.Mesh(new THREE.BoxGeometry(2.4, 0.5, 0.8), gMat2);
  const cab = new THREE.Mesh(new THREE.BoxGeometry(1.0, 0.5, 0.6), new THREE.MeshBasicMaterial({ color: 0xff661f })); cab.position.y = 0.45;
  boat.add(hull, cab); scene.add(boat);

  // ---- pins / labels (DOM) ----
  const layer = document.getElementById("hud-labels");
  const mk = (cls, html) => { const e = document.createElement("div"); e.className = "lbl " + cls; e.innerHTML = html; layer.appendChild(e); return e; };
  for (const l of A.labels) {
    const poi = l.poi ? META.poi[l.poi] : null;
    const text = l.text || (poi && poi.label) || "";
    const el = mk(l.kind, `<i class="ring"></i><i class="ring r2"></i><i class="dot"></i><span class="tx">${text}</span>`);
    let pos;
    if (l.lake === "thun") { const bp = boatCurve.getPoint(0.42); pos = bp.clone(); pos.y += 120; }
    else pos = new THREE.Vector3(poi.x - OX, Math.max(0, poi.h) * HS + 40, -(poi.y - OY));
    dom.labels.push({ ...l, el, pos });
  }
  // neighbour labels at run midpoints
  const seen = {};
  for (const b of lines.borders) {
    if (b.code === "LI" || seen[b.code]) continue;
    seen[b.code] = 1;
    const el = mk("nbr", `<span class="tx">${A.borderName[b.code]}</span>`);
    el.style.setProperty("--c", A.borderColor[b.code]);
    const fixed = { DE: [8.0, 47.8], FR: [5.62, 46.55], IT: [7.55, 45.78], AT: [10.35, 47.62] }[b.code];
    dom.nbr.push({ el, pos: W3(fixed[0], fixed[1], 0).add(new THREE.Vector3(0, 6000, 0)), code: b.code });
  }
  ready = true;
}

// ---------- camera ----------
function camAt(t) {
  const K = A.cam;
  let a = K[0], b = K[0];
  if (t <= K[0].t) { a = b = K[0]; }
  else if (t >= K[K.length - 1].t) { a = b = K[K.length - 1]; }
  else for (let i = 0; i < K.length - 1; i++) if (t >= K[i].t && t < K[i + 1].t) { a = K[i]; b = K[i + 1]; break; }
  let u = a === b ? 0 : (t - a.t) / (b.t - a.t);
  const e = b.e;
  u = e === "io" ? easeIO(u) : e === "out" ? easeOut(u) : u;
  // distance interpolates in log space (smooth dolly)
  const d = Math.exp(lerp(Math.log(a.d), Math.log(b.d), u));
  return { lon: lerp(a.lon, b.lon, u), lat: lerp(a.lat, b.lat, u), d, p: lerp(a.p, b.p, u), h: lerp(a.h, b.h, u), sx: lerp(a.sx, b.sx, u) };
}

const tmp = new THREE.Vector3();
function placeCamera(t) {
  const c = camAt(t);
  const tgt = W3(c.lon, c.lat, 0);
  const dist = c.d * KM;
  const p = (c.p * Math.PI) / 180, hh = (c.h * Math.PI) / 180;
  // subtle handheld drift
  const dr = dist * 0.0009;
  const jx = Math.sin(t * 0.9) * dr + Math.sin(t * 2.3 + 1.7) * dr * 0.4;
  const jy = Math.sin(t * 1.1 + 0.6) * dr * 0.6;
  camera.position.set(tgt.x + Math.sin(hh) * Math.cos(p) * dist + jx, tgt.y + Math.sin(p) * dist + jy, tgt.z + Math.cos(hh) * Math.cos(p) * dist);
  camera.near = Math.max(80, dist * 0.02);
  camera.far = dist * 40 + 4e5;
  camera.lookAt(tgt);
  camera.updateProjectionMatrix();
  camera.setViewOffset(W, H, c.sx, 0, W, H);
  camera.updateMatrixWorld(true);
  U.uCam.value.copy(camera.position);
  U.uFogDen.value = 1 / (dist * 2.4 + 1.2e6);
  return { c, dist };
}

function project(pos) {
  tmp.copy(pos).project(camera);
  return { x: (tmp.x * 0.5 + 0.5) * W, y: (-tmp.y * 0.5 + 0.5) * H, z: tmp.z };
}

const inWin = (t) => A.mapOn.some(([a, b]) => t >= a - 0.08 && t <= b + 0.08);

function updateUniforms(t) {
  U.uTime.value = t;
  const chC = new THREE.Vector2(mx(8.22) - OX, -(my(46.8) - OY));
  U.uFillC.value.copy(chC);
  const sweepT = clamp((t - 2.7) / 1.5);
  U.uFillR.value = t < 2.7 ? 0 : lerp(0, 520000, easeIO(sweepT)) + (t > 4.2 ? 1e7 : 0);
  U.uFill.value = t < 2.7 ? 0 : 1;
  U.uGlow.value = sstep(2.7, 3.6, t) * 0.95;
  U.uFillMix.value = lerp(0.80, 0.07, sstep(6.2, 8.6, t));
  U.uDim.value = sstep(3.3, 4.6, t);
  U.uGrid.value = (1 - sstep(7.0, 9.5, t)) * sstep(1.5, 2.2, t) * 0.9 + (t > 35 ? sstep(35.2, 36, t) * (1 - sstep(37, 38, t)) * 0.7 : 0);
  const sc = clamp((t - 1.9) / 1.5);
  U.uScanOn.value = t > 1.9 && t < 3.5 ? 1 : 0;
  U.uScan.value = lerp(-(my(41.5) - OY) * -1 + 0, 0, 0) + lerp(-(my(42.2) - OY), -(my(51.5) - OY), easeIO(sc)) * 1;
  U.uLakeGlow.value = sstep(44.8, 46, t) * (1 - sstep(51.0, 51.8, t)) + sstep(36.8, 38, t) * (1 - sstep(38.5, 38.8, t)) * 0.6;
  const sp = META.poi.spiez;
  U.uPing.value.set(sp.x - OX, -(sp.y - OY));
  U.uPingOn.value = sstep(44.9, 46.2, t) * (1 - sstep(51.0, 51.8, t));
}

function updateLines(t) {
  // border draw-on, staggered per run
  const total = lines.borders.length;
  lines.borders.forEach((b, i) => {
    const t0 = 3.25 + i * 0.16, dur = 1.5;
    const p = easeIO(clamp((t - t0) / dur));
    const k = Math.floor(p * b.n);
    for (const part of b.parts) {
      part.visible = k >= 1;
      if (k >= 1) part.geometry.instanceCount = k;
    }
    // fade out as we leave the national overview
    const fade = 1 - sstep(6.4, 8.6, t) * 0.85;
    b.parts[0].material.opacity = 0.22 * fade; b.parts[1].material.opacity = 0.55 * fade; b.parts[2].material.opacity = fade;
    
  });
  // cable + gondolas
  const cabOn = t > 7.6 && t < 10.5;
  if (lines.cable) lines.cable.visible = cabOn && sstep(8.0, 9.2, t) > 0.01;
  const gsz = camAt(t).d * KM * 0.0055;
  gondolas.forEach((g, i) => {
    g.visible = cabOn;
    if (!cabOn) return;
    const cyc = ((t - 8.4) / 6.5 + i * 0.5) % 1;
    const u = i === 0 ? easeIO(cyc < 0 ? cyc + 1 : cyc) : 1 - easeIO(cyc < 0 ? cyc + 1 : cyc);
    g.position.copy(cableCurve.getPoint(clamp(u)));
    g.position.y -= gsz * 0.9;
    g.scale.setScalar(gsz * (0.4 + 0.6 * sstep(8.0, 9.6, t)));
    g.lookAt(camera.position.x, g.position.y, camera.position.z);
  });
  // boat
  const boatOn = false;
  boat.visible = boatOn;
  if (boatOn) {
    const u = (((t - 36.8) / 14) % 1 + 1) % 1;
    boat.position.copy(boatCurve.getPoint(u));
    const tan = boatCurve.getTangent(u);
    boat.rotation.y = Math.atan2(-tan.z, tan.x);
    boat.scale.setScalar(camAt(t).d * KM * 0.01);
  }
  for (const m of lineMats) m.resolution.set(W, H);
}

function updateLabels(t) {
  const place = (el, pos, t0, t1, scaleBase = 1) => {
    const vis = t >= t0 - 0.02 && t <= t1;
    if (!vis) { el.style.opacity = 0; return; }
    const pr = project(pos);
    const inn = clamp((t - t0) / 0.45), out = 1 - clamp((t - (t1 - 0.3)) / 0.3);
    const s = easeOutBack(inn) * scaleBase;
    el.style.opacity = String(clamp(inn * 3) * out);
    el.style.transform = `translate(${pr.x.toFixed(1)}px, ${pr.y.toFixed(1)}px) scale(${s.toFixed(3)})`;
    // ping ring phase (deterministic)
    const ph = (t * 0.9) % 1;
    el.style.setProperty("--p1", ph.toFixed(3));
    el.style.setProperty("--p2", ((ph + 0.5) % 1).toFixed(3));
  };
  for (const l of dom.labels) place(l.el, l.pos, l.t0, l.t1);
  for (const n of dom.nbr) place(n.el, n.pos, A.nbrLabels.t0 + 0.1, A.nbrLabels.t1);
}

let lastT = -1;
export function renderAt(t) {
  if (!ready) return;
  lastT = t;
  const on = inWin(t);
  canvas.style.visibility = on ? "visible" : "hidden";
  if (!on) { for (const l of dom.labels) l.el.style.opacity = 0; for (const n of dom.nbr) n.el.style.opacity = 0; return; }
  updateUniforms(t);
  placeCamera(t);
  updateLines(t);
  renderer.render(scene, camera);
  updateLabels(t);
  // HUD callouts that follow map points (SVG leader lines) are updated by the page script
  if (window.AKG_afterMap) window.AKG_afterMap(t, { project, META, W3 });
}

window.AKG_map = { renderAt, project: (p) => project(p) };
window.__hf = window.__hf || {};
window.__hf.buildReady = window.__hf.buildReady || {};
window.__hf.buildReady["akg-map"] = build().then(() => { renderAt(window.__hfThreeTime || 0); });
window.addEventListener("hf-seek", (e) => renderAt(e.detail.time));
