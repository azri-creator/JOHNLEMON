#!/bin/bash
# Soft synthesized SFX for Epic Style ads (all quiet; mix.py puts them ~-12 dB under everything).
# Usage: bash make_sfx.sh <out_dir>
#   lift.wav  rising filtered air for each lift transition
#   wind.wav  slow gusting wind (heights, bridges, "angin")
#   hum.wav   low cable-car hum (gondola / train rides)
#   ice.wav   glassy chimes (glacier, snow, cold places)
#   pop.wav   tiny pop when a title lands
# Swap or add destination-specific beds (waves, city murmur...) the same way; keep them soft.
set -e
mkdir -p "$1"; cd "$1"
g() { ffmpeg -v error -y -f lavfi -i "$1" -ac 2 -ar 48000 "$2"; }
g "anoisesrc=d=0.75:c=pink:r=48000:a=0.8,highpass=f=500,lowpass=f=4500,afade=t=in:st=0:d=0.45:curve=qsin,afade=t=out:st=0.45:d=0.3:curve=qsin,volume=0.5" lift.wav
g "anoisesrc=d=4.2:c=brown:r=48000:a=0.9,lowpass=f=900,highpass=f=120,volume='0.5+0.35*sin(2*PI*0.45*t)':eval=frame,afade=t=in:st=0:d=1.2,afade=t=out:st=2.8:d=1.4" wind.wav
g "aevalsrc='0.25*sin(2*PI*98*t)+0.12*sin(2*PI*196*t)+0.05*sin(2*PI*294*t)':d=8.4:s=48000,volume='0.7+0.3*sin(2*PI*0.3*t)':eval=frame,afade=t=in:st=0:d=1.5,afade=t=out:st=6.6:d=1.8" hum.wav
g "aevalsrc='0.22*(sin(2*PI*2093*t)*exp(-5*t)+0.7*sin(2*PI*3136*(t-0.18))*exp(-6*(t-0.18))*gte(t,0.18)+0.5*sin(2*PI*2637*(t-0.42))*exp(-5*(t-0.42))*gte(t,0.42))':d=1.6:s=48000,aecho=0.8:0.7:90|160:0.3|0.2" ice.wav
g "aevalsrc='0.5*sin(2*PI*(900-2400*t)*t)*exp(-30*t)':d=0.18:s=48000" pop.wav
ls -la
