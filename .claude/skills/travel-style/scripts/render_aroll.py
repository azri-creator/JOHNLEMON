"""Cut A-roll from EDL into one 1080x1920 30fps bt709 video + clean mono voice.
Usage: python3 -I render_aroll.py <srcdir> <edl.json> <outdir>"""
import sys, json, subprocess, os

SRC, EDL, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
edl = json.load(open(EDL))
inputs, filt, vlabels, alabels, timeline = [], [], [], [], []
t = 0.0
n = 0
for ci, clip in enumerate(edl):
    inputs += ["-i", os.path.join(SRC, clip["src"])]
    clip_start = t
    for a, b in clip["segs"]:
        d = b - a
        filt.append(f"[{ci}:v]trim={a}:{b},setpts=PTS-STARTPTS,fps=30,"
                    f"scale=1080:1920:flags=lanczos,unsharp=5:5:0.35,setsar=1[v{n}]")
        filt.append(f"[{ci}:a]atrim={a}:{b},asetpts=PTS-STARTPTS,pan=mono|c0=0.5*c0+0.5*c1,"
                    f"aresample=48000,afade=t=in:d=0.012,afade=t=out:st={d - 0.015:.3f}:d=0.015[a{n}]")
        vlabels.append(f"[v{n}]"); alabels.append(f"[a{n}]")
        n += 1
        t += d
    timeline.append({"name": clip["name"], "start": round(clip_start, 3), "end": round(t, 3)})

filt.append("".join(vlabels) + f"concat=n={n}:v=1:a=0[vc]")
filt.append("".join(alabels) + f"concat=n={n}:v=0:a=1,highpass=f=80,afftdn=nr=10:nf=-45,"
            "acompressor=threshold=-24dB:ratio=2.5:attack=8:release=120,"
            "loudnorm=I=-16:TP=-1.5:LRA=7[ac]")
fc = ";".join(filt)
subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", fc,
                "-map", "[vc]", "-c:v", "libx264", "-crf", "14", "-preset", "medium",
                "-pix_fmt", "yuv420p", "-colorspace", "bt709", "-color_primaries", "bt709",
                "-color_trc", "bt709", "-color_range", "tv", "-an", os.path.join(OUT, "aroll_cut.mp4"),
                "-map", "[ac]", "-ar", "48000", "-ac", "1", os.path.join(OUT, "voice.wav")], check=True)
json.dump(timeline, open(os.path.join(OUT, "line_times.json"), "w"), indent=1)
print(json.dumps(timeline, indent=1), "total", round(t, 3))
