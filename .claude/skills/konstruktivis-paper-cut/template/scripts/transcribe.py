import json, sys
from faster_whisper import WhisperModel
m = WhisperModel("large-v3", device="cpu", compute_type="int8")
segs, info = m.transcribe(sys.argv[1], language="ms", word_timestamps=True, vad_filter=False, beam_size=5)
out = []
for s in segs:
    print(f"[{s.start:6.2f}-{s.end:6.2f}] {s.text}", flush=True)
    for w in s.words: out.append([round(w.start,2), round(w.end,2), w.word.strip()])
json.dump(out, open(sys.argv[2], "w"), ensure_ascii=False)
