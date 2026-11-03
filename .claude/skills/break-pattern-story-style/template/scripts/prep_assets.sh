#!/bin/zsh
# Stage the assets the master timeline expects into hf/assets/.
# Usage (from the project root):
#   CHAR="<folder with 4 cut-out PNGs>" FOOT="<folder of raw .mov talking-head clips>" CS="<before/after demo mp4>" \
#   LOGO_ICON="<student's square logo png>" LOGO_WORDMARK="<student's wide logo png>" \
#   CARDS="<folder with 3 product screenshots, sorted: zero / vault / belajar slots>" zsh scripts/prep_assets.sh
# The cut-outs must be named 01_*Shoot*.png, 02_*Serabut*.png, 03_*Penat*.png and 04_*Presenter*.png (true alpha, full body).
# Logos and product cards always come from the student. When one is missing, a neutral "LOGO" / "PRODUK" placeholder is written.
set -e
A=hf/assets
mkdir -p $A/char $A/footage $A/ui $A/video $A/audio
cp "$CHAR"/01_*.png $A/char/shoot.png
cp "$CHAR"/02_*.png $A/char/serabut.png
cp "$CHAR"/03_*.png $A/char/penat.png
cp "$CHAR"/04_*.png $A/char/presenter.png
[ -n "$CS" ] && cp "$CS" $A/video/casestudy.mp4

/usr/bin/python3 - "$LOGO_ICON" "$LOGO_WORDMARK" "$CARDS" <<'EOF'
import sys, glob, os
from PIL import Image, ImageDraw, ImageFont
icon, wordmark, cards = sys.argv[1:4]
def placeholder(path, w, h, label):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([8, 8, w - 8, h - 8], radius=min(w, h) // 8, outline=(242, 238, 230, 255), width=8)
    try: f = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Black.ttf", h // 4)
    except Exception: f = ImageFont.load_default()
    tw = d.textlength(label, font=f); d.text(((w - tw) / 2, h / 2 - h // 7), label, font=f, fill=(242, 238, 230, 255))
    im.save(path)
def stage(src, dst, w, h, label):
    if src and os.path.exists(src): Image.open(src).convert("RGBA").save(dst)
    else: placeholder(dst, w, h, label); print("placeholder:", dst)
stage(icon, "hf/assets/ui/brand_icon.png", 600, 600, "LOGO")
stage(wordmark, "hf/assets/ui/brand_wordmark.png", 1080, 640, "LOGO")
shots = sorted(glob.glob(os.path.join(cards, "*"))) if cards else []
for k, name in enumerate(["card_zero", "card_vault", "card_belajar"]):
    stage(shots[k] if k < len(shots) else "", f"hf/assets/ui/{name}.png", 321, 562, "PRODUK")
EOF

# 24-30 "footage cards": stills from the student's own raw clips (6 per clip at spread-out times)
i=0
for f in "$FOOT"/*.mov; do
  d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$f")
  for k in 1 2 3 4 5 6; do
    i=$((i+1)); t=$(echo "$d*$k/7" | bc -l)
    ffmpeg -v error -y -ss $t -i "$f" -frames:v 1 -vf "scale=720:-2" -q:v 3 $A/footage/clip_$(printf %02d $i).jpg
  done
  [ $i -ge 30 ] && break
done
echo "footage stills: $i"
