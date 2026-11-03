#!/usr/bin/env python3
"""Word-level BM transcript with faster-whisper large-v3 (cached in ~/.cache/huggingface).
Usage: python3 transcribe_words.py <audio.wav> <out_words.json> ["initial prompt with names/terms"]
Text only — take cut/sync boundaries from the voice energy envelope, not these word times."""
import sys, json
from faster_whisper import WhisperModel
src, out = sys.argv[1], sys.argv[2]
prompt = sys.argv[3] if len(sys.argv) > 3 else "AI, prompt, character sheet, custom GPT, template, video AI, taip, komen."
m = WhisperModel("large-v3", device="cpu", compute_type="int8")
segs, _ = m.transcribe(src, language="ms", beam_size=5, word_timestamps=True, initial_prompt=prompt)
res = []
for s in segs:
    print(f"{s.start:6.2f}-{s.end:6.2f} {s.text.strip()}")
    res.append({"s": s.start, "e": s.end, "t": s.text.strip(),
                "w": [(w.word.strip(), round(w.start, 2), round(w.end, 2)) for w in s.words]})
json.dump(res, open(out, "w"), ensure_ascii=False)
