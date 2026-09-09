"""Renderers. json for machines, markdown for reading, voc for the message map."""

from __future__ import annotations

import json
from typing import Any

from . import voc as voc_module
from .models import Channel, Video

FORMATS = ("json", "markdown", "voc")


def render(data: Any, fmt: str, **voc_kwargs) -> str:
    if fmt == "json":
        return to_json(data)
    if fmt == "voc":
        return to_json(_voc(data, **voc_kwargs))
    if fmt == "markdown":
        return _markdown(data)
    raise ValueError(f"Unknown format {fmt!r}. Choose from {', '.join(FORMATS)}.")


def to_json(data: Any) -> str:
    def default(obj):
        if hasattr(obj, "to_dict"):
            return obj.to_dict()
        raise TypeError(f"not serializable: {type(obj)}")

    return json.dumps(data, indent=2, ensure_ascii=False, default=default)


def _voc(data: Any, **kwargs) -> dict:
    if isinstance(data, Video):
        return voc_module.shape(data, **kwargs)
    if isinstance(data, list) and data and isinstance(data[0], Video):
        return voc_module.shape_many(data, **kwargs)
    raise ValueError(
        "The voc format needs a video or a list of videos. Channel metadata and "
        "captions have no VOC shape."
    )


def _markdown(data: Any) -> str:
    if isinstance(data, Video):
        return _video_markdown(data)
    if isinstance(data, Channel):
        return _channel_markdown(data)
    if isinstance(data, list):
        if data and isinstance(data[0], Video):
            return "\n\n".join(
                _video_markdown(v) if v.comments else _video_summary(v) for v in data
            )
        return to_json(data)
    if isinstance(data, dict) and data.get("source") == "yt-dlp":
        return (
            f"# Captions for {data['video_id']} ({data.get('language')})\n\n"
            f"> Retrieved with yt-dlp, outside the official API.\n\n"
            f"{data.get('plain_text', '')}"
        )
    return to_json(data)


def _channel_markdown(channel: Channel) -> str:
    return "\n".join(
        [
            f"# {channel.title}",
            "",
            f"{channel.url}",
            f"{channel.subscribers or '?'} subscribers, {channel.video_count or '?'} videos, "
            f"{channel.view_count or '?'} total views",
            "",
            channel.description or "",
        ]
    )


def _video_summary(video: Video) -> str:
    bits = [f"{video.views} views" if video.views is not None else None,
            f"{video.comment_count} comments" if video.comment_count is not None else None]
    meta = ", ".join(b for b in bits if b)
    return f"- **{video.title}** ({meta})\n  {video.url}"


def _video_markdown(video: Video) -> str:
    lines = [
        f"# {video.title}",
        "",
        f"{video.channel_title} - {video.views if video.views is not None else '?'} views "
        f"- {video.comment_count if video.comment_count is not None else '?'} comments "
        f"- {video.published}",
        video.url,
        "",
    ]
    if video.comments:
        lines += ["---", ""]
        for comment in video.comments:
            indent = "  " * comment.depth
            marker = " [channel]" if comment.is_author else ""
            lines.append(f"{indent}**{comment.author}**{marker} - {comment.likes} likes")
            for line in comment.text.splitlines() or [""]:
                lines.append(f"{indent}{line}")
            lines.append("")
    return "\n".join(lines)
