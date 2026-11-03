#!/bin/zsh
# 16:9 assets from the main source: frame-exact A-roll cut, voice, exact cut-out segment, last frame.
# Find the start frame in an energy dip before the first word (see SKILL.md "Clean start"); OFF0 = that frame.
set -e
cd "${0:A:h}/.."
SRC="${SRC:?set SRC to the main 16:9 source}"
OFF0=${OFF0:?start frame}; NF=${NF:?A-roll length in frames}      # e.g. 302 and 1362 (45.40 s @ 30 fps)
P0=${P0:-}; PN=${PN:-}                                             # optional cut-out segment (bg-swap beats)
A=hf/assets; W=work; mkdir -p $A $W
TAG=(-color_range tv -colorspace bt709 -color_trc bt709 -color_primaries bt709)
ffmpeg -v error -y -i "$SRC" -vf "trim=start_frame=$OFF0:end_frame=$((OFF0+NF)),setpts=PTS-STARTPTS" \
  -c:v libx264 -crf 14 -preset slow -pix_fmt yuv420p $TAG -an $A/aroll.mp4
FPS=$(ffprobe -v error -select_streams v:0 -show_entries stream=r_frame_rate -of csv=p=0 "$SRC" | bc -l)
SS=$(printf %.6f $(echo "$OFF0/$FPS" | bc -l)); TT=$(printf %.6f $(echo "$NF/$FPS" | bc -l))   # bc drops the leading 0 (".0666"), ffmpeg rejects it
ffmpeg -v error -y -ss $SS -i "$SRC" -t $TT -vn -ac 2 -ar 48000 $W/voice.wav
if [[ -n $P0 ]]; then
  ffmpeg -v error -y -i "$SRC" -vf "trim=start_frame=$P0:end_frame=$((P0+PN)),setpts=PTS-STARTPTS" \
    -c:v libx264 -crf 8 -preset slow -pix_fmt yuv420p $TAG -an $W/seg.mp4
  (cd hf && npx hyperframes remove-background --quality best -o ../$W/seg_rb.webm ../$W/seg.mp4)
  ffmpeg -v error -y -i $W/seg.mp4 -c:v libvpx-vp9 -i $W/seg_rb.webm \
    -filter_complex "[1:v]alphaextract[m];[0:v][m]alphamerge,format=yuva420p" \
    -c:v libvpx-vp9 -pix_fmt yuva420p -crf 12 -b:v 0 -deadline good -cpu-used 4 -row-mt 1 -auto-alt-ref 0 $TAG -an $A/person.webm
fi
ffmpeg -v error -y -sseof -0.1 -i $A/aroll.mp4 -frames:v 1 -q:v 2 $A/lastframe.jpg
echo PREP16_DONE
