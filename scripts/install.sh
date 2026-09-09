#!/usr/bin/env bash
# Build the venv and put `youtube` on PATH. Idempotent, safe to re-run.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV="${YOUTUBE_PLUGIN_VENV:-$HOME/.local/share/youtube-plugin/venv}"
BINDIR="${YOUTUBE_PLUGIN_BIN:-$HOME/.local/bin}"
PYTHON="${PYTHON:-python3}"

echo "repo: $REPO"
echo "venv: $VENV"
echo "bin:  $BINDIR/youtube"
echo

[ -x "$VENV/bin/python" ] || { echo "Creating venv..."; "$PYTHON" -m venv "$VENV"; }

"$VENV/bin/python" -m pip install --quiet --upgrade pip
"$VENV/bin/python" -m pip install --quiet -e "$REPO[mcp]"

mkdir -p "$BINDIR"
ln -sf "$REPO/bin/youtube" "$BINDIR/youtube"

echo "Installed. Verifying..."
"$BINDIR/youtube" --version

command -v yt-dlp >/dev/null 2>&1 \
  && echo "yt-dlp: $(command -v yt-dlp)" \
  || echo "yt-dlp: not installed (only needed for --via-yt-dlp). brew install yt-dlp"

case ":$PATH:" in
  *":$BINDIR:"*) ;;
  *) echo; echo "NOTE: $BINDIR is not on your PATH." ;;
esac

echo
echo "Next: enable YouTube Data API v3, create an API key, then \`youtube doctor\`."
