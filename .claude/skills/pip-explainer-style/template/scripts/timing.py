"""PER VIDEO: word anchors, layout, punch-ins, shakes and flashes. Shared by build.py (picture) and make_audio.py (sound),
so a timing change moves both. Anchors are written in SOURCE seconds (Whisper word starts, refined on the voice
envelope) and mapped through the EDL, so an EDL change moves everything with it.

The values below are the approved "Bisnes Baru Nak AI" edit (worked example). Replace them per video."""
import json, os

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
EDL = json.load(open(os.path.join(ROOT, "data", "edl.json"), encoding="utf-8"))
SEGS = EDL["segs"]
TOTAL = EDL["total"]
SPEECH_END = EDL["speechEnd"]
WORDS = EDL["words"]


def at(src):
    """source-footage seconds -> edit timeline seconds"""
    for s in SEGS:
        if s["in"] - 0.06 <= src <= s["out"] + 0.06:
            return round(s["at"] + max(0.0, src - s["in"]), 4)
    raise ValueError(f"source time {src} is not in the edit")


# Word anchors (source seconds). Name them after the word, use them everywhere.
_SRC = dict(
    boleh=0.0, jual=0.7, produk=1.44, bisnesBaru=2.58, tapi=3.26, ai100=3.62, pakaiAI=4.92, video=5.68, gambar=6.88,
    poster=8.26, sebelum=9.5, mentor=11.88,
    # 3 mekanisme
    dalam=12.9, tiga=14.1, wajib=15.16, corong=15.98, trafik=18.24, kedua=19.46, konten=20.32, ketiga=21.56, paling=22.6,
    closing=23.5, conversion=24.8,
    # trafik & konten
    trafikQ=26.12, sumber=27.14, orangTengok=29.02, tiktok=31.88, facebook=32.44, instagram=33.0, untukMenarik=33.56,
    kenaAda=34.96, dalamKonten=35.82, pecahan=37.5, pecahanBesar=38.04, satuVideo=39.4, videoSebenar=41.04,
    keduaVideo=41.68, videoAI2=42.58, soDekat=43.54,
    # brand trust
    bolehTak=44.36, launch=45.72, semua=46.18, takBoleh=47.5, sebab=47.98, brand1=49.7, trust1=50.42, orangDah=51.04,
    percayaBrand=51.44, percayaProduk=52.58, sebabTu=53.9, fyp=54.96, gunaAI=55.54, view=56.44, conv2=57.02,
    brandSendiri=58.06, orangPercaya=59.02, videoAI=59.86, boost=61.56, keinginan=61.96, soKalau=63.14, dapatkan=64.28,
    brandDulu=64.98, buatKonten=65.94, result=67.2, testimoni=68.02, samaClosing=68.9,
    # chatbot / blueprint
    baruBaru=70.72, chatbot=72.42, bayangkan=73.22, service=75.18, produk2=75.86, awakSendiri=76.36, takAda=76.82,
    blueprint=77.38, closing2=78.12, takAda2=79.4, macamMana=81.26, chatbot2=81.58, close=83.12, kalauAwak=83.96,
    blueprint2=85.34, soClear=86.08, samaKontenAI=86.92,
    # ending
    kalauTak=88.52, fundamental=89.06, kontenTu=89.76, buih=90.96, lautan=91.7,
)
T = {k: at(v) for k, v in _SRC.items()}

END_CARD = round(SPEECH_END - 0.1, 4)  # end card starts just after the last word; never cover it

# Layout: FULL close-up (0) or PiP card + graphic panel (1). The presenter is ONE video; build.py morphs it.
LAYOUT = [
    (0, 0),
    (T["bisnesBaru"] - 0.05, 1),
    (T["sebelum"] - 0.05, 0),       # mentor
    (T["tiga"] - 0.05, 1),
    (T["paling"] - 0.1, 0),
    (T["closing"] + 0.02, 1),
    (T["trafikQ"] - 0.05, 0),       # "trafik mekanisme ni apa?"
    (T["sumber"] - 0.05, 1),
    (T["untukMenarik"] - 0.05, 0),  # "kena ada konten"
    (T["dalamKonten"] - 0.05, 1),
    (T["takBoleh"] - 0.04, 0),
    (T["orangDah"] - 0.05, 1),
    (T["brandSendiri"] - 0.05, 0),
    (T["videoAI"] - 0.05, 1),
    (T["soKalau"] - 0.05, 0),
    (T["buatKonten"] - 0.06, 1),
    (T["macamMana"] - 0.05, 0),
    (T["samaKontenAI"] - 0.05, 1),
]
# PiP -> PiP scene changes (the card nudges on these)
PANEL_CUTS = [T["soDekat"], T["samaClosing"] - 0.05, T["baruBaru"] - 0.05, T["awakSendiri"] - 0.05]

# Punch-ins on emphasis words: multiply the 1.2x base crop, pivot on the face. e = "snap" (fast) or "out".
# Each key starts moving to v at t over d seconds (sorted automatically; a key is cut short by the next one).
PUNCH = [
    # intro: snap in from frame 0, punch on "jual" and "produk"
    (0, 1.22, 0.01), (0.02, 1.0, 0.35, "snap"),
    (T["jual"], 1.1, 0.1, "snap"), (T["jual"] + 0.35, 1.04, 0.3),
    (T["produk"], 1.16, 0.1, "snap"), (T["produk"] + 0.4, 1.06, 0.3),
    # mentor
    (T["sebelum"] - 0.05, 1.12, 0.01), (T["sebelum"], 1.0, 0.4), (T["mentor"], 1.08, 0.15, "snap"),
    (T["dalam"], 1.16, 0.1, "snap"), (T["dalam"] + 0.3, 1.02, 0.5),
    (T["paling"] - 0.1, 1.16, 0.01), (T["paling"] - 0.08, 1.08, 0.35),
    (T["takBoleh"] - 0.04, 1.22, 0.1, "snap"), (T["sebab"], 1.1, 0.5),
    (T["brand1"], 1.16, 0.12, "snap"), (T["trust1"] + 0.4, 1.06, 0.4),
    (T["brandSendiri"] - 0.05, 1.12, 0.01), (T["brandSendiri"], 1.02, 0.35),
    (T["soKalau"] - 0.05, 1.1, 0.01), (T["soKalau"], 1.0, 0.35),
    (T["dapatkan"], 1.14, 0.12, "snap"), (T["buatKonten"] - 0.2, 1.05, 0.2),
    (T["trafikQ"] - 0.05, 1.14, 0.01), (T["trafikQ"], 1.04, 0.35),
    (T["untukMenarik"] - 0.05, 1.1, 0.01), (T["untukMenarik"], 1.0, 0.35), (T["kenaAda"], 1.12, 0.12, "snap"),
    (T["macamMana"] - 0.05, 1.08, 0.01), (T["macamMana"], 1.0, 0.35),
    (T["kalauAwak"], 1.1, 1.6), (T["soClear"], 1.18, 0.12, "snap"), (T["samaKontenAI"] - 0.3, 1.08, 0.25),
]

# Presenter shakes in FULL (start, seconds, amplitude px, seed)
SHAKES = [(T["takBoleh"] - 0.04, 0.3, 9, 3), (T["produk"], 0.2, 6, 5), (0, 0.18, 8, 7)]

# Screen-blend flashes, only on the big accents (time, amplitude, colour)
FLASHES = [
    (0, 0.5, "#ffffff"), (T["produk"], 0.25, "#FFE600"), (T["ai100"], 0.35, "#FFE600"), (T["pakaiAI"], 0.2, "#ffffff"),
    (T["takBoleh"] - 0.03, 0.55, "#ffffff"), (T["brand1"] - 0.03, 0.25, "#FFE600"), (T["baruBaru"] - 0.05, 0.3, "#00CFF5"),
    (END_CARD, 0.7, "#ffffff"),
]


def layout_at(t):
    m = 0
    for a, v in LAYOUT:
        if t >= a: m = v
    return m
