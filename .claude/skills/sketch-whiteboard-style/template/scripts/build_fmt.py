# Write the landscape copies of hf/index.html (the 9:16 source):  hf169/ (1920x1080)  and  hf43/ (1440x1080)
import os, shutil
P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = open(f"{P}/hf/index.html").read()
for fmt, out, w, h in [("16x9", "hf169", 1920, 1080), ("4x3", "hf43", 1440, 1080)]:
    html = src
    for a, b in [
        ('const FMT = "9x16";', f'const FMT = "{fmt}";'),
        ('content="width=1080, height=1920"', f'content="width={w}, height={h}"'),
        ("--W: 1080px;\n        --H: 1920px;", f"--W: {w}px;\n        --H: {h}px;"),
        ('data-width="1080" data-height="1920"', f'data-width="{w}" data-height="{h}"'),
        ('data-resolution="portrait"', 'data-resolution="landscape"'),
    ]:
        assert html.count(a) == 1, (fmt, a)
        html = html.replace(a, b)
    os.makedirs(f"{P}/{out}/assets", exist_ok=True)
    for f in os.listdir(f"{P}/hf/assets"):
        if f.endswith((".wav", ".png")) and f in ("mix.wav", "brand_logo.png"):
            shutil.copy2(f"{P}/hf/assets/{f}", f"{P}/{out}/assets/{f}")
    for f in ("hyperframes.json", "package.json", "meta.json"):
        shutil.copy2(f"{P}/hf/{f}", f"{P}/{out}/{f}")
    open(f"{P}/{out}/index.html", "w").write(html)
    print("built", out, w, h)
