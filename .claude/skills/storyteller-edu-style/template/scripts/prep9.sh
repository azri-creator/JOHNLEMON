#!/bin/zsh
# 9:16 strips from the portrait source (prefer the RAW / un-swapped take when the user asks for it).
# The portrait source must be frame-aligned with the 16:9 source (check audio cross-correlation = 0 first).
# A-roll = frames A0..A1 (same cut as aroll.mp4); cut-out = frames P0..P1 with a fresh matte from remove-background.
# Crop 1040 px wide from X0, lanczos x1.7778 -> 1848x1920 strip. Pixels untouched apart from scale + light unsharp.
set -e
cd "${0:A:h}/.."
SRC="${SRC9:?set SRC9 to the portrait source (RAW / un-swapped footage, frame-aligned with the 16:9 source)}"
A0=${A0:-302}; A1=${A1:-1664}     # A-roll frame range (same as aroll.mp4)
P0=${P0:-896}; P1=${P1:-1219}     # cut-out segment frame range
X0=${X0:-470}                      # crop x so the face sits ~x 940 in the 1848 strip
A=hf9/assets; W=work9
TAG=(-color_range tv -colorspace bt709 -color_trc bt709 -color_primaries bt709)
VF="crop=1040:1080:$X0:0,scale=1848:1920:flags=lanczos,unsharp=5:5:0.4:5:5:0"
ffmpeg -v error -y -i "$SRC" -vf "trim=start_frame=$A0:end_frame=$A1,setpts=PTS-STARTPTS,$VF" \
  -c:v libx264 -crf 14 -preset slow -pix_fmt yuv420p $TAG -an $A/aroll9.mp4
ffmpeg -v error -y -i "$SRC" -vf "trim=start_frame=$P0:end_frame=$P1,setpts=PTS-STARTPTS" \
  -c:v libx264 -crf 8 -preset slow -pix_fmt yuv420p $TAG -an $W/raw_seg.mp4
(cd hf9 && npx hyperframes remove-background --quality best -o ../$W/raw_seg_rb.webm ../$W/raw_seg.mp4)
# exact cut-out: RAW pixels + matte alpha
ffmpeg -v error -y -i $W/raw_seg.mp4 -c:v libvpx-vp9 -i $W/raw_seg_rb.webm \
  -filter_complex "[1:v]alphaextract[m];[0:v][m]alphamerge,$VF,format=yuva420p" \
  -c:v libvpx-vp9 -pix_fmt yuva420p -crf 12 -b:v 0 -deadline good -cpu-used 4 -row-mt 1 -auto-alt-ref 0 $TAG -an $A/person9.webm
ffmpeg -v error -y -ss 45.33 -i $A/aroll9.mp4 -vf "crop=1080:1920:402:0" -frames:v 1 -q:v 2 $A/lastframe9.jpg
echo PREP_DONE
