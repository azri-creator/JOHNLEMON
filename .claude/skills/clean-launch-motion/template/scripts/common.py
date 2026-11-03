"""Shared paths and helpers for the Clean Launch Motion scripts.

Project layout (the template folder copied to work/<Name>/):
  plan.json                 per-video config
  vo/vo_script_locked.txt   the locked script, one delivery line per line
  vo/takes/lines/           ElevenLabs line takes (tts_lines.py)
  vo/vo_words.json          word timings (rough_timing.py or build_vo.py), the timing source for everything
  scripts/                  these scripts, lib.js, index.tpl.html, scenes/*.html
  hf/                       the HyperFrames project (npx hyperframes init hf ...); build.py writes hf/index.html
  hf/assets/                vo.wav, music.wav, sfx.wav, mix.wav, img/, video/
"""
import json, os, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, ".."))
HF = os.path.join(PROJ, "hf")
ASSETS = os.path.join(HF, "assets")
WORDS_JSON = os.path.join(PROJ, "vo", "vo_words.json")


def load_plan():
    return json.load(open(os.path.join(PROJ, "plan.json"), encoding="utf-8"))


def script_lines(plan):
    path = os.path.join(PROJ, plan["script"])
    return [l.strip() for l in open(path, encoding="utf-8") if l.strip()]


def ffmpeg():
    """$FFMPEG, then ffmpeg on PATH, then the imageio-ffmpeg binary."""
    if os.environ.get("FFMPEG"):
        return os.environ["FFMPEG"]
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        raise SystemExit("ffmpeg not found: run `bash setup.sh` or set FFMPEG=/path/to/ffmpeg")


def load_words():
    return json.load(open(WORDS_JSON, encoding="utf-8"))["words"]


def timing(plan, words):
    """Scene cuts: `lead` s before each scene's first VO word (the picture leads the line). First scene starts at 0.
    Returns (CUT, SPAN, VO_END, TOTAL). The same formula is used by build.py (picture) and make_audio.py (sound)."""
    scenes = plan["scenes"]
    vo_end = words[-1]["e"]
    total = round(vo_end + plan["end_hold"], 3)
    cut = {}
    for i, k in enumerate(scenes):
        ws = [w for w in words if w["scene"] == k]
        if not ws:
            raise SystemExit(f"scene '{k}' has no VO words: check plan.line_scene")
        cut[k] = 0.0 if i == 0 else round(ws[0]["s"] - plan["lead"], 3)
    span = {k: [cut[k], cut[scenes[i + 1]] if i + 1 < len(scenes) else total] for i, k in enumerate(scenes)}
    return cut, span, vo_end, total
