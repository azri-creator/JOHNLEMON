#!/bin/bash
# Media prep for a Epic Style build. Run from the project folder. Each sub-command is independent.
#
#   bash prep_media.sh presenter <touchup.mov> [pad_seconds]
#       Cut-out of the already-graded TouchUp video: ML matte (hyperframes remove-background, ~5 min for 77 s),
#       then alphamerge with the SOURCE Y/U/V so skin and grade stay pixel-identical (bt709 tagged).
#       The last frame is held for pad_seconds (default 0.9) so the outro can rise over it.
#   bash prep_media.sh outro <outro.mov>
#       iPhone HLG -> SDR with Apple's own tone mapping (avconvert), then 30 fps bt709.
#       Never use a hand-rolled HLG formula here: it blew out faces and white shirts ("overexposure").
#   bash prep_media.sh clip <montage.mov> <name> <start> <dur> <crop_x>
#       Cut a 1920x1080 montage shot to a 1080x1920 cover crop (608x1080 window at crop_x, ~1.78x upscale,
#       light unsharp). Add 1 s of held frame with TPAD=1 if the clip must outlast its scene.
#   bash prep_media.sh stills <src_dir> [max_px]
#       Copy b-roll stills to assets/broll as JPEG, longest side <= max_px (default 3000).
set -e
enc=(-c:v libx264 -crf 17 -preset medium -g 15 -colorspace bt709 -color_primaries bt709 -color_trc bt709 -color_range tv -movflags +faststart)
case "$1" in
  presenter)
    mkdir -p work assets
    npx --yes hyperframes@0.8.149 remove-background "$2" -o work/matte_raw.webm --quality best
    ffmpeg -v error -y -i "$2" -c:v libvpx-vp9 -i work/matte_raw.webm -filter_complex \
      "[1:v]format=yuva420p,alphaextract[a];[0:v]format=yuv420p[v];[v][a]alphamerge,format=yuva420p,tpad=stop_mode=clone:stop_duration=${3:-0.9}[o]" \
      -map "[o]" -an -c:v libvpx-vp9 -pix_fmt yuva420p -crf 14 -b:v 0 -deadline good -cpu-used 3 -row-mt 1 \
      -colorspace bt709 -color_primaries bt709 -color_trc bt709 -color_range tv assets/presenter.webm
    ffmpeg -v error -y -i "$2" -vn -ac 2 -ar 48000 work/vo_src.wav
    ffprobe -v error -show_entries format=duration -of csv=p=0 assets/presenter.webm ;;
  outro)
    mkdir -p work assets/clips
    avconvert -s "$2" -p Preset1920x1080 -o work/outro_apple.mov --replace
    ffmpeg -v error -y -i work/outro_apple.mov -an -vf "fps=30,format=yuv420p" "${enc[@]}" -crf 16 assets/clips/outro.mp4
    ffmpeg -v error -y -i "$2" -vn -ac 2 -ar 48000 work/outro.wav
    ffprobe -v error -show_entries format=duration:stream=color_transfer -of compact assets/clips/outro.mp4 ;;
  clip)
    mkdir -p assets/clips
    pad=""; [ -n "$TPAD" ] && pad=",tpad=stop_mode=clone:stop_duration=$TPAD"
    ffmpeg -v error -y -ss "$4" -t "$5" -i "$2" -an \
      -vf "crop=608:1080:$6:0,scale=1080:1920:flags=lanczos,unsharp=5:5:0.5,fps=30$pad,format=yuv420p" "${enc[@]}" "assets/clips/$3.mp4" ;;
  stills)
    mkdir -p assets/broll
    for f in "$2"/*.{jpg,jpeg,png,webp,JPG,PNG}; do [ -e "$f" ] || continue
      b=$(basename "${f%.*}"); ffmpeg -v error -y -i "$f" -vf "scale='if(gt(iw,ih),min(${3:-3000},iw),-2)':'if(gt(iw,ih),-2,min(${3:-3000},ih))'" -q:v 2 "assets/broll/$b.jpg"; done
    ls assets/broll ;;
  *) sed -n 2,20p "$0" ;;
esac
