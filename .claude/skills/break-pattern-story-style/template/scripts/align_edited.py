import json
from faster_whisper import WhisperModel
m = WhisperModel("large-v3", device="cpu", compute_type="int8")
segs, _ = m.transcribe("audio/VO_Break_Pattern_EDITED.wav", language="ms", word_timestamps=True,
                       beam_size=5, condition_on_previous_text=False,
                       initial_prompt="Cuba tengok balik dekat galeri tu, berapa banyak footage yang tak sempat nak edit. VGC, ChatGPT, Claude, b-roll, subtitle, sound effect, automate editing.")
out = []
for s in segs:
    out.append({"start": s.start, "end": s.end, "text": s.text,
                "words": [{"w": w.word.strip(), "s": round(w.start, 3), "e": round(w.end, 3)} for w in s.words]})
    print(f"[{s.start:6.2f}-{s.end:6.2f}] " + " ".join(f"{w.word.strip()}({w.start:.2f}-{w.end:.2f})" for w in s.words), flush=True)
json.dump(out, open("audio/transcript_edited.json", "w"), ensure_ascii=False, indent=1)
