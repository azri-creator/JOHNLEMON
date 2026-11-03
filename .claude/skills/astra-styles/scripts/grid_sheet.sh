#!/bin/bash
# Contact sheet with a 10x10 grid (each cell = 108x192 px of a 1080x1920 frame) to read hand/face positions by eye.
# Usage: grid_sheet.sh <video> <start_s> <dur_s> <fps> <out.jpg>
ffmpeg -hide_banner -loglevel error -y -ss "$2" -t "$3" -i "$1" \
  -vf "fps=$4,scale=270:-1,drawgrid=w=27:h=48:t=1:c=yellow@0.3,tile=10x2:padding=3" -frames:v 1 "$5" && echo "$5"
