"""Channel resolution and uploads-playlist sweeps.

Deliberately never calls search.list. That method sits in its own bucket capped at
100 calls a day, whereas channels.list with forHandle costs 1 unit from the shared
10,000. Resolving by handle instead of searching is the difference between a tool that
works all day and one that dies after a hundred lookups.
"""

from __future__ import annotations

from .api import Api, YouTubeError, parse_channel_ref
from .models import Channel, Video

CHANNEL_PARTS = "snippet,statistics,contentDetails"


def resolve(api: Api, ref: str, use_cache: bool = True) -> Channel:
    """Resolve a @handle, channel URL, or UC... id to a Channel. Costs 1 unit."""
    kind, value = parse_channel_ref(ref)
    params = {"part": CHANNEL_PARTS}
    params["id" if kind == "id" else "forHandle"] = value

    data = api.get("channels.list", params, use_cache=use_cache)
    items = data.get("items") or []
    if not items:
        raise YouTubeError(
            f"No channel found for {ref!r}. Handles are case-sensitive and must "
            f"include the @ (for example @InstituteofDigitalDentistry)."
        )
    return Channel.from_api(items[0])


def videos(
    api: Api, channel: Channel, *, limit: int | None = None, use_cache: bool = True
) -> list[Video]:
    """A channel's uploads, newest first. 1 unit per 50 videos."""
    if not channel.uploads_playlist:
        raise YouTubeError(
            f"Channel {channel.title!r} exposes no uploads playlist, so its videos "
            f"cannot be listed."
        )
    items = api.paginate(
        "playlistItems.list",
        {"part": "snippet,contentDetails", "playlistId": channel.uploads_playlist,
         "maxResults": 50},
        max_items=limit,
        use_cache=use_cache,
    )
    out = []
    for item in items:
        video = Video.from_api(item)
        # playlistItems puts the real video id under contentDetails
        vid = (item.get("contentDetails") or {}).get("videoId")
        if vid:
            video.id = vid
        if video.id:
            out.append(video)
    return out


def hydrate(api: Api, videos_in: list[Video], *, use_cache: bool = True) -> list[Video]:
    """Add statistics to videos from a playlist listing. 1 unit per 50 videos.

    playlistItems.list returns no view or comment counts, so a sweep that wants to
    pick the most-commented videos has to hydrate first.
    """
    by_id = {v.id: v for v in videos_in if v.id}
    ids = list(by_id)
    for start in range(0, len(ids), 50):
        batch = ids[start : start + 50]
        data = api.get(
            "videos.list",
            {"part": "snippet,statistics,contentDetails", "id": ",".join(batch),
             "maxResults": 50},
            use_cache=use_cache,
        )
        for raw in data.get("items", []):
            fresh = Video.from_api(raw)
            target = by_id.get(fresh.id)
            if target:
                target.views = fresh.views
                target.likes = fresh.likes
                target.comment_count = fresh.comment_count
                target.duration = fresh.duration
                target.description = fresh.description or target.description
    return videos_in


def plan_sweep(
    video_count: int, avg_comments: int = 100, pool_size: int | None = None
) -> dict[str, int]:
    """Estimated {method: calls} for a sweep, for the pre-flight quota check.

    `pool_size` is the candidate set that gets listed and hydrated for ranking, which
    is usually far larger than the number of videos actually swept. Omitting it was a
    real bug: an 806-video channel reported an estimate of 23 units for a run that
    actually cost 77, because listing and hydrating the ranking pool was invisible.

    Reply fetches are deliberately not modelled. They depend on how many threads
    exceed their inline reply subset, which is unknowable before fetching, so this
    is a floor rather than a forecast and the caller should say so.
    """
    pages = lambda n: max(1, -(-n // 50))  # noqa: E731 - ceil-divide, reads clearer inline
    pool = pool_size if pool_size is not None else video_count
    return {
        "channels.list": 1,
        "playlistItems.list": pages(pool),
        "videos.list": pages(pool),
        "commentThreads.list": video_count * max(1, -(-avg_comments // 100)),
    }
