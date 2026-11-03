"""Clean-speech cut list for Travel Style A-roll: drop the off-camera prompter cue at the head of each take,
then squeeze every inner silence so only the talent's delivery remains.

Usage: python3 -I cutlist.py <clips.json> <wav_dir> <edl_out.json>

clips.json is in SCRIPT order (the order the lines are spoken in the ad, not file-name order):
[
  {"name": "L1", "src": "take_a.mp4", "wav": "take_a.wav", "from": 1.60, "to": 10.85},
  ...
]
"from"/"to" bound the window where ONLY the talent speaks: start it after the prompter's cue (find it with a
loudness envelope + a whisper pass on the first 2-3 s of each take) and end it before the stop-tap.
wav files are 16 kHz mono extracts of each take (ffmpeg -i take.mp4 -ac 1 -ar 16000 take.wav).
"""
import sys, wave, array, math, json

CLIPS, WAVDIR, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
HOP = 0.02
THR = -37.5          # dBFS: talent speech ~ -26..-34, room floor ~ -40..-48. Re-measure for a new room.
MIN_GAP = 0.24       # silences longer than this get squeezed
KEEP_GAP = 0.14      # inner pause left after the squeeze
PRE, POST = 0.06, 0.12


def env(path):
    w = wave.open(path); sr = w.getframerate()
    d = array.array('h', w.readframes(w.getnframes()))
    hop = int(sr * HOP); out = []
    for i in range(0, len(d), hop):
        seg = d[i:i + hop]
        r = math.sqrt(sum(x * x for x in seg) / max(1, len(seg)))
        out.append(20 * math.log10(r / 32768 + 1e-9))
    return out


edl = []
for c in json.load(open(CLIPS)):
    e = env(f"{WAVDIR}/{c['wav']}")
    ia, ib = int(c["from"] / HOP), min(int(c["to"] / HOP), len(e))
    sm = [max(e[max(0, i - 1):i + 2]) for i in range(len(e))]   # consonant dips don't count as silence
    loud = [i for i in range(ia, ib) if sm[i] > THR]
    if not loud:
        sys.exit(f"{c['name']}: no speech above {THR} dB in the window")
    s0, s1 = loud[0] * HOP - PRE, (loud[-1] + 1) * HOP + POST
    segs, cur, i = [], s0, loud[0]
    while i < loud[-1]:
        if sm[i] <= THR:
            j = i
            while j < loud[-1] and sm[j] <= THR:
                j += 1
            if (j - i) * HOP > MIN_GAP:
                segs.append([round(cur, 3), round(i * HOP + KEEP_GAP / 2, 3)])
                cur = j * HOP - KEEP_GAP / 2
            i = j
        else:
            i += 1
    segs.append([round(cur, 3), round(s1, 3)])
    edl.append({"name": c["name"], "src": c["src"], "segs": segs})
    print(c["name"], segs, "->", round(sum(y - x for x, y in segs), 2), "s")

json.dump(edl, open(OUT, "w"), indent=1)
