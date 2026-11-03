#!/bin/zsh
# Render the composition, then tag the delivery file H.264 High / yuv420p / BT.709 / 30 fps, AAC 48 kHz, +faststart.
#   QUALITY=draft scripts/finish.sh      (preview)      scripts/finish.sh   (delivery)
# Add SDR=1 when any source is HDR (HLG/PQ): the render then tone-maps to SDR BT.709.
set -e
cd "${0:A:h}/../hf"
HFV=${HFV:-0.8.213}          # pin the CLI: npx otherwise chases a just-published version that may not resolve yet
mkdir -p renders
RAW="renders/_raw.mp4"; OUT="renders/${NAME:-GlowKeyword}_9x16_${QUALITY:-delivery}.mp4"
npx --yes hyperframes@$HFV render --quality ${QUALITY:-delivery} --fps 30 ${SDR:+--sdr} -o "$RAW"
ffmpeg -v error -y -i "$RAW" -c:v libx264 -profile:v high -preset slow -crf ${CRF:-16} -pix_fmt yuv420p -r 30 \
  -x264-params colorprim=bt709:transfer=bt709:colormatrix=bt709 \
  -color_primaries bt709 -color_trc bt709 -colorspace bt709 -color_range tv \
  -c:a aac -b:a 256k -ar 48000 -ac 2 -movflags +faststart "$OUT"
rm -f "$RAW"
ffprobe -v error -show_entries stream=codec_name,width,height,pix_fmt,color_primaries,color_transfer,r_frame_rate,sample_rate -of compact "$OUT"
ffmpeg -hide_banner -i "$OUT" -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+(I|Peak):" || true
echo "wrote hf/$OUT"
