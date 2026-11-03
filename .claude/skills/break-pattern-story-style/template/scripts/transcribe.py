import json, sys
from faster_whisper import WhisperModel

m = WhisperModel("large-v3", device="cpu", compute_type="int8")
segs, info = m.transcribe(
    "audio/vo_raw.wav", language="ms", word_timestamps=True,
    vad_filter=False, beam_size=5, condition_on_previous_text=False,
)
out = []
for s in segs:
    out.append({
        "start": s.start, "end": s.end, "text": s.text,
        "words": [{"w": w.word, "s": w.start, "e": w.end, "p": w.probability} for w in s.words],
    })
    print(f"[{s.start:6.2f}-{s.end:6.2f}] {s.text}", flush=True)
json.dump(out, open("audio/transcript_raw.json", "w"), ensure_ascii=False, indent=1)
