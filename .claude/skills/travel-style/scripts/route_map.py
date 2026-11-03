"""Route map: Natural Earth 10m countries, a flight from ORIGIN to pin A, then a ground trail A -> VIA -> B.
Worked example: KLIA -> Abu Dhabi flight, Abu Dhabi -> Dubai trail.
Writes assets/js/routemap.js (SVG markup + camera + screen positions) and checks every point is inside its country.
Usage: python3 -I route_map.py <ne_countries.geojson> <out_js>
For another trip, edit PTS (lon, lat, ISO A3 from Natural Earth's ADM0_A3) and, if needed, the overview camera (X0, Y0, U0)."""
import json, math, sys

NE, OUT = sys.argv[1], sys.argv[2]
LAT0 = 15.0
KX = math.cos(math.radians(LAT0)) * 100
W = lambda lon, lat: (lon * KX, -lat * 100)          # world units

# Roles: origin = flight start, a = pin A (first stop), via = trail midpoint, b = pin B (final stop). Verify coordinates on OpenStreetMap.
PTS = {
    "origin": (101.7074480, 2.7448046, "MYS"),   # KLIA
    "a":      (54.3773438, 24.4538840, "ARE"),   # Abu Dhabi
    "via":    (54.9400, 24.7600, "ARE"),         # inland, between the two cities
    "b":      (55.2744, 25.1972, "ARE"),         # Dubai
}
ORIGIN_A3, DEST_A3 = PTS["origin"][2], PTS["b"][2]

# camera 0: overview (destination left, Malaysia right), camera 1: close-up on the A -> B trail
U0 = 6.9                                              # units per px
X0 = 30.2 * KX
Y0 = -32.0 * 100 - 150 * U0                           # lat 32 lands at y=150 px
mid = ((PTS["a"][0] + PTS["b"][0]) / 2, (PTS["a"][1] + PTS["b"][1]) / 2)
SEP_PX = 470
U1 = math.hypot((PTS["b"][0] - PTS["a"][0]) * KX, (PTS["b"][1] - PTS["a"][1]) * 100) / SEP_PX
MX, MY = W(*mid)
X1 = MX - 540 * U1
Y1 = MY - 420 * U1
CAM0 = [X0, Y0, 1080 * U0, 1920 * U0]
CAM1 = [X1, Y1, 1080 * U1, 1920 * U1]

def px(cam, lon, lat):
    x, y = W(lon, lat)
    u = cam[2] / 1080
    return [round((x - cam[0]) / u, 1), round((y - cam[1]) / u, 1)]

def inside(poly_rings, x, y):
    c = False
    for ring in poly_rings:
        n = len(ring)
        for i in range(n):
            x1, y1 = ring[i]; x2, y2 = ring[(i + 1) % n]
            if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
                c = not c
    return c

def dp(pts, tol):
    if len(pts) < 3:
        return pts
    (ax, ay), (bx, by) = pts[0], pts[-1]
    dx, dy = bx - ax, by - ay
    L = math.hypot(dx, dy) or 1e-9
    imax, dmax = 0, -1
    for i in range(1, len(pts) - 1):
        d = abs(dy * pts[i][0] - dx * pts[i][1] + bx * ay - by * ax) / L
        if d > dmax:
            imax, dmax = i, d
    if dmax > tol:
        return dp(pts[:imax + 1], tol)[:-1] + dp(pts[imax:], tol)
    return [pts[0], pts[-1]]

sys.setrecursionlimit(100000)
feats = json.load(open(NE))["features"]
BB = (24, -14, 125, 44)
paths = {"land": [], ORIGIN_A3: [], DEST_A3: []}
polys = {}
for f in feats:
    a3 = f["properties"]["ADM0_A3"]
    g = f["geometry"]
    ps = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
    keep = []
    for poly in ps:
        xs = [p[0] for p in poly[0]]; ys = [p[1] for p in poly[0]]
        if max(xs) < BB[0] or min(xs) > BB[2] or max(ys) < BB[1] or min(ys) > BB[3]:
            continue
        keep.append(poly)
    if not keep:
        continue
    if a3 in (ORIGIN_A3, DEST_A3):
        polys[a3] = [poly[0] for poly in keep]
    tol = 0.004 if a3 in (ORIGIN_A3, DEST_A3) else 0.03
    d = []
    for poly in keep:
        for ring in poly:
            h = len(ring) // 2
            r = dp(ring[:h + 1], tol)[:-1] + dp(ring[h:], tol)   # closed ring: simplify two open halves
            if len(r) < 4:
                continue
            d.append("M" + "L".join(f"{W(x, y)[0]:.1f},{W(x, y)[1]:.1f}" for x, y in r) + "Z")
    paths[a3 if a3 in (ORIGIN_A3, DEST_A3) else "land"].append("".join(d))

# inside-border check
ok = True
for k, (lon, lat, a3) in PTS.items():
    ins = any(inside([ring], lon, lat) for ring in polys[a3])
    print(f"{k:7s} {lat:.4f},{lon:.4f} in {a3}: inside={ins}  cam0={px(CAM0, lon, lat)} cam1={px(CAM1, lon, lat)}")
    ok &= ins
if not ok:
    sys.exit("point outside its country")

NS = 'vector-effect="non-scaling-stroke"'
svg = (f'<svg id="routemap" class="abs" viewBox="{" ".join(f"{v:.2f}" for v in CAM0)}" width="1080" height="1920" preserveAspectRatio="none">'
       f'<defs><linearGradient id="gold" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffe07a"/><stop offset="1" stop-color="#f4b400"/></linearGradient></defs>'
       f'<rect x="-100000" y="-100000" width="200000" height="200000" fill="#0a1a4f" opacity="0.86"/>'
       f'<path d="{"".join(paths["land"])}" fill="#22366f" stroke="#6f86c9" stroke-opacity="0.55" stroke-width="1.2" {NS}/>'
       f'<path id="map-dest" d="{"".join(paths[DEST_A3])}" fill="url(#gold)" stroke="#ffffff" stroke-width="2.6" stroke-linejoin="round" {NS}/>'
       f'<path id="map-origin" d="{"".join(paths[ORIGIN_A3])}" fill="url(#gold)" stroke="#ffffff" stroke-width="2.6" stroke-linejoin="round" {NS}/>'
       '</svg>')

# flight arc (screen px at cam0) and trail (screen px at cam1)
A = px(CAM0, *PTS["origin"][:2]); B = px(CAM0, *PTS["a"][:2])
C = [(A[0] + B[0]) / 2, min(A[1], B[1]) - 330]
tj, tb, tm = px(CAM1, *PTS["a"][:2]), px(CAM1, *PTS["via"][:2]), px(CAM1, *PTS["b"][:2])
trail = (f"M{tj[0]},{tj[1]} C{tj[0] + 70},{tj[1] + 40} {tb[0] - 80},{tb[1] - 6} {tb[0]},{tb[1]} "
         f"S{tm[0] - 70},{tm[1] + 10} {tm[0]},{tm[1]}")
out = {
    "svg": svg, "cam0": CAM0, "cam1": CAM1, "arc": {"a": A, "c": C, "b": B},
    "trail": trail, "pins": {"a": tj, "b": tm, "via": tb},
    "labels0": {"dest": px(CAM0, 54.0, 23.2), "origin": px(CAM0, 102.0, 5.2), "origin_pt": A},
}
open(OUT, "w").write("window.ROUTEMAP = " + json.dumps(out) + ";\n")
print("cam0", [round(v, 1) for v in CAM0], "cam1", [round(v, 2) for v in CAM1], "zoom", round(U0 / U1, 1), "svg KB", len(svg) // 1024)
