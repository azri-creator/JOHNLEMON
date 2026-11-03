# Refine key-word starts from the voice energy envelope (Whisper drifts 0.2-0.3 s).
# Output: work/times.json, times on the NEW timeline (source - OFFSET).
import json, wave, numpy as np, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OFFSET = 10.06
KEY = {  # name: whisper start in source seconds
 'para':10.22,'ilmu':12.52,'slide':13.56,'bayangkan':13.80,'satu':14.72,'macam':16.12,'transform':16.82,
 'jadi':17.52,'motion':18.54,'education':19.12,'voice':20.62,'over':21.08,'animation':22.20,'untuk':22.62,
 'pelajar':23.80,'konteks':25.80,'sebab':26.36,'pisau':27.76,'betul':28.20,'okey':29.26,'salah':29.98,
 'memang':31.14,'kalau':32.00,'cari':33.68,'explain':34.80,'satu2':35.94,'chapter':36.56,'sekarang':36.80,
 'cikgu2':37.56,'lecturer2':38.36,'control':39.70,'dan':40.46,'tak':41.70,'skill':42.38,'editing':42.98,
 'tapi':43.40,'knowledge':44.58,'workflow':44.92,'sebab2':45.28,'panduan':46.52,'edit':46.96,'video':47.16,
 'guna':47.50,'code':47.84,'khas':47.98,'newbie':48.44,'belajar':49.62,'expert':50.86,'menggunakan':51.32,
 'claude':52.08,'chat':52.96,'nak':53.66,'tekan':54.62,'ada_end':55.16}
w = wave.open(os.path.join(ROOT, 'work/voice.wav')); sr = w.getframerate(); n = w.getnchannels()
x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32).reshape(-1, n).mean(1) / 32768
H = sr // 100
env = 20 * np.log10(np.sqrt(np.convolve(x**2, np.ones(H) / H, 'same')[::H]) + 1e-9)  # 10 ms frames
out = {}
for k, s in KEY.items():
    t = s - OFFSET
    a, b = int((t - .12) * 100), int((t + .12) * 100)
    m = a + int(np.argmin(env[a:b]))
    on = m
    while on < min(m + 40, len(env) - 1) and env[on] < max(env[m] + 9, -38): on += 1
    # soft onsets (s-, f-) read late on RMS, so trust the envelope only within -0.10..+0.15 of Whisper
    out[k] = round(min(max(on / 100, t - .10), t + .15), 2)
    print(f'{k:12s} whisper {t:6.2f}  onset {out[k]:6.2f}  ({out[k]-t:+.2f})')
out['END_VOICE'] = 45.24
json.dump(out, open(os.path.join(ROOT, 'work/times.json'), 'w'), indent=1)
