#!/bin/bash
set -e
cd "$1"
g() { ffmpeg -v error -y -f lavfi -i "$1" -ac 2 "$2"; }
# whoosh long (zoom-through)
g "anoisesrc=d=1.1:c=pink:r=44100:a=0.9,highpass=f=300,lowpass=f=5200,afade=t=in:st=0:d=0.8:curve=exp,afade=t=out:st=0.8:d=0.3,volume=0.55" wl_n.wav
g "aevalsrc='0.35*sin(2*PI*(180+1500*t*t/1.1)*t)*min(1,t/0.5)*max(0,1-(t-0.8)/0.3)':d=1.1:s=44100" wl_t.wav
ffmpeg -v error -y -i wl_n.wav -i wl_t.wav -filter_complex "amix=inputs=2:normalize=0,aecho=0.6:0.5:60:0.25,alimiter=limit=0.9" whoosh_long.wav
# swipe whoosh (peak in the middle)
g "anoisesrc=d=0.85:c=white:r=44100:a=0.9,bandpass=f=2200:w=1.4,afade=t=in:st=0:d=0.4:curve=qsin,afade=t=out:st=0.4:d=0.45:curve=qsin,volume=0.6" sw_n.wav
g "aevalsrc='0.3*sin(2*PI*(260+900*sin(PI*t/0.85))*t)*sin(PI*t/0.85)':d=0.85:s=44100" sw_t.wav
ffmpeg -v error -y -i sw_n.wav -i sw_t.wav -filter_complex "amix=inputs=2:normalize=0,aecho=0.5:0.4:45:0.2,alimiter=limit=0.9" swipe.wav
# hit / snap punch
g "aevalsrc='0.9*sin(2*PI*(95-260*t)*t)*exp(-10*t)+0.35*sin(2*PI*180*t)*exp(-22*t)':d=0.5:s=44100" h_a.wav
g "anoisesrc=d=0.2:c=white:r=44100:a=0.8,highpass=f=1800,afade=t=out:st=0:d=0.2:curve=exp,volume=0.5" h_b.wav
ffmpeg -v error -y -i h_a.wav -i h_b.wav -filter_complex "amix=inputs=2:normalize=0:duration=longest,alimiter=limit=0.9" hit.wav
# pop, tick, ding
g "aevalsrc='0.8*sin(2*PI*(1100-4200*t)*t)*exp(-26*t)':d=0.22:s=44100" pop.wav
g "aevalsrc='0.7*sin(2*PI*2600*t)*exp(-90*t)':d=0.08:s=44100" tick.wav
g "aevalsrc='0.45*(sin(2*PI*1318*t)+0.5*sin(2*PI*1975*t)+0.25*sin(2*PI*2637*t))*exp(-6*t)':d=0.9:s=44100" ding.wav
# riser
g "aevalsrc='0.22*sin(2*PI*(220+2200*t*t/1.6)*t)*min(1,t/0.9)':d=1.6:s=44100" r_t.wav
g "anoisesrc=d=1.6:c=pink:r=44100:a=0.7,highpass=f=1200,afade=t=in:st=0:d=1.4:curve=exp,afade=t=out:st=1.4:d=0.2,volume=0.35" r_n.wav
ffmpeg -v error -y -i r_t.wav -i r_n.wav -filter_complex "amix=inputs=2:normalize=0,alimiter=limit=0.9" riser.wav
# iris reveal (falling glass sweep)
g "aevalsrc='0.3*sin(2*PI*(2200-1700*t/0.9)*t)*sin(PI*t/0.9)':d=0.9:s=44100" i_t.wav
g "anoisesrc=d=0.9:c=pink:r=44100:a=0.8,highpass=f=800,afade=t=in:st=0:d=0.5:curve=qsin,afade=t=out:st=0.5:d=0.4,volume=0.4" i_n.wav
ffmpeg -v error -y -i i_t.wav -i i_n.wav -filter_complex "amix=inputs=2:normalize=0,alimiter=limit=0.9" iris.wav
rm -f wl_*.wav sw_*.wav h_*.wav r_*.wav i_*.wav
ls -la
