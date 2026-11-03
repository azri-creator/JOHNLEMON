#!/bin/zsh
# Delivery render + exact audio master.
#   NAME=Bisnes_Baru_Nak_AI zsh scripts/finish.sh          -> renders/<NAME>_9x16.mp4
#   QUALITY=draft zsh scripts/finish.sh                    -> quick check render
# HyperFrames renders the picture (SDR BT.709); the voice/music/SFX master from make_audio.py is muxed back unchanged,
# so the loudness stays exactly at -14 LUFS / -1.5 dBTP. H.264 High, AAC 48 kHz 256k, 1080x1920, 30 fps, +faststart.
set -e
cd "${0:A:h}/.."
HF=(${=HF:-npx --yes hyperframes})   # if npx fails with ETARGET (registry lag), pin it: HF="npx --yes hyperframes@0.8.212"
mkdir -p renders
RAW="renders/_raw.mp4"; OUT="${OUT:-renders/${NAME:-PiP_Explainer}_9x16.mp4}"
$HF render hf --quality ${QUALITY:-delivery} --fps 30 --sdr -o "$RAW"
ffmpeg -v error -y -i "$RAW" -i hf/assets/audio/mix_master.wav -map 0:v:0 -map 1:a:0 -vf format=yuv420p \
  -c:v libx264 -profile:v high -preset slow -crf 16 -r 30 -g 60 -x264-params colorprim=bt709:transfer=bt709:colormatrix=bt709 \
  -color_primaries bt709 -color_trc bt709 -colorspace bt709 -color_range tv \
  -c:a aac -b:a 256k -ar 48000 -ac 2 -shortest -movflags +faststart "$OUT"
rm -f "$RAW"
echo "wrote $OUT"
ffmpeg -hide_banner -i "$OUT" -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+(I|Peak):" | tail -2
