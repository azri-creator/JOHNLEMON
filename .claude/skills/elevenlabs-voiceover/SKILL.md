---
name: elevenlabs-voiceover
description: Generate voice-over audio (MP3, optional SRT subtitles) with ElevenLabs text-to-speech. Use whenever the user wants a voice over, VO, narration, suara, audio for a video/reel/TikTok/YouTube, or to list/change ElevenLabs voices. Works in Bahasa Melayu and English.
---

# ElevenLabs voice-over

Script: `.claude/skills/elevenlabs-voiceover/scripts/voiceover.py` (stdlib Python, no install).
API key lives in macOS Keychain (service `elevenlabs-api-key`) or env `ELEVENLABS_API_KEY`.
Never print, echo, or ask the user to paste the key in chat. If the key is missing, tell the user to run
`python3 .claude/skills/elevenlabs-voiceover/scripts/voiceover.py setup` in their own Terminal.

## Workflow

1. If the user has no script yet, write the voice-over script first and show it for approval
   (keep it natural for speech: short sentences, numbers written the way they're spoken).
2. Save the script to a `.txt` file next to the project (or in the scratchpad), then generate:

```bash
python3 .claude/skills/elevenlabs-voiceover/scripts/voiceover.py tts --file script.txt -o ~/Movies/Voiceover/<name>.mp3 --srt
```

   - `--voice "<name or id>"` to pick a voice (else the saved default).
   - `--language ms` forces Bahasa Melayu pronunciation if needed; `--speed 0.9`-`1.1` to adjust pace.
   - `--stability` (0-1, lower = more expressive), `--style` (0-1, more dramatic).
   - `--srt` also writes matching subtitles for video editors (CapCut, Premiere, DaVinci).
   - Long scripts are split and stitched automatically.
3. Report the output path(s). Default output folder: `~/Movies/Voiceover/`.

## Other commands

- `check` - verify the key and show remaining character quota (do this before big jobs).
- `voices [--search female]` - list voices on the account.
- `default --voice "<name>" [--model <id>]` - save default voice/model.
- `models` - list TTS models. Default `eleven_multilingual_v2` (best quality, supports Malay).
  `eleven_flash_v2_5` is cheaper/faster.

Every character generated costs ElevenLabs credits; confirm with the user before generating very long scripts or many takes.
