// Bakes terrain patches (heights, albedo, SDF), borders and POIs for the Switzerland map.
// Data: AWS Terrain Tiles (terrarium), NASA GIBS Blue Marble, Natural Earth (public domain).
import fs from "node:fs";
import path from "node:path";
import sharp from "sharp";
import { createCanvas } from "@napi-rs/canvas";

const SCR = process.argv[2];
const OUT = process.argv[3];
const CACHE = path.join(SCR, "data", "tiles");
fs.mkdirSync(CACHE, { recursive: true });
fs.mkdirSync(OUT, { recursive: true });

const T = 256;
const lonX = (lon, z) => ((lon + 180) / 360) * 2 ** z * T;
const latY = (lat, z) => {
  const r = (lat * Math.PI) / 180;
  return ((1 - Math.log(Math.tan(r) + 1 / Math.cos(r)) / Math.PI) / 2) * 2 ** z * T;
};
// world mercator metres (origin at lon=0,lat=0; y up)
const R = 6378137;
const mx = (lon) => (lon * Math.PI * R) / 180;
const my = (lat) => R * Math.log(Math.tan(Math.PI / 4 + (lat * Math.PI) / 360));

async function fetchTile(url, file) {
  const fp = path.join(CACHE, file);
  if (fs.existsSync(fp) && fs.statSync(fp).size > 200) return fs.readFileSync(fp);
  for (let a = 0; a < 4; a++) {
    try {
      const r = await fetch(url);
      if (r.ok) {
        const b = Buffer.from(await r.arrayBuffer());
        fs.writeFileSync(fp, b);
        return b;
      }
      if (r.status === 404) return null;
    } catch (e) {}
    await new Promise((r) => setTimeout(r, 400 * (a + 1)));
  }
  return null;
}

async function pool(items, n, fn) {
  const res = new Array(items.length);
  let i = 0;
  await Promise.all(
    Array.from({ length: n }, async () => {
      while (i < items.length) {
        const k = i++;
        res[k] = await fn(items[k], k);
      }
    }),
  );
  return res;
}

// Mosaic of tiles covering a bbox at zoom z -> {px: Float32 elev or RGB buffer, w, h, x0, y0}
async function mosaic(kind, bbox, z) {
  const x0 = lonX(bbox.w, z), x1 = lonX(bbox.e, z);
  const y0 = latY(bbox.n, z), y1 = latY(bbox.s, z);
  const tx0 = Math.floor(x0 / T), tx1 = Math.floor((x1 - 1e-6) / T);
  const ty0 = Math.floor(y0 / T), ty1 = Math.floor((y1 - 1e-6) / T);
  const tiles = [];
  for (let ty = ty0; ty <= ty1; ty++) for (let tx = tx0; tx <= tx1; tx++) tiles.push({ tx, ty });
  const W = (tx1 - tx0 + 1) * T, H = (ty1 - ty0 + 1) * T;
  const comps = await pool(tiles, 12, async ({ tx, ty }) => {
    let url, file;
    if (kind === "terr") {
      url = `https://s3.amazonaws.com/elevation-tiles-prod/terrarium/${z}/${tx}/${ty}.png`;
      file = `terr_${z}_${tx}_${ty}.png`;
    } else {
      url = `https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/BlueMarble_ShadedRelief_Bathymetry/default/2004-08/GoogleMapsCompatible_Level8/${z}/${ty}/${tx}.jpeg`;
      file = `bm_${z}_${tx}_${ty}.jpg`;
    }
    const buf = await fetchTile(url, file);
    if (!buf) return null;
    return { input: buf, left: (tx - tx0) * T, top: (ty - ty0) * T };
  });
  const ok = comps.filter(Boolean);
  const img = await sharp({ create: { width: W, height: H, channels: 3, background: { r: 0, g: 0, b: 0 } } })
    .composite(ok)
    .removeAlpha()
    .toColourspace("srgb")
    .raw()
    .toBuffer();
  if (img.length !== W * H * 3) throw new Error(`mosaic channel mismatch ${img.length} vs ${W * H * 3}`);
  // crop to bbox pixel window
  const cx = Math.round(x0 - tx0 * T), cy = Math.round(y0 - ty0 * T);
  const cw = Math.round(x1 - x0), ch = Math.round(y1 - y0);
  const out = Buffer.alloc(cw * ch * 3);
  for (let y = 0; y < ch; y++) img.copy(out, y * cw * 3, ((cy + y) * W + cx) * 3, ((cy + y) * W + cx + cw) * 3);
  return { buf: out, w: cw, h: ch, missing: tiles.length - ok.length, tiles: tiles.length };
}

function decodeElev(rgb, n) {
  const e = new Float32Array(n);
  for (let i = 0; i < n; i++) e[i] = rgb[i * 3] * 256 + rgb[i * 3 + 1] + rgb[i * 3 + 2] / 256 - 32768;
  return e;
}

function resizeF32(src, sw, sh, dw, dh) {
  if (sw === dw && sh === dh) return src;
  const out = new Float32Array(dw * dh);
  for (let y = 0; y < dh; y++) {
    const fy = ((y + 0.5) * sh) / dh - 0.5;
    const y0 = Math.max(0, Math.floor(fy)), y1 = Math.min(sh - 1, y0 + 1), ty = fy - Math.floor(fy);
    for (let x = 0; x < dw; x++) {
      const fx = ((x + 0.5) * sw) / dw - 0.5;
      const x0 = Math.max(0, Math.floor(fx)), x1 = Math.min(sw - 1, x0 + 1), tx = fx - Math.floor(fx);
      const a = src[y0 * sw + x0], b = src[y0 * sw + x1], c = src[y1 * sw + x0], d = src[y1 * sw + x1];
      out[y * dw + x] = (a * (1 - tx) + b * tx) * (1 - ty) + (c * (1 - tx) + d * tx) * ty;
    }
  }
  return out;
}

async function resizeRGB(buf, sw, sh, dw, dh) {
  if (sw === dw && sh === dh) return buf;
  return sharp(buf, { raw: { width: sw, height: sh, channels: 3 } }).resize(dw, dh, { kernel: "lanczos3" }).raw().toBuffer();
}

// deterministic value noise
function hash(x, y) {
  let h = x * 374761393 + y * 668265263;
  h = (h ^ (h >>> 13)) * 1274126177;
  return ((h ^ (h >>> 16)) >>> 0) / 4294967295;
}
function vnoise(x, y) {
  const xi = Math.floor(x), yi = Math.floor(y), xf = x - xi, yf = y - yi;
  const u = xf * xf * (3 - 2 * xf), v = yf * yf * (3 - 2 * yf);
  return (hash(xi, yi) * (1 - u) + hash(xi + 1, yi) * u) * (1 - v) + (hash(xi, yi + 1) * (1 - u) + hash(xi + 1, yi + 1) * u) * v;
}
function fbm(x, y) {
  return vnoise(x, y) * 0.5 + vnoise(x * 2.1, y * 2.1) * 0.25 + vnoise(x * 4.3, y * 4.3) * 0.125 + vnoise(x * 8.7, y * 8.7) * 0.0625;
}

// Euclidean distance transform (Felzenszwalb), returns squared distance
function edt(mask, w, h) {
  const INF = 1e20;
  const f = new Float64Array(Math.max(w, h)), d = new Float64Array(Math.max(w, h));
  const v = new Int32Array(Math.max(w, h)), z = new Float64Array(Math.max(w, h) + 1);
  const g = new Float64Array(w * h);
  for (let i = 0; i < w * h; i++) g[i] = mask[i] ? 0 : INF;
  const pass = (n, get, set) => {
    let k = 0;
    v[0] = 0; z[0] = -INF; z[1] = INF;
    for (let q = 1; q < n; q++) {
      let s;
      while (true) {
        const p = v[k];
        s = (f[q] + q * q - (f[p] + p * p)) / (2 * q - 2 * p);
        if (s <= z[k]) k--; else break;
        if (k < 0) { k = 0; break; }
      }
      k++; v[k] = q; z[k] = s; z[k + 1] = INF;
    }
    k = 0;
    for (let q = 0; q < n; q++) {
      while (z[k + 1] < q) k++;
      const p = v[k];
      d[q] = (q - p) * (q - p) + f[p];
    }
  };
  for (let x = 0; x < w; x++) {
    for (let y = 0; y < h; y++) f[y] = g[y * w + x];
    pass(h);
    for (let y = 0; y < h; y++) g[y * w + x] = d[y];
  }
  for (let y = 0; y < h; y++) {
    for (let x = 0; x < w; x++) f[x] = g[y * w + x];
    pass(w);
    for (let x = 0; x < w; x++) g[y * w + x] = d[x];
  }
  return g;
}

// ---------- vector data ----------
const countries = JSON.parse(fs.readFileSync(path.join(SCR, "ne.json"), "utf8"));
const lakes = JSON.parse(fs.readFileSync(path.join(SCR, "data", "ne_lakes.json"), "utf8"));
const lakesEu = JSON.parse(fs.readFileSync(path.join(SCR, "data", "ne_lakes_eu.json"), "utf8"));
lakes.features.push(...lakesEu.features);
const rivers = JSON.parse(fs.readFileSync(path.join(SCR, "data", "ne_rivers.json"), "utf8"));
const byName = (n) => countries.features.find((f) => f.properties.NAME === n || f.properties.ADMIN === n);
const polysOf = (f) => (f.geometry.type === "Polygon" ? [f.geometry.coordinates] : f.geometry.coordinates);
const officialCH = JSON.parse(fs.readFileSync(path.join(SCR, "geo", "sb_CH.json"), "utf8")).results[0];
const officialLI = JSON.parse(fs.readFileSync(path.join(SCR, "geo", "sb_LI.json"), "utf8")).results[0];
const CH = { geometry: officialCH.geometry }; // swisstopo swissBOUNDARIES3D (official), WGS84

// ---------- patches ----------
const PATCHES = [
  { id: "eu", bbox: { w: -14, e: 32, s: 33, n: 61 }, zt: 7, zb: 7, maxW: 3900 },
  { id: "ch", bbox: { w: 5.55, e: 10.85, s: 45.7, n: 48.0 }, zt: 10, zb: 8, maxW: 3600 },
  { id: "titlis", bbox: { w: 8.12, e: 8.76, s: 46.62, n: 46.98 }, zt: 12, zb: 8, maxW: 2800 },
  { id: "thun", bbox: { w: 7.38, e: 8.02, s: 46.52, n: 46.86 }, zt: 12, zb: 8, maxW: 2800 },
];

const meta = {};
let chHeightForLines = null; // for border elevation sampling

for (const P of PATCHES) {
  console.log("patch", P.id);
  const mt = await mosaic("terr", P.bbox, P.zt);
  console.log("  terrain tiles", mt.tiles, "missing", mt.missing, mt.w, mt.h);
  const elev0 = decodeElev(mt.buf, mt.w * mt.h);
  const scale = Math.min(1, P.maxW / mt.w);
  const W = Math.round(mt.w * scale), H = Math.round(mt.h * scale);
  const elev = resizeF32(elev0, mt.w, mt.h, W, H);
  const mb = await mosaic("bm", P.bbox, P.zb);
  const bm = await resizeRGB(mb.buf, mb.w, mb.h, W, H);

  // mercator extents (metres)
  const X0 = mx(P.bbox.w), X1 = mx(P.bbox.e), Y0 = my(P.bbox.s), Y1 = my(P.bbox.n);
  const mpp = (X1 - X0) / W; // metres per pixel (mercator)
  const lat0 = ((P.bbox.s + P.bbox.n) / 2) * (Math.PI / 180);
  const realMpp = mpp * Math.cos(lat0); // true ground metres per pixel

  const toPx = (lon, lat) => [((mx(lon) - X0) / (X1 - X0)) * W, ((Y1 - my(lat)) / (Y1 - Y0)) * H];

  // water + CH masks via canvas
  const cvs = createCanvas(W, H);
  const ctx = cvs.getContext("2d");
  const drawPolys = (polys, fill) => {
    ctx.fillStyle = fill;
    for (const poly of polys) {
      ctx.beginPath();
      for (const ring of poly) {
        ring.forEach(([lo, la], i) => {
          const [x, y] = toPx(lo, la);
          i ? ctx.lineTo(x, y) : ctx.moveTo(x, y);
        });
        ctx.closePath();
      }
      ctx.fill("evenodd");
    }
  };
  ctx.fillStyle = "#000"; ctx.fillRect(0, 0, W, H);
  for (const f of lakes.features) {
    if (!f.geometry) continue;
    drawPolys(polysOf(f), "#fff");
  }
  let img = ctx.getImageData(0, 0, W, H).data;
  const lakeMask = new Uint8Array(W * H);
  for (let i = 0; i < W * H; i++) lakeMask[i] = img[i * 4];

  if (P.id !== "eu") {
    // refine lakes with the DEM: lake surfaces are exactly flat in the terrain data
    const dNE = edt(lakeMask.map((v) => (v > 127 ? 1 : 0)), W, H);
    const near = new Uint8Array(W * H);
    for (let i = 0; i < W * H; i++) near[i] = Math.sqrt(dNE[i]) * realMpp < 3000 ? 1 : 0;
    const flat = new Uint8Array(W * H);
    for (let y = 2; y < H - 2; y++) for (let x = 2; x < W - 2; x++) {
      const i = y * W + x;
      if (!near[i] || elev[i] > 1500) continue;
      let mn = 1e9, mxv = -1e9;
      for (let dy = -2; dy <= 2; dy++) for (let dx = -2; dx <= 2; dx++) { const v = elev[(y + dy) * W + x + dx]; if (v < mn) mn = v; if (v > mxv) mxv = v; }
      if (mxv - mn < 0.06) flat[i] = 1;
    }
    // closing (dilate then erode by 1px) to remove speckle
    const dil = new Uint8Array(W * H), ero = new Uint8Array(W * H);
    for (let y = 1; y < H - 1; y++) for (let x = 1; x < W - 1; x++) {
      let a = 0; for (let dy = -1; dy <= 1; dy++) for (let dx = -1; dx <= 1; dx++) a |= flat[(y + dy) * W + x + dx];
      dil[y * W + x] = a;
    }
    for (let y = 1; y < H - 1; y++) for (let x = 1; x < W - 1; x++) {
      let a = 1; for (let dy = -1; dy <= 1; dy++) for (let dx = -1; dx <= 1; dx++) a &= dil[(y + dy) * W + x + dx];
      ero[y * W + x] = a;
    }
    let nFlat = 0, nNE = 0;
    for (let i = 0; i < W * H; i++) { nFlat += ero[i]; nNE += lakeMask[i] > 127 ? 1 : 0; }
    console.log("  lake px DEM", nFlat, "NE", nNE);
    for (let i = 0; i < W * H; i++) lakeMask[i] = ero[i] ? 255 : 0;
  }

  ctx.fillStyle = "#000"; ctx.fillRect(0, 0, W, H);
  drawPolys(polysOf(CH), "#fff");
  img = ctx.getImageData(0, 0, W, H).data;
  const chMask = new Uint8Array(W * H);
  for (let i = 0; i < W * H; i++) chMask[i] = img[i * 4] > 127 ? 1 : 0;

  // Flatten lakes in elevation: set to local lake surface (min over lake neighbourhood handled by data) -> keep as is
  // signed distance of CH (metres, mercator-ground)
  const inside = edt(chMask.map((v) => (v ? 0 : 1)), W, H); // distance to nearest inside (for outside px)
  const outside = edt(chMask, W, H); // distance to nearest outside... (mask true = zero)
  // outside: g=0 where mask==1 -> distance of px to nearest mask(1) px => for outside pixels
  // inside2: mask==0 => zero -> for inside pixels distance to nearest outside
  const sdf = new Float32Array(W * H);
  for (let i = 0; i < W * H; i++) {
    const dOutPx = Math.sqrt(outside[i]); // distance to nearest inside pixel (0 when inside)
    const dInPx = Math.sqrt(inside[i]); // distance to nearest outside pixel (0 when outside)
    sdf[i] = chMask[i] ? -dInPx * realMpp : dOutPx * realMpp; // negative inside
  }

  // albedo
  const rgb = Buffer.alloc(W * H * 3);
  const lx = -0.55, ly = 0.65, lz = 0.52; // light from NW above
  const ll = Math.hypot(lx, ly, lz);
  const L = [lx / ll, ly / ll, lz / ll];
  const exag = P.id === "eu" ? 2.2 : 1.8;
  const noiseScale = 1 / (P.id === "eu" ? 22 : P.id === "ch" ? 40 : 90);
  const clamp01 = (v) => Math.max(0, Math.min(1, v));
  const mix = (a, b, t) => a + (b - a) * t;
  for (let y = 0; y < H; y++) {
    for (let x = 0; x < W; x++) {
      const i = y * W + x;
      const e = elev[i];
      const xl = elev[y * W + Math.max(0, x - 1)], xr = elev[y * W + Math.min(W - 1, x + 1)];
      const yu = elev[Math.max(0, y - 1) * W + x], yd = elev[Math.min(H - 1, y + 1) * W + x];
      const dzdx = (xr - xl) / (2 * realMpp), dzdy = (yd - yu) / (2 * realMpp);
      let nx = -dzdx * exag, ny = dzdy * exag, nz = 1;
      const nl = Math.hypot(nx, ny, nz); nx /= nl; ny /= nl; nz /= nl;
      const shade = clamp01(nx * L[0] + ny * L[1] + nz * L[2]);
      const slope = Math.atan(Math.hypot(dzdx, dzdy)) * (180 / Math.PI);
      const n = fbm(x * noiseScale, y * noiseScale);
      let r, g, b;
      const lake = lakeMask[i] > 127;
      if (e <= 1 && !lake && P.id === "eu") {
        // sea with depth shading (bathymetry in terrarium)
        const d = clamp01(-e / 2200);
        r = mix(60, 10, Math.sqrt(d)); g = mix(165, 55, Math.sqrt(d)); b = mix(200, 110, Math.sqrt(d));
        const bmx = [bm[i * 3], bm[i * 3 + 1], bm[i * 3 + 2]];
        r = mix(r, bmx[0] * 0.9, 0.18); g = mix(g, bmx[1] * 0.95, 0.18); b = mix(b, bmx[2] * 1.05, 0.18);
        rgb[i * 3] = r; rgb[i * 3 + 1] = g; rgb[i * 3 + 2] = b;
        continue;
      }
      if (lake) {
        const t = clamp01(n);
        r = mix(30, 52, t); g = mix(138, 168, t); b = mix(168, 190, t);
        const sh = 0.9 + 0.15 * shade;
        rgb[i * 3] = r * sh; rgb[i * 3 + 1] = g * sh; rgb[i * 3 + 2] = b * sh;
        continue;
      }
      // land hypsometric
      const stops = [
        [0, [118, 150, 74]], [350, [100, 140, 66]], [800, [78, 120, 58]], [1300, [58, 98, 52]],
        [1750, [96, 118, 70]], [2150, [142, 138, 92]], [2550, [150, 140, 126]], [3000, [168, 162, 156]],
      ];
      let c = stops[stops.length - 1][1];
      for (let s = 0; s < stops.length - 1; s++) {
        if (e < stops[s + 1][0]) {
          const t = (e - stops[s][0]) / (stops[s + 1][0] - stops[s][0]);
          c = [mix(stops[s][1][0], stops[s + 1][1][0], t), mix(stops[s][1][1], stops[s + 1][1][1], t), mix(stops[s][1][2], stops[s + 1][1][2], t)];
          break;
        }
      }
      r = c[0]; g = c[1]; b = c[2];
      // fields/patchwork at low alt
      if (e < 1000) {
        const f = fbm(x * noiseScale * 3.2 + 40, y * noiseScale * 3.2) ;
        const t = clamp01((f - 0.35) * 3);
        r = mix(r, 156, t * 0.35); g = mix(g, 168, t * 0.35); b = mix(b, 84, t * 0.35);
      }
      // rock on steep slopes
      const rockT = clamp01((slope - 28) / 18) * clamp01((e - 700) / 900);
      r = mix(r, 132, rockT); g = mix(g, 124, rockT); b = mix(b, 116, rockT);
      // snow
      const snowLine = 2550 + (n - 0.5) * 380;
      const snowT = clamp01((e - snowLine) / 220) * clamp01(1 - (slope - 38) / 22);
      r = mix(r, 244, snowT); g = mix(g, 247, snowT); b = mix(b, 252, snowT);
      // colour variation
      const v = 0.88 + n * 0.28;
      r *= v; g *= v; b *= v;
      // blue marble blend
      const bw = P.id === "eu" ? 0.38 : P.id === "ch" ? 0.22 : 0.16;
      r = mix(r, bm[i * 3] * 1.05, bw); g = mix(g, bm[i * 3 + 1] * 1.05, bw); b = mix(b, bm[i * 3 + 2] * 1.05, bw);
      // shading
      const sh = 0.42 + 0.95 * shade;
      r *= sh; g *= sh; b *= sh;
      rgb[i * 3] = Math.min(255, r); rgb[i * 3 + 1] = Math.min(255, g); rgb[i * 3 + 2] = Math.min(255, b);
    }
  }
  await sharp(rgb, { raw: { width: W, height: H, channels: 3 } }).modulate({ saturation: 1.18, brightness: 1.02 }).jpeg({ quality: 90 }).toFile(path.join(OUT, `${P.id}_albedo.jpg`));

  // height as int16 (metres*4) little-endian bin
  const hb = Buffer.alloc(W * H * 2);
  for (let i = 0; i < W * H; i++) hb.writeInt16LE(Math.max(-32768, Math.min(32767, Math.round(elev[i] * 4))), i * 2);
  fs.writeFileSync(path.join(OUT, `${P.id}_height.bin`), hb);

  // sdf png: R = signed distance mapped [-12km,+12km]; G = lake mask
  const SD = 12000;
  const sdfPng = Buffer.alloc(W * H * 3);
  for (let i = 0; i < W * H; i++) {
    sdfPng[i * 3] = Math.max(0, Math.min(255, Math.round((sdf[i] / SD) * 127.5 + 127.5)));
    sdfPng[i * 3 + 1] = lakeMask[i];
    sdfPng[i * 3 + 2] = 0;
  }
  await sharp(sdfPng, { raw: { width: W, height: H, channels: 3 } }).png({ compressionLevel: 6 }).toFile(path.join(OUT, `${P.id}_sdf.png`));

  const elevMax = elev.reduce((a, b) => Math.max(a, b), -1e9);
  meta[P.id] = { bbox: P.bbox, w: W, h: H, x0: X0, x1: X1, y0: Y0, y1: Y1, sdfRange: SD, elevMax: Math.round(elevMax), realMpp };
  if (P.id === "ch") chHeightForLines = { elev, W, H, X0, X1, Y0, Y1 };
  console.log("  done", W, H, "elevMax", elevMax);
}

// ---------- borders (coloured per neighbour) — from the OFFICIAL swisstopo outline ----------
const KMX = Math.cos((47 * Math.PI) / 180) * 111.32, KMY = 110.57;
const kmDist = (a, b) => Math.hypot((a[0] - b[0]) * KMX, (a[1] - b[1]) * KMY);
const inBox = (p) => p[0] > 5.4 && p[0] < 11.0 && p[1] > 45.5 && p[1] < 48.4;
const segsOf = (feat) => {
  const out = [];
  for (const poly of polysOf(feat)) for (const ring of poly) for (let i = 0; i < ring.length - 1; i++) if (inBox(ring[i]) || inBox(ring[i + 1])) out.push([ring[i], ring[i + 1]]);
  return out;
};
const nbSegs = { FR: segsOf(byName("France")), DE: segsOf(byName("Germany")), IT: segsOf(byName("Italy")), AT: segsOf(byName("Austria")), LI: segsOf({ geometry: officialLI.geometry }) };
const ptSeg = (p, a, b) => {
  const ax = (a[0] - p[0]) * KMX, ay = (a[1] - p[1]) * KMY, bx = (b[0] - p[0]) * KMX, by = (b[1] - p[1]) * KMY;
  const dx = bx - ax, dy = by - ay, l2 = dx * dx + dy * dy;
  let t = l2 ? -(ax * dx + ay * dy) / l2 : 0; t = Math.max(0, Math.min(1, t));
  return Math.hypot(ax + t * dx, ay + t * dy);
};
const resample = (ring, step) => {
  const out = [ring[0]];
  let last = ring[0];
  for (let i = 1; i < ring.length; i++) if (kmDist(ring[i], last) >= step) { out.push(ring[i]); last = ring[i]; }
  if (out[out.length - 1] !== ring[ring.length - 1]) out.push(ring[ring.length - 1]);
  return out;
};
const chPoly = polysOf(CH)[0]; // [outer, hole1, hole2]
const outerRing = chPoly[0];
const classify = (pts) => pts.map((p) => {
  let best = null, bd = 1e9;
  for (const [code, segs] of Object.entries(nbSegs)) for (const [a, b] of segs) { const d = ptSeg(p, a, b); if (d < bd) { bd = d; best = code; } }
  return best;
});
const smooth = (arr, w) => arr.map((_, i) => {
  const cnt = {};
  for (let k = -w; k <= w; k++) { const c = arr[(i + k + arr.length) % arr.length]; cnt[c] = (cnt[c] || 0) + 1; }
  return Object.entries(cnt).sort((a, b) => b[1] - a[1])[0][0];
});
const mkRuns = (ring, step, forceCode) => {
  const dens = resample(ring, step);
  const lab = forceCode ? dens.map(() => forceCode) : smooth(classify(dens), 4);
  let st = lab.findIndex((c, i) => c !== lab[(i - 1 + lab.length) % lab.length]);
  if (st < 0) st = 0;
  const runs = [];
  let cur = null;
  for (let k = 0; k < dens.length; k++) {
    const i = (st + k) % dens.length;
    if (!cur || cur.code !== lab[i]) { cur = { code: lab[i], pts: [] }; runs.push(cur); }
    cur.pts.push(dens[i]);
  }
  for (let r = 0; r < runs.length; r++) runs[r].pts.push(runs[(r + 1) % runs.length].pts[0]);
  return runs;
};
const runs = mkRuns(outerRing, 0.45, null);
// enclaves: Büsingen (DE) and Campione d'Italia (IT) are holes of the official Swiss polygon
const holeRuns = chPoly.slice(1).map((h) => {
  const lab = classify([h[0], h[Math.floor(h.length / 2)]]);
  return mkRuns(h, 0.25, lab[0])[0];
});
const hs = chHeightForLines;
const sampleH = (lon, lat) => {
  const px = ((mx(lon) - hs.X0) / (hs.X1 - hs.X0)) * hs.W, py = ((hs.Y1 - my(lat)) / (hs.Y1 - hs.Y0)) * hs.H;
  const x = Math.max(0, Math.min(hs.W - 2, Math.floor(px))), y = Math.max(0, Math.min(hs.H - 2, Math.floor(py)));
  const tx = px - x, ty = py - y;
  const e = hs.elev;
  return (e[y * hs.W + x] * (1 - tx) + e[y * hs.W + x + 1] * tx) * (1 - ty) + (e[(y + 1) * hs.W + x] * (1 - tx) + e[(y + 1) * hs.W + x + 1] * tx) * ty;
};
const borders = [...runs, ...holeRuns].map((r) => ({ code: r.code, pts: r.pts.map(([lo, la]) => [mx(lo), my(la), sampleH(lo, la), lo, la]) }));
console.log("border runs", borders.map((b) => `${b.code}:${b.pts.length}`).join(" "));

// ---------- POIs (real WGS84 city centres; verified against the official outline + swisstopo gazetteer) ----------
const pois = {
  zurich: [8.5417, 47.3769, "ZÜRICH"],
  bern: [7.4474, 46.9481, "BERN"],
  geneva: [6.1432, 46.2044, "GENÈVE"],
  lugano: [8.9511, 46.0037, "LUGANO"],
  basel: [7.5886, 47.5596, "BASEL"],
  lucerne: [8.3093, 47.0502, "LUZERN"],
  interlaken: [7.8632, 46.6863, "INTERLAKEN"],
  engelberg: [8.4064, 46.8204, "ENGELBERG"],
  titlis: [8.4378, 46.7720, "MT TITLIS"],
  spiez: [7.6741, 46.6889, "SPIEZ"],
  thun: [7.628, 46.758, "THUN"],
  lauterbrunnen: [7.9077, 46.5935, "LAUTERBRUNNEN"],
};
const inRing = (pt, ring) => { let c = false; for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) { const [xi, yi] = ring[i], [xj, yj] = ring[j]; if ((yi > pt[1]) !== (yj > pt[1]) && pt[0] < ((xj - xi) * (pt[1] - yi)) / (yj - yi) + xi) c = !c; } return c; };
const insideCH = (pt) => inRing(pt, chPoly[0]) && !chPoly.slice(1).some((h) => inRing(pt, h));
const borderDist = (pt) => { let d = 1e9; for (let i = 0; i < chPoly[0].length - 1; i += 1) { const a = chPoly[0][i], b = chPoly[0][i + 1]; if (Math.abs(a[0] - pt[0]) > 0.3 && Math.abs(b[0] - pt[0]) > 0.3) continue; d = Math.min(d, ptSeg(pt, a, b)); } return d; };
const poi = {};
const check = {};
for (const [k, [lo, la, label]] of Object.entries(pois)) {
  poi[k] = { lon: lo, lat: la, label, x: mx(lo), y: my(la), h: sampleH(lo, la) };
  check[k] = { lon: lo, lat: la, insideSwitzerland: insideCH([lo, la]), distanceToNearestBorderKm: +borderDist([lo, la]).toFixed(2) };
}
console.log("CITY CHECK vs official outline:\n" + Object.entries(check).map(([k, v]) => `  ${k.padEnd(14)} inside=${v.insideSwitzerland}  border=${v.distanceToNearestBorderKm} km`).join("\n"));
fs.writeFileSync(path.join(OUT, "geo_check.json"), JSON.stringify({ source: "swisstopo swissBOUNDARIES3D (api3.geo.admin.ch, layer ch.swisstopo.swissboundaries3d-land-flaeche.fill, id=CH)", outerRingPoints: chPoly[0].length, holes: chPoly.length - 1, cities: check }, null, 2));

// rivers in CH region for subtle blue lines
const riv = [];
for (const f of rivers.features) {
  if (!f.geometry) continue;
  const lines = f.geometry.type === "LineString" ? [f.geometry.coordinates] : f.geometry.coordinates;
  for (const ln of lines) {
    const pts = ln.filter((p) => p[0] > 5.4 && p[0] < 11 && p[1] > 45.6 && p[1] < 48.1);
    if (pts.length > 2) riv.push(pts.map(([lo, la]) => [mx(lo), my(la), sampleH(lo, la) + 8]));
  }
}

fs.writeFileSync(path.join(OUT, "meta.json"), JSON.stringify({ patches: meta, borders, poi, rivers: riv, merc: { R } }));
console.log("baked ->", OUT);
