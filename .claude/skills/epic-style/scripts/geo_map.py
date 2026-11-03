"""Accurate flat vector map with an A -> B trail (official boundary + lakes + verified points).

Commands
  python3 geo_map.py fetch-ch <geo_dir>
      Downloads the official swisstopo outline (swissBOUNDARIES3D) -> boundary.json and all Swiss lakes
      (BAFU VECTOR25, ch.bafu.vec25-seen) -> lakes.json. For another country, save that country's OFFICIAL
      boundary as GeoJSON (Polygon/MultiPolygon) yourself; lakes are optional.
  python3 geo_map.py gazetteer "<name>"
      swisstopo gazetteer lookup (Switzerland only). Prefer the municipality (gg25) or "Ort" hit, never guess.
  python3 geo_map.py build <map.json>
      map.json:
      {
        "boundary": "geo/boundary.json", "lakes": "geo/lakes.json",
        "points": [                                   # in trail order; every point must be verified
          {"id": "pin-a", "name": "Luzern",    "lon": 8.305033, "lat": 47.051125, "pin": "pa", "side": "r"},
          {"name": "Stans",                    "lon": 8.362702, "lat": 46.962468},             # via point, no pin
          {"id": "pin-e", "name": "Engelberg", "lon": 8.405006, "lat": 46.821465, "pin": "pe", "side": "l"},
          {"name": "Trubsee",                  "lon": 8.399545, "lat": 46.794031},
          {"id": "pin-b", "name": "Titlis",    "lon": 8.424844, "lat": 46.770126, "pin": "pb", "side": "r"}
        ],
        "zoom": 4.6, "center": [540, 560],          # where the route midpoint lands on the 1080x1920 frame
        "map_width": 900, "map_origin": [90, 330]   # full-country view before the zoom
      }
      Writes <map.json stem>_built.json, checks every point is inside the boundary (exit 1 if not).
  python3 geo_map.py inject <built.json> <project_dir>
      Replaces <svg id="chmap">…</svg> and the .pin divs inside #bkmap in index.html, and the #mapcam zoom
      numbers in assets/js/anim.js. Pin labels show the "name" field.
"""
import json
import math
import re
import subprocess
import sys

sys.setrecursionlimit(100000)
API = "https://api3.geo.admin.ch/rest/services/api"


def curl(url, params, out=None):
    cmd = ["curl", "-s", "-G", url] + sum([["--data-urlencode", f"{k}={v}"] for k, v in params.items()], [])
    r = subprocess.run(cmd + (["-o", out] if out else []), capture_output=True, text=True, check=True)
    return r.stdout


def fetch_ch(geo_dir):
    curl(f"{API}/MapServer/find", {"layer": "ch.swisstopo.swissboundaries3d-land-flaeche.fill", "searchText": "CH",
                                   "searchField": "id", "returnGeometry": "true", "sr": "4326", "geometryFormat": "geojson"},
         f"{geo_dir}/boundary_raw.json")
    g = json.load(open(f"{geo_dir}/boundary_raw.json"))["results"][0]["geometry"]
    json.dump(g, open(f"{geo_dir}/boundary.json", "w"))
    ext = "5.9,45.8,10.5,47.85"
    curl(f"{API}/MapServer/identify", {"geometryType": "esriGeometryEnvelope", "geometry": ext, "sr": "4326",
                                       "layers": "all:ch.bafu.vec25-seen", "tolerance": "0", "returnGeometry": "true",
                                       "geometryFormat": "geojson", "imageDisplay": "1000,1000,96", "mapExtent": ext,
                                       "limit": "200"}, f"{geo_dir}/lakes_raw.json")
    lakes = [r["geometry"] for r in json.load(open(f"{geo_dir}/lakes_raw.json"))["results"]]
    json.dump(lakes, open(f"{geo_dir}/lakes.json", "w"))
    print("boundary.json + lakes.json:", len(lakes), "lakes")


def gazetteer(name):
    out = curl(f"{API}/SearchServer", {"searchText": name, "type": "locations", "origins": "gg25,gazetteer",
                                       "sr": "4326", "limit": "6"})
    for r in json.loads(out)["results"]:
        a = r["attrs"]
        print(re.sub("<[^>]+>", "", a["label"]), "|", a.get("origin"), "| lat", a["lat"], "lon", a["lon"])


def rings_of(g):
    polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
    return [p[0] for p in polys]


def dp(pts, eps):
    (x1, y1), (x2, y2) = pts[0], pts[-1]
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy) or 1e-9
    dm, ix = 0, 0
    for i in range(1, len(pts) - 1):
        x, y = pts[i]
        dd = abs(dy * x - dx * y + x2 * y1 - y2 * x1) / L
        if dd > dm:
            dm, ix = dd, i
    if dm > eps:
        return dp(pts[: ix + 1], eps)[:-1] + dp(pts[ix:], eps)
    return [pts[0], pts[-1]]


def simplify_ring(ring, eps):  # closed rings: split in two so the first/last point is not degenerate
    h = len(ring) // 2
    return dp(ring[: h + 1], eps)[:-1] + dp(ring[h:], eps)


def path_of(pts):
    return "M" + " L".join(f"{x:.2f},{y:.2f}" for x, y in pts) + "Z"


def inside(lon, lat, ring):
    ins, j = False, len(ring) - 1
    for i in range(len(ring)):
        xi, yi = ring[i][:2]
        xj, yj = ring[j][:2]
        if (yi > lat) != (yj > lat) and lon < (xj - xi) * (lat - yi) / (yj - yi) + xi:
            ins = not ins
        j = i
    return ins


def catmull(seq):
    ext = [seq[0]] + seq + [seq[-1]]
    d = f"M{seq[0][0]:.1f},{seq[0][1]:.1f}"
    for i in range(1, len(ext) - 2):
        p0, p1, p2, p3 = ext[i - 1], ext[i], ext[i + 1], ext[i + 2]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f" C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}"
    return d


def build(cfg_path):
    cfg = json.load(open(cfg_path))
    rings = rings_of(json.load(open(cfg["boundary"])))
    allp = [p for r in rings for p in r]
    lat0 = (min(p[1] for p in allp) + max(p[1] for p in allp)) / 2
    c = math.cos(math.radians(lat0))
    minx = min(p[0] for p in allp) * c
    maxx = max(p[0] for p in allp) * c
    maxy = max(p[1] for p in allp)
    W = cfg.get("map_width", 900)
    s = W / (maxx - minx)
    ox, oy = cfg.get("map_origin", [90, 330])
    proj = lambda lon, lat: ((lon * c - minx) * s, (maxy - lat) * s)  # map space (0..W)
    outline = " ".join(path_of(simplify_ring([proj(*p[:2]) for p in r], 0.5)) for r in rings if len(r) > 20)
    lakes = []
    if cfg.get("lakes"):
        for g in json.load(open(cfg["lakes"])):
            for r in rings_of(g):
                pr = [proj(*p[:2]) for p in r]
                a = abs(sum(pr[i][0] * pr[i - 1][1] - pr[i - 1][0] * pr[i][1] for i in range(len(pr)))) / 2
                if a >= 1.5:  # smaller ponds are invisible even zoomed in
                    lakes.append(path_of(simplify_ring(pr, 0.08)))
    ok = True
    for p in cfg["points"]:
        ins = any(inside(p["lon"], p["lat"], r) for r in rings)
        print(f'{p["name"]:<14} inside={ins}')
        ok &= ins
    if not ok:
        sys.exit("A point is outside the official boundary: re-check its coordinates before rendering.")
    mp = [(proj(p["lon"], p["lat"])[0] + ox, proj(p["lon"], p["lat"])[1] + oy) for p in cfg["points"]]
    Z = cfg.get("zoom", 4.6)
    C = cfg.get("center", [540, 560])
    mid = ((mp[0][0] + mp[-1][0]) / 2, (mp[0][1] + mp[-1][1]) / 2)
    scr = [(C[0] + Z * (x - mid[0]), C[1] + Z * (y - mid[1])) for x, y in mp]
    out = {"outline": outline, "lakes": " ".join(lakes), "origin": [ox, oy], "zoom": Z,
           "cam": [C[0] - Z * mid[0], C[1] - Z * mid[1]], "trail": catmull(scr),
           "pins": [dict(p, x=round(x), y=round(y)) for p, (x, y) in zip(cfg["points"], scr) if p.get("id")]}
    dst = cfg_path.rsplit(".", 1)[0] + "_built.json"
    json.dump(out, open(dst, "w"))
    for p in out["pins"]:
        print("pin", p["id"], p["name"], p["x"], p["y"])
    print("->", dst)


def inject(built_path, proj_dir):
    b = json.load(open(built_path))
    ox, oy = b["origin"]
    svg = f'''<svg id="chmap" class="abs" viewBox="0 0 1080 1920" width="1080" height="1920">
            <g id="mapcam"><g transform="translate({ox},{oy})">
              <path id="ch-fill" d="{b["outline"]}" fill="#ffffff" fill-opacity="0.93" stroke="none"/>
              <path id="ch-lakes" d="{b["lakes"]}" fill="#9fd0ea" stroke="#5ea9d1" stroke-width="1" vector-effect="non-scaling-stroke"/>
              <path id="ch-line" d="{b["outline"]}" fill="none" stroke="#b3121e" stroke-width="4" stroke-linejoin="round" vector-effect="non-scaling-stroke" pathLength="1" stroke-dasharray="1 1"/>
            </g></g>
            <path id="trail-case" d="{b["trail"]}" fill="none" stroke="#ffffff" stroke-width="16" stroke-linecap="round" stroke-linejoin="round" pathLength="1" stroke-dasharray="1 1"/>
            <path id="trail" d="{b["trail"]}" fill="none" stroke="#b3121e" stroke-width="8" stroke-linecap="round" stroke-linejoin="round" pathLength="1" stroke-dasharray="1 1"/>
          </svg>'''
    pins = "\n          ".join(
        f'<div class="pin {p.get("pin", "pa")} {p.get("side", "r")}" id="{p["id"]}" style="left:{p["x"]}px;top:{p["y"]}px"><i></i><span>{p["name"]}</span></div>'
        for p in b["pins"])
    ip = f"{proj_dir}/index.html"
    s = open(ip).read()
    s, n1 = re.subn(r'<svg id="chmap".*?</svg>', lambda m: svg, s, flags=re.S)
    s, n2 = re.subn(r'(</svg>\s*)(?:<div class="pin[^>]*><i></i><span>[^<]*</span></div>\s*)+', lambda m: m.group(1) + pins + "\n        ", s)
    open(ip, "w").write(s)
    ap = f"{proj_dir}/assets/js/anim.js"
    a = open(ap).read()
    a, n3 = re.subn(r'(tl\.fromTo\("#mapcam", \{ x: 0, y: 0, scale: 1 \}, \{ )x: -?[\d.]+, y: -?[\d.]+, scale: [\d.]+',
                    lambda m: f'{m.group(1)}x: {b["cam"][0]:.2f}, y: {b["cam"][1]:.2f}, scale: {b["zoom"]}', a)
    open(ap, "w").write(a)
    print("svg", n1, "pins", n2, "zoom", n3, "(each should be 1); pin ids used:", [p["id"] for p in b["pins"]])


if __name__ == "__main__":
    cmd = sys.argv[1]
    {"fetch-ch": lambda: fetch_ch(sys.argv[2]), "gazetteer": lambda: gazetteer(sys.argv[2]),
     "build": lambda: build(sys.argv[2]), "inject": lambda: inject(sys.argv[2], sys.argv[3])}[cmd]()
