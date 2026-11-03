#!/usr/bin/env bash
# VGC Repo by Coach Am: one-time setup (macOS or Linux / Claude Code cloud).
# Installs Node.js, ffmpeg, the Python packages the styles use, and the HyperFrames render browser.
set -e
say() { printf "\n\033[1m%s\033[0m\n" "$1"; }
has() { command -v "$1" >/dev/null 2>&1; }

OS="$(uname -s)"
say "1/4 Node.js + ffmpeg"
if [ "$OS" = "Darwin" ]; then
  if ! has brew; then
    echo "Homebrew belum ada. Pasang dari https://brew.sh dahulu, kemudian jalankan semula: bash setup.sh"; exit 1
  fi
  has node   || brew install node
  has ffmpeg || brew install ffmpeg
else
  SUDO=""; [ "$(id -u)" != "0" ] && has sudo && SUDO="sudo"
  if ! has node || ! has ffmpeg; then
    $SUDO apt-get update -y
    has ffmpeg || $SUDO apt-get install -y ffmpeg
    has node   || { curl -fsSL https://deb.nodesource.com/setup_20.x | $SUDO bash - && $SUDO apt-get install -y nodejs; }
  fi
fi
node --version; ffmpeg -version | head -1

say "2/4 Python packages"
# Pick a python that can install packages (macOS system python first, it is what the style scripts were tested with)
PY=python3; [ "$OS" = "Darwin" ] && [ -x /usr/bin/python3 ] && PY=/usr/bin/python3
$PY -m pip install --user --upgrade numpy scipy pillow opencv-python-headless pypdf soundfile faster-whisper 2>/dev/null \
  || $PY -m pip install --user --break-system-packages --upgrade numpy scipy pillow opencv-python-headless pypdf soundfile faster-whisper
$PY -c "import numpy, scipy, PIL, cv2, pypdf; print('python ok:', '$PY')"

say "3/4 HyperFrames + render browser"
npx --yes hyperframes --version
npx --yes hyperframes browser ensure

say "4/4 Check"
npx --yes hyperframes doctor || true
mkdir -p input output work
echo
echo "Siap! Letak fail dalam input/ dan beritahu Claude style yang kau nak."
