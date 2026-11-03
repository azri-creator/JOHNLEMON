#!/usr/bin/env python3
"""Storyboard frames for a HyperFrames project.

Snapshots one still per beat from the built composition and lays them out on
numbered storyboard sheets the student can review on a phone before any MP4 is
rendered.

Usage:
  python3 storyboard.py <project_dir>               # every frame in storyboard.json
  python3 storyboard.py <project_dir> --only 3,5    # re-snapshot frames 3 and 5 only

Reads  <project_dir>/storyboard/storyboard.json
Writes <project_dir>/storyboard/frames/NN.png
       <project_dir>/storyboard/storyboard_v<version>_p<page>.jpg
       <project_dir>/storyboard/STORYBOARD.md

storyboard.json:
  {"title": "Nama projek", "version": 1,
   "frames": [{"n": 1, "t": 0.8, "line": "ayat VO", "visual": "apa yang nampak",
               "changed": false}, ...]}

Env: HF overrides the CLI (default "npx --yes hyperframes@0.8.212").
"""
import argparse, glob, json, os, re, shlex, shutil, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFont

PER_PAGE = 12
INK, MUTED, PAPER, ACCENT = (24, 26, 33), (96, 102, 115), (247, 246, 242), (255, 214, 0)


def font(size, bold=False):
    names = (["Arial Bold.ttf", "Arial-BoldMT.ttf", "DejaVuSans-Bold.ttf", "LiberationSans-Bold.ttf"] if bold
             else ["Arial.ttf", "ArialMT.ttf", "DejaVuSans.ttf", "LiberationSans-Regular.ttf"])
    dirs = ["/System/Library/Fonts/Supplemental", "/Library/Fonts", "/usr/share/fonts/truetype/dejavu",
            "/usr/share/fonts/truetype/liberation", "/usr/share/fonts/dejavu", "/usr/share/fonts"]
    for d in dirs:
        for n in names:
            p = os.path.join(d, n)
            if os.path.exists(p):
                return ImageFont.truetype(p, size)
    try:
        return ImageFont.load_default(size)
    except TypeError:
        return ImageFont.load_default()


def wrap(draw, text, fnt, width):
    lines, cur = [], ""
    for word in str(text or "").split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def stage_size(project):
    html = open(os.path.join(project, "index.html"), encoding="utf-8").read()
    w = re.search(r'data-width="(\d+)"', html)
    h = re.search(r'data-height="(\d+)"', html)
    return (int(w.group(1)), int(h.group(1))) if w and h else (1080, 1920)


def mmss(t):
    return f"{int(t // 60)}:{t % 60:04.1f}"


def snapshot(project, frames, out_dir):
    tmp = tempfile.mkdtemp(prefix="sb_")
    times = ",".join(f"{f['t']:.3f}" for f in frames)
    cmd = shlex.split(os.environ.get("HF", "npx --yes hyperframes@0.8.212")) + [
        "snapshot", project, "--at", times, "--no-end", "--keep", "-o", tmp]
    print("$", " ".join(cmd))
    subprocess.run(cmd, check=True)
    shots = []
    for p in glob.glob(os.path.join(tmp, "at-*s.png")):
        m = re.match(r"at-([\d.]+)s\.png$", os.path.basename(p))
        if m:
            shots.append((float(m.group(1)), p))
    for f in frames:
        if not shots:
            sys.exit("snapshot wrote no stills; run `npx hyperframes check` on the project")
        t, p = min(shots, key=lambda s: abs(s[0] - f["t"]))
        if abs(t - f["t"]) > 0.05:
            sys.exit(f"no still near t={f['t']} for frame {f['n']}")
        shutil.move(p, os.path.join(out_dir, f"{int(f['n']):02d}.png"))
    shutil.rmtree(tmp, ignore_errors=True)


def sheets(sb_dir, plan, size):
    w, h = size
    portrait = h > w
    cols = 4 if portrait else 3
    cell_w = 300 if portrait else 420
    cell_h = round(cell_w * h / w)
    pad, text_h, head_h = 24, 150, 96
    f_num, f_line, f_vis, f_head = font(22, True), font(19), font(16), font(34, True)
    frames = sorted(plan["frames"], key=lambda f: int(f["n"]))
    pages = [frames[i:i + PER_PAGE] for i in range(0, len(frames), PER_PAGE)]
    out = []
    for pi, page in enumerate(pages, 1):
        rows = -(-len(page) // cols)
        W = pad + cols * (cell_w + pad)
        H = head_h + rows * (cell_h + text_h + pad) + pad
        sheet = Image.new("RGB", (W, H), PAPER)
        d = ImageDraw.Draw(sheet)
        title = f"{plan.get('title', 'Storyboard')}  ·  v{plan.get('version', 1)}"
        if len(pages) > 1:
            title += f"  ·  {pi}/{len(pages)}"
        d.text((pad, 28), title, font=f_head, fill=INK)
        for i, f in enumerate(page):
            x = pad + (i % cols) * (cell_w + pad)
            y = head_h + (i // cols) * (cell_h + text_h + pad)
            path = os.path.join(sb_dir, "frames", f"{int(f['n']):02d}.png")
            if os.path.exists(path):
                im = Image.open(path).convert("RGB").resize((cell_w, cell_h), Image.LANCZOS)
                sheet.paste(im, (x, y))
            else:
                d.rectangle([x, y, x + cell_w, y + cell_h], fill=(220, 220, 220))
                d.text((x + 12, y + 12), "belum ada frame", font=f_vis, fill=MUTED)
            if f.get("changed"):
                d.rectangle([x - 5, y - 5, x + cell_w + 5, y + cell_h + 5], outline=ACCENT, width=6)
            ty = y + cell_h + 10
            tag = f"#{f['n']}  ·  {mmss(float(f['t']))}" + ("  ·  DIUBAH" if f.get("changed") else "")
            d.text((x, ty), tag, font=f_num, fill=INK)
            ty += 30
            for ln in wrap(d, f"“{f.get('line', '')}”", f_line, cell_w)[:3]:
                d.text((x, ty), ln, font=f_line, fill=INK)
                ty += 24
            for ln in wrap(d, f.get("visual", ""), f_vis, cell_w)[:2]:
                d.text((x, ty), ln, font=f_vis, fill=MUTED)
                ty += 20
        name = f"storyboard_v{plan.get('version', 1)}_p{pi}.jpg"
        sheet.save(os.path.join(sb_dir, name), quality=88)
        out.append(name)
    return out


def write_md(sb_dir, plan, pages):
    rows = ["| # | Masa | Ayat VO | Visual | Status |", "|---|---|---|---|---|"]
    for f in sorted(plan["frames"], key=lambda f: int(f["n"])):
        rows.append(f"| {f['n']} | {mmss(float(f['t']))} | {f.get('line', '')} | {f.get('visual', '')} | "
                    f"{'diubah' if f.get('changed') else 'ok'} |")
    body = [f"# {plan.get('title', 'Storyboard')} (v{plan.get('version', 1)})", ""]
    body += [f"![storyboard]({p})" for p in pages] + [""] + rows + [""]
    open(os.path.join(sb_dir, "STORYBOARD.md"), "w", encoding="utf-8").write("\n".join(body))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--only", help="comma-separated frame numbers to re-snapshot")
    a = ap.parse_args()
    project = os.path.abspath(a.project)
    sb_dir = os.path.join(project, "storyboard")
    plan = json.load(open(os.path.join(sb_dir, "storyboard.json"), encoding="utf-8"))
    os.makedirs(os.path.join(sb_dir, "frames"), exist_ok=True)
    frames = plan["frames"]
    if a.only:
        want = {int(x) for x in a.only.split(",")}
        frames = [f for f in frames if int(f["n"]) in want]
    if frames:
        snapshot(project, frames, os.path.join(sb_dir, "frames"))
    pages = sheets(sb_dir, plan, stage_size(project))
    write_md(sb_dir, plan, pages)
    for p in pages:
        print(os.path.join(sb_dir, p))


if __name__ == "__main__":
    main()
