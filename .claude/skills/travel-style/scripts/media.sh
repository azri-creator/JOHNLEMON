#!/bin/bash
# Travel Style media helpers. Run from the project folder. Each sub-command is independent.
#
#   bash media.sh cutout <aroll_cut.mp4>
#       Pixel-exact presenter cut-out: ML matte (hyperframes remove-background, ~2 min per 40 s on Apple silicon),
#       alphamerged with the SOURCE Y/U/V so skin and grade stay identical (bt709). -> assets/presenter.webm
#   bash media.sh clip <src> <name> <start> <dur>
#       Portrait B-roll (or a slice of the cut A-roll) -> 1080x1920 30 fps bt709, muted. -> assets/clips/<name>.mp4
#       Landscape sources: add a crop first (crop=ih*9/16:ih:<x>:0) and keep the shot short (it is upscaled).
#   bash media.sh still <src> <time> <name>
#       One frame, 1188x2112, for the blurred map background. -> assets/broll/<name>.jpg
#   bash media.sh sfx <out_dir>
#       Soft synthesised SFX: lift (scene rise), pop (title/pin), jet (flight), zoom (map fly-in).
#   bash media.sh bed <voice.wav> <pad.wav> <duration> <voice_end> <out.wav>
#       Voice + music bed: pad normalised to -36 LUFS (~20 dB under a -16 LUFS voice), lowpassed, small room,
#       swells +7 dB after the voice ends for the logo, fades out.
set -e
enc=(-an -c:v libx264 -crf 16 -preset medium -g 15 -pix_fmt yuv420p -colorspace bt709 -color_primaries bt709 -color_trc bt709 -color_range tv -movflags +faststart)
case "$1" in
  cutout)
    mkdir -p work assets
    npx --yes hyperframes@0.8.149 remove-background "$2" -o work/matte_raw.webm --quality best
    ffmpeg -v error -y -i "$2" -c:v libvpx-vp9 -i work/matte_raw.webm -filter_complex \
      "[1:v]format=yuva420p,alphaextract[a];[0:v]format=yuv420p[v];[v][a]alphamerge,format=yuva420p[o]" \
      -map "[o]" -an -c:v libvpx-vp9 -pix_fmt yuva420p -crf 14 -b:v 0 -deadline good -cpu-used 3 -row-mt 1 \
      -colorspace bt709 -color_primaries bt709 -color_trc bt709 -color_range tv assets/presenter.webm
    ffprobe -v error -show_entries format=duration -of csv=p=0 assets/presenter.webm ;;
  clip)
    mkdir -p assets/clips
    ffmpeg -v error -y -ss "$4" -t "$5" -i "$2" -vf "fps=30,scale=1080:1920:flags=lanczos,setsar=1" "${enc[@]}" "assets/clips/$3.mp4" ;;
  still)
    mkdir -p assets/broll
    ffmpeg -v error -y -ss "$3" -i "$2" -frames:v 1 -vf "scale=1188:2112:force_original_aspect_ratio=increase,crop=1188:2112" -q:v 3 "assets/broll/$4.jpg" ;;
  sfx)
    mkdir -p "$2"; cd "$2"
    g() { ffmpeg -v error -y -f lavfi -i "$1" -ac 2 -ar 48000 "$2"; }
    g "anoisesrc=d=0.75:c=pink:r=48000:a=0.8,highpass=f=500,lowpass=f=4500,afade=t=in:st=0:d=0.45:curve=qsin,afade=t=out:st=0.45:d=0.3:curve=qsin,volume=0.5" lift.wav
    g "aevalsrc='0.5*sin(2*PI*(900-2400*t)*t)*exp(-30*t)':d=0.18:s=48000" pop.wav
    g "anoisesrc=d=2.4:c=pink:r=48000:a=0.7,bandpass=f=900:w=1.4,volume='0.15+0.85*sin(PI*t/2.4)^2':eval=frame,afade=t=in:d=0.5,afade=t=out:st=1.7:d=0.7" jet.wav
    g "anoisesrc=d=1.2:c=pink:r=48000:a=0.8,lowpass=f=1800,highpass=f=200,afade=t=in:d=0.6:curve=qsin,afade=t=out:st=0.6:d=0.6:curve=qsin" zoom.wav
    ls ;;
  bed)
    ffmpeg -v error -y -i "$3" -af "aresample=48000,lowpass=f=3200,aecho=0.8:0.7:120|260:0.35|0.22,loudnorm=I=-36:TP=-6:LRA=11" -ar 48000 work_pad_norm.wav
    ffmpeg -v error -y -i "$2" -i work_pad_norm.wav -filter_complex \
      "[0]apad=whole_dur=$4[v];[1]atrim=0:$4,volume='if(lt(t,$5),1,if(lt(t,$5+0.7),1+(t-$5)/0.7*1.24,2.24))':eval=frame,afade=t=in:d=1.2,afade=t=out:st=$(echo "$4-1.3" | bc):d=1.3[m];[v][m]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.89[o]" \
      -map "[o]" -ar 48000 -ac 2 "$6"
    rm -f work_pad_norm.wav
    ffmpeg -hide_banner -i "$6" -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+(I:|Peak:)" ;;
  *) sed -n 2,20p "$0" ;;
esac
