"""Colour grade shared by prep_footage.py: per-shot match, then one common look modelled on the reference
(deeper shadows, warm-natural skin, soft highlight glow/halation, subtle radial chromatic fringe, light vignette)."""

# shot boundaries in the source .mov (seconds) and per-shot balancing
SHOTS = [
    # (start, end, eq, colorbalance)
    (0.00, 6.27,  "eq=contrast=1.02:brightness=-0.005:saturation=0.96", "colorbalance=rm=-0.035:gm=0.005:bm=0.01:rs=-0.02"),
    (6.27, 14.57, "eq=contrast=1.03:brightness=-0.010:saturation=1.00", "colorbalance=rm=-0.005:bm=0.005"),
    (14.57, 20.27, "eq=contrast=1.03:brightness=-0.005:saturation=1.02", "colorbalance=rm=0.0"),
    (20.27, 29.60, "eq=contrast=1.04:brightness=-0.010:saturation=1.05", "colorbalance=rm=0.01:rh=0.005"),
    (29.60, 37.57, "eq=contrast=1.05:brightness=-0.025:saturation=1.05", "colorbalance=rm=0.01:bm=-0.005"),
    (37.57, 99.00, "eq=contrast=1.09:brightness=-0.040:saturation=1.12", "colorbalance=rm=0.025:gm=-0.005:bm=-0.025:rh=0.0:bh=-0.01"),
]

LOOK_CURVE = "curves=all='0/0 0.10/0.065 0.30/0.27 0.55/0.56 0.85/0.88 1/0.985'"
LOOK_SAT = "eq=saturation=1.06"
GLOW_OPACITY = 0.17
CA = (1.0045, 1.0022, 1.0)  # radial scale for R, G, B planes -> red/cyan fringe towards the edges


def look_chain(inp: str, out: str, w=1080, h=1920) -> str:
    """filter_complex fragment: [inp] -> [out]"""
    sr, sg, sb = CA
    def sc(s):
        W2, H2 = int(round(w * s / 2) * 2), int(round(h * s / 2) * 2)
        return f"scale={W2}:{H2}:flags=bicubic,crop={w}:{h}:(iw-{w})/2:(ih-{h})/2"
    return (
        f"[{inp}]{LOOK_CURVE},{LOOK_SAT},format=gbrp,split=2[lk0][lk1];"
        f"[lk1]curves=all='0/0 0.62/0 1/1',gblur=sigma=38,colorbalance=rh=0.08:bh=-0.04[glw];"
        f"[lk0][glw]blend=all_mode=screen:all_opacity={GLOW_OPACITY}[lk2];"
        f"[lk2]split=3[c0][c1][c2];"
        f"[c0]extractplanes=r,{sc(sr)}[pr];[c1]extractplanes=g,{sc(sg)}[pg];[c2]extractplanes=b,{sc(sb)}[pb];"
        f"[pg][pb][pr]mergeplanes=0x001020:gbrp,vignette=angle=0.32:mode=forward,format=yuv420p[{out}]"
    )
