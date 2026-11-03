#!/usr/bin/env python3
"""ElevenLabs voice-over helper for Claude Code (stdlib only, Python 3.9+).

Commands:
  setup                      Save your ElevenLabs API key to macOS Keychain (prompts, hidden input)
  check                      Verify the key works and show remaining character quota
  voices [--search TEXT]     List voices available on your account
  models                     List TTS models
  default [--voice V] [--model M]   Show or set default voice/model
  tts --text/--file ... [-o out.mp3] [--voice V] [--srt] [--play]
                             Generate a voice-over MP3 (long scripts are chunked automatically)
"""
import argparse
import base64
import getpass
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime

API = "https://api.elevenlabs.io"
KEYCHAIN_SERVICE = "elevenlabs-api-key"
CONFIG_DIR = os.path.expanduser("~/.config/elevenlabs-voiceover")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")
DEFAULT_OUT_DIR = os.path.expanduser("~/Movies/Voiceover")
DEFAULTS = {
    "voice_id": "JBFqnCBsd6RMkjVDRZzb",  # "George" premade voice
    "model_id": "eleven_multilingual_v2",  # supports Bahasa Melayu + English
    "output_format": "mp3_44100_128",
}
CHUNK_CHARS = 4000


# ---------- config / key ----------

def load_config():
    cfg = dict(DEFAULTS)
    try:
        with open(CONFIG_PATH) as f:
            cfg.update(json.load(f))
    except (OSError, ValueError):
        pass
    return cfg


def save_config(cfg):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2)


def get_key():
    key = os.environ.get("ELEVENLABS_API_KEY")
    if key:
        return key.strip()
    try:
        out = subprocess.run(
            ["security", "find-generic-password", "-s", KEYCHAIN_SERVICE, "-w"],
            capture_output=True, text=True,
        )
        if out.returncode == 0 and out.stdout.strip():
            return out.stdout.strip()
    except FileNotFoundError:
        pass
    sys.exit("No ElevenLabs API key found. Run:  python3 %s setup" % os.path.abspath(__file__))


# ---------- http ----------

def request(method, path, key, body=None, raw=False):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(API + path, data=data, method=method)
    req.add_header("xi-api-key", key)
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            payload = r.read()
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")
        sys.exit("ElevenLabs API error %s on %s: %s" % (e.code, path, detail[:800]))
    except urllib.error.URLError as e:
        sys.exit("Network error: %s" % e.reason)
    return payload if raw else json.loads(payload)


# ---------- commands ----------

def cmd_setup(_args):
    print("Paste your ElevenLabs API key (input hidden), then press Enter.")
    print("Get one at: https://elevenlabs.io/app/settings/api-keys")
    key = getpass.getpass("API key: ").strip()
    if not key:
        sys.exit("No key entered.")
    subprocess.run(["security", "delete-generic-password", "-s", KEYCHAIN_SERVICE],
                   capture_output=True)
    r = subprocess.run(["security", "add-generic-password", "-s", KEYCHAIN_SERVICE,
                        "-a", getpass.getuser(), "-w", key], capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit("Could not save to Keychain: " + r.stderr)
    print("Saved to macOS Keychain (service: %s). Testing..." % KEYCHAIN_SERVICE)
    cmd_check(None)


def cmd_check(_args):
    key = get_key()
    voices = request("GET", "/v1/voices", key)
    print("OK - key works. %d voices available." % len(voices.get("voices", [])))
    req = urllib.request.Request(API + "/v1/user/subscription")
    req.add_header("xi-api-key", key)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            sub = json.loads(r.read())
        used, limit = sub.get("character_count", 0), sub.get("character_limit", 0)
        print("Plan: %s | characters used %s / %s (remaining %s)"
              % (sub.get("tier"), used, limit, limit - used))
    except urllib.error.HTTPError:
        print("(Quota not readable - key lacks 'user read' permission; that's fine.)")
    cfg = load_config()
    print("Default voice: %s | model: %s" % (cfg["voice_id"], cfg["model_id"]))


def fetch_voices(key):
    return request("GET", "/v1/voices", key).get("voices", [])


def cmd_voices(args):
    voices = fetch_voices(get_key())
    s = (args.search or "").lower()
    for v in voices:
        labels = v.get("labels") or {}
        desc = ", ".join(str(x) for x in labels.values() if x)
        line = "%-22s %-24s %-10s %s" % (v["voice_id"], v["name"][:24], v.get("category", ""), desc)
        if not s or s in line.lower():
            print(line)


def cmd_models(_args):
    for m in request("GET", "/v1/models", get_key()):
        if m.get("can_do_text_to_speech"):
            langs = ", ".join(l.get("name", "") for l in m.get("languages", [])[:6])
            print("%-28s %s  [%s...]" % (m["model_id"], m.get("name", ""), langs))


def resolve_voice(key, voice):
    if re.fullmatch(r"[A-Za-z0-9]{20}", voice):
        return voice
    for v in fetch_voices(key):
        if v["name"].lower() == voice.lower() or v["name"].lower().startswith(voice.lower()):
            return v["voice_id"]
    sys.exit("Voice '%s' not found. Run the 'voices' command to see options." % voice)


def cmd_default(args):
    cfg = load_config()
    if args.voice:
        cfg["voice_id"] = resolve_voice(get_key(), args.voice)
    if args.model:
        cfg["model_id"] = args.model
    if args.voice or args.model:
        save_config(cfg)
        print("Saved.")
    print(json.dumps({k: cfg[k] for k in DEFAULTS}, indent=2))


def split_text(text, limit=CHUNK_CHARS):
    text = text.strip()
    if len(text) <= limit:
        return [text]
    parts = re.split(r"(?<=[.!?。])\s+|\n{2,}", text)
    chunks, cur = [], ""
    for p in parts:
        p = p.strip()
        if not p:
            continue
        while len(p) > limit:  # pathological long sentence
            chunks.append(p[:limit])
            p = p[limit:]
        if cur and len(cur) + 1 + len(p) > limit:
            chunks.append(cur)
            cur = p
        else:
            cur = (cur + " " + p).strip()
    if cur:
        chunks.append(cur)
    return chunks


def srt_time(t):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return "%02d:%02d:%02d,%03d" % (h, m, s, ms)


def build_srt(chars, starts, ends, max_chars=42):
    """Group character alignment into subtitle cues split on punctuation / length."""
    cues, buf, cstart = [], "", None
    for ch, st, en in zip(chars, starts, ends):
        if cstart is None:
            if ch.isspace():
                continue
            cstart = st
        buf += ch
        cend = en
        if (ch in ".!?,;:" and len(buf) > 12) or (ch == " " and len(buf) >= max_chars):
            cues.append((cstart, cend, buf.strip()))
            buf, cstart = "", None
    if buf.strip():
        cues.append((cstart, cend, buf.strip()))
    return "\n".join("%d\n%s --> %s\n%s\n" % (i, srt_time(a), srt_time(b), t)
                     for i, (a, b, t) in enumerate(cues, 1))


def cmd_tts(args):
    if args.file:
        with open(os.path.expanduser(args.file)) as f:
            text = f.read()
    elif args.text:
        text = args.text
    else:
        text = sys.stdin.read()
    if not text.strip():
        sys.exit("No text given.")

    key = get_key()
    cfg = load_config()
    voice_id = resolve_voice(key, args.voice) if args.voice else cfg["voice_id"]
    model_id = args.model or cfg["model_id"]
    out = args.output or os.path.join(
        DEFAULT_OUT_DIR, "voiceover_%s.mp3" % datetime.now().strftime("%Y%m%d_%H%M%S"))
    out = os.path.abspath(os.path.expanduser(out))
    os.makedirs(os.path.dirname(out), exist_ok=True)

    settings = {"stability": args.stability, "similarity_boost": args.similarity,
                "style": args.style, "use_speaker_boost": True}
    if args.speed is not None:
        settings["speed"] = args.speed

    chunks = split_text(text)
    audio = b""
    all_chars, all_starts, all_ends, offset = [], [], [], 0.0
    for i, chunk in enumerate(chunks):
        body = {"text": chunk, "model_id": model_id, "voice_settings": settings}
        if args.language:
            body["language_code"] = args.language
        if i > 0:
            body["previous_text"] = chunks[i - 1][-500:]
        if i < len(chunks) - 1:
            body["next_text"] = chunks[i + 1][:500]
        path = "/v1/text-to-speech/%s" % voice_id
        q = "?output_format=%s" % cfg["output_format"]
        if len(chunks) > 1:
            print("Generating part %d/%d (%d chars)..." % (i + 1, len(chunks), len(chunk)), file=sys.stderr)
        if args.srt:
            res = request("POST", path + "/with-timestamps" + q, key, body)
            audio += base64.b64decode(res["audio_base64"])
            al = res.get("alignment") or {}
            ends = al.get("character_end_times_seconds", [])
            all_chars += al.get("characters", []) + [" "]
            all_starts += [t + offset for t in al.get("character_start_times_seconds", [])] + [offset + (ends[-1] if ends else 0)]
            all_ends += [t + offset for t in ends] + [offset + (ends[-1] if ends else 0)]
            offset += ends[-1] if ends else 0
        else:
            audio += request("POST", path + q, key, body, raw=True)

    with open(out, "wb") as f:
        f.write(audio)
    print("Saved voice-over: %s (%d chars, voice %s, model %s)" % (out, len(text), voice_id, model_id))
    if args.srt:
        srt_path = os.path.splitext(out)[0] + ".srt"
        with open(srt_path, "w") as f:
            f.write(build_srt(all_chars, all_starts, all_ends))
        print("Saved subtitles:  %s" % srt_path)
    if args.play:
        subprocess.run(["afplay", out])


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("setup").set_defaults(fn=cmd_setup)
    sub.add_parser("check").set_defaults(fn=cmd_check)
    sv = sub.add_parser("voices"); sv.add_argument("--search"); sv.set_defaults(fn=cmd_voices)
    sub.add_parser("models").set_defaults(fn=cmd_models)
    sd = sub.add_parser("default"); sd.add_argument("--voice"); sd.add_argument("--model")
    sd.set_defaults(fn=cmd_default)
    st = sub.add_parser("tts")
    st.add_argument("--text"); st.add_argument("--file")
    st.add_argument("-o", "--output")
    st.add_argument("--voice", help="voice name or id (default from config)")
    st.add_argument("--model")
    st.add_argument("--language", help="ISO 639-1 code, e.g. ms, en (optional)")
    st.add_argument("--stability", type=float, default=0.5)
    st.add_argument("--similarity", type=float, default=0.75)
    st.add_argument("--style", type=float, default=0.0)
    st.add_argument("--speed", type=float, help="0.7-1.2")
    st.add_argument("--srt", action="store_true", help="also write .srt subtitles")
    st.add_argument("--play", action="store_true")
    st.set_defaults(fn=cmd_tts)
    args = p.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
