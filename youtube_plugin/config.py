"""Configuration and quota accounting.

Resolution order, highest wins: environment, then config.toml, then defaults.
An optional 1Password reference is consulted only when the direct value is absent,
so a working config never blocks on the op CLI (which has hung on approval before).
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tomllib
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

CONFIG_DIR = Path(os.environ.get("YOUTUBE_PLUGIN_HOME", Path.home() / ".config" / "youtube-plugin"))
CONFIG_PATH = CONFIG_DIR / "config.toml"
CLIENTS_PATH = CONFIG_DIR / "clients.toml"
CACHE_DIR = CONFIG_DIR / "cache"
QUOTA_PATH = CONFIG_DIR / "quota.json"

DAILY_QUOTA = 10_000  # Google's default for the shared bucket.

# Per-method unit costs, from https://developers.google.com/youtube/v3/determine_quota_cost
COSTS = {
    "channels.list": 1,
    "playlistItems.list": 1,
    "videos.list": 1,
    "commentThreads.list": 1,
    "comments.list": 1,
    "captions.list": 50,
    "captions.download": 200,
}


class ConfigError(RuntimeError):
    """User-facing configuration failure."""


@dataclass
class Config:
    api_key: str | None = None
    cache_enabled: bool = True
    cache_ttl_hours: int = 24
    quota_warn_at: float = 0.8

    def require_key(self) -> None:
        if self.api_key:
            return
        raise ConfigError(
            "No YouTube API key configured.\n"
            "1. Enable the YouTube Data API v3 on your Google Cloud project\n"
            "   (Julian's is pro-marketing-494311)\n"
            "2. Create an API key under APIs and Services, Credentials\n"
            f"3. Put it in {CONFIG_PATH} as api_key under [youtube], or set "
            "YOUTUBE_API_KEY\n"
            "Then run `youtube doctor`."
        )


def _resolve_op_ref(ref: str, account: str | None) -> str | None:
    """Read a secret from 1Password, degrading to None rather than raising."""
    if not shutil.which("op"):
        return None
    cmd = ["op", "read", ref] + (["--account", account] if account else [])
    try:
        done = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
    except (subprocess.TimeoutExpired, OSError):
        return None
    return done.stdout.strip() or None if done.returncode == 0 else None


def _read_toml(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        with path.open("rb") as handle:
            return tomllib.load(handle)
    except (tomllib.TOMLDecodeError, OSError) as exc:
        raise ConfigError(f"Could not read {path}: {exc}") from exc


def load(path: Path | None = None) -> Config:
    raw = _read_toml(path or CONFIG_PATH)
    yt = raw.get("youtube", {})
    cache = raw.get("cache", {})
    op = yt.get("op", {})

    api_key = os.environ.get("YOUTUBE_API_KEY") or yt.get("api_key")
    if not api_key and op.get("api_key_ref"):
        api_key = _resolve_op_ref(op["api_key_ref"], op.get("account"))

    return Config(
        api_key=api_key,
        cache_enabled=bool(cache.get("enabled", True)),
        cache_ttl_hours=int(cache.get("ttl_hours", 24)),
        quota_warn_at=float(yt.get("quota_warn_at", 0.8)),
    )


# -- quota -------------------------------------------------------------
# Google resets daily quota at midnight Pacific, so the ledger is keyed by
# Pacific date rather than local date. Getting this wrong would silently
# reset the counter at the wrong moment and let a sweep blow the budget.


def pacific_date(now: datetime | None = None) -> str:
    """Current date in US Pacific. Uses a fixed -8/-7 approximation only as a
    fallback; zoneinfo is preferred and present on all supported Pythons."""
    now = now or datetime.now(timezone.utc)
    try:
        from zoneinfo import ZoneInfo

        return now.astimezone(ZoneInfo("America/Los_Angeles")).date().isoformat()
    except Exception:  # pragma: no cover - zoneinfo missing is not expected
        return (now - timedelta(hours=8)).date().isoformat()


class Quota:
    """Per-day unit ledger persisted to disk."""

    def __init__(self, path: Path | None = None, daily: int = DAILY_QUOTA):
        self.path = path or QUOTA_PATH
        self.daily = daily

    def _load(self) -> dict:
        if not self.path.exists():
            return {}
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}

    def spent(self) -> int:
        data = self._load()
        return int(data.get(pacific_date(), 0))

    def remaining(self) -> int:
        return max(0, self.daily - self.spent())

    def charge(self, method: str, calls: int = 1) -> int:
        """Record `calls` invocations of `method`. Returns units charged."""
        units = COSTS.get(method, 1) * calls
        data = self._load()
        today = pacific_date()
        data = {today: int(data.get(today, 0)) + units}  # drop old days
        self.path.parent.mkdir(parents=True, exist_ok=True)
        try:
            self.path.write_text(json.dumps(data), encoding="utf-8")
        except OSError:
            pass  # ledger failure must not fail the command
        return units

    def estimate(self, plan: dict[str, int]) -> int:
        """Units a plan of {method: call_count} would cost."""
        return sum(COSTS.get(m, 1) * n for m, n in plan.items())

    def report(self) -> dict:
        spent = self.spent()
        return {
            "pacific_date": pacific_date(),
            "spent": spent,
            "remaining": self.remaining(),
            "daily_limit": self.daily,
            "percent_used": round(100 * spent / self.daily, 1) if self.daily else 0.0,
            "note": (
                "Local estimate from this tool's own calls, not read back from Google. "
                "Other tools sharing the project also consume the same quota."
            ),
        }
