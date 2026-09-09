"""MCP surface.

Every tool here is a thin wrapper over youtube_plugin.core, the same functions the
CLI calls. No logic lives in this file, so the two surfaces cannot drift.

Named mcp_server rather than mcp so it does not shadow the installed `mcp` package.
"""

from __future__ import annotations

import json

from . import core, formats
from .config import load as load_config

INSTRUCTIONS = """Read YouTube for research via the official Data API.

Comments carry full reply resolution: YouTube returns only a subset of replies inline,
and these tools fetch the remainder, so a thread is complete rather than quietly
truncated.

The `voc` format shapes comments for an Ultimate Message Map. It applies a MECHANICAL
prefilter only (deleted, bots, very short, duplicates) and reports every drop. It does
NOT apply the sticky-VOC filter, which is a human judgement, and you must not report
that it did.

Captions: the official API cannot return captions for videos the authenticated user
cannot edit. youtube_captions with via_yt_dlp=true retrieves them outside the official
API. Only set that when the user has asked for it, and say so in your answer.
"""


def _server_class():
    """Return the server class across MCP SDK majors.

    mcp 2.x renamed FastMCP to MCPServer. The decorator, run() and list_tools()
    signatures are otherwise compatible, so one shim covers both rather than pinning
    the SDK and going stale.
    """
    try:
        from mcp.server.mcpserver import MCPServer  # mcp >= 2

        return MCPServer
    except ImportError:
        pass
    try:
        from mcp.server.fastmcp import FastMCP  # mcp 1.x

        return FastMCP
    except ImportError as exc:
        raise SystemExit(
            f"Could not load an MCP server class from the installed SDK ({exc}).\n"
            f"Run scripts/install.sh to reinstall the [mcp] extra. If the SDK has "
            f"changed its API again, this shim in mcp_server.py needs a new branch."
        ) from exc


def build():
    server = _server_class()("youtube", instructions=INSTRUCTIONS)

    @server.tool()
    def youtube_comments(
        video: str, limit: int | None = None, output: str = "voc",
        min_length: int = 80, keep_all: bool = False, lang: str | None = None,
    ) -> str:
        """Comments for one video with replies fully resolved.

        video: URL or 11-character id. limit caps TOP-LEVEL comments (whole threads
        are kept). output: json, markdown, or voc.
        """
        cfg = load_config()
        v, stats = core.video_comments(cfg, video, limit=limit)
        kwargs = {}
        if output == "voc":
            kwargs = {"min_length": min_length, "keep_all": keep_all}
            if lang:
                kwargs["languages"] = [s.strip().lower() for s in lang.split(",")]
        return formats.render(v, output, **kwargs)

    @server.tool()
    def youtube_channel(channel: str, videos: int = 0) -> str:
        """Channel metadata by @handle, URL, or UC id. Set videos to also list uploads."""
        cfg = load_config()
        if videos:
            ch, vids = core.channel_videos(cfg, channel, limit=videos)
            return formats.to_json({"channel": ch.to_dict(), "videos": [v.to_dict() for v in vids]})
        return formats.to_json(core.channel_info(cfg, channel))

    @server.tool()
    def youtube_sweep(
        channel: str, videos: int = 10, comments_per_video: int | None = 100,
        sort: str = "discussed", pool: int | None = None, output: str = "voc",
    ) -> str:
        """Comments across a channel's videos. Works on any public channel, including
        competitors. sort: discussed (best for research), popular, or recent.

        For discussed and popular, ranking spans EVERY video on the channel by
        default, because ranking only the newest page returns whatever was posted
        this week rather than what people actually discussed. pool caps that
        candidate set if a channel is enormous.

        Costs roughly one unit per 50 videos listed, one per 50 hydrated, then one
        per 100 comments. Check youtube_quota first for a large sweep.
        """
        cfg = load_config()
        _, vids, totals = core.sweep(
            cfg, channel, videos_limit=videos,
            comments_limit=comments_per_video, sort_by=sort, pool=pool,
        )
        with_comments = [v for v in vids if v.comments]
        body = formats.render(with_comments, output) if with_comments else "[]"
        return json.dumps({"totals": totals, "data": json.loads(body) if output != "markdown" else body}, indent=2)

    @server.tool()
    def youtube_captions(video: str, via_yt_dlp: bool = False, lang: str = "en") -> str:
        """Captions for a video.

        The official API only returns captions for videos the authenticated user can
        edit, and needs OAuth which this version does not yet have. via_yt_dlp=true
        retrieves them OUTSIDE the official API. Only use it when the user asked for
        it, and tell them that is what happened.
        """
        cfg = load_config()
        return formats.to_json(
            core.captions(cfg, video, via_yt_dlp=via_yt_dlp, languages=lang.split(","))
        )

    @server.tool()
    def youtube_quota() -> str:
        """Quota units this tool has spent today against the 10,000 daily limit."""
        return formats.to_json(core.quota_report(load_config()))

    return server


def main() -> None:
    build().run()


if __name__ == "__main__":
    main()
