"""Captions: two paths, and the boundary between them is the point of this module.

OFFICIAL PATH (captions.list, captions.download)
    Sanctioned, but bounded by ownership. Google's reference for captions.download
    states it "requires the user to have permission to edit the video", enforced with
    a 403. So the official API can tell you what caption tracks exist on anyone's
    video, and can only hand you the text of videos you own or edit. It also needs
    OAuth, not an API key, which lands with v2.

YT-DLP PATH (--via-yt-dlp)
    Retrieves captions for videos you do not own, which the official API does not
    offer at all. Julian asked for this explicitly, after being told the trade.

    Rules, which exist so this stays honest rather than becoming a silent fallback:

    1. It runs ONLY when the caller passes via_yt_dlp=True. Never from a retry, an
       except branch, or a "the official one failed so let us try the other" path.
    2. Every record it produces carries official_api=False and source="yt-dlp".
    3. yt-dlp is invoked as a subprocess and never imported, so its behaviour cannot
       leak into the rest of the tool.

    A future session tempted to make this a transparent fallback should not. The harm
    is not using yt-dlp; it is a reader believing a transcript came from the
    sanctioned path when it did not.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path

from .api import Api, YouTubeError

YT_DLP_TIMEOUT = 120


class CaptionsUnavailable(YouTubeError):
    """Captions could not be retrieved by the requested path."""


def list_tracks(api: Api, video_id: str, use_cache: bool = True) -> list[dict]:
    """Caption track metadata for any video. 50 units. Needs OAuth (v2).

    Kept here so the v2 wiring is obvious, but it will raise until OAuth exists.
    """
    raise CaptionsUnavailable(
        "captions.list needs OAuth, which arrives with v2 of this plugin. "
        "For now use --via-yt-dlp, or read the transcript in the YouTube UI."
    )


def yt_dlp_available() -> str | None:
    return shutil.which("yt-dlp")


def via_yt_dlp(video_id: str, *, languages: list[str] | None = None, auto: bool = True) -> dict:
    """Fetch captions with yt-dlp. OUTSIDE the official API surface, by request.

    Returns a record stamped official_api=False. Raises if yt-dlp is missing or the
    video has no matching caption track.
    """
    binary = yt_dlp_available()
    if not binary:
        raise CaptionsUnavailable(
            "yt-dlp is not installed, so the --via-yt-dlp path cannot run.\n"
            "Install it with: brew install yt-dlp"
        )

    langs = languages or ["en"]
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "cap"
        cmd = [
            binary,
            "--skip-download",
            "--write-subs",
            *(["--write-auto-subs"] if auto else []),
            "--sub-langs", ",".join(langs),
            "--sub-format", "vtt",
            "--output", str(out),
            f"https://www.youtube.com/watch?v={video_id}",
        ]
        try:
            done = subprocess.run(cmd, capture_output=True, text=True, timeout=YT_DLP_TIMEOUT)
        except subprocess.TimeoutExpired as exc:
            raise CaptionsUnavailable(f"yt-dlp timed out after {YT_DLP_TIMEOUT}s.") from exc

        files = sorted(Path(tmp).glob("*.vtt"))
        if not files:
            detail = (done.stderr or done.stdout or "").strip().splitlines()
            tail = detail[-1] if detail else "no output"
            raise CaptionsUnavailable(
                f"yt-dlp returned no caption track for {video_id} in {','.join(langs)}. "
                f"Last message: {tail}"
            )

        track = files[0]
        text = track.read_text(encoding="utf-8", errors="replace")

    return {
        "video_id": video_id,
        "language": track.stem.split(".")[-1],
        "format": "vtt",
        "text": text,
        "plain_text": vtt_to_text(text),
        "source": "yt-dlp",
        "official_api": False,
        "note": (
            "Retrieved with yt-dlp, OUTSIDE the official YouTube API. The API's "
            "captions.download is restricted to videos you have permission to edit, "
            "so there is no sanctioned route for third-party transcripts."
        ),
    }


def vtt_to_text(vtt: str) -> str:
    """Strip WebVTT timing and markup to running prose, de-duplicating the rolling
    repeats that auto-captions produce."""
    lines: list[str] = []
    for raw in vtt.splitlines():
        line = raw.strip()
        if not line or line.startswith(("WEBVTT", "Kind:", "Language:", "NOTE")):
            continue
        if "-->" in line or line.isdigit():
            continue
        cleaned = _strip_tags(line)
        if cleaned and (not lines or lines[-1] != cleaned):
            lines.append(cleaned)
    return "\n".join(lines)


def _strip_tags(line: str) -> str:
    out, depth = [], 0
    for char in line:
        if char == "<":
            depth += 1
        elif char == ">":
            depth = max(0, depth - 1)
        elif depth == 0:
            out.append(char)
    return "".join(out).strip()
