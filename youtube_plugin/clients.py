"""Client registry: maps a short client name to an output path and its channels.

Keeps Pro Marketing client corpora from mixing. A client's research lands in that
client's own folder, wherever Julian files it, rather than in a tool-owned directory.

Example ~/.config/youtube-plugin/clients.toml

    [clients.idd]
    name = "Institute of Digital Dentistry"
    path = "~/code/idd-world/research/voc"
    channels = ["@InstituteofDigitalDentistry"]
    competitors = ["@DigitalSmileDesignOfficial"]

    [clients.acme]
    name = "Acme Dental"
    path = "~/code/clients/acme/voc"
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .config import CLIENTS_PATH, ConfigError, _read_toml


@dataclass
class Client:
    slug: str
    name: str
    path: Path
    channels: list[str] = field(default_factory=list)
    competitors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "slug": self.slug,
            "name": self.name,
            "path": str(self.path),
            "path_exists": self.path.exists(),
            "channels": self.channels,
            "competitors": self.competitors,
        }


def _resolve_path(raw: str, slug: str) -> Path:
    path = Path(raw).expanduser()
    if not path.is_absolute():
        raise ConfigError(
            f"Client {slug!r} has a relative path {raw!r}. Use an absolute path so "
            f"output does not depend on the working directory."
        )
    return path


def load_all(path: Path | None = None) -> dict[str, Client]:
    raw = _read_toml(path or CLIENTS_PATH)
    out: dict[str, Client] = {}
    for slug, entry in (raw.get("clients") or {}).items():
        if not isinstance(entry, dict) or "path" not in entry:
            raise ConfigError(f"Client {slug!r} is missing a path.")
        out[slug] = Client(
            slug=slug,
            name=entry.get("name", slug),
            path=_resolve_path(entry["path"], slug),
            channels=list(entry.get("channels", [])),
            competitors=list(entry.get("competitors", [])),
        )
    return out


def get(slug: str, path: Path | None = None) -> Client:
    clients = load_all(path)
    if slug not in clients:
        known = ", ".join(sorted(clients)) or "none configured"
        raise ConfigError(
            f"Unknown client {slug!r}. Known clients: {known}.\n"
            f"Add one to {path or CLIENTS_PATH}, or pass --out with an explicit path."
        )
    return clients[slug]


def resolve_output(
    client_slug: str | None,
    out: str | None,
    filename: str,
    clients_path: Path | None = None,
) -> Path | None:
    """Where a command should write. None means stdout.

    --out wins over --client so an explicit path is always obeyed.
    """
    if out:
        target = Path(out).expanduser()
        return target / filename if target.is_dir() else target
    if client_slug:
        return get(client_slug, clients_path).path / filename
    return None


def safe_filename(*parts: str) -> str:
    """Build a filename from untrusted pieces (channel handles, video ids).

    Handles and titles come from the API, so they are attacker-influenced in the
    sense that anyone can name a channel anything. Strip to a conservative set
    rather than trusting them in a path.
    """
    cleaned = []
    for part in parts:
        keep = "".join(c if (c.isalnum() or c in "-_") else "-" for c in part.strip())
        keep = "-".join(filter(None, keep.split("-")))
        if keep:
            cleaned.append(keep[:60])
    return ("-".join(cleaned) or "output")[:180]
