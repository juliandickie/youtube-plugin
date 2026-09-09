"""YouTube Data API v3 transport.

Plain urllib rather than google-api-python-client: for API-key reads the official
client mostly wraps the same GET and still leaves pagination and quota to you, so v1
stays dependency-free.

Every call charges the local quota ledger. That ledger is an estimate of this tool's
own spend, not a read-back from Google, and says so in its own report.
"""

from __future__ import annotations

import hashlib
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Iterator

from .config import CACHE_DIR, Config, Quota

BASE = "https://www.googleapis.com/youtube/v3"
TIMEOUT = 30

VIDEO_ID_RE = re.compile(r"(?:v=|/shorts/|youtu\.be/|/embed/)([A-Za-z0-9_-]{11})")
BARE_VIDEO_RE = re.compile(r"^[A-Za-z0-9_-]{11}$")
HANDLE_RE = re.compile(r"youtube\.com/(@[A-Za-z0-9._-]+)")
CHANNEL_ID_RE = re.compile(r"youtube\.com/channel/(UC[A-Za-z0-9_-]{22})")


class YouTubeError(RuntimeError):
    """User-facing failure talking to YouTube."""


def parse_video_id(value: str) -> str:
    """Accept a watch URL, a Shorts URL, a youtu.be link, or a bare id."""
    value = value.strip()
    if BARE_VIDEO_RE.match(value):
        return value
    match = VIDEO_ID_RE.search(value)
    if match:
        return match.group(1)
    raise YouTubeError(f"Could not read a video id out of {value!r}.")


def parse_channel_ref(value: str) -> tuple[str, str]:
    """Return (kind, value) where kind is 'id' or 'handle'."""
    value = value.strip()
    match = CHANNEL_ID_RE.search(value)
    if match:
        return "id", match.group(1)
    match = HANDLE_RE.search(value)
    if match:
        return "handle", match.group(1)
    if value.startswith("@"):
        return "handle", value
    if re.match(r"^UC[A-Za-z0-9_-]{22}$", value):
        return "id", value
    raise YouTubeError(
        f"Could not read a channel out of {value!r}. Pass a @handle, a channel URL, "
        f"or a UC... channel id."
    )


class Cache:
    def __init__(self, enabled: bool, ttl_hours: int, directory: Path | None = None):
        self.enabled = enabled
        self.ttl = ttl_hours * 3600
        self.dir = directory or CACHE_DIR

    def _path(self, signature: str) -> Path:
        return self.dir / f"{hashlib.sha256(signature.encode()).hexdigest()[:32]}.json"

    def get(self, signature: str) -> Any | None:
        if not self.enabled:
            return None
        path = self._path(signature)
        if not path.exists():
            return None
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return None
        if time.time() - payload.get("cached_at", 0) > self.ttl:
            return None
        return payload.get("data")

    def put(self, signature: str, data: Any) -> None:
        if not self.enabled:
            return
        self.dir.mkdir(parents=True, exist_ok=True)
        try:
            self._path(signature).write_text(
                json.dumps({"cached_at": time.time(), "data": data}), encoding="utf-8"
            )
        except OSError:
            pass

    def info(self) -> dict:
        if not self.dir.exists():
            return {"path": str(self.dir), "entries": 0, "bytes": 0}
        files = list(self.dir.glob("*.json"))
        return {
            "path": str(self.dir),
            "entries": len(files),
            "bytes": sum(f.stat().st_size for f in files),
        }

    def clear(self) -> int:
        if not self.dir.exists():
            return 0
        files = list(self.dir.glob("*.json"))
        for f in files:
            f.unlink(missing_ok=True)
        return len(files)


class Api:
    """Thin Data API client. One `get` per HTTP call, one quota charge per call."""

    def __init__(self, config: Config, quota: Quota | None = None, cache: Cache | None = None):
        self.config = config
        self.quota = quota or Quota()
        self.cache = cache or Cache(config.cache_enabled, config.cache_ttl_hours)

    def get(self, method: str, params: dict, use_cache: bool = True) -> dict:
        """Call one Data API method. `method` is e.g. 'commentThreads.list'."""
        self.config.require_key()
        resource = method.split(".")[0]
        query = {k: v for k, v in params.items() if v is not None}
        signature = f"{method}:{json.dumps(query, sort_keys=True)}"

        if use_cache:
            hit = self.cache.get(signature)
            if hit is not None:
                return hit

        query["key"] = self.config.api_key
        url = f"{BASE}/{resource}?{urllib.parse.urlencode(query)}"
        request = urllib.request.Request(url, headers={"Accept": "application/json"})

        try:
            with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
                data = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            raise YouTubeError(_http_message(exc, method)) from exc
        except urllib.error.URLError as exc:
            raise YouTubeError(f"Network error calling {method}: {exc.reason}") from exc

        self.quota.charge(method)
        self.cache.put(signature, data)
        return data

    def paginate(
        self, method: str, params: dict, *, max_items: int | None = None, use_cache: bool = True
    ) -> Iterator[dict]:
        """Yield items across pages, following nextPageToken.

        Stops at max_items, at the last page, or when quota runs out. Quota
        exhaustion mid-pagination raises rather than returning a short list
        silently, because a truncated corpus that looks complete is the failure
        mode this whole tool is built to avoid.
        """
        seen = 0
        token = None
        while True:
            if self.quota.remaining() <= 0:
                raise YouTubeError(
                    f"Daily quota exhausted after {seen} items. "
                    f"Run `youtube quota` for details; it resets midnight Pacific."
                )
            page = self.get(method, {**params, "pageToken": token}, use_cache=use_cache)
            for item in page.get("items", []):
                yield item
                seen += 1
                if max_items and seen >= max_items:
                    return
            token = page.get("nextPageToken")
            if not token:
                return


def _http_message(exc: urllib.error.HTTPError, method: str) -> str:
    """Turn Google's error envelope into something actionable."""
    try:
        body = json.loads(exc.read().decode("utf-8"))
        error = body.get("error", {})
        reason = (error.get("errors") or [{}])[0].get("reason", "")
        message = error.get("message", "")
    except Exception:
        reason, message = "", ""

    if reason in ("quotaExceeded", "dailyLimitExceeded"):
        return (
            f"YouTube reports the daily quota is exhausted ({method}). "
            f"It resets at midnight Pacific. Note this is Google's count, which "
            f"includes anything else using the same Cloud project."
        )
    if reason == "commentsDisabled":
        return "Comments are disabled on this video. Nothing to fetch."
    if reason in ("videoNotFound", "notFound"):
        return f"Not found ({method}). Check the id, and that the video or channel is public."
    if exc.code == 403:
        return (
            f"Forbidden calling {method}: {message or 'no detail'}. "
            f"Common causes: the API key is restricted, or the YouTube Data API v3 is "
            f"not enabled on the project."
        )
    if exc.code == 400 and "API key not valid" in message:
        return "The API key is not valid. Check it, and that it is unrestricted or allows the YouTube Data API."
    return f"HTTP {exc.code} calling {method}: {message or exc.reason}"
