"""Word-level transcript (faster-whisper large-v3, BM).
  ffmpeg -i <footage> -vn -ac 1 -ar 16000 analysis/foot16k.wav
  ASR_PROMPT="<key terms>" /usr/bin/python3 scripts/transcribe.py analysis/foot16k.wav analysis/words.json
Put the key terms of the video into ASR_PROMPT so brand words are spelled right."""
import os
PROMPT = os.environ.get("ASR_PROMPT", "Bisnes, AI, trafik, konten, closing, brand trust, FYP, chatbot, blueprint, testimoni, fundamental.")
import json, sys
from faster_whisper import WhisperModel
m = WhisperModel("large-v3", device="cpu", compute_type="int8")
src, out = sys.argv[1], sys.argv[2]
segs, info = m.transcribe(src, language="ms", word_timestamps=True, vad_filter=False, initial_prompt=PROMPT)
res = []
for s in segs:
    res.append({"start": s.start, "end": s.end, "text": s.text, "words": [{"w": w.word, "s": w.start, "e": w.end} for w in s.words]})
    print(f"{s.start:6.2f}-{s.end:6.2f} {s.text}", flush=True)
os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
json.dump(res, open(out, "w"), ensure_ascii=False, indent=1)
