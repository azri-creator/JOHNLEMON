#!/bin/zsh
# Render the 9:16 composition, then drop the first 8 frames (same clean start as 16:9 v2).
set -e
cd "${0:A:h}/../hf9"
mkdir -p renders
RAW="renders/_raw_9x16_v2.mp4"; OUT="renders/${NAME:-Video} 9x16 PREVIEW ${VER:-v1}.mp4"
npx hyperframes render --quality delivery --fps 30 --sdr -o "$RAW"
ffmpeg -v error -y -i "$RAW" -ss ${TRIM:-0.2667} -c:v libx264 -crf 14 -preset slow -pix_fmt yuv420p \
  -color_range tv -colorspace bt709 -color_trc bt709 -color_primaries bt709 \
  -af "afade=t=in:st=0:d=0.012" -c:a aac -b:a 256k -movflags +faststart "$OUT"
rm -f "$RAW"
