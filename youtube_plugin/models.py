"""Normalized records. Everything crossing out of api.py becomes one of these."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field

WATCH = "https://www.youtube.com/watch?v="


@dataclass
class Comment:
    id: str
    author: str | None
    author_channel_id: str | None
    text: str
    likes: int
    published: str | None
    updated: str | None
    depth: int  # 0 top-level, 1 reply. YouTube supports no deeper nesting.
    parent_id: str | None
    video_id: str | None
    is_author: bool = False  # comment by the video's channel owner

    @property
    def permalink(self) -> str | None:
        if not (self.video_id and self.id):
            return None
        return f"{WATCH}{self.video_id}&lc={self.id}"

    def to_dict(self) -> dict:
        data = asdict(self)
        data["permalink"] = self.permalink
        return data

    @classmethod
    def from_snippet(cls, raw: dict, depth: int, video_id: str | None) -> "Comment":
        """Build from a `comment` resource's snippet block."""
        s = raw.get("snippet", {})
        author_channel = (s.get("authorChannelId") or {}).get("value")
        return cls(
            id=raw.get("id", ""),
            author=s.get("authorDisplayName"),
            author_channel_id=author_channel,
            text=s.get("textOriginal") or s.get("textDisplay") or "",
            likes=int(s.get("likeCount") or 0),
            published=s.get("publishedAt"),
            updated=s.get("updatedAt"),
            depth=depth,
            parent_id=s.get("parentId"),
            video_id=s.get("videoId") or video_id,
        )


@dataclass
class Video:
    id: str
    title: str
    channel_id: str | None
    channel_title: str | None
    published: str | None
    description: str = ""
    views: int | None = None
    likes: int | None = None
    comment_count: int | None = None
    duration: str | None = None
    comments: list[Comment] = field(default_factory=list)

    @property
    def url(self) -> str:
        return f"{WATCH}{self.id}"

    def to_dict(self) -> dict:
        data = asdict(self)
        data["url"] = self.url
        data["comments"] = [c.to_dict() for c in self.comments]
        return data

    @classmethod
    def from_api(cls, raw: dict) -> "Video":
        s = raw.get("snippet", {})
        stats = raw.get("statistics", {})
        content = raw.get("contentDetails", {})
        vid = raw.get("id")
        if isinstance(vid, dict):  # search-style responses nest the id
            vid = vid.get("videoId")
        return cls(
            id=vid or s.get("resourceId", {}).get("videoId", ""),
            title=s.get("title", ""),
            channel_id=s.get("channelId"),
            channel_title=s.get("channelTitle"),
            published=s.get("publishedAt"),
            description=s.get("description", "") or "",
            views=int(stats["viewCount"]) if "viewCount" in stats else None,
            likes=int(stats["likeCount"]) if "likeCount" in stats else None,
            comment_count=int(stats["commentCount"]) if "commentCount" in stats else None,
            duration=content.get("duration"),
        )


@dataclass
class Channel:
    id: str
    title: str
    handle: str | None
    description: str = ""
    subscribers: int | None = None
    video_count: int | None = None
    view_count: int | None = None
    uploads_playlist: str | None = None

    @property
    def url(self) -> str:
        return f"https://www.youtube.com/{self.handle}" if self.handle else f"https://www.youtube.com/channel/{self.id}"

    def to_dict(self) -> dict:
        data = asdict(self)
        data["url"] = self.url
        return data

    @classmethod
    def from_api(cls, raw: dict) -> "Channel":
        s = raw.get("snippet", {})
        stats = raw.get("statistics", {})
        uploads = (
            raw.get("contentDetails", {}).get("relatedPlaylists", {}).get("uploads")
        )
        subs = stats.get("subscriberCount")
        return cls(
            id=raw.get("id", ""),
            title=s.get("title", ""),
            handle=s.get("customUrl"),
            description=s.get("description", "") or "",
            subscribers=int(subs) if subs is not None else None,
            video_count=int(stats["videoCount"]) if "videoCount" in stats else None,
            view_count=int(stats["viewCount"]) if "viewCount" in stats else None,
            uploads_playlist=uploads,
        )
